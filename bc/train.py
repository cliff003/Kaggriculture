r"""Train the behaviour-cloning policy on GPU (research, 09-27). Run with the ML environment:

.venv-ml\Scripts\python.exe bc\train.py OUT_WEIGHTS.npz SHARD.npz [SHARD.npz ...] [--epochs 8] [--width 64]

Unit head: CNN over the team's 10x10 board (+ a channel marking the acting unit), features gathered at the unit's
tile + pooled board features + global and unit vectors -> 44 action classes (+ log quantity for PICKUP/PLACE).
Market head: pooled board + global vector -> expected counts of the step's market orders (Poisson).
Games are split 90/10 by game for validation. Weights are exported as plain numpy arrays for bc/policy.py.
"""
import argparse
import os
import sys

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import encode as E  # noqa: E402

NA = len(E.ACTIONS)
NM = len(E.MKT)
QTY_ACTS = torch.tensor([1 if (a.startswith("PICKUP_") or a.startswith("PLACE_")) else 0 for a in E.ACTIONS])


class Net(nn.Module):
    def __init__(self, width=64, gdim=E.G, udim=16):
        super().__init__()
        c = E.C + 1
        self.c1 = nn.Conv2d(c, width, 3, padding=1)
        self.c2 = nn.Conv2d(width, width, 3, padding=1)
        self.c3 = nn.Conv2d(width, width, 3, padding=1)
        self.c4 = nn.Conv2d(width, width, 3, padding=1)
        self.g1 = nn.Linear(gdim, 128)
        self.u1 = nn.Linear(width * 2 + 128 + udim, 256)
        self.u2 = nn.Linear(256, 256)
        self.ua = nn.Linear(256, NA)
        self.uq = nn.Linear(256, NA)
        self.m1 = nn.Linear(width + 128, 256)
        self.m2 = nn.Linear(256, 2 * NM)

    def trunk(self, board, unit_plane):
        x = torch.cat([board, unit_plane], 1)
        x = F.relu(self.c1(x))
        x = F.relu(self.c2(x)) + x
        x = F.relu(self.c3(x)) + x
        x = F.relu(self.c4(x)) + x
        return x

    def unit(self, feat, pos, gvec, uvec):
        b = torch.arange(feat.shape[0], device=feat.device)
        at = feat[b, :, pos[:, 1], pos[:, 0]]
        pooled = feat.mean((2, 3))
        g = F.relu(self.g1(gvec))
        h = F.relu(self.u1(torch.cat([at, pooled, g, uvec], 1)))
        h = F.relu(self.u2(h))
        return self.ua(h), self.uq(h)

    def market(self, feat, gvec):
        g = F.relu(self.g1(gvec))
        h = F.relu(self.m1(torch.cat([feat.mean((2, 3)), g], 1)))
        return self.m2(h)


def load(paths):
    parts = [np.load(p) for p in paths]
    out = {}
    off = 0
    goff = 0
    for d in parts:
        for k in ("boards", "globs", "mkts", "u_vec", "u_pos", "u_act", "u_qty"):
            out.setdefault(k, []).append(d[k])
        out.setdefault("u_step", []).append(d["u_step"] + off)
        out.setdefault("game", []).append(d["game"] + goff)
        off += len(d["boards"])
        goff += int(d["game"].max()) + 1
    return {k: np.concatenate(v) for k, v in out.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("shards", nargs="+")
    ap.add_argument("--epochs", type=int, default=8)
    ap.add_argument("--width", type=int, default=64)
    ap.add_argument("--batch", type=int, default=1024)
    ap.add_argument("--lr", type=float, default=2e-3)
    a = ap.parse_args()
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    D = load(a.shards)
    ngames = int(D["game"].max()) + 1
    rng = np.random.default_rng(0)
    val_games = set(rng.choice(ngames, max(1, ngames // 10), replace=False).tolist())
    step_game = D["game"]
    u_game = step_game[D["u_step"]]
    tr_u = np.where(~np.isin(u_game, list(val_games)))[0]
    va_u = np.where(np.isin(u_game, list(val_games)))[0]
    tr_s = np.where(~np.isin(step_game, list(val_games)))[0]
    va_s = np.where(np.isin(step_game, list(val_games)))[0]
    print(f"games {ngames} (val {len(val_games)}), steps {len(step_game)}, unit samples {len(D['u_act'])}", flush=True)
    boards = torch.from_numpy(D["boards"])          # uint8, on CPU
    globs = torch.from_numpy(D["globs"])
    mkts = torch.from_numpy(D["mkts"])
    u_step = torch.from_numpy(D["u_step"].astype(np.int64))
    u_vec = torch.from_numpy(D["u_vec"])
    u_pos = torch.from_numpy(D["u_pos"].astype(np.int64))
    u_act = torch.from_numpy(D["u_act"].astype(np.int64))
    u_qty = torch.from_numpy(np.log1p(np.maximum(0, D["u_qty"]).astype(np.float32)))
    counts = np.bincount(D["u_act"], minlength=NA)
    print("action frequencies:", {E.ACTIONS[i]: int(c) for i, c in enumerate(counts) if c}, flush=True)
    net = Net(a.width).to(dev)
    opt = torch.optim.AdamW(net.parameters(), lr=a.lr, weight_decay=1e-4)
    qmask = QTY_ACTS.to(dev)

    def unit_batch(idx):
        s = u_step[idx]
        b = boards[s].to(dev).float() / 4.0
        plane = torch.zeros((len(idx), 1, 10, 10), device=dev)
        p = u_pos[idx].to(dev)
        plane[torch.arange(len(idx), device=dev), 0, p[:, 1], p[:, 0]] = 1.0
        return b, plane, p, globs[s].to(dev), u_vec[idx].to(dev), u_act[idx].to(dev), u_qty[idx].to(dev)

    for ep in range(a.epochs):
        net.train()
        perm = torch.from_numpy(rng.permutation(tr_u))
        tot = 0.0
        nb = 0
        for i in range(0, len(perm), a.batch):
            idx = perm[i:i + a.batch]
            b, plane, p, g, uv, act, q = unit_batch(idx)
            feat = net.trunk(b, plane)
            logits, qpred = net.unit(feat, p, g, uv)
            loss = F.cross_entropy(logits, act)
            qm = qmask[act].bool()
            if qm.any():
                loss = loss + 0.2 * F.mse_loss(qpred[qm, act[qm]], q[qm])
            # market head on the steps of this batch
            s = u_step[idx].unique()
            bs = boards[s].to(dev).float() / 4.0
            fs = net.trunk(bs, torch.zeros((len(s), 1, 10, 10), device=dev))
            mo = net.market(fs, globs[s].to(dev))
            y = mkts[s].to(dev)
            pos = y > 0
            loss = loss + 0.5 * F.binary_cross_entropy_with_logits(mo[:, :NM], pos.float())
            if pos.any():
                loss = loss + 0.2 * F.mse_loss(mo[:, NM:][pos], torch.log(y[pos]))
            opt.zero_grad()
            loss.backward()
            opt.step()
            tot += float(loss.detach())
            nb += 1
        net.eval()
        correct = total = 0
        with torch.no_grad():
            for i in range(0, len(va_u), 4096):
                idx = torch.from_numpy(va_u[i:i + 4096])
                b, plane, p, g, uv, act, q = unit_batch(idx)
                logits, _ = net.unit(net.trunk(b, plane), p, g, uv)
                correct += int((logits.argmax(1) == act).sum())
                total += len(idx)
        tp = fp = fn = 0
        with torch.no_grad():
            for i in range(0, len(va_s), 2048):
                s = torch.from_numpy(va_s[i:i + 2048])
                fs = net.trunk(boards[s].to(dev).float() / 4.0, torch.zeros((len(s), 1, 10, 10), device=dev))
                mo = net.market(fs, globs[s].to(dev))
                pred = mo[:, :NM] > 0
                pos = mkts[s].to(dev) > 0
                tp += int((pred & pos).sum()); fp += int((pred & ~pos).sum()); fn += int((~pred & pos).sum())
        print(f"epoch {ep + 1}: train loss {tot / max(1, nb):.3f}  val unit accuracy {correct / max(1, total):.3f}  "
              f"market orders precision {tp / max(1, tp + fp):.3f} recall {tp / max(1, tp + fn):.3f}", flush=True)
    sd = {k: v.detach().cpu().numpy() for k, v in net.state_dict().items()}
    np.savez(a.out, width=np.int64(a.width), **{k.replace(".", "__"): v for k, v in sd.items()})
    print("saved", a.out)


if __name__ == "__main__":
    main()

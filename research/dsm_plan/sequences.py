r"""Per-tile use sequences (what gets planted/built on each tile, and on which day), modal over games.
    .venv\Scripts\python.exe research\dsm_plan\sequences.py      -> out\tile_sequences.md

Notation: <crop letter><day> for a planting (w wheat, c carrot, t tomato, s strawberry, m melon); a run of
consecutive wheat plantings is shown as w<first>..<last>; p/o<animal letter><day> = pasture/coop built on <day>
and the animal placed on it (C cow, S sheep, G goose).
"""
import collections
import os

from common import HERE, load_games

OUT = os.path.join(HERE, "out")


def main():
    G = load_games()
    N = len(G)
    seqs = collections.defaultdict(collections.Counter)
    for g in G:
        s = collections.defaultdict(list)
        for (t, idx, a, pos, tb, ta, d) in g["units"]:
            if not a or tb == ta:
                continue
            if a[0] == "PLANT":
                s[pos].append(f"{ta[1][0].lower()}{t // 24}")
            elif a[0] in ("BUILD_COOP", "BUILD_PASTURE"):
                s[pos].append(("o" if a[0] == "BUILD_COOP" else "p") + str(t // 24))
            elif a[0] == "PLACE" and ta and ta != "L" and ta[0] == "A" and s[pos]:
                s[pos][-1] = s[pos][-1][0] + ta[2][0] + s[pos][-1][1:]
        for pos, L in s.items():
            out = []
            for e in L:
                if out and e[0] == "w" and out[-1][0] == "w":
                    out[-1] = out[-1].split("..")[0] + ".." + e[1:]
                else:
                    out.append(e)
            seqs[pos][" ".join(out)] += 1
    lines = [f"# Modal use sequence per tile ({N} games)\n", __doc__.split("\n\n", 1)[1], "",
             "| tile | quadrant | most common sequence (games) | 2nd (games) | 3rd (games) |", "|---|---|---|---|---|"]
    for y in range(10):
        for x in range(10):
            c = seqs[(x, y)]
            if not c:
                continue
            top = c.most_common(3) + [("", 0)] * 3
            q = ("N" if y < 5 else "S") + ("W" if x < 5 else "E")
            lines.append(f"| ({x},{y}) | {q} | " + " | ".join(f"`{k}` ({v})" if v else "" for k, v in top[:3]) + " |")
    text = "\n".join(lines) + "\n"
    with open(os.path.join(OUT, "tile_sequences.md"), "w", encoding="utf-8") as f:
        f.write(text)
    print(text)


if __name__ == "__main__":
    main()

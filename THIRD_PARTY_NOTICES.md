# Third-party notices

Team 42's own code and text are under the Apache License 2.0 ([LICENSE](LICENSE)). This repository also contains, or is derived from, the following third-party work. All of it is Apache-2.0, and its license text and attribution notices are kept unchanged where the code is embedded.

| Where | What | Author and license |
|---|---|---|
| `submissions/*/` (every package from v4 on) | the embedded source of the public [cha22 agent](https://www.kaggle.com/code/abhinav0370/cha22-agent) (main.py SHA-256 `127ed3e6...`): verbatim up to v9, with the production patches listed in each package's `NOTICE.txt` from v10 on | Abhinav0370, Apache-2.0; itself a derivative of the public route-replay lineage by thomastschinkel, yhay81, destbreso, aurax7, tetsutani, prvsiyan, Dmitrii Gluzdov, Ahmed Berat Ozer and others |
| `submissions/v3_own_rescue_slot/` | the embedded public rescue agent | Dmitrii Gluzdov, Apache-2.0, same lineage |
| `research/carrera/base_v10.py` | a decoded copy of the public V39 lineage base used for research | Apache-2.0, upstream notices retained in the file |
| `research/panel/emu_*/main.py` | local test opponents built on cha22 | Abhinav0370 and lineage, Apache-2.0, notices retained |
| `tools/add_carrot.py` | a layer adapted from the public "v9 CARROT" layer of the rescue lineage | Dmitrii Gluzdov and co-authors, Apache-2.0 |
| `research/notebook_0930_2032/probe_settlement.py` | a local research port of "Guarded Shop Settlement v2" | lynnsakurai, Apache-2.0 ([notebook](https://www.kaggle.com/code/lynnsakurai/farmer-john-and-the-wheat-seller)) |
| `docs/figures/fonts/` | figure fonts: Inter (variable) and JetBrains Mono (Medium, Bold), embedded in the rendered figures | Inter by Rasmus Andersson, JetBrains Mono by JetBrains; both SIL Open Font License 1.1 (`Inter-OFL.txt`, `JetBrainsMono-OFL.txt`) |

Not included: the public agents we uploaded verbatim (cha22, rescue, morewheat, farm2945, herdsafe_race) as stand-alone files, the other public agents we tested against, and Frank Yang's own planner. The game engine, [kaggle-environments](https://github.com/Kaggle/kaggle-environments) (Apache-2.0), is a dependency and is not redistributed.

Ideas, not code:

- The wheat tick arbitrage was learned from public replays of the team Otter Vibe.
- DECEM's public description of demand-proportional production informed our production research.
- Public analyses we read: georgymamarin (game datasets and an analysis of 2600+ farms), destbreso (x-ray), ashok205 (replay archive of the top 10), raykkretzschmar, goodpjw2008, haideptry, leoprovorov, evgendvorkin.

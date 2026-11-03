# Bundled third-party files

Inlined into every generated HTML so reports work offline.

| File | Project | Version | Licence | Source |
| --- | --- | --- | --- | --- |
| `echarts/echarts.min.js` | Apache ECharts | 6.1.0 | Apache-2.0 (`echarts/LICENSE`, `echarts/NOTICE`) | npm `echarts@6.1.0` |
| `vazirmatn/Vazirmatn-Variable.woff2` | Vazirmatn | 33.0.3 | SIL OFL 1.1 (`vazirmatn/OFL.txt`) | npm `vazirmatn@33.0.3` |

Update with `npm pack <package>@<version>`, copy the same files, and update this table.

## Agent skills (instructions and offline scripts only)

Pinned copies, reviewed before bundling. Reporch never runs their network code, and none is included.

| Folder | Project | Commit | Licence | What is kept | What is left out, and why |
| --- | --- | --- | --- | --- | --- |
| `persian-writing/` | [ali2000hos/persian-writing](https://github.com/ali2000hos/persian-writing) | `75fcdf3` (2026-10-04) | MIT (`persian-writing/LICENSE`) | `GUIDE.md` (their `SKILL.md`, renamed so agents don't load it as a second skill); `references/` writing-style, orthography, html-css, content-structures; `scripts/fa_lint.py` and `scripts/persian_cleanup.py` (standard library, no network) | font downloader (network), docx/pdf tools and fonts (Reporch has its own), 7 MB word list (only used for an optional hint), cleanup API docs |
| `taste-skill/` | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | `12af471` (2026-10-25) | MIT (`taste-skill/LICENSE`) | `GUIDE.md` (their `SKILL.md`, renamed so agents don't load it as a second skill); `references/` tells, type, layout, colour, critique, copy | Node scripts (`assets.mjs` searches image sites over the network; the inspector needs Chrome), libraries, images |

To update: clone at a new commit, read every changed file, check again for network or shell calls, copy the
same files, and update this table. `modules/design.md` and `modules/write.md` say how Reporch uses them.

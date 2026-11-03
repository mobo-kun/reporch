<p align="center"><img src="media/banner.svg" alt="Reporch: Report of Research" width="100%"></p>

<p align="center">
  <b>English</b> · <a href="README.fa.md">فارسی</a> ·
  <a href="HOW-TO-USE.md">How to use</a> ·
  <a href="ROADMAP.md">Roadmap</a> ·
  <a href="CHANGELOG.md">Changelog</a>
</p>

**Reporch** turns the raw material of a user-research study into a report people can read, share and
publish. You talk to it (a voice transcript is perfect) or hand it your notes, transcripts, spreadsheets
and survey exports. It asks what's missing, runs the analyses your data supports, and builds:

- an **HTML report** that works offline: table of contents, slide mode, charts, zoomable images;
- a **blog post** telling the same story for readers outside the team;
- a **PDF** of the report;

in one language or two (each document has one language), with Markdown copies if you want them.

It's an agent skill for **Claude Code** and **Codex**, made for product, UX and UI designers and user
researchers, and useful to anyone who ran a study: PMs, data people, students.

<p align="center"><img src="media/report-en.png" alt="The demo report in English" width="49%"> <img src="media/report-fa.png" alt="The demo report in Persian" width="49%"></p>

## Why it's different

| | |
| --- | --- |
| **Your words stay yours** | Reporch never cuts, merges, reorders or rewords what you wrote without asking you first, in your language. |
| **Nothing invented** | No number, quote, finding or image without a source in your data or your answers. Gaps become questions. |
| **Every finding has evidence** | Each claim links to the participant, file, row or timestamp behind it. Quotes are checked word for word against your inputs. |
| **Real statistics** | 118 analyses from *Measuring the User Experience* (Tullis & Albert), *Usability Engineering* (Nielsen) and product-metrics practice: adjusted Wald intervals, log-time means, SUS, NPS, χ², Fisher, t tests, funnels, cohorts… Reporch offers only what your data supports, 10 to 40 per report. |
| **Checked before you publish** | A QA pass traces every number, checks quotes, language, right-to-left layout, phone width, charts, file size and the PDF. |
| **Lossless migration** | Bring an old HTML or PDF report: every heading, paragraph, table cell, chart value and image comes across, and a check proves it. |
| **Private by default** | Names become `P01, P02…`; emails, phones and card numbers are removed. Nothing leaves your machine without your OK. |

## Install

**One line** (asks whether you want it for Claude Code, Codex or both; uses only `git`):

```bash
curl -fsSL https://raw.githubusercontent.com/mobo-kun/reporch/main/install.sh | bash
```

**Or by hand:**

```bash
git clone https://github.com/mobo-kun/reporch ~/.claude/skills/reporch
```

```bash
git clone https://github.com/mobo-kun/reporch ~/.agents/skills/reporch
```

The first is for Claude Code, the second for Codex. Restart your agent afterwards.

**Needs:** Python 3.9+ (standard library only). The PDF step uses Playwright and Chromium; Reporch asks
before installing them, and without them you can print the HTML to PDF from Chrome.

## Use

In Claude Code or Codex:

> Use Reporch. I ran a usability test with eight people. Here are my notes.

Reporch introduces itself, proposes this path, and remembers where you stopped:

```
collect → interview → analysis → outline → write → translate → build → check
```

The full guide is in [HOW-TO-USE.md](HOW-TO-USE.md) ([فارسی](HOW-TO-USE.fa.md)).

## See it

[`examples/demo`](examples/demo) holds a complete **fictional** study (an imaginary grocery app, invented
participants and numbers) with its inputs and `content.json`. Build it yourself:

```bash
python3 scripts/reporch.py build examples/demo/basket-checkout --markdown
```

<p align="center"><img src="media/chart-en.png" alt="An analysis with its chart" width="60%"> <img src="media/phone-fa.png" alt="The Persian report on a phone" width="22%"></p>

## What's inside

```
SKILL.md          the skill: rules, workflow, tools (AGENTS.md points Codex here)
modules/          one instruction file per phase: intake, interview, brand, languages,
                  analysis, write, images, build, qa, migrate
references/       outline, content model, theme, the 118-analysis catalogue (.md and .json)
scripts/          reporch.py and its library: intake, anonymiser, statistics, renderer, PDF, QA, migration
templates/        report and blog styles, the page script, generated theme tokens
vendor/           ECharts (Apache-2.0) and Vazirmatn (OFL), bundled for offline reports
examples/demo/    the fictional demo study
tests/            unit tests (python3 -m unittest discover -s tests)
```

## Versions

Reporch uses [semantic versioning](https://semver.org). The current version is in [`VERSION`](VERSION);
changes are in [CHANGELOG.md](CHANGELOG.md) and what's next is in [ROADMAP.md](ROADMAP.md). If you allow it,
Reporch checks GitHub for a newer version once a day.

| Version | Status | Highlights |
| --- | --- | --- |
| **1.0** | now | raw material → report, blog and PDF; 118 analyses; QA; lossless HTML/PDF migration |
| 1.1 | next | screenshots, audio and video as inputs; FigJam and Miro exports |
| 1.2 | planned | export to CMS, Notion and Confluence |
| 2.0 | planned | research planning (plans, guides, screeners); marketplace plugin |

## Credits

Made by **Mobo · Behdad Morsalpoor** (بهداد مرسل‌پور). Every report Reporch builds carries a small credit line.

Charts by [Apache ECharts](https://echarts.apache.org) (Apache-2.0). Typeface
[Vazirmatn](https://github.com/rastikerdar/vazirmatn) by Saber Rastikerdar (OFL-1.1). See [NOTICE](NOTICE).

## License

[MIT](LICENSE) © 2026 Mobo · Behdad Morsalpoor. Use it, change it, share it; keep the copyright notice.

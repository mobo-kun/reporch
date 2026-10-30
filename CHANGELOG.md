# Changelog

All notable changes to Reporch. The format follows [Keep a Changelog](https://keepachangelog.com) and
versions follow [semantic versioning](https://semver.org).

## [1.0.0] - 2026-10-30

First release.

### Added
- **Skill:** `SKILL.md` with the first-run greeting, the non-negotiable rules (never change the user's
  words without asking, never invent, evidence for every finding, privacy first) and the eight-phase
  workflow; `AGENTS.md` for Codex; how-to-use guides in English and Persian.
- **Intake:** readers for text, Markdown, voice and interview transcripts (`.vtt`, `.srt`), Word and
  Google Docs (`.docx`), `.csv`/`.tsv` and `.xlsx` (Google Forms, Typeform), standard library only;
  automatic anonymisation of names, emails, phones (Latin and Persian digits), card numbers and IBANs.
- **Interview:** gap-driven questions in batches, 5–40 in total, in the user's language.
- **Analysis:** a catalogue of 118 analyses in nine groups (task performance, scores, surveys,
  qualitative, behaviour data, card sorting and heuristics, study-wide, product metrics, onboarding), each
  with the data it needs; selection of what the data supports; a statistics library checked against
  reference values.
- **Outputs:** single-language offline HTML report (sticky contents, phone drawer, progress bar, slide
  mode, image zoom, ECharts charts drawn from their tables, evidence index), blog post, Markdown, PDF via
  Playwright, right-to-left support, image placeholders that describe the picture needed.
- **Theme:** light theme with dot pattern and glow, a palette with WCAG-checked text shades, brand colour
  and logo per project, brand fonts only from the user's own `assets/`.
- **QA:** content validation, number tracing, verbatim quote check, language and orthography, offline
  and size checks, phone and desktop layout and chart drawing in a browser, PDF checks.
- **Migration:** lossless migration of existing HTML (incl. Chart.js charts) and PDF reports, with a
  check that every piece of the original is kept.
- **Install and updates:** one-line installer for Claude Code and Codex; opt-in update check.
- **Demo:** a complete fictional study generated from invented data.

# content.json

One file per report holds all of its content in every chosen language. Outputs are rendered from it;
nothing is written into an output that isn't in `content.json`. Validate with
`python3 scripts/reporch.py validate <project> [--final]`.

## Shape

```json
{
  "schema": "reporch/content@1",
  "meta": {
    "title": {"en": "…", "fa": "…"},
    "headline": {"en": "…", "fa": "…"},
    "slug": "checkout-usability-2026",
    "authors": [{"name": "…", "role": "…"}],
    "methods": ["usability-test"],
    "studyGoal": "formative",
    "dates": {"start": "2026-09-01", "end": "2026-09-10"},
    "languages": ["en", "fa"],
    "brand": {"primary": "#754EC6", "logo": "assets/logo.svg", "font": null}
  },
  "participants": [{"id": "P01", "segment": "mobile", "notes": "…"}],
  "evidence": [{"id": "E1", "source": "inputs/session-notes.docx", "locator": "p.2", "participant": "P01"}],
  "analyses": [{
    "id": "AN1", "catalogueId": "A1",
    "title": {"en": "…", "fa": "…"}, "finding": {"en": "…", "fa": "…"},
    "table": {"columns": ["task", "success"], "rows": [["T1", 0.6]]},
    "chart": {"kind": "bar", "x": "task", "series": ["success"]},
    "values": {"n": 10, "low": 0.103, "high": 0.608},
    "evidence": ["E1"]
  }],
  "sections": [{
    "id": "summary", "role": "summary", "title": {"en": "…", "fa": "…"},
    "blocks": [{"type": "paragraph", "text": {"en": "…", "fa": "…"}, "evidence": ["E1"]}],
    "children": []
  }],
  "blog": {"title": {"en": "…"}, "dek": {"en": "…"},
           "sections": [{"id": "b1", "title": {"en": "…"}, "blocks": [ … same block types … ]}]},
  "glossary": [{"term": "SEQ", "text": {"en": "…", "fa": "…"}}],
  "openQuestions": [{"text": {"en": "…", "fa": "…"}}]
}
```

`values` holds the summary numbers a finding quotes that aren't table cells (means, interval ends, p,
n, a difference). QA traces every number in a finding to the table or to `values`.

## Blocks

| Type | Required fields | Notes |
| --- | --- | --- |
| `heading` | text | |
| `paragraph` | text | |
| `callout` | tone (info, warn, critical, success), text | |
| `quote` | text, participant, evidence | No quote without evidence |
| `stats` | items (label, value, note, tone) | Stat cards |
| `table` | columns, rows | Every row has one cell per column |
| `chart` | chart, table | The chart is drawn from its table, so they always match |
| `image` / `video` | caption, and src or placeholder | Placeholder = kind + description of what is needed |
| `list` | items | |
| `analysis` | analysis | Places an analysis (by id) in a section |
| `actionPlan` | items (text, priority, effort, owner) | Only if the user wants it |
| `persona` | name, text | |
| `flow` | steps (text, status ok/fail/neutral) | |
| `timeline` | items (date, text) | |
| `pending` | text | Something the user still has to give |
| `compare` | before, after (each: src or placeholder, optional label, alt, note); caption; changes (list) | Old vs new design side by side, and what changed. Images or videos. Gets its own slide |

Stat items may also carry `detail`: the raw numbers behind an impact value ("8 of 8 people" under "100%").
`meta.studyType` is `redesign`, `new`, `current-state` or `other`; a redesign without a `compare` block gets a
warning.

Any block may carry `evidence: ["E…"]`.

## Rules the validator enforces

- Every localized text has every language in `meta.languages` (draft: warning; final: error). A text
  marked `"_pendingTranslation": true` is allowed in drafts only.
- Participants are anonymised (`P01`, `P02`, …); quotes and evidence refer to known participants.
- Every analysis has evidence; every reference points at something that exists.
- Every chart has its source table, and the chart's columns exist in it.
- Top-level sections follow `references/outline.md`; summary, problem, solution and result are required.
- 10–40 analyses (draft: warning; final: error), each placed in a section.
- The blog post exists (final) and its blocks follow the same rules.

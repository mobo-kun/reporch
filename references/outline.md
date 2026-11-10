# The standard outline

Every report, whatever the method, uses this outline (R15). The spine is
**summary → problem → solution → result**; the other sections hang around it. Sections may have
children, so the outline grows with the study without changing its shape.

| # | Role | Required | What goes in it |
| --- | --- | --- | --- |
| 1 | `summary` | yes | 3–5 key findings, the main numbers (stat cards), one line on what happens next. Written last, only from the user's content. |
| 2 | `context` | no | Product, why the study was run, the research questions, formative or summative. |
| 3 | `method` | no | Method(s), tasks, dates, tools, what was recorded, help policy. |
| 4 | `participants` | no | Who, how many, segments, recruitment (G1). Anonymised ids only. |
| 5 | `problem` | yes | What is wrong or unknown: the findings that describe the problem, with evidence. |
| 6 | `solution` | yes | What was designed or proposed in response. If no solution exists yet, a `pending` block says so and an open question asks for it. For a redesign (`meta.studyType: redesign`) it opens with a `compare` block: old and new design side by side and what changed. A current-state study has no comparison. |
| 7 | `result` | yes | What the analyses show: the 10–40 analyses grouped by question, each with chart/table, finding and evidence; precision note (G2). A framework map (HEART or AARRR) may lead it when the data fits. |
| 8 | `actionPlan` | no | Only if the user wants it (suggested, never forced): items with priority, effort and owner from the user. |
| 9 | `limitations` | no | Sample size vs method, validity threats, what the results don't cover. |
| 10 | `appendix` | no | Evidence index, glossary, open questions, data-cleaning note (G6), raw tables. |

Rules:

- Top-level sections appear in this order; any may be left out except the four required ones.
- A finding sits in `problem` when it describes the situation before the change, and in `result` when it
  measures the outcome. When unsure, ask the user.
- Every section can carry image placeholders (`references/placeholders.md`).
- The blog post uses the same spine as a story: hook (the problem in one scene) → what we did →
  what we found → what changed → what's next.

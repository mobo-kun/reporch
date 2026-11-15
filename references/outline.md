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

## Benchmark studies (`meta.studyType: benchmark`)

A benchmark compares products (or versions) on the same tasks and measures, so it has no "solution".
Its spine is **summary → products → result → position**:

| Role | Required | What goes in it |
| --- | --- | --- |
| `summary` | yes | The headline: where the product stands, in impact numbers |
| `context`, `method`, `participants` | no | Why the benchmark, which tasks and measures, who took part |
| `products` | yes | The products compared, opening with a `compare` block (`items`: one shot per product) and the key differences |
| `result` | yes | The analyses product by product: competitor benchmark (F7), feature comparison (F4), strengths and weaknesses (F5), industry reference values with their source |
| `position` | yes | Where the product stands overall: ahead, level, behind, and on what |
| `opportunities` | no | What the others do better that is worth learning from, from the data only |
| `actionPlan`, `limitations`, `appendix` | no | As above |

`problem` and `solution` may still be used if the designer wants them. A benchmark is often delivered
as slides only (`meta.outputs: ["slides"]`).

Rules:

- Top-level sections appear in this order; any may be left out except the four required ones.
- A finding sits in `problem` when it describes the situation before the change, and in `result` when it
  measures the outcome. When unsure, ask the user.
- Every section can carry image placeholders (`references/placeholders.md`).
- The blog post uses the same spine as a story: hook (the problem in one scene) → what we did →
  what we found → what changed → what's next.

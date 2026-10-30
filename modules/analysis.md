# Module: analysis (phase 3)

Goal: 10–40 correct analyses, each built only from the user's data and answers, each with its evidence
and its precision.

## 1. Choose

1. Run `reporch.py possible <project>`. Only these analyses may be offered.
2. If fewer than 10 are possible, go back to the interview with the top gaps. Never pad the list.
3. Rank: (a) answers the study's research questions; (b) uses the richest data; (c) covers different
   groups (task performance, scores, qualitative, behaviour…); (d) formative studies favour problem
   analyses (D, F, A18, A13), summative favour measures and comparisons (A, B, G7, G12–G14).
   Always include G1 (participants) and G2 (what the sample supports) when numbers are reported.
4. Show the user the list (id, title, one line on why) and get a yes before computing. They may drop
   or add any possible analysis.

## 2. Compute

- Use `reporch.py calc <function> '<json>'` (or `reporch_lib.stats` in a short script) for every number.
  Never compute in your head; never round before the end.
- Follow the statistics rules in `references/analyses.md` §0.1. In short: adjusted Wald 95% for rates;
  t-based CI for means; geometric mean and log-time CI for times; paired tests for the same people;
  χ² on counts (Fisher's exact for small 2×2 tables); medians and frequencies for ordinal data.
- Clean data openly: excluded rows (outliers, too-fast attempts, incomplete responses) go into G6 with
  the reason. Ask before excluding anything.
- Keep raw numbers: the table holds counts and n, not only percentages.

## 3. Write each analysis into content.json

```json
{"id": "AN3", "catalogueId": "A1", "title": {…}, "finding": {…},
 "table": {"columns": ["task", "success rate", "low", "high", "n"], "rows": [["T1", 0.3, 0.103, 0.608, 10]]},
 "chart": {"kind": "rangeBar", "x": "task", "series": ["success rate"], "range": ["low", "high"]},
 "evidence": ["E4", "E5"], "method": "adjusted Wald 95%"}
```

- **Finding:** one or two sentences in plain words, with the number and its interval ("3 of 10 finished
  task 1 alone (30%, 95% CI 10–61%)"). No interpretation the data can't carry.
- **Evidence:** every participant row, file or session used.
- **Chart:** chosen from the catalogue's output column; the chart is drawn from the table, so they match.
- **Precision:** small samples are fine, but say what they support (G2). Never call a difference
  "significant" without a test, and report the test and p.

## 4. Qualitative analyses

- Code transcripts and notes yourself, then show the user the codes and themes with counts (how many
  participants) and two or three example quotes each. Themes enter the report only after the user
  approves them; they may rename, merge or drop any.
- Quotes are copied exactly from `inputs/clean/` with their evidence id. Never fix a quote's grammar.
- Severity, priority and impact ratings come from the user; you may propose, they decide.

## 5. Charts that exist only as images

If the user gives a chart as a picture, ask for its numbers and redraw it from them. If they don't have
the numbers, keep the picture with its caption and source.

When the user approves the analyses, `advance`.

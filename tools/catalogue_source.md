# Analyses catalogue

Reporch chooses 10–40 of these analyses for each report, and only those the user's data supports.
`analyses.json` holds the same list with machine field keys (`needs`) for `reporch.py possible`.

Sources (ideas in our own words): **[TA]** Tullis & Albert, *Measuring the User Experience*, 2nd ed.
(2013) · **[N]** Nielsen, *Usability Engineering* (1993) · **[ART]** product-metrics articles: Product
Compass ("Are you tracking the right metrics?" and "The Ultimate Guide to Product Metrics", 2025),
UX Collective ("Product Metrics That Matter", 2021), Design With Value (AARRR), Appcues (onboarding
patterns), UX Design Institute (UX KPIs).

## 0. Rules for choosing analyses

1. **Offer only what the data supports.** Each analysis lists its **Needs**. Missing field → don't offer
   it; if fewer than 10 are possible, ask the user for the missing fields (named exactly), never invent.
2. **10–40 per report.** Rank candidates by: answers the study's goal → uses the richest data →
   variety across groups. G1 and G2 are always included when numbers are reported.
3. **Formative vs summative** (ask first) [N]: formative studies lean on D, F and A-problem analyses;
   summative on A/B measures, G-scorecards and comparisons.
4. **Definitions come from the user.** Success criteria, "active", "key action", targets, weights,
   severity, costs: if not given, state what the data implies and ask the user to confirm. Never set them ourselves.
5. **Every result shows its evidence** (participants, rows, sessions) and its precision.

## 0.1 Statistics rules (all analyses)

| Rule | Detail | Source |
| --- | --- | --- |
| Classify each variable first | nominal → counts/χ²; ordinal → medians, frequencies, never means; interval → means OK; ratio → means, geometric mean | [TA] ch.2 |
| Proportions | **Adjusted Wald 95% CI** (default; state it). Show it even at n = 5 | [TA] p.70 |
| Means | t-based CI; state 95% (90% optional when the user asks) | [TA] pp.22–24 |
| Times | report median and geometric mean beside the mean; CI on log times; say if only successful tasks count; outliers (>mean+3 SD, or faster than an expert) are excluded and listed (G6) | [TA] p.80 |
| Two groups | independent t (between-subjects); **paired t** (same people, or matched days) | [TA] pp.25–29 |
| More than two | one-way ANOVA, pairwise only if significant | [TA] pp.29–30 |
| Counts | χ² on raw counts; Fisher's exact when expected counts are small, or don't test | [TA] pp.31–32 |
| Relationship | Pearson r with n; never claim cause | [TA] p.30 |
| Small n | never refuse a metric for small n; always show the interval and a precision note (G2) | [TA], [N] ch.6 |
| Benchmarks | only with their source (e.g. SUS 68, satisfaction median 3.6/5); always marked as rules of thumb | [TA], [N] p.36 |
| Charts | bars for categories, lines only for continuous x, stacked bars sum to 100%, % axes start at 0, error bars labelled with the CI level | [TA] §2.7 |

## A. Task performance (usability tests, tree tests)

| # | Analysis | Needs | Output | Source |
| --- | --- | --- | --- | --- |
| A1 | Task success rate + CI; failure types (gave up / wrong / timed out) | success yes/no per P per task (+ failure type) | bar with CI | TA, N |
| A2 | Levels of success (unaided, assisted, partial, failed); help use and help success | success level per P per task | 100% stacked bar (never averaged) | TA, N |
| A3 | Time on task (median, geometric mean, CI); expert subgroup; optional predicted-vs-measured | time per P per task (+ success, expertise) | bar / box | TA, N |
| A4 | Errors: single-opportunity (% with error) and multi-opportunity (rate per opportunity); minor vs catastrophic; recovery time | errors per P per task (+ opportunities, type, severity) | table, bar | TA, N, ART |
| A5 | Ease per task (SEQ, ASQ) + session mean | post-task rating | bar with CI | TA |
| A6 | Path / first-click accuracy; % on the efficient path | first click or path per P | table, pie-tree | TA, N |
| A7 | Step drop-off (where people got stuck) | step reached per P | funnel with drop % | TA |
| A8 | Directness / backtracking (tree tests and any hierarchy) | path per P | stacked bar | TA |
| A9 | Segment comparison of A1/A3 (device, experience, locale, accessibility group) | A1/A3 + segment | grouped bar | TA, N |
| A10 | Learnability over trials; time to criterion | ≥2 attempts per P | line | TA, N |
| A11 | Memorability (returning-user performance or recall score) | performance after a break, or recall test | bar | N |
| A12 | Comprehension rate of icons/labels vs criterion | right/wrong per element per P | bar with criterion line | N |
| A13 | Problem impact (people affected × time lost) | issues with time lost per P | ranked table | N |
| A14 | Time-threshold attainment (% within the user's threshold) | times + threshold from user | bar with CI | TA |
| A15 | Actions per task vs optimum; % at optimum | clicks/steps per P + optimum | bar | TA |
| A16 | Lostness | pages visited, unique, optimum per P per task | bar with 0.4/0.5 bands | TA |
| A17 | Efficiency (success ÷ time), per task and per participant | A1 + A3 | bar | TA |
| A18 | Issues by task (by severity) | issue list tagged with task | stacked bar | TA |
| A19 | Expectation vs experience quadrant | pre-task expectation + post-task rating | scatter, 4 quadrants | TA |
| A20 | Comparison to expert performance | expert time/steps per task | bar ratio | TA |
| A21 | Navigation vs search share | method per P per task | stacked bar | ART |

## B. Questionnaires and scores

| # | Analysis | Needs | Output | Source |
| --- | --- | --- | --- | --- |
| B1 | SUS score, grade/percentile (with source), CI; stability note below ~12 | 10 SUS items per P | gauge, table | TA |
| B2 | NPS with CI per component; "not a usability measure" note | 0–10 per P | stacked bar | TA, ART |
| B3 | Satisfaction / CSAT: distribution, CSAT = share of 4–5 answers (top-2) with CI, bottom-box, reference anchor; prefer ratings taken right after the action | rating per P + scale | bar | TA, N, ART |
| B4 | Standard scales (UMUX-Lite, ASQ, PSSUQ/CSUQ, QUIS, USE) incl. subscales | items per P | bar / radar | TA |
| B5 | Custom Likert items (distribution, mean ± CI, top-2 box; reversed items handled) | Likert answers | diverging bar | TA, N |
| B6 | Attribute ratings (trust, appeal, credibility, confidence…) | ratings per attribute | bar / radar | TA |
| B7 | Intent (return, recommend, buy) | rating per P | bar | — |
| B8 | Score by segment | any B score + segment | grouped bar | TA, N |
| B9 | Preference between systems/designs (+ order caveat) | choice per P | bar with CI | N |
| B10 | Reaction cards / chosen words (frequency, positive share) | words per P | word bars | TA |
| B11 | Customer Effort Score (mean rating; scale direction stated) | effort rating per P | bar | ART |

## C. Surveys

| # | Analysis | Needs | Output | Source |
| --- | --- | --- | --- | --- |
| C1 | Response overview (n, completion, drop-off; self-selection note) | export with blanks/timestamps | table, funnel | TA |
| C2 | Single-choice distribution + CI | one choice question | bar | TA |
| C3 | Multi-choice frequency | multi-choice | bar | — |
| C4 | Cross-tab + χ² / Fisher | two categorical questions | heatmap | TA |
| C5 | Ranking (mean rank) | ranking answers | bar | — |
| C6 | Open-text themes (coded), positive/negative ratio | open answers | theme table + quotes | TA |
| C7 | Respondent profile | demographic columns | tiles | — |
| C8 | Awareness / comprehension (corrected with distractor items) | aware yes/no per item (+ distractors) | bar | TA |
| C9 | Awareness–usefulness gap | awareness + usefulness per feature | paired bars by gap | TA |

## D. Qualitative (interviews, think-aloud, diary, issues)

| # | Analysis | Needs | Output | Source |
| --- | --- | --- | --- | --- |
| D1 | Themes with frequency (how many P) | transcripts/notes per P | theme table | N |
| D2 | Pain points: frequency × severity (× persistence), % P per issue with CI | issues per P + severity | priority matrix | TA, N |
| D3 | Severity ratings as the user rated them (0–4, 3-level, multi-factor); raters, mean, spread | issue list + ratings | table | TA, N |
| D4 | Quotes per theme (illustration, not frequency) | transcripts | quote cards | N |
| D5 | Mental models: expectation vs reality (observed behaviour preferred) | transcripts + observations | two-column table | N |
| D6 | Journey map | stage notes | journey chart | — |
| D7 | Personas / archetypes | ≥5 P with behaviour notes | persona cards | — |
| D8 | Jobs to be done | goals in transcripts | JTBD table | — |
| D9 | Diary: change over time | dated entries per P | timeline | — |
| D10 | Say vs do (incl. questionnaire claim vs observed use) | statements + behaviour | table | N |
| D11 | Tone of remarks (positive / critical / neutral) per task or screen; frustration moments | coded remarks | stacked bar | TA, N |
| D12 | Critical incidents (best and worst moments, with context) | incident notes | table | N |
| D13 | Locale and translation issues | issues tagged by locale | table | N |
| D14 | Unique issues by severity and iteration | issue list (+ iteration) | stacked bar | TA |
| D15 | Issues per participant | issue × participant matrix | bar | TA |
| D16 | Issues by category | issues with category | stacked bar | TA |

## E. Behaviour data (analytics, replay, logs, A/B)

| # | Analysis | Needs | Output | Source |
| --- | --- | --- | --- | --- |
| E1 | Funnel conversion and drop-off per step (bounce/exit) | step counts | funnel | TA |
| E2 | Session outcome split | sessions + outcome | doughnut | — |
| E3 | Issue frequency across sessions | coded sessions | bar | — |
| E4 | Device / platform split | device per session | doughnut | — |
| E5 | A/B difference + CI + test (between/within noted) | conversions/means and n per variant | bar with CI | TA, N |
| E6 | Before/after (paired t on matched days; any metric) | same metric, two periods | slope / bar | TA, N |
| E7 | Clicks / attention per element (χ² on counts; near-miss clicks; on screenshot) | click counts | bar / overlay | TA, N |
| E8 | Feature usage and never-used features (Pareto) | usage log per feature | Pareto | N |
| E9 | Error-message Pareto | logged errors by type | Pareto | N |
| E10 | Feedback / complaint classification and trend | tickets/feedback | stacked bar, line | N |
| E11 | Response-time bands (0.1 / 1 / 10 s) | wait times per step | stacked bar | N |
| E12 | Eye-tracking per area (dwell, time to first fixation, hit ratio) | AOI data | table, heatmap | TA |
| E13 | Physiological measures (only if supplied) | sensor data | line | TA |

## F. Card sorting, heuristics, competition, accessibility

| # | Analysis | Needs | Output | Source |
| --- | --- | --- | --- | --- |
| F1 | Card-sort similarity matrix | card → group per P | heatmap | TA |
| F2 | Clustering into categories + goodness of fit | F1 data | dendrogram | TA |
| F3 | Heuristic violations by heuristic and severity; found by k of n evaluators; positives | evaluators' issue lists | matrix | N |
| F4 | Competitor feature comparison | features per competitor | grid tiles | — |
| F5 | Competitor strengths / weaknesses | notes | table | — |
| F6 | Evaluator overlap and aggregation curve | ≥2 evaluators' lists | line | N, TA |
| F7 | Competitor benchmark (same tasks, same metrics) | A/B metrics per product | grouped bar | N |
| F8 | MDS map of cards (with stress) | F1 data | scatter | TA |
| F9 | Closed card-sort agreement per card | card → fixed category per P | table | TA |
| F10 | Accessibility compliance (violations per page, pass/fail) | audit results | bar | TA |

## G. Across the study

| # | Analysis | Needs | Output | Source |
| --- | --- | --- | --- | --- |
| G1 | Participant overview | participant table | tiles | — |
| G2 | What the sample supports: CI widths, needed-n hint, method minimums | n per measure | callout | TA, N |
| G3 | Problem → solution → result map (design rationale) | findings + solutions + results | flow | N |
| G4 | Finding confidence: sources, participants and methods behind each finding; each number paired with its explaining theme | evidence index | table | ART, N |
| G5 | Recommendation priority (impact × effort from the user) | rated recommendations | matrix | — |
| G6 | Data-cleaning note (excluded records and why) | any cleaned data | callout | TA |
| G7 | Goal attainment / target scorecard (unacceptable–minimum–target–exceeds; % meeting all goals) | targets set **before** the study | bands, table | N, TA |
| G8 | Problem discovery curve, 1−(1−p)ⁿ | issue × participant matrix | line | N, TA |
| G9 | Change per version (regressions flagged) | same metrics over iterations | slope / table | N |
| G10 | ROI / cost-benefit (inputs and assumptions shown) | volumes and costs from user | table | N, TA |
| G11 | Percentage-based combined score (user weights) | ≥2 metrics per P | bar | TA |
| G12 | z-score comparison of designs (≥10 per condition) | metrics per P per design | bar | TA |
| G13 | Single Usability Metric (SUM) | success, time (+spec), errors, satisfaction per task | bar | TA |
| G14 | Usability scorecard (task × metric; "liked but failed" flags) | A and B data per task | matrix, radar | TA |
| G15 | Metric quality check (flags raw totals, vanity metrics) | reported metrics | callout | ART |
| G16 | Leading vs lagging tags with time-lag evidence | time series | table | ART |
| G17 | HEART result map (Happiness, Engagement, Adoption, Retention, Task success) | findings tagged by HEART | grid | ART |

## H. Product metrics and growth (needs analytics exports)

| # | Analysis | Needs | Output | Source |
| --- | --- | --- | --- | --- |
| H1 | AARRR / RARRA stage funnel | counts per stage | funnel | ART |
| H2 | North Star metric tree with inputs | NSM + input metrics | tree | ART |
| H3 | Activation rate | sign-ups + "key action" definition | bar / line | ART |
| H4 | Time to value (median, users not yet there) | sign-up and key-action times | line / box | ART |
| H5 | Cohort retention (triangle, curves, day-N); acquisition cohorts and behavioural cohorts (did X vs did not) | user activity by date | heatmap, lines | ART |
| H6 | Churn and net adds | users/customers by period | line, bar | ART |
| H7 | Stickiness (DAU/MAU) | daily/monthly actives | line | ART |
| H8 | Feature adoption (breadth × frequency; first-time share; usage frequency by segment) | feature use per user | scatter | ART |
| H9 | Revenue and monetisation (MRR/ARR, ARPA, revenue per user, expansion, net revenue churn, NRR, ACV, gross margin) | revenue data | line | ART |
| H10 | Unit economics (customer lifetime = 1 ÷ churn, CLV = lifetime × ARPA, CAC, CLV:CAC) | revenue, costs, retention | table | ART |
| H11 | Acquisition by channel (acquisition rate, traffic sources, conversion, landing-page conversion, CTR, bounce, CPA/CPC/CPM) | traffic by channel | grouped bar | ART |
| H12 | Referral rate, referral conversion and viral coefficient | invites and conversions | bar | ART |
| H13 | Engagement depth (actions per user, time between actions, session length and frequency) | events per user with timestamps | box / histogram | ART |
| H14 | Subscription health (trial-to-paid, renewal, upgrade, retained time) | plan and billing events per user | bar / line | ART |
| H15 | Product-qualified leads / accounts (users or accounts crossing the user's usage threshold) | usage per user/account + threshold | bar | ART |
| H16 | Behavioural referral ("recommended in the past two weeks?" yes/no, or tracked shares) | survey item or share events | bar with CI | ART |

## I. Onboarding

| # | Analysis | Needs | Output | Source |
| --- | --- | --- | --- | --- |
| I1 | Onboarding completion and step drop-off | step reached per user | funnel | ART |
| I2 | Time to first key action (onboarding view of H4) | event times | box | ART |
| I3 | Completers vs non-completers: activation and retention | completion + retention per user | grouped bar | ART |
| I4 | Onboarding pattern inventory | screens/flows | grid tiles | ART |
| I5 | Guidance engagement (tours, tooltips: seen, dismissed, completed) | guidance events | stacked bar | ART |

## Interview questions this catalogue needs (feeds the interview module)

Study goal (formative/summative) · users, segments, recruitment, experience definition · task list and
success criteria · help policy · what was recorded and how (time start/stop, error definition) ·
questionnaire, scale, reversed items · targets set before the study · severity raters · evaluators ·
comparisons (versions, competitors, locales; between/within; counterbalancing) · iterations · field data
(logs, tickets) · metric definitions (active, key action, windows) · costs (only for ROI) · pilot ·
consent for quotes and recordings. Source: [N] pp.170–171, [TA] ch.3, [ART].

Not included: delivery metrics (lead time, cycle time, time to market, WIP, throughput, velocity). They
measure the team's process, not users, so they don't belong in a research report.

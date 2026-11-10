# Module: write (phases 4–5: outline, report, blog post)

Everything written comes from `inputs/clean/`, `answers.md` and the approved analyses. Write in the
user's first language; the second language comes later (`modules/languages.md`).

## Outline (phase 4)

Propose the outline from `references/outline.md`: section titles, what goes in each, which analyses sit
where, which images are needed. Show it as a short list. Write nothing else until the user approves it.

## Report (phase 5)

- **Summary last.** Write the sections in outline order, then the summary from them: 3–5 key findings,
  the main numbers as stat cards, one line on what's next.
- **Lead with the impact, keep the raw numbers.** In the headline places (cover headline, summary stat
  cards, the first slides) show what a result means as one number: a rate ("70% finished without help"),
  a change ("conversion 44.2%, up from 38.8%") or the result against its target ("70%, target 80%"). Put
  the raw count and n in the stat's `detail` line ("7 of 10 people"). The full raw numbers, intervals and
  tables stay in the result section and its slides. Only use numbers that are in the analyses; with small
  samples always keep the n visible, and never round in a way that flatters. Turning the designer's raw
  numbers into an impact headline is a rewording: show it and ask first.
- **The user's words stay theirs.** Use their sentences where they wrote them. If something should be cut,
  merged, moved or reworded (for clarity, length or tone), ask first, showing before and after.
- **Before and after.** For a redesign, open the solution with a `compare` block (old and new design, what
  changed) from the shots the designer gave; for a current-state study there is no comparison.
- **Problem → solution → result.** Problem: the situation and its evidence. Solution: what was designed
  or decided (from the user only; `pending` if none yet). Result: the analyses.
- **Every claim has evidence** (`evidence` ids). A claim without evidence becomes an open question.
- **Quotes** exactly as said, with participant id and evidence. Don't translate a quote in the first
  language; in the second language add a faithful translation and keep the original in `note`.
- **Plain language.** Short sentences, concrete verbs, numbers with their n and interval. No hype, no
  "significant" without a test.
- **Persian text** follows the bundled **persian-writing** skill: read `vendor/persian-writing/GUIDE.md`,
  `references/writing-style.md` and `references/orthography.md` before writing Persian. Formal-but-human
  register (است, not می‌باشد), نیم‌فاصله, Persian ی and ک, «گیومه», no translated-English sentence shapes.
  Run `reporch.py falint <project>` after writing and fix what it finds in your own text; for the
  designer's own sentences show the change and ask first. Quotes are never "corrected".
- **Action plan** only if the user wants one: suggest it once after the result section.
- **Limitations:** sample, method, what the results don't cover.

## Blog post (phase 5)

`content.json` → `blog`: the same facts as a story for readers outside the team, in the style of a
design article on Medium or a company design blog.

- **Shape:** hook (the problem in one scene or one number) → why it mattered → what we did → what we
  found (3–5 findings, each with one number or quote) → what we changed → what's next → credits.
- **Length:** 800–1,500 words. Title under 70 characters; a one-sentence dek under it.
- **Voice:** first person plural ("we") for what the team did; facts stated plainly; one idea per
  paragraph; subheadings every 2–4 paragraphs.
- **Same rules:** nothing that isn't in the report; numbers identical to the report; participants
  anonymised; at most 3 charts; image placeholders where a picture tells it better.
- The user approves the blog text like the report text.

When both are approved, `advance` (to translate, or to build if there is one language).

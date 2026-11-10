# Module: interview (phase 2)

Goal: fill every gap that blocks a correct report, in the fewest questions. Minimum 5, maximum 40 in
total, depending on how complete the material is. Ask in the user's language, in batches of 3–6
numbered questions; wait for the answers before the next batch.

## What to ask, in order

1. **Basics (first batch, always):** the designer's name and role, if not asked at the greeting (it is the
   report's author, on the cover and the slides; never a role in place of a name), report languages (default two languages, four documents: HTML and
   PDF in each; offer one language), brand (`modules/brand.md`), the study goal (find problems or
   measure/compare), and who the report is for.
2. **What kind of study, and the designs (first or second batch):** ask whether the study tested a
   **redesign** (old vs new), a **new** design, or looked at the **current** product without changing it
   (e.g. a session-recording review, analytics or interviews about today's flow). Save it as
   `meta.studyType` (`redesign`, `new`, `current-state`, `other`). For a redesign, ask for the **old and new
   design**: screenshots, a short screen recording or a prototype export of each, and what changed between
   them. For a new design, ask for its shots. For a current-state study, don't ask for a comparison; ask for
   shots of the flow only if they help the reader. Files go in `assets/images/` (or `assets/video/`); what
   isn't given yet becomes a placeholder.
3. **Study facts the outline needs:** research questions, method(s), dates, participants and segments,
   recruitment, tasks and success criteria, help policy, what was recorded and how (how time was
   measured, what counted as an error).
4. **Gaps from `reporch.py possible`:** each gap names a missing field and the analyses it would unlock.
   Ask for the ones next to data they already have first. Name the data exactly ("Do you have, for each
   participant, whether they finished task 2 without help?"). If fewer than 10 analyses are possible,
   say so and ask for the gaps that unlock the most.
4. **Definitions** the analyses depend on: targets set before the study, severity ratings and who rated
   them, "active user" or "key action" for product metrics, weights, costs. If the data implies a
   definition, state it and ask them to confirm. Never set one yourself.
5. **Problem → solution → result:** what the problem was, what they designed or decided, and what changed
   (if anything has been measured yet). If no solution exists yet, the section stays `pending`.
6. **Evidence:** consent to quote participants; whether recordings or screenshots may be shown.
7. **Images:** which designs, screenshots or charts they can give (see `modules/images.md`).

## How to ask

- One idea per question; offer choices when the answer is one of a few.
- Quote the material when asking about it ("In P03's notes you wrote 'gave up'. Was that a task failure?").
- Never ask what the material already answers.
- Record every question and answer in `answers.md` (question, answer, date). Answers are evidence: refer
  to them as `answers.md#Qn`.
- Questions that don't block the work go to the project's dependencies
  (`project.add_dependency`) with the default you'll use; ask blocking ones at once.
- After the answers, update the data profile (`profile`) and run `possible` again.

When the gaps are closed (or the user has nothing more), summarise what the report will contain and
`advance`.

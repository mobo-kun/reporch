# Study plan: basket-checkout

Written by Reporch after the interview, in the designer's language. Work top to bottom, one task at a
time. Tick `[x]` only when every acceptance criterion (AC) under the task is true; never skip a task.
If a task is blocked, write why under it and ask the designer. Add sub-tasks for this study (one per
section, analysis or chart) before starting each phase.

## P1 · Inputs read and understood

- [x] 1.1 Every input read to the end (READING.md, pass 1)
  - AC: every file in READING.md has pass 1 ticked; lines and rows read equal the totals
- [x] 1.2 Every input read again critically (pass 2)
  - AC: every fact noted has a locator (file, row, line or timestamp)
  - AC: contradictions, gaps and unclear points are written down and became questions

## P2 · Interview closed

- [x] 2.1 All blocking questions answered and saved in answers.md
  - AC: no open blocking question; non-blocking ones have a default in state.json
- [x] 2.2 Languages, brand, fonts, audience and outputs chosen
  - AC: each choice is in MEMORY.md

## P3 · Analyses

- [x] 3.1 10–40 analyses chosen from what the data supports (`reporch.py possible`), list below
  - AC: each analysis names its data, its method and its evidence
- [x] 3.2 Every number calculated with `reporch.py calc`, never by hand
  - AC: every number in content.json traces back to an input or a calculation

## P4 · Outline

- [x] 4.1 Outline proposed and approved by the designer
  - AC: the approval is in HISTORY.md

## P5 · Writing

- [x] 5.1 One sub-task per section (add them here), written only from the designer's content
  - AC: no claim, number or quote without evidence; wording changes were asked first
  - AC: Persian text follows `vendor/persian-writing` and passes `reporch.py falint`

## P6 · Translation

- [x] 6.1 Second language written with the glossary
  - AC: every field has both languages; terms match the glossary

## P7 · Build

- [x] 7.1 Report, blog and slides built (`reporch.py build`)
  - AC: `reporch.py validate --final` has no errors
- [x] 7.2 Design checked against `modules/design.md`
  - AC: slides fit the 16:9 frame without scrolling; titles two lines or fewer
- [x] 7.3 PDF made, if the designer wants one

## P8 · Review with the designer

- [x] 8.1 Designer reviewed the outputs; every change they asked for is done
  - AC: the review and changes are in HISTORY.md

## P9 · Deliver

- [ ] 9.1 `reporch.py qa` passes with no errors
- [ ] 9.2 Version kept (`reporch.py snapshot`) and the files handed over

# Module: plan, memory and history (whole project)

## The project folder

The project is **the folder the designer opened for this study** (where the agent was started). Run
`reporch.py init` there; it creates nothing anywhere else. If the agent is running somewhere else (the
home folder, the skill folder, a parent folder), stop and ask the designer which folder is the study's,
then use `init --dir <that folder>`. Never create a sibling or nested folder of your own.

## Memory and history (every session)

Chats get long, get cut, or start again; the files in the project remember for you.

- **At the start of every session**, before anything else: read `MEMORY.md`, `HISTORY.md`, `TODO.md`,
  `READING.md` and `reporch.py status`. Continue from the next open task; don't ask again what is there.
- **`MEMORY.md`** holds what is true now: decisions (`remember --kind decision`), confirmed facts
  (`--kind fact`), the designer's preferences (`--kind preference`), open questions (`--kind question`).
  When something changes, edit the old line instead of adding a contradicting one.
- **`HISTORY.md`** is the dated story: after every answer from the designer and every finished task, add
  one line (`reporch.py log <project> "…" --who designer|agent`). Summarise; don't paste whole chats.

## The study plan (`TODO.md`), after the interview

When the interview is closed (all blocking answers in `answers.md`), run `reporch.py plan <project>`. It
writes a template with phases, sub-tasks and acceptance criteria (AC). Then tailor it to this study, in
the designer's language:

- Under P3 list every analysis you will run (name, data, method). Under P5 add one sub-task per section of
  the outline, under P7 one per output (report, blog, slides, PDF).
- Each sub-task gets AC that can be checked by reading a file or running a command.
- Show the plan to the designer and adjust it if they ask.

Then **build from the plan, step by step**: take the first open task, do it, check its AC, tick it
(`- [x]`), log it, move on. Never tick a task whose AC aren't all true, and never jump ahead. If a task
is blocked, write the reason under it and ask. `reporch.py status` shows the next task; `reporch.py qa`
fails while tasks before P9 are open.

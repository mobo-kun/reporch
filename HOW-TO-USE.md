# How to use Reporch

Reporch turns your raw research material into a report you can publish: an **HTML report**, a
**blog post** and a **PDF**, in one or two languages.

## 1. Start

In Claude Code or Codex, say something like:

> Use Reporch. I ran a usability test with 8 people and want a report.

Reporch introduces itself and proposes the path below. You can change the path at any time.

## 2. Give it your material

Talk or paste: voice transcripts are welcome. Or give files:

| You have | Give it as |
| --- | --- |
| Notes, chat, voice transcript | text, `.md` |
| Interview transcripts | `.txt`, `.docx`, `.vtt`, `.srt` |
| Word or Google Docs | `.docx` (Google Docs: File → Download → Microsoft Word) |
| Spreadsheets, Google Forms, Typeform | `.csv` or `.xlsx` |
| An old report (HTML or PDF) | the file; Reporch migrates it |

Reporch asks for the participants' names first and replaces them with `P01, P02, …`. Emails, phone
numbers and card numbers are removed automatically. Nothing leaves your computer without your OK.

## 3. Answer its questions

Reporch asks in short batches (between 5 and 40 questions in total, depending on what's missing):
languages, brand colour and logo, what the study was for, and the data that would allow more analyses.
Answer what you can; "I don't know" is a fine answer.

## 4. Review

- **Analyses:** Reporch runs 10–40 analyses your data supports and shows them to you.
- **Outline:** you approve the outline before the full text is written.
- **Your words stay yours:** anything Reporch wants to cut, merge or reword is asked first.
- **Images:** where a picture would help, the report holds a placeholder that says exactly what is
  needed (a screen, an analytics screenshot, a wireframe…). Put the files in the project's `assets/`.

## 5. Get the outputs

In `out/` inside your study folder:

- `report.<lang>.html`: works offline, with a table of contents, slides and charts
- `blog.<lang>.html`: the same findings as an article (Markdown on request)
- `report.<lang>.pdf`

Every rebuild keeps the previous outputs in `versions/`.

## The path

collect → interview → analysis → outline → write → translate → build → check

You can stop at any point and continue later: Reporch remembers where you were.

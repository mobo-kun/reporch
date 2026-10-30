# Module: intake (phase 1, collect)

Goal: every file the user gives is in the project, readable, anonymised, and described as data fields.

1. **Project.** Ask where their research folder is (default: the current folder). Run
   `reporch.py init <slug> --root <folder> --languages <codes>` (languages are confirmed in the
   interview; start with the default two). The slug is short, lowercase, hyphenated.
2. **Take the material.** Accept anything they paste or speak (voice transcripts are welcome: save them
   as `.md` in a temporary place, then ingest) and files: `.txt`, `.md`, `.vtt`, `.srt`, `.docx`
   (Google Docs: File → Download → .docx), `.csv`, `.tsv`, `.xlsx` (Google Forms and Typeform exports).
   PDF and HTML *reports* go to `modules/migrate.md`. Images, audio, video, FigJam and Miro come in v2:
   ask for a text export or a description for now.
3. **Names first.** Before ingesting, ask for the participants' names as they appear in the material and
   propose ids `P01, P02, …`. Save the map as `names.json` **outside** the project's `inputs/clean/`
   (keep it in the project root; it never goes into any output). Then run
   `reporch.py ingest <project> FILE… --names names.json`.
4. **Check the index.** `inputs/index.json` lists every file, its kind, tables, and how many emails,
   phones, card numbers and names were removed. Tell the user the counts (not the values). If a first
   name was ambiguous (two participants share it), it is left in place: ask which participant it is.
5. **Read everything.** Read every file in `inputs/clean/` fully. Do not skim; do not summarise yet.
6. **Data profile.** Decide which field keys from `references/analyses.json` (`fields`) the material
   contains, and record them with `reporch.py profile <project> --fields …`. Only list a field when the
   data is actually there for the participants or rows it claims to cover.
7. **What it supports.** Run `reporch.py possible <project>`. Keep the result for the interview.
8. Tell the user, in two or three sentences, what you received and what it supports. Then
   `reporch.py advance <project>`.

Never send the material anywhere. If a tool would upload it, ask first (rule 4).

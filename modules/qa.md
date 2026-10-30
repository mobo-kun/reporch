# Module: qa (phase 8)

Reports go public. Nothing is "ready" until `reporch.py qa <project>` reports **0 errors**, and every
warning is either fixed or explained to the user.

| Check | What it catches | Level |
| --- | --- | --- |
| content | anything `validate --final` finds (translations, evidence, outline, charts vs tables, 10–40 analyses) | error |
| numbers | a number in a finding that isn't in the analysis table or its `values` | warning: confirm the source with the user, then add it to `values` or correct the text |
| quotes | a quote that doesn't appear word for word in `inputs/clean/` or `answers.md` | error: never paraphrase a quote |
| outputs | a missing report or blog file | error |
| size / offline | a file over 40 MB, or one that loads anything from the network | error |
| language / rtl / orthography | another script in a single-language document; a Persian page not right-to-left; Arabic ي/ك | error |
| credit | the footer credit missing | error |
| brand / contrast | a brand colour that isn't a colour, or has no shade readable on white | error |
| layout / charts / script | sideways scroll at 360 px, charts not drawn, script errors (needs Playwright) | error, or skipped |
| pdf | a PDF that isn't valid or is over 40 MB | error, or skipped |
| images | placeholders still waiting for files | warning |

Then read the outputs yourself, once, as a reader would:

1. Every finding says what the data says, with n and its interval; nothing more.
2. The user's sentences are unchanged unless they approved the change.
3. The summary's numbers match the result section.
4. The blog post doesn't say anything the report doesn't.
5. Persian reads naturally (formal-but-human, ZWNJ, Persian digits); English is plain.

A **skipped** check is not a pass. Tell the user what wasn't checked and why (for example, "Playwright
isn't installed, so I couldn't check the phone layout").

Finally, give the user the paths of the outputs, the list of image placeholders still open, and any
dependencies still waiting for their answer. Then `advance` to `done`.

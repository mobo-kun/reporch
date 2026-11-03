# Module: build (phase 7)

1. `reporch.py validate <project> --final` must report 0 errors. Fix the content (or ask the user);
   never weaken the check.
2. `reporch.py snapshot <project>` keeps the previous outputs as a version.
3. `reporch.py build <project>` writes, for each language in `meta.languages`:
   - `out/report.<lang>.html`: one offline file (fonts, charts and images inlined), table of contents
     (sticky on desktop, drawer on phones), reading progress bar, a 16:9 slide deck built from the content (`modules/design.md`),
     zoomable images, footer credit.
   - `out/blog.<lang>.html`: the blog post as one offline article page.
   - with `--markdown`: `out/report.<lang>.md` and `out/blog.<lang>.md`.
4. `reporch.py pdf <project>` renders `out/report.<lang>.pdf` from the HTML with headless Chromium
   (Playwright). If Playwright isn't installed, ask the user before installing it
   (`python3 -m pip install playwright && python3 -m playwright install chromium`). If they decline,
   tell them to open the HTML in Chrome and print to PDF (the print layout is built in).
5. Run QA (`modules/qa.md`) before telling the user the outputs are ready.

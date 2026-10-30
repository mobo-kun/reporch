# Module: migrate an existing report

Goal: the designer's old report (HTML or PDF) in Reporch's template, with **nothing lost and nothing
changed** without their OK. Then the usual outputs: HTML report, blog post, PDF.

1. **Project.** `reporch.py init <slug> --root <their folder> --languages <the report's language>`.
2. **Migrate.** `reporch.py migrate <project> <report.html|.pdf> --lang <code>`. It copies the original to
   `inputs/original/`, writes `migration/inventory.json` (every section, heading, paragraph, list item,
   table, chart and image in the original order) and a draft `content.json`, and prints how many content
   units were kept. It must say **kept N/N**. If not, run `reporch.py lossless <project>`, which lists the
   missing pieces, and fix the draft until it is complete. Never continue with anything missing.
   - **PDF:** needs `pypdf` (ask before installing). Without it, read the PDF with your own tools and
     build the same inventory by hand. Tables and charts in a PDF are often pictures: ask for the numbers
     and redraw them (if the designer has no numbers, keep the picture). Ask for the original images
     rather than using images cut out of the PDF.
3. **Ask, in the designer's language** (the command prints the questions):
   - which outline part each section is (summary, problem, solution, result…), when the title doesn't say;
   - whether to keep the original order (sections nest under the outline parts) or move them; moving needs
     their OK, section by section;
   - who said each quote with no participant id (`P??` in the draft);
   - what the summary and the solution say, if the original has none (or keep them as "still needed");
   - the authors and dates;
   - the original image files.
4. **Keep the words.** The draft holds the original text exactly. Shortening, merging or rewording is a
   question for the designer, showing before and after. Duplicates (for example a title that appears
   twice) are also only removed with their OK.
5. **Charts.** Chart.js charts become Reporch charts drawn from tables holding the same numbers. If a
   chart's data couldn't be read, the draft has a "still needed" block: ask for the numbers.
6. **Second language.** If the designer wants two languages, translate after the structure is approved
   (`modules/languages.md`). If the original already has both languages, map each one to its language
   instead of translating.
7. **Analyses.** A migrated report keeps its own findings. If it has fewer than 10 analyses, offer more
   from the original's data (`modules/analysis.md`); add them only with the designer's OK.
8. **Preview** any time: `reporch.py build <project> --draft`. When the questions are answered and
   `lossless` is complete, continue with the normal build and QA. QA fails while anything of the
   original is missing.

# Module: design (phase 7, and whenever the look is discussed)

Reporch's theme (`references/theme.md`) sets colours, fonts, the dot pattern and the glow. On top of it,
apply the craft rules from **taste-skill** (bundled in `vendor/taste-skill/`, MIT, pinned). Read
`vendor/taste-skill/references/tells.md` and `type.md` before changing any template or making slides.

## What Reporch takes from taste-skill

- Titles two lines or fewer at every width; cut words before shrinking type.
- Two or three type sizes do the work, far apart; text 16–20 px with 45–75 characters per line.
- One ground, one ink, one accent; running text in full ink, never soft grey.
- Surfaces separated by space or a small tone step; shadows only on what floats (menus, lightbox).
- No eyebrows or pill badges added by Reporch, no index numbers (01, 02), no emoji, no gradient text.
- One dominant image beats several small ones; nothing sits on top of a title.
- Proof by measuring, not by eye: overflow, contrast, line count, slide fit.

## Where Reporch's theme wins

The dot pattern (kept, at about 1.1:1 contrast), the blurred glow at the top of the page, the brand
primary colour (even if it is violet), and cards for stats and charts in the long-form report. A study's
own content (e.g. a label the designer wrote) is never removed for style; ask first.

## Fonts

Body text, tables, navigation and charts: **Vazirmatn**. A brand font (e.g. Lahzeh, from
`<project>/assets/fonts/`) is used **only for titles, subtitles and big numbers** (`--font-display`).

## Slides

`build` makes a 16:9 deck inside every report (Slides button, or open `report.<lang>.html?slides`):
cover, then each section as slides: one analysis per slide (finding beside its chart), up to three quotes
per slide, text grouped to a slide's worth, tables six rows per slide, action plan, open questions, end.
Arrow keys, click, Home/End, Esc. Check every slide fits without scrolling and every title is two lines
or fewer; if a slide is too dense, ask the designer whether to split or shorten that content (never cut
it yourself).

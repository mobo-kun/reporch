# Module: brand (phase 2, first batch)

Decide the report's look from what the user says in their **first messages**; don't ask about a company
they haven't named.

- **They named Nobitex (نوبیتکس)** in their own words (`intake.mentions_brand`): use the default theme
  as it is. Ask only for the Nobitex logo (SVG or PNG) and tell them to put the **Lahzeh** font files in
  `<project>/assets/fonts/` if they want the brand font. Use Vazirmatn until those files exist.
- **Anyone else:** ask for their primary colour (hex, or a description you turn into a hex they
  confirm) and their logo. Use Vazirmatn. Don't mention any other company or font.
- Logos and fonts are copied into `<project>/assets/` and never into the skill folder.
- Record the brand in `content.json` → `meta.brand` (`primary`, `logo`, `font`).

# Module: languages and glossary (phases 2 and 6)

- **Default:** two languages, each output once per language; every document has one language only. Ask
  which two (usually the user's language and English). One language is fine.
- **Writing the second language:** translate the user's approved text faithfully. Keep research terms
  in English inside the other language (SUS, SEQ, Think Aloud, CTA, NPS, A/B test). Numbers stay the
  same; only their digits change (Persian digits in Persian text).
- **Glossary:** `content.json` → `glossary` holds every research term used, with a one-line meaning in
  each language. The user may edit it; their wording wins.
- **Review:** the user approves the translated text before build. Mark untranslated texts with
  `"_pendingTranslation": true` while drafting; `validate --final` refuses them.
- Persian text: formal-but-human register, ZWNJ (نیم‌فاصله), Persian ی and ک, Persian digits, «گیومه», no
  em dashes. English: plain, concrete, short sentences.

# Module: images and placeholders

Pictures make a report readable: the screen the problem happened on, the redesigned screen, the analytics
view behind a number. Reporch never draws or generates a fake screenshot; it asks for the real one.

- Wherever a picture would help a reader understand a finding, add an `image` block with a
  **placeholder** (`kind` + `description`) instead of `src`:

```json
{"type": "image", "caption": {"en": "The checkout's payment step on mobile"},
 "placeholder": {"kind": "screenshot",
   "description": "Mobile screenshot of the checkout payment step, before the redesign, with the 'Pay' button visible (P03 and P07 missed it)."}}
```

- **Kinds:** `design` (a designed page or flow), `screenshot` (the live product), `analytics` (a view
  from an analytics or replay tool), `illustration`, `wireframe`, `photo` (of a session or setting, with
  consent), `diagram`, `video` (a short clip), `logo`, `other`.
- **Description:** what exactly to capture: which screen, state, device, which part to show, and why
  (the finding it supports). Specific enough that someone else could take the picture.
- Placeholders render as a dashed frame with the description, so the report is usable before the images
  arrive. List them all for the user at the end of the write phase.
- When the user gives a file, put it in `<project>/assets/images/` and replace the placeholder with
  `"src": "assets/images/<file>"` and an `alt` text. Keep their caption wording.
- Video and GIF: short clips only, compressed; the whole HTML must stay under 40 MB. The PDF shows the
  first frame (or a `poster` image).
- Faces and personal data in images: ask the user to blur them before giving the file.

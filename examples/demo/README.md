# Demo: Basket checkout (fictional)

Everything here is invented: the grocery app "Basket", the eight participants and every number. It shows
what Reporch produces from a usability test, a funnel export and an A/B test.

- `reporch-projects/basket-checkout/inputs/clean/`: the (anonymised) inputs
- `reporch-projects/basket-checkout/content.json`: the report content in English and Persian, 13 analyses
- `tools/make_demo.py` regenerates all of it, computing every number with Reporch's own statistics

Build the outputs (HTML report and blog in both languages, plus Markdown):

```bash
python3 scripts/reporch.py build examples/demo/reporch-projects/basket-checkout --markdown
```

Then open `examples/demo/reporch-projects/basket-checkout/out/report.en.html` in a browser.

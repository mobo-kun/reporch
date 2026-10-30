"""Render the report HTML to PDF with headless Chromium (Playwright), if it is installed.

Playwright is optional: `available()` says whether it can run, and the build module asks the user before
installing it. Without it, the HTML's print layout lets the user print to PDF from Chrome.
"""
import os
import pathlib


def available():
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
        return True
    except ImportError:
        return False


INSTALL = "python3 -m pip install playwright && python3 -m playwright install chromium"


def render(html_path, pdf_path, timeout_ms=60000):
    from playwright.sync_api import sync_playwright
    url = pathlib.Path(os.path.abspath(html_path)).as_uri() + "?print"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page(viewport={"width": 1100, "height": 1400})
            page.emulate_media(media="print")
            page.goto(url, wait_until="load", timeout=timeout_ms)
            page.wait_for_function("window.__REPORCH_CHARTS_READY__ === true", timeout=timeout_ms)
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(300)
            page.pdf(path=pdf_path, format="A4", print_background=True, prefer_css_page_size=True)
        finally:
            browser.close()
    return pdf_path

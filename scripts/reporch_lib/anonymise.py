"""Remove personal data before anything is analysed or written (R4).

- Names: replaced by participant ids from a map the user confirms ({"Sara Ahmadi": "P01"}); first names
  alone are replaced too when they are unambiguous.
- Emails, phone numbers (Latin or Persian digits), card numbers and IBANs: replaced by a tag.
The result reports how many of each were replaced, never the values themselves.
"""
import re

_FA = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+")
IBAN = re.compile(r"\b[A-Z]{2}\d{2}(?:[ ]?[\dA-Z]{4}){3,7}(?:[ ]?[\dA-Z]{1,4})?\b")
CARD = re.compile(r"(?<![\d.])(?:\d{4}[- ]?){3}\d{4}(?!\d|\.\d)")
PHONE = re.compile(r"(?<![\w.])(?:\+|00)?\d[\d\s().-]{8,16}\d(?!\w|\.\d)")
TAGS = {"email": "[email removed]", "iban": "[IBAN removed]", "card": "[card number removed]",
        "phone": "[phone removed]"}


def _digits(m):
    return sum(ch.isdigit() for ch in m.group(0))


def anonymise(text, names=None):
    """Return (clean text, counts). Persian digits are matched as digits but kept elsewhere."""
    counts = {k: 0 for k in ("name", *TAGS)}
    latin = text.translate(_FA)            # same length, so match positions line up with text

    spans = []
    for kind, rx in (("email", EMAIL), ("iban", IBAN), ("card", CARD), ("phone", PHONE)):
        for m in rx.finditer(latin):
            if kind == "phone" and not 10 <= _digits(m) <= 15:
                continue
            if any(s < m.end() and m.start() < e for s, e, _ in spans):
                continue
            spans.append((m.start(), m.end(), kind))
    out, last = [], 0
    for s, e, kind in sorted(spans):
        out.append(text[last:s]); out.append(TAGS[kind]); last = e; counts[kind] += 1
    out.append(text[last:])
    text = "".join(out)

    for real, pid in sorted((names or {}).items(), key=lambda kv: -len(kv[0])):
        for variant in _variants(real, names):
            rx = re.compile(r"(?<![\w؀-ۿ])" + re.escape(variant) + r"(?![\w؀-ۿ])", re.I)
            text, n = rx.subn(pid, text)
            counts["name"] += n
    return text, counts


def _variants(real, names):
    yield real
    first = real.split()[0]
    others = [n.split()[0] for n in names if n != real]
    if first != real and first not in others and len(first) > 2:
        yield first

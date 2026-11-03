"""Theme tokens: palette scales, contrast checks and the CSS they produce (references/theme.md).

Each base colour is step 500; lighter steps mix it with white, darker steps with black. `text_step`
picks the lightest step that reaches WCAG AA (4.5:1) on white, so coloured text stays readable.
A brand primary from the user replaces `primary` and gets the same treatment.
"""

PALETTE = {
    "primary": "#754EC6",
    "green": "#2BAD87",
    "red": "#E54C50",
    "blue": "#4483C2",
    "teal": "#67C6C3",
    "indigo": "#5338EA",
    "pink": "#D278C8",
    "rose": "#E0547F",
    "amber": "#F5A524",
}
GLOW = ("#9747FF", 0.10)          # the large blurred circle
NEUTRAL = "#6B6B76"               # greys for text, borders and the dot pattern
STEPS = {50: 0.92, 100: 0.84, 200: 0.68, 300: 0.48, 400: 0.24, 500: 0.0,
         600: -0.16, 700: -0.32, 800: -0.48, 900: -0.64}
# Chart series order: distinct hues first, so neighbouring series never look alike.
CHART_ORDER = ["primary", "green", "amber", "blue", "rose", "teal", "indigo", "pink", "red"]


def _rgb(hex_):
    h = hex_.lstrip("#")
    if len(h) != 6:
        raise ValueError(f"{hex_!r} is not a #RRGGBB colour")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _hex(rgb):
    return "#" + "".join(f"{max(0, min(255, round(c))):02X}" for c in rgb)


def mix(hex_, amount):
    """amount > 0 mixes toward white, < 0 toward black."""
    r = _rgb(hex_)
    target = 255 if amount > 0 else 0
    a = abs(amount)
    return _hex(tuple(c + (target - c) * a for c in r))


def scale(hex_):
    return {step: mix(hex_, amt) for step, amt in STEPS.items()}


def luminance(hex_):
    def ch(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(c) for c in _rgb(hex_))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def text_step(hex_, on="#FFFFFF", ratio=4.5):
    for step, value in scale(hex_).items():
        if step >= 500 and contrast(value, on) >= ratio:
            return step
    return 900


def tokens(primary=None):
    pal = dict(PALETTE)
    if primary:
        _rgb(primary)
        pal["primary"] = primary.upper()
    return {name: scale(base) for name, base in pal.items()} | {"neutral": scale(NEUTRAL)}


def css(primary=None):
    t = tokens(primary)
    lines = [":root {"]
    for name, sc in t.items():
        for step, value in sc.items():
            lines.append(f"  --{name}-{step}: {value};")
        lines.append(f"  --{name}-text: var(--{name}-{text_step(sc[500])});")
    g, a = GLOW
    lines += [
        f"  --glow: rgba({', '.join(str(c) for c in _rgb(g))}, {a});",
        "  --bg: #FFFFFF;",
        "  --ink: #1C1B22;",
        "  --ink-soft: var(--neutral-700);",
        "  --line: var(--neutral-100);",
        "  --dot: var(--neutral-50);",             # about 1.1:1 on white: a quiet pattern, not a grey screen
        "  --credit: var(--neutral-300);",
        "  --chart: " + ", ".join(f"var(--{n}-500)" for n in CHART_ORDER) + ";",
        "}",
    ]
    return "\n".join(lines) + "\n"

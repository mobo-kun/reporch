#!/usr/bin/env python3
"""Generate the fictional demo project (examples/demo) from an invented dataset.

Everything here is fictional: the app "Basket", the participants and every number. The numbers in
content.json are computed from the raw data below with Reporch's own statistics, so the demo shows
exactly what Reporch produces from such inputs. Run: python3 tools/make_demo.py
"""
import csv
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from reporch_lib import stats  # noqa: E402

PROJECT = os.path.join(ROOT, "examples", "demo", "basket-checkout")
P = [f"P{i:02d}" for i in range(1, 9)]
DEVICE = dict(zip(P, ["mobile"] * 4 + ["desktop"] * 4))
TASKS = ["T1", "T2", "T3", "T4"]
TASK_NAMES = {
    "T1": ("Find a product and add it to the basket", "پیدا کردن محصول و افزودن به سبد"),
    "T2": ("Choose a delivery slot", "انتخاب زمان تحویل"),
    "T3": ("Apply a discount code", "اعمال کد تخفیف"),
    "T4": ("Pay", "پرداخت"),
}
# 1 = unaided success, "A" = assisted, 0 = failed
SUCCESS = {
    "P01": [1, 1, 0, 1], "P02": [1, "A", 0, 1], "P03": [1, 1, "A", 0], "P04": [1, 0, 0, 1],
    "P05": [1, 1, 1, 1], "P06": [1, "A", 0, "A"], "P07": [1, 1, 0, 0], "P08": [1, 1, "A", 1],
}
TIMES = {"T1": [32, 41, 28, 55, 30, 38, 47, 35], "T2": [64, 95, 58, 120, 52, 88, 61, 70],
         "T3": [140, 160, 98, 175, 72, 150, 165, 110], "T4": [45, 50, 90, 48, 40, 85, 95, 52]}
SEQ = {"T1": [6, 6, 7, 5, 7, 6, 6, 7], "T2": [5, 4, 6, 3, 6, 4, 5, 6],
       "T3": [2, 2, 4, 1, 5, 3, 2, 3], "T4": [6, 5, 3, 6, 7, 4, 2, 6]}
SUS = {
    "P01": [4, 2, 4, 2, 4, 2, 4, 2, 4, 2], "P02": [3, 2, 4, 2, 3, 3, 4, 2, 3, 2],
    "P03": [3, 3, 3, 2, 3, 3, 4, 3, 3, 2], "P04": [2, 4, 3, 3, 2, 4, 3, 3, 2, 3],
    "P05": [5, 1, 5, 1, 4, 1, 5, 1, 5, 1], "P06": [3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
    "P07": [2, 3, 3, 2, 3, 4, 3, 4, 2, 3], "P08": [4, 2, 4, 1, 4, 2, 5, 2, 4, 2],
}
ISSUES = [  # id, en, fa, severity (designer's 1–4), participants
    ("I1", "The discount field is hidden behind “More options”", "فیلد کد تخفیف پشت «گزینه‌های بیشتر» پنهان است", 4,
     ["P01", "P02", "P03", "P04", "P06", "P07"]),
    ("I2", "Available delivery slots look disabled", "زمان‌های تحویلِ آزاد غیرفعال به نظر می‌رسند", 3, ["P02", "P04", "P06"]),
    ("I3", "The Pay button is below the fold on mobile", "دکمه‌ی پرداخت در موبایل زیر لبه‌ی صفحه است", 4, ["P03", "P07", "P06"]),
    ("I4", "The card error message doesn't say what to fix", "پیام خطای کارت نمی‌گوید چه چیزی را باید درست کرد", 2, ["P06", "P07"]),
    ("I5", "The basket count doesn't update after adding", "شمار سبد بعد از افزودن به‌روز نمی‌شود", 1, ["P04"]),
]
THEMES = [  # en, fa, participants
    ("Couldn't find where to enter the code", "جای واردکردن کد را پیدا نکردند", ["P01", "P02", "P03", "P04", "P06", "P07"]),
    ("Liked how fast product search was", "سرعت جست‌وجوی محصول را دوست داشتند", ["P01", "P03", "P05", "P07", "P08"]),
    ("Unsure whether a slot was available", "مطمئن نبودند زمان تحویل آزاد است", ["P02", "P04", "P06"]),
    ("Didn't see the Pay button", "دکمه‌ی پرداخت را ندیدند", ["P03", "P06", "P07"]),
]
QUOTES = [  # evidence id, participant, en, fa, locator
    ("E6", "P02", "I know I have a code, but there's nowhere to put it.", "می‌دانم کد دارم، ولی جایی برای واردکردنش نیست.", "session 2, 14:05"),
    ("E7", "P07", "So… where do I pay? Is it scrolling?", "خب… کجا پرداخت کنم؟ باید اسکرول کنم؟", "session 7, 22:40"),
    ("E8", "P04", "These grey times, are they full or can I pick them?", "این ساعت‌های خاکستری پُرند یا می‌شود انتخابشان کرد؟", "session 4, 09:12"),
    ("E9", "P05", "Search is quick, I found the milk straight away.", "جست‌وجو سریع است، شیر را همان اول پیدا کردم.", "session 5, 03:30"),
]
FUNNEL = [("Basket", "سبد", 12400), ("Delivery", "تحویل", 8060), ("Payment", "پرداخت", 5210), ("Paid", "پرداخت‌شده", 3890)]
AB = {"old": (1940, 5000), "new": (2210, 5000)}


COLS = {  # column headers in both languages
    "task": ("task", "تسک"), "success": ("success", "موفقیت"), "low": ("low", "کران پایین"), "high": ("high", "کران بالا"),
    "successes": ("successes", "موفق"), "n": ("n", "n"), "unaided": ("unaided", "بدون کمک"), "assisted": ("assisted", "با کمک"),
    "failed": ("failed", "ناموفق"), "geometric mean (s)": ("geometric mean (s)", "میانگین هندسی (ثانیه)"),
    "median (s)": ("median (s)", "میانه (ثانیه)"), "SEQ mean": ("SEQ mean", "میانگین SEQ"), "participant": ("participant", "شرکت‌کننده"),
    "SUS": ("SUS", "SUS"), "issue": ("issue", "مشکل"), "participants": ("participants", "شرکت‌کننده‌ها"), "severity": ("severity", "شدت"),
    "theme": ("theme", "تم"), "step": ("step", "گام"), "users": ("users", "کاربران"), "from top": ("from top", "از ابتدا"),
    "drop": ("drop", "ریزش"), "variant": ("variant", "نسخه"), "conversion": ("conversion", "تبدیل"), "paid": ("paid", "پرداخت‌شده"),
    "visitors": ("visitors", "بازدیدکننده"), "share found": ("share found", "سهم یافته‌شده"), "device": ("device", "دستگاه"),
    "observed": ("observed", "مشاهده‌شده"), "mobile": ("mobile", "موبایل"), "desktop": ("desktop", "دسکتاپ"),
}


def r1(x):
    """One decimal, rounding half up (6.25 -> 6.3), as QA does."""
    return f"{round(x + 1e-9, 1):.1f}"


def T(en, fa):
    return {"en": en, "fa": fa}


def fa_num(x):
    return str(x).translate(str.maketrans("0123456789.", "۰۱۲۳۴۵۶۷۸۹٫"))


def pct(x, d=1):
    """Percent with up to d decimals (12.5, not 12), never rounding half to even."""
    v = round(x * 100 + 1e-9, d)
    return f"{v:.{d}f}".rstrip("0").rstrip(".")


def write_inputs():
    inp = os.path.join(PROJECT, "inputs", "clean")
    os.makedirs(inp, exist_ok=True)
    with open(os.path.join(inp, "tasks.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["participant", "device", "task", "result", "time_s", "seq"])
        for i, p in enumerate(P):
            for j, t in enumerate(TASKS):
                r = SUCCESS[p][j]
                w.writerow([p, DEVICE[p], t, {1: "success", 0: "fail", "A": "assisted"}[r], TIMES[t][i], SEQ[t][i]])
    with open(os.path.join(inp, "sus.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["participant"] + [f"q{i}" for i in range(1, 11)])
        for p in P:
            w.writerow([p] + SUS[p])
    with open(os.path.join(inp, "analytics-funnel.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["step", "users"])
        for name, _, n in FUNNEL:
            w.writerow([name, n])
    with open(os.path.join(inp, "ab-test.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["variant", "paid", "visitors"])
        for k, (s, n) in AB.items():
            w.writerow([k, s, n])
    with open(os.path.join(inp, "session-notes.md"), "w", encoding="utf-8") as f:
        f.write("# Session notes (fictional)\n\n")
        for e, p, en, _, loc in QUOTES:
            f.write(f"- {p} ({loc}): \"{en}\"\n")
        for i, en, _, sev, ps in ISSUES:
            f.write(f"- Issue {i} (severity {sev}): {en}. Seen with {', '.join(ps)}.\n")


def analyses():
    out = []
    # AN1 success with adjusted Wald CI
    rows = []
    for j, t in enumerate(TASKS):
        s = sum(1 for p in P if SUCCESS[p][j] == 1)
        r = stats.proportion(s, len(P))
        rows.append([t, round(r["rate"], 4), round(r["low"], 4), round(r["high"], 4), s, len(P)])
    worst = min(rows, key=lambda r: r[1])
    out.append({"id": "AN1", "catalogueId": "A1", "title": T("Unaided task success", "موفقیت بدون کمک در هر تسک"),
                "finding": T(f"Everyone found and added a product (8 of 8). Applying a discount code was the hardest task: "
                             f"{worst[4]} of 8 did it alone ({pct(worst[1])}%, 95% CI {pct(worst[2])}–{pct(worst[3])}%).",
                             f"همه محصول را پیدا کردند و به سبد افزودند (۸ از ۸). اعمال کد تخفیف سخت‌ترین تسک بود: "
                             f"{fa_num(worst[4])} نفر از ۸ نفر بدون کمک انجامش دادند ({fa_num(pct(worst[1]))}٪، بازه‌ی اطمینان ۹۵٪: "
                             f"{fa_num(pct(worst[2]))} تا {fa_num(pct(worst[3]))}٪)."),
                "table": {"columns": ["task", "success", "low", "high", "successes", "n"], "rows": rows,
                          "format": {"success": "percent", "low": "percent", "high": "percent"}},
                "chart": {"kind": "rangeBar", "x": "task", "series": ["success"], "range": ["low", "high"]},
                "method": T("Adjusted Wald 95% CI", "بازه‌ی اطمینان ۹۵٪ به روش Adjusted Wald"), "evidence": ["E2"]})
    # AN2 levels of success
    rows = []
    for j, t in enumerate(TASKS):
        vals = [SUCCESS[p][j] for p in P]
        rows.append([t, vals.count(1), vals.count("A"), vals.count(0)])
    out.append({"id": "AN2", "catalogueId": "A2", "title": T("Levels of success", "سطح موفقیت"),
                "finding": T("Help mattered most in the discount and delivery tasks: 2 people needed help in each, "
                             "and 5 people could not apply the code at all.",
                             "کمک بیشتر از همه در تسک تخفیف و تحویل لازم شد: در هر کدام ۲ نفر به کمک نیاز داشتند و "
                             "۵ نفر اصلاً نتوانستند کد را اعمال کنند."),
                "table": {"columns": ["task", "unaided", "assisted", "failed"], "rows": rows,
                          "labels": {"unaided": T("unaided", "بدون کمک"), "assisted": T("assisted", "با کمک"), "failed": T("failed", "ناموفق")}},
                "chart": {"kind": "stackedBar", "x": "task", "series": ["unaided", "assisted", "failed"]},
                "evidence": ["E2"]})
    # AN3 time on task
    rows = []
    for t in TASKS:
        r = stats.time_summary(TIMES[t])
        rows.append([t, round(r["geometricMean"], 1), round(r["low"], 1), round(r["high"], 1), r["median"]])
    t3 = rows[2]
    out.append({"id": "AN3", "catalogueId": "A3", "title": T("Time on task", "زمان انجام تسک"),
                "finding": T(f"The discount task took longest: a geometric mean of {t3[1]:.0f} seconds "
                             f"(95% CI {t3[2]:.0f}–{t3[3]:.0f} s), about four times the product task.",
                             f"تسک تخفیف از همه طولانی‌تر بود: میانگین هندسی {fa_num(round(t3[1]))} ثانیه "
                             f"(بازه‌ی اطمینان ۹۵٪: {fa_num(round(t3[2]))} تا {fa_num(round(t3[3]))} ثانیه)، حدود چهار برابر تسک محصول."),
                "table": {"columns": ["task", "geometric mean (s)", "low", "high", "median (s)"], "rows": rows},
                "chart": {"kind": "rangeBar", "x": "task", "series": ["geometric mean (s)"], "range": ["low", "high"]},
                "method": T("Geometric mean, CI on log times; all attempts", "میانگین هندسی، بازه‌ی اطمینان روی لگاریتم زمان؛ همه‌ی تلاش‌ها"),
                "evidence": ["E2"]})
    # AN4 SEQ
    rows = []
    for t in TASKS:
        r = stats.mean_ci(SEQ[t])
        rows.append([t, round(r["mean"], 2), round(r["low"], 2), round(r["high"], 2)])
    out.append({"id": "AN4", "catalogueId": "A5", "title": T("Ease per task (SEQ, 1–7)", "سهولت هر تسک (SEQ، ۱ تا ۷)"),
                "finding": T(f"People rated the discount task hardest ({r1(rows[2][1])} of 7) and the product task easiest ({r1(rows[0][1])}).",
                             f"شرکت‌کننده‌ها تسک تخفیف را سخت‌ترین ({fa_num(r1(rows[2][1]))} از ۷) و تسک محصول را آسان‌ترین ({fa_num(r1(rows[0][1]))}) دانستند."),
                "table": {"columns": ["task", "SEQ mean", "low", "high"], "rows": rows},
                "chart": {"kind": "rangeBar", "x": "task", "series": ["SEQ mean"], "range": ["low", "high"]},
                "method": T("t-based 95% CI", "بازه‌ی اطمینان ۹۵٪ بر پایه‌ی t"), "evidence": ["E2"]})
    # AN5 SUS
    s = stats.sus([SUS[p] for p in P])
    out.append({"id": "AN5", "catalogueId": "B1", "title": T("System Usability Scale", "مقیاس کاربردپذیری سیستم (SUS)"),
                "values": {"mean": round(s["mean"], 2), "low": round(s["low"], 2), "high": round(s["high"], 2), "n": len(P)},
                "finding": T(f"The checkout scored {r1(s['mean'])} on SUS (95% CI {round(s['low'])}–{round(s['high'])}), "
                             "below the common average of 68. With 8 people the interval is wide.",
                             f"امتیاز SUS فرایند پرداخت {fa_num(r1(s['mean']))} بود (بازه‌ی اطمینان ۹۵٪: "
                             f"{fa_num(round(s['low']))} تا {fa_num(round(s['high']))})، پایین‌تر از میانگین رایج ۶۸. با ۸ نفر این بازه پهن است."),
                "table": {"columns": ["participant", "SUS"], "rows": [[p, sc] for p, sc in zip(P, s["scores"])]},
                "chart": {"kind": "bar", "x": "participant", "series": ["SUS"]},
                "method": T("Standard SUS scoring; t-based 95% CI; benchmark 68 (Sauro & Lewis)",
                            "امتیازدهی استاندارد SUS؛ بازه‌ی اطمینان ۹۵٪ بر پایه‌ی t؛ معیار ۶۸ (Sauro و Lewis)"),
                "evidence": ["E3"]})
    # AN6 issues by frequency and severity
    rows = [[i, len(ps), sev] for i, _, _, sev, ps in ISSUES]
    out.append({"id": "AN6", "catalogueId": "D2", "values": {"n": len(P)}, "title": T("Issues by frequency and severity", "مشکل‌ها بر اساس تکرار و شدت"),
                "finding": T("Two severe issues (4 of 4) explain most failures: the hidden discount field (6 of 8 people) and the Pay button below the fold (3 of 8).",
                             "دو مشکل شدید (۴ از ۴) بیشترِ شکست‌ها را توضیح می‌دهند: فیلد پنهانِ کد تخفیف (۶ نفر از ۸ نفر) و دکمه‌ی پرداختِ زیر لبه‌ی صفحه (۳ نفر از ۸ نفر)."),
                "table": {"columns": ["issue", "participants", "severity"], "rows": rows},
                "chart": {"kind": "barHorizontal", "x": "issue", "series": ["participants"]},
                "method": T("Severity rated by the designer (1 low – 4 critical)", "شدت را طراح تعیین کرده است (۱ کم تا ۴ بحرانی)"),
                "evidence": ["E1"]})
    # AN7 themes
    rows = [[T(en, fa), len(ps)] for en, fa, ps in THEMES]
    out.append({"id": "AN7", "catalogueId": "D1", "values": {"n": len(P)}, "title": T("Themes", "تم‌ها"),
                "finding": T("The most common theme was not finding where to enter the code (6 of 8). The most common positive theme was fast product search (5 of 8).",
                             "رایج‌ترین تم پیدا نکردن جای واردکردن کد بود (۶ نفر از ۸ نفر). رایج‌ترین تم مثبت سرعت جست‌وجوی محصول بود (۵ نفر از ۸ نفر)."),
                "table": {"columns": ["theme", "participants"], "rows": rows},
                "chart": {"kind": "barHorizontal", "x": "theme", "series": ["participants"]},
                "evidence": ["E1", "E6", "E9"]})
    # AN8 device comparison
    rows = []
    for j, t in enumerate(TASKS):
        m = sum(1 for p in P if DEVICE[p] == "mobile" and SUCCESS[p][j] == 1)
        d = sum(1 for p in P if DEVICE[p] == "desktop" and SUCCESS[p][j] == 1)
        rows.append([t, m / 4, d / 4])
    out.append({"id": "AN8", "catalogueId": "A9", "title": T("Success by device", "موفقیت به تفکیک دستگاه"),
                "finding": T("Payment failed more on mobile, where the Pay button sat below the fold. With 4 people per device this is a direction, not a measured difference.",
                             "پرداخت در موبایل بیشتر شکست خورد، جایی که دکمه‌ی پرداخت زیر لبه‌ی صفحه بود. با ۴ نفر در هر دستگاه این فقط یک جهت است، نه تفاوتی اندازه‌گیری‌شده."),
                "table": {"columns": ["task", "mobile", "desktop"], "rows": rows, "format": {"mobile": "percent", "desktop": "percent"},
                          "labels": {"mobile": T("mobile", "موبایل"), "desktop": T("desktop", "دسکتاپ")}},
                "chart": {"kind": "bar", "x": "task", "series": ["mobile", "desktop"]}, "evidence": ["E2"]})
    # AN9 funnel
    f = stats.funnel([(n, c) for n, _, c in FUNNEL])
    rows = [[T(en, fa), x["count"], round(x["fromTop"], 4), round(x["dropFromPrevious"], 4)] for (en, fa, _), x in zip(FUNNEL, f)]
    out.append({"id": "AN9", "catalogueId": "E1", "values": {"days": 30}, "title": T("Checkout funnel before the redesign", "قیف پرداخت پیش از طراحی دوباره"),
                "finding": T(f"Over 30 days, {pct(f[-1]['fromTop'])}% of people who opened the basket paid. The biggest drop was basket → delivery ({pct(f[1]['dropFromPrevious'])}%).",
                             f"در ۳۰ روز، {fa_num(pct(f[-1]['fromTop']))}٪ از کسانی که سبد را باز کردند پرداخت کردند. بیشترین ریزش در گام سبد ← تحویل بود ({fa_num(pct(f[1]['dropFromPrevious']))}٪)."),
                "table": {"columns": ["step", "users", "from top", "drop"], "rows": rows, "format": {"from top": "percent", "drop": "percent"}},
                "chart": {"kind": "funnel", "x": "step", "series": ["users"]}, "evidence": ["E4"]})
    # AN10 A/B test
    (s1, n1), (s2, n2) = AB["new"], AB["old"]
    ab = stats.two_proportions(s1, n1, s2, n2)
    rows = [[T("old", "قدیم"), s2 / n2, s2, n2], [T("new", "جدید"), s1 / n1, s1, n1]]
    out.append({"id": "AN10", "catalogueId": "E5",
                "values": {"difference": round(ab["difference"], 4), "low": round(ab["low"], 4), "high": round(ab["high"], 4),
                           "p": round(ab["p"], 6), "pThreshold": 0.001, "days": 14}, "title": T("A/B test: old vs new checkout", "تست A/B: پرداخت قدیم و جدید"),
                "finding": T(f"The new checkout converted {pct(ab['rateA'], 1)}% against {pct(ab['rateB'], 1)}% (difference {pct(ab['difference'], 1)} points, "
                             f"95% CI {pct(ab['low'], 1)}–{pct(ab['high'], 1)}; two-proportion z test, p < 0.001).",
                             f"پرداخت جدید {fa_num(pct(ab['rateA'], 1))}٪ تبدیل داشت در برابر {fa_num(pct(ab['rateB'], 1))}٪ (تفاوت {fa_num(pct(ab['difference'], 1))} واحد درصد، "
                             f"بازه‌ی اطمینان ۹۵٪: {fa_num(pct(ab['low'], 1))} تا {fa_num(pct(ab['high'], 1))}؛ آزمون z دو نسبت، p کمتر از ۰٫۰۰۱)."),
                "table": {"columns": ["variant", "conversion", "paid", "visitors"], "rows": rows, "format": {"conversion": "percent"}},
                "chart": {"kind": "bar", "x": "variant", "series": ["conversion"]},
                "method": T("Two-proportion z test; Agresti–Caffo 95% CI for the difference", "آزمون z دو نسبت؛ بازه‌ی اطمینان ۹۵٪ Agresti–Caffo برای تفاوت"),
                "evidence": ["E5"], "_p": ab["p"]})
    # AN11 problem discovery
    matrix = [[1 if p in ps else 0 for *_, ps in ISSUES] for p in P]
    pd = stats.problem_discovery(matrix)
    rows = [[c["users"], round(c["share"], 4)] for c in pd["curve"][:12]]
    out.append({"id": "AN11", "catalogueId": "G8", "title": T("How many problems 8 people can find", "۸ نفر چند درصد مشکل‌ها را پیدا می‌کنند"),
                "finding": T(f"Each issue was seen by {pct(pd['p'])}% of people on average, so 8 people would find about {pct(pd['foundShare'])}% of issues this common. Small samples make this estimate optimistic.",
                             f"هر مشکل به‌طور میانگین برای {fa_num(pct(pd['p']))}٪ از افراد پیش آمد؛ پس ۸ نفر حدود {fa_num(pct(pd['foundShare']))}٪ از مشکل‌هایی با این میزان رواج را پیدا می‌کنند. نمونه‌ی کوچک این برآورد را خوش‌بینانه می‌کند."),
                "table": {"columns": ["users", "share found"], "rows": rows, "format": {"share found": "percent"}},
                "chart": {"kind": "line", "x": "users", "series": ["share found"]}, "evidence": ["E1"]})
    # AN12 participants
    out.append({"id": "AN12", "catalogueId": "G1", "values": {"n": len(P)}, "title": T("Participants", "شرکت‌کننده‌ها"),
                "finding": T("8 people who order groceries online at least twice a month: 4 on mobile, 4 on desktop.",
                             "۸ نفر که دست‌کم ماهی دو بار خرید آنلاین مواد غذایی دارند: ۴ نفر با موبایل و ۴ نفر با دسکتاپ."),
                "table": {"columns": ["device", "participants"], "rows": [[T("mobile", "موبایل"), 4], [T("desktop", "دسکتاپ"), 4]]},
                "chart": {"kind": "doughnut", "x": "device", "series": ["participants"]}, "evidence": ["E2"]})
    # AN13 precision
    w = stats.proportion(4, 8)
    out.append({"id": "AN13", "catalogueId": "G2", "title": T("What 8 people can tell us", "۸ نفر چه چیزی را می‌توانند نشان دهند"),
                "finding": T(f"With 8 people, a 50% success rate has a 95% interval of {pct(w['low'])}–{pct(w['high'])}%. "
                             "That is enough to find the main problems, not to measure small differences.",
                             f"با ۸ نفر، نرخ موفقیت ۵۰٪ بازه‌ی اطمینان ۹۵٪ از {fa_num(pct(w['low']))} تا {fa_num(pct(w['high']))}٪ دارد. "
                             "این برای پیدا کردن مشکل‌های اصلی کافی است، نه برای اندازه‌گیری تفاوت‌های کوچک."),
                "table": {"columns": ["observed", "low", "high", "n"], "rows": [[0.5, round(w["low"], 4), round(w["high"], 4), 8]],
                          "format": {"observed": "percent", "low": "percent", "high": "percent"}},
                "evidence": ["E2"]})
    for a in out:
        a.pop("_p", None)
        t = a.get("table")
        if t:
            t.setdefault("labels", {})
            for c in t["columns"]:
                if c in COLS and c not in t["labels"]:
                    t["labels"][c] = T(*COLS[c])
    return out, s


def content(an, sus):
    para = lambda en, fa, ev=None: {"type": "paragraph", "text": T(en, fa), **({"evidence": ev} if ev else {})}
    place = lambda *ids: [{"type": "analysis", "analysis": i} for i in ids]
    quote = lambda e: next({"type": "quote", "text": T(en, fa), "participant": p, "evidence": [e]} for ee, p, en, fa, _ in QUOTES if ee == e)
    return {
        "schema": "reporch/content@1",
        "meta": {"title": T("Basket checkout usability test", "تست کاربردپذیری پرداخت در Basket"),
                 "eyebrow": T("Demo report · fictional data", "گزارش نمونه · داده‌ی خیالی"),
                 "headline": T("Most people could fill a basket. Few could use a discount code, and mobile users missed the Pay button.",
                               "بیشتر افراد سبد را پر کردند. کمتر کسی توانست کد تخفیف را اعمال کند و کاربران موبایل دکمه‌ی پرداخت را ندیدند."),
                 "slug": "basket-checkout", "authors": [{"name": T("Demo Designer", "طراح نمونه"), "role": T("Product designer", "طراح محصول")}],
                 "methods": ["usability-test", "a-b-test", "analytics"], "studyGoal": "mixed",
                 "dates": {"start": "2026-09-01", "end": "2026-09-12"}, "languages": ["en", "fa"],
                 "brand": {"primary": "#754EC6", "logo": None, "font": None}},
        "participants": [{"id": p, "segment": DEVICE[p]} for p in P],
        "evidence": [
            {"id": "E1", "source": "inputs/clean/session-notes.md", "locator": T("issues list", "فهرست مشکل‌ها")},
            {"id": "E2", "source": "inputs/clean/tasks.csv"}, {"id": "E3", "source": "inputs/clean/sus.csv"},
            {"id": "E4", "source": "inputs/clean/analytics-funnel.csv", "locator": T("30 days before the redesign", "۳۰ روز پیش از طراحی دوباره")},
            {"id": "E5", "source": "inputs/clean/ab-test.csv", "locator": T("14 days, 50/50 split", "۱۴ روز، تقسیم ۵۰/۵۰")},
        ] + [{"id": e, "source": "inputs/clean/session-notes.md", "locator": T(loc, fa_num(loc).replace("session", "جلسه‌ی")), "participant": p}
             for e, p, _, _, loc in QUOTES],
        "analyses": an,
        "sections": [
            {"id": "summary", "role": "summary", "title": T("Summary", "خلاصه"), "blocks": [
                {"type": "stats", "items": [
                    {"label": T("found and added a product alone", "محصول را بدون کمک پیدا کردند"), "value": T("8 of 8", "۸ از ۸"), "tone": "green"},
                    {"label": T("applied a discount code alone", "کد تخفیف را بدون کمک اعمال کردند"), "value": T("1 of 8", "۱ از ۸"), "tone": "red"},
                    {"label": T("SUS score", "امتیاز SUS"), "value": T(f"{sus['mean']:.1f}", fa_num(f"{sus['mean']:.1f}")), "note": T("average is 68", "میانگین رایج ۶۸ است"), "tone": "amber"},
                    {"label": T("conversion, new vs old", "تبدیل، جدید در برابر قدیم"), "value": T("44.2% vs 38.8%", "۴۴٫۲٪ در برابر ۳۸٫۸٪"), "tone": "green"}]},
                {"type": "list", "items": [
                    T("The discount field was hidden: 6 of 8 people couldn't find it, and only 1 applied a code alone.", "فیلد تخفیف پنهان بود: ۶ نفر از ۸ نفر پیدایش نکردند و فقط ۱ نفر بدون کمک کد را اعمال کرد."),
                    T("On mobile the Pay button sat below the fold; 3 people missed it.", "در موبایل دکمه‌ی پرداخت زیر لبه‌ی صفحه بود و ۳ نفر آن را ندیدند."),
                    T("The redesign moved both into view. In an A/B test, conversion rose from 38.8% to 44.2%.", "طراحی دوباره هر دو را در دید قرار داد. در تست A/B نرخ تبدیل از ۳۸٫۸٪ به ۴۴٫۲٪ رسید.")]},
            ]},
            {"id": "context", "role": "context", "title": T("Context", "زمینه"), "blocks": [
                para("Basket is a fictional grocery delivery app used here as a demo. Its checkout lost most people between the basket and payment. We wanted to know where and why.",
                     "Basket یک اپ خیالی تحویل مواد غذایی است که اینجا برای نمونه استفاده شده است. بیشتر کاربران بین سبد و پرداخت از فرایند خارج می‌شدند. می‌خواستیم بدانیم کجا و چرا."),
            ]},
            {"id": "method", "role": "method", "title": T("Method", "روش"), "blocks": [
                para("Moderated think-aloud test with 8 people (4 mobile, 4 desktop), four tasks each, followed by SEQ after each task and SUS at the end. "
                     "We also read 30 days of funnel data and ran a 14-day A/B test of the redesign.",
                     "تست Think Aloud با حضور تسهیلگر و ۸ نفر (۴ موبایل، ۴ دسکتاپ)، هر نفر چهار تسک، با SEQ بعد از هر تسک و SUS در پایان. "
                     "داده‌ی قیف ۳۰ روز را هم بررسی کردیم و طراحی جدید را ۱۴ روز با تست A/B سنجیدیم."),
                {"type": "table", "columns": ["task", "description"],
                 "labels": {"task": T("task", "تسک"), "description": T("description", "شرح")},
                 "rows": [[t, T(*TASK_NAMES[t])] for t in TASKS]},
            ]},
            {"id": "participants", "role": "participants", "title": T("Participants", "شرکت‌کننده‌ها"), "blocks": place("AN12")},
            {"id": "problem", "role": "problem", "title": T("Problem", "مسئله"), "blocks": [
                para("Before the redesign, fewer than a third of people who opened the basket paid. In the test, two things stopped people: the discount field and the Pay button.",
                     "پیش از طراحی دوباره، کمتر از یک‌سوم کسانی که سبد را باز می‌کردند پرداخت می‌کردند. در تست، دو چیز مانع افراد شد: فیلد تخفیف و دکمه‌ی پرداخت.", ["E4"]),
                *place("AN9", "AN1", "AN2"), quote("E6"), quote("E7"), quote("E8"), *place("AN6", "AN7"),
                {"type": "image", "src": "assets/images/checkout-old.svg",
                 "caption": T("The old checkout on mobile (fictional mockup): the discount field is hidden and the Pay button is below the fold",
                              "پرداخت قدیمی در موبایل (طرح خیالی): فیلد تخفیف پنهان است و دکمه‌ی پرداخت زیر لبه‌ی صفحه"),
                 "alt": T("Mockup of the old mobile checkout", "طرح پرداخت قدیمی در موبایل")},
                {"type": "image", "caption": T("Where people left the funnel", "جایی که افراد از قیف خارج شدند"),
                 "placeholder": {"kind": "analytics", "description": T(
                     "Screenshot of the analytics funnel for the 30 days before the redesign (Basket → Delivery → Payment → Paid), with the drop percentages visible.",
                     "اسکرین‌شات قیف ابزار تحلیل برای ۳۰ روزِ پیش از طراحی دوباره (سبد ← تحویل ← پرداخت ← پرداخت‌شده) با درصدهای ریزش.")}},
            ]},
            {"id": "solution", "role": "solution", "title": T("Solution", "راه‌حل"), "blocks": [
                para("The redesign shows the discount field open by default, makes free delivery slots solid and selectable, and pins the Pay button to the bottom of the screen on mobile.",
                     "در طراحی جدید فیلد تخفیف به‌طور پیش‌فرض باز است، زمان‌های تحویلِ آزاد پررنگ و قابل‌انتخاب‌اند و دکمه‌ی پرداخت در موبایل به پایین صفحه چسبیده است."),
                {"type": "flow", "steps": [{"text": T("Basket", "سبد"), "status": "ok"}, {"text": T("Delivery slot", "زمان تحویل"), "status": "ok"},
                                           {"text": T("Discount (open)", "تخفیف (باز)"), "status": "ok"}, {"text": T("Pay (pinned)", "پرداخت (ثابت)"), "status": "ok"}]},
                {"type": "image", "src": "assets/images/checkout-new.svg",
                 "caption": T("The new checkout on mobile (fictional mockup): discount field open, Pay button pinned",
                              "پرداخت جدید در موبایل (طرح خیالی): فیلد تخفیف باز و دکمه‌ی پرداخت ثابت"),
                 "alt": T("Mockup of the redesigned mobile checkout", "طرح پرداخت جدید در موبایل")},
            ]},
            {"id": "result", "role": "result", "title": T("Result", "نتیجه"), "blocks": [
                *place("AN10", "AN3", "AN4", "AN5", "AN8", "AN11", "AN13"), quote("E9"),
            ]},
            {"id": "limitations", "role": "limitations", "title": T("Limitations", "محدودیت‌ها"), "blocks": [
                para("Eight people are enough to find the main problems, not to compare devices precisely. The A/B test ran for 14 days only.",
                     "هشت نفر برای پیدا کردن مشکل‌های اصلی کافی‌اند، نه برای مقایسه‌ی دقیق دستگاه‌ها. تست A/B فقط ۱۴ روز اجرا شد."),
                {"type": "callout", "tone": "info", "text": T("Everything in this report is fictional demo data.", "همه‌ی داده‌های این گزارش خیالی و برای نمونه است.")},
            ]},
        ],
        "blog": {
            "title": T("The discount code nobody could find", "کد تخفیفی که کسی پیدایش نکرد"),
            "dek": T("How eight usability sessions and one A/B test fixed a checkout (a fictional demo).",
                     "چطور هشت جلسه‌ی تست کاربردپذیری و یک تست A/B فرایند پرداخت را درست کرد (نمونه‌ی خیالی)."),
            "sections": [
                {"id": "b1", "blocks": [
                    para("P02 had a discount code ready. She looked at the payment step for almost three minutes, then said:",
                         "P02 کد تخفیف را آماده داشت. نزدیک سه دقیقه به گام پرداخت نگاه کرد و بعد گفت:"), quote("E6"),
                    para("She wasn't alone. Six of our eight participants couldn't find where to enter a code.",
                         "او تنها نبود. شش نفر از هشت شرکت‌کننده‌ی ما جای واردکردن کد را پیدا نکردند.", ["E1"])]},
                {"id": "b2", "title": T("What we did", "چه کردیم"), "blocks": [
                    para("We asked eight people to buy groceries in Basket's checkout, on mobile and desktop, thinking aloud. Then we read a month of funnel data.",
                         "از هشت نفر خواستیم در فرایند پرداخت Basket، با موبایل و دسکتاپ، خرید کنند و فکرشان را بلند بگویند. بعد داده‌ی یک ماهِ قیف را خواندیم.")]},
                {"id": "b3", "title": T("What we found", "چه یافتیم"), "blocks": [
                    para("Filling the basket was easy: all eight did it alone. Using a discount code was the hardest step: only one person managed it without help. On mobile, three people missed the Pay button because it sat below the fold.",
                         "پر کردن سبد آسان بود: هر هشت نفر بدون کمک انجامش دادند. استفاده از کد تخفیف سخت‌ترین گام بود: فقط یک نفر بدون کمک موفق شد. در موبایل سه نفر دکمه‌ی پرداخت را ندیدند، چون زیر لبه‌ی صفحه بود.", ["E2"]),
                    *place("AN1")]},
                {"id": "b4", "title": T("What changed", "چه تغییر کرد"), "blocks": [
                    para("We opened the discount field by default and pinned the Pay button on mobile. In a 14-day A/B test, conversion rose from 38.8% to 44.2%.",
                         "فیلد تخفیف را به‌طور پیش‌فرض باز کردیم و دکمه‌ی پرداخت را در موبایل ثابت کردیم. در تست A/B چهارده‌روزه، نرخ تبدیل از ۳۸٫۸٪ به ۴۴٫۲٪ رسید.", ["E5"]),
                    *place("AN10")]},
                {"id": "b5", "title": T("What's next", "قدم بعدی"), "blocks": [
                    para("Next we'll test the delivery slots, which three people thought were unavailable.",
                         "قدم بعدی تست زمان‌های تحویل است که سه نفر فکر می‌کردند در دسترس نیستند.", ["E1"])]},
            ]},
        "glossary": [
            {"term": "SEQ", "text": T("Single Ease Question: how easy a task was, 1–7.", "Single Ease Question: سهولت یک تسک، از ۱ تا ۷.")},
            {"term": "SUS", "text": T("System Usability Scale: ten questions, scored 0–100.", "System Usability Scale: ده سؤال با امتیاز ۰ تا ۱۰۰.")},
            {"term": "CI", "text": T("Confidence interval: the range the true value is likely in.", "بازه‌ی اطمینان: محدوده‌ای که مقدار واقعی به احتمال زیاد در آن است.")},
        ],
        "openQuestions": [{"text": T("Do the delivery-slot changes reduce the basket → delivery drop?", "آیا تغییرات زمان تحویل ریزش سبد ← تحویل را کم می‌کند؟")}],
    }


def main():
    if os.path.isdir(PROJECT):
        shutil.rmtree(PROJECT)
    for d in ("inputs/clean", "assets", "out", "versions"):
        os.makedirs(os.path.join(PROJECT, d), exist_ok=True)
    write_inputs()
    images = os.path.join(PROJECT, "assets", "images")
    os.makedirs(images, exist_ok=True)
    for name in ("checkout-old.svg", "checkout-new.svg"):
        shutil.copy2(os.path.join(ROOT, "tools", "demo-assets", name), images)
    an, sus = analyses()
    doc = content(an, sus)
    with open(os.path.join(PROJECT, "content.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    state = {"schema": "reporch/state@1", "slug": "basket-checkout", "created": "2026-09-12T10:00:00+00:00",
             "updated": "2026-09-12T10:00:00+00:00", "phase": "qa", "phasesDone": ["collect", "interview", "plan", "analysis",
             "outline", "write", "translate", "build"], "workflow": ["collect", "interview", "plan", "analysis", "outline", "write",
             "translate", "build", "qa", "done"], "languages": ["en", "fa"], "brand": None, "questionsAsked": 14,
             "version": 0, "dependencies": [], "dataFields": ["participants", "task_success", "success_level", "assisted",
             "task_time", "post_task_rating", "sus_items", "issues", "issue_severity", "issue_participant", "transcripts",
             "segment", "step_counts", "variant_results"]}
    with open(os.path.join(PROJECT, "state.json"), "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from reporch_lib import project
    todo = project.plan(PROJECT, force=True)          # the demo's plan, worked through up to delivery
    with open(todo, encoding="utf-8") as f:
        plan = f.read()
    head, tail = plan.split(project.DELIVER, 1)
    with open(todo, "w", encoding="utf-8") as f:
        f.write(head.replace("- [ ]", "- [x]") + project.DELIVER + tail)
    for name, text in (("MEMORY.md", "# Memory: basket-checkout\n\n## Decisions\n\n- 2026-09-12: Languages en and fa; "
                        "default theme (fictional study).\n"),
                       ("HISTORY.md", "# History: basket-checkout\n\n- 2026-09-12 10:00 · reporch: Fictional demo generated "
                        "by tools/make_demo.py.\n")):
        with open(os.path.join(PROJECT, name), "w", encoding="utf-8") as f:
            f.write(text)
    print(PROJECT)


if __name__ == "__main__":
    main()

"""Statistics for research reports, standard library only (references/analyses.md §0.1).

Every function returns plain dicts so results can go straight into content.json tables. Confidence
levels default to 95%. Distributions (t, F, chi-square) are computed from the regularized incomplete
beta and gamma functions, so no SciPy is needed.
"""
import math
import statistics

# ---------------------------------------------------------------- special functions

def _betacf(a, b, x):
    tiny, qab, qap, qam = 1e-300, a + b, a + 1, a - 1
    c, d = 1.0, 1 - qab * x / qap
    d = 1 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1 + aa * d; d = 1 / (d if abs(d) > tiny else tiny)
        c = 1 + aa / c if abs(1 + aa / c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1 + aa * d; d = 1 / (d if abs(d) > tiny else tiny)
        c = 1 + aa / c if abs(1 + aa / c) > tiny else tiny
        delta = d * c
        h *= delta
        if abs(delta - 1) < 1e-12:
            break
    return h


def betainc(a, b, x):
    """Regularized incomplete beta I_x(a, b)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(lbt) * _betacf(a, b, x) / a
    return 1 - math.exp(lbt) * _betacf(b, a, 1 - x) / b


def gammainc_upper(s, x):
    """Regularized upper incomplete gamma Q(s, x)."""
    if x <= 0:
        return 1.0
    if x < s + 1:
        term = total = 1 / s
        n = s
        for _ in range(500):
            n += 1; term *= x / n; total += term
            if abs(term) < abs(total) * 1e-14:
                break
        return 1 - total * math.exp(-x + s * math.log(x) - math.lgamma(s))
    tiny = 1e-300
    b, c, d = x + 1 - s, 1 / tiny, 1 / (x + 1 - s)
    h = d
    for i in range(1, 500):
        an = -i * (i - s); b += 2
        d = an * d + b; d = 1 / (d if abs(d) > tiny else tiny)
        c = b + an / c; c = c if abs(c) > tiny else tiny
        delta = d * c; h *= delta
        if abs(delta - 1) < 1e-14:
            break
    return math.exp(-x + s * math.log(x) - math.lgamma(s)) * h


def t_sf2(t, df):
    """Two-tailed p for Student's t."""
    return betainc(df / 2, 0.5, df / (df + t * t))


def t_ppf(p, df):
    """Quantile of Student's t (p in (0, 1)), by bisection on the CDF."""
    target = 2 * (1 - p) if p > 0.5 else 2 * p
    lo, hi = 0.0, 1e4
    for _ in range(200):
        mid = (lo + hi) / 2
        if t_sf2(mid, df) > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2 * (1 if p > 0.5 else -1)


def z_ppf(p):
    """Standard normal quantile (Acklam's approximation, refined once with Newton)."""
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02, 1.383577518672690e+02,
         -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02, 6.680131188771972e+01,
         -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00, -2.549732539343734e+00,
         4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00, 3.754408661907416e+00]
    q = min(p, 1 - p)
    if q < 0.02425:
        r = math.sqrt(-2 * math.log(q))
        x = (((((c[0] * r + c[1]) * r + c[2]) * r + c[3]) * r + c[4]) * r + c[5]) / \
            ((((d[0] * r + d[1]) * r + d[2]) * r + d[3]) * r + 1)
        x = x if p < 0.5 else -x
    else:
        r = p - 0.5
        s = r * r
        x = (((((a[0] * s + a[1]) * s + a[2]) * s + a[3]) * s + a[4]) * s + a[5]) * r / \
            (((((b[0] * s + b[1]) * s + b[2]) * s + b[3]) * s + b[4]) * s + 1)
    e = 0.5 * math.erfc(-x / math.sqrt(2)) - p
    return x - e * math.sqrt(2 * math.pi) * math.exp(x * x / 2)


def _z(level):
    return z_ppf(1 - (1 - level) / 2)

# ---------------------------------------------------------------- proportions

def proportion(successes, n, level=0.95):
    """Observed rate with the adjusted Wald interval (default) and Wilson for reference."""
    if n <= 0 or not 0 <= successes <= n:
        raise ValueError("need 0 <= successes <= n and n > 0")
    z = _z(level)
    p = successes / n
    n_adj = n + z * z
    p_adj = (successes + z * z / 2) / n_adj
    half = z * math.sqrt(p_adj * (1 - p_adj) / n_adj)
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    w_half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return {"rate": p, "successes": successes, "n": n, "level": level, "method": "adjusted Wald",
            "low": max(0.0, p_adj - half), "high": min(1.0, p_adj + half),
            "wilsonLow": max(0.0, centre - w_half), "wilsonHigh": min(1.0, centre + w_half)}

# ---------------------------------------------------------------- means and times

def mean_ci(values, level=0.95):
    v = [float(x) for x in values]
    n = len(v)
    if n < 2:
        raise ValueError("need at least 2 values")
    m, sd = statistics.fmean(v), statistics.stdev(v)
    half = t_ppf(1 - (1 - level) / 2, n - 1) * sd / math.sqrt(n)
    return {"mean": m, "sd": sd, "n": n, "level": level, "low": m - half, "high": m + half,
            "median": statistics.median(v)}


def time_summary(times, level=0.95):
    """Task times are skewed: geometric mean with a CI from log times, plus median and mean."""
    t = [float(x) for x in times]
    if any(x <= 0 for x in t):
        raise ValueError("times must be positive")
    logs = mean_ci([math.log(x) for x in t], level)
    base = mean_ci(t, level)
    return {"geometricMean": math.exp(logs["mean"]), "low": math.exp(logs["low"]), "high": math.exp(logs["high"]),
            "median": statistics.median(t), "mean": base["mean"], "sd": base["sd"], "n": len(t), "level": level,
            "method": "CI on log times"}


def outliers(values, sd_limit=3.0, floor=None):
    """Indices to exclude: above mean + sd_limit*SD, or below `floor` (e.g. an expert's minimum time)."""
    v = [float(x) for x in values]
    m, sd = statistics.fmean(v), statistics.stdev(v) if len(v) > 1 else 0.0
    return [i for i, x in enumerate(v) if (sd and x > m + sd_limit * sd) or (floor is not None and x < floor)]

# ---------------------------------------------------------------- scores

def sus(responses):
    """SUS from ten 1–5 answers per participant (odd items positive). Returns per-person scores and CI."""
    scores = []
    for r in responses:
        if len(r) != 10 or not all(1 <= int(x) <= 5 for x in r):
            raise ValueError("each SUS response needs ten answers from 1 to 5")
        s = sum((int(x) - 1) if i % 2 == 0 else (5 - int(x)) for i, x in enumerate(r))
        scores.append(s * 2.5)
    out = {"scores": scores, "n": len(scores), "mean": statistics.fmean(scores)}
    if len(scores) > 1:
        out.update({k: v for k, v in mean_ci(scores).items() if k in ("low", "high", "sd", "level")})
    out["benchmark"] = {"average": 68, "source": "Sauro & Lewis; Tullis & Albert"}
    return out


def nps(scores, level=0.95):
    s = [int(x) for x in scores]
    if not s or any(not 0 <= x <= 10 for x in s):
        raise ValueError("NPS scores are 0–10")
    n = len(s)
    pro, det = sum(x >= 9 for x in s), sum(x <= 6 for x in s)
    return {"nps": 100 * (pro - det) / n, "n": n, "promoters": proportion(pro, n, level),
            "passives": proportion(n - pro - det, n, level), "detractors": proportion(det, n, level),
            "note": "NPS measures intent, not behaviour, and is not a usability measure."}


def top_box(ratings, scale_max, boxes=2, level=0.95):
    r = [int(x) for x in ratings]
    hits = sum(x > scale_max - boxes for x in r)
    return proportion(hits, len(r), level) | {"boxes": boxes, "scaleMax": scale_max}


def lostness(visited, unique, optimal):
    """Smith's lostness: 0 is perfect, above ~0.4–0.5 people look lost (Tullis & Albert)."""
    if min(visited, unique, optimal) <= 0 or unique > visited:
        raise ValueError("need visited >= unique >= 1 and optimal >= 1")
    return math.sqrt((unique / visited - 1) ** 2 + (optimal / unique - 1) ** 2)


def efficiency(successes, times):
    """Tasks completed per minute, from success flags (0/1) and times in seconds."""
    total = sum(float(t) for t in times)
    return sum(int(s) for s in successes) / (total / 60) if total else 0.0


def problem_discovery(matrix):
    """matrix[participant][problem] in {0,1}. Estimates p and the share of problems found by n people."""
    n = len(matrix)
    k = len(matrix[0]) if n else 0
    if not n or not k:
        raise ValueError("need a participants × problems matrix")
    p = sum(map(sum, matrix)) / (n * k)
    return {"p": p, "n": n, "problems": k, "foundShare": 1 - (1 - p) ** n,
            "curve": [{"users": i, "share": 1 - (1 - p) ** i} for i in range(1, max(n, 15) + 1)],
            "note": "Small samples overestimate p, so the curve is optimistic."}

# ---------------------------------------------------------------- tests

def t_test(a, b, paired=False):
    a = [float(x) for x in a]; b = [float(x) for x in b]
    if paired:
        if len(a) != len(b):
            raise ValueError("paired samples need equal length")
        d = [x - y for x, y in zip(a, b)]
        ci = mean_ci(d)
        t = ci["mean"] / (ci["sd"] / math.sqrt(len(d))) if ci["sd"] else float("inf")
        df = len(d) - 1
        return {"test": "paired t", "t": t, "df": df, "p": t_sf2(t, df) if math.isfinite(t) else 0.0,
                "meanDifference": ci["mean"], "low": ci["low"], "high": ci["high"]}
    va, vb = statistics.variance(a) / len(a), statistics.variance(b) / len(b)
    diff = statistics.fmean(a) - statistics.fmean(b)
    se = math.sqrt(va + vb)
    df = (va + vb) ** 2 / (va ** 2 / (len(a) - 1) + vb ** 2 / (len(b) - 1))
    t = diff / se
    half = t_ppf(0.975, df) * se
    return {"test": "Welch t", "t": t, "df": df, "p": t_sf2(t, df), "meanDifference": diff,
            "low": diff - half, "high": diff + half}


def anova(*groups):
    gs = [[float(x) for x in g] for g in groups]
    allv = [x for g in gs for x in g]
    grand = statistics.fmean(allv)
    ssb = sum(len(g) * (statistics.fmean(g) - grand) ** 2 for g in gs)
    ssw = sum((x - statistics.fmean(g)) ** 2 for g in gs for x in g)
    dfb, dfw = len(gs) - 1, len(allv) - len(gs)
    f = (ssb / dfb) / (ssw / dfw)
    return {"test": "one-way ANOVA", "F": f, "dfBetween": dfb, "dfWithin": dfw,
            "p": betainc(dfw / 2, dfb / 2, dfw / (dfw + dfb * f))}


def chi_square(table):
    """Chi-square test of independence on raw counts. Warns when expected counts are small."""
    rows, cols = len(table), len(table[0])
    total = sum(map(sum, table))
    rt = [sum(r) for r in table]
    ct = [sum(table[i][j] for i in range(rows)) for j in range(cols)]
    chi, small = 0.0, 0
    for i in range(rows):
        for j in range(cols):
            e = rt[i] * ct[j] / total
            small += e < 5
            chi += (table[i][j] - e) ** 2 / e if e else 0
    df = (rows - 1) * (cols - 1)
    out = {"test": "chi-square", "chi2": chi, "df": df, "p": gammainc_upper(df / 2, chi / 2)}
    if small:
        out["warning"] = f"{small} expected count(s) below 5; use Fisher's exact test for 2×2 tables"
    return out


def fisher_exact(table):
    """Two-sided Fisher's exact test for a 2×2 table [[a, b], [c, d]]."""
    (a, b), (c, d) = table
    r1, c1, n = a + b, a + c, a + b + c + d

    def prob(x):
        return math.comb(c1, x) * math.comb(n - c1, r1 - x) / math.comb(n, r1)
    p0 = prob(a)
    lo, hi = max(0, r1 + c1 - n), min(r1, c1)
    p = sum(prob(x) for x in range(lo, hi + 1) if prob(x) <= p0 * (1 + 1e-9))
    return {"test": "Fisher's exact", "p": min(1.0, p)}


def two_proportions(s1, n1, s2, n2):
    """Difference between two rates (A/B), with a z test and an adjusted CI for the difference."""
    p1, p2 = s1 / n1, s2 / n2
    pooled = (s1 + s2) / (n1 + n2)
    se0 = math.sqrt(pooled * (1 - pooled) * (1 / n1 + 1 / n2))
    z = (p1 - p2) / se0 if se0 else 0.0
    q1, q2 = (s1 + 1) / (n1 + 2), (s2 + 1) / (n2 + 2)          # Agresti–Caffo
    se = math.sqrt(q1 * (1 - q1) / (n1 + 2) + q2 * (1 - q2) / (n2 + 2))
    diff = q1 - q2
    return {"test": "two-proportion z", "rateA": p1, "rateB": p2, "difference": p1 - p2, "z": z,
            "p": math.erfc(abs(z) / math.sqrt(2)), "low": diff - 1.96 * se, "high": diff + 1.96 * se}


def correlation(x, y):
    n = len(x)
    r = statistics.correlation([float(v) for v in x], [float(v) for v in y])
    t = r * math.sqrt((n - 2) / (1 - r * r)) if abs(r) < 1 else float("inf")
    return {"test": "Pearson", "r": r, "n": n, "p": t_sf2(t, n - 2) if math.isfinite(t) else 0.0,
            "note": "Correlation does not show cause."}

# ---------------------------------------------------------------- combined and product metrics

def z_scores(values, higher_is_better=True):
    v = [float(x) for x in values]
    m, sd = statistics.fmean(v), statistics.stdev(v)
    return [((x - m) / sd) * (1 if higher_is_better else -1) for x in v]


def funnel(steps):
    """steps: [(name, count)]. Conversion from the top and drop-off from the previous step."""
    out, first, prev = [], steps[0][1], None
    for name, count in steps:
        out.append({"step": name, "count": count, "fromTop": count / first if first else 0.0,
                    "dropFromPrevious": (1 - count / prev) if prev else 0.0})
        prev = count
    return out


def retention(cohorts):
    """cohorts: {cohort: [active users in period 0, 1, 2, …]}. Returns shares of period 0."""
    return {k: [c / v[0] if v[0] else 0.0 for c in v] for k, v in cohorts.items()}


def stickiness(dau, mau):
    return dau / mau if mau else 0.0


def customer_lifetime_value(arpa, churn_rate):
    """CLV = lifetime × ARPA, with lifetime = 1 / churn (per period)."""
    if churn_rate <= 0:
        raise ValueError("churn rate must be above 0")
    return {"lifetime": 1 / churn_rate, "clv": arpa / churn_rate}


def net_revenue_retention(beginning, expansion, churned, downgraded):
    return {"nrr": (beginning + expansion - churned - downgraded) / beginning,
            "netRevenueChurn": (churned + downgraded - expansion) / beginning}

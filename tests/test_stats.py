import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from reporch_lib import stats  # noqa: E402


class DistributionTest(unittest.TestCase):
    """Reference values from standard tables."""

    def test_quantiles(self):
        self.assertAlmostEqual(stats.z_ppf(0.975), 1.959964, places=5)
        self.assertAlmostEqual(stats.z_ppf(0.05), -1.644854, places=5)
        self.assertAlmostEqual(stats.t_ppf(0.975, 9), 2.262157, places=4)
        self.assertAlmostEqual(stats.t_ppf(0.975, 1), 12.7062, places=3)
        self.assertAlmostEqual(stats.t_ppf(0.95, 30), 1.697261, places=4)

    def test_tail_probabilities(self):
        self.assertAlmostEqual(stats.t_sf2(2.262157, 9), 0.05, places=5)
        self.assertAlmostEqual(stats.gammainc_upper(0.5, 3.841459 / 2), 0.05, places=5)   # chi2 df1
        self.assertAlmostEqual(stats.gammainc_upper(2, 9.487729 / 2), 0.05, places=5)     # chi2 df4


class ProportionTest(unittest.TestCase):
    def test_adjusted_wald_and_wilson(self):
        r = stats.proportion(3, 10)
        self.assertAlmostEqual(r["low"], 0.1033, places=3)
        self.assertAlmostEqual(r["high"], 0.6077, places=3)
        self.assertAlmostEqual(r["wilsonLow"], 0.1078, places=3)
        self.assertAlmostEqual(r["wilsonHigh"], 0.6032, places=3)
        self.assertEqual(r["method"], "adjusted Wald")

    def test_extremes_stay_in_range(self):
        for s in (0, 5):
            r = stats.proportion(s, 5)
            self.assertGreaterEqual(r["low"], 0); self.assertLessEqual(r["high"], 1)
        with self.assertRaises(ValueError):
            stats.proportion(6, 5)


class MeansTest(unittest.TestCase):
    def test_mean_ci(self):
        r = stats.mean_ci([2, 4, 4, 4, 5, 5, 7, 9])
        self.assertAlmostEqual(r["mean"], 5.0)
        self.assertAlmostEqual(r["sd"], 2.13809, places=4)
        self.assertAlmostEqual(r["high"] - r["mean"], 2.364624 * 2.13809 / 8 ** 0.5, places=3)

    def test_time_summary_uses_logs(self):
        r = stats.time_summary([10, 20, 40])
        self.assertAlmostEqual(r["geometricMean"], 20.0, places=6)
        self.assertEqual(r["median"], 20)
        self.assertLess(r["low"], 20); self.assertGreater(r["high"], 20)
        with self.assertRaises(ValueError):
            stats.time_summary([0, 5])

    def test_outliers(self):
        self.assertEqual(stats.outliers([10] * 20 + [400]), [20])
        self.assertEqual(stats.outliers([10, 12, 3], floor=5), [2])


class ScoresTest(unittest.TestCase):
    def test_sus(self):
        r = stats.sus([[3] * 10, [5, 1] * 5])
        self.assertEqual(r["scores"], [50.0, 100.0])
        self.assertEqual(r["mean"], 75.0)
        with self.assertRaises(ValueError):
            stats.sus([[3] * 9])

    def test_nps_and_top_box(self):
        r = stats.nps([10, 9, 8, 7, 6, 0, 10, 9, 5, 10])
        self.assertAlmostEqual(r["nps"], 20.0)
        self.assertEqual(r["promoters"]["successes"], 5)
        self.assertEqual(stats.top_box([5, 4, 3, 2, 5], 5)["successes"], 3)

    def test_lostness_and_efficiency(self):
        self.assertEqual(stats.lostness(4, 4, 4), 0.0)
        self.assertAlmostEqual(stats.lostness(10, 5, 2), (0.25 + 0.36) ** 0.5)
        self.assertAlmostEqual(stats.efficiency([1, 1, 0], [60, 60, 60]), 2 / 3)

    def test_problem_discovery(self):
        r = stats.problem_discovery([[1, 0, 1, 0]] * 5)
        self.assertAlmostEqual(r["p"], 0.5)
        self.assertAlmostEqual(r["foundShare"], 1 - 0.5 ** 5)


class TestsTest(unittest.TestCase):
    def test_anova_reference(self):
        r = stats.anova([1, 2, 3], [2, 3, 4], [5, 6, 7])
        self.assertAlmostEqual(r["F"], 13.0)
        self.assertAlmostEqual(r["p"], (1 + 13 * 2 / 6) ** -3, places=6)   # exact for df1 = 2

    def test_fisher_reference(self):
        self.assertAlmostEqual(stats.fisher_exact([[1, 9], [11, 3]])["p"], 0.002759, places=5)

    def test_chi_square_warns_on_small_counts(self):
        r = stats.chi_square([[10, 20], [20, 10]])
        self.assertAlmostEqual(r["chi2"], 6.6667, places=3)
        self.assertAlmostEqual(r["p"], 0.009823, places=5)
        self.assertNotIn("warning", r)
        self.assertIn("warning", stats.chi_square([[1, 2], [3, 1]]))

    def test_t_tests(self):
        paired = stats.t_test([5, 6, 7, 8], [4, 5, 5, 6], paired=True)
        self.assertAlmostEqual(paired["meanDifference"], 1.5)
        self.assertAlmostEqual(paired["t"], 5.196152, places=4)
        self.assertAlmostEqual(paired["p"], 0.01385, places=4)
        welch = stats.t_test([1, 2, 3, 4, 5], [3, 4, 5, 6, 7])
        self.assertAlmostEqual(welch["t"], -2.0)
        self.assertAlmostEqual(welch["df"], 8.0)
        self.assertAlmostEqual(welch["p"], 0.08052, places=4)

    def test_two_proportions_and_correlation(self):
        r = stats.two_proportions(50, 100, 40, 100)
        self.assertAlmostEqual(r["z"], 1.4213, places=3)
        self.assertAlmostEqual(r["p"], 0.1552, places=3)
        c = stats.correlation([1, 2, 3, 4, 5], [2, 4, 5, 4, 5])
        self.assertAlmostEqual(c["r"], 0.774597, places=5)
        self.assertAlmostEqual(c["p"], 0.1240, places=3)


class ProductTest(unittest.TestCase):
    def test_funnel_retention_and_revenue(self):
        f = stats.funnel([("visit", 1000), ("signup", 200), ("pay", 50)])
        self.assertEqual([round(x["fromTop"], 3) for x in f], [1.0, 0.2, 0.05])
        self.assertAlmostEqual(f[2]["dropFromPrevious"], 0.75)
        self.assertEqual(stats.retention({"Sep": [100, 40, 25]})["Sep"], [1.0, 0.4, 0.25])
        self.assertEqual(stats.customer_lifetime_value(20, 0.05), {"lifetime": 20.0, "clv": 400.0})
        r = stats.net_revenue_retention(1000, 100, 50, 30)
        self.assertAlmostEqual(r["nrr"], 1.02); self.assertAlmostEqual(r["netRevenueChurn"], -0.02)
        self.assertEqual(stats.stickiness(200, 1000), 0.2)


if __name__ == "__main__":
    unittest.main()

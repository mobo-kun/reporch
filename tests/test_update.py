import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from reporch_lib import update  # noqa: E402


class UpdateTest(unittest.TestCase):
    def setUp(self):
        self.cfg = os.path.join(tempfile.mkdtemp(), "settings.json")

    def test_off_until_the_user_agrees(self):
        calls = []
        r = update.check(self.cfg, fetch=lambda: calls.append(1) or "v9.9.9")
        self.assertEqual(r["status"], "off")
        self.assertEqual(calls, [])                                   # no request without consent

    def test_update_found_and_daily_limit(self):
        update.save_settings({"updateCheck": True}, self.cfg)
        r = update.check(self.cfg, fetch=lambda: "v9.0.0", now=1_000_000)
        self.assertEqual(r["status"], "update")
        self.assertIn("git -C", r["message"])
        again = update.check(self.cfg, fetch=lambda: self.fail("asked twice in a day"), now=1_000_100)
        self.assertEqual(again["status"], "asked-recently")

    def test_current_and_errors(self):
        update.save_settings({"updateCheck": True}, self.cfg)
        self.assertEqual(update.check(self.cfg, fetch=lambda: "v" + update.current(), now=1)["status"], "current")

        def boom():
            raise OSError("offline")
        update.save_settings({"lastCheck": 1}, self.cfg)
        self.assertEqual(update.check(self.cfg, fetch=boom, now=200_000)["status"], "error")

    def test_version_order(self):
        self.assertTrue(update.newer("v1.10.0", "1.9.3"))
        self.assertFalse(update.newer("v1.0.0", "1.0.0"))
        self.assertTrue(update.newer("2.0.0-rc1", "1.9.9"))


if __name__ == "__main__":
    unittest.main()

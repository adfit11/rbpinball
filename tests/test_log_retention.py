"""MPF log retention: today's sessions (at least the last two) in development, only this session in production."""

import os
import tempfile
import unittest

from custom_code.log_retention import prune, stale_logs

TODAY = "2026-11-22"
CURRENT = "2026-11-22-17-20-00-mpf-MacBookAir.log"
NAMES = [
    CURRENT,
    "2026-11-22-09-00-00-mpf-MacBookAir.log",
    "2026-11-21-22-00-00-mpf-MacBookAir.log",
    "2026-11-20-22-00-00-mpf-MacBookAir.log",
    "2025-01-19-17-07-38-mpf-Adrians-MBP.log",
    "notes.txt",
]


class TestLogRetention(unittest.TestCase):
    def test_development_keeps_todays_sessions(self):
        self.assertEqual(stale_logs(NAMES, CURRENT, False, TODAY), NAMES[2:5])

    def test_development_keeps_the_last_two_sessions_on_a_new_day(self):
        current = "2026-11-23-08-00-00-mpf-MacBookAir.log"
        names = [current, *NAMES]
        self.assertEqual(stale_logs(names, current, False, "2026-11-23"), names[2:6])

    def test_production_keeps_only_this_session(self):
        self.assertEqual(stale_logs(NAMES, CURRENT, True, TODAY), NAMES[1:5])

    def test_prune_deletes_only_stale_mpf_logs(self):
        with tempfile.TemporaryDirectory() as directory:
            for name in NAMES:
                open(os.path.join(directory, name), "w").close()
            self.assertEqual(prune(directory, CURRENT, False, TODAY), 3)
            self.assertEqual(sorted(os.listdir(directory)), sorted([*NAMES[:2], "notes.txt"]))

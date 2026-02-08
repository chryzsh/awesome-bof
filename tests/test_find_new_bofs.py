import unittest

from scripts.find_new_bofs import _repo_in_date_window


class FindNewBofsTests(unittest.TestCase):
    def test_repo_in_date_window_by_pushed(self):
        repo = {
            "pushed_at": "2026-02-02T17:18:28Z",
            "created_at": "2026-01-01T00:00:00Z",
        }
        self.assertTrue(_repo_in_date_window(repo, "2026-01-09"))

    def test_repo_in_date_window_by_created(self):
        repo = {
            "pushed_at": "2026-01-01T00:00:00Z",
            "created_at": "2026-01-21T17:28:00Z",
        }
        self.assertTrue(_repo_in_date_window(repo, "2026-01-09"))

    def test_repo_outside_date_window(self):
        repo = {
            "pushed_at": "2025-12-31T23:59:59Z",
            "created_at": "2025-12-31T00:00:00Z",
        }
        self.assertFalse(_repo_in_date_window(repo, "2026-01-09"))


if __name__ == "__main__":
    unittest.main()

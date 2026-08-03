import io
import unittest
from contextlib import redirect_stderr
from unittest.mock import Mock, patch

import requests

from scripts.find_new_bofs import _paginate_code_search, _paginate_search, _repo_in_date_window


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

    def test_repository_search_returns_partial_results_when_rate_limited(self):
        for status in (403, 429):
            with self.subTest(status=status):
                response = Mock(status_code=status, headers={})
                with patch("scripts.find_new_bofs.requests.get", return_value=response):
                    self.assertEqual(_paginate_search("bof", {}), [])

    def test_repository_search_returns_empty_results_after_transient_errors(self):
        with patch(
            "scripts.find_new_bofs.requests.get",
            side_effect=requests.exceptions.Timeout("timed out"),
        ), patch("scripts.find_new_bofs.time.sleep") as sleep:
            self.assertEqual(_paginate_search("bof", {}), [])

        self.assertEqual(sleep.call_count, 2)

    def test_code_search_returns_partial_results_when_rate_limited(self):
        for status in (403, 429):
            with self.subTest(status=status):
                response = Mock(status_code=status, headers={})
                with patch("scripts.find_new_bofs._throttle_code_search"), patch(
                    "scripts.find_new_bofs.requests.get", return_value=response
                ):
                    items, partial = _paginate_code_search("extension:cna", {})

                self.assertEqual(items, [])
                self.assertTrue(partial)

    def test_code_search_returns_partial_results_after_transient_errors(self):
        with patch("scripts.find_new_bofs._throttle_code_search"), patch(
            "scripts.find_new_bofs.requests.get",
            side_effect=requests.exceptions.ConnectionError("offline"),
        ), patch("scripts.find_new_bofs.time.sleep"):
            items, partial = _paginate_code_search("extension:cna", {})

        self.assertEqual(items, [])
        self.assertTrue(partial)

    def test_code_search_rate_limit_is_logged_as_partial(self):
        response = Mock(status_code=429, headers={})
        stderr = io.StringIO()
        with patch("scripts.find_new_bofs._throttle_code_search"), patch(
            "scripts.find_new_bofs.requests.get", return_value=response
        ), redirect_stderr(stderr):
            _paginate_code_search("extension:cna", {})

        self.assertIn("result is partial", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()

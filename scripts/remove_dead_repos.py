#!/usr/bin/env python3
"""
Check all GitHub repos in BOF-CATALOG.md for 404s and remove dead entries.

Usage:
    python3 scripts/remove_dead_repos.py              # dry-run (default)
    python3 scripts/remove_dead_repos.py --apply       # actually remove dead entries
"""

import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

CATALOG_PATH = Path(__file__).parent.parent / "BOF-CATALOG.md"
REPO_URL_RE = re.compile(
    r"\|\s*\[[^\]]+\]\((https?://github\.com/([^/\s\)]+)/([^/\s\)]+))\)"
)


# Terminal statuses that mean the repo really is gone and should be removed.
# Everything else (including transient 403 rate-limits and 5xx from GitHub)
# is treated as alive so a noisy scheduled run can't wipe live entries.
_DEAD_STATUSES = {404, 410, 451}


def check_repo_alive(owner, name, headers):
    """Return True if the repo exists or the probe is inconclusive.

    Only returns False for terminal "repo gone" statuses (404/410/451).
    Transient errors (403 rate-limit, 5xx, network faults) return True so
    we never delete a live catalog entry on a flaky response.
    """
    url = f"https://api.github.com/repos/{owner}/{name}"
    try:
        resp = requests.head(url, headers=headers, timeout=15, allow_redirects=True)
    except requests.RequestException:
        return True  # network error — assume alive, don't remove
    if resp.status_code in _DEAD_STATUSES:
        return False
    if resp.status_code != 200:
        # Unexpected status (403 rate-limit, 5xx, 401, etc.) — be conservative.
        print(
            f"  warning: {owner}/{name} returned HTTP {resp.status_code}; "
            "treating as alive",
            file=sys.stderr,
        )
    return True


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Remove dead repos from BOF catalog")
    parser.add_argument("--apply", action="store_true", help="Actually remove dead entries (default is dry-run)")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN required.", file=sys.stderr)
        sys.exit(1)

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
    }

    # Parse catalog
    lines = CATALOG_PATH.read_text(encoding="utf-8").splitlines(keepends=True)
    repos_by_line = {}
    for i, line in enumerate(lines):
        m = REPO_URL_RE.search(line)
        if m:
            url, owner, name = m.group(1), m.group(2), m.group(3)
            name = name.split("#")[0].split("?")[0].rstrip("/")
            repos_by_line[i] = (owner, name, url)

    print(f"Checking {len(repos_by_line)} GitHub repos...", file=sys.stderr)

    # Check all repos in parallel
    dead_lines = []
    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = {
            executor.submit(check_repo_alive, owner, name, headers): (line_idx, owner, name, url)
            for line_idx, (owner, name, url) in repos_by_line.items()
        }
        for future in as_completed(futures):
            line_idx, owner, name, url = futures[future]
            alive = future.result()
            if not alive:
                dead_lines.append((line_idx, owner, name, url))

    if not dead_lines:
        print("No dead repos found.")
        return

    dead_lines.sort(key=lambda x: x[0])
    print(f"\nDead repos ({len(dead_lines)}):")
    for _, owner, name, url in dead_lines:
        print(f"  - {owner}/{name} ({url})")

    if not args.apply:
        print(f"\nDry run — pass --apply to remove these {len(dead_lines)} entries.")
        return

    # Remove dead lines
    dead_indices = {dl[0] for dl in dead_lines}
    new_lines = [line for i, line in enumerate(lines) if i not in dead_indices]
    CATALOG_PATH.write_text("".join(new_lines), encoding="utf-8")
    print(f"\nRemoved {len(dead_lines)} dead entries from {CATALOG_PATH.name}.")


if __name__ == "__main__":
    main()

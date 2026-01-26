#!/usr/bin/env python3
"""
BOF Discovery Script

Searches GitHub for recently updated C repositories with "bof" keyword,
filters out repos already in the catalog, and outputs candidates for review.

Usage:
    python find_new_bofs.py --since 2025-01-01
    python find_new_bofs.py --days 30
    python find_new_bofs.py --days 30 --markdown
"""

import argparse
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

import requests


def get_catalog_urls(catalog_path: Path) -> set[str]:
    """Extract GitHub URLs already in the catalog."""
    urls = set()
    if not catalog_path.exists():
        return urls

    content = catalog_path.read_text()
    # Match GitHub URLs in markdown links and plain URLs
    pattern = r'https?://github\.com/([^/\s\)]+)/([^/\s\)]+)'
    for match in re.finditer(pattern, content):
        owner, repo = match.groups()
        # Normalize: lowercase and strip any trailing characters
        repo = repo.split('#')[0].split('?')[0].rstrip('/')
        urls.add(f"{owner.lower()}/{repo.lower()}")

    return urls


def search_github_repos(since_date: str, token: str = None) -> list[dict]:
    """Search GitHub for C repos with 'bof' keyword updated since the given date."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    # Search query: C language, "bof" in name/description/readme, updated since date
    query = f"bof language:C pushed:>{since_date}"
    url = "https://api.github.com/search/repositories"

    all_repos = []
    page = 1

    while True:
        params = {
            "q": query,
            "sort": "updated",
            "order": "desc",
            "per_page": 100,
            "page": page
        }

        response = requests.get(url, headers=headers, params=params, timeout=30)

        if response.status_code == 403:
            print("Error: API rate limit exceeded. Set GITHUB_TOKEN env var for higher limits.",
                  file=sys.stderr)
            break

        response.raise_for_status()
        data = response.json()

        repos = data.get("items", [])
        if not repos:
            break

        all_repos.extend(repos)

        # GitHub search API returns max 1000 results
        if len(all_repos) >= data.get("total_count", 0) or page >= 10:
            break

        page += 1

    return all_repos


def format_repo(repo: dict, markdown: bool = False) -> str:
    """Format a repository for output."""
    name = repo["full_name"]
    url = repo["html_url"]
    description = repo.get("description") or "[No description]"
    stars = repo["stargazers_count"]
    updated = repo["pushed_at"][:10]  # YYYY-MM-DD

    if markdown:
        # Format as markdown table row matching catalog format
        owner, repo_name = name.split("/")
        stars_badge = f"![](https://img.shields.io/github/stars/{owner}/{repo_name}?label=&style=flat)"
        commit_badge = f"![](https://img.shields.io/github/last-commit/{owner}/{repo_name}?label=&style=flat)"
        safe_desc = description.replace("|", "\\|")
        return f"| [{repo_name}]({url}) | {safe_desc} | {stars_badge} | {commit_badge} |"
    else:
        return f"{name} ({stars} stars, updated {updated})\n  {url}\n  {description}"


def main():
    parser = argparse.ArgumentParser(
        description="Find new BOF repositories on GitHub"
    )
    date_group = parser.add_mutually_exclusive_group(required=True)
    date_group.add_argument(
        "--since",
        help="Search for repos updated since this date (YYYY-MM-DD)"
    )
    date_group.add_argument(
        "--days",
        type=int,
        help="Search for repos updated in the last N days"
    )
    parser.add_argument(
        "--markdown", "-m",
        action="store_true",
        help="Output as markdown table rows for easy copy-paste"
    )
    parser.add_argument(
        "--include-existing",
        action="store_true",
        help="Include repos already in the catalog"
    )

    args = parser.parse_args()

    # Determine the since date
    if args.since:
        since_date = args.since
    else:
        since_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")

    print(f"Searching for BOF repos updated since {since_date}...", file=sys.stderr)

    # Get existing catalog URLs
    script_dir = Path(__file__).parent
    catalog_path = script_dir.parent / "reference" / "bofs-catalog.md"
    existing_urls = get_catalog_urls(catalog_path)
    print(f"Found {len(existing_urls)} repos already in catalog", file=sys.stderr)

    # Get GitHub token from environment
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Note: Set GITHUB_TOKEN env var for higher API rate limits", file=sys.stderr)

    # Search GitHub
    repos = search_github_repos(since_date, token)
    print(f"Found {len(repos)} repos matching search", file=sys.stderr)

    # Filter out existing repos
    new_repos = []
    for repo in repos:
        repo_key = repo["full_name"].lower()
        if args.include_existing or repo_key not in existing_urls:
            new_repos.append(repo)

    if not args.include_existing:
        print(f"After filtering existing: {len(new_repos)} new candidates", file=sys.stderr)

    print("", file=sys.stderr)  # Blank line before output

    # Output results
    if args.markdown:
        print("| Project | Description | Stars | Last commit |")
        print("|---------|-------------|-------|-------------|")

    for repo in new_repos:
        print(format_repo(repo, args.markdown))
        if not args.markdown:
            print()  # Blank line between entries


if __name__ == "__main__":
    main()

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


def _paginate_search(query: str, headers: dict) -> list[dict]:
    """Run a paginated GitHub search and return all result items."""
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


def _paginate_code_search(query: str, headers: dict) -> list[dict]:
    """Run paginated GitHub code search and return all result items."""
    url = "https://api.github.com/search/code"
    all_items = []
    page = 1

    while True:
        params = {
            "q": query,
            "per_page": 100,
            "page": page,
        }

        response = requests.get(url, headers=headers, params=params, timeout=30)

        if response.status_code == 401:
            print(
                "Warning: code search requires authentication. "
                "Set GITHUB_TOKEN to enable BOF code-indicator discovery.",
                file=sys.stderr,
            )
            break

        if response.status_code == 403:
            print("Error: API rate limit exceeded during code search.", file=sys.stderr)
            break

        response.raise_for_status()
        data = response.json()
        items = data.get("items", [])
        if not items:
            break

        all_items.extend(items)

        # Code search also caps at 1000 results
        if len(all_items) >= data.get("total_count", 0) or page >= 10:
            break

        page += 1

    return all_items


def _repo_in_date_window(repo: dict, since_date: str) -> bool:
    """Check if a repository is in scope by pushed or created date."""
    pushed = (repo.get("pushed_at") or "")[:10]
    created = (repo.get("created_at") or "")[:10]
    return (pushed and pushed > since_date) or (created and created > since_date)


def _discover_code_indicator_repos(
    since_date: str, headers: dict, max_repo_fetches: int = 250
) -> list[dict]:
    """Find BOF repos by BOF-specific code indicators (e.g., .cna patterns)."""
    indicator_queries = [
        "extension:cna beacon_command_register",
        "extension:cna beacon_inline_execute",
        "extension:cna bof_pack",
    ]

    repo_candidates = {}
    for query in indicator_queries:
        items = _paginate_code_search(query, headers)
        print(f"  code query '{query}' returned {len(items)} matches", file=sys.stderr)
        for item in items:
            repo = item.get("repository") or {}
            full_name = repo.get("full_name")
            api_url = repo.get("url")
            repo_id = repo.get("id")
            if full_name and api_url and repo_id:
                repo_candidates[full_name] = (repo_id, api_url)

    detailed = []
    # Prioritize likely-new repos first (higher GitHub repo ID generally means newer repo)
    ordered_candidates = sorted(
        repo_candidates.items(),
        key=lambda item: item[1][0],
        reverse=True,
    )

    for i, (full_name, (_, api_url)) in enumerate(ordered_candidates, start=1):
        if i > max_repo_fetches:
            print(
                f"  reached max code-indicator repo fetch limit ({max_repo_fetches})",
                file=sys.stderr,
            )
            break
        response = requests.get(api_url, headers=headers, timeout=30)
        if response.status_code == 403:
            print("Error: API rate limit exceeded while fetching repo details.", file=sys.stderr)
            break
        if response.status_code != 200:
            continue
        repo = response.json()
        if _repo_in_date_window(repo, since_date):
            detailed.append(repo)

    print(f"  code-indicator repos in date window: {len(detailed)}", file=sys.stderr)
    return detailed


def search_github_repos(
    since_date: str,
    token: str = None,
    include_code_indicators: bool = True,
    max_code_repo_fetches: int = 250,
) -> list[dict]:
    """Search GitHub for C repos with 'bof' keyword updated since the given date.

    Runs two queries to avoid gaps between discovery runs:
    1. pushed:>date  — repos with code changes in the window
    2. created:>date — repos created in the window (catches repos whose
       only push was at creation time and may age out of the pushed window)
    """
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    pushed_query = f"bof language:C pushed:>{since_date}"
    created_query = f"bof language:C created:>{since_date}"

    pushed_repos = _paginate_search(pushed_query, headers)
    print(f"  pushed:> query returned {len(pushed_repos)} repos", file=sys.stderr)

    created_repos = _paginate_search(created_query, headers)
    print(f"  created:> query returned {len(created_repos)} repos", file=sys.stderr)

    code_indicator_repos = []
    if include_code_indicators:
        code_indicator_repos = _discover_code_indicator_repos(
            since_date, headers, max_repo_fetches=max_code_repo_fetches
        )

    # Deduplicate by repo id, preserving order
    seen = set()
    merged = []
    for repo in pushed_repos + created_repos + code_indicator_repos:
        if repo["id"] not in seen:
            seen.add(repo["id"])
            merged.append(repo)

    return merged


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
    parser.add_argument(
        "--no-code-indicators",
        action="store_true",
        help="Disable BOF code-indicator discovery (default: enabled)"
    )
    parser.add_argument(
        "--max-code-repo-fetches",
        type=int,
        default=250,
        help="Max repository detail lookups from code-indicator search (default: 250)"
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
    catalog_path = script_dir.parent / "BOF-CATALOG.md"
    existing_urls = get_catalog_urls(catalog_path)
    print(f"Found {len(existing_urls)} repos already in catalog", file=sys.stderr)

    # Get GitHub token from environment
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Note: Set GITHUB_TOKEN env var for higher API rate limits", file=sys.stderr)
        print(
            "Note: BOF code-indicator discovery is disabled without GITHUB_TOKEN.",
            file=sys.stderr,
        )

    # Search GitHub
    repos = search_github_repos(
        since_date,
        token,
        include_code_indicators=(not args.no_code_indicators) and bool(token),
        max_code_repo_fetches=args.max_code_repo_fetches,
    )
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

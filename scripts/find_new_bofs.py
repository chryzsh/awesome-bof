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

sys.path.insert(0, str(Path(__file__).parent))
from sanitize import sanitize_description
from repo_checks import (
    build_github_headers,
    check_binary_files,
    detect_copycats,
    fetch_owner_metadata,
    normalize_repo_name,
)

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


def compute_suspicion_signals(
    repo: dict,
    catalog_names: dict,
    headers: dict,
    owner_cache: dict,
) -> list[str]:
    """Check a candidate repo for suspicious indicators.

    Args:
        repo: GitHub API repo dict
        catalog_names: dict mapping normalized repo name -> "owner/name" (highest-star catalog entry)
        headers: GitHub API headers
        owner_cache: dict for caching owner metadata

    Returns list of warning strings.
    """
    warnings = []
    repo_name = repo["name"]
    full_name = repo["full_name"]
    norm = normalize_repo_name(repo_name)

    # Check for name collision with existing catalog entries
    if norm in catalog_names:
        existing = catalog_names[norm]
        if full_name.lower() != existing.lower():
            warnings.append(
                f"POSSIBLE_COPYCAT: shares name with catalog entry {existing}"
            )

    # Check owner account
    owner = repo["owner"]["login"]
    owner_meta = fetch_owner_metadata(owner, headers, owner_cache)
    if owner_meta:
        created = owner_meta.get("created_at", "")
        pub_repos = owner_meta.get("public_repos", 0)
        if created:
            try:
                from datetime import timezone
                created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                age_days = (datetime.now(timezone.utc) - created_dt).days
                if age_days < 90 and pub_repos < 3:
                    warnings.append(
                        f"NEW_ACCOUNT: owner created {age_days}d ago, {pub_repos} public repos"
                    )
            except (ValueError, TypeError):
                pass

    return warnings


def build_catalog_name_index(catalog_path: Path) -> dict:
    """Build a dict mapping normalized repo names to 'owner/name' from the catalog.

    When multiple repos share a normalized name, keeps the first one found
    (catalog is roughly ordered by prominence).
    """
    index = {}
    if not catalog_path.exists():
        return index

    pattern = re.compile(r'https?://github\.com/([^/\s\)]+)/([^/\s\)]+)')
    for line in catalog_path.read_text().splitlines():
        m = pattern.search(line)
        if m:
            owner, name = m.groups()
            name = name.split("#")[0].split("?")[0].rstrip("/")
            norm = normalize_repo_name(name)
            if norm not in index:
                index[norm] = f"{owner}/{name}"
    return index


def format_repo(repo: dict, markdown: bool = False, warnings: list = None) -> str:
    """Format a repository for output."""
    name = repo["full_name"]
    url = repo["html_url"]
    description = sanitize_description(repo.get("description") or "[No description]")
    stars = repo["stargazers_count"]
    updated = repo["pushed_at"][:10]  # YYYY-MM-DD

    if markdown:
        # Format as markdown table row matching catalog format
        owner, repo_name = name.split("/")
        stars_badge = f"![](https://img.shields.io/github/stars/{owner}/{repo_name}?label=&style=flat)"
        commit_badge = f"![](https://img.shields.io/github/last-commit/{owner}/{repo_name}?label=&style=flat)"
        safe_desc = description.replace("|", "\\|")
        row = f"| [{repo_name}]({url}) | {safe_desc} | {stars_badge} | {commit_badge} |"
        if warnings:
            warning_lines = "; ".join(warnings)
            row += f"\n> **Warnings:** {warning_lines}"
        return row
    else:
        output = f"{name} ({stars} stars, updated {updated})\n  {url}\n  {description}"
        if warnings:
            for w in warnings:
                output += f"\n  WARNING: {w}"
        return output


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
    parser.add_argument(
        "--skip-suspicious",
        action="store_true",
        help="Auto-skip candidates flagged as POSSIBLE_COPYCAT"
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

    # Compute suspicion signals for each candidate
    catalog_names = build_catalog_name_index(catalog_path)
    headers = build_github_headers(token)
    owner_cache = {}
    repo_warnings = {}
    for repo in new_repos:
        signals = compute_suspicion_signals(repo, catalog_names, headers, owner_cache)
        if signals:
            repo_warnings[repo["id"]] = signals

    # Filter out suspicious if requested
    if args.skip_suspicious:
        before = len(new_repos)
        new_repos = [
            r for r in new_repos
            if not any("POSSIBLE_COPYCAT" in w for w in repo_warnings.get(r["id"], []))
        ]
        skipped = before - len(new_repos)
        if skipped:
            print(f"Skipped {skipped} suspicious candidates", file=sys.stderr)

    print("", file=sys.stderr)  # Blank line before output

    # Output results
    if args.markdown:
        print("| Project | Description | Stars | Last commit |")
        print("|---------|-------------|-------|-------------|")

    for repo in new_repos:
        warnings = repo_warnings.get(repo["id"])
        print(format_repo(repo, args.markdown, warnings))
        if not args.markdown:
            print()  # Blank line between entries


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Audit BOF catalog for suspicious/copycat repositories.

Checks all repos in BOF-CATALOG.md against multiple heuristics:
- Copycat detection (shared names with higher-starred originals)
- Pre-compiled binaries without source code
- Account age and activity signals
- Dead repos (404)
- Low-quality signals (low stars, no description)

Usage:
    python3 scripts/audit_catalog.py
    python3 scripts/audit_catalog.py --json
    python3 scripts/audit_catalog.py --min-stars 3
    python3 scripts/audit_catalog.py --check-binaries
"""

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from repo_checks import (
    build_github_headers,
    check_binary_files,
    detect_copycats,
    fetch_owner_metadata,
    fetch_repo_metadata,
)

_REPO_URL_RE = re.compile(
    r"\|\s*\[[^\]]+\]\(https?://github\.com/([^/\s\)]+)/([^/\s\)]+)\)"
)


@dataclass
class AuditResult:
    owner: str
    name: str
    url: str
    flags: list = field(default_factory=list)
    stars: int = 0
    description: str = ""
    created_at: str = ""
    owner_account_age_days: int = -1
    owner_public_repos: int = -1
    binary_files: list = field(default_factory=list)
    possible_copycat_of: str = ""
    catalog_line: int = 0


def parse_catalog(catalog_path):
    """Extract repo entries with line numbers from BOF-CATALOG.md."""
    entries = []
    with open(catalog_path) as f:
        for i, line in enumerate(f, 1):
            m = _REPO_URL_RE.search(line)
            if m:
                owner, name = m.groups()
                name = name.split("#")[0].split("?")[0].rstrip("/")
                entries.append({
                    "owner": owner,
                    "name": name,
                    "url": f"https://github.com/{owner}/{name}",
                    "line": i,
                })
    return entries


def audit_repo(entry, headers, owner_cache, min_stars=3, check_binaries=False):
    """Run all checks on a single repo entry."""
    result = AuditResult(
        owner=entry["owner"],
        name=entry["name"],
        url=entry["url"],
        catalog_line=entry["line"],
    )

    # Fetch repo metadata
    meta = fetch_repo_metadata(entry["owner"], entry["name"], headers)
    if meta is None:
        result.flags.append("REPO_NOT_FOUND")
        return result

    result.stars = meta.get("stargazers_count", 0)
    result.description = meta.get("description") or ""
    result.created_at = meta.get("created_at", "")

    # Low stars
    if result.stars < min_stars:
        result.flags.append("LOW_STARS")

    # No description
    if not result.description.strip():
        result.flags.append("NO_DESCRIPTION")

    # Owner signals
    owner_meta = fetch_owner_metadata(entry["owner"], headers, owner_cache)
    if owner_meta:
        created = owner_meta.get("created_at", "")
        if created:
            try:
                created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                age_days = (datetime.now(timezone.utc) - created_dt).days
                result.owner_account_age_days = age_days
                if age_days < 90:
                    result.flags.append("NEW_ACCOUNT")
            except (ValueError, TypeError):
                pass

        pub_repos = owner_meta.get("public_repos", 0)
        result.owner_public_repos = pub_repos
        if pub_repos < 3:
            result.flags.append("LOW_ACTIVITY_ACCOUNT")

    # Pre-compiled binaries (optional, costs extra API calls)
    if check_binaries:
        binaries = check_binary_files(entry["owner"], entry["name"], headers)
        if binaries:
            result.binary_files = binaries[:10]  # cap for readability
            result.flags.append("PRECOMPILED_BINARIES")

    return result


def run_audit(entries, headers, min_stars=3, check_binaries=False):
    """Audit all entries and run cross-repo copycat detection."""
    owner_cache = {}
    results = []

    total = len(entries)
    for i, entry in enumerate(entries, 1):
        if i % 50 == 0 or i == 1:
            print(f"  Auditing {i}/{total}...", file=sys.stderr)

        result = audit_repo(entry, headers, owner_cache, min_stars, check_binaries)
        results.append(result)

    # Cross-repo copycat detection
    repos_for_copycat = [
        {
            "owner": r.owner,
            "name": r.name,
            "stars": r.stars,
            "created_at": r.created_at,
        }
        for r in results
        if "REPO_NOT_FOUND" not in r.flags
    ]
    copycats = detect_copycats(repos_for_copycat)

    for result in results:
        key = f"{result.owner}/{result.name}"
        if key in copycats:
            result.possible_copycat_of = copycats[key]
            result.flags.append("POSSIBLE_COPYCAT")

    return results


def format_report(results, output_json=False):
    """Format audit results as markdown or JSON."""
    flagged = [r for r in results if r.flags]

    if output_json:
        return json.dumps([asdict(r) for r in flagged], indent=2)

    if not flagged:
        return "No suspicious repos found."

    # Group by severity
    severity_order = [
        "REPO_NOT_FOUND",
        "POSSIBLE_COPYCAT",
        "PRECOMPILED_BINARIES",
        "NEW_ACCOUNT",
        "LOW_ACTIVITY_ACCOUNT",
        "LOW_STARS",
        "NO_DESCRIPTION",
    ]

    lines = [
        f"# Catalog Audit Report",
        f"",
        f"**Total repos scanned:** {len(results)}",
        f"**Flagged repos:** {len(flagged)}",
        f"",
    ]

    for flag_type in severity_order:
        matching = [r for r in flagged if flag_type in r.flags]
        if not matching:
            continue

        lines.append(f"## {flag_type} ({len(matching)})")
        lines.append("")
        lines.append("| Repo | Stars | Line | All Flags | Details |")
        lines.append("|------|-------|------|-----------|---------|")

        for r in matching:
            details = ""
            if r.possible_copycat_of:
                details += f"copycat of {r.possible_copycat_of}"
            if r.binary_files:
                details += f" binaries: {', '.join(r.binary_files[:3])}"
            if r.owner_account_age_days >= 0:
                details += f" account: {r.owner_account_age_days}d"

            flags_str = ", ".join(r.flags)
            lines.append(
                f"| [{r.owner}/{r.name}]({r.url}) | {r.stars} | {r.catalog_line} | {flags_str} | {details.strip()} |"
            )

        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Audit BOF catalog for suspicious repositories"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output as JSON"
    )
    parser.add_argument(
        "--min-stars", type=int, default=3,
        help="Star threshold for LOW_STARS flag (default: 3)"
    )
    parser.add_argument(
        "--check-binaries", action="store_true",
        help="Scan repo trees for pre-compiled binaries (slower, extra API calls)"
    )
    parser.add_argument(
        "--output", "-o", type=str,
        help="Write report to file instead of stdout"
    )

    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print(
            "Error: GITHUB_TOKEN required for auditing (731+ API calls).",
            file=sys.stderr,
        )
        sys.exit(1)

    headers = build_github_headers(token)

    catalog_path = Path(__file__).parent.parent / "BOF-CATALOG.md"
    if not catalog_path.exists():
        print(f"Error: {catalog_path} not found", file=sys.stderr)
        sys.exit(1)

    entries = parse_catalog(catalog_path)
    print(f"Found {len(entries)} repos in catalog", file=sys.stderr)

    results = run_audit(entries, headers, args.min_stars, args.check_binaries)
    report = format_report(results, args.json)

    if args.output:
        Path(args.output).write_text(report)
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    main()

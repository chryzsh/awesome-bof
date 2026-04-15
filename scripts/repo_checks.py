"""Shared repository suspicion checks used by audit_catalog.py and find_new_bofs.py.

Provides reusable functions for detecting copycat repos, pre-compiled binaries,
suspicious account signals, and rate-limited GitHub API access.
"""

import re
import sys
import time

import requests

# Suffixes commonly appended to copied repo names
_STRIP_SUFFIXES = re.compile(
    r"[-_]?(fork|copy|clone|mod|modified|updated|new|v2|ag|port)$", re.IGNORECASE
)

# Binary file extensions that are suspicious without corresponding source
BINARY_EXTENSIONS = {".o", ".obj", ".exe", ".dll", ".bin", ".sys", ".so", ".dylib"}
SOURCE_EXTENSIONS = {".c", ".h", ".cpp", ".hpp", ".cxx"}


def rate_limited_get(url, headers, params=None, timeout=30, retries=3):
    """GET with automatic rate-limit backoff and transient-error retry.

    Returns the Response object, or None if rate-limited/unreachable after retries.
    """
    response = None
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
            break
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            if attempt == retries - 1:
                print(f"  Network error after {retries} attempts: {e}", file=sys.stderr)
                return None
            backoff = 2 ** attempt
            print(f"  Transient error, retrying in {backoff}s...", file=sys.stderr)
            time.sleep(backoff)

    if response is None:
        return None

    if response.status_code == 403:
        remaining = int(response.headers.get("X-RateLimit-Remaining", "0"))
        if remaining == 0:
            reset_at = int(response.headers.get("X-RateLimit-Reset", "0"))
            wait = max(reset_at - int(time.time()), 1)
            if wait <= 120:
                print(f"  Rate limited, waiting {wait}s...", file=sys.stderr)
                time.sleep(wait + 1)
                try:
                    response = requests.get(
                        url, headers=headers, params=params, timeout=timeout
                    )
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                    return None
            else:
                print(
                    f"  Rate limited, reset in {wait}s (too long to wait).",
                    file=sys.stderr,
                )
                return None

    return response


def normalize_repo_name(name):
    """Normalize repo name for copycat comparison.

    Lowercases, strips common fork/copy suffixes.
    """
    name = name.lower().strip()
    name = _STRIP_SUFFIXES.sub("", name)
    return name


def fetch_repo_metadata(owner, name, headers):
    """Fetch repository metadata from GitHub API.

    Returns the JSON dict or None on failure.
    """
    url = f"https://api.github.com/repos/{owner}/{name}"
    resp = rate_limited_get(url, headers)
    if resp is None or resp.status_code != 200:
        return None
    return resp.json()


def fetch_owner_metadata(owner, headers, cache=None):
    """Fetch GitHub user metadata, with optional cache.

    Returns the JSON dict or None on failure.
    """
    if cache is not None and owner in cache:
        return cache[owner]

    url = f"https://api.github.com/users/{owner}"
    resp = rate_limited_get(url, headers)
    result = None
    if resp is not None and resp.status_code == 200:
        result = resp.json()

    if cache is not None:
        cache[owner] = result
    return result


def check_binary_files(owner, name, headers):
    """Check repo tree for pre-compiled binary files without corresponding source.

    Returns a list of suspicious binary file paths, or empty list.
    Only flags binaries when no source files (.c/.h) exist in the same directory.
    """
    url = f"https://api.github.com/repos/{owner}/{name}/git/trees/HEAD"
    resp = rate_limited_get(url, headers, params={"recursive": "1"})
    if resp is None or resp.status_code != 200:
        return []

    tree = resp.json().get("tree", [])

    # Group files by directory
    dir_files = {}
    for entry in tree:
        if entry.get("type") != "blob":
            continue
        path = entry["path"]
        parts = path.rsplit("/", 1)
        directory = parts[0] if len(parts) > 1 else ""
        filename = parts[-1]
        dir_files.setdefault(directory, []).append(filename)

    suspicious = []
    for directory, files in dir_files.items():
        has_source = any(
            f.endswith(tuple(SOURCE_EXTENSIONS)) for f in files
        )
        for f in files:
            ext = "." + f.rsplit(".", 1)[-1] if "." in f else ""
            if ext.lower() in BINARY_EXTENSIONS and not has_source:
                path = f"{directory}/{f}" if directory else f
                suspicious.append(path)

    return suspicious


def detect_copycats(repos_with_metadata):
    """Detect potential copycat repos by grouping on normalized name.

    Args:
        repos_with_metadata: list of dicts with keys:
            "owner", "name", "stars", "created_at"

    Returns:
        dict mapping "owner/name" -> "original_owner/original_name"
        for repos flagged as possible copycats.
    """
    # Group by normalized name
    groups = {}
    for repo in repos_with_metadata:
        norm = normalize_repo_name(repo["name"])
        groups.setdefault(norm, []).append(repo)

    copycats = {}
    for norm_name, group in groups.items():
        if len(group) < 2:
            continue

        # The "original" is the one with the most stars
        group.sort(key=lambda r: r["stars"], reverse=True)
        original = group[0]

        # Only flag if the original has meaningful stars
        if original["stars"] < 5:
            continue

        for repo in group[1:]:
            # Flag if repo has <20% of original's stars
            if repo["stars"] < original["stars"] * 0.2:
                key = f"{repo['owner']}/{repo['name']}"
                orig_key = f"{original['owner']}/{original['name']}"
                copycats[key] = orig_key

    return copycats


def build_github_headers(token=None):
    """Build standard GitHub API headers."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    return headers

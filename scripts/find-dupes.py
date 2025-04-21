#!/usr/bin/env python3

import os
import re
import argparse
from collections import defaultdict
import sys

# Regex to find a Markdown link: [text](url) and capture the url
MARKDOWN_LINK_PATTERN = re.compile(r'\[.*?\]\(([^)]+)\)')

# Regex to match a GitHub repo URL and capture the username/repo part
# Ensures it starts with http/https and github.com
GITHUB_REPO_PATTERN = re.compile(r'^https?://github\.com/([\w._-]+/[\w._-]+)')

def find_markdown_files(root_dir):
    """Recursively finds all '.md' files in the given directory."""
    markdown_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith(".md"):
                markdown_files.append(os.path.join(dirpath, filename))
    return markdown_files

def extract_repo_references(filepath):
    """
    Extracts 'username/repo' references ONLY from the primary Markdown link
    (expected in the first data column of a table row) in a file.
    """
    references = []
    file_name = os.path.basename(filepath)
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                stripped_line = line.strip()
                # Check if the line looks like a table row
                if not stripped_line.startswith('|') or not stripped_line.endswith('|'):
                    continue

                parts = stripped_line.split('|')
                # Need at least 4 parts for "| Col1 | Col2 | ... |" structure
                # parts[0] is empty, parts[1] is Col1 content, parts[2] is Col2 content etc. parts[-1] is empty
                if len(parts) < 4:
                    continue

                # Target the content of the first data column (between the first two pipes)
                first_col_content = parts[1].strip()

                # Find the first Markdown link within this first column's content
                link_match = MARKDOWN_LINK_PATTERN.search(first_col_content)
                if not link_match:
                    continue # No markdown link found in the first column

                # Extract the URL from the link
                url = link_match.group(1).strip()

                # Check if this URL is specifically a GitHub repo URL
                repo_match = GITHUB_REPO_PATTERN.match(url) # Use match() for start-of-string check
                if repo_match:
                    # Extract the username/repo part
                    repo_path = repo_match.group(1)
                    # Clean potential trailing characters (though less likely with stricter regex)
                    repo_path = repo_path.rstrip('./')
                    normalized_repo = repo_path.lower()

                    # Store the reference details
                    references.append({
                        "repo": normalized_repo,
                        "file_path": filepath,
                        "file_name": file_name,
                        "line": line_num,
                        "content": stripped_line # Store original stripped line content
                    })

    except IOError as e:
        print(f"Error reading file {filepath}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred processing {filepath}: {e}", file=sys.stderr)
    return references

def main():
    parser = argparse.ArgumentParser(
        description="Find duplicate table entries based on the primary GitHub link in the first column within the *same* Markdown file."
    )
    parser.add_argument(
        "root_dir",
        help="The root directory to search for Markdown files recursively."
    )
    args = parser.parse_args()

    if not os.path.isdir(args.root_dir):
        print(f"Error: Directory not found: {args.root_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning for Markdown files in '{args.root_dir}'...")
    markdown_files = find_markdown_files(args.root_dir)

    if not markdown_files:
        print("No Markdown files found.")
        sys.exit(0)

    print(f"Found {len(markdown_files)} Markdown files. Extracting primary table link references...")

    # Store all valid references found
    all_references_list = []
    total_refs_found = 0

    for md_file in markdown_files:
        refs_in_file = extract_repo_references(md_file)
        all_references_list.extend(refs_in_file)
        total_refs_found += len(refs_in_file)

    print(f"Found {total_refs_found} primary GitHub link references in table rows.")
    print("-" * 30)

    # Group references by (normalized_repo, file_name)
    grouped_references = defaultdict(list)
    for ref in all_references_list:
        key = (ref['repo'], ref['file_name'])
        grouped_references[key].append(ref)

    # --- Reporting Duplicates Found WITHIN the SAME FILE based on Primary Link ---
    duplicates_found_overall = False
    # Sort keys for consistent output (by repo, then filename)
    sorted_keys = sorted(grouped_references.keys())

    for key in sorted_keys:
        locations = grouped_references[key]
        if len(locations) > 1: # Found duplicates of this primary repo link within this specific file
            repo, file_name = key
            if not duplicates_found_overall:
                print("Duplicate Primary Link References Found (within the same file):")
                duplicates_found_overall = True

            print(f"\nRepository: {repo} (Found {len(locations)} times as primary link in File: {file_name})")
            # Sort locations within the file by line number
            sorted_locations = sorted(locations, key=lambda x: x['line'])
            for loc in sorted_locations:
                # Use file_path for the full path display
                print(f"  - Path: {loc['file_path']}, Line: {loc['line']}")
                print(f"    Content: {loc['content']}")

    if not duplicates_found_overall:
        print("No duplicate primary link references found within the same file.")

if __name__ == "__main__":
    main()
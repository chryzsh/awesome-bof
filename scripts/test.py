 #!/usr/bin/env python3

import re
import requests
import time
import argparse
from urllib.parse import urlparse
import os

# --- Configuration ---

# Delay between requests to avoid rate limiting
REQUEST_DELAY_SECONDS = 0.5

# --- Functions ---

def extract_repo_urls(markdown_content):
    """Extracts GitHub repo URLs from Markdown table rows."""
    # Regex: Look for lines starting with '| [' then capture the URL in (...)
    # Handles both http and https
    urls = re.findall(r"^\s*\|\s*\[.*?\]\((https?://github\.com/[^/]+/[^)]+)\)", markdown_content, re.MULTILINE)
    return list(set(urls)) # Use set to remove duplicates, then convert back to list

def get_raw_readme_url(repo_url):
    """Attempts to construct the raw README URL for main and master branches."""
    parsed_url = urlparse(repo_url)
    if parsed_url.netloc.lower() != 'github.com':
        return None, None # Not a github URL

    path_parts = parsed_url.path.strip('/').split('/')
    if len(path_parts) < 2:
        return None, None # Invalid path

    user = path_parts[0]
    repo = path_parts[1]

    # URLs for raw content
    raw_url_main = f"https://raw.githubusercontent.com/{user}/{repo}/main/README.md"
    raw_url_master = f"https://raw.githubusercontent.com/{user}/{repo}/master/README.md"

    return raw_url_main, raw_url_master

def fetch_readme_content(repo_url):
    """Fetches the raw README content, trying main and master branches."""
    raw_url_main, raw_url_master = get_raw_readme_url(repo_url)
    if not raw_url_main:
        print(f"[-] Invalid GitHub URL structure: {repo_url}")
        return None

    headers = {'Accept': 'text/plain'} # Ask for plain text
    content = None
    print(f"[*] Fetching README for {repo_url}")

    # Try main branch first
    try:
        # print(f"[*] Trying main branch...")
        response = requests.get(raw_url_main, headers=headers, timeout=15) # Increased timeout
        if response.status_code == 200:
            content = response.text
            # print(f"[+] Found README on main branch.")
        elif response.status_code == 404:
            # print(f"[-] README not found on main branch (404).")
            pass # Don't print noise if it's just not found
        else:
            print(f"[!] Warning: Error fetching main branch for {repo_url}: Status {response.status_code}")

    except requests.exceptions.Timeout:
         print(f"[!] Warning: Timeout fetching main branch for {repo_url}")
    except requests.exceptions.RequestException as e:
        print(f"[!] Warning: Network error fetching main branch for {repo_url}: {e}")

    # If main failed, try master branch
    if content is None and raw_url_master:
         time.sleep(REQUEST_DELAY_SECONDS / 2) # Smaller delay between branch attempts
         try:
            # print(f"[*] Trying master branch...")
            response = requests.get(raw_url_master, headers=headers, timeout=15) # Increased timeout
            if response.status_code == 200:
                content = response.text
                # print(f"[+] Found README on master branch.")
            elif response.status_code == 404:
                 # print(f"[-] README not found on master branch (404).")
                 pass # Don't print noise
            else:
                print(f"[!] Warning: Error fetching master branch for {repo_url}: Status {response.status_code}")

         except requests.exceptions.Timeout:
            print(f"[!] Warning: Timeout fetching master branch for {repo_url}")
         except requests.exceptions.RequestException as e:
            print(f"[!] Warning: Network error fetching master branch for {repo_url}: {e}")

    if content is None:
        print(f"[-] Failed to fetch README for {repo_url} on main or master branch.")
    return content


def extract_potential_bofs(readme_content):
    """
    Applies heuristics to extract potential BOF names from README Markdown.
    THIS IS HEURISTIC AND WILL LIKELY NEED TUNING.
    """
    if not readme_content:
        return []

    found_bofs = set()

    # --- Heuristics (Add more as needed) ---

    # 1. Look for items in backticks (common for commands/filenames)
    #    Regex: Find words (alphanumeric, underscore, hyphen) within backticks
    #    Ignore very short (1-2 chars) or very long names.
    #    Added check for .c/.o extensions specifically.
    for potential_name in re.findall(r"`([a-zA-Z0-9_.-]+\.(?:c|o)|[a-zA-Z0-9_-]{3,35})`", readme_content): # Increased max length slightly
         # Basic filtering (can be improved)
        if len(potential_name) > 2:
             # Avoid adding common markdown/code terms if possible (tricky)
             if potential_name.lower() not in ['bof', 'c', 'o', 'cs', 'cpp', 'dll', 'exe', 'aggressor', 'output', 'input', 'cmd', 'ps']:
                 found_bofs.add(potential_name.strip().strip('.')) # Strip trailing dots too

    # 2. Look for bold items (another common formatting)
    #    Regex: Similar logic for text within **...**
    for potential_name in re.findall(r"\*\*([a-zA-Z0-9_.-]+\.(?:c|o)|[a-zA-Z0-9_-]{3,35})\*\*", readme_content): # Increased max length slightly
         if len(potential_name) > 2:
             if potential_name.lower() not in ['bof', 'c', 'o', 'cs', 'cpp', 'dll', 'exe', 'aggressor', 'output', 'input', 'cmd', 'ps']:
                 found_bofs.add(potential_name.strip().strip('.'))

    # 3. Look for list items (lines starting with *, -, or number.)
    #    Try to grab the first likely "name" part after the marker.
    #    Regex: Matches start marker, optional formatting (`/`), captures the name part.
    for line in readme_content.splitlines():
        # Match lines like: * `bof_name` ... OR - **bof_name** ... OR 1. bof_name: ...
        # Adjusted regex to be slightly more flexible and capture name before common separators
        match = re.match(r"^\s*(?:[-*]|\d+\.)\s+[`\*]*([a-zA-Z0-9_.-]+\.(?:c|o)|[a-zA-Z0-9_-]{3,35})[`\*]*[\s:–-]", line)
        if match:
            potential_name = match.group(1)
            if potential_name: # Check if group(1) actually captured something
                if len(potential_name) > 2:
                     if potential_name.lower() not in ['bof', 'c', 'o', 'cs', 'cpp', 'dll', 'exe', 'aggressor', 'usage', 'example', 'note', 'output', 'input', 'cmd', 'ps']:
                         found_bofs.add(potential_name.strip().strip('.'))

    # 4. Look for specific filenames mentioned (e.g., "compile mybof.c")
    for potential_name in re.findall(r'([a-zA-Z0-9_-]+\.(?:c|o))\b', readme_content):
         # Filter out generic examples if possible
         if potential_name.lower() not in ['beacon.c', 'beacon.h', 'example.c', 'main.c', 'common.c', 'common.h']:
             found_bofs.add(potential_name.strip())

    # 5. Look for text following numbered headings (like the Yaxser example)
    #    Regex: Match "# Number ) Potential BOF Name Here"
    for match in re.finditer(r"^\s*#+\s*\d+\s*\)\s*(.*)", readme_content, re.MULTILINE | re.IGNORECASE):
        potential_name = match.group(1).strip()
        # Simple cleanup: remove trailing markdown like '[...]' or further description
        potential_name = re.sub(r'\[.*?\].*$', '', potential_name).strip()
        potential_name = re.sub(r'[:–-].*$', '', potential_name).strip() # Remove description after hyphen/colon/emdash
        # Check if it looks like a reasonable name
        if 2 < len(potential_name) < 50 and re.match(r'^[a-zA-Z0-9\s_/().-]+$', potential_name): # Allow more chars in name
             # Avoid overly generic heading titles
             if potential_name.lower() not in ['usage', 'compilation', 'instructions', 'features', 'acknowledgement', 'acknowledgments', 'example', 'introduction', 'overview', 'note', 'notes', 'why are you doing this', 'did you write this from the ground up', 'note on quality', 'can i/we reach you', 'can i/we help you', 'requirements', 'setup']:
                found_bofs.add(potential_name.strip().strip('.'))


    # --- Final Filtering ---
    # Convert set to list and sort
    bof_list = sorted(list(found_bofs), key=str.lower) # Case-insensitive sort

    # Remove items that are likely just descriptions or common words (can be expanded)
    # Added more specific words to filter
    common_words_to_filter = {
        'the', 'and', 'for', 'with', 'using', 'via', 'from', 'this', 'that', 'bof', 'file', 'object', 'beacon', 'cobalt', 'strike',
        'command', 'output', 'input', 'example', 'description', 'parameter', 'argument', 'arguments', 'function', 'feature',
        'module', 'script', 'tool', 'utility', 'windows', 'linux', 'api', 'net', 'system', 'process', 'thread', 'memory',
        'injection', 'payload', 'bypass', 'lateral', 'movement', 'privilege', 'escalation', 'collection', 'various', 'general',
        'purpose', 'command', 'control', 'active', 'directory', 'kerberos', 'number', 'string', 'value', 'path', 'name'
        }
    # Filter based on common words and word count
    bof_list = [
        bof for bof in bof_list
        if bof.lower() not in common_words_to_filter and len(bof.split()) < 5 # Exclude multi-word phrases > 4 words
           and not re.match(r'^\d+$', bof) # Exclude pure numbers
           and not (bof.startswith('.') or bof.endswith('.')) # Exclude if starts/ends with dot after strip
           and len(bof) > 2 # Ensure min length after stripping
    ]

    # Specific post-filter for common false positives if needed
    # e.g., bof_list = [bof for bof in bof_list if bof.lower() != 'readme.md']

    return bof_list

# --- Main Execution ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract potential BOF names from READMEs linked in a Markdown file.")
    parser.add_argument("markdown_file", help="Path to the input Markdown file containing the table of repositories.")
    args = parser.parse_args()

    if not os.path.exists(args.markdown_file):
        print(f"[!] Error: Input file not found: {args.markdown_file}")
        exit(1)

    print(f"[*] Reading input file: {args.markdown_file}")
    try:
        with open(args.markdown_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
    except Exception as e:
        print(f"[!] Error reading file: {e}")
        exit(1)

    repo_urls = extract_repo_urls(markdown_content)
    print(f"[*] Found {len(repo_urls)} unique repository URLs in the table.")

    results = {}

    for i, url in enumerate(repo_urls, 1):
        print("-" * 40)
        print(f"[*] Processing {i}/{len(repo_urls)}: {url}")
        readme = fetch_readme_content(url)

        if readme:
            potential_bofs = extract_potential_bofs(readme)
            results[url] = potential_bofs
            print(f"[*] Potential BOFs found: {potential_bofs if potential_bofs else 'None detected'}")
        else:
            results[url] = [] # Mark as processed but no content/BOFs found

        # Respectful delay
        if i < len(repo_urls): # Don't sleep after the last one
            time.sleep(REQUEST_DELAY_SECONDS)

    print("\n" + "=" * 60)
    print("          FINAL RESULTS SUMMARY")
    print("=" * 60)
    updated_markdown_lines = []
    processed_urls = set()

    # Rebuild the markdown table with results
    print("[*] Generating updated Markdown snippet (add 'Includes' column manually if needed):\n")
    original_lines = markdown_content.splitlines()
    header_found = False
    table_separator_found = False
    output_started = False

    for line in original_lines:
        match = re.search(r"^\s*\|\s*\[.*?\]\((https?://github\.com/[^/]+/[^)]+)\)", line)
        current_line_url = match.group(1) if match else None

        # Handle table header and separator
        if re.match(r"^\s*\|\s*Project\s*\|", line, re.IGNORECASE):
             print(f"| Project | Description | Includes | Stars | Last commit |") # Suggest new header
             updated_markdown_lines.append(line) # Keep original structure for now
             header_found = True
             continue
        if header_found and re.match(r"^\s*\|\s*-+.*", line):
             print(f"|---------|-------------|----------|-------|-------------|") # Suggest new separator
             updated_markdown_lines.append(line) # Keep original structure
             table_separator_found = True
             output_started = True # Start printing table rows after this
             continue

        if current_line_url and current_line_url in results:
            bofs = results[current_line_url]
            bofs_str = ", ".join(f"`{b}`" for b in bofs) if bofs else "" # Format BOFs in backticks
            # Attempt to insert the BOF list into the existing table line
            parts = line.strip().split('|')
            if len(parts) >= 4: # Expecting at least | Project | Desc | Stars | Commit | (5 parts with outer pipes)
                # Insert the new column between Description and Stars
                new_line = f"| {parts[1].strip()} | {parts[2].strip()} | {bofs_str} | {parts[3].strip()} | {parts[4].strip()} |"
                print(new_line)
                updated_markdown_lines.append(new_line)
                processed_urls.add(current_line_url)
            else:
                 # Fallback if parsing the line fails, just print original and results separately
                print(line)
                print(f"  (Includes: {bofs_str})")
                updated_markdown_lines.append(line) # Keep original line
        elif output_started: # Print non-URL lines within the table area as is
            print(line)
            updated_markdown_lines.append(line)


    print("\n" + "=" * 60)
    print("[*] Processing Complete.")
    # Optionally write the updated_markdown_lines to a new file
    # with open("output.md", "w", encoding='utf-8') as f_out:
    #    f_out.write("\n".join(updated_markdown_lines))
    # print("[*] Updated markdown structure written to output.md (for review)")

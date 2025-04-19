#!/usr/bin/env python3

import re
import requests
import time
import argparse
from urllib.parse import urlparse, urljoin
import os
import sys

# --- Configuration ---
REQUEST_DELAY_SECONDS = 0.5

# --- Functions --- (Keep functions as they are, no changes needed here)
def extract_repo_urls(markdown_content):
    urls = re.findall(r"^\s*\|\s*\[.*?\]\((https?://github\.com/[^/]+/[^)]+)\)", markdown_content, re.MULTILINE)
    return list(set(urls))
# ... (keep get_repo_base_info, get_raw_file_url, fetch_readme_content, extract_potential_bofs) ...
def get_repo_base_info(repo_url):
    parsed_url = urlparse(repo_url);
    if parsed_url.netloc.lower() != 'github.com': return None, None, None
    path_parts = parsed_url.path.strip('/').split('/');
    if len(path_parts) < 2: return None, None, None
    user = path_parts[0]; repo = path_parts[1]; base_url = f"https://github.com/{user}/{repo}"
    return user, repo, base_url
def get_raw_file_url(user, repo, file_path, branch):
    return f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{file_path.lstrip('/')}"
def fetch_readme_content(repo_url):
    user, repo, base_url = get_repo_base_info(repo_url);
    if not user: return None, None
    headers = {'Accept': 'text/plain'}; content = None; found_branch = None;
    for branch in ['main', 'master']:
        readme_path = 'README.md'; raw_url = get_raw_file_url(user, repo, readme_path, branch);
        try:
            response = requests.get(raw_url, headers=headers, timeout=15);
            if response.status_code == 200: content = response.text; found_branch = branch; break;
            elif response.status_code != 404: print(f"[!] Warning: Fetch '{branch}' for {repo_url}: Status {response.status_code}", file=sys.stderr)
        except requests.exceptions.Timeout: print(f"[!] Warning: Timeout fetch '{branch}' for {repo_url}", file=sys.stderr)
        except requests.exceptions.RequestException as e: print(f"[!] Warning: Network error fetch '{branch}' for {repo_url}: {e}", file=sys.stderr)
        if content is None and branch == 'main': time.sleep(REQUEST_DELAY_SECONDS / 2)
    return content, found_branch
def extract_potential_bofs(readme_content, repo_url=None, user=None, repo=None, branch=None):
    if not readme_content: return []
    found_bofs = set();
    # 1: Backticks
    for name in re.findall(r"`([a-zA-Z0-9_.-]+\.(?:c|o)|[a-zA-Z0-9_.-]{3,35})`", readme_content):
        if len(name) > 2 and name.lower() not in ['bof','c','o','cs','cpp','dll','exe','aggressor','output','input','cmd','ps']: found_bofs.add(name.strip('.'))
    # 2: Bold
    for name in re.findall(r"\*\*([a-zA-Z0-9_.-]+\.(?:c|o)|[a-zA-Z0-9_.-]{3,35})\*\*", readme_content):
        if len(name) > 2 and name.lower() not in ['bof','c','o','cs','cpp','dll','exe','aggressor','output','input','cmd','ps']: found_bofs.add(name.strip('.'))
    # 3: List items
    for line in readme_content.splitlines():
        m = re.match(r"^\s*(?:[-*]|\d+\.)\s+[`\*]*([a-zA-Z0-9_.-]+\.(?:c|o)|[a-zA-Z0-9_.-]{3,35})[`\*]*[\s:–-]", line)
        if m and m.group(1) and len(m.group(1)) > 2 and m.group(1).lower() not in ['bof','c','o','cs','cpp','dll','exe','aggressor','usage','example','note','output','input','cmd','ps']: found_bofs.add(m.group(1).strip('.'))
    # 4: Filenames .c/.o
    for name in re.findall(r'([a-zA-Z0-9_-]+\.(?:c|o))\b', readme_content):
        if name.lower() not in ['beacon.c','beacon.h','example.c','main.c','common.c','common.h']: found_bofs.add(name.strip())
    # 5: Numbered headings
    for m in re.finditer(r"^\s*#+\s*\d+\s*\)\s*(.*)", readme_content, re.M|re.I):
        name = m.group(1).strip(); name = re.sub(r'\[.*?\].*$', '', name).strip(); name = re.sub(r'[:–-].*$', '', name).strip()
        if 2 < len(name) < 50 and re.match(r'^[a-zA-Z0-9\s_/().-]+$', name) and name.lower() not in ['usage','compilation','instructions','features','acknowledgement','acknowledgments','example','introduction','overview','note','notes','why are you doing this','did you write this from the ground up','note on quality','can i/we reach you','can i/we help you','requirements','setup']: found_bofs.add(name.strip('.'))
    # 6: Table first column
    header_pattern = re.compile(r"Commands?|Project|Name", re.I); separator_pattern = re.compile(r"^\s*\|?\s*--+.*")
    for line in readme_content.splitlines():
        if separator_pattern.match(line): continue
        m = re.match(r"^\s*\|\s*([^|]+?)\s*\|", line)
        if m:
            name = m.group(1).strip(); name = re.sub(r'\[([^\]]+)\]\(.*?\)', r'\1', name).strip(); name = name.replace('`', '').replace('*', '').strip()
            if name and 2 < len(name) < 50 and not header_pattern.search(name) and name.lower() not in ['bof','c','o','cs','cpp','dll','exe','aggressor','usage','example','note','output','input','cmd','ps']: found_bofs.add(name.strip('.'))
    # 7: Sub-projects/Dirs (README links)
    for m in re.finditer(r"\[[^\]]+\]\(((?!https?://)[^)]*?)/README\.md\)", readme_content):
        dir_name = m.group(1).strip();
        if dir_name and '/' not in dir_name and 2 < len(dir_name) < 30: found_bofs.add(dir_name)
    # 7b: Sub-projects/Dirs (H2 Headings)
    for m in re.finditer(r"^\s*##\s+([a-zA-Z0-9_-]+)", readme_content, re.M):
         h_name = m.group(1).strip();
         if 2 < len(h_name) < 30 and h_name.lower() not in ['usage','compilation','features','references','notes','acknowledgement','acknowledgments','installation','setup','examples','commands','modules']: found_bofs.add(h_name)
    # Final Filtering
    bof_list = sorted(list(found_bofs), key=str.lower);
    common_words_to_filter = {'the','and','for','with','using','via','from','this','that','bof','file','object','beacon','cobalt','strike','command','output','input','example','description','parameter','argument','arguments','function','feature','module','script','tool','utility','windows','linux','api','net','system','process','thread','memory','injection','payload','bypass','lateral','movement','privilege','escalation','collection','various','general','purpose','command','control','active','directory','kerberos','number','string','value','path','name','project','usage','notes','note','references','commands'};
    bof_list = [b for b in bof_list if b.lower() not in common_words_to_filter and len(b.split()) < 5 and not re.match(r'^\d+$', b) and not (b.startswith('.') or b.endswith('.')) and len(b) > 2]
    return bof_list

# --- Main Execution ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract potential BOF names from READMEs linked in a Markdown file.")
    parser.add_argument("markdown_file", help="Path to the input Markdown file containing the table of repositories.")
    args = parser.parse_args()

    if not os.path.exists(args.markdown_file): print(f"[!] Error: Input file not found: {args.markdown_file}", file=sys.stderr); exit(1)

    print(f"[*] Reading input file: {args.markdown_file}")
    try:
        with open(args.markdown_file, 'r', encoding='utf-8') as f: markdown_content = f.read()
    except Exception as e: print(f"[!] Error reading file: {e}", file=sys.stderr); exit(1)

    repo_urls = extract_repo_urls(markdown_content)
    print(f"[*] Found {len(repo_urls)} unique repository URLs in the table.")

    results = {}
    print("[*] Processing repositories...")
    for i, url in enumerate(repo_urls, 1):
        user, repo, base_url = get_repo_base_info(url)
        if not user: print(f"[-] Skipping invalid URL: {url}"); results[url] = []; continue
        readme_content, found_branch = fetch_readme_content(url)
        if readme_content and found_branch: results[url] = extract_potential_bofs(readme_content, url, user, repo, found_branch)
        else: results[url] = []
        if i < len(repo_urls): time.sleep(REQUEST_DELAY_SECONDS)
    print("[*] Finished processing repositories.")

    # --- Optional: Print final results dictionary for debugging ---
    # print("\nDEBUG: Final Results Dictionary:", file=sys.stderr)
    # import json
    # print(json.dumps(results, indent=2), file=sys.stderr)
    # print("-" * 60, file=sys.stderr) # Separator for debug output

    print("\n" + "=" * 60)
    print("          FINAL RESULTS SUMMARY - UPDATED MARKDOWN SNIPPET")
    print("=" * 60)
    print("[*] (Review and manually integrate into your main README file)\n")

    original_lines = markdown_content.splitlines()
    header_printed = False
    separator_printed = False
    header_pattern_check = re.compile(r"^\s*\|\s*Project\s*\|", re.IGNORECASE)
    separator_pattern_check = re.compile(r"^\s*\|\s*-+.*")

    # --- FINAL OUTPUT LOOP - REVISED REGEX ---
    for line_num, line in enumerate(original_lines, 1):
        line_stripped = line.strip()
        # print(f"DEBUG Line {line_num}: Processing: '{line_stripped}'", file=sys.stderr) # Optional debug

        if not line_stripped: print(line); continue

        # Handle Header
        if not header_printed and header_pattern_check.match(line):
            print(f"| Project | Description | Includes | Stars | Last commit |")
            header_printed = True; continue

        # Handle Separator
        if not separator_printed and separator_pattern_check.match(line):
            print(f"|---------|-------------|----------|-------|-------------|")
            separator_printed = True; continue

        # Process potential data rows
        if line_stripped.startswith('|') and line_stripped.endswith('|'):
            # Try to extract URL from this line
            match_url = re.search(r"\(https?://github\.com/([^/]+/[^)]+?)\)", line)
            current_line_url_full = None
            if match_url:
                url_path = match_url.group(1).strip('/')
                current_line_url_full = f"https://github.com/{url_path}"

            if current_line_url_full:
                bofs_str = ""
                if current_line_url_full in results:
                    bofs = results[current_line_url_full]
                    bofs_str = ", ".join(f"`{b}`" for b in bofs) if bofs else ""

                # --- USE NEW REGEX TO CAPTURE ALL 5 CELLS ---
                # Regex: | cell1 | cell2 | cell3 | cell4 | cell5 |
                #        (Proj)  (Desc) (Empty) (Stars) (Commit)
                row_match = re.match(r"^\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*$", line_stripped)

                if row_match:
                    proj_cell   = row_match.group(1).strip()
                    desc_cell   = row_match.group(2).strip()
                    # empty_cell  = row_match.group(3).strip() # We don't need this one
                    stars_cell  = row_match.group(4).strip()
                    commit_cell = row_match.group(5).strip()

                    # Print the reconstructed line inserting bofs_str correctly
                    print(f"| {proj_cell} | {desc_cell} | {bofs_str} | {stars_cell} | {commit_cell} |")
                    continue # Successfully processed this row

                else:
                    # Fallback if the NEW regex fails (should be less likely now)
                    print(f"DEBUG Line {line_num}: Row regex FAILED.", file=sys.stderr)
                    print(line + f" <!-- Regex Failed. Includes: {bofs_str} -->")
                    continue
            else:
                 # Looked like data row but no URL extracted
                 print(line)
                 continue

        # Print non-table lines as is
        print(line)


    print("\n" + "=" * 60)
    print("[*] Processing Complete.")
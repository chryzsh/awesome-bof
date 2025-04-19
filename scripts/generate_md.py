#!/usr/bin/env python3

import requests
import argparse
import sys
from urllib.parse import urlparse

def get_repo_info(repo_url):
    """
    Fetches repository description using the GitHub API.
    Returns username, repo_name, description or None on error.
    """
    parsed_url = urlparse(repo_url)
    if parsed_url.netloc.lower() != 'github.com':
        print(f"Error: URL '{repo_url}' is not a valid GitHub repository URL.", file=sys.stderr)
        return None, None, None

    path_parts = parsed_url.path.strip('/').split('/')
    if len(path_parts) < 2:
        print(f"Error: Could not parse username/repository from URL path '{parsed_url.path}'.", file=sys.stderr)
        return None, None, None

    username = path_parts[0]
    repo_name = path_parts[1]
    api_url = f"https://api.github.com/repos/{username}/{repo_name}"

    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        data = response.json()
        description = data.get("description") # Use .get() to handle missing key safely
        if description is None:
            description = "[No description provided]" # Provide a placeholder
        elif not description.strip(): # Handle empty string description
             description = "[Description is empty]"

        return username, repo_name, description

    except requests.exceptions.Timeout:
        print(f"Error: Request timed out while fetching data for {repo_url}.", file=sys.stderr)
        return None, None, None
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            print(f"Error: Repository not found at {repo_url} (404).", file=sys.stderr)
        elif response.status_code == 403:
             print(f"Error: API rate limit likely exceeded or forbidden access (403).", file=sys.stderr)
        else:
            print(f"Error: HTTP error fetching data for {repo_url}: {e}", file=sys.stderr)
        return None, None, None
    except requests.exceptions.RequestException as e:
        print(f"Error: Could not connect or fetch data for {repo_url}: {e}", file=sys.stderr)
        return None, None, None
    except Exception as e: # Catch potential JSON decoding errors or others
        print(f"Error: An unexpected error occurred: {e}", file=sys.stderr)
        return None, None, None


def format_markdown_row(url, username, repo_name, description):
    """Formats the data into the desired Markdown table row."""
    stars_badge = f"![](https://img.shields.io/github/stars/{username}/{repo_name}?label=&style=flat)"
    commit_badge = f"![](https://img.shields.io/github/last-commit/{username}/{repo_name}?label=&style=flat)"

    # Ensure the original URL is used in the link
    markdown_link = f"[{repo_name}]({url})"

    # Escape pipe characters within the description if necessary (optional, but good practice)
    safe_description = description.replace('|', '\\|')

    return f"| {markdown_link} | {safe_description} | {stars_badge} | {commit_badge} |"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a Markdown table row for a GitHub repository.")
    parser.add_argument("repo_url", help="The full URL of the GitHub repository (e.g., https://github.com/user/repo)")
    args = parser.parse_args()

    repo_url = args.repo_url
    username, repo_name, description = get_repo_info(repo_url)

    if username and repo_name: # Check if we got valid data back
        markdown_row = format_markdown_row(repo_url, username, repo_name, description)
        print(markdown_row)
    else:
        # Error message was already printed to stderr by get_repo_info
        sys.exit(1) # Exit with a non-zero status to indicate failure
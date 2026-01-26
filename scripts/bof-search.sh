#!/usr/bin/env bash
#
# bof-search.sh - Interactive BOF search using fzf
#
# Usage: ./scripts/bof-search.sh [query]
#
# Requirements: jq, fzf
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INDEX_FILE="${SCRIPT_DIR}/../bof-index.json"

# Check dependencies
for cmd in jq fzf; do
    if ! command -v "$cmd" &> /dev/null; then
        echo "Error: $cmd is required but not installed." >&2
        exit 1
    fi
done

# Check index file exists
if [[ ! -f "$INDEX_FILE" ]]; then
    echo "Error: BOF index not found at $INDEX_FILE" >&2
    echo "Run: python3 scripts/bof_indexer.py" >&2
    exit 1
fi

# Build searchable list: "name | description | repository"
# Use tab as delimiter for fzf column handling
build_list() {
    jq -r '.bofs[] | "\(.name)\t\(.description)\t\(.repository)"' "$INDEX_FILE"
}

# Format selected entry for display
show_details() {
    local name="$1"
    local repo="$2"
    
    jq -r --arg name "$name" --arg repo "$repo" '
        .bofs[] | select(.name == $name and .repository == $repo) |
        "Name:        \(.name)",
        "Description: \(.description)",
        "Repository:  \(.repository)",
        "Source:      \(.source_file) (\(.source_format))"
    ' "$INDEX_FILE"
}

# Main search interface
main() {
    local initial_query="${1:-}"
    
    local selected
    selected=$(build_list | fzf \
        --delimiter='\t' \
        --with-nth=1,2 \
        --query="$initial_query" \
        --preview="echo {1} && echo {2} && echo {3}" \
        --preview-window=up:3:wrap \
        --header="Search BOFs ($(jq '.bofs | length' "$INDEX_FILE") indexed)" \
        --bind='ctrl-o:execute-silent(open {3})' \
        --bind='ctrl-y:execute-silent(echo -n {3} | pbcopy)' \
        --header-first \
        --info=inline \
        --layout=reverse \
        --height=80% \
        --border \
        --prompt="BOF> " \
    ) || exit 0
    
    # Parse selection
    local name repo
    name=$(echo "$selected" | cut -f1)
    repo=$(echo "$selected" | cut -f3)
    
    echo
    show_details "$name" "$repo"
    echo
    echo "Press Enter to open repository, or Ctrl-C to exit"
    read -r
    open "$repo"
}

main "$@"

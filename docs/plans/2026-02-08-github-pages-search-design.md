# GitHub Pages BOF Search Design

Date: 2026-02-08
Status: Draft approved in chat

## Goal
Create a public GitHub Pages web UI for BOF discovery that is terminal-inspired but web-native, optimized for quickly finding BOFs and opening the original repository.

## Scope Decisions
- Use a hybrid terminal-style web UI (not a literal terminal emulator).
- Use client-side search over static `bof-index.json`.
- Host in this same repository.
- Keep `docs/` for documentation only.
- Place web app in top-level `site/`.
- `Enter` opens selected repo directly.
- Open repo in a new browser tab.

## Proposed Structure
- `site/index.html`
- `site/styles.css`
- `site/app.js`
- `site/vendor/fuse.min.js` (or equivalent local fuzzy-search dependency)
- `site/data/bof-index.json` (copy of root `bof-index.json` for Pages runtime)

## Architecture
Static single-page app on GitHub Pages:
- Browser fetches `site/data/bof-index.json`.
- JavaScript normalizes entries and builds fuzzy search index.
- UI maintains state: `query`, `filteredResults`, `selectedIndex`.
- Optional URL query sync: `?q=<term>`.

No backend and no required build step for v1.

## UX Requirements
Primary workflow: type query -> navigate if needed -> press `Enter` -> open repo.

Layout:
- Left pane: searchable result list.
- Right pane: details for selected BOF.

Result row content:
- Name (primary)
- Description (secondary)
- Repository slug (`owner/repo`) (tertiary)

Details pane content:
- Full name
- Full description
- Repository URL
- Source metadata (`source_file`, `source_format`)
- Actions: `Open GitHub Repo`, `Copy Repo URL`

## Keyboard and Interaction
- `↑/↓` and `j/k`: move selection
- `Enter`: open selected repo in new tab
- `o`: open selected repo in new tab
- `/`: focus search input
- `Esc`: clear query or blur input
- Click row: select row
- Double-click row: open repo in new tab

## Search Behavior
- Fuzzy search across `name`, `description`, and repo text.
- Weighted ranking: name > description > repo.
- Inline highlighting of matched segments.
- Show result count.

## States and Error Handling
- Loading state while index fetches.
- Empty state for no matches.
- Error state with retry if index fetch fails.

## Accessibility and Responsiveness
- Visible focus states.
- ARIA labels for search, results, and actions.
- Keyboard-first support without breaking mouse use.
- Responsive layout for desktop and mobile.

## Content/Data Update Flow
Current index generation remains source of truth:
1. `python3 scripts/bof_indexer.py`
2. Copy `bof-index.json` -> `site/data/bof-index.json`

Optional helper script:
- `scripts/update-site-data.sh` to automate copy/sync.

## Deployment
GitHub Pages configuration:
- Branch: `main`
- Folder: `/site`

This preserves `docs/` as documentation-only.

## Acceptance Criteria
- Users can search BOFs with sub-second feedback.
- Users can open selected repository with one key (`Enter`) in a new tab.
- Users can copy repository URL from details pane.
- Site functions as static Pages app with no backend.
- Data can be refreshed from existing indexing workflow.

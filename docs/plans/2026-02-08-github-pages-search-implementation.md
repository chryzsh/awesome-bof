# GitHub Pages BOF Search UI Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a static GitHub Pages web UI in `site/` for fast BOF discovery with keyboard-first search and one-key open-to-repo in a new tab.

**Architecture:** A no-backend single-page app loads `site/data/bof-index.json`, builds a client-side fuzzy index (Fuse.js), and renders a split-pane interface (results + details). All behavior runs in browser state (`query`, `selectedIndex`, `filteredResults`) with keyboard navigation and action shortcuts. Data refresh reuses existing `scripts/bof_indexer.py` output by syncing root `bof-index.json` into `site/data/`.

**Tech Stack:** Static HTML/CSS/JavaScript, Fuse.js (vendored local asset), GitHub Pages (`main` + `/site`).

---

## Deviation Log

### D1: Search engine implementation changed from Fuse.js to custom weighted search

- **Planned:** Vendored `site/vendor/fuse.min.js` and `new Fuse(...)` integration.
- **Implemented:** Native JavaScript weighted search in `site/app.js` (`scoreEntry` + `applyFilter`), no external dependency.
- **Reason:** Keep v1 dependency-free and fully static while preserving required behavior (fast client-side filtering and ranking by name > description > repository).
- **Impact:** No user-facing feature loss for current scope; lower maintenance and no third-party asset management.
- **Approved by:** User selected plan-audit option to document deviation before go-live (2026-02-08).

---

### Task 1: Scaffold static site shell

**Files:**
- Create: `site/index.html`
- Create: `site/styles.css`
- Create: `site/app.js`
- Create: `site/vendor/` (directory)
- Create: `site/data/` (directory)

**Step 1: Write the failing test (manual smoke check definition)**

```text
Expected behavior:
- Opening site/index.html should render app frame with search input, list pane, and details pane.
- Without JS data loaded, app should show explicit loading state.
```

**Step 2: Run test to verify it fails**

Run: `ls site/index.html site/styles.css site/app.js`
Expected: missing file errors.

**Step 3: Write minimal implementation**

```html
<!-- site/index.html -->
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>awesome-bof search</title>
    <link rel="stylesheet" href="./styles.css" />
  </head>
  <body>
    <main id="app" aria-busy="true">
      <header class="topbar">
        <input id="search" type="search" placeholder="Search BOFs..." aria-label="Search BOFs" />
        <span id="result-count">Loading...</span>
      </header>
      <section class="layout">
        <ul id="results" aria-label="Search results"></ul>
        <article id="details" aria-live="polite">Select a BOF to view details.</article>
      </section>
      <p id="status" role="status">Loading index...</p>
    </main>
    <script src="./app.js" defer></script>
  </body>
</html>
```

**Step 4: Run test to verify it passes**

Run: `rg -n "id=\"search\"|id=\"results\"|id=\"details\"" site/index.html`
Expected: all selectors present.

**Step 5: Commit**

```bash
git add site/index.html site/styles.css site/app.js
git commit -m "feat(site): scaffold static github pages app shell"
```

### Task 2: Add visual system and responsive split-pane layout

**Files:**
- Modify: `site/styles.css`

**Step 1: Write the failing test (manual visual check definition)**

```text
Expected behavior:
- Desktop: two-column layout with bordered panels.
- Mobile: stacked layout.
- Visible keyboard focus on interactive controls.
```

**Step 2: Run test to verify it fails**

Run: `rg -n "layout|:focus-visible|@media" site/styles.css`
Expected: no matches (or incomplete).

**Step 3: Write minimal implementation**

```css
:root {
  --bg: #0f1419;
  --panel: #151b22;
  --text: #e7edf3;
  --muted: #9aa6b2;
  --accent: #4cc38a;
  --border: #2a3441;
}
body { margin: 0; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; background: radial-gradient(circle at top, #1a2330, var(--bg)); color: var(--text); }
.topbar { display: flex; gap: 0.75rem; padding: 0.75rem; border-bottom: 1px solid var(--border); }
.layout { display: grid; grid-template-columns: 1.2fr 1fr; min-height: calc(100vh - 56px); }
#results, #details { margin: 0; padding: 0.75rem; border-right: 1px solid var(--border); overflow: auto; }
#details { border-right: 0; }
:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
@media (max-width: 900px) { .layout { grid-template-columns: 1fr; } #results { border-right: 0; border-bottom: 1px solid var(--border); } }
```

**Step 4: Run test to verify it passes**

Run: `rg -n "grid-template-columns|focus-visible|@media \(max-width: 900px\)" site/styles.css`
Expected: all rules found.

**Step 5: Commit**

```bash
git add site/styles.css
git commit -m "feat(site): add terminal-inspired responsive layout styles"
```

### Task 3: Add data loading and error/empty/loading states

**Files:**
- Modify: `site/app.js`
- Modify: `site/index.html`

**Step 1: Write the failing test**

```text
Expected behavior:
- App fetches ./data/bof-index.json.
- While loading, status shows loading text.
- On fetch error, status shows retry hint.
- If no results, list shows explicit empty message.
```

**Step 2: Run test to verify it fails**

Run: `rg -n "fetch\(|Loading index|Retry" site/app.js site/index.html`
Expected: missing or partial matches.

**Step 3: Write minimal implementation**

```js
const state = { entries: [], filtered: [], selectedIndex: 0, query: "" };

async function loadIndex() {
  const status = document.getElementById("status");
  status.textContent = "Loading index...";
  try {
    const res = await fetch("./data/bof-index.json", { cache: "no-store" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    state.entries = Array.isArray(data.bofs) ? data.bofs : [];
    state.filtered = state.entries;
    render();
    status.textContent = "";
  } catch (err) {
    status.textContent = "Failed to load BOF index. Refresh to retry.";
  }
}
```

**Step 4: Run test to verify it passes**

Run: `rg -n "fetch\(" site/app.js && rg -n "Failed to load BOF index" site/app.js`
Expected: matches exist.

**Step 5: Commit**

```bash
git add site/app.js site/index.html
git commit -m "feat(site): implement index loading and base app states"
```

### Task 4: Add fuzzy search engine integration

**Files:**
- Modify: `site/app.js`

**Step 1: Write the failing test**

```text
Expected behavior:
- Typing query filters results by name, description, repo.
- Name matches rank above description/repo matches.
```

**Step 2: Run test to verify it fails**

Run: `rg -n "Fuse|fuse" site/index.html site/app.js`
Expected: no matches.

**Step 3: Write minimal implementation**

```js
function scoreEntry(entry, terms) {
  let score = 0;
  const n = entry.name.toLowerCase();
  const d = entry.description.toLowerCase();
  const r = entry.repository.toLowerCase();

  for (const term of terms) {
    if (!term) continue;
    if (n.startsWith(term)) score += 120;
    else if (n.includes(term)) score += 80;
    if (d.includes(term)) score += 28;
    if (r.includes(term)) score += 16;
  }

  return score;
}

function applyFilter(query) {
  const terms = query.trim().toLowerCase().split(/\s+/).filter(Boolean);
  const matches = state.entries
    .map((entry) => ({ entry, score: scoreEntry(entry, terms) }))
    .filter((m) => m.score > 0)
    .sort((a, b) => b.score - a.score || a.entry.name.localeCompare(b.entry.name));
  state.filtered = query.trim() ? matches.map((m) => m.entry) : state.entries;
  state.selectedIndex = 0;
  render();
}
```

**Step 4: Run test to verify it passes**

Run: `rg -n "scoreEntry|applyFilter|startsWith|includes" site/app.js`
Expected: weighted search implementation present.

**Step 5: Commit**

```bash
git add site/app.js
git commit -m "feat(site): add client-side weighted search with no external dependency"
```

### Task 5: Implement results rendering, details panel, and action buttons

**Files:**
- Modify: `site/app.js`
- Modify: `site/index.html`
- Modify: `site/styles.css`

**Step 1: Write the failing test**

```text
Expected behavior:
- Result rows show name, short description, repo slug.
- Selected row updates details panel.
- Details panel has Open Repo and Copy URL buttons.
```

**Step 2: Run test to verify it fails**

Run: `rg -n "Open GitHub Repo|Copy Repo URL|repository" site/index.html site/app.js`
Expected: missing or incomplete wiring.

**Step 3: Write minimal implementation**

```js
function render() {
  const results = document.getElementById("results");
  const details = document.getElementById("details");
  const count = document.getElementById("result-count");
  count.textContent = `${state.filtered.length} results`;

  if (!state.filtered.length) {
    results.innerHTML = '<li class="empty">No matches for query.</li>';
    details.textContent = "No BOF selected.";
    return;
  }

  const selected = state.filtered[state.selectedIndex] ?? state.filtered[0];
  results.innerHTML = state.filtered.map((item, idx) => `
    <li class="row ${idx === state.selectedIndex ? "selected" : ""}" data-index="${idx}" tabindex="0">
      <div class="name">${escapeHtml(item.name || "(unnamed)")}</div>
      <div class="desc">${escapeHtml(item.description || "")}</div>
      <div class="repo">${escapeHtml(repoSlug(item.repository || ""))}</div>
    </li>
  `).join("");

  details.innerHTML = `
    <h2>${escapeHtml(selected.name || "(unnamed)")}</h2>
    <p>${escapeHtml(selected.description || "")}</p>
    <p><a href="${escapeAttr(selected.repository)}" target="_blank" rel="noopener">${escapeHtml(selected.repository || "")}</a></p>
    <p>Source: ${escapeHtml(selected.source_file || "") } (${escapeHtml(selected.source_format || "")})</p>
    <div class="actions">
      <button id="open-repo">Open GitHub Repo</button>
      <button id="copy-repo">Copy Repo URL</button>
    </div>
  `;
}
```

**Step 4: Run test to verify it passes**

Run: `rg -n "Open GitHub Repo|Copy Repo URL|result-count" site/app.js site/index.html`
Expected: all UI action strings and counter wiring exist.

**Step 5: Commit**

```bash
git add site/app.js site/index.html site/styles.css
git commit -m "feat(site): render results/details with open and copy actions"
```

### Task 6: Implement keyboard and mouse interaction model

**Files:**
- Modify: `site/app.js`

**Step 1: Write the failing test**

```text
Expected behavior:
- j/k and arrows move selection.
- Enter and o open selected repo in new tab.
- / focuses search; Esc clears query.
- click selects; double-click opens.
```

**Step 2: Run test to verify it fails**

Run: `rg -n "keydown|Enter|ArrowDown|ArrowUp|window.open|dblclick" site/app.js`
Expected: missing key handlers.

**Step 3: Write minimal implementation**

```js
document.addEventListener("keydown", (e) => {
  const search = document.getElementById("search");
  if (e.key === "/") { e.preventDefault(); search.focus(); return; }
  if (e.key === "Escape") { search.value = ""; applyFilter(""); return; }
  if (e.key === "j" || e.key === "ArrowDown") { e.preventDefault(); moveSelection(1); return; }
  if (e.key === "k" || e.key === "ArrowUp") { e.preventDefault(); moveSelection(-1); return; }
  if (e.key === "Enter" || e.key.toLowerCase() === "o") { e.preventDefault(); openSelected(); }
});

function openSelected() {
  const item = state.filtered[state.selectedIndex];
  if (item?.repository) window.open(item.repository, "_blank", "noopener");
}
```

**Step 4: Run test to verify it passes**

Run: `rg -n "window.open\(|keydown|moveSelection\(" site/app.js`
Expected: handlers and open logic present.

**Step 5: Commit**

```bash
git add site/app.js
git commit -m "feat(site): add keyboard-first navigation and open shortcuts"
```

### Task 7: Add URL query sync and clipboard support

**Files:**
- Modify: `site/app.js`

**Step 1: Write the failing test**

```text
Expected behavior:
- Visiting ?q=kerberos preloads search query.
- Copy Repo URL button writes selected URL to clipboard.
```

**Step 2: Run test to verify it fails**

Run: `rg -n "URLSearchParams|clipboard" site/app.js`
Expected: no matches.

**Step 3: Write minimal implementation**

```js
function readInitialQuery() {
  const params = new URLSearchParams(window.location.search);
  return params.get("q") || "";
}

function writeQueryToUrl(query) {
  const url = new URL(window.location.href);
  if (query) url.searchParams.set("q", query);
  else url.searchParams.delete("q");
  window.history.replaceState({}, "", url);
}

async function copySelectedRepo() {
  const item = state.filtered[state.selectedIndex];
  if (!item?.repository) return;
  await navigator.clipboard.writeText(item.repository);
}
```

**Step 4: Run test to verify it passes**

Run: `rg -n "URLSearchParams|navigator\.clipboard\.writeText" site/app.js`
Expected: both present.

**Step 5: Commit**

```bash
git add site/app.js
git commit -m "feat(site): add query deep-linking and clipboard copy action"
```

### Task 8: Add data sync helper and documentation

**Files:**
- Create: `scripts/update-site-data.sh`
- Modify: `README.md`
- Modify: `docs/bof-search.md`

**Step 1: Write the failing test**

```text
Expected behavior:
- One command syncs root index to site data path.
- README/docs explain local preview and pages publishing source.
```

**Step 2: Run test to verify it fails**

Run: `ls scripts/update-site-data.sh && rg -n "site/|GitHub Pages|update-site-data" README.md docs/bof-search.md`
Expected: helper script missing, docs incomplete.

**Step 3: Write minimal implementation**

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cp "${ROOT_DIR}/bof-index.json" "${ROOT_DIR}/site/data/bof-index.json"
echo "Synced bof-index.json -> site/data/bof-index.json"
```

Document:
- generate index: `python3 scripts/bof_indexer.py`
- sync index: `bash scripts/update-site-data.sh`
- publish source: Pages from `main` + `/site`

**Step 4: Run test to verify it passes**

Run: `bash scripts/update-site-data.sh && test -f site/data/bof-index.json && echo OK`
Expected: sync message then `OK`.

**Step 5: Commit**

```bash
git add scripts/update-site-data.sh README.md docs/bof-search.md site/data/bof-index.json
git commit -m "docs(site): add data sync workflow and pages publishing docs"
```

### Task 9: Verification pass before completion

**Files:**
- Verify: `site/index.html`
- Verify: `site/styles.css`
- Verify: `site/app.js`
- Verify: `site/data/bof-index.json`

**Step 1: Write the failing test (verification checklist)**

```text
Checklist:
- Search filters results quickly.
- Enter opens selected repo in new tab.
- Copy button copies URL.
- Empty and error states are visible when triggered.
- Mobile layout is usable.
```

**Step 2: Run test to verify it fails (if unverified)**

Run: `python3 -m http.server 8000`
Then visit `http://localhost:8000/site/` and execute checklist.
Expected: identify any remaining defects.

**Step 3: Write minimal implementation**

Fix any defects found during manual verification in relevant files.

**Step 4: Run test to verify it passes**

Run: `python3 -m http.server 8000`
Expected: all checklist items pass.

**Step 5: Commit**

```bash
git add site/index.html site/styles.css site/app.js
# include any files changed during bugfix pass
git commit -m "fix(site): resolve final qa findings for pages search ui"
```

## Notes
- Preferred execution environment: dedicated git worktree before implementation.
- Keep implementation DRY/YAGNI: no framework build pipeline for v1.
- If dataset performance regresses later, add precomputed search index as follow-up, not in v1.

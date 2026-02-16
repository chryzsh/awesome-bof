# BOF Catalog Maintenance Instructions

Instructions for an LLM to discover and add new BOFs to the catalog.

## Task: Weekly Issue Triage (primary workflow)

A GitHub Actions workflow runs weekly and creates an issue titled "Weekly BOF discovery report" with candidate repos. This is the main way new BOFs get added.

### Step 1: Check the Latest Open Issues

```bash
gh issue list --limit 2 --state open --json number,title,author,body,url,createdAt
```

Look for issues titled "Weekly BOF discovery report" created by `app/github-actions`.

### Step 2: Evaluate Candidates

For each candidate in the issue, check whether it's a real BOF worth adding:

```bash
gh api repos/OWNER/REPO --jq '{description,stargazers_count,language,topics,created_at,pushed_at}'
gh api repos/OWNER/REPO/readme --jq '.content' | base64 -d | head -80
```

**Include** repos that are:
- Actual Beacon Object Files (C source with beacon.h, .cna aggressor scripts, etc.)
- For any C2 framework (Cobalt Strike, Sliver, Havoc, Adaptix, etc.)
- Have real source code and a reasonable README
- Low-star repos are fine if the BOF is functional and focused

**Exclude** repos that are:
- Not BOFs (false positives like "Bank of America", game mods, buffer overflow labs)
- Download-focused repos pushing pre-built binaries without proper build-from-source workflow
- Forks/copies of existing BOFs with no meaningful changes
- Empty, no description, or clearly abandoned learning repos
- Generic tool collections, cheatsheets, or pentest dumps that aren't BOF-specific
- Already in the catalog (grep BOF-CATALOG.md first)

### Step 3: Add to BOF-CATALOG.md

Place each BOF in the correct section:

| Section | Criteria |
|---------|----------|
| `## 🧰 BOF Collections` | Multi-BOF suites/toolkits (5+ BOFs) |
| `## 🤏 Smaller BOF Packs` | 2-5 related BOFs bundled together |
| `## C2 specific BOFs` | BOFs written for a non-Cobalt Strike C2 (Adaptix, Havoc, Sliver, etc.) |
| `## 🧩 Other BOFs` | Individual/single-purpose BOFs (default category) |

Use this table row format:
```
| [RepoName](https://github.com/owner/repo) | Short description of what it does | ![](https://img.shields.io/github/stars/owner/repo?label=&style=flat) | ![](https://img.shields.io/github/last-commit/owner/repo?label=&style=flat) |
```

Or use the helper: `python3 scripts/generate_md.py https://github.com/owner/repo`

### Step 4: Rebuild Search Index and Sync

```bash
python3 scripts/bof_indexer.py
bash scripts/update-site-data.sh
```

### Step 5: Commit and Push

Stage all three files, commit, and push:
```bash
git add BOF-CATALOG.md bof-index.json site/data/bof-index.json
git commit -m "feat(catalog): add N BOFs from weekly discovery issues #X and #Y"
git push
```

If push is rejected (remote has new commits), pull with rebase first:
```bash
git pull --rebase && git push
```

### Step 6: Close the Processed Issues

After pushing, close the issues that were triaged:
```bash
gh issue close NUMBER --comment "Triaged: added N repos, skipped M (reason summary)"
```

---

## Task: Discover and Add New BOFs (manual)

Use this when you want to search beyond the weekly automated issues.

### Step 1: Run Discovery Script

```bash
python3 scripts/find_new_bofs.py --days 30
```

Or for a specific date range:
```bash
python3 scripts/find_new_bofs.py --since 2025-01-01
```

The script will:
- Search GitHub for C repos with "bof" keyword
- Filter out repos already in BOF-CATALOG.md
- Output candidates with stars, description, and URL

### Step 2: Filter Candidates

**Include** repos that are:
- Actual Beacon Object Files (for Cobalt Strike, Sliver, Havoc, etc.)
- Have meaningful descriptions
- Preferably 10+ stars (but interesting low-star BOFs are fine)

**Exclude** repos that are:
- Not BOFs (e.g., "Breath of Fire" game mods, buffer overflow labs)
- Forks with no meaningful changes
- Empty or abandoned (no commits in 2+ years, 0 stars, no description)
- Duplicates of existing entries

### Step 3: Categorize

Place BOFs in the correct section of BOF-CATALOG.md:

| Section | Criteria |
|---------|----------|
| `## 🧰 BOF Collections` | Multi-BOF suites/toolkits |
| `## 🤏 Smaller BOF Packs` | 2-5 related BOFs |
| `## C2 specific BOFs` | BOFs for specific C2 (Adaptix, Havoc-only, etc.) |
| `## 🧩 Other BOFs` | Individual BOFs, single-purpose tools |

### Step 4: Generate Markdown Rows

Use the helper script:
```bash
python3 scripts/generate_md.py https://github.com/owner/repo
```

This outputs a properly formatted table row with stars and commit badges.

### Step 5: Add to Catalog

Edit BOF-CATALOG.md and add the row to the appropriate section's table.

### Step 6: Commit

```bash
git add BOF-CATALOG.md
git commit -m "Add [repo-name] to BOF catalog

[Brief description of what the BOF does]

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

### Step 7: Rebuild the BOF Index

After adding new entries to the catalog, regenerate the search index so the new BOFs are searchable:

```bash
python3 scripts/bof_indexer.py
```

This will:
1. Parse `BOF-CATALOG.md` for all repository URLs
2. Shallow-clone each repo (or reuse existing clones in `repos/`)
3. Extract BOF command names and descriptions from READMEs, `.cna` files, Havoc Python, Stage1 Python, and directory structures
4. Write the updated `bof-index.json`

Note: This clones all repos and takes several minutes. Use `--skip-clone` to reuse existing clones.

Commit the updated index:
```bash
git add bof-index.json
git commit -m "Update BOF index"
```

### Step 8: Refresh Web Search Data (GitHub Pages)

After rebuilding `bof-index.json`, sync the web UI copy so the public site uses the latest index:

```bash
bash scripts/update-site-data.sh
```

Commit the synced web index:

```bash
git add site/data/bof-index.json
git commit -m "Sync web BOF index data"
```

GitHub Pages is configured for:
- Branch: `main`
- Folder: `/`

Public web UI path:
- `https://chryzsh.github.io/awesome-bof/site/`

## BOF Search

An interactive search tool lets you fuzzy-search across all indexed BOF commands:

```bash
./scripts/bof-search.sh            # Interactive search
./scripts/bof-search.sh kerberos   # Search with initial query
```

Requires `jq` and `fzf`. See [docs/bof-search.md](docs/bof-search.md) for full usage.

## Repository Structure

```
awesome-bof/
├── BOF-CATALOG.md         # Main catalog - add BOFs here
├── bof-index.json         # Generated search index (from bof_indexer.py)
├── README.md              # Simple README linking to catalog
├── LICENSE
├── docs/
│   └── bof-search.md      # BOF search documentation
├── scripts/
│   ├── find_new_bofs.py   # Discovery script (GitHub search)
│   ├── bof_indexer.py     # BOF index generator (clones + parses repos)
│   ├── bof-search.sh      # Interactive fzf search over the index
│   ├── generate_md.py     # Generate table rows for catalog
│   └── find-dupes.py      # Find duplicate entries
└── _archive/              # Archived old documentation
```

## Notes

- Set `GITHUB_TOKEN` env var for higher API rate limits
- The catalog has 367+ BOFs - always check for duplicates
- When in doubt, ask the human for approval before adding
- After adding BOFs, rebuild the index so they appear in search

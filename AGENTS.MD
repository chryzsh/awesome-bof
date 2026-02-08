# BOF Catalog Maintenance Instructions

Instructions for an LLM to discover and add new BOFs to the catalog.

## Task: Discover and Add New BOFs

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

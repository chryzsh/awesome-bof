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

## Repository Structure

```
awesome-bof/
├── BOF-CATALOG.md      # Main catalog - add BOFs here
├── README.md           # Simple README linking to catalog
├── LICENSE
├── scripts/
│   ├── find_new_bofs.py   # Discovery script
│   ├── generate_md.py     # Generate table rows
│   └── find-dupes.py      # Find duplicate entries
└── _archive/              # Archived old documentation
```

## Notes

- Set `GITHUB_TOKEN` env var for higher API rate limits
- The catalog has 367+ BOFs - always check for duplicates
- When in doubt, ask the human for approval before adding

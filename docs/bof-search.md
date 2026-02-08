# BOF Search

Search across 1200+ BOF commands from the catalog using fuzzy search.

## Web UI (GitHub Pages)

A public, static web UI is available in `site/` with keyboard-first navigation.

### Quick Start (local)

```bash
bash scripts/update-site-data.sh
python3 -m http.server 8000
```

Open `http://localhost:8000/site/`.

### Keyboard shortcuts (web)

| Key | Action |
|-----|--------|
| `/` | Focus search |
| `j` / `k` | Move selection down/up |
| `↑` / `↓` | Move selection down/up |
| `Enter` | Open selected repository in new tab |
| `o` | Open selected repository in new tab |
| `Esc` | Clear search (when input focused) |

### Publish with GitHub Pages

Configure Pages to serve from:
- Branch: `main`
- Folder: `/`

Web UI URL:
- `https://chryzsh.github.io/awesome-bof/site/`

## Quick Start

```bash
./scripts/bof-search.sh
```

This opens an interactive search interface. Type to filter, press Enter to select.

## Requirements

- `jq` - JSON processor
- `fzf` - Fuzzy finder

Install on Debian/Ubuntu:
```bash
sudo apt install jq fzf
```

Install on macOS:
```bash
brew install jq fzf
```

## Usage

### Interactive search
```bash
./scripts/bof-search.sh
```

### Search with initial query
```bash
./scripts/bof-search.sh ldap      # Find LDAP-related BOFs
./scripts/bof-search.sh dump      # Find dump/dumping commands
./scripts/bof-search.sh kerberos  # Find Kerberos commands
```

### Keyboard shortcuts

| Key | Action |
|-----|--------|
| `Enter` | Select and show details, then open repo |
| `Ctrl-O` | Open repository in browser |
| `Ctrl-Y` | Copy repository URL |
| `Ctrl-C` | Exit |

## How it works

The search uses a pre-generated index (`bof-index.json`) containing BOF metadata extracted from all repositories in the catalog.

Each entry contains:
- **name** - Command/BOF name
- **description** - What it does
- **repository** - Source GitHub repo
- **source_file** - Where the metadata was found
- **source_format** - How it was parsed (readme_table, cna, etc.)

## Updating the index

To refresh the index with latest BOFs from all repositories:

```bash
python3 scripts/bof_indexer.py
bash scripts/update-site-data.sh
```

This will:
1. Parse `BOF-CATALOG.md` for repository URLs
2. Clone each repo shallowly
3. Extract BOF metadata from READMEs, .cna files, directory structures
4. Output updated `bof-index.json`
5. Copy refreshed index to `site/data/bof-index.json` for web search

Note: This downloads all repos and takes several minutes.

## Index statistics

The index parses multiple formats:
- README tables
- Cobalt Strike `.cna` aggressor scripts
- Directory structures (folders containing .c/.o files)
- OC2 `stage1.py` files
- Havoc `havoc.py` files
- README bullet lists

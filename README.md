# Awesome BOF

A curated list of Beacon Object File (BOF) projects.

## [View the BOF Catalog](./BOF-CATALOG.md)
## [Search BOFs (Web UI)](./site/)

## Contributing

Add new BOFs via pull request. Use `scripts/generate_md.py <github-url>` to generate table rows.

## Web Search UI

A terminal-inspired, keyboard-first web search UI lives in `site/` and can be published with GitHub Pages.

### Refresh data for the site

```bash
python3 scripts/bof_indexer.py
bash scripts/update-site-data.sh
```

### Run locally

```bash
python3 -m http.server 8000
# open http://localhost:8000/site/
```

### GitHub Pages configuration

- Branch: `main`
- Folder: `/`

The web UI is served at:
- `https://chryzsh.github.io/awesome-bof/site/`

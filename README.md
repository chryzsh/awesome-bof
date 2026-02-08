# Awesome BOF

Curated Beacon Object Files, plus a fast searchable index.

## Start Here

- Catalog: [BOF-CATALOG.md](./BOF-CATALOG.md)
- Search: [awesome-bof web search](https://chryzsh.github.io/awesome-bof/site/)

## Update Search Data

```bash
python3 scripts/bof_indexer.py
bash scripts/update-site-data.sh
```

## Run Locally

```bash
python3 -m http.server 8000
# open http://localhost:8000/site/
```

## Contributing

Add new BOFs via pull request.  
Use `scripts/generate_md.py <github-url>` to generate table rows.

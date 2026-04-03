# Awesome BOF

> [!WARNING]
> **Security Notice:** Entries in this catalog are community-sourced and **not all manually vetted**.
> Some repositories may contain malicious code, backdoored binaries, or be copycat repos impersonating legitimate tools.
>
> Before using any BOF from this catalog:
> - **Inspect the source code** before compiling or running
> - **Never trust pre-compiled binaries** (`.o`, `.exe`, `.dll`) from any repository — always build from source
> - **Verify the repo author** — check account age, other repos, and stars relative to the original project
> - **Report suspicious entries** by [opening an issue](https://github.com/chryzsh/awesome-bof/issues)

A place to find Beacon Object Files, plus a fast searchable index of them.

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

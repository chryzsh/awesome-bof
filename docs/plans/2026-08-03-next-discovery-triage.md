# Next Discovery Triage Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Triage the highest-starred, source-available projects in the consolidated discovery queue and add eligible BOFs to the catalogue with factual AI-assisted review notes.

**Architecture:** Extract the untriaged repository URLs from issue #42, remove entries already present in the catalogue, and rank the remainder by GitHub stars. Review a small first batch under @bof-code-review, then update the Markdown catalogue, review record, search index, and site metadata only for projects that meet the catalogue’s scope.

**Tech Stack:** GitHub CLI/API, Git, Make, Python, boflint, Markdown, JSON, Node.js.

---

### Task 1: Select the first review batch

**Files:**
- Reference: GitHub issue #42
- Reference: `BOF-CATALOG.md`

**Step 1: Extract candidate repository URLs from #42.**

Run: `gh api repos/chryzsh/awesome-bof/issues/42 --jq .body`

Expected: candidate URLs from the original and consolidated report sections are available.

**Step 2: Exclude catalogued projects and rank the remaining candidates by stars.**

Run: query each GitHub repository’s `stargazers_count` through the GitHub API.

Expected: a reproducible short list of source-available, high-interest candidates.

**Step 3: Select up to three projects in scope for the first batch.**

Expected: each selection has source code and implements a BOF or an in-scope BOF collection.

### Task 2: Review selected BOFs

**Files:**
- Create: `docs/catalog-reviews/2026-08-03-<batch>-reviews.md`
- Reference: cloned project sources in a temporary directory

**Step 1: Clone each selected repository at its reviewed commit and read its build and usage documentation.**

Expected: the report records exact reviewed commits and review scope.

**Step 2: Build and run `boflint` for each available BOF artifact.**

Run: each project’s documented build command followed by `python3 ~/.claude/skills/bof-development/assets/boflint.py <artifact> --loader any`.

Expected: build and lint outcomes are recorded; failures remain factual review notes.

**Step 3: Review source for concrete stability, memory-safety, and Beacon-runtime issues.**

Expected: findings cite source locations and state the concrete failure mode; no speculative severity labels.

### Task 3: Update catalogue and search data

**Files:**
- Modify: `BOF-CATALOG.md`
- Modify: `bof-index.json`
- Modify: `site/data/bof-index.json`
- Modify: `docs/catalog-reviews/2026-08-03-<batch>-reviews.md`

**Step 1: Add eligible projects with source links and concise descriptions.**

Expected: entries fit an existing catalogue category and preserve the project’s published purpose.

**Step 2: Add dated review metadata to each new search-index entry.**

Expected: each note links to the review document and includes the established AI-assisted disclaimer.

**Step 3: Regenerate the index and synchronize site data.**

Run: `/usr/bin/python3 scripts/bof_indexer.py` and `bash scripts/update-site-data.sh`.

Expected: root and site index JSON match and contain the new records.

### Task 4: Verify and publish

**Files:**
- Verify: `BOF-CATALOG.md`, `bof-index.json`, `site/data/bof-index.json`, `site/app.js`

**Step 1: Validate JSON and JavaScript syntax.**

Run: `jq empty bof-index.json site/data/bof-index.json && node --check site/app.js && git diff --check`.

Expected: all checks pass.

**Step 2: Commit and push the review, catalogue, and generated-index changes.**

Expected: GitHub Pages receives the update.

**Step 3: Confirm the deployed page shows each review card.**

Expected: review notes are visible only on the newly reviewed entries.

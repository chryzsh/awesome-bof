# Second Discovery Batch Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Review and publish catalogue entries for ADWS-BOF, GeoLocation_BOF, and logon-monitor-bof.

**Architecture:** Clone each project at a pinned revision, run its available build and mandatory BOF lint checks, and record concrete source findings. Add eligible repositories to the existing Other BOFs table, regenerate the index, add one review card per generated command, and deploy the published data.

**Tech Stack:** GitHub, Git, Make, MinGW, Python, boflint, Markdown, JSON.

---

### Task 1: Review the three source projects

**Files:**
- Create: `docs/catalog-reviews/2026-08-03-second-discovery-batch-reviews.md`
- Reference: temporary clones of the three public repositories

**Step 1: Pin each source revision and read its documented build instructions.**

**Step 2: Build available artifacts and run `boflint --loader any`.**

**Step 3: Record only concrete source-level stability and runtime findings with source locations.**

### Task 2: Add the reviewed repositories

**Files:**
- Modify: `BOF-CATALOG.md`
- Modify: `bof-index.json`
- Modify: `site/data/bof-index.json`

**Step 1: Add an Other BOFs table row for each project with its limited-review link.**

**Step 2: Regenerate and synchronize the search index.**

Run: `/usr/bin/python3 scripts/bof_indexer.py && bash scripts/update-site-data.sh`

**Step 3: Add dated review metadata for each newly generated command entry.**

### Task 3: Verify and publish

**Files:**
- Verify: `BOF-CATALOG.md`, `bof-index.json`, `site/data/bof-index.json`, `site/app.js`

**Step 1: Run JSON, JavaScript, and whitespace validation.**

Run: `jq empty bof-index.json site/data/bof-index.json && node --check site/app.js && git diff --check`

**Step 2: Commit, push, and confirm a successful GitHub Pages deployment.**

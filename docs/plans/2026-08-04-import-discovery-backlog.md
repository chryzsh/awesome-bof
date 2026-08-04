# Discovery Backlog Import Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Import all remaining in-scope projects from issue #42 into the BOF catalogue without AI review notes, then begin a separate star-prioritized assessment programme for existing entries.

**Architecture:** Normalize all issue URLs, remove catalogued projects, then screen the remainder only for project scope and credible operator-targeting/malware concerns. Add qualifying projects to the appropriate catalog section with their published descriptions; preserve exclusions in an issue comment. Regenerate the search index. Assessments are intentionally a later, independent pass ordered by repository stars.

**Tech Stack:** GitHub CLI/API, Git, Python, Markdown, JSON.

---

### Task 1: Classify the untriaged discovery backlog

**Files:**
- Reference: GitHub issue #42
- Reference: `BOF-CATALOG.md`

**Step 1: Extract and normalize candidate repository URLs from #42.**

**Step 2: Remove URLs already catalogued and inspect the remaining repository metadata and README/source indicators.**

**Step 3: Produce an import list and a short exclusion list for clear false positives or credible operator-targeting/malware concerns.**

### Task 2: Import qualifying projects

**Files:**
- Modify: `BOF-CATALOG.md`
- Modify: `bof-index.json`
- Modify: `site/data/bof-index.json`

**Step 1: Add qualifying projects as ordinary catalogue rows, with no review links or assessment metadata.**

**Step 2: Regenerate and synchronize the search index.**

Run: `/usr/bin/python3 scripts/bof_indexer.py && bash scripts/update-site-data.sh`

**Step 3: Validate JSON and check that every imported URL is searchable.**

### Task 3: Close out the discovery queue and start assessment ordering

**Files:**
- Reference: GitHub issue #42
- Create: `docs/plans/2026-08-04-star-prioritized-assessments.md`

**Step 1: Post the import/exclusion summary to #42 and close it if no candidates remain.**

**Step 2: Produce the initial high-star assessment batch from catalogued entries without review metadata.**

**Step 3: Commit, push, and verify GitHub Pages deployment.**

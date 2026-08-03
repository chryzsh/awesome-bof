# Catalog Review Pilot Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add three source-available BOF projects to the catalog with dated, neutral AI-assisted review notes.

**Architecture:** The catalog rows remain concise and link to one review document. Each note fixes the date and reviewed commit, identifies Codex as the reviewing agent, limits the scope of the review, and records factual build/lint results plus operational cautions without declaring a project safe or unsafe.

**Tech Stack:** Markdown, GitHub source links, MinGW builds, boflint.

---

### Task 1: Create the pilot review record

**Files:**
- Create: `docs/catalog-reviews/2026-08-03-initial-bof-reviews.md`

**Step 1: Add the shared AI disclaimer**

State that the limited reviews were performed by Codex, an OpenAI GPT-5 agent; are AI-assisted; cover only the stated checks; and are neither security audits nor guarantees of safety.

**Step 2: Add one dated record per project**

Record repository URL, review date, source revision, review scope, and conclusions for RawHive, evtxsearch-bof, and DNSRPC-BOF. Include the observed build/lint results and exact operational cautions.

**Step 3: Verify required metadata**

Run: `rg -n 'Codex|AI-assisted|RawHive|evtxsearch|DNSRPC|boflint' docs/catalog-reviews/2026-08-03-initial-bof-reviews.md`
Expected: every review has the required metadata and the shared disclaimer is present.

### Task 2: Add catalog rows and review links

**Files:**
- Modify: `BOF-CATALOG.md:370`

**Step 1: Add the three entries**

Add the repositories to `Other BOFs` using their upstream descriptions and standard badges. Link each description to the corresponding anchored review record.

**Step 2: Preserve neutral language**

Use `Review: limited AI-assisted review (YYYY-MM-DD)` rather than safety claims or developer judgments.

### Task 3: Validate and commit

**Files:**
- Modify: `BOF-CATALOG.md`
- Create: `docs/catalog-reviews/2026-08-03-initial-bof-reviews.md`

**Step 1: Review generated index compatibility**

Run: `python3 scripts/bof_indexer.py --help`
Expected: exits 0.

**Step 2: Check the final diff**

Run: `git diff --check && git diff -- BOF-CATALOG.md docs/catalog-reviews/2026-08-03-initial-bof-reviews.md`
Expected: no whitespace errors and factual, neutral review language.

**Step 3: Commit**

Run: `git add BOF-CATALOG.md docs/catalog-reviews/2026-08-03-initial-bof-reviews.md docs/plans/2026-08-03-catalog-review-pilot.md && git commit -m "docs: add initial BOF review notes"`
Expected: creates one documentation commit.

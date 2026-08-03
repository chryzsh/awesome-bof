# Third Discovery Batch Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Review and publish catalogue entries for Entropia, async-pico-hub, and GDID-Extractor.

**Architecture:** Verify whether each source project fits the catalog’s broad BOF scope, assess available build and object-file evidence, and record factual compatibility or trust cautions. Add qualifying entries, regenerate the index, attach date-stamped review cards, and deploy.

**Tech Stack:** GitHub, Git, Make, CMake, Python, boflint, Markdown, JSON.

---

### Task 1: Review project scope and code

**Files:**
- Create: `docs/catalog-reviews/2026-08-03-third-discovery-batch-reviews.md`
- Reference: temporary source clones

**Step 1: Pin revisions and verify BOF relevance from source and documentation.**

**Step 2: Build available artifacts and run `boflint --loader any` where an object file is available.**

**Step 3: Record concrete build, loader, runtime, and provenance cautions.**

### Task 2: Update and publish catalogue data

**Files:**
- Modify: `BOF-CATALOG.md`
- Modify: `bof-index.json`
- Modify: `site/data/bof-index.json`

**Step 1: Add in-scope projects and dated review links.**

**Step 2: Regenerate the index and attach review metadata to produced entries.**

**Step 3: Validate, commit, push, and confirm Pages deployment.**

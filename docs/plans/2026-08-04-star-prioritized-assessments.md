# Star-Prioritized Catalogue Assessments Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add dated, limited AI-assisted assessments to established catalogue projects in descending repository-star order.

**Architecture:** Select the highest-starred repositories without review metadata, review source at a pinned revision with documented build and BOF lint evidence, and attach concise factual notes to the existing catalogue and search cards. Reviews remain separate from inclusion decisions.

**Tech Stack:** GitHub, Git, Make, Python, boflint, Markdown, JSON.

---

### Task 1: Review the first high-star batch

**Files:**
- Create: `docs/catalog-reviews/2026-08-04-high-star-batch-1.md`

**Step 1: Review `fortra/nanodump`, `trustedsec/CS-Situational-Awareness-BOF`, and `Mr-Un1k0d3r/SCShell` at pinned revisions.**

**Step 2: Run documented builds and `boflint` for available artifacts, then record only concrete findings.**

### Task 2: Publish assessment metadata

**Files:**
- Modify: `BOF-CATALOG.md`
- Modify: `bof-index.json`
- Modify: `site/data/bof-index.json`

**Step 1: Add dated review links and search-card metadata for all generated commands from the three repositories.**

**Step 2: Validate, commit, push, and confirm Pages deployment.**

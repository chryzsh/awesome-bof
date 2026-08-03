# Search Review Card Pilot Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Display RawHive's dated, AI-assisted operational caution on its search details card as a pilot for catalog-review metadata.

**Architecture:** Add an optional `review` object to the generated index entry for RawHive and have the existing details-card renderer show it only when present. The card will identify the review date and scope, link to the catalog review record, and use neutral caution language; entries without review metadata remain unchanged.

**Tech Stack:** JavaScript, JSON, HTML/CSS, Markdown.

---

### Task 1: Add optional review metadata to the search model

**Files:**
- Modify: `site/app.js:78-88`
- Modify: `bof-index.json`
- Modify: `site/data/bof-index.json`

**Step 1: Write a focused normalization test**

Add a JavaScript test or browser-independent assertion that confirms an entry with `review` metadata retains its date, status, note, and URL, while an ordinary entry remains review-free.

**Step 2: Extend normalized entries**

Preserve an optional, structured review object: `date`, `label`, `note`, and `url`.

**Step 3: Add RawHive's pilot record**

Set the date to `2026-08-03`, label to `Limited AI-assisted review`, link to `docs/catalog-reviews/2026-08-03-initial-bof-reviews.md#rawhive`, and summarize the bounded MFT-scan concern.

### Task 2: Render the review card on details view

**Files:**
- Modify: `site/app.js:164-189`
- Modify: `site/styles.css`

**Step 1: Render only when review metadata exists**

Add a clearly distinct review block beneath the project description. Include the review label/date, neutral note, and a `Read review` link.

**Step 2: Add accessible, restrained styling**

Use a neutral caution treatment that is readable without implying a safety rating or developer judgment.

**Step 3: Verify ordinary cards**

Confirm an entry without review metadata has no blank block or extra spacing.

### Task 3: Validate and publish the pilot

**Files:**
- Modify: `site/app.js`
- Modify: `site/styles.css`
- Modify: `bof-index.json`
- Modify: `site/data/bof-index.json`

**Step 1: Validate JSON and JavaScript**

Run: `jq empty bof-index.json && jq empty site/data/bof-index.json && node --check site/app.js`
Expected: exits 0.

**Step 2: Inspect the rendered card**

Run the local site and open the RawHive search result. Confirm the review block appears only on RawHive and the link resolves.

**Step 3: Commit and publish**

Run: `git add site/app.js site/styles.css bof-index.json site/data/bof-index.json docs/plans/2026-08-03-search-review-card-pilot.md && git commit -m "feat(site): show catalog review metadata" && git push origin main`
Expected: the Pages deployment publishes the pilot.

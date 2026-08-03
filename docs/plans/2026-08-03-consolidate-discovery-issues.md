# Consolidate Discovery Issues Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Preserve every untriaged discovery candidate in one open GitHub issue and close the superseded weekly reports.

**Architecture:** Issue #42 becomes the canonical queue. Its body records candidates unique to #38–#41 and links to each source report; each older issue receives a closure comment pointing to #42 before it is closed.

**Tech Stack:** GitHub CLI, GitHub Issues API, Markdown.

---

### Task 1: Build a complete canonical queue

**Files:**
- Modify: GitHub issue #42
- Reference: GitHub issues #38, #39, #40, #41

**Step 1: Extract and normalize GitHub repository URLs from all five reports.**

Run: `gh api repos/chryzsh/awesome-bof/issues/42 --jq .body`

Expected: the existing report body is available for update.

**Step 2: Append a provenance section to #42.**

Include every candidate from #38–#41 that is absent from #42, grouped under its source issue, and state that #42 is the canonical untriaged queue.

**Step 3: Verify preservation.**

Run: compare the normalized URL union from #38–#42 with the URLs in the revised #42 plus the three already-catalogued repositories.

Expected: every previously open candidate remains represented.

### Task 2: Close superseded reports

**Files:**
- Modify: GitHub issues #38, #39, #40, #41

**Step 1: Post a closure comment on each older report.**

Use the same concise statement: the candidate queue was consolidated into #42, with a direct link.

**Step 2: Close each older report.**

Run: `gh issue close <number> --repo chryzsh/awesome-bof`

Expected: #38–#41 are closed and #42 remains open.

### Task 3: Verify public state

**Files:**
- Verify: GitHub issues #38, #39, #40, #41, #42

**Step 1: List open issues.**

Run: `gh issue list --repo chryzsh/awesome-bof --state open`

Expected: only #42 remains from this set.

**Step 2: Confirm closure comments and canonical provenance.**

Run: `gh issue view 42 --repo chryzsh/awesome-bof --comments`

Expected: the canonical queue and its source links are visible.

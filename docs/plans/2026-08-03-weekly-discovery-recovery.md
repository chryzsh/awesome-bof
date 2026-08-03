# Weekly Discovery Recovery Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make scheduled BOF discovery resilient to GitHub API throttling and run discovery once for every missed scheduled window.

**Architecture:** The discovery client will treat GitHub API rate limiting and transient HTTP failures as partial-result conditions instead of uncaught failures. The workflow will expose a `since` dispatch input, selecting it over the normal 14-day scheduled window, so one backfill run can cover the period since the last successful window without gaps or duplicate weekly issues.

**Tech Stack:** Python 3.11, requests, unittest, GitHub Actions YAML.

---

### Task 1: Reproduce and test resilient GitHub search handling

**Files:**
- Modify: `tests/test_find_new_bofs.py`
- Modify: `scripts/find_new_bofs.py`

**Step 1: Write failing tests**

Add mocked-response tests proving repository and code search return partial/empty results for `403`, `429`, and transient request errors rather than raising `requests.HTTPError`. Add a test that code-search rate limiting is logged as partial.

**Step 2: Run the focused tests**

Run: `python3 -m unittest tests.test_find_new_bofs -v`
Expected: FAIL because the existing search paths call `raise_for_status()` for unhandled responses.

**Step 3: Implement the minimal resilient behavior**

Wrap outbound GitHub search requests in a helper that retries transient connection/timeout and 5xx responses with bounded backoff. Treat rate limits and other non-success API responses as a logged partial result; never raise from a scheduled discovery run solely because GitHub search is temporarily unavailable. Preserve successful results already collected.

**Step 4: Run focused tests**

Run: `python3 -m unittest tests.test_find_new_bofs -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add scripts/find_new_bofs.py tests/test_find_new_bofs.py
git commit -m "fix(discovery): tolerate GitHub API throttling"
```

### Task 2: Add a safe backfill mode to the workflow

**Files:**
- Modify: `.github/workflows/weekly-bof-discovery.yml`

**Step 1: Add a manual `since` input**

Define `workflow_dispatch.inputs.since` as an optional ISO date. Scheduled runs retain `--days 14`; manually dispatched backfills use `--since <date>`.

**Step 2: Ensure reports exist even after partial discovery**

Keep the discovery command successful when GitHub responses are temporarily unavailable and retain the existing report/artifact/issue flow for partial results.

**Step 3: Validate the workflow structure**

Run: `ruby -e 'require "yaml"; YAML.load_file(".github/workflows/weekly-bof-discovery.yml")'`
Expected: exits 0.

**Step 4: Commit**

```bash
git add .github/workflows/weekly-bof-discovery.yml
git commit -m "ci: support discovery backfills"
```

### Task 3: Verify and execute the historical recovery

**Files:**
- No repository files required beyond Tasks 1–2.

**Step 1: Run the full test suite**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS.

**Step 2: Review the final diff**

Run: `git diff --check && git diff -- .github/workflows/weekly-bof-discovery.yml scripts/find_new_bofs.py tests/test_find_new_bofs.py`
Expected: no whitespace errors; only intended resilience and dispatch changes.

**Step 3: Push the fix**

Run: `git push origin main`
Expected: remote branch advances with the workflow fix.

**Step 4: Dispatch one backfill run**

Dispatch `Weekly BOF Discovery` with `since=2026-04-06`, the start of the last successful weekly window before the earliest failed run. This covers all failed scheduled weeks (April 13; June 1, 8, 22, 29; July 13, 20; and August 3) in one deduplicated discovery pass.

**Step 5: Verify recovery**

Confirm the dispatched run completes successfully, its artifact includes a report, and any candidates create one recovery issue.

**Step 6: Commit plan record**

```bash
git add docs/plans/2026-08-03-weekly-discovery-recovery.md
git commit -m "docs: plan weekly discovery recovery"
```

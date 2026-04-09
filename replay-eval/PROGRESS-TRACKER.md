# TestBot Replay-and-Diff Evaluation - Progress Tracker

**Started:** 2026-04-08
**Last Updated:** 2026-04-08
**Status:** Not Started

---

## Current Phase

**Phase:** 0 - Repository Setup & Infrastructure
**Step:** Not started
**Status:** ⏸️ Awaiting approval to begin

---

## Progress Overview

| Phase | Status | PRs | Completion |
|-------|--------|-----|------------|
| Phase 0: Setup | ⏸️ Not Started | - | 0/6 steps |
| Phase 1: Validation | ⏸️ Not Started | 1 (PR #21267) | 0/6 steps |
| Phase 2: Tier 1 | ⏸️ Not Started | 5 PRs | 0/4 steps |
| Phase 3: Tier 2 | ⏸️ Not Started | 6 PRs | 0/3 steps |
| Phase 4: Tier 3 | ⏸️ Not Started | 2 PRs | 0/2 steps |
| Phase 5: Final Report | ⏸️ Not Started | - | 0/2 steps |

**Legend:**
- ⏸️ Not Started
- 🔄 In Progress
- ✅ Complete
- ❌ Failed/Blocked
- ⏭️ Skipped

---

## Phase 0: Repository Setup & Infrastructure

### Step 0.1: Create New Fork from PrefectHQ/prefect
- **Status:** ⏸️ Not Started
- **Assignee:** [TBD]
- **Started:** -
- **Completed:** -
- **Notes:**
  - Fork name: `prefect-testbot-eval`
  - Owner: `sxarsky`
  - Full history required (uncheck "Copy the main branch only")
- **Verification:**
  ```bash
  gh repo view sxarsky/prefect-testbot-eval --json name,description
  ```
- **Issues/Blockers:** None

---

### Step 0.2: Clone Fork and Setup Git Remotes
- **Status:** ⏸️ Not Started
- **Assignee:** [TBD]
- **Started:** -
- **Completed:** -
- **Notes:**
  - Clone location: `/Users/syedsky/Skyramp/content/product/features/testbot/testing/forks/prefect-testbot-eval`
  - Remotes: origin (fork) + upstream (PrefectHQ/prefect)
- **Verification:**
  ```bash
  git remote -v
  git log --oneline -1
  ```
- **Issues/Blockers:** None

---

### Step 0.3: Copy and Configure TestBot Workflow
- **Status:** ⏸️ Not Started
- **Assignee:** [TBD]
- **Started:** -
- **Completed:** -
- **Notes:**
  - Source: `../prefect-testb/.github/workflows/skyramp-testbot.yml`
  - Destination: `.github/workflows/skyramp-testbot.yml`
- **Verification:**
  ```bash
  gh api repos/sxarsky/prefect-testbot-eval/actions/workflows --jq '.workflows[].name'
  ```
- **Issues/Blockers:** None

---

### Step 0.4: Configure GitHub Secrets
- **Status:** ⏸️ Not Started
- **Assignee:** [TBD]
- **Started:** -
- **Completed:** -
- **Notes:**
  - URL: https://github.com/sxarsky/prefect-testbot-eval/settings/secrets/actions
  - Required secrets: SKYRAMP_LICENSE + others
- **Verification:**
  ```bash
  gh api repos/sxarsky/prefect-testbot-eval/actions/secrets --jq '.secrets[].name'
  ```
- **Issues/Blockers:** None

---

### Step 0.5: Copy and Update Evaluation Scripts
- **Status:** ⏸️ Not Started
- **Assignee:** [TBD]
- **Started:** -
- **Completed:** -
- **Notes:**
  - Copy `replay-eval/` directory
  - Update FORK_REPO in all .sh files
  - Make scripts executable
- **Verification:**
  ```bash
  grep "FORK_REPO" replay-eval/*.sh | grep "prefect-testbot-eval"
  ```
- **Issues/Blockers:** None

---

### Step 0.6: Validate Prerequisites
- **Status:** ⏸️ Not Started
- **Assignee:** [TBD]
- **Started:** -
- **Completed:** -
- **Notes:**
  - Check: gh auth, repo access, Python version, workflow config
- **Verification:**
  - All prerequisite checks pass
- **Issues/Blockers:** None

---

## Phase 1: Infrastructure Validation (PR #21267)

### Step 1.1: Extract Patches for PR #21267
- **Status:** ⏸️ Not Started
- **Assignee:** [TBD]
- **Started:** -
- **Completed:** -
- **Command:**
  ```bash
  ./replay-eval/extract_patches.sh 21267
  ```
- **Expected Output:**
  - `patches/pr21267/metadata.json`
  - `patches/pr21267/code-only.patch`
  - `patches/pr21267/test-ground-truth.patch`
  - `patches/pr21267/ground-truth/tests/utilities/test_processutils.py`
- **Issues/Blockers:** None

---

### Step 1.2: Prepare Replay Branch
- **Status:** ⏸️ Not Started
- **Assignee:** [TBD]
- **Started:** -
- **Completed:** -
- **Command:**
  ```bash
  ./replay-eval/prepare_replay.sh 21267
  ```
- **Expected Output:**
  - Branch `replay/pr21267` created
  - Only code changes (no tests)
- **Issues/Blockers:** None

---

### Step 1.3: Trigger TestBot
- **Status:** ⏸️ Not Started
- **Assignee:** [TBD]
- **Started:** -
- **Completed:** -
- **Command:**
  ```bash
  ./replay-eval/trigger_testbot.sh 21267 --wait
  ```
- **Expected Output:**
  - PR created on fork
  - TestBot workflow runs
  - TestBot commits generated tests
- **Notes:**
  - Monitor: 10-15 minutes for TestBot completion
  - Max wait: 20 minutes
- **Issues/Blockers:** None

---

### Step 1.4: Collect Results
- **Status:** ⏸️ Not Started
- **Assignee:** [TBD]
- **Started:** -
- **Completed:** -
- **Command:**
  ```bash
  ./replay-eval/collect_results.sh 21267
  ```
- **Expected Output:**
  - `results/replay/pr21267/generated/`
  - `results/replay/pr21267/comments/`
  - `results/replay/pr21267/logs/`
  - `results/replay/pr21267/collection_summary.md`
- **Issues/Blockers:** None

---

### Step 1.5: Run Comparison Analysis
- **Status:** ⏸️ Not Started
- **Assignee:** [TBD]
- **Started:** -
- **Completed:** -
- **Command:**
  ```bash
  python3 ./replay-eval/compare_tests.py 21267
  ```
- **Expected Output:**
  - `results/replay/pr21267/comparison/evaluation_report.md`
  - `results/replay/pr21267/comparison/comparison.json`
  - Structural similarity score and grade
- **Issues/Blockers:** None

---

### Step 1.6: Review and Validate Results
- **Status:** ⏸️ Not Started
- **Assignee:** [TBD]
- **Started:** -
- **Completed:** -
- **Checklist:**
  - [ ] Read full evaluation report
  - [ ] Compare test files manually
  - [ ] Check generated tests are valid Python
  - [ ] Verify comparison metrics make sense
- **Decision:** Proceed to Phase 2? YES / NO / ITERATE
- **Issues/Blockers:** None

---

## Phase 2: Tier 1 Full Execution

### Step 2.1: Run Remaining Tier 1 PRs
- **Status:** ⏸️ Not Started
- **Assignee:** [TBD]
- **Started:** -
- **Completed:** -
- **PRs:**
  - ✅ PR #21267 (done in Phase 1)
  - ⏸️ PR #21320 - Fix dotenv_values
  - ⏸️ PR #21307 - Add position to block schema
  - ⏸️ PR #21443 - Fix identity-verify run_results
  - ⏸️ PR #21356 - Fix deploy pull step
- **Command:**
  ```bash
  ./replay-eval/run_evaluation.sh --tier 1
  # OR individually:
  ./replay-eval/run_evaluation.sh 21320
  ./replay-eval/run_evaluation.sh 21307
  ./replay-eval/run_evaluation.sh 21443
  ./replay-eval/run_evaluation.sh 21356
  ```
- **Expected Duration:** 2-3 hours
- **Issues/Blockers:** None

---

### Step 2.2: Generate Tier 1 Summary Report
- **Status:** ⏸️ Not Started
- **Assignee:** [TBD]
- **Started:** -
- **Completed:** -
- **Command:**
  ```bash
  python3 replay-eval/summarize_tier.py 1 > results/tier1-summary.md
  ```
- **Expected Output:**
  - Table with all Tier 1 results
  - Average scores and recall
- **Issues/Blockers:** None

---

### Step 2.3: Analyze Tier 1 Patterns
- **Status:** ⏸️ Not Started
- **Assignee:** [TBD]
- **Started:** -
- **Completed:** -
- **Deliverable:** `results/tier1-findings.md`
- **Checklist:**
  - [ ] Document TestBot strengths
  - [ ] Document TestBot gaps
  - [ ] Provide specific examples
  - [ ] Make recommendations
- **Issues/Blockers:** None

---

### Step 2.4: Checkpoint Decision
- **Status:** ⏸️ Not Started
- **Assignee:** [TBD]
- **Started:** -
- **Completed:** -
- **Decision:** ✅ Proceed to Tier 2 / ⚠️ Iterate / 🛑 Pause
- **Reasoning:** [TBD after analysis]
- **Issues/Blockers:** None

---

## Phase 3: Tier 2 Execution

### Step 3.1: Run Tier 2 PRs
- **Status:** ⏸️ Not Started
- **Assignee:** [TBD]
- **Started:** -
- **Completed:** -
- **PRs:**
  - ⏸️ PR #21436 - Schedule persistence fix
  - ⏸️ PR #21365 - Worker attribution fix
  - ⏸️ PR #21350 - Parameter size limit
  - ⏸️ PR #21354 - ECS retry enhancement
  - ⏸️ PR #20951 - Concurrency API change
  - ⏸️ PR #21304 - Subprocess logging
- **Command:**
  ```bash
  ./replay-eval/run_evaluation.sh --tier 2
  ```
- **Expected Duration:** 3-4 hours
- **Issues/Blockers:** None

---

### Step 3.2: Generate Tier 2 Summary
- **Status:** ⏸️ Not Started
- **Assignee:** [TBD]
- **Started:** -
- **Completed:** -
- **Command:**
  ```bash
  python3 replay-eval/summarize_tier.py 2 > results/tier2-summary.md
  ```
- **Issues/Blockers:** None

---

### Step 3.3: Compare Tier 1 vs Tier 2
- **Status:** ⏸️ Not Started
- **Assignee:** [TBD]
- **Started:** -
- **Completed:** -
- **Deliverable:** `results/tier1-vs-tier2-comparison.md`
- **Analysis:** Does complexity degrade TestBot performance?
- **Issues/Blockers:** None

---

## Phase 4: Tier 3 and Bonus PRs

### Step 4.1: Run Tier 3 (Large Refactors)
- **Status:** ⏸️ Not Started
- **Assignee:** [TBD]
- **Started:** -
- **Completed:** -
- **PRs:**
  - ⏸️ PR #21286 - BuildKit support (1073 lines)
  - ⏸️ PR #21252 - Remove Runner usage (731 lines)
- **Command:**
  ```bash
  ./replay-eval/run_evaluation.sh --tier 3
  ```
- **Expected Duration:** 1-2 hours
- **Issues/Blockers:** None

---

### Step 4.2: Optional Bonus PRs
- **Status:** ⏸️ Not Started
- **Assignee:** [TBD]
- **Started:** -
- **Completed:** -
- **PRs:** 4 specialized PRs (21273, 21033, 21231, 21211)
- **Command:**
  ```bash
  ./replay-eval/run_evaluation.sh --tier bonus
  ```
- **Decision:** Run bonus PRs? YES / NO / PARTIAL
- **Issues/Blockers:** None

---

## Phase 5: Final Analysis and Report

### Step 5.1: Generate Comprehensive Summary
- **Status:** ⏸️ Not Started
- **Assignee:** [TBD]
- **Started:** -
- **Completed:** -
- **Deliverable:** `results/FINAL-EVALUATION-REPORT.md`
- **Contents:**
  - Executive summary
  - Results by tier
  - Overall metrics
  - Key findings
  - Recommendations
- **Issues/Blockers:** None

---

### Step 5.2: Archive and Preserve Results
- **Status:** ⏸️ Not Started
- **Assignee:** [TBD]
- **Started:** -
- **Completed:** -
- **Actions:**
  - [ ] Create tarball archive
  - [ ] Commit results to repo
  - [ ] Push to GitHub
  - [ ] Create release tag
- **Issues/Blockers:** None

---

## Issues Log

| Date | Phase/Step | Issue | Resolution | Status |
|------|------------|-------|------------|--------|
| - | - | - | - | - |

---

## Notes and Observations

### [Date] - [Phase/Step]
[Capture ad-hoc observations here as we work through the evaluation]

---

## Metrics Summary

### Tier 1 Results
| PR | Title | GT Tests | Gen Tests | Recall | Score | Grade |
|----|-------|----------|-----------|--------|-------|-------|
| #21267 | [TBD] | - | - | - | - | - |
| #21320 | [TBD] | - | - | - | - | - |
| #21307 | [TBD] | - | - | - | - | - |
| #21443 | [TBD] | - | - | - | - | - |
| #21356 | [TBD] | - | - | - | - | - |
| **Avg** | - | - | - | - | - | - |

### Tier 2 Results
| PR | Title | GT Tests | Gen Tests | Recall | Score | Grade |
|----|-------|----------|-----------|--------|-------|-------|
| [TBD] | - | - | - | - | - | - |

### Tier 3 Results
| PR | Title | GT Tests | Gen Tests | Recall | Score | Grade |
|----|-------|----------|-----------|--------|-------|-------|
| [TBD] | - | - | - | - | - | - |

---

## Timeline Tracking

| Phase | Planned Duration | Actual Duration | Variance | Notes |
|-------|-----------------|-----------------|----------|-------|
| Phase 0: Setup | 2-3 hours | - | - | - |
| Phase 1: Validation | 4-6 hours | - | - | - |
| Phase 2: Tier 1 | 1-2 days | - | - | - |
| Phase 3: Tier 2 | 1-2 days | - | - | - |
| Phase 4: Tier 3 | 1 day | - | - | - |
| Phase 5: Final | 1 day | - | - | - |
| **Total** | **~1-2 weeks** | - | - | - |

---

## Decision Points

### Phase 1 Validation Complete
- **Date:** [TBD]
- **Decision:** Proceed / Iterate / Pause
- **Reasoning:** [TBD]

### Phase 2 Tier 1 Complete
- **Date:** [TBD]
- **Decision:** Proceed / Iterate / Pause
- **Reasoning:** [TBD]

---

## Next Step

**Current Status:** Ready to begin Phase 0, Step 0.1
**Next Action:** Create fork at https://github.com/PrefectHQ/prefect
**Waiting On:** User approval to proceed
**Assigned To:** [TBD]

---

**Last Updated:** 2026-04-08
**Updated By:** Claude

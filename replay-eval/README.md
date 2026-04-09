# Replay-and-Diff Evaluation Scripts

Automated pipeline for evaluating TestBot's test generation quality against human-written tests from real PrefectHQ/prefect PRs.

## Prerequisites

Before running anything, verify these from your local machine:

```bash
# 1. gh CLI is authenticated and can access both repos
gh auth status
gh repo view PrefectHQ/prefect --json name -q .name        # should print "prefect"
gh repo view sxarsky/prefect-testb --json name -q .name     # should print "prefect-testb"

# 2. You're in the prefect fork directory
cd /Users/syedsky/Skyramp/content/product/features/testbot/testing/forks/prefect-testb

# 3. Git remotes are correct (origin = your fork)
git remote -v
# origin  https://github.com/sxarsky/prefect-testb.git (fetch/push)
# If 'upstream' doesn't exist, extract_patches.sh will add it automatically

# 4. You have push access to the fork
git push --dry-run origin main 2>&1 | head -1  # should not error

# 5. Python 3.8+ is available (for compare_tests.py — uses only stdlib)
python3 --version

# 6. TestBot workflow is configured in the fork
cat .github/workflows/skyramp-testbot.yml | head -5

# 7. GitHub secrets are set on sxarsky/prefect-testb
#    (SKYRAMP_LICENSE, any other required secrets)
#    Check at: https://github.com/sxarsky/prefect-testb/settings/secrets/actions

# 8. Scripts are executable
chmod +x /Users/syedsky/Skyramp/content/product/features/testbot/testing/replay-eval/*.sh
```

## Quick Start

```bash
# Navigate to the prefect fork
cd /Users/syedsky/Skyramp/content/product/features/testbot/testing/forks/prefect-testb

# Run the full pipeline for a single PR (smallest, good first test)
../replay-eval/run_evaluation.sh 21267

# Or run step by step:
../replay-eval/extract_patches.sh 21267
../replay-eval/prepare_replay.sh 21267
../replay-eval/trigger_testbot.sh 21267 --wait
../replay-eval/collect_results.sh 21267
python3 ../replay-eval/compare_tests.py 21267
```

## Step-by-Step Walkthrough

### Step 0: Choose a PR

Review `CANDIDATES.md` or `candidates.csv` in this directory. Start with Tier 1 (smallest PRs) to validate the pipeline works end-to-end before scaling up.

Recommended first PR: **#21267** (Fix UnicodeDecodeError — 25 lines, 1 test file).

### Step 1: Extract Patches

```bash
cd /Users/syedsky/Skyramp/content/product/features/testbot/testing/forks/prefect-testb
../replay-eval/extract_patches.sh 21267
```

**What it does:**
1. Fetches PR metadata from PrefectHQ/prefect via `gh`
2. Adds `upstream` remote if not present, fetches the merge commit
3. Identifies the parent commit (pre-PR state of main)
4. Generates the full diff, then splits it into:
   - `patches/pr21267/code-only.patch` — source file changes only
   - `patches/pr21267/test-ground-truth.patch` — test file changes only
5. Extracts full test file contents at the merge commit into `patches/pr21267/ground-truth/`

**Verify:** Check that `patches/pr21267/` contains both patches and the ground-truth directory has `.py` test files.

### Step 2: Prepare Replay Branch

```bash
../replay-eval/prepare_replay.sh 21267
```

**What it does:**
1. Checks out the pre-PR commit (detached HEAD)
2. Creates branch `replay/pr21267`
3. Applies the code-only patch (no tests)
4. Commits with a descriptive message linking to the original PR

**Verify:** `git log --oneline -3` should show your replay commit on top of the pre-PR state. `git diff HEAD~1 --stat` should show only source files, no test files.

### Step 3: Trigger TestBot

```bash
../replay-eval/trigger_testbot.sh 21267 --wait
```

**What it does:**
1. Pushes `replay/pr21267` to `origin` (your fork)
2. Creates a PR on `sxarsky/prefect-testb` via `gh pr create`
3. With `--wait`: polls every 60 seconds (up to 20 min) for TestBot to commit generated tests

**Verify:** Visit the PR URL printed by the script. You should see TestBot's comment and/or commit with generated tests.

**Without --wait:** If you prefer to check manually:
```bash
../replay-eval/trigger_testbot.sh 21267
# ... go check the PR on GitHub when ready ...
../replay-eval/collect_results.sh 21267
```

### Step 4: Collect Results

```bash
../replay-eval/collect_results.sh 21267
```

**What it does:**
1. Fetches the latest state of the replay branch (including TestBot's commits)
2. Diffs between your replay commit and the branch tip to find TestBot-added files
3. Extracts generated test files to `results/replay/pr21267/generated/`
4. Collects PR comments (TestBot's analysis) to `results/replay/pr21267/comments/`
5. Downloads workflow run logs to `results/replay/pr21267/logs/`

**Verify:** `results/replay/pr21267/generated/` should contain `.py` files. `collection_summary.md` shows counts.

### Step 5: Compare

```bash
python3 ../replay-eval/compare_tests.py 21267
```

**What it does:**
1. AST-parses both test suites (ground truth and generated)
2. Profiles each: test function count, assertion types, fixtures, mocks, parametrization
3. Computes matching metrics (exact name match, fuzzy match, recall)
4. Classifies test types (unit/integration/contract)
5. Calculates a structural similarity score (0-100)
6. Generates `results/replay/pr21267/comparison/evaluation_report.md`

**Verify:** Read the evaluation report. It contains the score, a breakdown of what matched and what was missed, and instructions for follow-up coverage and mutation testing.

## Running Multiple PRs

### By Tier

```bash
# Tier 1: 5 small PRs for methodology validation (~1 day)
./run_evaluation.sh --tier 1

# Tier 2: 6 medium PRs for cross-system analysis (~3 days)
./run_evaluation.sh --tier 2

# Tier 3: 2 large refactors (~2 days)
./run_evaluation.sh --tier 3

# All 17 PRs (~2 weeks)
./run_evaluation.sh --all

# Dry run to preview what would happen
./run_evaluation.sh --tier 1 --dry-run
```

### Resuming After Interruption

If you've already run some steps for a PR, skip ahead:

```bash
# TestBot already ran, just need to collect and compare
./run_evaluation.sh 21267 --skip-to collect

# Patches extracted, need to prepare+trigger+collect+compare
./run_evaluation.sh 21267 --skip-to prepare
```

### Tier Composition

| Tier | PRs | Focus |
|------|-----|-------|
| 1 | 21267, 21320, 21307, 21443, 21356 | Small/focused — validate the pipeline |
| 2 | 21436, 21365, 21350, 21354, 20951, 21304 | Medium — cross-system changes |
| 3 | 21286, 21252 | Large — stress test with big refactors |
| Bonus | 21273, 21033, 21231, 21211 | Specialized — concurrency, schema, multi-integration |

## Output Structure

```
prefect-testb/
├── patches/pr<N>/
│   ├── metadata.json              # PR number, title, merge commit, dates
│   ├── base_commit.txt            # The pre-PR commit hash
│   ├── full.patch                 # Complete PR diff (reference)
│   ├── code-only.patch            # Source changes only (used for replay)
│   ├── test-ground-truth.patch    # Test changes only (the benchmark)
│   ├── code_files.txt             # List of changed source files
│   ├── test_files.txt             # List of changed test files
│   ├── fork_pr_number.txt         # PR number on your fork (after trigger)
│   └── ground-truth/              # Full test file contents at merge commit
│       └── tests/.../*.py
│
└── results/replay/pr<N>/
    ├── generated/                 # TestBot-generated test files
    │   └── tests/.../*.py
    ├── comments/
    │   ├── all_comments.json      # All PR comments
    │   └── testbot_comments.md    # TestBot's analysis text
    ├── logs/
    │   ├── workflow_runs.json     # Workflow run metadata
    │   └── run_<ID>.log           # Full workflow log
    ├── testbot-diff.patch         # Diff of everything TestBot added
    ├── collection_summary.md      # Summary of collected artifacts
    └── comparison/
        ├── evaluation_report.md   # Human-readable scored report
        ├── comparison.json        # Full comparison data (machine-readable)
        ├── ground_truth_profile.json  # AST analysis of human tests
        └── generated_profile.json     # AST analysis of TestBot tests
```

## Troubleshooting

**"Could not find parent of merge commit"**
The PR may have been squash-merged. The script falls back to `baseRefOid` from the PR metadata. If that also fails, you may need to `git fetch upstream main --unshallow` to get more history.

**Patch application fails**
The code-only patch is applied to the exact parent commit, so conflicts should be rare. If they happen, the script reports the failure and suggests `git apply --reject` for manual resolution.

**TestBot doesn't run**
Check that the GitHub workflow is configured and secrets are set. Visit the fork's Actions tab to see if the workflow was triggered. Common issues: workflow file not on the target branch, missing secrets, TestBot version mismatch.

**TestBot runs but doesn't commit tests**
This is a known issue (silent commit failures from the March 20 regression). Check the workflow logs for errors. The `collect_results.sh` script will warn if no TestBot commits are found.

**compare_tests.py finds 0 functions**
The AST parser looks for functions starting with `test_`. If TestBot generates tests with different naming, the parser won't pick them up. Check the generated files manually.

## Files in This Directory

| File | Description |
|------|-------------|
| `README.md` | This file — full walkthrough and reference |
| `CANDIDATES.md` | Detailed analysis of all 17 candidate PRs with rationales |
| `candidates.csv` | Machine-readable PR reference (for filtering/sorting) |
| `run_evaluation.sh` | End-to-end orchestrator (single PR, tier, or all) |
| `extract_patches.sh` | Step 1: Fetch upstream PR, split into code + test patches |
| `prepare_replay.sh` | Step 2: Create replay branch with code-only changes |
| `trigger_testbot.sh` | Step 3: Push branch, create fork PR, trigger TestBot |
| `collect_results.sh` | Step 4: Gather TestBot output (tests, comments, logs) |
| `compare_tests.py` | Step 5: Multi-dimensional comparison with scored report |

## Related Documents

- **Methodology doc:** `REPLAY-DIFF-METHODOLOGY.md` (this directory) — full rationale, metrics definitions, risk mitigations
- **Master tracking:** `../MASTER-TRACKING.md` — overall TestBot validation progress
- **Previous results:** `../results/` — March 16 and March 20 testing session outputs
- **Product evaluation:** `../PRODUCT_PROGRESS_EVALUATION.md` — v0.4.x vs v0.5.0+ regression analysis

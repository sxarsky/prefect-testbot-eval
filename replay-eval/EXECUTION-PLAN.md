# TestBot Replay-and-Diff Evaluation - Execution Plan

**Created:** 2026-04-08
**Owner:** Syed
**Goal:** Quantitatively evaluate TestBot's test generation quality against human-written tests from real PRs

---

## Overview

This plan executes the replay-and-diff methodology using a new dedicated fork (`prefect-testbot-eval`) to isolate the evaluation work. We'll process 17 candidate PRs in tiers, comparing TestBot's generated tests against human-written ground truth.

**Why a new fork?**
- Clean isolation from other TestBot work
- No conflicts with existing PRs/branches
- Easy to archive after completion
- Can repeat with different TestBot versions

---

## Phase 0: Repository Setup & Infrastructure

**Goal:** Create and configure a new fork with TestBot infrastructure ready to run.

### Step 0.1: Create New Fork from PrefectHQ/prefect

**Actions:**
1. Navigate to https://github.com/PrefectHQ/prefect
2. Click "Fork" button → "Create a new fork"
3. Configure fork:
   - **Repository name:** `prefect-testbot-eval`
   - **Owner:** `sxarsky` (or your organization)
   - **Description:** "TestBot replay-and-diff evaluation - comparing generated vs human tests"
   - **IMPORTANT:** Uncheck "Copy the main branch only" - we need full history for git operations
4. Click "Create fork"

**Expected outcome:**
- New repository at `https://github.com/sxarsky/prefect-testbot-eval`
- Full repository history available

**Verification:**
```bash
# Check the fork exists
gh repo view sxarsky/prefect-testbot-eval --json name,description
```

---

### Step 0.2: Clone Fork and Setup Git Remotes

**Actions:**
```bash
# Navigate to forks directory
cd /Users/syedsky/Skyramp/content/product/features/testbot/testing/forks/

# Clone the new fork
git clone https://github.com/sxarsky/prefect-testbot-eval.git
cd prefect-testbot-eval

# Add upstream remote (required by extraction scripts)
git remote add upstream https://github.com/PrefectHQ/prefect.git

# Verify remotes are correct
git remote -v
# Expected:
# origin    https://github.com/sxarsky/prefect-testbot-eval.git (fetch)
# origin    https://github.com/sxarsky/prefect-testbot-eval.git (push)
# upstream  https://github.com/PrefectHQ/prefect.git (fetch)
# upstream  https://github.com/PrefectHQ/prefect.git (push)

# Sync with latest upstream main
git fetch upstream main
git merge upstream/main --ff-only
git push origin main
```

**Expected outcome:**
- Local clone at `/Users/syedsky/Skyramp/content/product/features/testbot/testing/forks/prefect-testbot-eval`
- Both `origin` (fork) and `upstream` (PrefectHQ/prefect) remotes configured
- Fork's main branch is up-to-date with upstream

**Verification:**
```bash
git log --oneline -1  # Should show latest Prefect commit
git remote -v         # Should show both remotes
```

---

### Step 0.3: Copy and Configure TestBot Workflow

**Actions:**
```bash
cd /Users/syedsky/Skyramp/content/product/features/testbot/testing/forks/prefect-testbot-eval

# Create workflows directory if it doesn't exist
mkdir -p .github/workflows

# Copy TestBot workflow from existing prefect-testb fork
cp ../prefect-testb/.github/workflows/skyramp-testbot.yml \
   .github/workflows/skyramp-testbot.yml

# Review the workflow file
cat .github/workflows/skyramp-testbot.yml

# Commit and push the workflow
git add .github/workflows/skyramp-testbot.yml
git commit -m "Add TestBot workflow for replay-and-diff evaluation"
git push origin main
```

**Expected outcome:**
- TestBot workflow configured at `.github/workflows/skyramp-testbot.yml`
- Workflow committed to main branch
- Workflow visible in GitHub Actions tab

**Verification:**
```bash
# Check file exists
ls -la .github/workflows/skyramp-testbot.yml

# Verify it's pushed
gh api repos/sxarsky/prefect-testbot-eval/actions/workflows --jq '.workflows[].name'
```

---

### Step 0.4: Configure GitHub Secrets

**Actions:**
1. Navigate to https://github.com/sxarsky/prefect-testbot-eval/settings/secrets/actions
2. Click "New repository secret" for each required secret
3. Copy values from existing prefect-testb fork secrets:
   - `SKYRAMP_LICENSE` - TestBot license key
   - Any additional secrets required by TestBot workflow

**Expected outcome:**
- All required secrets configured in new fork
- TestBot workflow can access necessary credentials

**Verification:**
```bash
# List configured secrets (names only, values hidden)
gh api repos/sxarsky/prefect-testbot-eval/actions/secrets --jq '.secrets[].name'
```

---

### Step 0.5: Copy and Update Evaluation Scripts

**Actions:**
```bash
cd /Users/syedsky/Skyramp/content/product/features/testbot/testing/forks/prefect-testbot-eval

# Copy the entire replay-eval directory
cp -r ../../replay-eval ./replay-eval

# Make all scripts executable
chmod +x replay-eval/*.sh

# Update FORK_REPO variable in all scripts
cd replay-eval
sed -i '' 's/sxarsky\/prefect-testb/sxarsky\/prefect-testbot-eval/g' *.sh

# Verify the changes
echo "=== Checking FORK_REPO in scripts ==="
grep "FORK_REPO=" *.sh

# Return to repo root
cd ..
```

**Expected outcome:**
- `replay-eval/` directory copied to new fork
- All scripts executable (chmod +x)
- FORK_REPO variable updated to `sxarsky/prefect-testbot-eval`

**Verification:**
```bash
# Check scripts exist and are executable
ls -la replay-eval/*.sh

# Verify FORK_REPO update
grep "FORK_REPO" replay-eval/*.sh | grep "prefect-testbot-eval"
```

---

### Step 0.6: Validate Prerequisites

**Actions:**
```bash
cd /Users/syedsky/Skyramp/content/product/features/testbot/testing/forks/prefect-testbot-eval

echo "=== Checking Prerequisites ==="

# 1. gh CLI authentication
echo "1. GitHub CLI authentication:"
gh auth status

# 2. Upstream repo access
echo "2. Upstream repo access:"
gh repo view PrefectHQ/prefect --json name -q .name

# 3. Fork repo access
echo "3. Fork repo access:"
gh repo view sxarsky/prefect-testbot-eval --json name -q .name

# 4. Push access to fork
echo "4. Push access:"
git push --dry-run origin main 2>&1 | head -1

# 5. Python version
echo "5. Python version:"
python3 --version

# 6. TestBot workflow exists
echo "6. TestBot workflow:"
cat .github/workflows/skyramp-testbot.yml | head -5

# 7. Scripts are executable
echo "7. Scripts executable:"
ls -l replay-eval/*.sh | head -3
```

**Expected outcome:**
- All checks pass without errors
- gh CLI is authenticated
- Python 3.8+ is available
- TestBot workflow is configured
- Scripts are executable

**Verification:**
All commands above should complete without errors.

---

## Phase 1: Infrastructure Validation

**Goal:** Prove the pipeline works end-to-end with the smallest PR before scaling up.

### Step 1.1: Extract Patches for PR #21267

**Why PR #21267?**
- Smallest in Tier 1: only 25 lines changed
- Single test file: `tests/utilities/test_processutils.py`
- Simple bug fix: Unicode handling in subprocess output
- Low risk for first run

**Actions:**
```bash
cd /Users/syedsky/Skyramp/content/product/features/testbot/testing/forks/prefect-testbot-eval

# Run extraction
./replay-eval/extract_patches.sh 21267
```

**Expected outcome:**
- Directory created: `patches/pr21267/`
- Files created:
  - `metadata.json` - PR details
  - `base_commit.txt` - Pre-PR commit hash
  - `full.patch` - Complete PR diff
  - `code-only.patch` - Source changes only
  - `test-ground-truth.patch` - Test changes only
  - `code_files.txt` - List of source files
  - `test_files.txt` - List of test files
  - `ground-truth/tests/utilities/test_processutils.py` - Human-written test

**Verification:**
```bash
# Check all expected files exist
ls -la patches/pr21267/

# Verify metadata
cat patches/pr21267/metadata.json

# Check patch sizes
echo "Code patch lines: $(wc -l < patches/pr21267/code-only.patch)"
echo "Test patch lines: $(wc -l < patches/pr21267/test-ground-truth.patch)"

# Verify ground truth test exists
ls -la patches/pr21267/ground-truth/tests/utilities/test_processutils.py
```

---

### Step 1.2: Prepare Replay Branch

**Actions:**
```bash
cd /Users/syedsky/Skyramp/content/product/features/testbot/testing/forks/prefect-testbot-eval

# Run prepare script
./replay-eval/prepare_replay.sh 21267
```

**Expected outcome:**
- Branch created: `replay/pr21267`
- Branch contains pre-PR state + code changes only (no tests)
- Clean commit with descriptive message

**Verification:**
```bash
# Check branch exists
git branch --list replay/pr21267

# Verify we're on the branch
git branch --show-current

# Check commit history
git log --oneline -3

# Verify only code files changed (no test files)
git diff HEAD~1 --name-only
# Should NOT include any files in tests/ directories

# Check the diff stats
git diff HEAD~1 --stat
```

---

### Step 1.3: Trigger TestBot

**Actions:**
```bash
cd /Users/syedsky/Skyramp/content/product/features/testbot/testing/forks/prefect-testbot-eval

# Run trigger script with --wait flag
./replay-eval/trigger_testbot.sh 21267 --wait
```

**What happens:**
1. Script pushes `replay/pr21267` branch to origin
2. Creates a PR on `sxarsky/prefect-testbot-eval`
3. TestBot workflow triggers automatically
4. Script polls every 60 seconds for TestBot completion (max 20 minutes)

**Expected outcome:**
- PR created on fork (number saved to `patches/pr21267/fork_pr_number.txt`)
- TestBot workflow runs
- TestBot analyzes code and generates tests
- TestBot commits generated tests to the PR
- Script detects TestBot completion

**Verification:**
```bash
# Check fork PR number was saved
cat patches/pr21267/fork_pr_number.txt

# View the PR in browser
gh pr view $(cat patches/pr21267/fork_pr_number.txt) --repo sxarsky/prefect-testbot-eval --web

# Check workflow status
gh run list --repo sxarsky/prefect-testbot-eval --branch replay/pr21267

# Monitor workflow logs (if still running)
gh run watch --repo sxarsky/prefect-testbot-eval
```

**Manual monitoring (if --wait times out):**
```bash
# Check PR for TestBot commits
gh pr view $(cat patches/pr21267/fork_pr_number.txt) \
  --repo sxarsky/prefect-testbot-eval \
  --json commits --jq '.commits[].messageHeadline'
```

---

### Step 1.4: Collect Results

**Actions:**
```bash
cd /Users/syedsky/Skyramp/content/product/features/testbot/testing/forks/prefect-testbot-eval

# Run collection script
./replay-eval/collect_results.sh 21267
```

**What happens:**
1. Fetches latest branch state (including TestBot commits)
2. Identifies TestBot's commits
3. Extracts generated test files
4. Collects PR comments (TestBot's analysis)
5. Downloads workflow run logs
6. Generates collection summary

**Expected outcome:**
- Directory created: `results/replay/pr21267/`
- Subdirectories:
  - `generated/` - TestBot-generated test files
  - `comments/` - PR comments and TestBot analysis
  - `logs/` - Workflow run logs
- Files:
  - `testbot-diff.patch` - Diff of TestBot's changes
  - `collection_summary.md` - Summary of collected artifacts

**Verification:**
```bash
# Check directory structure
tree results/replay/pr21267/ -L 2

# View collection summary
cat results/replay/pr21267/collection_summary.md

# Count generated test files
find results/replay/pr21267/generated -name "*.py" -type f

# Check TestBot comments
cat results/replay/pr21267/comments/testbot_comments.md
```

---

### Step 1.5: Run Comparison Analysis

**Actions:**
```bash
cd /Users/syedsky/Skyramp/content/product/features/testbot/testing/forks/prefect-testbot-eval

# Run comparison script
python3 ./replay-eval/compare_tests.py 21267
```

**What happens:**
1. AST-parses ground truth tests from `patches/pr21267/ground-truth/`
2. AST-parses generated tests from `results/replay/pr21267/generated/`
3. Profiles both test suites (functions, assertions, fixtures, mocks)
4. Computes comparison metrics (matching, recall, similarity)
5. Calculates structural similarity score (0-100)
6. Generates human-readable evaluation report

**Expected outcome:**
- Directory created: `results/replay/pr21267/comparison/`
- Files:
  - `evaluation_report.md` - Human-readable comparison with score and grade
  - `comparison.json` - Machine-readable comparison data
  - `ground_truth_profile.json` - AST analysis of human tests
  - `generated_profile.json` - AST analysis of TestBot tests

**Verification:**
```bash
# Check all output files exist
ls -la results/replay/pr21267/comparison/

# Read the evaluation report
cat results/replay/pr21267/comparison/evaluation_report.md

# Check the score
grep "Total Structural Similarity" results/replay/pr21267/comparison/evaluation_report.md
grep "Grade:" results/replay/pr21267/comparison/evaluation_report.md

# View raw comparison data
python3 -m json.tool results/replay/pr21267/comparison/comparison.json | head -50
```

---

### Step 1.6: Review and Validate Results

**Actions:**
1. Read the full evaluation report
2. Manually compare a few test functions between ground truth and generated
3. Check if generated tests are syntactically valid
4. Verify the comparison metrics make sense

**Review checklist:**
```bash
cd /Users/syedsky/Skyramp/content/product/features/testbot/testing/forks/prefect-testbot-eval

# 1. Read the full report
less results/replay/pr21267/comparison/evaluation_report.md

# 2. Compare test files side by side
echo "=== Ground Truth Tests ==="
ls -la patches/pr21267/ground-truth/tests/

echo "=== Generated Tests ==="
ls -la results/replay/pr21267/generated/tests/

# 3. Check if generated tests are syntactically valid Python
python3 -m py_compile results/replay/pr21267/generated/tests/**/*.py

# 4. Review key metrics
echo "=== Key Metrics ==="
python3 -c "
import json
with open('results/replay/pr21267/comparison/comparison.json') as f:
    data = json.load(f)
    print(f\"Ground truth tests: {data['summary']['ground_truth_test_count']}\")
    print(f\"Generated tests: {data['summary']['generated_test_count']}\")
    print(f\"Exact matches: {data['matching']['exact_name_matches']}\")
    print(f\"Recall: {data['matching']['recall_fuzzy']:.0%}\")
"
```

**Decision point:**
- ✅ **If successful:** Pipeline is validated, proceed to Phase 2 (Tier 1 full execution)
- ❌ **If issues found:** Debug and fix before proceeding

**Common issues and fixes:**
- **No generated tests:** Check workflow logs for errors
- **Syntax errors in generated tests:** Note as TestBot issue, continue with evaluation
- **Comparison script errors:** Check Python version, fix script bugs
- **Unexpected metrics:** Review scoring methodology in compare_tests.py

---

## Phase 2: Tier 1 Full Execution

**Goal:** Run all 5 Tier 1 PRs to establish baseline metrics and validate methodology at scale.

### Step 2.1: Run Remaining Tier 1 PRs

**Tier 1 PRs:**
- ✅ PR #21267 - Fix UnicodeDecodeError (25 lines) - **DONE in Phase 1**
- PR #21320 - Fix dotenv_values (28 lines)
- PR #21307 - Add position to block schema (132 lines)
- PR #21443 - Fix identity-verify run_results (292 lines)
- PR #21356 - Fix deploy pull step (216 lines)

**Option A: Run individually for control**
```bash
cd /Users/syedsky/Skyramp/content/product/features/testbot/testing/forks/prefect-testbot-eval

# Run each PR individually, reviewing results after each
./replay-eval/run_evaluation.sh 21320
./replay-eval/run_evaluation.sh 21307
./replay-eval/run_evaluation.sh 21443
./replay-eval/run_evaluation.sh 21356
```

**Option B: Run all at once**
```bash
# Run all remaining Tier 1 PRs
# (The script skips 21267 if already complete)
./replay-eval/run_evaluation.sh --tier 1
```

**Expected duration:** 2-3 hours total (10-15 min per PR)

**Expected outcome:**
- 5 complete evaluation results in `results/replay/pr<N>/`
- 5 evaluation reports with scores and grades

**Verification after each PR:**
```bash
# Check that all phases completed
ls -la results/replay/pr21320/comparison/evaluation_report.md

# Quick score check
grep "Total Structural Similarity" results/replay/pr21320/comparison/evaluation_report.md
```

---

### Step 2.2: Generate Tier 1 Summary Report

**Actions:**
```bash
cd /Users/syedsky/Skyramp/content/product/features/testbot/testing/forks/prefect-testbot-eval

# Create summary script
cat > replay-eval/summarize_tier.py <<'EOF'
#!/usr/bin/env python3
import json
import sys
from pathlib import Path

tier_num = sys.argv[1] if len(sys.argv) > 1 else "1"

# Tier PR mappings
TIERS = {
    "1": [21267, 21320, 21307, 21443, 21356],
    "2": [21436, 21365, 21350, 21354, 20951, 21304],
    "3": [21286, 21252],
    "bonus": [21273, 21033, 21231, 21211]
}

print(f"# Tier {tier_num} Summary Report\n")
print("| PR | Title | GT Tests | Gen Tests | Recall | Score | Grade |")
print("|---|---|---|---|---|---|---|")

for pr in TIERS.get(tier_num, []):
    comp_file = Path(f"results/replay/pr{pr}/comparison/comparison.json")
    meta_file = Path(f"patches/pr{pr}/metadata.json")

    if not comp_file.exists():
        continue

    with open(comp_file) as f:
        data = json.load(f)

    with open(meta_file) as f:
        meta = json.load(f)

    title = meta["title"][:40]
    gt_count = data["summary"]["ground_truth_test_count"]
    gen_count = data["summary"]["generated_test_count"]
    recall = data["matching"]["recall_fuzzy"]

    # Extract score from report (simplified)
    report_file = Path(f"results/replay/pr{pr}/comparison/evaluation_report.md")
    score = "N/A"
    grade = "N/A"
    if report_file.exists():
        content = report_file.read_text()
        for line in content.split("\n"):
            if "Total Structural Similarity:" in line:
                # Parse something like "Total Structural Similarity: 65.0/100 (65%)"
                parts = line.split(":")[-1].strip()
                score = parts.split("(")[0].strip()
            if "Grade:" in line:
                grade = line.split(":")[-1].strip()

    print(f"| #{pr} | {title} | {gt_count} | {gen_count} | {recall:.0%} | {score} | {grade} |")

print("\n## Summary Statistics\n")
# Calculate averages
scores = []
recalls = []
for pr in TIERS.get(tier_num, []):
    comp_file = Path(f"results/replay/pr{pr}/comparison/comparison.json")
    if comp_file.exists():
        with open(comp_file) as f:
            data = json.load(f)
            recalls.append(data["matching"]["recall_fuzzy"])

if scores:
    print(f"Average score: {sum(scores)/len(scores):.1f}/100")
if recalls:
    print(f"Average recall: {sum(recalls)/len(recalls):.0%}")
EOF

chmod +x replay-eval/summarize_tier.py

# Generate summary
python3 replay-eval/summarize_tier.py 1 > results/tier1-summary.md

# View the summary
cat results/tier1-summary.md
```

**Expected outcome:**
- Summary table with all Tier 1 results
- Quick comparison of scores across PRs
- Patterns become visible

---

### Step 2.3: Analyze Tier 1 Patterns

**Actions:**
Create a findings document analyzing patterns across Tier 1:

```bash
cd /Users/syedsky/Skyramp/content/product/features/testbot/testing/forks/prefect-testbot-eval

cat > results/tier1-findings.md <<'EOF'
# Tier 1 Findings - Methodology Validation

**Date:** $(date +%Y-%m-%d)
**PRs Evaluated:** 5 (21267, 21320, 21307, 21443, 21356)

## Executive Summary

- **Average Structural Similarity:** [TBD after analysis]
- **Average Recall:** [TBD]
- **Best Performer:** PR #[TBD] - [reason]
- **Weakest Performer:** PR #[TBD] - [reason]

## Key Patterns

### TestBot Strengths

What did TestBot consistently do well across all/most PRs?

- [ ] Basic test function generation (test_ naming)
- [ ] Simple assertions (assertEquals, assertTrue)
- [ ] Fixture identification and usage
- [ ] Edge case detection
- [ ] Mock/patch usage
- [ ] Parametrization
- [ ] Other: _______

### TestBot Gaps

What did TestBot consistently miss or struggle with?

- [ ] Complex assertion chains
- [ ] Context manager usage
- [ ] Async test patterns
- [ ] Integration test setup
- [ ] Specific edge cases
- [ ] Other: _______

### Specific Examples

#### Example 1: [Description]
- PR: #[number]
- Ground truth did: [description]
- TestBot generated: [description]
- Gap: [what was missed]

#### Example 2: [Description]
[Similar structure]

## Quality Observations

### Generated Tests Quality
- Do generated tests run without errors?
- Are they syntactically correct?
- Do they follow pytest conventions?
- Do they use appropriate fixtures?

### Comparison Methodology
- Does the scoring make sense?
- Are there metrics we should add?
- Are there false matches/misses?

## Recommendations

### For TestBot Improvement
1. [Specific recommendation based on gaps]
2. [Specific recommendation based on patterns]
3. [etc.]

### For Methodology Refinement
1. [Any changes needed to evaluation approach?]
2. [Scoring weight adjustments?]
3. [Additional metrics?]

## Decision: Proceed to Tier 2?

- [ ] Yes - methodology validated, results consistent
- [ ] No - need to address [specific issues] first
- [ ] Partial - proceed with caution, monitor [specific concerns]
EOF

# Open for manual editing and analysis
code results/tier1-findings.md
```

**Manual analysis required:**
Review each evaluation report and fill in the findings document with actual observations.

---

### Step 2.4: Checkpoint Decision

**Decision point:** Based on Tier 1 findings, decide next steps:

✅ **Proceed to Tier 2** if:
- Pipeline ran smoothly for all 5 PRs
- Results are consistent and make sense
- No critical methodology issues found

⚠️ **Iterate on methodology** if:
- Scoring seems off (too harsh or too lenient)
- Missing important comparison dimensions
- Comparison script has bugs

🛑 **Pause and investigate** if:
- TestBot failed on multiple PRs
- Results are inconsistent or confusing
- Infrastructure issues blocking evaluation

---

## Phase 3: Tier 2 Execution

**Goal:** Evaluate TestBot on medium-complexity PRs with cross-system changes.

### Step 3.1: Run Tier 2 PRs

**Tier 2 PRs (6 total):**
- PR #21436 - Schedule persistence fix (504 lines, 9 test files)
- PR #21365 - Worker attribution fix (205 lines, 3 test files)
- PR #21350 - Parameter size limit (151 lines, 4 test files)
- PR #21354 - ECS retry enhancement (119 lines, 1 test file)
- PR #20951 - Concurrency API change (160 lines, 1 test file)
- PR #21304 - Subprocess logging (265 lines, 2 test files)

**Actions:**
```bash
cd /Users/syedsky/Skyramp/content/product/features/testbot/testing/forks/prefect-testbot-eval

# Run all Tier 2 PRs
./replay-eval/run_evaluation.sh --tier 2
```

**Expected duration:** 3-4 hours

**Expected outcome:**
- 6 complete evaluation results
- Patterns emerge for more complex changes

---

### Step 3.2: Generate Tier 2 Summary

**Actions:**
```bash
# Generate summary
python3 replay-eval/summarize_tier.py 2 > results/tier2-summary.md

# View results
cat results/tier2-summary.md
```

---

### Step 3.3: Compare Tier 1 vs Tier 2

**Actions:**
Analyze if complexity affects TestBot performance:

```bash
cat > results/tier1-vs-tier2-comparison.md <<'EOF'
# Tier 1 vs Tier 2 Comparison

## Hypothesis
TestBot performance may degrade with increased complexity (more files, cross-system changes).

## Results

| Metric | Tier 1 (Simple) | Tier 2 (Medium) | Delta |
|--------|----------------|----------------|-------|
| Avg Score | [TBD] | [TBD] | [TBD] |
| Avg Recall | [TBD] | [TBD] | [TBD] |
| Avg Test Count Ratio | [TBD] | [TBD] | [TBD] |

## Observations

### Complexity Impact
- Does performance degrade with more files?
- Does cross-system complexity affect quality?
- Are integration tests harder for TestBot?

### New Patterns in Tier 2
[Document any new patterns not seen in Tier 1]

## Recommendations for Tier 3
[Based on Tier 2 results, any concerns for large refactors?]
EOF

code results/tier1-vs-tier2-comparison.md
```

---

## Phase 4: Tier 3 and Bonus PRs

### Step 4.1: Run Tier 3 (Large Refactors)

**Tier 3 PRs (2 total):**
- PR #21286 - BuildKit support (1073 lines, 4 test files, 8 source files)
- PR #21252 - Remove Runner usage (731 lines, 11 test files, 15 source files)

**Actions:**
```bash
./replay-eval/run_evaluation.sh --tier 3
```

**Expected duration:** 1-2 hours

**Note:** These are stress tests - TestBot may struggle with very large changes.

---

### Step 4.2: Optional Bonus PRs

**Only if time permits and results are interesting:**

```bash
./replay-eval/run_evaluation.sh --tier bonus
```

Bonus PRs (4 total): 21273, 21033, 21231, 21211

---

## Phase 5: Final Analysis and Report

### Step 5.1: Generate Comprehensive Summary

**Actions:**
```bash
cd /Users/syedsky/Skyramp/content/product/features/testbot/testing/forks/prefect-testbot-eval

# Generate summary across all tiers
cat > results/FINAL-EVALUATION-REPORT.md <<'EOF'
# TestBot Replay-and-Diff Evaluation - Final Report

**Evaluation Period:** [dates]
**Repository:** sxarsky/prefect-testbot-eval
**Methodology:** Replay-and-diff using PrefectHQ/prefect PRs as ground truth

---

## Executive Summary

Total PRs evaluated: [N]
- Tier 1 (Simple): 5 PRs
- Tier 2 (Medium): 6 PRs
- Tier 3 (Large): 2 PRs
- Bonus: [N] PRs

**Key Finding:** [1-2 sentence summary of main insight]

---

## Methodology

[Briefly describe the replay-and-diff approach]

---

## Results by Tier

### Tier 1: Small, Focused Changes
[Include tier1-summary.md content]

### Tier 2: Medium Complexity
[Include tier2-summary.md content]

### Tier 3: Large Refactors
[Include tier3 results]

---

## Overall Performance Metrics

| Metric | Mean | Median | Min | Max |
|--------|------|--------|-----|-----|
| Structural Similarity | [TBD] | [TBD] | [TBD] | [TBD] |
| Function Recall | [TBD] | [TBD] | [TBD] | [TBD] |
| Test Count Ratio | [TBD] | [TBD] | [TBD] | [TBD] |
| Assertion Density | [TBD] | [TBD] | [TBD] | [TBD] |

---

## Key Findings

### TestBot Strengths
1. [Specific strength with examples]
2. [Specific strength with examples]
3. [etc.]

### TestBot Limitations
1. [Specific limitation with examples]
2. [Specific limitation with examples]
3. [etc.]

### Impact of PR Complexity
[How does TestBot perform as PR complexity increases?]

---

## Recommendations

### For TestBot Product Team
1. **High Priority:** [Recommendation based on critical gaps]
2. **Medium Priority:** [Recommendation for improvements]
3. **Low Priority:** [Nice-to-have enhancements]

### For Evaluation Methodology
[How can this evaluation be improved for future runs?]

---

## Appendix: Individual PR Results

[Table with link to each PR's evaluation report]

---

## Reproducibility

This evaluation can be reproduced or extended:

```bash
git clone https://github.com/sxarsky/prefect-testbot-eval.git
cd prefect-testbot-eval
./replay-eval/run_evaluation.sh --tier 1
```

All scripts, patches, and results are preserved in this repository.
EOF

code results/FINAL-EVALUATION-REPORT.md
```

---

### Step 5.2: Archive and Preserve Results

**Actions:**
```bash
cd /Users/syedsky/Skyramp/content/product/features/testbot/testing/forks/prefect-testbot-eval

# Create timestamped archive
tar -czf ../testbot-eval-results-$(date +%Y%m%d).tar.gz \
    results/ \
    patches/ \
    replay-eval/

# Commit all results to repo
git add results/ patches/
git commit -m "TestBot replay-and-diff evaluation results - $(date +%Y-%m-%d)"
git push origin main

# Create a release tag
git tag -a v1.0-evaluation -m "Complete replay-and-diff evaluation - $(date +%Y-%m-%d)"
git push origin v1.0-evaluation
```

**Expected outcome:**
- All results preserved in git repository
- Tarball backup created
- Easy to share and reference

---

## Quick Reference

### Running Individual PRs
```bash
./replay-eval/run_evaluation.sh <PR_NUMBER>
```

### Running by Tier
```bash
./replay-eval/run_evaluation.sh --tier 1  # or 2, 3, bonus
```

### Running All PRs
```bash
./replay-eval/run_evaluation.sh --all
```

### Resuming Interrupted Runs
```bash
# Skip to a specific step
./replay-eval/run_evaluation.sh <PR_NUMBER> --skip-to collect
# Steps: extract, prepare, trigger, collect, compare
```

### Dry Run (Preview)
```bash
./replay-eval/run_evaluation.sh --tier 1 --dry-run
```

---

## Timeline Estimate

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Phase 0: Setup | 2-3 hours | Configured fork with TestBot |
| Phase 1: Validation | 4-6 hours | Pipeline proven with PR #21267 |
| Phase 2: Tier 1 | 1-2 days | 5 PRs evaluated, baseline metrics |
| Phase 3: Tier 2 | 1-2 days | 6 more PRs, cross-system analysis |
| Phase 4: Tier 3+Bonus | 1 day | Large PRs, specialized cases |
| Phase 5: Final Report | 1 day | Comprehensive analysis document |
| **Total** | **~1-2 weeks** | Complete quantitative evaluation |

---

## Success Criteria

This evaluation is successful if it produces:

1. ✅ **Quantitative baseline** - Coverage parity and structural similarity scores for each PR
2. ✅ **Pattern analysis** - Clear documentation of TestBot strengths and gaps
3. ✅ **Actionable findings** - Specific recommendations for product improvements
4. ✅ **Reproducible pipeline** - Can be re-run with future TestBot versions

---

## Notes and Observations

[Space for capturing ad-hoc observations during execution]

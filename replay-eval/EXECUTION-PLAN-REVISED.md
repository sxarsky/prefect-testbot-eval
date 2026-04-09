# TestBot Replay-and-Diff Evaluation - Execution Plan (Revised)

**Created:** 2026-04-08
**Revised:** 2026-04-08
**Owner:** Syed
**Goal:** Quantitatively evaluate TestBot's test generation quality against human-written tests from real PRs

---

## Overview

This plan executes the replay-and-diff methodology using a **copy of the existing `sxarsky/prefect-testb` fork**. Since GitHub doesn't allow two forks of the same upstream repo under one account, we'll clone the existing fork and push it to a new repo called `prefect-testbot-eval`.

**Why copy prefect-testb instead of forking upstream?**
- ✅ TestBot already configured and working
- ✅ All secrets and workflows already set up
- ✅ Proven infrastructure
- ✅ Clean isolation for evaluation work

---

## Phase 0: Repository Setup & Infrastructure

**Goal:** Create a copy of prefect-testb with TestBot infrastructure ready to run.

### Step 0.1: Create New Empty Repository on GitHub

**Actions:**
Use `gh` CLI to create the new repository:

```bash
# Create new empty repository
gh repo create sxarsky/prefect-testbot-eval \
  --public \
  --description "TestBot replay-and-diff evaluation - comparing generated vs human tests" \
  --clone=false
```

**Expected outcome:**
- New empty repository at `https://github.com/sxarsky/prefect-testbot-eval`
- No code yet, just an empty repo

**Verification:**
```bash
gh repo view sxarsky/prefect-testbot-eval --json name,description
```

---

### Step 0.2: Clone Existing prefect-testb Repository

**Actions:**
```bash
# Navigate to forks directory
cd /Users/syedsky/Skyramp/content/product/features/testbot/testing/forks/

# Clone the existing prefect-testb fork
git clone https://github.com/sxarsky/prefect-testb.git prefect-testbot-eval-temp
cd prefect-testbot-eval-temp

# Verify we have the right repo
git remote -v
# Should show origin pointing to prefect-testb
```

**Expected outcome:**
- Local clone of prefect-testb at `prefect-testbot-eval-temp/`
- All history, branches, and configuration included

**Verification:**
```bash
# Check we have TestBot workflow
ls -la .github/workflows/skyramp-testbot.yml

# Check recent commits
git log --oneline -3
```

---

### Step 0.3: Update Remotes and Push to New Repository

**Actions:**
```bash
cd /Users/syedsky/Skyramp/content/product/features/testbot/testing/forks/prefect-testbot-eval-temp

# Remove old origin (pointing to prefect-testb)
git remote remove origin

# Add new origin (pointing to prefect-testbot-eval)
git remote add origin https://github.com/sxarsky/prefect-testbot-eval.git

# Verify remote is correct
git remote -v

# Push all branches and tags to new repo
git push origin --all
git push origin --tags

# Verify upstream remote exists (needed by extraction scripts)
git remote -v | grep upstream || git remote add upstream https://github.com/PrefectHQ/prefect.git

# Fetch latest from upstream
git fetch upstream main
```

**Expected outcome:**
- All code pushed to new `prefect-testbot-eval` repository
- Remote `origin` points to new repo
- Remote `upstream` points to PrefectHQ/prefect

**Verification:**
```bash
# Check remotes
git remote -v
# origin    https://github.com/sxarsky/prefect-testbot-eval.git
# upstream  https://github.com/PrefectHQ/prefect.git

# Verify push succeeded
gh repo view sxarsky/prefect-testbot-eval --json pushedAt
```

---

### Step 0.4: Rename Directory and Clean Up

**Actions:**
```bash
cd /Users/syedsky/Skyramp/content/product/features/testbot/testing/forks/

# Rename the temp directory
mv prefect-testbot-eval-temp prefect-testbot-eval

# Verify
cd prefect-testbot-eval
pwd
# Should be: /Users/syedsky/Skyramp/content/product/features/testbot/testing/forks/prefect-testbot-eval
```

**Expected outcome:**
- Working directory properly named
- Clean setup ready for evaluation work

---

### Step 0.5: Configure GitHub Secrets

**Actions:**
The new repository needs the same secrets as prefect-testb. You have two options:

**Option A: Copy via gh CLI (if supported)**
```bash
# List secrets from old repo
gh secret list --repo sxarsky/prefect-testb

# Copy each secret (requires secret values - may need manual)
# This will require you to input the secret values
gh secret set SKYRAMP_LICENSE --repo sxarsky/prefect-testbot-eval
# ... repeat for other secrets
```

**Option B: Manual via Web UI**
1. Get secret values from: https://github.com/sxarsky/prefect-testb/settings/secrets/actions
2. Set in new repo at: https://github.com/sxarsky/prefect-testbot-eval/settings/secrets/actions
3. Required secrets:
   - `SKYRAMP_LICENSE`
   - Any other secrets used by the TestBot workflow

**Expected outcome:**
- All required secrets configured in new repository
- TestBot workflow can access credentials

**Verification:**
```bash
# List configured secrets (names only, values hidden)
gh api repos/sxarsky/prefect-testbot-eval/actions/secrets --jq '.secrets[].name'
```

---

### Step 0.6: Copy and Update Evaluation Scripts

**Actions:**
```bash
cd /Users/syedsky/Skyramp/content/product/features/testbot/testing/forks/prefect-testbot-eval

# Copy the replay-eval directory
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
- `replay-eval/` directory copied to new repo
- All scripts executable
- FORK_REPO variable updated to `sxarsky/prefect-testbot-eval`

**Verification:**
```bash
# Check scripts exist and are executable
ls -la replay-eval/*.sh

# Verify FORK_REPO update
grep "FORK_REPO" replay-eval/*.sh | grep "prefect-testbot-eval"
```

---

### Step 0.7: Validate Prerequisites

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

# 3. New repo access
echo "3. New repo access:"
gh repo view sxarsky/prefect-testbot-eval --json name -q .name

# 4. Push access to new repo
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

# 8. Remotes configured correctly
echo "8. Git remotes:"
git remote -v
```

**Expected outcome:**
- All checks pass without errors
- gh CLI is authenticated
- Python 3.8+ is available
- TestBot workflow is configured
- Scripts are executable
- Both remotes configured (origin = new repo, upstream = PrefectHQ/prefect)

**Verification:**
All commands above should complete without errors.

---

## Phase 1: Infrastructure Validation

[Rest of the plan remains the same as original EXECUTION-PLAN.md, starting with Step 1.1: Extract Patches for PR #21267]

---

## Summary of Changes from Original Plan

**Original approach:** Fork PrefectHQ/prefect → Configure from scratch
**Revised approach:** Clone prefect-testb → Push to new repo → Already configured

**Benefits:**
- Faster setup (workflow already configured)
- Lower risk (known working configuration)
- Proven infrastructure
- Same secrets can be copied

**Trade-offs:**
- Need to manually copy secrets
- Slightly more complex git operations
- But overall simpler than configuring from scratch

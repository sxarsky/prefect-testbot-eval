#!/usr/bin/env bash
# prepare_replay.sh - Create replay branches with code-only changes
#
# Usage: ./prepare_replay.sh <PR_NUMBER> [PATCHES_DIR]
#
# Creates a branch from the pre-PR state with only code changes applied
# (no tests), ready to be pushed and trigger TestBot.
#
# Prerequisites:
#   - extract_patches.sh has been run for this PR
#   - Run from within the prefect-testb fork directory

set -euo pipefail

PR_NUMBER="${1:?Usage: $0 <PR_NUMBER> [PATCHES_DIR]}"
PATCHES_DIR="${2:-./patches/pr${PR_NUMBER}}"

echo "=== Preparing replay branch for PR #${PR_NUMBER} ==="

# Validate prerequisites
if [ ! -f "${PATCHES_DIR}/metadata.json" ]; then
    echo "ERROR: Patches not found. Run extract_patches.sh first."
    echo "Expected: ${PATCHES_DIR}/metadata.json"
    exit 1
fi

if [ ! -f "${PATCHES_DIR}/code-only.patch" ]; then
    echo "ERROR: Code-only patch not found at ${PATCHES_DIR}/code-only.patch"
    exit 1
fi

BASE_COMMIT=$(cat "${PATCHES_DIR}/base_commit.txt")
PR_TITLE=$(jq -r '.title' "${PATCHES_DIR}/metadata.json")
BRANCH_NAME="replay/pr${PR_NUMBER}"

echo "Base commit: ${BASE_COMMIT}"
echo "Branch: ${BRANCH_NAME}"
echo "Title: ${PR_TITLE}"

# Check if branch already exists
if git rev-parse --verify "${BRANCH_NAME}" >/dev/null 2>&1; then
    echo ""
    echo "WARNING: Branch ${BRANCH_NAME} already exists."
    read -p "Delete and recreate? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git branch -D "${BRANCH_NAME}"
    else
        echo "Aborting."
        exit 1
    fi
fi

# Step 1: Create branch from base commit
echo ""
echo "--- Step 1: Creating branch from pre-PR state ---"
git checkout "${BASE_COMMIT}" --detach 2>/dev/null
git checkout -b "${BRANCH_NAME}"
echo "Created branch ${BRANCH_NAME} at $(git rev-parse --short HEAD)"

# Step 2: Apply code-only patch
echo ""
echo "--- Step 2: Applying code-only patch ---"
PATCH_SIZE=$(wc -l < "${PATCHES_DIR}/code-only.patch" | tr -d ' ')

if [ "${PATCH_SIZE}" -eq 0 ]; then
    echo "WARNING: Code-only patch is empty. No code changes to apply."
    echo "This PR may have only test changes."
    exit 1
fi

# Try to apply the patch
if git apply --check "${PATCHES_DIR}/code-only.patch" 2>/dev/null; then
    git apply "${PATCHES_DIR}/code-only.patch"
    echo "Patch applied cleanly."
else
    echo "Clean apply failed. Trying with 3-way merge..."
    if git apply --3way "${PATCHES_DIR}/code-only.patch" 2>/dev/null; then
        echo "Patch applied with 3-way merge."
    else
        echo "ERROR: Patch could not be applied."
        echo "This likely means the base commit doesn't match expectations."
        echo ""
        echo "Manual resolution needed. The patch is at:"
        echo "  ${PATCHES_DIR}/code-only.patch"
        echo ""
        echo "Try: git apply --reject ${PATCHES_DIR}/code-only.patch"
        git checkout main 2>/dev/null || git checkout - 2>/dev/null
        git branch -D "${BRANCH_NAME}" 2>/dev/null || true
        exit 1
    fi
fi

# Step 3: Commit the code-only changes
echo ""
echo "--- Step 3: Committing code-only changes ---"
git add -A
git commit -m "$(cat <<EOF
Replay PR #${PR_NUMBER}: ${PR_TITLE}

Code-only replay for TestBot evaluation.
Tests have been stripped - TestBot should generate them.

Original PR: https://github.com/PrefectHQ/prefect/pull/${PR_NUMBER}
Evaluation methodology: replay-and-diff
EOF
)"

echo ""
echo "=== Replay branch ready ==="
echo "Branch: ${BRANCH_NAME}"
echo "Commit: $(git rev-parse --short HEAD)"
echo "Files changed: $(git diff --stat HEAD~1 | tail -1)"
echo ""
echo "Next steps:"
echo "  1. Push:  git push origin ${BRANCH_NAME}"
echo "  2. Create PR:  gh pr create --title 'Replay PR #${PR_NUMBER}: ${PR_TITLE}'"
echo "  3. Wait for TestBot to run (~10-15 min)"
echo "  4. Collect results with collect_results.sh"
echo ""
echo "Or run: ./trigger_testbot.sh ${PR_NUMBER}"

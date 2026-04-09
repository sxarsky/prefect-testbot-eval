#!/usr/bin/env bash
# trigger_testbot.sh - Push replay branch and open PR to trigger TestBot
#
# Usage: ./trigger_testbot.sh <PR_NUMBER> [--wait]
#
# Pushes the prepared replay branch and creates a PR on the fork.
# With --wait, polls until TestBot has completed.
#
# Prerequisites:
#   - prepare_replay.sh has been run for this PR
#   - gh CLI authenticated with push access to the fork

set -euo pipefail

FORK_REPO="sxarsky/prefect-testbot-eval"
UPSTREAM_REPO="PrefectHQ/prefect"

PR_NUMBER="${1:?Usage: $0 <PR_NUMBER> [--wait]}"
WAIT_FLAG="${2:-}"
PATCHES_DIR="./patches/pr${PR_NUMBER}"
BRANCH_NAME="replay/pr${PR_NUMBER}"

echo "=== Triggering TestBot for PR #${PR_NUMBER} ==="

# Validate
if ! git rev-parse --verify "${BRANCH_NAME}" >/dev/null 2>&1; then
    echo "ERROR: Branch ${BRANCH_NAME} not found. Run prepare_replay.sh first."
    exit 1
fi

PR_TITLE=$(jq -r '.title' "${PATCHES_DIR}/metadata.json" 2>/dev/null || echo "PR #${PR_NUMBER}")

# Step 1: Push the branch
echo ""
echo "--- Step 1: Pushing replay branch ---"
git push origin "${BRANCH_NAME}" --force-with-lease 2>/dev/null || \
    git push origin "${BRANCH_NAME}" --force

echo "Pushed ${BRANCH_NAME} to origin"

# Step 2: Create the PR
echo ""
echo "--- Step 2: Creating PR ---"

# Check if PR already exists for this branch
EXISTING_PR=$(gh pr list --repo "${FORK_REPO}" --head "${BRANCH_NAME}" --json number -q '.[0].number' 2>/dev/null || echo "")

if [ -n "${EXISTING_PR}" ]; then
    echo "PR #${EXISTING_PR} already exists for branch ${BRANCH_NAME}"
    FORK_PR_NUMBER="${EXISTING_PR}"
else
    FORK_PR_NUMBER=$(gh pr create \
        --repo "${FORK_REPO}" \
        --title "Replay PR #${PR_NUMBER}: ${PR_TITLE}" \
        --body "$(cat <<BODYEOF
## TestBot Evaluation: Replay-and-Diff

**Original PR:** https://github.com/${UPSTREAM_REPO}/pull/${PR_NUMBER}
**Methodology:** Code-only replay (tests stripped for TestBot to generate)

### What This Is

This PR replays the code changes from PrefectHQ/prefect#${PR_NUMBER} without any test files.
TestBot should analyze these changes and generate appropriate tests.

The generated tests will be compared against the human-written tests from the original PR
to evaluate TestBot's test generation quality.

### Evaluation Dimensions
- Coverage parity (do generated tests cover the same code paths?)
- Bug detection (do generated tests catch the same faults?)
- Structural similarity (test organization, assertions, mocks)

---
*Automated replay for TestBot evaluation pipeline*
BODYEOF
)" \
        --head "${BRANCH_NAME}" \
        2>&1 | grep -oP '\d+$' || echo "")

    if [ -z "${FORK_PR_NUMBER}" ]; then
        # Try to extract PR number from URL output
        FORK_PR_NUMBER=$(gh pr list --repo "${FORK_REPO}" --head "${BRANCH_NAME}" --json number -q '.[0].number' 2>/dev/null || echo "unknown")
    fi

    echo "Created PR #${FORK_PR_NUMBER} on ${FORK_REPO}"
fi

# Save the fork PR number
echo "${FORK_PR_NUMBER}" > "${PATCHES_DIR}/fork_pr_number.txt"

# Step 3: Optionally wait for TestBot
if [ "${WAIT_FLAG}" = "--wait" ]; then
    echo ""
    echo "--- Step 3: Waiting for TestBot ---"
    echo "Polling every 60 seconds for TestBot completion..."

    MAX_WAIT=1200  # 20 minutes
    ELAPSED=0

    while [ ${ELAPSED} -lt ${MAX_WAIT} ]; do
        # Check for TestBot commits on the PR
        TESTBOT_COMMITS=$(gh pr view "${FORK_PR_NUMBER}" --repo "${FORK_REPO}" \
            --json commits -q '.commits[] | select(.messageHeadline | test("(?i)testbot|skyramp")) | .oid' 2>/dev/null || echo "")

        if [ -n "${TESTBOT_COMMITS}" ]; then
            echo ""
            echo "TestBot has committed! Commits:"
            echo "${TESTBOT_COMMITS}"
            break
        fi

        # Check workflow runs
        WORKFLOW_STATUS=$(gh run list --repo "${FORK_REPO}" --branch "${BRANCH_NAME}" \
            --limit 1 --json status,conclusion -q '.[0].status' 2>/dev/null || echo "unknown")

        echo "  [${ELAPSED}s] Workflow status: ${WORKFLOW_STATUS}"

        sleep 60
        ELAPSED=$((ELAPSED + 60))
    done

    if [ ${ELAPSED} -ge ${MAX_WAIT} ]; then
        echo ""
        echo "WARNING: Timed out waiting for TestBot (${MAX_WAIT}s)"
        echo "Check the PR manually: https://github.com/${FORK_REPO}/pull/${FORK_PR_NUMBER}"
    fi
fi

echo ""
echo "=== Done ==="
echo "Fork PR: https://github.com/${FORK_REPO}/pull/${FORK_PR_NUMBER}"
echo "Original PR: https://github.com/${UPSTREAM_REPO}/pull/${PR_NUMBER}"
echo ""
echo "Next: After TestBot completes, run:"
echo "  ./collect_results.sh ${PR_NUMBER}"

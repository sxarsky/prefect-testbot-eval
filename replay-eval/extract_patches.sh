#!/usr/bin/env bash
# extract_patches.sh - Extract code-only and test-only patches from upstream PRs
#
# Usage: ./extract_patches.sh <PR_NUMBER> [OUTPUT_DIR]
#
# Extracts two separate patches from a PrefectHQ/prefect PR:
#   1. code-only patch (all non-test file changes)
#   2. test-only patch (all test file changes = ground truth)
#
# Prerequisites:
#   - gh CLI authenticated
#   - git available
#   - Run from within the prefect-testb fork directory

set -euo pipefail

UPSTREAM_REPO="PrefectHQ/prefect"
FORK_REPO="sxarsky/prefect-testbot-eval"

# Test file path patterns (Prefect's test layout)
TEST_PATTERNS=(
    "tests/"
    "*/tests/"
    "**/tests/"
)

PR_NUMBER="${1:?Usage: $0 <PR_NUMBER> [OUTPUT_DIR]}"
OUTPUT_DIR="${2:-./patches/pr${PR_NUMBER}}"

echo "=== Extracting patches for PR #${PR_NUMBER} ==="
echo "Output directory: ${OUTPUT_DIR}"

mkdir -p "${OUTPUT_DIR}"

# Step 1: Get PR metadata
echo ""
echo "--- Step 1: Fetching PR metadata ---"
PR_JSON=$(gh pr view "${PR_NUMBER}" --repo "${UPSTREAM_REPO}" \
    --json title,mergeCommit,baseRefOid,headRefOid,files,mergedAt,body)

PR_TITLE=$(echo "${PR_JSON}" | jq -r '.title')
MERGE_COMMIT=$(echo "${PR_JSON}" | jq -r '.mergeCommit.oid')
MERGED_AT=$(echo "${PR_JSON}" | jq -r '.mergedAt')

echo "Title: ${PR_TITLE}"
echo "Merge commit: ${MERGE_COMMIT}"
echo "Merged at: ${MERGED_AT}"

# Save metadata
cat > "${OUTPUT_DIR}/metadata.json" <<METAEOF
{
    "pr_number": ${PR_NUMBER},
    "title": "${PR_TITLE}",
    "merge_commit": "${MERGE_COMMIT}",
    "merged_at": "${MERGED_AT}",
    "upstream_repo": "${UPSTREAM_REPO}",
    "extracted_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
METAEOF

# Step 2: Ensure we have the upstream remote and the merge commit
echo ""
echo "--- Step 2: Fetching upstream commits ---"
if ! git remote | grep -q "^upstream$"; then
    echo "Adding upstream remote..."
    git remote add upstream "https://github.com/${UPSTREAM_REPO}.git" 2>/dev/null || true
fi

git fetch upstream "${MERGE_COMMIT}" --depth=50 2>/dev/null || {
    echo "Shallow fetch failed, trying full fetch of main..."
    git fetch upstream main --depth=200
}

# Step 3: Identify the parent commit (pre-PR state)
echo ""
echo "--- Step 3: Identifying base commit ---"
# The merge commit's first parent is the state of main before the PR
BASE_COMMIT=$(git rev-parse "${MERGE_COMMIT}^" 2>/dev/null || echo "")

if [ -z "${BASE_COMMIT}" ]; then
    echo "ERROR: Could not find parent of merge commit ${MERGE_COMMIT}"
    echo "This might be a squash-merge. Trying alternative approach..."
    # For squash merges, use the baseRefOid from the PR
    BASE_COMMIT=$(echo "${PR_JSON}" | jq -r '.baseRefOid')
    if [ "${BASE_COMMIT}" = "null" ] || [ -z "${BASE_COMMIT}" ]; then
        echo "FATAL: Cannot determine base commit for PR #${PR_NUMBER}"
        exit 1
    fi
fi

echo "Base commit (pre-PR): ${BASE_COMMIT}"
echo "${BASE_COMMIT}" > "${OUTPUT_DIR}/base_commit.txt"

# Step 4: Get the full diff
echo ""
echo "--- Step 4: Generating full diff ---"
FULL_DIFF=$(git diff "${BASE_COMMIT}..${MERGE_COMMIT}" 2>/dev/null || {
    echo "Direct diff failed. Fetching more history..."
    git fetch upstream --deepen=100
    git diff "${BASE_COMMIT}..${MERGE_COMMIT}"
})

echo "${FULL_DIFF}" > "${OUTPUT_DIR}/full.patch"
echo "Full patch: $(echo "${FULL_DIFF}" | grep "^diff --git" | wc -l) files"

# Step 5: Separate into code-only and test-only patches
echo ""
echo "--- Step 5: Separating code and test patches ---"

# List all changed files
CHANGED_FILES=$(git diff --name-only "${BASE_COMMIT}..${MERGE_COMMIT}")

# Classify files as test or code
TEST_FILES=""
CODE_FILES=""

while IFS= read -r file; do
    [ -z "$file" ] && continue
    is_test=false

    # Check if file is in a test directory or is a test file
    if echo "$file" | grep -qE "(^tests/|/tests/|_test\.py$|test_[^/]*\.py$|conftest\.py$)"; then
        is_test=true
    fi

    if $is_test; then
        TEST_FILES="${TEST_FILES}${file}\n"
    else
        CODE_FILES="${CODE_FILES}${file}\n"
    fi
done <<< "${CHANGED_FILES}"

echo ""
echo "Test files:"
echo -e "${TEST_FILES}" | grep -v "^$" | while read -r f; do echo "  [TEST] $f"; done

echo ""
echo "Code files:"
echo -e "${CODE_FILES}" | grep -v "^$" | while read -r f; do echo "  [CODE] $f"; done

# Save file lists
echo -e "${TEST_FILES}" | grep -v "^$" > "${OUTPUT_DIR}/test_files.txt" 2>/dev/null || touch "${OUTPUT_DIR}/test_files.txt"
echo -e "${CODE_FILES}" | grep -v "^$" > "${OUTPUT_DIR}/code_files.txt" 2>/dev/null || touch "${OUTPUT_DIR}/code_files.txt"

# Generate code-only patch
if [ -s "${OUTPUT_DIR}/code_files.txt" ]; then
    CODE_PATHS=$(cat "${OUTPUT_DIR}/code_files.txt" | tr '\n' ' ')
    git diff "${BASE_COMMIT}..${MERGE_COMMIT}" -- ${CODE_PATHS} > "${OUTPUT_DIR}/code-only.patch"
    echo ""
    echo "Code-only patch: $(grep "^diff --git" "${OUTPUT_DIR}/code-only.patch" | wc -l) files"
else
    touch "${OUTPUT_DIR}/code-only.patch"
    echo "WARNING: No code files found in PR"
fi

# Generate test-only patch (ground truth)
if [ -s "${OUTPUT_DIR}/test_files.txt" ]; then
    TEST_PATHS=$(cat "${OUTPUT_DIR}/test_files.txt" | tr '\n' ' ')
    git diff "${BASE_COMMIT}..${MERGE_COMMIT}" -- ${TEST_PATHS} > "${OUTPUT_DIR}/test-ground-truth.patch"
    echo "Test-only patch (ground truth): $(grep "^diff --git" "${OUTPUT_DIR}/test-ground-truth.patch" | wc -l) files"
else
    touch "${OUTPUT_DIR}/test-ground-truth.patch"
    echo "WARNING: No test files found in PR"
fi

# Step 6: Extract the actual ground truth test file contents (post-PR state)
echo ""
echo "--- Step 6: Extracting ground truth test file contents ---"
GROUND_TRUTH_DIR="${OUTPUT_DIR}/ground-truth"
mkdir -p "${GROUND_TRUTH_DIR}"

while IFS= read -r test_file; do
    [ -z "$test_file" ] && continue
    # Create directory structure
    mkdir -p "${GROUND_TRUTH_DIR}/$(dirname "$test_file")"
    # Extract file content at the merge commit
    git show "${MERGE_COMMIT}:${test_file}" > "${GROUND_TRUTH_DIR}/${test_file}" 2>/dev/null || {
        echo "  WARNING: Could not extract ${test_file} at ${MERGE_COMMIT}"
    }
done < "${OUTPUT_DIR}/test_files.txt"

echo "Ground truth files saved to: ${GROUND_TRUTH_DIR}"

# Summary
echo ""
echo "=== Extraction Complete ==="
echo "PR #${PR_NUMBER}: ${PR_TITLE}"
echo ""
echo "Files created:"
echo "  ${OUTPUT_DIR}/metadata.json       - PR metadata"
echo "  ${OUTPUT_DIR}/base_commit.txt     - Pre-PR commit hash"
echo "  ${OUTPUT_DIR}/full.patch          - Complete PR diff"
echo "  ${OUTPUT_DIR}/code-only.patch     - Code changes only (for replay)"
echo "  ${OUTPUT_DIR}/test-ground-truth.patch - Test changes only (ground truth)"
echo "  ${OUTPUT_DIR}/code_files.txt      - List of changed code files"
echo "  ${OUTPUT_DIR}/test_files.txt      - List of changed test files"
echo "  ${OUTPUT_DIR}/ground-truth/       - Full test file contents at merge"
echo ""
echo "Code files: $(wc -l < "${OUTPUT_DIR}/code_files.txt" | tr -d ' ')"
echo "Test files: $(wc -l < "${OUTPUT_DIR}/test_files.txt" | tr -d ' ')"
echo "Code patch size: $(wc -l < "${OUTPUT_DIR}/code-only.patch" | tr -d ' ') lines"
echo "Test patch size: $(wc -l < "${OUTPUT_DIR}/test-ground-truth.patch" | tr -d ' ') lines"

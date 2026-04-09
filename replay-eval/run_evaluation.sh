#!/usr/bin/env bash
# run_evaluation.sh - End-to-end orchestrator for the replay-and-diff pipeline
#
# Usage: ./run_evaluation.sh <PR_NUMBER> [--all-tiers] [--tier N]
#
# Runs the full pipeline for a single PR or a tier of PRs:
#   1. extract_patches.sh  - Get code-only and test-only diffs
#   2. prepare_replay.sh   - Create replay branch
#   3. trigger_testbot.sh  - Push and create PR (triggers TestBot)
#   4. collect_results.sh  - Gather TestBot output
#   5. compare_tests.py    - Run comparison analysis
#
# Prerequisites:
#   - All scripts in this directory
#   - gh CLI authenticated
#   - Run from within the prefect-testb fork directory

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# PR tiers (from candidate analysis)
TIER1_PRS=(21267 21320 21307 21443 21356)
TIER2_PRS=(21436 21365 21350 21354 20951 21304)
TIER3_PRS=(21286 21252)
BONUS_PRS=(21273 21033 21231 21211)
ALL_PRS=("${TIER1_PRS[@]}" "${TIER2_PRS[@]}" "${TIER3_PRS[@]}" "${BONUS_PRS[@]}")

usage() {
    cat <<EOF
Usage: $0 <PR_NUMBER|--tier N|--all>

Run the complete replay-and-diff evaluation pipeline.

Options:
  <PR_NUMBER>     Run for a single PR
  --tier 1        Run all Tier 1 PRs (methodology validation)
  --tier 2        Run all Tier 2 PRs (medium complexity)
  --tier 3        Run all Tier 3 PRs (large refactors)
  --tier bonus    Run all Bonus PRs
  --all           Run all candidate PRs
  --dry-run       Show what would be done without executing
  --skip-to STEP  Skip to a specific step (extract|prepare|trigger|collect|compare)
  --help          Show this help

Examples:
  $0 21267                    # Run for a single small PR (good first test)
  $0 --tier 1                 # Run all 5 Tier 1 PRs
  $0 21443 --skip-to collect  # Skip to collection (TestBot already ran)
EOF
}

run_single_pr() {
    local pr=$1
    local skip_to="${2:-}"

    echo ""
    echo "################################################################"
    echo "# Evaluating PR #${pr}"
    echo "################################################################"
    echo ""

    local start_time=$(date +%s)

    # Step 1: Extract patches
    if [ -z "$skip_to" ] || [ "$skip_to" = "extract" ]; then
        echo ">>> Step 1/5: Extracting patches..."
        bash "${SCRIPT_DIR}/extract_patches.sh" "${pr}"
        echo ""
    fi

    # Step 2: Prepare replay branch
    if [ -z "$skip_to" ] || [ "$skip_to" = "extract" ] || [ "$skip_to" = "prepare" ]; then
        echo ">>> Step 2/5: Preparing replay branch..."
        bash "${SCRIPT_DIR}/prepare_replay.sh" "${pr}"
        echo ""
    fi

    # Step 3: Trigger TestBot
    if [ -z "$skip_to" ] || [ "$skip_to" = "extract" ] || [ "$skip_to" = "prepare" ] || [ "$skip_to" = "trigger" ]; then
        echo ">>> Step 3/5: Triggering TestBot..."
        bash "${SCRIPT_DIR}/trigger_testbot.sh" "${pr}" --wait
        echo ""
    fi

    # Step 4: Collect results
    if [ -z "$skip_to" ] || [ "$skip_to" = "collect" ]; then
        echo ">>> Step 4/5: Collecting results..."
        bash "${SCRIPT_DIR}/collect_results.sh" "${pr}"
        echo ""
    fi

    # Step 5: Run comparison
    echo ">>> Step 5/5: Running comparison..."
    python3 "${SCRIPT_DIR}/compare_tests.py" "${pr}"
    echo ""

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    echo "PR #${pr} completed in ${duration}s ($(( duration / 60 ))m $(( duration % 60 ))s)"
    echo ""

    # Return the comparison result path
    echo "results/replay/pr${pr}/comparison/evaluation_report.md"
}

run_tier() {
    local tier_name=$1
    shift
    local prs=("$@")

    echo "================================================================"
    echo "Running ${tier_name}: ${#prs[@]} PRs"
    echo "PRs: ${prs[*]}"
    echo "================================================================"

    local reports=()
    local start_time=$(date +%s)

    for pr in "${prs[@]}"; do
        report=$(run_single_pr "${pr}" "")
        reports+=("${report}")
    done

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    echo ""
    echo "================================================================"
    echo "${tier_name} Complete"
    echo "================================================================"
    echo "Total time: ${duration}s ($(( duration / 60 ))m $(( duration % 60 ))s)"
    echo "Reports generated:"
    for r in "${reports[@]}"; do
        echo "  - ${r}"
    done
}

# Parse arguments
DRY_RUN=false
SKIP_TO=""
TARGET=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            usage
            exit 0
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --skip-to)
            SKIP_TO="$2"
            shift 2
            ;;
        --tier)
            case $2 in
                1) TARGET="tier1" ;;
                2) TARGET="tier2" ;;
                3) TARGET="tier3" ;;
                bonus) TARGET="bonus" ;;
                *) echo "Unknown tier: $2"; exit 1 ;;
            esac
            shift 2
            ;;
        --all)
            TARGET="all"
            shift
            ;;
        *)
            if [[ $1 =~ ^[0-9]+$ ]]; then
                TARGET="single:$1"
            else
                echo "Unknown argument: $1"
                usage
                exit 1
            fi
            shift
            ;;
    esac
done

if [ -z "${TARGET}" ]; then
    usage
    exit 1
fi

# Execute
case $TARGET in
    single:*)
        PR_NUM="${TARGET#single:}"
        if $DRY_RUN; then
            echo "[DRY RUN] Would evaluate PR #${PR_NUM}"
        else
            run_single_pr "${PR_NUM}" "${SKIP_TO}"
        fi
        ;;
    tier1)
        if $DRY_RUN; then
            echo "[DRY RUN] Would evaluate Tier 1: ${TIER1_PRS[*]}"
        else
            run_tier "Tier 1 (Methodology Validation)" "${TIER1_PRS[@]}"
        fi
        ;;
    tier2)
        if $DRY_RUN; then
            echo "[DRY RUN] Would evaluate Tier 2: ${TIER2_PRS[*]}"
        else
            run_tier "Tier 2 (Medium Complexity)" "${TIER2_PRS[@]}"
        fi
        ;;
    tier3)
        if $DRY_RUN; then
            echo "[DRY RUN] Would evaluate Tier 3: ${TIER3_PRS[*]}"
        else
            run_tier "Tier 3 (Large Refactors)" "${TIER3_PRS[@]}"
        fi
        ;;
    bonus)
        if $DRY_RUN; then
            echo "[DRY RUN] Would evaluate Bonus: ${BONUS_PRS[*]}"
        else
            run_tier "Bonus (Specialized)" "${BONUS_PRS[@]}"
        fi
        ;;
    all)
        if $DRY_RUN; then
            echo "[DRY RUN] Would evaluate all ${#ALL_PRS[@]} PRs"
        else
            run_tier "Full Evaluation" "${ALL_PRS[@]}"
        fi
        ;;
esac

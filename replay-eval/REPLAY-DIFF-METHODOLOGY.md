# TestBot Replay-and-Diff Evaluation Methodology

**Created:** 2026-04-08
**Target Repo:** PrefectHQ/prefect (fork: sxarsky/prefect-testb)
**Status:** Implementation Plan

---

## 1. Overview

This document describes a quantitative, repeatable methodology for evaluating TestBot's test generation quality by comparing its output against human-written tests from real PRs in the PrefectHQ/prefect repository.

### Core Idea

Use existing human-written tests as ground truth. For each target PR:

1. Capture the human-written tests as the benchmark
2. Revert the repo to the pre-PR state
3. Replay the code-only changes (no tests) through TestBot
4. Compare TestBot's generated tests against the human originals

This gives us an objective, quantitative measure of TestBot's test generation quality across multiple dimensions: coverage, bug detection, structural similarity, and assertion quality.

### Why This Approach

Previous TestBot evaluation (March 16-20 sessions) used forward-only testing with synthetic scenarios. That yielded valuable qualitative insights but couldn't answer: "How close does TestBot get to what a real developer would write?" The replay-and-diff approach directly answers this question.

---

## 2. Prerequisite: Fork Setup

### Current State

The `sxarsky/prefect-testb` fork already exists with TestBot infrastructure:
- TestBot workflow configured (`.github/workflows/skyramp-testbot.yml`)
- Deployment scripts in place
- Docker setup for local Prefect server
- GitHub secrets configured

### Required Preparation

Before running the evaluation, the fork needs to be reset to a clean state that mirrors upstream at a specific point in time. The scripts in `testing/replay-eval/` handle this automatically.

---

## 3. Candidate PR Selection

### Selection Criteria

PRs were selected from PrefectHQ/prefect (Oct 2025 - Apr 2026) based on:
- Contains both source code AND test changes
- Reasonably scoped (3-27 files, not massive refactors)
- Feature additions or bug fixes (not CI/docs-only)
- Meaningful test additions (not trivial single-assert)

### Evaluation Tiers

#### Tier 1: Methodology Validation (Start Here)

| PR | Title | Lines | Test Files | Source Files |
|----|-------|-------|------------|--------------|
| #21267 | Fix UnicodeDecodeError for non-UTF-8 subprocess output | +25/-5 | 1 | 2 |
| #21320 | Fix dotenv_values when .env is not a regular file | +28/-2 | 2 | 2 |
| #21307 | Add `position` to block schema properties | +132/-29 | 2 | 1 |
| #21443 | Fix identity-verify run_results for weakref objects | +292/-9 | 1 | 3 |
| #21356 | Fix deploy pull step for custom Docker images | +216/-1 | 2 | 1 |

**Purpose:** Small, focused PRs to validate the end-to-end pipeline works before scaling up.

#### Tier 2: Medium Complexity

| PR | Title | Lines | Test Files | Source Files |
|----|-------|-------|------------|--------------|
| #21436 | Persist explicit DTSTART on RRule schedules | +504/-37 | 9 | 3 |
| #21365 | Set worker attribution env vars in worker process | +205/-1 | 3 | 3 |
| #21350 | Add configurable parameter size limit | +151/-9 | 4 | 4 |
| #21354 | Add exponential backoff retries for ECS registration | +119/-3 | 1 | 2 |
| #20951 | Separate raise_on_lease_renewal_failure from strict | +160/-8 | 1 | 5 |
| #21304 | Add `with_context()` for subprocess logging | +265/-1 | 2 | 2 |

**Purpose:** Cross-system changes that test TestBot's ability to generate coordinated tests.

#### Tier 3: Large Refactors

| PR | Title | Lines | Test Files | Source Files |
|----|-------|-------|------------|--------------|
| #21286 | Add opt-in BuildKit/buildx support | +1073/-43 | 4 | 8 |
| #21252 | Remove internal Runner usage | +731/-121 | 11 | 15 |

**Purpose:** Stress-test TestBot with large, multi-module changes.

#### Bonus: Specialized

| PR | Title | Focus |
|----|-------|-------|
| #21273 | Fix EventsWorker class variable mutation | Concurrency/state |
| #21033 | Add bounded queue to prevent OOM | Cross-subsystem |
| #21231 | Fix Jinja template parameter coercion | Schema hydration |
| #21211 | Add pre-commit hook for double backticks | Multi-integration |

---

## 4. Detailed Pipeline

### Step 1: Extract Ground Truth

For each target PR, extract two patch sets:

```
PR Diff = Code Patch + Test Patch
```

- **Code Patch:** All changes to non-test files (the "feature")
- **Test Patch:** All changes to test files (the "ground truth")

The extraction script (`extract_patches.sh`) uses git diff with path filters to cleanly separate these. Test files are identified by path pattern (`tests/**`, `**/tests/**`, `**/*_test.py`, `**/*test_*.py`).

### Step 2: Establish Baseline

For each PR, identify the merge-base commit (the state of `main` just before the PR was merged). This becomes the starting point for replay.

```bash
# The commit just before the PR merge
BASE_COMMIT=$(gh pr view $PR_NUMBER --repo PrefectHQ/prefect --json mergeCommit -q '.mergeCommit.oid')
git log --oneline ${BASE_COMMIT}^..${BASE_COMMIT}
```

### Step 3: Prepare Replay Branch

Create a clean branch from the baseline, apply only the code patch (no tests):

```bash
git checkout -b replay/pr${PR_NUMBER} ${BASE_COMMIT}~1
git apply code-only-${PR_NUMBER}.patch
git commit -m "Replay PR #${PR_NUMBER} code changes (tests stripped)"
```

### Step 4: Push and Trigger TestBot

Push the replay branch and open a PR against the fork's main:

```bash
git push origin replay/pr${PR_NUMBER}
gh pr create \
  --repo sxarsky/prefect-testb \
  --title "Replay PR #${PR_NUMBER}: <title>" \
  --body "Automated replay for TestBot evaluation. Original: PrefectHQ/prefect#${PR_NUMBER}"
```

TestBot triggers automatically via the configured GitHub workflow.

### Step 5: Collect TestBot Output

After TestBot completes (typically 10-15 minutes):
1. Check the PR for TestBot's commit with generated tests
2. Extract the generated test files
3. Save to `results/replay/pr${PR_NUMBER}/generated/`

### Step 6: Compare

Run the comparison suite across three dimensions:

#### 6a. Coverage Comparison
- Run both test suites against the same codebase
- Compare line/branch coverage using `pytest-cov`
- Metric: Coverage delta (% difference in lines covered)

#### 6b. Bug Detection (Mutation Testing)
- Inject known mutations into the feature code using `mutmut` or manual fault injection
- Run both test suites against the mutated code
- Metric: Mutation kill rate (% of injected bugs caught)

#### 6c. Structural Comparison
- Count: number of test functions, assertions, parametrized cases
- Classify: test types (unit, integration, contract)
- Compare: fixture/mock usage patterns
- Metric: Structural similarity score

---

## 5. Comparison Metrics (Detailed)

### Primary Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| **Coverage Parity** | \|coverage_testbot - coverage_human\| | < 10% delta |
| **Mutation Kill Rate** | mutations_killed / total_mutations | > 70% of human rate |
| **Test Function Recall** | matching_functions / human_functions | > 60% |
| **False Positive Rate** | failing_generated_tests / total_generated | < 10% |

### Secondary Metrics

| Metric | Definition | Notes |
|--------|-----------|-------|
| Assertion Density | assertions / test_function | Compare distribution |
| Edge Case Detection | boundary_tests / total_tests | Human vs. generated |
| Mock Accuracy | correct_mocks / total_mocks | Do mocks target the right deps? |
| Parametrization Rate | parametrized_tests / total_tests | Compare patterns |
| Test Execution Time | seconds to run full suite | Generated vs. human |

### Qualitative Assessment

For each PR, also record:
- Did TestBot identify the correct modules to test?
- Did it understand the intent of the code change?
- What did the human write that TestBot missed (and vice versa)?
- Would the generated tests catch a regression if the feature broke?

---

## 6. Automation Scripts

All scripts live in `testing/replay-eval/`:

| Script | Purpose |
|--------|---------|
| `extract_patches.sh` | Extract code-only and test-only patches from upstream PRs |
| `prepare_replay.sh` | Create replay branches with code-only changes |
| `trigger_testbot.sh` | Push branches and open PRs to trigger TestBot |
| `collect_results.sh` | Gather TestBot output after completion |
| `compare_tests.py` | Run the multi-dimensional comparison suite |
| `run_evaluation.sh` | End-to-end orchestrator for the full pipeline |

---

## 7. Expected Timeline

| Phase | PRs | Estimated Time | Goal |
|-------|-----|---------------|------|
| Pipeline validation | 1-2 Tier 1 PRs | 1 day | Verify end-to-end works |
| Tier 1 evaluation | 5 PRs | 2-3 days | Baseline metrics |
| Tier 2 evaluation | 6 PRs | 3-4 days | Cross-system analysis |
| Tier 3 evaluation | 2 PRs | 2-3 days | Stress testing |
| Analysis & report | All | 2-3 days | Final findings |
| **Total** | **17 PRs** | **~2 weeks** | Comprehensive evaluation |

---

## 8. Risks and Mitigations

### Risk: TestBot infrastructure issues block replay
**Mitigation:** We've already resolved most deployment issues (307 redirects, Docker builds from source, DB init). The existing prefect-testb fork has working infrastructure.

### Risk: Patch application fails due to conflicts
**Mitigation:** We're applying patches to the exact parent commit, so conflicts should be rare. The `prepare_replay.sh` script detects and reports failures.

### Risk: Comparison is too noisy (tests are structurally different)
**Mitigation:** We use multiple comparison dimensions. Coverage and mutation testing are objective even when test structure differs completely.

### Risk: TestBot version changes during evaluation
**Mitigation:** Pin TestBot version in workflow config. Record version for each run.

### Risk: Prefect's test infrastructure (fixtures, conftest) is too complex for TestBot
**Mitigation:** Start with Tier 1 PRs that have minimal fixture dependencies. Evaluate TestBot's ability to leverage existing test infrastructure.

---

## 9. Success Criteria

The evaluation is successful if it produces:

1. **Quantitative baseline:** Coverage parity and mutation kill rate numbers for each PR
2. **Pattern analysis:** Which types of changes TestBot handles well vs. poorly
3. **Actionable findings:** Specific recommendations for improving TestBot's test generation
4. **Reproducible pipeline:** Scripts that can be re-run against future TestBot versions to measure improvement

### Stretch Goals

- Run the same evaluation against a second repo (e.g., FastAPI) to test generalizability
- Establish a "TestBot Quality Score" that can be tracked over releases
- Integrate the evaluation pipeline into TestBot's own CI

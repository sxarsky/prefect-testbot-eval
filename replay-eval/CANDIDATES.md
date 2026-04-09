# TestBot Replay-and-Diff Evaluation Candidates

## Methodology Summary
These PRs are suitable for evaluating TestBot using a "replay-and-diff" methodology:
1. Human-written tests serve as ground truth
2. PR code changes are replayed through TestBot
3. Generated tests are compared against human-written tests

## Selection Criteria Met
- Added or modified files in both source code AND tests
- Reasonably scoped (3-27 files changed, median ~6 files)
- Clear feature additions, bug fixes, or enhancements
- Merged in last 6 months (Oct 2025 - Apr 2026)
- Meaningful test additions (not trivial single-assert tests)

---

## Candidate PRs (17 Total)

### 1. PR #21443 - Core Engine Bugfix
**Type:** BUGFIX | **Author:** nate nowack | **Date:** 2026-04-08

**Title:** fix(engine): identity-verify run_results lookups for weakref-able objects

**Scope:** +292/-9 | 4 files changed (1 test, 3 source)

**Test Files:**
- `tests/test_tasks.py`

**Source Files:**
- `src/prefect/context.py`
- `src/prefect/tasks.py`
- `src/prefect/utilities/engine.py`

**Rationale:** Core engine fix with focused test coverage. Good candidate for evaluating TestBot's ability to handle object lifecycle and weakref-related edge cases.

---

### 2. PR #21436 - Schedule Persistence Fix
**Type:** BUGFIX | **Author:** nate nowack | **Date:** 2026-04-07

**Title:** fix(schedules): persist explicit DTSTART on RRule schedules at write time

**Scope:** +504/-37 | 12 files changed (9 test, 3 source)

**Test Files:**
- `tests/_internal/schemas/test_validation.py`
- `tests/cli/deployment/test_deployment_cli.py`
- `tests/cli/test_deploy.py`
- `tests/cli/test_flow.py`
- `tests/client/schemas/test_schedules.py`
- `tests/deployment/test_schedules.py`
- `tests/runner/test_runner.py`
- `tests/server/schemas/test_actions.py`
- `tests/test_flows.py`

**Source Files:**
- `src/prefect/_internal/schemas/validators.py`
- `src/prefect/client/schemas/actions.py`
- `src/prefect/server/schemas/actions.py`

**Rationale:** Excellent candidate with extensive cross-system test coverage. Tests span CLI, client, server, and runner layers. Good for evaluating TestBot on complex schema changes affecting multiple layers.

---

### 3. PR #21365 - Worker Attribution Fix
**Type:** BUGFIX | **Author:** Zach Angell | **Date:** 2026-03-31

**Title:** fix: set worker attribution env vars in the worker process itself

**Scope:** +205/-1 | 6 files changed (3 test, 3 source)

**Test Files:**
- `src/integrations/prefect-docker/tests/test_worker.py`
- `tests/workers/test_process_worker.py`
- `tests/workers/test_worker_attribution.py`

**Source Files:**
- `src/integrations/prefect-docker/prefect_docker/worker.py`
- `src/prefect/workers/base.py`
- `src/prefect/workers/process.py`

**Rationale:** Medium-scoped bugfix touching core worker infrastructure with focused test coverage. Good for evaluating integration test generation across multiple worker types.

---

### 4. PR #21356 - Docker Deploy Step Fix
**Type:** BUGFIX | **Author:** devin-ai-integration[bot] | **Date:** 2026-03-31

**Title:** Fix deploy pull step for custom Docker images without build step

**Scope:** +216/-1 | 3 files changed (2 test, 1 source)

**Test Files:**
- `tests/cli/deploy/test_deploy_actions.py`

**Source Files:**
- `src/prefect/cli/deploy/_actions.py`

**Rationale:** Highly focused bugfix with good test coverage. Single source file makes this ideal for evaluating TestBot on targeted fixes with high test/code ratio.

---

### 5. PR #21350 - Parameter Size Limit Feature
**Type:** ENHANCEMENT | **Author:** devin-ai-integration[bot] | **Date:** 2026-03-31

**Title:** Add configurable parameter size limit for flow runs and deployments

**Scope:** +151/-9 | 8 files changed (4 test, 4 source)

**Test Files:**
- `tests/events/server/actions/test_running_deployment.py`
- `tests/server/orchestration/api/test_deployments.py`
- `tests/server/orchestration/api/test_flow_runs.py`
- `tests/test_settings.py`

**Source Files:**
- `src/prefect/_internal/schemas/validators.py`
- `src/prefect/server/schemas/actions.py`
- `src/prefect/settings/models/server/api.py`
- `ui-v2/src/api/prefect.ts`

**Rationale:** Cross-layer feature (server + settings + UI). Good for evaluating TestBot on features that span multiple domains and require coordinated test generation.

---

### 6. PR #21354 - ECS Worker Retry Enhancement
**Type:** ENHANCEMENT | **Author:** devin-ai-integration[bot] | **Date:** 2026-03-30

**Title:** Add exponential backoff retries for ECS task definition registration

**Scope:** +119/-3 | 3 files changed (1 test, 2 source)

**Test Files:**
- `src/integrations/prefect-aws/tests/workers/test_ecs_worker.py`

**Source Files:**
- `src/integrations/prefect-aws/prefect_aws/settings.py`
- `src/integrations/prefect-aws/prefect_aws/workers/ecs_worker.py`

**Rationale:** Integration-focused feature enhancement. Good for evaluating TestBot on AWS-specific worker functionality and retry logic testing.

---

### 7. PR #20951 - Concurrency API Enhancement
**Type:** ENHANCEMENT | **Author:** Adam Zionts | **Date:** 2026-03-27

**Title:** Separate raise_on_lease_renewal_failure from strict in concurrency()

**Scope:** +160/-8 | 6 files changed (1 test, 5 source)

**Test Files:**
- `tests/concurrency/test_raise_on_lease_renewal_failure.py`

**Source Files:**
- `src/prefect/concurrency/_asyncio.py`
- `src/prefect/concurrency/_leases.py`
- `src/prefect/concurrency/_sync.py`
- `src/prefect/concurrency/asyncio.py`
- `src/prefect/concurrency/sync.py`

**Rationale:** Multi-module API change with focused test. Good for evaluating TestBot on async/sync API changes affecting multiple parallel implementations.

---

### 8. PR #21286 - BuildKit Support Feature
**Type:** ENHANCEMENT | **Author:** devin-ai-integration[bot] | **Date:** 2026-03-27

**Title:** Add opt-in BuildKit/buildx support via python-on-whales

**Scope:** +1073/-43 | 13 files changed (4 test, 8 source)

**Test Files:**
- `src/integrations/prefect-docker/tests/deployments/test_steps.py`
- `tests/docker/test_buildx.py`
- `tests/docker/test_docker_image.py`
- `tests/docker/test_image_builds.py`

**Source Files:**
- `pyproject.toml`
- `src/integrations/prefect-docker/prefect_docker/deployments/steps.py`
- `src/integrations/prefect-docker/pyproject.toml`
- `src/prefect/docker/__init__.py`
- `src/prefect/docker/_buildx.py`
- `src/prefect/docker/docker_image.py`
- `ui-v2/src/api/prefect.ts`
- `uv.lock`

**Rationale:** Substantial feature addition with comprehensive test coverage. Good for evaluating TestBot on larger features spanning Docker integration, deployment steps, and schema changes. Tests span multiple layers (unit, integration, API).

---

### 9. PR #21304 - Subprocess Logging Feature
**Type:** ENHANCEMENT | **Author:** Alex Streed | **Date:** 2026-03-27

**Title:** Add `with_context()` for logging from subprocesses

**Scope:** +265/-1 | 4 files changed (2 test, 2 source)

**Test Files:**
- `tests/test_subprocess_logging.py`

**Source Files:**
- `src/prefect/context.py`

**Rationale:** New logging API for subprocesses with targeted test coverage. Good for evaluating TestBot on context management and logging API design.

---

### 10. PR #21320 - Dotenv Configuration Fix
**Type:** BUGFIX | **Author:** devin-ai-integration[bot] | **Date:** 2026-03-27

**Title:** Fix #21319: Skip dotenv_values when .env is not a regular file

**Scope:** +28/-2 | 4 files changed (2 test, 2 source)

**Test Files:**
- `tests/cli/test_config.py`
- `tests/test_settings.py`

**Source Files:**
- `src/prefect/cli/config.py`
- `src/prefect/settings/sources.py`

**Rationale:** Small, focused bugfix with good test coverage ratio. Excellent for evaluating TestBot on edge case handling (file type checking) with minimal code changes.

---

### 11. PR #21307 - Block Schema Position Property
**Type:** ENHANCEMENT | **Author:** devin-ai-integration[bot] | **Date:** 2026-03-27

**Title:** Add `position` to block schema properties for UI field ordering

**Scope:** +132/-29 | 3 files changed (2 test, 1 source)

**Test Files:**
- `tests/blocks/test_core.py`
- `tests/server/models/test_block_schemas.py`

**Source Files:**
- `src/prefect/blocks/core.py`

**Rationale:** Focused schema enhancement with good test coverage spanning core and server layers. Good for evaluating TestBot on schema property addition and serialization/deserialization.

---

### 12. PR #21267 - Unicode Subprocess Fix
**Type:** BUGFIX | **Author:** Krishna Chaitanya | **Date:** 2026-03-25

**Title:** Fix UnicodeDecodeError when subprocess outputs non-UTF-8 bytes

**Scope:** +25/-5 | 3 files changed (1 test, 2 source)

**Test Files:**
- `tests/utilities/test_processutils.py`

**Source Files:**
- `src/prefect/deployments/steps/utility.py`
- `src/prefect/utilities/processutils.py`

**Rationale:** Minimal, focused bugfix for encoding edge case. Good for evaluating TestBot on edge case test generation with very small surface area.

---

### 13. PR #21273 - EventsWorker Class Variable Fix
**Type:** BUGFIX | **Author:** devin-ai-integration[bot] | **Date:** 2026-03-25

**Title:** Fix EventsWorker class variable mutation and add `_on_item_dropped` for queue cleanup

**Scope:** +144/-4 | 4 files changed (2 test, 2 source)

**Test Files:**
- `tests/_internal/concurrency/test_services.py`
- `tests/events/client/test_bounded_queue.py`

**Source Files:**
- `src/prefect/_internal/concurrency/services.py`
- `src/prefect/events/worker.py`

**Rationale:** Concurrency/state management bugfix with good test coverage. Good for evaluating TestBot on mutable state and resource cleanup scenarios.

---

### 14. PR #21033 - Bounded Queue Feature
**Type:** ENHANCEMENT | **Author:** Adam Zionts | **Date:** 2026-03-25

**Title:** Add bounded queue support to QueueService to prevent OOM during server outages

**Scope:** +131/-3 | 6 files changed (2 test, 4 source)

**Test Files:**
- `tests/events/client/test_bounded_queue.py`
- `tests/test_settings.py`

**Source Files:**
- `src/prefect/_internal/concurrency/services.py`
- `src/prefect/events/worker.py`
- `src/prefect/settings/models/events.py`
- `src/prefect/settings/models/root.py`

**Rationale:** Feature spanning core services, events, and settings. Good for evaluating TestBot on cross-subsystem feature generation with focus on queue behavior and settings integration.

---

### 15. PR #21252 - Remove Internal Runner Usage
**Type:** ENHANCEMENT | **Author:** Alex Streed | **Date:** 2026-03-24

**Title:** Remove internal Runner usage from bundle execution and CLI paths

**Scope:** +731/-121 | 27 files changed (11 test, 15 source)

**Test Files (11 total):**
- `src/integrations/prefect-aws/tests/experimental/test_bundles.py`
- `src/integrations/prefect-azure/tests/experimental/bundles/test_execute.py`
- `src/integrations/prefect-gcp/tests/experimental/bundles/test_execute.py`
- `tests/cli/test_flow_run.py`
- `tests/experimental/test_bundles.py`
- `tests/runner/test__flow_run_executor.py`
- `tests/runner/test__scheduled_run_poller.py`
- `tests/runner/test__state_proposer.py`
- `tests/runner/test_runner.py`
- `tests/test_infrastructure_bound_flow.py`
- `tests/test_observers.py`

**Source Files (15 total, across integrations and core):**
- Integration updates (AWS, Azure, GCP)
- Core runner and CLI changes
- Infrastructure and observer updates

**Rationale:** Largest PR in candidate set. Major architectural refactor with extensive test coverage across multiple integrations and core components. Excellent for evaluating TestBot on large, coordinated refactors with cross-cutting concerns.

---

### 16. PR #21231 - Jinja Template Parameter Coercion
**Type:** BUGFIX | **Author:** devin-ai-integration[bot] | **Date:** 2026-03-23

**Title:** Fix Jinja template parameter type coercion in RunDeployment actions

**Scope:** +201/-7 | 4 files changed (2 test, 2 source)

**Test Files:**
- `tests/events/server/actions/test_running_deployment.py`
- `tests/utilities/schema_tools/test_hydration.py`

**Source Files:**
- `src/prefect/server/events/actions.py`
- `src/prefect/utilities/schema_tools/hydration.py`

**Rationale:** Schema/serialization bugfix with event action focus. Good for evaluating TestBot on type coercion and schema hydration scenarios.

---

### 17. PR #21211 - Pre-commit Hook Enhancement
**Type:** ENHANCEMENT | **Author:** Alex Streed | **Date:** 2026-03-20

**Title:** Add pre-commit hook to prevent double backticks

**Scope:** +81/-76 | 26 files changed (6 test, 20 source)

**Test Files (6 total):**
- `src/integrations/prefect-azure/tests/test_aci_worker.py`
- `src/integrations/prefect-dbt/tests/core/conftest.py`
- `src/integrations/prefect-dbt/tests/core/test_executor.py`
- `src/integrations/prefect-dbt/tests/core/test_orchestrator_cache.py`
- `src/integrations/prefect-kubernetes/tests/test_observer.py`
- `src/integrations/prefect-openai/tests/test_agent.py`

**Source Files (20 total, across multiple integrations):**
- Integration modules (AWS, Azure, DBT, GCP, Kubernetes, etc.)
- Docstring/formatting changes

**Rationale:** Broad integration-touching enhancement. Good for evaluating TestBot on changes that affect multiple independent integration modules while maintaining test consistency.

---

## Summary Statistics

| Metric | Min | Max | Median |
|--------|-----|-----|--------|
| Files Changed | 3 | 27 | 6 |
| Lines Added | 25 | 1073 | 205 |
| Lines Deleted | 1 | 121 | 8 |
| Test Files | 1 | 11 | 2 |
| Source Files | 1 | 15 | 3 |
| **Bugfixes** | - | - | 6 |
| **Enhancements** | - | - | 11 |

## Recommended Evaluation Sets

### Tier 1: Best Starting Points (5 PRs)
- **#21443** - Small, focused core engine bugfix
- **#21356** - Minimal, targeted Docker fix
- **#21320** - Tiny bugfix with great test ratio
- **#21307** - Schema enhancement with clean tests
- **#21267** - Encoding edge case minimal fix

### Tier 2: Medium Complexity (6 PRs)
- **#21436** - Complex schedule fix with multi-system tests
- **#21365** - Worker attribution fix spanning integrations
- **#21350** - Cross-layer feature spanning multiple domains
- **#21354** - AWS-specific worker feature
- **#20951** - Async/sync API duality
- **#21304** - New logging API with focused tests

### Tier 3: Large Refactors (2 PRs)
- **#21286** - Large feature addition (Docker BuildKit)
- **#21252** - Massive architectural refactor (27 files, 11 test files)

### Bonus: Integration-Spanning (4 PRs)
- **#21273** - Concurrency/state management
- **#21033** - Cross-subsystem feature (events + settings)
- **#21231** - Schema hydration bugfix
- **#21211** - Multi-integration enhancement

---

## How to Use These Candidates

1. **Select a PR** from the appropriate tier based on your evaluation complexity preference
2. **Clone/checkout** the commit before the PR merge to get the baseline code
3. **Extract human-written tests** from the PR to serve as ground truth
4. **Strip the tests** and run the code changes through TestBot in "generate tests" mode
5. **Compare generated tests** against human tests:
   - Test coverage (which test functions exist in each set)
   - Assertion distribution (types of assertions used)
   - Edge case detection (boundary conditions tested)
   - Mock/fixture usage patterns

## Repository Information
- **Repository:** https://github.com/PrefectHQ/prefect
- **Analysis Period:** October 2025 - April 2026
- **Total PRs in Period:** 77 merged
- **Candidates Selected:** 17 (with both tests and source changes, reasonably scoped)


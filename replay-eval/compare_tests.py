#!/usr/bin/env python3
"""
compare_tests.py - Multi-dimensional comparison of generated vs ground truth tests

Usage: python3 compare_tests.py <PR_NUMBER> [--patches-dir DIR] [--results-dir DIR]

Compares TestBot-generated tests against human-written ground truth across:
  1. Structural comparison (test counts, assertions, patterns)
  2. Coverage comparison (requires running both suites)
  3. Semantic similarity (test intent matching)

Prerequisites:
  - collect_results.sh has been run for the PR
  - Python 3.8+ with ast module (stdlib)
"""

import ast
import json
import os
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


@dataclass
class TestFunction:
    name: str
    file: str
    line: int
    decorators: list = field(default_factory=list)
    assertion_count: int = 0
    assertion_types: list = field(default_factory=list)
    has_parametrize: bool = False
    param_count: int = 0
    fixtures_used: list = field(default_factory=list)
    mock_count: int = 0
    line_count: int = 0
    docstring: str = ""


@dataclass
class TestSuiteProfile:
    source: str  # "ground_truth" or "generated"
    pr_number: int
    files: list = field(default_factory=list)
    functions: list = field(default_factory=list)
    total_assertions: int = 0
    total_lines: int = 0
    assertion_type_dist: dict = field(default_factory=dict)
    fixture_usage: dict = field(default_factory=dict)
    test_types: dict = field(default_factory=dict)  # unit/integration/contract


class TestFileAnalyzer(ast.NodeVisitor):
    """Analyze a Python test file using AST parsing."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.functions: list[TestFunction] = []
        self._current_function: Optional[TestFunction] = None

    def analyze(self, source: str) -> list[TestFunction]:
        try:
            tree = ast.parse(source)
            self.visit(tree)
        except SyntaxError as e:
            print(f"  WARNING: Syntax error in {self.filepath}: {e}")
        return self.functions

    def visit_FunctionDef(self, node):
        if node.name.startswith("test_"):
            func = TestFunction(
                name=node.name,
                file=self.filepath,
                line=node.lineno,
                line_count=node.end_lineno - node.lineno + 1 if node.end_lineno else 0,
            )

            # Analyze decorators
            for dec in node.decorator_list:
                dec_name = self._get_decorator_name(dec)
                func.decorators.append(dec_name)
                if "parametrize" in dec_name.lower():
                    func.has_parametrize = True
                    func.param_count = self._count_params(dec)

            # Analyze function arguments (fixtures)
            for arg in node.args.args:
                if arg.arg not in ("self", "cls"):
                    func.fixtures_used.append(arg.arg)

            # Get docstring
            if (node.body and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, (ast.Str, ast.Constant))):
                val = node.body[0].value
                func.docstring = val.s if isinstance(val, ast.Str) else str(val.value)

            # Count assertions and mocks
            self._current_function = func
            self.generic_visit(node)
            self._current_function = None

            self.functions.append(func)
        else:
            self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Assert(self, node):
        if self._current_function:
            self._current_function.assertion_count += 1
            self._current_function.assertion_types.append("assert")
        self.generic_visit(node)

    def visit_Call(self, node):
        if self._current_function:
            call_name = self._get_call_name(node)

            # Count assertion-like calls
            assertion_patterns = [
                "assertEqual", "assertIn", "assertTrue", "assertFalse",
                "assertRaises", "assertIsNone", "assertIsNotNone",
                "assert_called", "assert_called_once", "assert_called_with",
                "assert_not_called",
            ]
            for pat in assertion_patterns:
                if pat in call_name:
                    self._current_function.assertion_count += 1
                    self._current_function.assertion_types.append(pat)
                    break

            # Count pytest assertions
            if call_name.startswith("pytest.raises"):
                self._current_function.assertion_count += 1
                self._current_function.assertion_types.append("pytest.raises")

            # Count mocks
            if any(m in call_name for m in ["mock", "Mock", "patch", "MagicMock"]):
                self._current_function.mock_count += 1

        self.generic_visit(node)

    def _get_decorator_name(self, node) -> str:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_decorator_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Call):
            return self._get_decorator_name(node.func)
        return "unknown"

    def _get_call_name(self, node) -> str:
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr
        return "unknown"

    def _count_params(self, decorator) -> int:
        """Count parametrize test cases."""
        if not isinstance(decorator, ast.Call) or not decorator.args:
            return 0
        # Second arg of @pytest.mark.parametrize is the params list
        if len(decorator.args) >= 2:
            arg = decorator.args[1]
            if isinstance(arg, (ast.List, ast.Tuple)):
                return len(arg.elts)
        return 0


def classify_test_type(func: TestFunction) -> str:
    """Classify a test as unit, integration, or contract based on heuristics."""
    name_lower = func.name.lower()
    file_lower = func.file.lower()
    fixtures_lower = [f.lower() for f in func.fixtures_used]

    # Contract tests
    if any(kw in name_lower for kw in ["contract", "schema", "serializ", "deserializ"]):
        return "contract"
    if any(kw in file_lower for kw in ["contract", "schema"]):
        return "contract"

    # Integration tests
    if any(kw in name_lower for kw in ["integration", "e2e", "end_to_end"]):
        return "integration"
    if any(f in fixtures_lower for f in ["client", "session", "db", "database", "server", "app"]):
        return "integration"
    if any(kw in file_lower for kw in ["integration", "e2e"]):
        return "integration"

    # Default to unit
    return "unit"


def profile_test_suite(source_label: str, pr_number: int, test_dir: Path) -> TestSuiteProfile:
    """Build a complete profile of a test suite."""
    profile = TestSuiteProfile(source=source_label, pr_number=pr_number)

    if not test_dir.exists():
        print(f"  WARNING: Directory not found: {test_dir}")
        return profile

    test_files = list(test_dir.rglob("*.py"))
    if not test_files:
        print(f"  WARNING: No Python files found in {test_dir}")
        return profile

    all_assertion_types = []
    all_fixtures = []
    type_counts = Counter()

    for test_file in test_files:
        rel_path = str(test_file.relative_to(test_dir))
        profile.files.append(rel_path)

        try:
            source = test_file.read_text(encoding="utf-8", errors="replace")
            profile.total_lines += source.count("\n") + 1
        except Exception as e:
            print(f"  WARNING: Could not read {test_file}: {e}")
            continue

        analyzer = TestFileAnalyzer(rel_path)
        functions = analyzer.analyze(source)

        for func in functions:
            test_type = classify_test_type(func)
            func_dict = {
                "name": func.name,
                "file": func.file,
                "type": test_type,
                "assertions": func.assertion_count,
                "parametrized": func.has_parametrize,
                "param_count": func.param_count,
                "mocks": func.mock_count,
                "fixtures": func.fixtures_used,
                "line_count": func.line_count,
            }
            profile.functions.append(func_dict)
            profile.total_assertions += func.assertion_count
            all_assertion_types.extend(func.assertion_types)
            all_fixtures.extend(func.fixtures_used)
            type_counts[test_type] += 1

    profile.assertion_type_dist = dict(Counter(all_assertion_types))
    profile.fixture_usage = dict(Counter(all_fixtures).most_common(20))
    profile.test_types = dict(type_counts)

    return profile


def compute_comparison(ground_truth: TestSuiteProfile, generated: TestSuiteProfile) -> dict:
    """Compute comparison metrics between ground truth and generated suites."""

    gt_func_names = {f["name"] for f in ground_truth.functions}
    gen_func_names = {f["name"] for f in generated.functions}

    # Name-based matching (exact)
    exact_matches = gt_func_names & gen_func_names

    # Fuzzy matching: strip test_ prefix, normalize
    def normalize_name(name: str) -> str:
        name = name.lower()
        name = re.sub(r"^test_", "", name)
        name = re.sub(r"_+", "_", name)
        return name

    gt_normalized = {normalize_name(n): n for n in gt_func_names}
    gen_normalized = {normalize_name(n): n for n in gen_func_names}
    fuzzy_matches = set(gt_normalized.keys()) & set(gen_normalized.keys())

    # Compute metrics
    gt_count = len(ground_truth.functions)
    gen_count = len(generated.functions)

    comparison = {
        "summary": {
            "ground_truth_test_count": gt_count,
            "generated_test_count": gen_count,
            "test_count_ratio": gen_count / gt_count if gt_count > 0 else 0,
            "ground_truth_files": len(ground_truth.files),
            "generated_files": len(generated.files),
            "ground_truth_total_lines": ground_truth.total_lines,
            "generated_total_lines": generated.total_lines,
        },
        "matching": {
            "exact_name_matches": len(exact_matches),
            "exact_match_names": sorted(exact_matches),
            "fuzzy_matches": len(fuzzy_matches),
            "fuzzy_match_pairs": {
                gt_normalized[n]: gen_normalized[n]
                for n in fuzzy_matches
                if n in gt_normalized and n in gen_normalized
            },
            "recall_exact": len(exact_matches) / gt_count if gt_count > 0 else 0,
            "recall_fuzzy": len(fuzzy_matches) / gt_count if gt_count > 0 else 0,
            "only_in_ground_truth": sorted(gt_func_names - gen_func_names),
            "only_in_generated": sorted(gen_func_names - gt_func_names),
        },
        "assertions": {
            "ground_truth_total": ground_truth.total_assertions,
            "generated_total": generated.total_assertions,
            "assertion_ratio": (
                generated.total_assertions / ground_truth.total_assertions
                if ground_truth.total_assertions > 0 else 0
            ),
            "ground_truth_per_test": (
                ground_truth.total_assertions / gt_count if gt_count > 0 else 0
            ),
            "generated_per_test": (
                generated.total_assertions / gen_count if gen_count > 0 else 0
            ),
            "ground_truth_type_dist": ground_truth.assertion_type_dist,
            "generated_type_dist": generated.assertion_type_dist,
        },
        "test_types": {
            "ground_truth": ground_truth.test_types,
            "generated": generated.test_types,
        },
        "complexity": {
            "ground_truth_avg_lines": (
                sum(f["line_count"] for f in ground_truth.functions) / gt_count
                if gt_count > 0 else 0
            ),
            "generated_avg_lines": (
                sum(f["line_count"] for f in generated.functions) / gen_count
                if gen_count > 0 else 0
            ),
            "ground_truth_parametrized": sum(
                1 for f in ground_truth.functions if f["parametrized"]
            ),
            "generated_parametrized": sum(
                1 for f in generated.functions if f["parametrized"]
            ),
            "ground_truth_mocked": sum(
                1 for f in ground_truth.functions if f["mocks"] > 0
            ),
            "generated_mocked": sum(
                1 for f in generated.functions if f["mocks"] > 0
            ),
        },
        "fixtures": {
            "ground_truth_top": ground_truth.fixture_usage,
            "generated_top": generated.fixture_usage,
            "shared_fixtures": sorted(
                set(ground_truth.fixture_usage.keys()) & set(generated.fixture_usage.keys())
            ),
        },
    }

    return comparison


def generate_report(pr_number: int, comparison: dict, output_path: Path):
    """Generate a human-readable comparison report."""

    s = comparison["summary"]
    m = comparison["matching"]
    a = comparison["assertions"]
    t = comparison["test_types"]
    c = comparison["complexity"]

    report = f"""# TestBot Evaluation Report: PR #{pr_number}

**Generated:** {__import__('datetime').datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
**Methodology:** Replay-and-Diff

---

## Executive Summary

| Metric | Ground Truth | Generated | Ratio |
|--------|-------------|-----------|-------|
| Test functions | {s['ground_truth_test_count']} | {s['generated_test_count']} | {s['test_count_ratio']:.2f}x |
| Total assertions | {a['ground_truth_total']} | {a['generated_total']} | {a['assertion_ratio']:.2f}x |
| Test files | {s['ground_truth_files']} | {s['generated_files']} | - |
| Total lines | {s['ground_truth_total_lines']} | {s['generated_total_lines']} | - |

## Test Function Matching

| Metric | Value |
|--------|-------|
| Exact name matches | {m['exact_name_matches']} / {s['ground_truth_test_count']} ({m['recall_exact']:.0%}) |
| Fuzzy name matches | {m['fuzzy_matches']} / {s['ground_truth_test_count']} ({m['recall_fuzzy']:.0%}) |
| Only in ground truth | {len(m['only_in_ground_truth'])} |
| Only in generated | {len(m['only_in_generated'])} |

### Tests Only in Ground Truth (missed by TestBot)
"""
    for name in m["only_in_ground_truth"]:
        report += f"- `{name}`\n"

    report += f"""
### Tests Only in Generated (TestBot extras)
"""
    for name in m["only_in_generated"]:
        report += f"- `{name}`\n"

    report += f"""
## Test Type Distribution

| Type | Ground Truth | Generated |
|------|-------------|-----------|
| Unit | {t['ground_truth'].get('unit', 0)} | {t['generated'].get('unit', 0)} |
| Integration | {t['ground_truth'].get('integration', 0)} | {t['generated'].get('integration', 0)} |
| Contract | {t['ground_truth'].get('contract', 0)} | {t['generated'].get('contract', 0)} |

## Assertion Analysis

| Metric | Ground Truth | Generated |
|--------|-------------|-----------|
| Assertions per test | {a['ground_truth_per_test']:.1f} | {a['generated_per_test']:.1f} |
| Total assertions | {a['ground_truth_total']} | {a['generated_total']} |

## Complexity Metrics

| Metric | Ground Truth | Generated |
|--------|-------------|-----------|
| Avg lines per test | {c['ground_truth_avg_lines']:.1f} | {c['generated_avg_lines']:.1f} |
| Parametrized tests | {c['ground_truth_parametrized']} | {c['generated_parametrized']} |
| Tests using mocks | {c['ground_truth_mocked']} | {c['generated_mocked']} |

## Shared Fixtures

Both suites use: {', '.join(f'`{f}`' for f in comparison['fixtures']['shared_fixtures']) or 'None'}

---

## Scoring

### Coverage Parity Score
*Requires running both test suites with pytest-cov. See instructions below.*

### Structural Similarity Score
"""
    # Compute a rough structural similarity score
    scores = []

    # Test count similarity (0-25 points)
    ratio = s["test_count_ratio"]
    count_score = max(0, 25 - abs(1 - ratio) * 25)
    scores.append(("Test Count Parity", count_score, 25))

    # Matching recall (0-25 points)
    recall_score = m["recall_fuzzy"] * 25
    scores.append(("Function Recall", recall_score, 25))

    # Assertion density (0-25 points)
    if a["ground_truth_per_test"] > 0:
        assert_ratio = a["generated_per_test"] / a["ground_truth_per_test"]
        assert_score = max(0, 25 - abs(1 - assert_ratio) * 25)
    else:
        assert_score = 0
    scores.append(("Assertion Density", assert_score, 25))

    # Type distribution similarity (0-25 points)
    all_types = set(list(t["ground_truth"].keys()) + list(t["generated"].keys()))
    if all_types and s["ground_truth_test_count"] > 0:
        type_diff = sum(
            abs(
                t["ground_truth"].get(tt, 0) / s["ground_truth_test_count"]
                - t["generated"].get(tt, 0) / max(s["generated_test_count"], 1)
            )
            for tt in all_types
        )
        type_score = max(0, 25 - type_diff * 25)
    else:
        type_score = 0
    scores.append(("Type Distribution", type_score, 25))

    total_score = sum(s for _, s, _ in scores)
    max_score = sum(m for _, _, m in scores)

    for label, score, max_s in scores:
        report += f"- **{label}**: {score:.1f}/{max_s}\n"

    report += f"\n**Total Structural Similarity: {total_score:.1f}/{max_score} ({total_score/max_score*100:.0f}%)**\n"

    # Grade
    pct = total_score / max_score * 100
    if pct >= 80:
        grade = "A - Excellent"
    elif pct >= 60:
        grade = "B - Good"
    elif pct >= 40:
        grade = "C - Fair"
    elif pct >= 20:
        grade = "D - Poor"
    else:
        grade = "F - Very Poor"

    report += f"\n**Grade: {grade}**\n"

    report += """
---

## Next Steps

### Run Coverage Comparison
```bash
# Install in the Prefect environment
pip install pytest-cov

# Run ground truth tests with coverage
pytest <ground_truth_test_files> --cov=src/prefect --cov-report=json:coverage_gt.json

# Run generated tests with coverage
pytest <generated_test_files> --cov=src/prefect --cov-report=json:coverage_gen.json

# Compare coverage reports
python3 compare_coverage.py coverage_gt.json coverage_gen.json
```

### Run Mutation Testing
```bash
pip install mutmut

# Run mutations against ground truth
mutmut run --paths-to-mutate=<source_files> --tests-dir=<ground_truth_tests>

# Run mutations against generated
mutmut run --paths-to-mutate=<source_files> --tests-dir=<generated_tests>

# Compare kill rates
```
"""

    output_path.write_text(report)
    return total_score, max_score


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 compare_tests.py <PR_NUMBER> [--patches-dir DIR] [--results-dir DIR]")
        sys.exit(1)

    pr_number = int(sys.argv[1])

    # Parse optional args
    patches_dir = Path(f"./patches/pr{pr_number}")
    results_dir = Path(f"./results/replay/pr{pr_number}")

    for i, arg in enumerate(sys.argv[2:], 2):
        if arg == "--patches-dir" and i + 1 < len(sys.argv):
            patches_dir = Path(sys.argv[i + 1])
        elif arg == "--results-dir" and i + 1 < len(sys.argv):
            results_dir = Path(sys.argv[i + 1])

    ground_truth_dir = patches_dir / "ground-truth"
    generated_dir = results_dir / "generated"

    print(f"=== Comparing tests for PR #{pr_number} ===")
    print(f"Ground truth: {ground_truth_dir}")
    print(f"Generated:    {generated_dir}")
    print()

    # Profile both suites
    print("--- Profiling ground truth tests ---")
    gt_profile = profile_test_suite("ground_truth", pr_number, ground_truth_dir)
    print(f"  Found {len(gt_profile.functions)} test functions in {len(gt_profile.files)} files")

    print("--- Profiling generated tests ---")
    gen_profile = profile_test_suite("generated", pr_number, generated_dir)
    print(f"  Found {len(gen_profile.functions)} test functions in {len(gen_profile.files)} files")

    # Compute comparison
    print("\n--- Computing comparison ---")
    comparison = compute_comparison(gt_profile, gen_profile)

    # Save raw data
    output_dir = results_dir / "comparison"
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "ground_truth_profile.json", "w") as f:
        json.dump({"functions": gt_profile.functions, "files": gt_profile.files,
                    "total_assertions": gt_profile.total_assertions,
                    "test_types": gt_profile.test_types}, f, indent=2)

    with open(output_dir / "generated_profile.json", "w") as f:
        json.dump({"functions": gen_profile.functions, "files": gen_profile.files,
                    "total_assertions": gen_profile.total_assertions,
                    "test_types": gen_profile.test_types}, f, indent=2)

    with open(output_dir / "comparison.json", "w") as f:
        json.dump(comparison, f, indent=2)

    # Generate report
    report_path = output_dir / "evaluation_report.md"
    score, max_score = generate_report(pr_number, comparison, report_path)

    print(f"\n=== Comparison Complete ===")
    print(f"Structural Similarity Score: {score:.1f}/{max_score} ({score/max_score*100:.0f}%)")
    print(f"\nReport:     {report_path}")
    print(f"Raw data:   {output_dir}/comparison.json")
    print(f"GT profile: {output_dir}/ground_truth_profile.json")
    print(f"Gen profile:{output_dir}/generated_profile.json")


if __name__ == "__main__":
    main()

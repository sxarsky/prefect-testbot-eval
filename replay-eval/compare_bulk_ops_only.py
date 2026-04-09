#!/usr/bin/env python3
"""Compare only the bulk operations test files."""
import ast
import sys
from pathlib import Path

def extract_test_names(filepath):
    """Extract all test function names from a Python test file."""
    with open(filepath) as f:
        tree = ast.parse(f.read())

    tests = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith('test_'):
                tests.append(node.name)

    return tests

# Paths
gt_file = Path("patches/pr20469/ground-truth/tests/server/orchestration/api/test_bulk_operations.py")
gen_file = Path("results/replay/pr20469/generated/tests/server/orchestration/api/test_bulk_operations.py")

# Extract test names
gt_tests = set(extract_test_names(gt_file))
gen_tests = set(extract_test_names(gen_file))

# Compare
matched = gt_tests & gen_tests
only_gt = gt_tests - gen_tests
only_gen = gen_tests - gt_tests

# Print results
print(f"=== BULK OPERATIONS TEST COMPARISON ===\n")
print(f"Ground Truth: {len(gt_tests)} tests")
print(f"Generated: {len(gen_tests)} tests")
print(f"\n=== EXACT MATCHES: {len(matched)}/{len(gt_tests)} ({len(matched)/len(gt_tests)*100:.0f}%) ===")

if len(matched) <= 50:
    for test in sorted(matched):
        print(f"  ✓ {test}")
else:
    for test in sorted(matched)[:25]:
        print(f"  ✓ {test}")
    print(f"  ... and {len(matched) - 25} more")

print(f"\n=== MISSED BY TESTBOT: {len(only_gt)} ===")
if only_gt:
    for test in sorted(only_gt):
        print(f"  ✗ {test}")
else:
    print("  None! TestBot generated ALL ground truth tests.")

print(f"\n=== TESTBOT EXTRAS: {len(only_gen)} ===")
if only_gen:
    if len(only_gen) <= 20:
        for test in sorted(only_gen):
            print(f"  + {test}")
    else:
        for test in sorted(only_gen)[:20]:
            print(f"  + {test}")
        print(f"  ... and {len(only_gen) - 20} more")
else:
    print("  None. TestBot generated exactly the ground truth tests.")

# Calculate recall
recall = len(matched) / len(gt_tests) if gt_tests else 0
precision = len(matched) / len(gen_tests) if gen_tests else 0
f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

print(f"\n=== METRICS ===")
print(f"Recall (coverage of ground truth): {recall:.1%}")
print(f"Precision (relevance of generated): {precision:.1%}")
print(f"F1 Score: {f1:.1%}")

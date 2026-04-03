import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.grader import grade_exercise


def test_correct_solution():
    code = "age = 25\nprint(age)"
    test_cases = [{"input": [], "expected_output": "25\n", "match_mode": "exact"}]
    result = grade_exercise(code, test_cases)
    assert result.all_passed, "Expected all passed, got {}/{}".format(result.passed, result.total)
    print("[PASS] correct_solution")


def test_wrong_output():
    code = "age = 99\nprint(age)"
    test_cases = [{"input": [], "expected_output": "25\n", "match_mode": "exact"}]
    result = grade_exercise(code, test_cases)
    assert not result.all_passed
    assert result.passed == 0
    print("[PASS] wrong_output")


def test_contains_match():
    code = "print('The answer is 42')"
    test_cases = [{"input": [], "expected_output": "42", "match_mode": "contains"}]
    result = grade_exercise(code, test_cases)
    assert result.all_passed
    print("[PASS] contains_match")


def test_function_call():
    code = "def add(a, b):\n    return a + b"
    test_cases = [
        {"function_name": "add", "input": [1, 2], "expected_output": "3\n"},
        {"function_name": "add", "input": [10, 20], "expected_output": "30\n"},
        {"function_name": "add", "input": [-1, 1], "expected_output": "0\n"},
    ]
    result = grade_exercise(code, test_cases)
    assert result.all_passed, "Expected all passed, got {}/{}".format(result.passed, result.total)
    assert len(result.details) == 3
    print("[PASS] function_call")


def test_syntax_error():
    code = "def f(:\n  pass"
    test_cases = [{"input": [], "expected_output": "5\n"}]
    result = grade_exercise(code, test_cases)
    assert result.passed == 0
    assert "错误" in result.details[0].actual
    print("[PASS] syntax_error")


def test_swap_variables():
    code = "a = 10\nb = 20\na, b = b, a\nprint(a, b)"
    test_cases = [{"input": [], "expected_output": "20 10\n", "match_mode": "exact"}]
    result = grade_exercise(code, test_cases)
    assert result.all_passed
    print("[PASS] swap_variables")


if __name__ == "__main__":
    tests = [
        test_correct_solution,
        test_wrong_output,
        test_contains_match,
        test_function_call,
        test_syntax_error,
        test_swap_variables,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print("[FAIL] {}: {}".format(t.__name__, e))
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n=== Results: {} passed, {} failed ===".format(passed, failed))
    if failed > 0:
        sys.exit(1)

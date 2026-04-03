from dataclasses import dataclass, field

from core.code_executor import execute_code


@dataclass
class TestResult:
    input_desc: str
    expected: str
    actual: str
    passed: bool


@dataclass
class GradingResult:
    passed: int
    total: int
    details: list = field(default_factory=list)
    error: str = ""

    @property
    def all_passed(self):
        return self.passed == self.total


def grade_exercise(user_code, test_cases):
    """Grade user code against test cases.

    Each test_case has:
      - input: list of args to pass to the function
      - expected_output: string to compare against stdout
      - match_mode: "exact" (default) or "contains"
    """
    if not test_cases:
        return GradingResult(0, 0, error="没有测试用例")

    results = []
    passed_count = 0

    for i, tc in enumerate(test_cases):
        expected = tc["expected_output"]
        match_mode = tc.get("match_mode", "exact")

        # Wrap user code + test invocation
        wrapped = _wrap_code(user_code, tc)

        exec_result = execute_code(wrapped)

        if not exec_result.success:
            results.append(
                TestResult(
                    input_desc=_describe_input(tc),
                    expected=expected.strip(),
                    actual="错误: {}".format(exec_result.error),
                    passed=False,
                )
            )
            continue

        actual = exec_result.output
        if match_mode == "exact":
            is_pass = actual == expected
        elif match_mode == "contains":
            is_pass = expected.strip() in actual.strip()
        else:
            is_pass = actual.strip() == expected.strip()

        if is_pass:
            passed_count += 1

        results.append(
            TestResult(
                input_desc=_describe_input(tc),
                expected=expected.strip(),
                actual=actual.strip(),
                passed=is_pass,
            )
        )

    return GradingResult(passed=passed_count, total=len(test_cases), details=results)


def _wrap_code(user_code, test_case):
    """Combine user code with a test invocation wrapper.

    If the test case has a 'function_name' field, we call that function with args.
    Otherwise, we just run the user code and capture stdout.
    """
    func_name = test_case.get("function_name")
    args = test_case.get("input", [])

    if func_name:
        # Function-based exercise: user defines function, we call it
        args_str = ", ".join(repr(a) for a in args)
        call_line = "print({}({}))".format(func_name, args_str)
        return "{}\n{}".format(user_code, call_line)
    else:
        # Output-based exercise: just run user code, capture print output
        return user_code


def _describe_input(test_case):
    """Create a human-readable description of the test input."""
    func_name = test_case.get("function_name")
    args = test_case.get("input", [])
    if func_name:
        args_str = ", ".join(repr(a) for a in args)
        return "{}({})".format(func_name, args_str)
    return "运行代码"

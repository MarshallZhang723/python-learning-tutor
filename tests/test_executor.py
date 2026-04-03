import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.code_executor import execute_code


def test_simple_print():
    result = execute_code("print('hello')")
    assert result.success
    assert result.output.strip() == "hello"
    print("[PASS] simple_print")


def test_math():
    result = execute_code("print(2 + 3)")
    assert result.success
    assert result.output.strip() == "5"
    print("[PASS] math")


def test_syntax_error():
    result = execute_code("def f(:\n  pass")
    assert not result.success
    assert "语法错误" in result.error or "SyntaxError" in result.error
    print("[PASS] syntax_error")


def test_name_error():
    result = execute_code("print(undefined_variable)")
    assert not result.success
    assert "NameError" in result.error
    print("[PASS] name_error")


def test_blocked_import_os():
    result = execute_code("import os")
    assert not result.success
    assert result.error  # any error message is acceptable
    print("[PASS] blocked_import_os")


def test_blocked_import_subprocess():
    result = execute_code("import subprocess")
    assert not result.success
    print("[PASS] blocked_import_subprocess")


def test_blocked_open():
    result = execute_code("open('/etc/passwd')")
    assert not result.success
    print("[PASS] blocked_open")


def test_blocked_exec():
    result = execute_code("exec('print(1)')")
    assert not result.success
    print("[PASS] blocked_exec")


def test_blocked_eval():
    result = execute_code("eval('1+1')")
    assert not result.success
    print("[PASS] blocked_eval")


def test_timeout():
    result = execute_code("while True: pass")
    assert not result.success
    assert "超时" in result.error or "timeout" in result.error.lower()
    print("[PASS] timeout")


def test_input_blocked():
    result = execute_code("input('name: ')")
    assert not result.success
    assert "不可用" in result.error or "not supported" in result.error.lower()
    print("[PASS] input_blocked")


def test_complex_program():
    code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

for i in range(10):
    print(fibonacci(i), end=' ')
print()
"""
    result = execute_code(code)
    assert result.success
    assert "0 1 1 2 3 5 8 13 21" in result.output
    print("[PASS] complex_program")


def test_multiple_outputs():
    code = """
for i in range(5):
    print(i)
"""
    result = execute_code(code)
    assert result.success
    lines = [l.strip() for l in result.output.strip().split("\n")]
    assert lines == ["0", "1", "2", "3", "4"]
    print("[PASS] multiple_outputs")


if __name__ == "__main__":
    tests = [
        test_simple_print,
        test_math,
        test_syntax_error,
        test_name_error,
        test_blocked_import_os,
        test_blocked_import_subprocess,
        test_blocked_open,
        test_blocked_exec,
        test_blocked_eval,
        test_timeout,
        test_input_blocked,
        test_complex_program,
        test_multiple_outputs,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print("[FAIL] {}: {}".format(t.__name__, e))
            failed += 1

    print("\n=== Results: {} passed, {} failed ===".format(passed, failed))
    if failed > 0:
        sys.exit(1)

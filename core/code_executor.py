import multiprocessing
import sys
import time
from dataclasses import dataclass
from io import StringIO

import config


@dataclass
class ExecutionResult:
    success: bool
    output: str
    error: str
    duration_ms: int


# Safe builtins whitelist
SAFE_BUILTINS = {
    "print": print,
    "range": range,
    "len": len,
    "int": int,
    "str": str,
    "float": float,
    "list": list,
    "dict": dict,
    "set": set,
    "tuple": tuple,
    "bool": bool,
    "type": type,
    "isinstance": isinstance,
    "issubclass": issubclass,
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "sum": sum,
    "sorted": sorted,
    "reversed": reversed,
    "enumerate": enumerate,
    "zip": zip,
    "map": map,
    "filter": filter,
    "any": any,
    "all": all,
    "chr": chr,
    "ord": ord,
    "hex": hex,
    "oct": oct,
    "bin": bin,
    "pow": pow,
    "divmod": divmod,
    "repr": repr,
    "hash": hash,
    "id": id,
    "callable": callable,
    "hasattr": hasattr,
    "format": format,
    "slice": slice,
    "complex": complex,
    "bytes": bytes,
    "bytearray": bytearray,
    "frozenset": frozenset,
    "object": object,
    "property": property,
    "super": super,
    "staticmethod": staticmethod,
    "classmethod": classmethod,
    "ValueError": ValueError,
    "TypeError": TypeError,
    "IndexError": IndexError,
    "KeyError": KeyError,
    "AttributeError": AttributeError,
    "ZeroDivisionError": ZeroDivisionError,
    "StopIteration": StopIteration,
    "Exception": Exception,
    "RuntimeError": RuntimeError,
    "OverflowError": OverflowError,
    "NotImplementedError": NotImplementedError,
    "ArithmeticError": ArithmeticError,
    "AssertionError": AssertionError,
    "EOFError": EOFError,
    "LookupError": LookupError,
    "NameError": NameError,
    "UnboundLocalError": UnboundLocalError,
    "OSError": OSError,
    "RecursionError": RecursionError,
    "IndentationError": IndentationError,
    "SyntaxError": SyntaxError,
    "TabError": TabError,
}


def _sandboxed_input(prompt=""):
    raise RuntimeError("input() 在沙箱中不可用")


def _run_code_in_process(code, result_queue):
    """Execute code in a child process with restricted builtins."""
    # Redirect stdout/stderr
    old_stdout, old_stderr = sys.stdout, sys.stderr
    captured_stdout, captured_stderr = StringIO(), StringIO()
    sys.stdout = captured_stdout
    sys.stderr = captured_stderr

    builtins_dict = dict(SAFE_BUILTINS)
    builtins_dict["input"] = _sandboxed_input
    restricted_globals = {"__builtins__": builtins_dict}

    error_msg = ""
    try:
        exec(compile(code, "<user_code>", "exec"), restricted_globals)
    except SyntaxError as e:
        error_msg = "语法错误: {}".format(e)
    except Exception as e:
        error_msg = "{}: {}".format(type(e).__name__, e)
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr

    output = captured_stdout.getvalue()
    stderr_output = captured_stderr.getvalue()

    # Truncate output
    if len(output) > config.SANDBOX_MAX_OUTPUT:
        output = output[: config.SANDBOX_MAX_OUTPUT] + "\n... (输出已截断)"

    if not error_msg and stderr_output:
        error_msg = stderr_output.strip()

    result_queue.put((output, error_msg))


def execute_code(code):
    """Run Python code in a sandboxed subprocess with timeout.

    Returns ExecutionResult with success, output, error, duration_ms.
    """
    result_queue = multiprocessing.Queue()
    start = time.monotonic()

    process = multiprocessing.Process(
        target=_run_code_in_process, args=(code, result_queue)
    )
    process.start()
    process.join(timeout=config.SANDBOX_TIMEOUT)

    duration_ms = int((time.monotonic() - start) * 1000)

    if process.is_alive():
        process.kill()
        process.join(timeout=1)
        return ExecutionResult(
            success=False,
            output="",
            error="代码执行超时（超过{}秒），可能存在无限循环。".format(
                config.SANDBOX_TIMEOUT
            ),
            duration_ms=duration_ms,
        )

    if not result_queue.empty():
        output, error = result_queue.get()
        return ExecutionResult(
            success=not bool(error),
            output=output,
            error=error,
            duration_ms=duration_ms,
        )
    else:
        return ExecutionResult(
            success=False,
            output="",
            error="代码执行异常终止",
            duration_ms=duration_ms,
        )

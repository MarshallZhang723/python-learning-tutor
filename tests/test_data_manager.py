import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import config


def test_progress_roundtrip():
    with tempfile.TemporaryDirectory() as tmpdir:
        config.DATA_DIR = Path(tmpdir)

        from core import progress_tracker

        progress_tracker._get_progress_path = lambda: os.path.join(tmpdir, "progress.json")
        progress_tracker._get_mistakes_path = lambda: os.path.join(tmpdir, "mistakes.json")

        progress = progress_tracker.load_progress()
        assert progress["completed_lessons"] == []
        assert progress["exercise_scores"] == {}
        assert progress["current_streak"] == 0

        progress_tracker.mark_lesson_complete("variables_01")
        progress = progress_tracker.load_progress()
        assert "variables_01" in progress["completed_lessons"]
        assert progress["current_streak"] == 1

        progress_tracker.record_exercise_score("variables_ex_01", 3, 5)
        progress = progress_tracker.load_progress()
        assert progress["exercise_scores"]["variables_ex_01"]["passed"] == 3
        assert progress["exercise_scores"]["variables_ex_01"]["total"] == 5

        print("[PASS] progress_roundtrip")


def test_mistakes_roundtrip():
    with tempfile.TemporaryDirectory() as tmpdir:
        config.DATA_DIR = Path(tmpdir)

        from core import progress_tracker

        progress_tracker._get_progress_path = lambda: os.path.join(tmpdir, "progress.json")
        progress_tracker._get_mistakes_path = lambda: os.path.join(tmpdir, "mistakes.json")

        mistakes = progress_tracker.load_mistakes()
        assert mistakes == []

        progress_tracker.log_mistake("ex_01", "x=1", "NameError", "解释")
        mistakes = progress_tracker.load_mistakes()
        assert len(mistakes) == 1
        assert mistakes[0]["exercise_id"] == "ex_01"
        assert mistakes[0]["error"] == "NameError"
        assert mistakes[0]["llm_explanation"] == "解释"

        print("[PASS] mistakes_roundtrip")


def test_duplicate_lesson():
    with tempfile.TemporaryDirectory() as tmpdir:
        config.DATA_DIR = Path(tmpdir)

        from core import progress_tracker

        progress_tracker._get_progress_path = lambda: os.path.join(tmpdir, "progress.json")
        progress_tracker._get_mistakes_path = lambda: os.path.join(tmpdir, "mistakes.json")

        progress_tracker.mark_lesson_complete("variables_01")
        progress_tracker.mark_lesson_complete("variables_01")
        progress = progress_tracker.load_progress()
        assert progress["completed_lessons"].count("variables_01") == 1

        print("[PASS] duplicate_lesson")


if __name__ == "__main__":
    tests = [test_progress_roundtrip, test_mistakes_roundtrip, test_duplicate_lesson]
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

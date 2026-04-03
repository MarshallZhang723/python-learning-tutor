import json
from datetime import date, datetime
from pathlib import Path

import config


def _load_json(filepath, default):
    """Load a JSON file, returning default if it doesn't exist or is corrupt."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        _save_json(filepath, default)
        return default


def _save_json(filepath, data):
    """Save data to a JSON file with UTF-8 encoding."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _get_progress_path():
    return config.DATA_DIR / "progress.json"


def _get_mistakes_path():
    return config.DATA_DIR / "mistakes.json"


def _default_progress():
    return {
        "completed_lessons": [],
        "exercise_scores": {},
        "current_streak": 0,
        "last_active": None,
    }


def load_progress():
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    return _load_json(_get_progress_path(), _default_progress())


def save_progress(progress):
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    _save_json(_get_progress_path(), progress)


def mark_lesson_complete(lesson_id):
    progress = load_progress()
    if lesson_id not in progress["completed_lessons"]:
        progress["completed_lessons"].append(lesson_id)
    _update_streak(progress)
    save_progress(progress)


def record_exercise_score(exercise_id, passed, total):
    progress = load_progress()
    progress["exercise_scores"][exercise_id] = {
        "passed": passed,
        "total": total,
        "timestamp": datetime.now().isoformat(),
    }
    _update_streak(progress)
    save_progress(progress)


def _update_streak(progress):
    today = date.today().isoformat()
    if progress["last_active"] == today:
        return
    if progress["last_active"]:
        try:
            last = date.fromisoformat(progress["last_active"])
            if (date.today() - last).days == 1:
                progress["current_streak"] += 1
            elif (date.today() - last).days > 1:
                progress["current_streak"] = 1
        except ValueError:
            progress["current_streak"] = 1
    else:
        progress["current_streak"] = 1
    progress["last_active"] = today


def load_mistakes():
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    return _load_json(_get_mistakes_path(), [])


def save_mistakes(mistakes):
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    _save_json(_get_mistakes_path(), mistakes)


def log_mistake(exercise_id, user_code, error, llm_explanation=""):
    mistakes = load_mistakes()
    mistakes.append(
        {
            "exercise_id": exercise_id,
            "user_code": user_code,
            "error": error,
            "llm_explanation": llm_explanation,
            "timestamp": datetime.now().isoformat(),
        }
    )
    save_mistakes(mistakes)

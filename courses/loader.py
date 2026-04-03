import json
from pathlib import Path

import config


def load_course(course_id):
    """Load a course module by ID. Returns the parsed JSON dict."""
    filepath = config.COURSES_DIR / "{}.json".format(course_id)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def list_courses():
    """List all available course IDs by scanning the courses directory."""
    courses = []
    for f in sorted(config.COURSES_DIR.glob("*.json")):
        try:
            with open(f, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                courses.append(
                    {"id": data.get("id", f.stem), "title": data.get("title", f.stem)}
                )
        except (json.JSONDecodeError, KeyError):
            continue
    return courses


def get_lesson(course_id, lesson_id):
    """Get a specific lesson from a course."""
    course = load_course(course_id)
    if not course:
        return None
    for lesson in course.get("lessons", []):
        if lesson["id"] == lesson_id:
            return lesson
    return None


def get_exercise(course_id, exercise_id):
    """Get a specific exercise from a course."""
    course = load_course(course_id)
    if not course:
        return None
    for ex in course.get("exercises", []):
        if ex["id"] == exercise_id:
            return ex
    return None

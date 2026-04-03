import streamlit as st


def code_editor(initial_code="", key=None, height=200, editable=True):
    """Render a code editor area. Returns the user's code string."""
    if editable:
        code = st.text_area(
            "代码编辑器",
            value=initial_code,
            height=height,
            key=key,
            help="在这里编写你的 Python 代码",
        )
    else:
        code = initial_code
        st.code(code, language="python")
    return code


def output_panel(result):
    """Display execution result (stdout/stderr)."""
    if result.success and result.output:
        st.success("运行成功")
        st.code(result.output, language="text")
    elif not result.success:
        st.error("运行失败: {}".format(result.error))
        if result.output:
            st.code(result.output, language="text")
    else:
        st.info("代码运行成功，没有输出")

    if result.duration_ms:
        st.caption("耗时: {}ms".format(result.duration_ms))


def lesson_card(lesson):
    """Render a lesson card with title, explanation, code example, and key points."""
    st.subheader(lesson["title"])
    st.markdown(lesson["explanation"])

    if lesson.get("key_points"):
        st.markdown("**要点：**")
        for point in lesson["key_points"]:
            st.markdown("- {}".format(point))

    if lesson.get("code_example"):
        st.markdown("**示例代码：**")
        st.code(lesson["code_example"], language="python")
        return lesson["code_example"]
    return ""


def exercise_card(exercise, grading_result=None):
    """Render an exercise card with description and difficulty."""
    st.subheader(exercise["title"])

    difficulty = exercise.get("difficulty", "medium")
    difficulty_emoji = {"easy": "简单", "medium": "中等", "hard": "困难"}
    st.caption("难度: {}".format(difficulty_emoji.get(difficulty, difficulty)))

    st.markdown(exercise["description"])

    if grading_result:
        st.markdown("---")
        if grading_result.all_passed:
            st.success("所有测试通过！({}/{})".format(grading_result.passed, grading_result.total))
        else:
            st.warning("通过 {}/{} 个测试".format(grading_result.passed, grading_result.total))
            for detail in grading_result.details:
                if detail.passed:
                    st.markdown(
                        "- **通过** `{}`：期望 `{}`，实际 `{}`".format(
                            detail.input_desc, detail.expected, detail.actual
                        )
                    )
                else:
                    st.markdown(
                        "- **失败** `{}`：期望 `{}`，实际 `{}`".format(
                            detail.input_desc, detail.expected, detail.actual
                        )
                    )


def sidebar_progress(progress):
    """Show progress overview in the sidebar."""
    completed = len(progress.get("completed_lessons", []))
    scores = progress.get("exercise_scores", {})
    streak = progress.get("current_streak", 0)

    st.sidebar.markdown("---")
    st.sidebar.markdown("**学习进度**")
    st.sidebar.metric("已完成课程", completed)
    st.sidebar.metric("已做练习", len(scores))
    st.sidebar.metric("连续学习天数", streak)

    # Completion rate for exercises
    if scores:
        perfect = sum(1 for s in scores.values() if s["passed"] == s["total"])
        st.sidebar.metric(
            "满分练习", "{}/{}".format(perfect, len(scores))
        )

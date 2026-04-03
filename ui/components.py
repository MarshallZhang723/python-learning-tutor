import streamlit as st


def code_editor(initial_code="", key=None, height=200, editable=True):
    """Render a code editor area. Returns the user's code string."""
    if editable:
        code = st.text_area(
            "代码编辑器",
            value=initial_code,
            height=height,
            key=key,
            label_visibility="collapsed",
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
    st.markdown('<div class="content-card">', unsafe_allow_html=True)

    st.markdown(
        '<h2>{}</h2>'.format(lesson["title"]),
        unsafe_allow_html=True,
    )

    st.markdown(lesson["explanation"])

    if lesson.get("key_points"):
        items = "".join(
            '<li>{}</li>'.format(p) for p in lesson["key_points"]
        )
        st.markdown(
            '<ul class="key-points">{}</ul>'.format(items),
            unsafe_allow_html=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)

    example_code = ""
    if lesson.get("code_example"):
        st.markdown(
            '<div class="code-label">示例代码</div>',
            unsafe_allow_html=True,
        )
        st.code(lesson["code_example"], language="python")
        example_code = lesson["code_example"]

    return example_code


def exercise_card(exercise, grading_result=None):
    """Render an exercise card with description and difficulty."""
    difficulty = exercise.get("difficulty", "medium")
    difficulty_map = {
        "easy": ("简单", "badge-easy"),
        "medium": ("中等", "badge-medium"),
        "hard": ("困难", "badge-hard"),
    }
    label, badge_class = difficulty_map.get(difficulty, ("中等", "badge-medium"))

    st.markdown(
        '<div class="content-card">'
        '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.8rem;">'
        '<h2 style="margin:0;">{}</h2>'
        '<span class="badge {}">{}</span>'
        '</div>'
        '<p>{}</p>'
        '</div>'.format(exercise["title"], badge_class, label, exercise["description"]),
        unsafe_allow_html=True,
    )

    if grading_result:
        if grading_result.all_passed:
            st.success(
                "所有测试通过！({}/{})".format(
                    grading_result.passed, grading_result.total
                )
            )
        else:
            st.warning(
                "通过 {}/{} 个测试".format(
                    grading_result.passed, grading_result.total
                )
            )
            for detail in grading_result.details:
                icon = "通过" if detail.passed else "失败"
                st.markdown(
                    "- **{}** `{}`：期望 `{}`，实际 `{}`".format(
                        icon, detail.input_desc, detail.expected, detail.actual
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

    if scores:
        perfect = sum(1 for s in scores.values() if s["passed"] == s["total"])
        st.sidebar.metric(
            "满分练习", "{}/{}".format(perfect, len(scores))
        )

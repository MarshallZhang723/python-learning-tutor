import streamlit as st

from core.code_executor import execute_code
from core.grader import grade_exercise
from core.progress_tracker import (
    load_mistakes,
    load_progress,
    log_mistake,
    mark_lesson_complete,
    record_exercise_score,
)
from courses.loader import get_exercise, get_lesson, list_courses, load_course
from ui.components import code_editor, exercise_card, lesson_card, output_panel


def welcome_page():
    # Apple-style landing page using Streamlit native components
    # Empty rows for vertical centering
    for _ in range(6):
        st.write("")

    # Title
    st.markdown(
        "<h1 style='text-align:center; font-size:3.5rem; font-weight:700; "
        "color:#1d1d1f; letter-spacing:-0.02em; margin-bottom:0;'>"
        "Welcome to Python</h1>",
        unsafe_allow_html=True,
    )

    # Subtitle
    st.markdown(
        "<p style='text-align:center; font-size:1.25rem; color:#6e6e73; "
        "margin-top:0.5rem; margin-bottom:1.5rem;'>"
        "交互式学习，从这里开始</p>",
        unsafe_allow_html=True,
    )

    # Button centered
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("开始学习", use_container_width=True, type="primary"):
            st.session_state["current_page"] = "学习"
            st.rerun()


def lesson_page():
    st.title("学习")

    courses = list_courses()
    if not courses:
        st.warning("暂无课程内容")
        return

    course_options = {c["title"]: c["id"] for c in courses}
    selected_title = st.selectbox("选择课程", list(course_options.keys()))
    course_id = course_options[selected_title]

    course = load_course(course_id)
    if not course:
        st.error("无法加载课程: {}".format(course_id))
        return

    st.markdown(course["description"])
    st.markdown("---")

    lessons = course.get("lessons", [])
    lesson_titles = {l["title"]: l["id"] for l in lessons}

    if not lessons:
        st.warning("该课程暂无内容")
        return

    selected_lesson_title = st.selectbox("选择章节", list(lesson_titles.keys()))
    lesson_id = lesson_titles[selected_lesson_title]

    lesson = get_lesson(course_id, lesson_id)
    if not lesson:
        st.error("无法加载章节")
        return

    example_code = lesson_card(lesson)

    if example_code:
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("运行示例代码", key="run_example"):
                with st.spinner("运行中..."):
                    result = execute_code(example_code)
                    st.session_state["last_run_result"] = result
        with col2:
            if st.button("标记为已学", key="mark_learned"):
                mark_lesson_complete(lesson_id)
                st.success("已标记「{}」为已学！".format(lesson["title"]))

    if "last_run_result" in st.session_state:
        output_panel(st.session_state["last_run_result"])


def practice_page():
    st.title("练习")

    courses = list_courses()
    if not courses:
        st.warning("暂无课程内容")
        return

    course_options = {c["title"]: c["id"] for c in courses}
    selected_title = st.selectbox("选择课程", list(course_options.keys()))
    course_id = course_options[selected_title]

    course = load_course(course_id)
    exercises = course.get("exercises", [])
    if not exercises:
        st.warning("该课程暂无练习")
        return

    ex_titles = {e["title"]: e["id"] for e in exercises}
    selected_ex_title = st.selectbox("选择题目", list(ex_titles.keys()))
    exercise_id = ex_titles[selected_ex_title]

    exercise = get_exercise(course_id, exercise_id)
    if not exercise:
        st.error("无法加载练习")
        return

    grading_result = st.session_state.get("grading_result_{}".format(exercise_id))
    exercise_card(exercise, grading_result)

    starter = exercise.get("starter_code", "# 在这里写你的代码\n")
    user_code = code_editor(
        initial_code=starter,
        key="exercise_editor_{}".format(exercise_id),
        height=250,
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("运行代码", key="run_{}".format(exercise_id)):
            with st.spinner("运行中..."):
                result = execute_code(user_code)
                st.session_state["run_result_{}".format(exercise_id)] = result
    with col2:
        if st.button("提交评分", key="submit_{}".format(exercise_id)):
            with st.spinner("评分中..."):
                grading = grade_exercise(user_code, exercise.get("test_cases", []))
                st.session_state["grading_result_{}".format(exercise_id)] = grading
                record_exercise_score(
                    exercise_id, grading.passed, grading.total
                )
                # If failed, try LLM diagnosis
                if not grading.all_passed and grading.details:
                    errors = [
                        d.actual for d in grading.details if not d.passed
                    ]
                    st.session_state["needs_diagnosis_{}".format(exercise_id)] = {
                        "code": user_code,
                        "error": "; ".join(errors),
                    }
                st.rerun()

    run_key = "run_result_{}".format(exercise_id)
    if run_key in st.session_state:
        output_panel(st.session_state[run_key])

    # Auto LLM diagnosis after failed submission
    diag_key = "needs_diagnosis_{}".format(exercise_id)
    if diag_key in st.session_state and "llm_client" in st.session_state:
        diag = st.session_state[diag_key]
        st.markdown("---")
        st.subheader("AI 诊断")
        with st.spinner("正在分析错误..."):
            try:
                llm = st.session_state["llm_client"]
                explanation = llm.analyze_error(diag["code"], diag["error"])
                st.markdown(explanation)
                log_mistake(exercise_id, diag["code"], diag["error"], explanation)
            except Exception as e:
                st.error("LLM 分析失败: {}".format(e))
                log_mistake(exercise_id, diag["code"], diag["error"], "")
        del st.session_state[diag_key]


def ask_page():
    st.title("提问")

    if "llm_client" not in st.session_state:
        st.warning("请先配置 ANTHROPIC_API_KEY 环境变量")
        return

    user_code = st.text_area(
        "粘贴你的 Python 代码",
        value="# 在这里粘贴你的代码\n",
        height=200,
    )
    user_question = st.text_area(
        "你的问题",
        value="",
        height=100,
        placeholder="例如：这段代码为什么会报错？如何优化这段代码？",
    )

    if st.button("提问", key="ask_btn"):
        if not user_question.strip():
            st.warning("请输入你的问题")
            return
        with st.spinner("AI 正在思考..."):
            try:
                llm = st.session_state["llm_client"]
                st.markdown("**回答：**")
                st.write_stream(
                    llm.answer_question_stream(user_code, user_question)
                )
            except Exception as e:
                st.error("调用 LLM 失败: {}".format(e))


def dashboard_page():
    st.title("学习进度")

    progress = load_progress()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("已完成课程", len(progress.get("completed_lessons", [])))
    with col2:
        st.metric("已做练习", len(progress.get("exercise_scores", {})))
    with col3:
        st.metric("连续学习天数", progress.get("current_streak", 0))

    # Completed lessons
    if progress.get("completed_lessons"):
        st.subheader("已完成的课程")
        for lid in progress["completed_lessons"]:
            st.markdown("- {}".format(lid))

    # Exercise scores
    scores = progress.get("exercise_scores", {})
    if scores:
        st.subheader("练习成绩")
        for ex_id, info in scores.items():
            status = "通过" if info["passed"] == info["total"] else "未通过"
            st.markdown(
                "- **{}**：{}/{} ({})".format(
                    ex_id, info["passed"], info["total"], status
                )
            )

    # Mistakes
    mistakes = load_mistakes()
    if mistakes:
        st.subheader("错题记录 (最近 10 条)")
        for m in reversed(mistakes[-10:]):
            with st.expander(
                "{} - {}".format(m["exercise_id"], m["timestamp"][:16])
            ):
                st.code(m["user_code"], language="python")
                st.error(m["error"])
                if m.get("llm_explanation"):
                    st.markdown("**AI 解释：**")
                    st.markdown(m["llm_explanation"])

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

# Global Apple-inspired CSS theme
GLOBAL_CSS = """
<style>
/* ── Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* ── Landing page hero ── */
.hero-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 70vh;
    padding: 2rem 1rem;
}
.hero-title {
    font-size: 3.8rem;
    font-weight: 700;
    color: #1d1d1f;
    letter-spacing: -0.04em;
    margin: 0;
    line-height: 1.1;
}
.hero-subtitle {
    font-size: 1.2rem;
    color: #86868b;
    margin-top: 1rem;
    margin-bottom: 2.5rem;
    font-weight: 400;
}

/* ── Cards ── */
.card {
    background: #ffffff;
    border: 1px solid #e5e5ea;
    border-radius: 16px;
    padding: 1.5rem 2rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    transition: box-shadow 0.2s ease;
}
.card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

/* ── Metric cards ── */
.metric-card {
    background: linear-gradient(135deg, #f5f5f7 0%, #ffffff 100%);
    border: 1px solid #e5e5ea;
    border-radius: 14px;
    padding: 1.5rem;
    text-align: center;
}
.metric-value {
    font-size: 2.4rem;
    font-weight: 700;
    color: #1d1d1f;
    line-height: 1;
}
.metric-label {
    font-size: 0.85rem;
    color: #86868b;
    margin-top: 0.4rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* ── Section headers ── */
.section-title {
    font-size: 1.4rem;
    font-weight: 600;
    color: #1d1d1f;
    margin-top: 2rem;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #e5e5ea;
}

/* ── Key points list ── */
.key-point {
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
    padding: 0.5rem 0;
    font-size: 0.95rem;
    color: #333;
}
.key-point::before {
    content: "✦";
    color: #007aff;
    font-weight: 700;
    flex-shrink: 0;
}

/* ── Difficulty badges ── */
.badge {
    display: inline-block;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.03em;
}
.badge-easy { background: #e8f5e9; color: #2e7d32; }
.badge-medium { background: #fff3e0; color: #e65100; }
.badge-hard { background: #fce4ec; color: #c62828; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #f5f5f7;
    border-right: 1px solid #e5e5ea;
}

/* ── Buttons ── */
.stButton > button {
    border-radius: 12px !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(0,122,255,0.3) !important;
}

/* ── Code blocks ── */
.stCodeBlock, pre {
    border-radius: 12px !important;
    border: 1px solid #e5e5ea !important;
}

/* ── Text areas ── */
.stTextArea textarea {
    border-radius: 12px !important;
    border: 1px solid #d2d2d7 !important;
    font-family: 'SF Mono', 'Fira Code', monospace !important;
}

/* ── Select boxes ── */
.stSelectbox div[data-baseweb="select"] {
    border-radius: 10px !important;
}

/* ── Mistake items ── */
.mistake-item {
    background: #fff5f5;
    border-left: 3px solid #ff3b30;
    border-radius: 0 10px 10px 0;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
}
</style>
"""


def _inject_css():
    """Inject global CSS once per session."""
    if not st.session_state.get("_css_injected"):
        st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
        st.session_state["_css_injected"] = True


def welcome_page():
    _inject_css()

    st.markdown(
        """
        <div class="hero-wrapper">
            <h1 class="hero-title">Welcome to Python</h1>
            <p class="hero-subtitle">交互式学习，从这里开始</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("开始学习", use_container_width=True, type="primary"):
            st.session_state["current_page"] = "学习"
            st.rerun()


def lesson_page():
    _inject_css()

    st.markdown('<h1 style="font-size:2rem;font-weight:700;color:#1d1d1f;">学习</h1>', unsafe_allow_html=True)

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

    st.markdown(
        '<p style="color:#86868b;font-size:1rem;margin-bottom:0.5rem;">{}</p>'.format(
            course["description"]
        ),
        unsafe_allow_html=True,
    )

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
    _inject_css()

    st.markdown('<h1 style="font-size:2rem;font-weight:700;color:#1d1d1f;">练习</h1>', unsafe_allow_html=True)

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
    _inject_css()

    st.markdown('<h1 style="font-size:2rem;font-weight:700;color:#1d1d1f;">提问</h1>', unsafe_allow_html=True)

    if "llm_client" not in st.session_state:
        st.warning("请先配置 ANTHROPIC_API_KEY 环境变量")
        return

    st.markdown('<div class="card">', unsafe_allow_html=True)
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
    st.markdown('</div>', unsafe_allow_html=True)

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
    _inject_css()

    st.markdown(
        '<h1 style="font-size:2rem;font-weight:700;color:#1d1d1f;">学习进度</h1>',
        unsafe_allow_html=True,
    )

    progress = load_progress()

    # Metric cards
    m1, m2, m3 = st.columns(3)
    metrics = [
        (m1, len(progress.get("completed_lessons", [])), "已完成课程"),
        (m2, len(progress.get("exercise_scores", {})), "已做练习"),
        (m3, progress.get("current_streak", 0), "连续学习天数"),
    ]
    for col, value, label in metrics:
        with col:
            st.markdown(
                '<div class="metric-card">'
                '<div class="metric-value">{}</div>'
                '<div class="metric-label">{}</div>'
                '</div>'.format(value, label),
                unsafe_allow_html=True,
            )

    # Completed lessons
    if progress.get("completed_lessons"):
        st.markdown('<div class="section-title">已完成的课程</div>', unsafe_allow_html=True)
        for lid in progress["completed_lessons"]:
            st.markdown(
                '<div class="card" style="padding:0.8rem 1.2rem;">{}</div>'.format(lid),
                unsafe_allow_html=True,
            )

    # Exercise scores
    scores = progress.get("exercise_scores", {})
    if scores:
        st.markdown('<div class="section-title">练习成绩</div>', unsafe_allow_html=True)
        for ex_id, info in scores.items():
            passed = info["passed"] == info["total"]
            badge_class = "badge-easy" if passed else "badge-hard"
            status = "通过" if passed else "未通过"
            st.markdown(
                '<div class="card" style="display:flex;justify-content:space-between;align-items:center;padding:0.8rem 1.2rem;">'
                '<strong>{}</strong>'
                '<span>{} / {} <span class="badge {}">{}</span></span>'
                '</div>'.format(ex_id, info["passed"], info["total"], badge_class, status),
                unsafe_allow_html=True,
            )

    # Mistakes
    mistakes = load_mistakes()
    if mistakes:
        st.markdown(
            '<div class="section-title">错题记录 (最近 10 条)</div>',
            unsafe_allow_html=True,
        )
        for m in reversed(mistakes[-10:]):
            with st.expander(
                "{} - {}".format(m["exercise_id"], m["timestamp"][:16])
            ):
                st.code(m["user_code"], language="python")
                st.error(m["error"])
                if m.get("llm_explanation"):
                    st.markdown("**AI 解释：**")
                    st.markdown(m["llm_explanation"])

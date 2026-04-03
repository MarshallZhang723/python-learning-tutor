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

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400&family=Source+Sans+3:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --ink: #1a1a2e;
    --paper: #faf8f5;
    --paper-warm: #f3efe8;
    --accent: #e85d26;
    --accent-glow: #ff7a45;
    --sage: #4a7c59;
    --sage-light: #e8f0eb;
    --slate: #6b7280;
    --mist: #e8e4de;
    --code-bg: #1e1e2e;
    --code-fg: #cdd6f4;
    --success-bg: #ecfdf5;
    --success-border: #4a7c59;
    --error-bg: #fef2f2;
    --error-border: #dc2626;
    --warning-bg: #fffbeb;
    --warning-border: #d97706;
    --radius: 14px;
    --radius-sm: 8px;
    --shadow-sm: 0 1px 2px rgba(26,26,46,0.05);
    --shadow-md: 0 4px 16px rgba(26,26,46,0.08);
    --shadow-lg: 0 8px 32px rgba(26,26,46,0.12);
    --shadow-glow: 0 0 40px rgba(232,93,38,0.15);
}

/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'Source Sans 3', -apple-system, sans-serif !important;
    background: var(--paper) !important;
    color: var(--ink) !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--ink) !important;
    border-right: none !important;
    padding-top: 1rem;
}
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] .stRadio span,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #e8e4de !important;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
    padding: 0.5rem 1rem !important;
    border-radius: var(--radius-sm) !important;
    transition: all 0.2s ease !important;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
    background: rgba(255,255,255,0.08) !important;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.1) !important;
}
[data-testid="stSidebar"] [data-testid="stMetric"] {
    background: rgba(255,255,255,0.05) !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.8rem !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
}
[data-testid="stSidebar"] [data-testid="stMetric"] label {
    color: #9ca3af !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
[data-testid="stSidebar"] [data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: var(--accent-glow) !important;
    font-family: 'Playfair Display', serif !important;
    font-size: 1.6rem !important;
}

/* ── Hero / Landing ── */
.hero {
    min-height: 85vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(ellipse at 30% 50%, rgba(232,93,38,0.06) 0%, transparent 50%),
                radial-gradient(ellipse at 70% 30%, rgba(74,124,89,0.05) 0%, transparent 50%),
                radial-gradient(ellipse at 50% 80%, rgba(232,93,38,0.03) 0%, transparent 40%);
    animation: drift 20s ease-in-out infinite alternate;
    pointer-events: none;
}
@keyframes drift {
    0% { transform: translate(0, 0) rotate(0deg); }
    100% { transform: translate(2%, -1%) rotate(2deg); }
}
.hero-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    font-weight: 500;
    color: var(--accent);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
    opacity: 0;
    animation: fadeUp 0.8s ease 0.2s forwards;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(2.8rem, 6vw, 5rem);
    font-weight: 900;
    color: var(--ink);
    line-height: 1.05;
    margin: 0;
    letter-spacing: -0.03em;
    opacity: 0;
    animation: fadeUp 0.8s ease 0.4s forwards;
}
.hero-title em {
    font-style: italic;
    color: var(--accent);
}
.hero-divider {
    width: 60px;
    height: 3px;
    background: var(--accent);
    margin: 1.5rem auto;
    border-radius: 2px;
    opacity: 0;
    animation: fadeUp 0.8s ease 0.6s forwards;
}
.hero-subtitle {
    font-family: 'Source Sans 3', sans-serif;
    font-size: 1.15rem;
    color: var(--slate);
    font-weight: 400;
    margin: 0 0 2.5rem 0;
    max-width: 400px;
    opacity: 0;
    animation: fadeUp 0.8s ease 0.8s forwards;
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* ── Page header ── */
.page-header {
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--mist);
}
.page-header h1 {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem;
    font-weight: 900;
    color: var(--ink);
    margin: 0;
    letter-spacing: -0.02em;
}
.page-header p {
    color: var(--slate);
    font-size: 0.95rem;
    margin: 0.3rem 0 0 0;
}

/* ── Content cards ── */
.content-card {
    background: #fff;
    border: 1px solid var(--mist);
    border-radius: var(--radius);
    padding: 2rem 2.2rem;
    margin-bottom: 1.5rem;
    box-shadow: var(--shadow-sm);
    transition: box-shadow 0.3s ease, transform 0.3s ease;
}
.content-card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
}
.content-card h2 {
    font-family: 'Playfair Display', serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--ink);
    margin: 0 0 1rem 0;
}
.content-card p {
    line-height: 1.8;
    color: #374151;
}

/* ── Key points ── */
.key-points {
    list-style: none;
    padding: 0;
    margin: 1rem 0 0 0;
}
.key-points li {
    position: relative;
    padding: 0.6rem 0 0.6rem 2rem;
    font-size: 0.95rem;
    color: var(--ink);
    border-bottom: 1px solid #f3f1ed;
}
.key-points li:last-child {
    border-bottom: none;
}
.key-points li::before {
    content: '';
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--accent);
}

/* ── Code display ── */
.code-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    color: var(--accent);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin: 1.5rem 0 0.5rem 0;
}
.stCodeBlock {
    border-radius: var(--radius) !important;
    overflow: hidden !important;
    box-shadow: var(--shadow-md) !important;
}
.stCodeBlock > div {
    background: var(--code-bg) !important;
}

/* ── Difficulty badges ── */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.25rem 0.8rem;
    border-radius: 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.badge-easy { background: var(--sage-light); color: var(--sage); }
.badge-medium { background: var(--warning-bg); color: var(--warning-border); }
.badge-hard { background: var(--error-bg); color: var(--error-border); }

/* ── Metric cards (dashboard) ── */
.metric-wrap {
    background: #fff;
    border: 1px solid var(--mist);
    border-radius: var(--radius);
    padding: 1.8rem 1.5rem;
    text-align: center;
    box-shadow: var(--shadow-sm);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.metric-wrap::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent), var(--sage));
    transform: scaleX(0);
    transition: transform 0.3s ease;
}
.metric-wrap:hover::after {
    transform: scaleX(1);
}
.metric-wrap:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-3px);
}
.metric-num {
    font-family: 'Playfair Display', serif;
    font-size: 3rem;
    font-weight: 900;
    color: var(--ink);
    line-height: 1;
}
.metric-lbl {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: var(--slate);
    margin-top: 0.5rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

/* ── Section titles ── */
.section-label {
    font-family: 'Playfair Display', serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--ink);
    margin: 2.5rem 0 1rem 0;
    padding-bottom: 0.6rem;
    border-bottom: 2px solid var(--ink);
    display: inline-block;
}

/* ── Score rows ── */
.score-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #fff;
    border: 1px solid var(--mist);
    border-radius: var(--radius-sm);
    padding: 0.9rem 1.3rem;
    margin-bottom: 0.5rem;
    transition: all 0.2s ease;
}
.score-row:hover {
    box-shadow: var(--shadow-sm);
    transform: translateX(4px);
}

/* ── Buttons ── */
.stButton > button {
    border-radius: var(--radius-sm) !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.65rem 1.8rem !important;
    transition: all 0.25s ease !important;
    border: none !important;
    letter-spacing: 0.02em !important;
}
.stButton > button[kind="primary"] {
    background: var(--accent) !important;
    color: #fff !important;
    box-shadow: 0 2px 8px rgba(232,93,38,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    background: var(--accent-glow) !important;
    box-shadow: 0 4px 16px rgba(232,93,38,0.4) !important;
    transform: translateY(-2px) !important;
}
.stButton > button:not([kind="primary"]) {
    background: #fff !important;
    color: var(--ink) !important;
    border: 1px solid var(--mist) !important;
}
.stButton > button:not([kind="primary"]):hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    transform: translateY(-1px) !important;
}

/* ── Text areas ── */
.stTextArea textarea {
    border-radius: var(--radius-sm) !important;
    border: 1px solid var(--mist) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.9rem !important;
    background: var(--code-bg) !important;
    color: var(--code-fg) !important;
    transition: border-color 0.2s ease !important;
}
.stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(232,93,38,0.1) !important;
}

/* ── Select boxes ── */
.stSelectbox label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--slate) !important;
}
.stSelectbox div[data-baseweb="select"] {
    border-radius: var(--radius-sm) !important;
    border-color: var(--mist) !important;
}

/* ── Alerts ── */
.stSuccess, .stError, .stWarning, .stInfo {
    border-radius: var(--radius-sm) !important;
    border-left-width: 4px !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    font-family: 'Source Sans 3', sans-serif !important;
    font-weight: 600 !important;
}

/* ── Main content area ── */
.main .block-container {
    padding-top: 2rem !important;
    max-width: 900px !important;
}
</style>
"""


def _inject_css():
    if not st.session_state.get("_css_injected"):
        st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
        st.session_state["_css_injected"] = True


def welcome_page():
    _inject_css()

    st.markdown(
        """
        <div class="hero">
            <div class="hero-label">Interactive Python Tutorial</div>
            <h1 class="hero-title">Welcome to<br><em>Python</em></h1>
            <div class="hero-divider"></div>
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

    st.markdown(
        '<div class="page-header"><h1>学习</h1><p>选择课程和章节，开始你的 Python 之旅</p></div>',
        unsafe_allow_html=True,
    )

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
        '<p style="color:var(--slate);font-size:0.95rem;margin-bottom:1rem;font-style:italic;">{}</p>'.format(
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
        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("运行示例代码", key="run_example"):
                with st.spinner("运行中..."):
                    result = execute_code(example_code)
                    st.session_state["last_run_result"] = result
        with c2:
            if st.button("标记为已学", key="mark_learned"):
                mark_lesson_complete(lesson_id)
                st.success("已标记「{}」为已学！".format(lesson["title"]))

    if "last_run_result" in st.session_state:
        output_panel(st.session_state["last_run_result"])


def practice_page():
    _inject_css()

    st.markdown(
        '<div class="page-header"><h1>练习</h1><p>动手编写代码，检验学习成果</p></div>',
        unsafe_allow_html=True,
    )

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

    st.markdown('<div class="code-label">代码编辑器</div>', unsafe_allow_html=True)
    starter = exercise.get("starter_code", "# 在这里写你的代码\n")
    user_code = code_editor(
        initial_code=starter,
        key="exercise_editor_{}".format(exercise_id),
        height=250,
    )

    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        if st.button("运行代码", key="run_{}".format(exercise_id)):
            with st.spinner("运行中..."):
                result = execute_code(user_code)
                st.session_state["run_result_{}".format(exercise_id)] = result
    with c2:
        if st.button("提交评分", key="submit_{}".format(exercise_id), type="primary"):
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
        st.markdown('<div class="code-label">AI 诊断</div>', unsafe_allow_html=True)
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

    st.markdown(
        '<div class="page-header"><h1>提问</h1><p>粘贴代码，AI 为你解答疑惑</p></div>',
        unsafe_allow_html=True,
    )

    if "llm_client" not in st.session_state:
        st.warning("请先配置 ANTHROPIC_API_KEY 环境变量")
        return

    st.markdown('<div class="content-card">', unsafe_allow_html=True)
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

    if st.button("提问", key="ask_btn", type="primary"):
        if not user_question.strip():
            st.warning("请输入你的问题")
            return
        with st.spinner("AI 正在思考..."):
            try:
                llm = st.session_state["llm_client"]
                st.markdown('<div class="code-label">回答</div>', unsafe_allow_html=True)
                st.markdown('<div class="content-card">', unsafe_allow_html=True)
                st.write_stream(
                    llm.answer_question_stream(user_code, user_question)
                )
                st.markdown('</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error("调用 LLM 失败: {}".format(e))


def dashboard_page():
    _inject_css()

    st.markdown(
        '<div class="page-header"><h1>学习进度</h1><p>回顾你的学习旅程</p></div>',
        unsafe_allow_html=True,
    )

    progress = load_progress()

    m1, m2, m3 = st.columns(3)
    metrics = [
        (m1, len(progress.get("completed_lessons", [])), "已完成课程"),
        (m2, len(progress.get("exercise_scores", {})), "已做练习"),
        (m3, progress.get("current_streak", 0), "连续学习天数"),
    ]
    for col, value, label in metrics:
        with col:
            st.markdown(
                '<div class="metric-wrap">'
                '<div class="metric-num">{}</div>'
                '<div class="metric-lbl">{}</div>'
                '</div>'.format(value, label),
                unsafe_allow_html=True,
            )

    if progress.get("completed_lessons"):
        st.markdown('<div class="section-label">已完成的课程</div>', unsafe_allow_html=True)
        for lid in progress["completed_lessons"]:
            st.markdown(
                '<div class="content-card" style="padding:0.8rem 1.4rem;">&#10003; {}</div>'.format(lid),
                unsafe_allow_html=True,
            )

    scores = progress.get("exercise_scores", {})
    if scores:
        st.markdown('<div class="section-label">练习成绩</div>', unsafe_allow_html=True)
        for ex_id, info in scores.items():
            passed = info["passed"] == info["total"]
            badge_class = "badge-easy" if passed else "badge-hard"
            status = "通过" if passed else "未通过"
            st.markdown(
                '<div class="score-row">'
                '<strong>{}</strong>'
                '<span>{} / {} <span class="badge {}">{}</span></span>'
                '</div>'.format(ex_id, info["passed"], info["total"], badge_class, status),
                unsafe_allow_html=True,
            )

    mistakes = load_mistakes()
    if mistakes:
        st.markdown(
            '<div class="section-label">错题记录 (最近 10 条)</div>',
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

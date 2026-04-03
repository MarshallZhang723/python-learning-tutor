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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

:root {
    --black: #1d1d1f;
    --gray-1: #6e6e73;
    --gray-2: #86868b;
    --gray-3: #d2d2d7;
    --gray-4: #e8e8ed;
    --gray-5: #f5f5f7;
    --white: #ffffff;
    --blue: #0077ed;
    --blue-hover: #0071e3;
    --green: #34c759;
    --red: #ff3b30;
    --orange: #ff9500;
    --purple: #af52de;
    --teal: #5ac8fa;
    --blue-bg: rgba(0,119,237,0.08);
    --green-bg: rgba(52,199,89,0.08);
    --red-bg: rgba(255,59,48,0.08);
    --orange-bg: rgba(255,149,0,0.08);
}

/* ═══════════════════════════════════════════
   BASE — Apple's clean foundation
   ═══════════════════════════════════════════ */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text',
                 'Helvetica Neue', 'Inter', sans-serif !important;
    background: var(--white) !important;
    color: var(--black) !important;
    -webkit-font-smoothing: antialiased !important;
    -moz-osx-font-smoothing: grayscale !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header {
    visibility: hidden !important;
}
.main .block-container {
    max-width: 980px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 4rem !important;
}

/* ═══════════════════════════════════════════
   SIDEBAR — Apple dark nav
   ═══════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: var(--black) !important;
    border-right: none !important;
    padding: 1.5rem 1rem !important;
}
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] .stRadio span,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    color: var(--gray-3) !important;
    font-size: 0.85rem !important;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
    padding: 0.6rem 0.9rem !important;
    border-radius: 8px !important;
    transition: all 0.15s ease !important;
    margin-bottom: 2px !important;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) {
    background: rgba(255,255,255,0.12) !important;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) span {
    color: var(--white) !important;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
    background: rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.08) !important;
}
[data-testid="stSidebar"] [data-testid="stMetric"] {
    background: transparent !important;
    border: none !important;
    padding: 0.5rem 0 !important;
}
[data-testid="stSidebar"] [data-testid="stMetric"] label {
    color: var(--gray-2) !important;
    font-size: 0.7rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}
[data-testid="stSidebar"] [data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: var(--white) !important;
    font-size: 1.4rem !important;
    font-weight: 600 !important;
}

/* ═══════════════════════════════════════════
   HERO — Apple.com landing
   ═══════════════════════════════════════════ */
.hero {
    padding: 5rem 0 2rem 0;
    text-align: center;
    position: relative;
}
.hero-eyebrow {
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--gray-1);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
    opacity: 0;
    animation: appleFade 1s ease 0.1s forwards;
}
.hero-title {
    font-size: clamp(3rem, 7vw, 5.5rem);
    font-weight: 800;
    color: var(--black);
    line-height: 1.05;
    margin: 0 0 0.3rem 0;
    letter-spacing: -0.025em;
    opacity: 0;
    animation: appleFade 1s ease 0.25s forwards;
}
.hero-title-gradient {
    background: linear-gradient(135deg, var(--blue) 0%, var(--purple) 50%, var(--orange) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-subtitle {
    font-size: 1.2rem;
    font-weight: 400;
    color: var(--gray-1);
    margin: 0.8rem 0 2rem 0;
    opacity: 0;
    animation: appleFade 1s ease 0.4s forwards;
}
@keyframes appleFade {
    from { opacity: 0; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
}

/* ═══════════════════════════════════════════
   TYPOGRAPHY — Apple hierarchy
   ═══════════════════════════════════════════ */
.page-title {
    font-size: 2.8rem;
    font-weight: 800;
    color: var(--black);
    letter-spacing: -0.02em;
    margin: 2rem 0 0.3rem 0;
    line-height: 1.1;
}
.page-desc {
    font-size: 1.05rem;
    color: var(--gray-1);
    margin: 0 0 2rem 0;
    font-weight: 400;
    line-height: 1.5;
}
.section-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--black);
    margin: 2.5rem 0 1rem 0;
    letter-spacing: -0.01em;
}
.card-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--black);
    margin: 0 0 0.8rem 0;
    letter-spacing: -0.01em;
}

/* ═══════════════════════════════════════════
   CARDS — Apple frosted glass
   ═══════════════════════════════════════════ */
.apple-card {
    background: var(--white);
    border: 1px solid var(--gray-4);
    border-radius: 18px;
    padding: 2rem 2.4rem;
    margin-bottom: 1.2rem;
    transition: all 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
    box-shadow: 0 0 0 rgba(0,0,0,0);
}
.apple-card:hover {
    border-color: var(--gray-3);
    box-shadow: 0 4px 24px rgba(0,0,0,0.06), 0 1px 4px rgba(0,0,0,0.04);
    transform: translateY(-2px);
}
.apple-card p {
    line-height: 1.7;
    color: #424245;
    font-size: 0.95rem;
}

/* ═══════════════════════════════════════════
   KEY POINTS — Apple list style
   ═══════════════════════════════════════════ */
.apple-points {
    list-style: none;
    padding: 0;
    margin: 1.2rem 0 0 0;
}
.apple-points li {
    display: flex;
    align-items: flex-start;
    gap: 0.7rem;
    padding: 0.7rem 0;
    font-size: 0.92rem;
    color: var(--black);
    border-bottom: 1px solid var(--gray-5);
}
.apple-points li:last-child { border-bottom: none; }
.apple-points li .dot {
    width: 6px;
    height: 6px;
    min-width: 6px;
    border-radius: 50%;
    background: var(--blue);
    margin-top: 0.45rem;
}

/* ═══════════════════════════════════════════
   CODE — Apple developer aesthetic
   ═══════════════════════════════════════════ */
.code-section-label {
    font-size: 0.7rem;
    font-weight: 600;
    color: var(--gray-1);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin: 1.5rem 0 0.5rem 0;
}
.stCodeBlock {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid var(--gray-4) !important;
    box-shadow: none !important;
}
.stCodeBlock > div {
    background: var(--black) !important;
}

/* ═══════════════════════════════════════════
   BADGES — Apple product colors
   ═══════════════════════════════════════════ */
.apple-badge {
    display: inline-flex;
    align-items: center;
    padding: 0.2rem 0.7rem;
    border-radius: 980px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}
.apple-badge.green { background: var(--green-bg); color: #1a8d3a; }
.apple-badge.orange { background: var(--orange-bg); color: #c76100; }
.apple-badge.red { background: var(--red-bg); color: #c72c24; }

/* ═══════════════════════════════════════════
   METRICS — Apple product page numbers
   ═══════════════════════════════════════════ */
.metric-block {
    text-align: center;
    padding: 1.5rem 1rem;
}
.metric-big {
    font-size: 3.2rem;
    font-weight: 800;
    color: var(--black);
    line-height: 1;
    letter-spacing: -0.03em;
}
.metric-label {
    font-size: 0.78rem;
    font-weight: 500;
    color: var(--gray-1);
    margin-top: 0.3rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* ═══════════════════════════════════════════
   SCORE ROWS
   ═══════════════════════════════════════════ */
.score-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 0;
    border-bottom: 1px solid var(--gray-5);
    transition: all 0.2s ease;
}
.score-item:last-child { border-bottom: none; }
.score-item:hover {
    padding-left: 8px;
}

/* ═══════════════════════════════════════════
   BUTTONS — Apple blue pill
   ═══════════════════════════════════════════ */
.stButton > button {
    border-radius: 980px !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    padding: 0.6rem 1.6rem !important;
    transition: all 0.2s cubic-bezier(0.25, 0.1, 0.25, 1) !important;
    letter-spacing: 0.01em !important;
}
.stButton > button[kind="primary"] {
    background: var(--blue) !important;
    color: #fff !important;
    border: none !important;
}
.stButton > button[kind="primary"]:hover {
    background: var(--blue-hover) !important;
    box-shadow: 0 2px 12px rgba(0,119,237,0.35) !important;
    transform: scale(1.02) !important;
}
.stButton > button:not([kind="primary"]) {
    background: transparent !important;
    color: var(--blue) !important;
    border: 1px solid var(--gray-4) !important;
}
.stButton > button:not([kind="primary"]):hover {
    background: var(--blue-bg) !important;
    border-color: var(--blue) !important;
}

/* ═══════════════════════════════════════════
   INPUTS — Apple form fields
   ═══════════════════════════════════════════ */
.stTextArea textarea {
    border-radius: 12px !important;
    border: 1px solid var(--gray-4) !important;
    font-family: 'SF Mono', 'Menlo', 'Consolas', monospace !important;
    font-size: 0.88rem !important;
    background: var(--gray-5) !important;
    color: var(--black) !important;
    transition: all 0.2s ease !important;
    padding: 1rem !important;
}
.stTextArea textarea:focus {
    border-color: var(--blue) !important;
    background: var(--white) !important;
    box-shadow: 0 0 0 4px rgba(0,119,237,0.12) !important;
    outline: none !important;
}

/* ── Select ── */
.stSelectbox label {
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    color: var(--gray-1) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
.stSelectbox div[data-baseweb="select"] {
    border-radius: 10px !important;
    border-color: var(--gray-4) !important;
}

/* ═══════════════════════════════════════════
   ALERTS — Apple system colors
   ═══════════════════════════════════════════ */
.stSuccess, .stError, .stWarning, .stInfo {
    border-radius: 12px !important;
    border: none !important;
}
.stSuccess { background: var(--green-bg) !important; }
.stError { background: var(--red-bg) !important; }
.stWarning { background: var(--orange-bg) !important; }

/* ═══════════════════════════════════════════
   DIVIDER — Apple thin rule
   ═══════════════════════════════════════════ */
.apple-hr {
    height: 1px;
    background: var(--gray-4);
    border: none;
    margin: 2rem 0;
}

/* ═══════════════════════════════════════════
   EXPANDER
   ═══════════════════════════════════════════ */
.streamlit-expanderHeader {
    font-weight: 500 !important;
    border-radius: 12px !important;
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
            <div class="hero-eyebrow">Interactive Python Tutorial</div>
            <h1 class="hero-title">
                Welcome to<br>
                <span class="hero-title-gradient">Python.</span>
            </h1>
            <p class="hero-subtitle">交互式学习，从这里开始</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        if st.button("开始学习", use_container_width=True, type="primary"):
            st.session_state["current_page"] = "学习"
            st.rerun()


def _build_steps(course):
    """Build interleaved lesson+exercise steps from a course."""
    lessons = course.get("lessons", [])
    exercises = course.get("exercises", [])
    steps = []
    for i, lesson in enumerate(lessons):
        steps.append({"type": "lesson", "data": lesson})
        if i < len(exercises):
            steps.append({"type": "exercise", "data": exercises[i]})
    return steps


def _find_resume_step(courses, progress):
    """Find the first step with an incomplete lesson. Returns (course_index, step_index)."""
    completed = set(progress.get("completed_lessons", []))
    for ci, c in enumerate(courses):
        course = load_course(c["id"])
        if not course:
            continue
        steps = _build_steps(course)
        for si, step in enumerate(steps):
            if step["type"] == "lesson" and step["data"]["id"] not in completed:
                return ci, si
    # All completed — go to last step of last course
    last_ci = len(courses) - 1
    last_course = load_course(courses[last_ci]["id"])
    last_si = len(_build_steps(last_course)) - 1 if last_course else 0
    return last_ci, last_si


def _render_exercise(exercise):
    """Render the exercise block (card + editor + buttons + results)."""
    exercise_id = exercise["id"]

    st.markdown('<hr class="apple-hr">', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.7rem;font-weight:600;color:var(--gray-1);letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.6rem;">练习</div>',
        unsafe_allow_html=True,
    )

    grading_result = st.session_state.get("grading_result_{}".format(exercise_id))
    exercise_card(exercise, grading_result)

    st.markdown(
        '<div class="code-section-label">代码编辑器</div>',
        unsafe_allow_html=True,
    )
    starter = exercise.get("starter_code", "# 在这里写你的代码\n")
    user_code = code_editor(
        initial_code=starter,
        key="exercise_editor_{}".format(exercise_id),
        height=250,
    )

    c1, c2, _ = st.columns([1, 1, 2])
    with c1:
        if st.button("▶  运行", key="run_{}".format(exercise_id)):
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

    # AI diagnosis on failed submission
    diag_key = "needs_diagnosis_{}".format(exercise_id)
    if diag_key in st.session_state and "llm_client" in st.session_state:
        diag = st.session_state[diag_key]
        st.markdown('<hr class="apple-hr">', unsafe_allow_html=True)
        st.markdown(
            '<div class="code-section-label">AI 诊断</div>',
            unsafe_allow_html=True,
        )
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


def lesson_page():
    _inject_css()

    courses = list_courses()
    if not courses:
        st.warning("暂无课程内容")
        return

    # Initialize session state
    if "lesson_ci" not in st.session_state:
        progress = load_progress()
        ci, si = _find_resume_step(courses, progress)
        st.session_state["lesson_ci"] = ci
        st.session_state["lesson_si"] = si

    ci = st.session_state["lesson_ci"]
    si = st.session_state["lesson_si"]

    # Clamp course index
    ci = max(0, min(ci, len(courses) - 1))
    course_id = courses[ci]["id"]
    course = load_course(course_id)
    if not course:
        st.error("无法加载课程")
        return

    steps = _build_steps(course)
    if not steps:
        st.warning("该课程暂无内容")
        return

    # Clamp step index
    si = max(0, min(si, len(steps) - 1))
    step = steps[si]
    total = len(steps)

    # ── Progress bar ──
    progress_pct = int((si + 1) / total * 100)
    st.markdown(
        '<div style="display:flex;align-items:center;gap:1rem;margin-bottom:0.3rem;">'
        '<div style="flex:1;height:4px;background:var(--gray-5);border-radius:2px;overflow:hidden;">'
        '<div style="width:{}%;height:100%;background:var(--blue);border-radius:2px;transition:width 0.4s ease;"></div>'
        '</div>'
        '<span style="font-size:0.78rem;color:var(--gray-2);font-weight:500;white-space:nowrap;">{} / {}</span>'
        '</div>'.format(progress_pct, si + 1, total),
        unsafe_allow_html=True,
    )

    # ── Course title ──
    st.markdown(
        '<p style="font-size:0.8rem;color:var(--gray-2);font-weight:500;margin:0.5rem 0 0 0;text-transform:uppercase;letter-spacing:0.06em;">{}</p>'.format(
            course["title"]
        ),
        unsafe_allow_html=True,
    )

    # ── Render current step ──
    if step["type"] == "lesson":
        lesson = step["data"]
        example_code = lesson_card(lesson)

        if example_code:
            run_col, _ = st.columns([1, 3])
            with run_col:
                if st.button("▶  运行示例", key="run_example"):
                    with st.spinner("运行中..."):
                        result = execute_code(example_code)
                        st.session_state["last_run_result"] = result

        if "last_run_result" in st.session_state:
            output_panel(st.session_state["last_run_result"])

        # Mark as learned
        progress_data = load_progress()
        is_learned = lesson["id"] in progress_data.get("completed_lessons", [])

        if not is_learned:
            if st.button("标记为已学", key="mark_learned", type="primary"):
                mark_lesson_complete(lesson["id"])
                st.rerun()
        else:
            st.markdown(
                '<div style="display:flex;align-items:center;gap:0.5rem;margin:0.5rem 0;color:var(--green);font-size:0.88rem;font-weight:500;">'
                '<span>&#10003;</span> 已完成</div>',
                unsafe_allow_html=True,
            )

    elif step["type"] == "exercise":
        _render_exercise(step["data"])

    # ── Bottom navigation ──
    st.markdown('<hr class="apple-hr">', unsafe_allow_html=True)

    has_prev = si > 0 or ci > 0
    is_last_step = (ci == len(courses) - 1) and (si == len(steps) - 1)
    is_last_in_course = si == len(steps) - 1

    nav_l, nav_r = st.columns(2)
    with nav_l:
        if has_prev:
            if st.button("←  上一步", key="prev_step", use_container_width=True):
                st.session_state["last_run_result"] = None
                if si > 0:
                    st.session_state["lesson_si"] = si - 1
                else:
                    st.session_state["lesson_ci"] = ci - 1
                    prev_course = load_course(courses[ci - 1]["id"])
                    if prev_course:
                        st.session_state["lesson_si"] = len(_build_steps(prev_course)) - 1
                st.rerun()
    with nav_r:
        if not is_last_step:
            if is_last_in_course:
                btn_label = "进入下一课程  →"
            else:
                btn_label = "下一步  →"
            if st.button(btn_label, key="next_step", type="primary", use_container_width=True):
                st.session_state["last_run_result"] = None
                if not is_last_in_course:
                    st.session_state["lesson_si"] = si + 1
                else:
                    st.session_state["lesson_ci"] = ci + 1
                    st.session_state["lesson_si"] = 0
                st.rerun()
        else:
            st.markdown(
                '<div style="text-align:center;padding:0.6rem;color:var(--gray-2);font-size:0.88rem;">'
                '所有课程已完成</div>',
                unsafe_allow_html=True,
            )


def ask_page():
    _inject_css()

    st.markdown(
        '<h1 class="page-title">提问</h1>'
        '<p class="page-desc">粘贴代码，AI 用中文为你解答。</p>',
        unsafe_allow_html=True,
    )

    if "llm_client" not in st.session_state:
        st.warning("请先配置 ANTHROPIC_API_KEY 环境变量")
        return

    st.markdown('<div class="apple-card">', unsafe_allow_html=True)
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
                st.markdown(
                    '<div class="code-section-label" style="margin-top:2rem;">回答</div>',
                    unsafe_allow_html=True,
                )
                st.markdown('<div class="apple-card">', unsafe_allow_html=True)
                st.write_stream(
                    llm.answer_question_stream(user_code, user_question)
                )
                st.markdown('</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error("调用 LLM 失败: {}".format(e))


def dashboard_page():
    _inject_css()

    st.markdown(
        '<h1 class="page-title">学习进度</h1>'
        '<p class="page-desc">回顾你的学习旅程。</p>',
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
                '<div class="metric-block">'
                '<div class="metric-big">{}</div>'
                '<div class="metric-label">{}</div>'
                '</div>'.format(value, label),
                unsafe_allow_html=True,
            )

    if progress.get("completed_lessons"):
        st.markdown(
            '<hr class="apple-hr">'
            '<div class="section-title">已完成的课程</div>',
            unsafe_allow_html=True,
        )
        for lid in progress["completed_lessons"]:
            st.markdown(
                '<div class="apple-card" style="padding:0.8rem 1.5rem;display:flex;align-items:center;gap:0.6rem;">'
                '<span style="color:var(--green);font-size:1.1rem;">&#10003;</span> {}</div>'.format(lid),
                unsafe_allow_html=True,
            )

    scores = progress.get("exercise_scores", {})
    if scores:
        st.markdown(
            '<hr class="apple-hr">'
            '<div class="section-title">练习成绩</div>',
            unsafe_allow_html=True,
        )
        for ex_id, info in scores.items():
            passed = info["passed"] == info["total"]
            badge_cls = "green" if passed else "red"
            status = "通过" if passed else "未通过"
            st.markdown(
                '<div class="score-item">'
                '<span style="font-weight:600;">{}</span>'
                '<span>{} / {} <span class="apple-badge {}">{}</span></span>'
                '</div>'.format(ex_id, info["passed"], info["total"], badge_cls, status),
                unsafe_allow_html=True,
            )

    mistakes = load_mistakes()
    if mistakes:
        st.markdown(
            '<hr class="apple-hr">'
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

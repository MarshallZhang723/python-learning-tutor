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
from courses.loader import list_courses, load_course
from ui.components import code_editor, output_panel

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;0,9..40,800;1,9..40,400&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg: #fafaf9;
    --surface: #ffffff;
    --ink: #1a1a1a;
    --ink-2: #555555;
    --ink-3: #999999);
    --border: #eaeaea;
    --border-light: #f0f0f0;
    --accent: #2563eb;
    --accent-soft: rgba(37,99,235,0.08);
    --accent-hover: #1d4ed8;
    --green: #16a34a;
    --green-soft: rgba(22,163,74,0.08);
    --red: #dc2626;
    --red-soft: rgba(220,38,38,0.08);
    --orange: #ea580c;
    --orange-soft: rgba(234,88,12,0.08);
    --code-bg: #1e1e2e;
    --code-surface: #2a2a3c;
    --code-text: #cdd6f4;
    --code-border: #3a3a4c;
    --topbar-h: 52px;
    --font-body: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    --font-mono: 'JetBrains Mono', 'SF Mono', 'Menlo', monospace;
}

/* ═══════════════════════════════════════════
   RESET & BASE
   ═══════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: var(--font-body) !important;
    background: var(--bg) !important;
    color: var(--ink) !important;
    -webkit-font-smoothing: antialiased !important;
    -moz-osx-font-smoothing: grayscale !important;
    line-height: 1.6 !important;
}

/* ── Kill ALL Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden !important; }
[data-testid="stSidebar"] { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
.main .block-container {
    max-width: 100% !important;
    padding: 0 !important;
}

/* ═══════════════════════════════════════════
   TOP NAV BAR — fixed, minimal
   ═══════════════════════════════════════════ */
.topnav {
    position: fixed;
    top: 0; left: 0; right: 0;
    height: var(--topbar-h);
    background: rgba(255,255,255,0.85);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 2rem;
    z-index: 1000;
    transition: box-shadow 0.3s ease;
}
.topnav.scrolled {
    box-shadow: 0 1px 12px rgba(0,0,0,0.06);
}
.topnav-logo {
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--ink);
    letter-spacing: -0.02em;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.topnav-logo .logo-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--accent);
}
.topnav-links {
    display: flex;
    gap: 0.25rem;
}
.topnav-link {
    font-size: 0.8rem;
    font-weight: 500;
    color: var(--ink-3);
    padding: 0.4rem 0.9rem;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.15s ease;
    text-decoration: none;
    border: none;
    background: none;
}
.topnav-link:hover {
    color: var(--ink);
    background: var(--border-light);
}
.topnav-link.active {
    color: var(--accent);
    background: var(--accent-soft);
    font-weight: 600;
}

/* ═══════════════════════════════════════════
   LAYOUT — content below topnav
   ═══════════════════════════════════════════ */
.page-content {
    padding-top: calc(var(--topbar-h) + 1.5rem);
    max-width: 760px;
    margin: 0 auto;
    padding-left: 2rem;
    padding-right: 2rem;
    padding-bottom: 6rem;
}
.page-content-wide {
    padding-top: calc(var(--topbar-h) + 1.5rem);
    max-width: 960px;
    margin: 0 auto;
    padding-left: 2rem;
    padding-right: 2rem;
    padding-bottom: 6rem;
}

/* ═══════════════════════════════════════════
   HERO — warm landing
   ═══════════════════════════════════════════ */
.hero {
    padding: 8rem 2rem 4rem 2rem;
    text-align: center;
    max-width: 680px;
    margin: 0 auto;
}
.hero-eyebrow {
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--accent);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 1rem;
    opacity: 0;
    animation: fadeUp 0.8s ease 0.1s forwards;
}
.hero-title {
    font-size: clamp(2.6rem, 6vw, 4.2rem);
    font-weight: 800;
    color: var(--ink);
    line-height: 1.08;
    margin: 0 0 0.5rem 0;
    letter-spacing: -0.03em;
    opacity: 0;
    animation: fadeUp 0.8s ease 0.2s forwards;
}
.hero-title-accent {
    background: linear-gradient(135deg, var(--accent) 0%, #7c3aed 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-subtitle {
    font-size: 1.1rem;
    font-weight: 400;
    color: var(--ink-2);
    margin: 1rem 0 2.5rem 0;
    line-height: 1.6;
    opacity: 0;
    animation: fadeUp 0.8s ease 0.35s forwards;
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* ═══════════════════════════════════════════
   STEP PROGRESS — thin bar + label
   ═══════════════════════════════════════════ */
.step-progress {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 2rem;
}
.step-progress-bar {
    flex: 1;
    height: 3px;
    background: var(--border);
    border-radius: 2px;
    overflow: hidden;
}
.step-progress-fill {
    height: 100%;
    background: var(--accent);
    border-radius: 2px;
    transition: width 0.5s cubic-bezier(0.25, 0.1, 0.25, 1);
}
.step-progress-label {
    font-size: 0.72rem;
    color: var(--ink-3);
    font-weight: 500;
    white-space: nowrap;
    font-variant-numeric: tabular-nums;
}
.step-course-tag {
    font-size: 0.7rem;
    font-weight: 600;
    color: var(--accent);
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
}

/* ═══════════════════════════════════════════
   CONTENT CARDS — clean, minimal
   ═══════════════════════════════════════════ */
.content-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 2rem;
    margin-bottom: 1rem;
}
.content-card h2 {
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--ink);
    margin: 0 0 1rem 0;
    letter-spacing: -0.015em;
    line-height: 1.3;
}
.content-card p {
    font-size: 0.92rem;
    color: var(--ink-2);
    line-height: 1.75;
    margin: 0;
}

/* key points */
.key-points {
    list-style: none;
    padding: 0;
    margin: 1rem 0 0 0;
}
.key-points li {
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
    padding: 0.55rem 0;
    font-size: 0.88rem;
    color: var(--ink);
    border-bottom: 1px solid var(--border-light);
}
.key-points li:last-child { border-bottom: none; }
.key-points li .kp-dot {
    width: 5px; height: 5px;
    min-width: 5px;
    border-radius: 50%;
    background: var(--accent);
    margin-top: 0.5rem;
}

/* ═══════════════════════════════════════════
   CODE BLOCKS — immersive dark
   ═══════════════════════════════════════════ */
.code-section {
    background: var(--code-bg);
    border-radius: 14px;
    overflow: hidden;
    margin: 1.2rem 0;
    border: 1px solid var(--code-border);
}
.code-section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.6rem 1rem;
    background: var(--code-surface);
    border-bottom: 1px solid var(--code-border);
}
.code-section-header span {
    font-size: 0.68rem;
    font-weight: 600;
    color: #888;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.code-dots {
    display: flex;
    gap: 5px;
}
.code-dots span {
    width: 10px; height: 10px;
    border-radius: 50%;
    background: #444;
}
.code-dots span:first-child { background: #ff5f57; }
.code-dots span:nth-child(2) { background: #febc2e; }
.code-dots span:nth-child(3) { background: #28c840; }
.code-section .stCodeBlock {
    border-radius: 0 !important;
    border: none !important;
    margin: 0 !important;
}
.code-section .stCodeBlock > div {
    background: var(--code-bg) !important;
}

/* exercise code editor */
.editor-section {
    background: var(--code-bg);
    border-radius: 14px;
    overflow: hidden;
    margin: 1rem 0;
    border: 1px solid var(--code-border);
}
.editor-section .stTextArea textarea {
    background: var(--code-bg) !important;
    color: var(--code-text) !important;
    border: none !important;
    border-radius: 0 !important;
    font-family: var(--font-mono) !important;
    font-size: 0.85rem !important;
    line-height: 1.6 !important;
    padding: 1rem 1.2rem !important;
    resize: none !important;
}
.editor-section .stTextArea textarea:focus {
    box-shadow: none !important;
    outline: none !important;
}
.editor-section .stTextArea textarea::placeholder {
    color: #666 !important;
}

/* ═══════════════════════════════════════════
   EXERCISE CARD
   ═══════════════════════════════════════════ */
.exercise-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.5rem 2rem;
    margin-bottom: 1rem;
}
.exercise-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.8rem;
}
.exercise-header h3 {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--ink);
    margin: 0;
    letter-spacing: -0.01em;
}
.exercise-desc {
    font-size: 0.88rem;
    color: var(--ink-2);
    line-height: 1.7;
    margin: 0;
}

/* ═══════════════════════════════════════════
   BADGES — subtle
   ═══════════════════════════════════════════ */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 0.15rem 0.6rem;
    border-radius: 6px;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}
.badge.green { background: var(--green-soft); color: var(--green); }
.badge.orange { background: var(--orange-soft); color: var(--orange); }
.badge.red { background: var(--red-soft); color: var(--red); }
.badge.blue { background: var(--accent-soft); color: var(--accent); }

/* ═══════════════════════════════════════════
   SECTION LABELS
   ═══════════════════════════════════════════ */
.section-label {
    font-size: 0.68rem;
    font-weight: 600;
    color: var(--ink-3);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin: 1.8rem 0 0.6rem 0;
}
.section-label-dark {
    font-size: 0.68rem;
    font-weight: 600;
    color: #888;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin: 0;
}

/* ═══════════════════════════════════════════
   BUTTONS — clean pills
   ═══════════════════════════════════════════ */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    padding: 0.55rem 1.4rem !important;
    transition: all 0.2s cubic-bezier(0.25, 0.1, 0.25, 1) !important;
    letter-spacing: 0 !important;
    font-family: var(--font-body) !important;
}
.stButton > button[kind="primary"] {
    background: var(--accent) !important;
    color: #fff !important;
    border: none !important;
}
.stButton > button[kind="primary"]:hover {
    background: var(--accent-hover) !important;
    box-shadow: 0 2px 12px rgba(37,99,235,0.3) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:not([kind="primary"]) {
    background: transparent !important;
    color: var(--ink-2) !important;
    border: 1px solid var(--border) !important;
}
.stButton > button:not([kind="primary"]):hover {
    border-color: var(--ink-3) !important;
    color: var(--ink) !important;
}

/* ═══════════════════════════════════════════
   INPUTS
   ═══════════════════════════════════════════ */
.stTextArea textarea {
    border-radius: 10px !important;
    border: 1px solid var(--border) !important;
    font-family: var(--font-body) !important;
    font-size: 0.88rem !important;
    background: var(--surface) !important;
    color: var(--ink) !important;
    transition: all 0.2s ease !important;
    padding: 0.8rem 1rem !important;
}
.stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-soft) !important;
    outline: none !important;
}

/* ═══════════════════════════════════════════
   ALERTS
   ═══════════════════════════════════════════ */
.stSuccess, .stError, .stWarning, .stInfo {
    border-radius: 10px !important;
    border: none !important;
    font-size: 0.88rem !important;
}
.stSuccess { background: var(--green-soft) !important; }
.stError { background: var(--red-soft) !important; }
.stWarning { background: var(--orange-soft) !important; }

/* ═══════════════════════════════════════════
   DIVIDER — hairline
   ═══════════════════════════════════════════ */
.hairline {
    height: 1px;
    background: var(--border);
    border: none;
    margin: 1.5rem 0;
}

/* ═══════════════════════════════════════════
   BOTTOM NAV — sticky step navigation
   ═══════════════════════════════════════════ */
.step-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 2rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--border);
}

/* ═══════════════════════════════════════════
   METRICS
   ═══════════════════════════════════════════ */
.metric-block {
    text-align: center;
    padding: 1.5rem 1rem;
}
.metric-big {
    font-size: 2.8rem;
    font-weight: 800;
    color: var(--ink);
    line-height: 1;
    letter-spacing: -0.03em;
}
.metric-label {
    font-size: 0.72rem;
    font-weight: 500;
    color: var(--ink-3);
    margin-top: 0.3rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* ═══════════════════════════════════════════
   SCORE ROWS
   ═══════════════════════════════════════════ */
.score-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.8rem 0;
    border-bottom: 1px solid var(--border-light);
    transition: all 0.2s ease;
}
.score-item:last-child { border-bottom: none; }

/* ═══════════════════════════════════════════
   SCROLL REVEAL
   ═══════════════════════════════════════════ */
.reveal {
    opacity: 0;
    transform: translateY(16px);
    transition: opacity 0.6s ease, transform 0.6s ease;
}
.reveal.visible {
    opacity: 1;
    transform: translateY(0);
}

/* ═══════════════════════════════════════════
   EXPANDER
   ═══════════════════════════════════════════ */
.streamlit-expanderHeader {
    font-weight: 500 !important;
    border-radius: 10px !important;
}

/* ═══════════════════════════════════════════
   PAGE TITLES (ask / dashboard)
   ═══════════════════════════════════════════ */
.page-title {
    font-size: 2.2rem;
    font-weight: 800;
    color: var(--ink);
    letter-spacing: -0.02em;
    margin: 0 0 0.3rem 0;
    line-height: 1.15;
}
.page-desc {
    font-size: 0.95rem;
    color: var(--ink-2);
    margin: 0 0 2rem 0;
    font-weight: 400;
    line-height: 1.6;
}
.section-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--ink);
    margin: 2rem 0 0.8rem 0;
    letter-spacing: -0.01em;
}
</style>

<script>
// Scroll reveal observer
document.addEventListener('DOMContentLoaded', function() {
    var obs = new IntersectionObserver(function(entries) {
        entries.forEach(function(e) {
            if (e.isIntersecting) { e.target.classList.add('visible'); }
        });
    }, { threshold: 0.08 });
    document.querySelectorAll('.reveal').forEach(function(el) { obs.observe(el); });
});
// Topnav scroll shadow
window.addEventListener('scroll', function() {
    var nav = document.querySelector('.topnav');
    if (nav) { nav.classList.toggle('scrolled', window.scrollY > 8); }
});
</script>
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
                Learn to code.<br>
                <span class="hero-title-accent">One step at a time.</span>
            </h1>
            <p class="hero-subtitle">
                交互式 Python 学习 — 每学一个知识点，立刻动手练习。<br>
                没有侧边栏，没有干扰，专注于当下这一步。
            </p>
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


def _render_lesson_card(lesson):
    """Render lesson content with new design. Returns example_code if any."""
    st.markdown(
        '<div class="content-card">'
        '<h2>{}</h2>'.format(lesson["title"]),
        unsafe_allow_html=True,
    )

    st.markdown(lesson["explanation"])

    if lesson.get("key_points"):
        items = "".join(
            '<li><span class="kp-dot"></span>{}</li>'.format(p)
            for p in lesson["key_points"]
        )
        st.markdown(
            '<ul class="key-points">{}</ul>'.format(items),
            unsafe_allow_html=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)

    return lesson.get("code_example", "")


def _render_exercise(exercise):
    """Render the exercise block (card + editor + buttons + results)."""
    exercise_id = exercise["id"]

    # Section label
    st.markdown(
        '<div class="section-label" style="margin-top:2rem;">练习</div>',
        unsafe_allow_html=True,
    )

    # Exercise card
    difficulty = exercise.get("difficulty", "medium")
    diff_map = {"easy": ("简单", "green"), "medium": ("中等", "orange"), "hard": ("困难", "red")}
    label, badge_cls = diff_map.get(difficulty, ("中等", "orange"))

    grading_result = st.session_state.get("grading_result_{}".format(exercise_id))

    st.markdown(
        '<div class="exercise-card">'
        '<div class="exercise-header">'
        '<h3>{}</h3>'
        '<span class="badge {}">{}</span>'
        '</div>'
        '<p class="exercise-desc">{}</p>'
        '</div>'.format(exercise["title"], badge_cls, label, exercise["description"]),
        unsafe_allow_html=True,
    )

    if grading_result:
        if grading_result.all_passed:
            st.success(
                "所有测试通过！({}/{})".format(grading_result.passed, grading_result.total)
            )
        else:
            st.warning(
                "通过 {}/{} 个测试".format(grading_result.passed, grading_result.total)
            )
            for detail in grading_result.details:
                icon = "✓" if detail.passed else "✗"
                st.markdown(
                    "- **{}** `{}`：期望 `{}`，实际 `{}`".format(
                        icon, detail.input_desc, detail.expected, detail.actual
                    )
                )

    # Code editor in dark container
    starter = exercise.get("starter_code", "# 在这里写你的代码\n")
    st.markdown(
        '<div class="editor-section">'
        '<div class="code-section-header">'
        '<span>代码编辑器</span>'
        '<div class="code-dots"><span></span><span></span><span></span></div>'
        '</div>',
        unsafe_allow_html=True,
    )
    user_code = code_editor(
        initial_code=starter,
        key="exercise_editor_{}".format(exercise_id),
        height=250,
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Action buttons
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

    # Run output
    run_key = "run_result_{}".format(exercise_id)
    if run_key in st.session_state:
        output_panel(st.session_state[run_key])

    # AI diagnosis on failed submission
    diag_key = "needs_diagnosis_{}".format(exercise_id)
    if diag_key in st.session_state and "llm_client" in st.session_state:
        diag = st.session_state[diag_key]
        st.markdown(
            '<div class="section-label">AI 诊断</div>',
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

    # ── Page content wrapper ──
    st.markdown('<div class="page-content">', unsafe_allow_html=True)

    # ── Progress bar ──
    progress_pct = int((si + 1) / total * 100)
    st.markdown(
        '<div class="step-progress">'
        '<div class="step-progress-bar"><div class="step-progress-fill" style="width:{}%;"></div></div>'
        '<span class="step-progress-label">{}/{}</span>'
        '</div>'.format(progress_pct, si + 1, total),
        unsafe_allow_html=True,
    )

    # ── Course tag ──
    st.markdown(
        '<div class="step-course-tag">{}</div>'.format(course["title"]),
        unsafe_allow_html=True,
    )

    # ── Render current step ──
    if step["type"] == "lesson":
        lesson = step["data"]

        # Lesson card
        st.markdown('<div class="reveal">', unsafe_allow_html=True)
        example_code = _render_lesson_card(lesson)
        st.markdown('</div>', unsafe_allow_html=True)

        # Code example in dark container
        if example_code:
            st.markdown(
                '<div class="code-section reveal">'
                '<div class="code-section-header">'
                '<span>示例代码</span>'
                '<div class="code-dots"><span></span><span></span><span></span></div>'
                '</div>',
                unsafe_allow_html=True,
            )
            st.code(example_code, language="python")
            st.markdown('</div>', unsafe_allow_html=True)

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
                '<div style="display:flex;align-items:center;gap:0.5rem;margin:1rem 0;color:var(--green);font-size:0.85rem;font-weight:500;">'
                '<span>&#10003;</span> 已完成</div>',
                unsafe_allow_html=True,
            )

    elif step["type"] == "exercise":
        st.markdown('<div class="reveal">', unsafe_allow_html=True)
        _render_exercise(step["data"])
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Bottom navigation ──
    has_prev = si > 0 or ci > 0
    is_last_step = (ci == len(courses) - 1) and (si == len(steps) - 1)
    is_last_in_course = si == len(steps) - 1

    st.markdown(
        '<div class="step-nav">',
        unsafe_allow_html=True,
    )
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
                '<span style="color:var(--ink-3);font-size:0.85rem;">所有课程已完成</span>',
                unsafe_allow_html=True,
            )
    st.markdown('</div>', unsafe_allow_html=True)  # close .step-nav

    st.markdown('</div>', unsafe_allow_html=True)  # close .page-content


def ask_page():
    _inject_css()

    st.markdown('<div class="page-content">', unsafe_allow_html=True)

    st.markdown(
        '<h1 class="page-title">提问</h1>'
        '<p class="page-desc">粘贴代码，AI 用中文为你解答。</p>',
        unsafe_allow_html=True,
    )

    if "llm_client" not in st.session_state:
        st.warning("请先配置 ANTHROPIC_API_KEY 环境变量")
        st.markdown('</div>', unsafe_allow_html=True)
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
                st.markdown(
                    '<div class="section-label" style="margin-top:2rem;">回答</div>',
                    unsafe_allow_html=True,
                )
                st.markdown('<div class="content-card">', unsafe_allow_html=True)
                st.write_stream(
                    llm.answer_question_stream(user_code, user_question)
                )
                st.markdown('</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error("调用 LLM 失败: {}".format(e))

    st.markdown('</div>', unsafe_allow_html=True)


def dashboard_page():
    _inject_css()

    st.markdown('<div class="page-content">', unsafe_allow_html=True)

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

    st.markdown('</div>', unsafe_allow_html=True)  # close .page-content

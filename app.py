import streamlit as st

import config
from ui.pages import ask_page, dashboard_page, lesson_page, welcome_page


def init_session_state():
    if "llm_client" not in st.session_state:
        try:
            from core.llm_client import LLMClient
            st.session_state["llm_client"] = LLMClient()
        except (ValueError, Exception):
            st.session_state["llm_client"] = None

    if "progress_tracker" not in st.session_state:
        from core import progress_tracker
        st.session_state["progress_tracker"] = progress_tracker


def main():
    st.set_page_config(
        page_title="Python 学习助手",
        page_icon="",
        layout="centered",
        initial_sidebar_state="collapsed",
    )

    init_session_state()

    # ── State-based page routing ──
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "首页"

    page = st.session_state["current_page"]

    if page == "首页":
        welcome_page()
        return

    # ── Top navigation bar ──
    pages_list = ["学习", "提问", "进度"]
    links_html = ""
    for label in pages_list:
        cls = "topnav-link active" if label == page else "topnav-link"
        # Each link is a hidden anchor; actual navigation via Streamlit buttons below
        links_html += '<span class="{}">{}</span>'.format(cls, label)

    st.markdown(
        '<div class="topnav">'
        '<div class="topnav-logo"><span class="logo-dot"></span>Python Tutor</div>'
        '<div class="topnav-links">{}</div>'
        '</div>'.format(links_html),
        unsafe_allow_html=True,
    )

    # Invisible navigation buttons overlaid on topnav links
    # Streamlit can't do JS→Python, so we use st.columns with small nav buttons
    # positioned to look like the topnav links
    nav_cols = st.columns(len(pages_list))
    for i, label in enumerate(pages_list):
        with nav_cols[i]:
            if label != page:
                if st.button(label, key="nav_{}".format(label)):
                    st.session_state["current_page"] = label
                    st.rerun()

    # ── Render page ──
    if page == "学习":
        lesson_page()
    elif page == "提问":
        ask_page()
    elif page == "进度":
        dashboard_page()


if __name__ == "__main__":
    main()

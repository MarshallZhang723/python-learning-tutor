import streamlit as st

import config
from ui.components import sidebar_progress
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
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    init_session_state()

    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "首页"

    page = st.session_state["current_page"]

    if page == "首页":
        # Hide sidebar entirely via CSS on landing page
        st.markdown(
            "<style>[data-testid='stSidebar'] {display: none;}</style>",
            unsafe_allow_html=True,
        )
        welcome_page()
        return

    # Other pages: show sidebar
    st.sidebar.title("Python 学习助手")
    pages_list = ["学习", "提问", "进度"]
    current_index = pages_list.index(page) if page in pages_list else 0
    nav_page = st.sidebar.radio("导航", pages_list, index=current_index)

    if nav_page != page:
        st.session_state["current_page"] = nav_page
        st.rerun()

    from core.progress_tracker import load_progress
    sidebar_progress(load_progress())

    if page == "学习":
        lesson_page()
    elif page == "提问":
        ask_page()
    elif page == "进度":
        dashboard_page()


if __name__ == "__main__":
    main()

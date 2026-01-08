import streamlit as st


def render_topbar():
    left, right = st.columns([6, 1])

    with left:
        st.title("TimeBoard — Today")

    with right:
        if st.button("➕", help="Add Event"):
            st.session_state["show_event_form"] = True

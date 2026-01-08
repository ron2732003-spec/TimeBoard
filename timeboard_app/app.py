import streamlit as st

from state.session import init_session_state
from timeboard_app.ui.active_time import render_active_time_slider
from timeboard_app.ui.timeline import render_timeline
from timeboard_app.ui.settings_panel import render_settings_panel
from timeboard_app.ui.event_form import render_event_form, render_event_list, render_add_event_button
from timeboard_core.settings import UserSettings

if "settings" not in st.session_state:
    st.session_state["settings"] = UserSettings()

if "events" not in st.session_state:
    st.session_state["events"] = []

if "show_event_form" not in st.session_state:
    st.session_state["show_event_form"] = False


# --------------------------------------------------
# App Boot
# --------------------------------------------------
st.set_page_config(
    page_title="TimeBoard",
    page_icon="📅",
    layout="wide"
)

st.markdown("# 📅 TimeBoard")

# --------------------------------------------------
# Session Init
# --------------------------------------------------
now_local = init_session_state()

# --------------------------------------------------
# Top Row: Settings + Add Event
# --------------------------------------------------
col_settings, col_events = st.columns([3, 1])

with col_settings:
    render_settings_panel()

with col_events:
    render_add_event_button()

# --------------------------------------------------
# Event Form (if open)
# --------------------------------------------------
settings = st.session_state["settings"]
render_event_form(settings)

# --------------------------------------------------
# Event List
# --------------------------------------------------
render_event_list()

# --------------------------------------------------
# Active Time Slider
# --------------------------------------------------
render_active_time_slider(now_local)

# --------------------------------------------------
# Timeline
# --------------------------------------------------
zones = settings.active_timezones

if zones:
    render_timeline(
        zones,
        settings,
        st.session_state["now_local_minute"],
        st.session_state["active_minute"],
        st.session_state["today_utc"],
        st.session_state["local_tz"],
    )
else:
    st.warning("⚠️ No timezones selected. Please add at least one timezone in Settings.")
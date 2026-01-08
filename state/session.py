import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo


def init_session_state():
    # ------------------------------------------------------------------
    # 1. Zeitbasis
    # ------------------------------------------------------------------
    utc = ZoneInfo("UTC")
    now_utc = datetime.now(tz=utc)

    local_tz = datetime.now().astimezone().tzinfo
    now_local = now_utc.astimezone(local_tz)

    today_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    today_utc = today_local.astimezone(utc)

    # ------------------------------------------------------------------
    # 2. Session State – Zeit
    # ------------------------------------------------------------------
    st.session_state["now_utc"] = now_utc              # intern
    st.session_state["local_tz"] = local_tz
    st.session_state["today_local"] = today_local
    st.session_state["today_utc"] = today_utc

    st.session_state["now_local_minute"] = (
        now_local.hour * 60 + now_local.minute
    )

    # ------------------------------------------------------------------
    # 3. Active Minute (UI-Wahrheit)
    # ------------------------------------------------------------------
    if "active_minute" not in st.session_state:
        st.session_state["active_minute"] = st.session_state["now_local_minute"]
    else:
        st.session_state["active_minute"] = max(
            0, min(1439, st.session_state["active_minute"])
        )

    # UTC-Ableitung (intern!)
    active_min = st.session_state["active_minute"]
    st.session_state["active_time_utc"] = today_utc.replace(
        hour=active_min // 60,
        minute=active_min % 60
    )

    # ------------------------------------------------------------------
    # 4. Sonstiges
    # ------------------------------------------------------------------
    if "events" not in st.session_state:
        st.session_state["events"] = []

    if "show_event_form" not in st.session_state:
        st.session_state["show_event_form"] = False

    return now_local

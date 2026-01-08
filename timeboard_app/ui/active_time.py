import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
from timeboard_core.time_axis import hhmm_from_minute


# Available timezone options for the slider
SLIDER_TIMEZONE_OPTIONS = {
    "Local": None,  # Will use device local timezone
    "UTC": "UTC",
    "PST (Los Angeles)": "America/Los_Angeles",
    "EST (New York)": "America/New_York",
    "CET (Berlin)": "Europe/Berlin",
}


def render_active_time_slider(now_local):
    st.markdown("### Active Time")
    
    # Get minute step from settings
    settings = st.session_state.get("settings")
    minute_step = getattr(settings, 'minute_step', 5) if settings else 5
    
    # ---------------------------------------------------------------
    # Timezone Selector
    # ---------------------------------------------------------------
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if "slider_timezone" not in st.session_state:
            st.session_state["slider_timezone"] = "Local"
        
        selected_tz_label = st.selectbox(
            "Timezone",
            options=list(SLIDER_TIMEZONE_OPTIONS.keys()),
            index=list(SLIDER_TIMEZONE_OPTIONS.keys()).index(st.session_state["slider_timezone"]),
            key="slider_tz_select",
            label_visibility="collapsed"
        )
        st.session_state["slider_timezone"] = selected_tz_label
    
    # ---------------------------------------------------------------
    # Calculate times based on selected timezone
    # ---------------------------------------------------------------
    now_utc = st.session_state["now_utc"]
    local_tz = st.session_state["local_tz"]
    
    # Get the selected timezone
    selected_tz_str = SLIDER_TIMEZONE_OPTIONS[selected_tz_label]
    if selected_tz_str is None:
        # Local timezone
        display_tz = local_tz
        tz_label = "Local"
    else:
        display_tz = ZoneInfo(selected_tz_str)
        tz_label = selected_tz_label.split(" ")[0]  # "PST", "UTC", etc.
    
    # Current time in selected timezone
    now_in_tz = now_utc.astimezone(display_tz)
    now_minute_in_tz = now_in_tz.hour * 60 + now_in_tz.minute
    
    # ---------------------------------------------------------------
    # Active Minute (stored as minute-of-day in selected timezone)
    # ---------------------------------------------------------------
    if "active_minute" not in st.session_state:
        # Snap to nearest step
        st.session_state["active_minute"] = (now_minute_in_tz // minute_step) * minute_step
    
    # Track timezone changes - convert active time to new timezone
    if "last_slider_timezone" not in st.session_state:
        st.session_state["last_slider_timezone"] = selected_tz_label
    
    if st.session_state["last_slider_timezone"] != selected_tz_label:
        # Timezone changed - convert active time to new timezone
        old_tz_str = SLIDER_TIMEZONE_OPTIONS[st.session_state["last_slider_timezone"]]
        old_tz = local_tz if old_tz_str is None else ZoneInfo(old_tz_str)
        
        # Get active time in UTC first
        old_active_min = st.session_state["active_minute"]
        today_in_old_tz = now_utc.astimezone(old_tz).replace(
            hour=old_active_min // 60,
            minute=old_active_min % 60,
            second=0, microsecond=0
        )
        
        # Convert to new timezone
        active_in_new_tz = today_in_old_tz.astimezone(display_tz)
        new_minute = active_in_new_tz.hour * 60 + active_in_new_tz.minute
        # Snap to step
        st.session_state["active_minute"] = (new_minute // minute_step) * minute_step
        st.session_state["last_slider_timezone"] = selected_tz_label
    
    current = max(0, min(1439, st.session_state["active_minute"]))
    current_hour = current // 60

    # ---------------------------------------------------------------
    # CSS
    # ---------------------------------------------------------------
    st.markdown("""
        <style>
        .slider-hours-container {
            position: relative;
            height: 20px;
            margin-bottom: 6px;
            padding: 0 12px;
        }
        .hour-marker {
            position: absolute;
            font-size: 11px;
        }
        .hour-marker.active {
            color: #ff3b3b;
            font-weight: 700;
            background: rgba(255,59,59,0.15);
            padding: 2px 4px;
            border-radius: 3px;
        }
        .time-marker {
            position: absolute;
            top: -5px;
            width: 3px;
            height: 30px;
            z-index: 10;
        }
        .time-marker.now {
            border-left: 2px dashed #4da3ff;
            opacity: 0.75;
        }
        .time-marker.active {
            border-left: 3px solid #ff3b3b;
        }
        .time-label {
            position: absolute;
            top: -26px;
            transform: translateX(-50%);
            font-size: 11px;
            font-weight: 700;
            color: #ff3b3b;
            pointer-events: none;
            white-space: nowrap;
        }
        .tz-badge {
            display: inline-block;
            background: #2d3a4a;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            margin-left: 8px;
            color: #4da3ff;
        }
        .step-badge {
            display: inline-block;
            background: #3a3a2d;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 10px;
            margin-left: 4px;
            color: #aaa;
        }
        </style>
    """, unsafe_allow_html=True)

    # ---------------------------------------------------------------
    # Hour Markers
    # ---------------------------------------------------------------
    with col1:
        markers = []
        for h in range(24):
            pos = (h * 60 / 1439) * 100
            markers.append(
                f"<div class='hour-marker{' active' if h == current_hour else ''}' "
                f"style='left:{pos}%;'>{h}</div>"
            )

        active_label = hhmm_from_minute(current)

        st.markdown(
            "<div class='slider-hours-container'>"
            + "".join(markers)
            # NOW marker
            + f"<div class='time-marker now' style='left:{(now_minute_in_tz/1439)*100}%;'></div>"
            # ACTIVE marker
            + f"<div class='time-marker active' style='left:{(current/1439)*100}%;'></div>"
            # ACTIVE time label (HH:MM)
            + f"<div class='time-label' style='left:{(current/1439)*100}%;'>{active_label}</div>"
            + "</div>",
            unsafe_allow_html=True
        )

        # ---------------------------------------------------------------
        # Slider with configurable step
        # ---------------------------------------------------------------
        def _update():
            st.session_state["active_minute"] = st.session_state["active_time_slider"]

        new_minute = st.slider(
            label="Active Time",
            min_value=0,
            max_value=1439,
            value=current,
            step=minute_step,  # Use configured step
            label_visibility="collapsed",
            format="",
            key="active_time_slider",
            on_change=_update
        )

        # ---------------------------------------------------------------
        # Text Display with Timezone Badge
        # ---------------------------------------------------------------
        step_label = f"{minute_step}min" if minute_step > 1 else "1min"
        
        st.markdown(
            f"<div style='display:flex;justify-content:space-between;margin-top:-10px;'>"
            f"<span style='color:#4da3ff;font-weight:600;'>Now: {hhmm_from_minute(now_minute_in_tz)}<span class='tz-badge'>{tz_label}</span></span>"
            f"<span style='color:#ff3b3b;font-weight:700;'>Active: {hhmm_from_minute(new_minute)}<span class='tz-badge'>{tz_label}</span><span class='step-badge'>{step_label}</span></span>"
            f"</div>",
            unsafe_allow_html=True
        )
    
    # ---------------------------------------------------------------
    # Store active time in UTC for timeline sync
    # ---------------------------------------------------------------
    today_in_display_tz = now_utc.astimezone(display_tz).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    active_datetime_in_tz = today_in_display_tz.replace(
        hour=new_minute // 60,
        minute=new_minute % 60
    )
    st.session_state["active_time_utc"] = active_datetime_in_tz.astimezone(ZoneInfo("UTC"))
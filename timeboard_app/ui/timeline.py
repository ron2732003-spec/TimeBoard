import streamlit as st
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from timeboard_core.events import instantiate_for_day
from timeboard_core.renderer import format_zone_label
from timeboard_core.overlays import TRADING_SESSIONS
from timeboard_core.settings import ZOOM_LEVELS


# ------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------
WEEKDAY_COLORS = {
    0: "#2d4a3e",  # Monday    - Green
    1: "#2d3a4a",  # Tuesday   - Blue
    2: "#3d2d4a",  # Wednesday - Purple
    3: "#4a4a2d",  # Thursday  - Olive
    4: "#4a2d2d",  # Friday    - Red
    5: "#2d4a4a",  # Saturday  - Cyan
    6: "#4a3a2d",  # Sunday    - Orange
}

# Lighter versions for daylight hours
WEEKDAY_COLORS_LIGHT = {
    0: "#4a7a6e",  # Monday    - Green (lighter)
    1: "#4a6a7a",  # Tuesday   - Blue (lighter)
    2: "#6a5a7a",  # Wednesday - Purple (lighter)
    3: "#7a7a4a",  # Thursday  - Olive (lighter)
    4: "#7a4a4a",  # Friday    - Red (lighter)
    5: "#4a7a7a",  # Saturday  - Cyan (lighter)
    6: "#7a6a4a",  # Sunday    - Orange (lighter)
}

WEEKDAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# Default daylight settings
DEFAULT_DAYLIGHT_START = 7
DEFAULT_DAYLIGHT_END = 22
DEFAULT_TRANSITION = 1.5


# ------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------
def _format_date(dt: datetime) -> str:
    """Format date as 'Mon 06.01.'"""
    return f"{WEEKDAY_NAMES[dt.weekday()]} {dt.strftime('%d.%m.')}"


def _format_date_short(dt: datetime) -> str:
    """Format date as 'Mon 06.'"""
    return f"{WEEKDAY_NAMES[dt.weekday()]} {dt.strftime('%d.')}"


# ------------------------------------------------------------------
# CSS for Timeline
# ------------------------------------------------------------------
def get_timeline_css(timeline_width: int) -> str:
    return f"""
<style>
.tb-scroll-container {{
    overflow-x: auto;
    overflow-y: visible;
    width: 100%;
    padding: 10px 0;
    margin: 10px 0;
}}

.tb-timeline-inner {{
    width: {timeline_width}px;
    position: relative;
    background: #0e1117;
}}

.tb-hours-row {{
    position: relative;
    height: 28px;
    border-bottom: 1px solid #333;
    margin-bottom: 8px;
}}

.tb-day-header {{
    position: absolute;
    font-size: 11px;
    font-weight: 600;
    color: #fff;
    background: #1a1a2e;
    padding: 3px 8px;
    border-radius: 3px;
    top: 3px;
    z-index: 5;
}}

.tb-hour-mark {{
    position: absolute;
    font-size: 9px;
    color: #555;
    top: 14px;
}}

.tb-zone-section {{
    margin-bottom: 16px;
}}

.tb-zone-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 4px 8px;
    background: #1a1a2e;
    border-radius: 4px 4px 0 0;
}}

.tb-zone-name {{
    font-weight: 600;
    font-size: 13px;
    color: #fff;
}}

.tb-zone-times {{
    display: flex;
    gap: 20px;
    font-size: 12px;
}}

.tb-time-now {{ color: #4da3ff; }}
.tb-time-active {{ color: #ff3b3b; }}

.tb-zone-bar {{
    position: relative;
    height: 42px;
    background: #111;
    border-radius: 0 0 4px 4px;
    overflow: visible;
}}

.tb-day-segment {{
    position: absolute;
    top: 0;
    bottom: 0;
    display: flex;
    align-items: flex-end;
    padding: 0 0 4px 6px;
    box-sizing: border-box;
}}

.tb-day-segment.with-border {{
    border-right: 2px solid #ffd700;
}}

.tb-day-label {{
    font-size: 9px;
    color: rgba(255,255,255,0.5);
    white-space: nowrap;
}}

.tb-transition {{
    position: absolute;
    top: 0;
    bottom: 0;
    z-index: 2;
    pointer-events: none;
}}

.tb-daylight {{
    position: absolute;
    top: 0;
    bottom: 0;
    z-index: 2;
    pointer-events: none;
}}

.tb-midnight-line {{
    position: absolute;
    top: 0;
    bottom: 0;
    border-left: 2px solid #ffd700;
    z-index: 10;
}}

.tb-now-line {{
    position: absolute;
    top: 0;
    bottom: 0;
    border-left: 2px dashed #4da3ff;
    z-index: 15;
}}

.tb-active-line {{
    position: absolute;
    top: 0;
    bottom: 0;
    border-left: 3px solid #ff3b3b;
    z-index: 16;
}}

.tb-event {{
    position: absolute;
    top: 6px;
    height: 22px;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 10px;
    color: white;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    z-index: 12;
}}

.tb-event.highlighted {{
    border: 2px solid #fff;
    box-shadow: 0 0 8px rgba(255,255,255,0.4);
}}

.tb-session {{
    position: absolute;
    top: 26px;
    height: 14px;
    border-radius: 2px;
    padding: 0 4px;
    font-size: 8px;
    color: #333;
    white-space: nowrap;
    overflow: hidden;
    z-index: 11;
    opacity: 0.8;
}}
</style>
"""


def render_timeline(
    zones: list,
    settings,
    now_local_minute: int,
    active_minute: int,
    today_utc: datetime,
    local_tz
):
    """
    Renders the scrollable multi-day timeline.
    """
    
    # ------------------------------------------------------------------
    # Get zoom settings
    # ------------------------------------------------------------------
    zoom_level = getattr(settings, 'zoom_level', 'week')
    zoom_config = ZOOM_LEVELS.get(zoom_level, ZOOM_LEVELS['week'])
    visible_days = zoom_config['days']
    timeline_width = zoom_config['width']
    total_minutes = visible_days * 1440
    
    # Helper for percentage calculation
    def _pct(minutes: float) -> float:
        return (minutes / total_minutes) * 100
    
    # ------------------------------------------------------------------
    # Session State for Navigation
    # ------------------------------------------------------------------
    if "timeline_start_offset" not in st.session_state:
        st.session_state["timeline_start_offset"] = 0 if visible_days == 1 else -(visible_days // 2)
    
    # Adjust offset when zoom changes
    if "last_zoom_level" not in st.session_state:
        st.session_state["last_zoom_level"] = zoom_level
    
    if st.session_state["last_zoom_level"] != zoom_level:
        # Reset to center on today when zoom changes
        st.session_state["timeline_start_offset"] = 0 if visible_days == 1 else -(visible_days // 2)
        st.session_state["last_zoom_level"] = zoom_level
    
    # ------------------------------------------------------------------
    # Navigation Buttons
    # ------------------------------------------------------------------
    st.markdown("### 📅 Timeline")
    
    # Navigation step based on zoom level
    nav_step = 1 if visible_days <= 3 else 7
    nav_step_small = 1
    
    nav_cols = st.columns([1, 1, 1, 3, 1, 1, 1])
    
    with nav_cols[0]:
        if st.button(f"⏮ -{nav_step}d", key="nav_m7"):
            st.session_state["timeline_start_offset"] -= nav_step
    
    with nav_cols[1]:
        if st.button(f"◀ -{nav_step_small}d", key="nav_m1"):
            st.session_state["timeline_start_offset"] -= nav_step_small
    
    with nav_cols[2]:
        if st.button("📍 Today", key="nav_today"):
            st.session_state["timeline_start_offset"] = 0 if visible_days == 1 else -(visible_days // 2)
    
    with nav_cols[3]:
        offset = st.session_state["timeline_start_offset"]
        start_date = today_utc + timedelta(days=offset)
        end_date = start_date + timedelta(days=visible_days - 1)
        
        if visible_days == 1:
            date_display = f"{_format_date(start_date)}"
        else:
            date_display = f"{_format_date_short(start_date)} — {_format_date_short(end_date)}"
        
        st.markdown(
            f"<div style='text-align:center;padding:6px;font-weight:500;'>"
            f"{date_display}"
            f"</div>",
            unsafe_allow_html=True
        )
    
    with nav_cols[4]:
        if st.button(f"+{nav_step_small}d ▶", key="nav_p1"):
            st.session_state["timeline_start_offset"] += nav_step_small
    
    with nav_cols[5]:
        if st.button(f"+{nav_step}d ⏭", key="nav_p7"):
            st.session_state["timeline_start_offset"] += nav_step
    
    # ------------------------------------------------------------------
    # Base Calculations
    # ------------------------------------------------------------------
    offset_days = st.session_state["timeline_start_offset"]
    now_utc = st.session_state["now_utc"]
    
    timeline_start_utc = (today_utc + timedelta(days=offset_days)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    
    # Get settings
    show_trading_sessions = getattr(settings, 'show_trading_sessions', False)
    show_daylight = getattr(settings, 'show_daylight', False)
    daylight_start = getattr(settings, 'daylight_start_hour', DEFAULT_DAYLIGHT_START)
    daylight_end = getattr(settings, 'daylight_end_hour', DEFAULT_DAYLIGHT_END)
    transition_hours = getattr(settings, 'transition_duration', DEFAULT_TRANSITION)
    
    # ------------------------------------------------------------------
    # Insert CSS
    # ------------------------------------------------------------------
    st.markdown(get_timeline_css(timeline_width), unsafe_allow_html=True)
    
    # ------------------------------------------------------------------
    # Build HTML completely
    # ------------------------------------------------------------------
    html_parts = []
    html_parts.append("<div class='tb-scroll-container'>")
    html_parts.append("<div class='tb-timeline-inner'>")
    
    # ---- Hours Row ----
    html_parts.append("<div class='tb-hours-row'>")
    
    # Determine hour marks based on zoom level
    if visible_days == 1:
        hour_marks = list(range(0, 24, 2))  # Every 2 hours for day view
    elif visible_days == 3:
        hour_marks = [0, 6, 12, 18]  # Every 6 hours
    else:
        hour_marks = [0, 6, 12, 18]  # Every 6 hours
    
    for day in range(visible_days):
        day_start_min = day * 1440
        day_date = timeline_start_utc + timedelta(days=day)
        
        # Day Header
        html_parts.append(
            f"<div class='tb-day-header' style='left:{_pct(day_start_min)}%;'>"
            f"{_format_date(day_date)}</div>"
        )
        
        # Hour Marks
        for h in hour_marks:
            minute = day_start_min + h * 60
            html_parts.append(
                f"<div class='tb-hour-mark' style='left:{_pct(minute)}%;'>{h:02d}</div>"
            )
    
    html_parts.append("</div>")  # End hours-row
    
    # ---- Timezones ----
    for zone in zones:
        tz = ZoneInfo(zone)
        zone_label = format_zone_label(zone, zone == settings.church_timezone, settings)
        
        # Calculate times
        zone_now = now_utc.astimezone(tz)
        zone_now_str = zone_now.strftime("%H:%M")
        zone_now_date = _format_date(zone_now)
        
        # Use active_time_utc from session state (set by active_time slider)
        active_utc = st.session_state.get("active_time_utc", now_utc)
        zone_active = active_utc.astimezone(tz)
        zone_active_str = zone_active.strftime("%H:%M")
        
        # Zone Section
        html_parts.append("<div class='tb-zone-section'>")
        
        # Header
        html_parts.append(
            f"<div class='tb-zone-header'>"
            f"<span class='tb-zone-name'>{zone_label}</span>"
            f"<span class='tb-zone-times'>"
            f"<span class='tb-time-now'>Now: {zone_now_str} ({zone_now_date})</span>"
            f"<span class='tb-time-active'>Active: {zone_active_str}</span>"
            f"</span></div>"
        )
        
        # Bar
        html_parts.append("<div class='tb-zone-bar'>")
        
        # ---- Process each day ----
        seen_days = set()
        
        for day in range(-1, visible_days + 2):
            utc_day = timeline_start_utc + timedelta(days=day)
            zone_ref = utc_day.astimezone(tz)
            zone_midnight = zone_ref.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Avoid duplicates
            day_key = zone_midnight.strftime("%Y-%m-%d")
            if day_key in seen_days:
                continue
            seen_days.add(day_key)
            
            midnight_utc = zone_midnight.astimezone(ZoneInfo("UTC"))
            day_start_min = (midnight_utc - timeline_start_utc).total_seconds() / 60
            
            if day_start_min > total_minutes or day_start_min + 1440 < 0:
                continue
            
            weekday = zone_midnight.weekday()
            color_dark = WEEKDAY_COLORS[weekday]
            color_light = WEEKDAY_COLORS_LIGHT[weekday]
            date_label = _format_date(zone_midnight)
            
            if show_daylight:
                # ---- DAYLIGHT MODE: Render with gradients ----
                transition_min = transition_hours * 60
                
                # Night 1: 00:00 to sunrise start
                night1_start = day_start_min
                night1_end = day_start_min + (daylight_start * 60) - transition_min
                
                # Sunrise: transition from dark to light
                sunrise_start = night1_end
                sunrise_end = day_start_min + (daylight_start * 60)
                
                # Daylight: full light period
                daylight_start_min_local = sunrise_end
                daylight_end_min_local = day_start_min + (daylight_end * 60)
                
                # Sunset: transition from light to dark
                sunset_start = daylight_end_min_local
                sunset_end = daylight_end_min_local + transition_min
                
                # Night 2: after sunset to midnight
                night2_start = sunset_end
                night2_end = day_start_min + 1440
                
                # Helper function to render a segment
                def render_segment(start, end, bg, show_label=False, is_last=False):
                    if end <= 0 or start >= total_minutes:
                        return
                    vis_start = max(0, start)
                    vis_end = min(total_minutes, end)
                    if vis_end <= vis_start:
                        return
                    
                    border_class = "with-border" if is_last else ""
                    label_html = f"<span class='tb-day-label'>{date_label}</span>" if show_label else ""
                    
                    html_parts.append(
                        f"<div class='tb-day-segment {border_class}' style='"
                        f"left:{_pct(vis_start)}%;"
                        f"width:{_pct(vis_end - vis_start)}%;"
                        f"background:{bg};'>"
                        f"{label_html}</div>"
                    )
                
                # Render Night 1 (dark)
                render_segment(night1_start, night1_end, color_dark, show_label=True)
                
                # Render Sunrise (gradient dark → light)
                if sunrise_end > 0 and sunrise_start < total_minutes:
                    vis_start = max(0, sunrise_start)
                    vis_end = min(total_minutes, sunrise_end)
                    if vis_end > vis_start:
                        html_parts.append(
                            f"<div class='tb-transition' style='"
                            f"left:{_pct(vis_start)}%;"
                            f"width:{_pct(vis_end - vis_start)}%;"
                            f"background:linear-gradient(to right, {color_dark}, {color_light});'></div>"
                        )
                
                # Render Daylight (light)
                render_segment(daylight_start_min_local, daylight_end_min_local, color_light)
                
                # Render Sunset (gradient light → dark)
                if sunset_end > 0 and sunset_start < total_minutes:
                    vis_start = max(0, sunset_start)
                    vis_end = min(total_minutes, sunset_end)
                    if vis_end > vis_start:
                        html_parts.append(
                            f"<div class='tb-transition' style='"
                            f"left:{_pct(vis_start)}%;"
                            f"width:{_pct(vis_end - vis_start)}%;"
                            f"background:linear-gradient(to right, {color_light}, {color_dark});'></div>"
                        )
                
                # Render Night 2 (dark) with border
                render_segment(night2_start, night2_end, color_dark, is_last=True)
                
                # Midnight line at day boundary
                if 0 < day_start_min < total_minutes:
                    html_parts.append(
                        f"<div class='tb-midnight-line' style='left:{_pct(day_start_min)}%;'></div>"
                    )
            
            else:
                # ---- SIMPLE MODE: Solid color per day ----
                visible_start = max(0, day_start_min)
                visible_end = min(total_minutes, day_start_min + 1440)
                
                if visible_end > visible_start:
                    html_parts.append(
                        f"<div class='tb-day-segment with-border' style='"
                        f"left:{_pct(visible_start)}%;"
                        f"width:{_pct(visible_end - visible_start)}%;"
                        f"background:{color_dark};'>"
                        f"<span class='tb-day-label'>{date_label}</span></div>"
                    )
        
        # ---- Now Marker ----
        now_min_from_start = (now_utc - timeline_start_utc).total_seconds() / 60
        if 0 <= now_min_from_start <= total_minutes:
            html_parts.append(
                f"<div class='tb-now-line' style='left:{_pct(now_min_from_start)}%;'></div>"
            )
        
        # ---- Active Marker ----
        active_min_from_start = (active_utc - timeline_start_utc).total_seconds() / 60
        if 0 <= active_min_from_start <= total_minutes:
            html_parts.append(
                f"<div class='tb-active-line' style='left:{_pct(active_min_from_start)}%;'></div>"
            )
        
        # ---- Events ----
        for day in range(visible_days + 1):
            day_utc = timeline_start_utc + timedelta(days=day)
            
            for event in st.session_state.get("events", []):
                inst = instantiate_for_day(event, day_utc)
                if not inst:
                    continue
                
                event_start_tz = inst.start_utc.astimezone(tz)
                event_end_tz = inst.end_utc.astimezone(tz)
                
                event_start_min = (inst.start_utc - timeline_start_utc).total_seconds() / 60
                event_end_min = (inst.end_utc - timeline_start_utc).total_seconds() / 60
                
                if event_end_min < 0 or event_start_min > total_minutes:
                    continue
                
                visible_start = max(0, event_start_min)
                visible_end = min(total_minutes, event_end_min)
                
                if visible_end <= visible_start:
                    continue
                
                color = getattr(inst, "_color", "#00FFFF")
                is_highlighted = event_start_min <= active_min_from_start < event_end_min
                hl_class = " highlighted" if is_highlighted else ""
                
                time_label = f"{event_start_tz.strftime('%H:%M')}-{event_end_tz.strftime('%H:%M')}"
                
                html_parts.append(
                    f"<div class='tb-event{hl_class}' style='"
                    f"left:{_pct(visible_start)}%;"
                    f"width:{_pct(visible_end - visible_start)}%;"
                    f"background:{color};' "
                    f"title='{inst.title} ({time_label})'>"
                    f"{inst.title}</div>"
                )
        
        # ---- Trading Sessions (only if enabled) ----
        if show_trading_sessions:
            for session in TRADING_SESSIONS:
                if session.zone != zone:
                    continue
                
                for day in range(visible_days + 1):
                    day_utc = timeline_start_utc + timedelta(days=day)
                    day_in_zone = day_utc.astimezone(tz).replace(hour=0, minute=0, second=0, microsecond=0)
                    
                    session_start = day_in_zone.replace(
                        hour=session.start.hour, minute=session.start.minute
                    )
                    session_end = day_in_zone.replace(
                        hour=session.end.hour, minute=session.end.minute
                    )
                    
                    if session_end <= session_start:
                        session_end += timedelta(days=1)
                    
                    session_start_utc = session_start.astimezone(ZoneInfo("UTC"))
                    session_end_utc = session_end.astimezone(ZoneInfo("UTC"))
                    
                    start_min = (session_start_utc - timeline_start_utc).total_seconds() / 60
                    end_min = (session_end_utc - timeline_start_utc).total_seconds() / 60
                    
                    if end_min < 0 or start_min > total_minutes:
                        continue
                    
                    visible_start = max(0, start_min)
                    visible_end = min(total_minutes, end_min)
                    
                    if visible_end <= visible_start:
                        continue
                    
                    html_parts.append(
                        f"<div class='tb-session' style='"
                        f"left:{_pct(visible_start)}%;"
                        f"width:{_pct(visible_end - visible_start)}%;"
                        f"background:{session.color};'>"
                        f"{session.name}</div>"
                    )
        
        html_parts.append("</div>")  # End zone-bar
        html_parts.append("</div>")  # End zone-section
    
    html_parts.append("</div>")  # End timeline-inner
    html_parts.append("</div>")  # End scroll-container
    
    # ------------------------------------------------------------------
    # Render everything in ONE call
    # ------------------------------------------------------------------
    st.markdown("".join(html_parts), unsafe_allow_html=True)
    
    # ------------------------------------------------------------------
    # Legend
    # ------------------------------------------------------------------
    with st.expander("📖 Legend"):
        cols = st.columns(7)
        for i, (day_name, color) in enumerate(zip(WEEKDAY_NAMES, WEEKDAY_COLORS.values())):
            with cols[i]:
                st.markdown(
                    f"<div style='background:{color};padding:8px;border-radius:4px;text-align:center;color:#fff;'>{day_name}</div>",
                    unsafe_allow_html=True
                )
        
        legend_items = [
            "- 🔵 **Blue dashed line** = Current time (Now)",
            "- 🔴 **Red line** = Selected time (Active)",
            "- 🟡 **Yellow line** = Day change (Midnight)",
        ]
        
        if show_daylight:
            sunrise_start = daylight_start - transition_hours
            sunset_end = daylight_end + transition_hours
            legend_items.extend([
                f"- 🌅 **Gradient** = Sunrise ({sunrise_start:.1f}:00 → {daylight_start:02d}:00)",
                f"- ☀️ **Lighter area** = Daylight ({daylight_start:02d}:00 - {daylight_end:02d}:00)",
                f"- 🌇 **Gradient** = Sunset ({daylight_end:02d}:00 → {sunset_end:.1f}:00)",
                "- 🌙 **Darker area** = Night hours",
            ])
        
        st.markdown("\n".join(legend_items))
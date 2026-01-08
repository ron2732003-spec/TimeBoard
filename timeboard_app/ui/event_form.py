import streamlit as st
from datetime import datetime, time, date, timedelta
from zoneinfo import ZoneInfo
from timeboard_core.events import (
    Event, create_event, 
    EVENT_CATEGORIES, RECURRENCE_TYPES, WEEKDAY_NAMES, 
    COLOR_PRESETS, format_recurrence, DEFAULT_REMINDERS_MIN
)
from timeboard_core.settings import AVAILABLE_TIMEZONES, TIMEZONE_ORDER


def render_event_form(settings):
    """Render the event creation/editing form"""
    
    if not st.session_state.get("show_event_form", False):
        return
    
    # Get minute step from settings
    minute_step = getattr(settings, 'minute_step', 5)
    
    st.markdown("---")
    st.markdown("## ➕ Create Event")
    
    # ----- Category Selection (outside form for dynamic updates) -----
    st.markdown("**📁 Event Type**")
    
    # Create category buttons in rows
    categories = list(EVENT_CATEGORIES.keys())
    
    if "selected_category" not in st.session_state:
        st.session_state["selected_category"] = "work"
    
    # First row (6 items)
    cat_cols1 = st.columns(6)
    for i, cat_id in enumerate(categories[:6]):
        cat = EVENT_CATEGORIES[cat_id]
        with cat_cols1[i]:
            is_selected = st.session_state["selected_category"] == cat_id
            btn_type = "primary" if is_selected else "secondary"
            if st.button(
                cat["icon"], 
                key=f"cat_btn_{cat_id}",
                type=btn_type,
                use_container_width=True,
                help=cat["label"]
            ):
                st.session_state["selected_category"] = cat_id
                # Reset color to category default
                st.session_state["selected_color"] = cat["color"]
                st.rerun()
    
    # Second row (remaining items)
    cat_cols2 = st.columns(6)
    for i, cat_id in enumerate(categories[6:]):
        cat = EVENT_CATEGORIES[cat_id]
        with cat_cols2[i]:
            is_selected = st.session_state["selected_category"] == cat_id
            btn_type = "primary" if is_selected else "secondary"
            if st.button(
                cat["icon"], 
                key=f"cat_btn_{cat_id}",
                type=btn_type,
                use_container_width=True,
                help=cat["label"]
            ):
                st.session_state["selected_category"] = cat_id
                # Reset color to category default
                st.session_state["selected_color"] = cat["color"]
                st.rerun()
    
    selected_cat_id = st.session_state["selected_category"]
    selected_cat = EVENT_CATEGORIES[selected_cat_id]
    
    # Show selected category name
    st.markdown(f"**Selected:** {selected_cat['label']}")
    
    # ----- Color Selection (outside form for dynamic updates) -----
    st.markdown("**🎨 Color**")
    
    if "selected_color" not in st.session_state:
        st.session_state["selected_color"] = selected_cat["color"]
    
    color_cols = st.columns(7)
    for i, (color_id, color_info) in enumerate(COLOR_PRESETS.items()):
        with color_cols[i]:
            is_selected = st.session_state["selected_color"] == color_info["color"]
            # Create colored button
            btn_style = "border: 3px solid white;" if is_selected else ""
            if st.button(
                "●",
                key=f"color_btn_{color_id}",
                help=color_info["label"],
                use_container_width=True,
            ):
                st.session_state["selected_color"] = color_info["color"]
                st.rerun()
            # Show color indicator
            st.markdown(
                f"<div style='background:{color_info['color']};height:8px;border-radius:4px;{btn_style}'></div>",
                unsafe_allow_html=True
            )
    
    # ----- Sleep Warning State -----
    if "sleep_warning_confirmed" not in st.session_state:
        st.session_state["sleep_warning_confirmed"] = False
    
    with st.form("add_event_form", clear_on_submit=True):
        # ----- Title -----
        # Different title handling based on category
        if selected_cat.get("has_custom_title"):
            # Custom category - free text input
            title = st.text_input(
                "Event Title",
                placeholder="Enter custom event name...",
                key="event_title"
            )
        elif selected_cat.get("has_name_input"):
            # Fellowship - needs a name
            fellowship_name = st.text_input(
                "Fellowship with...",
                placeholder="Enter name (e.g., John, Small Group...)",
                key="fellowship_name"
            )
            title = f"Fellowship with {fellowship_name}" if fellowship_name else "Fellowship"
        else:
            # Predefined category - use category label as title
            title = selected_cat["label"].split(" ", 1)[1] if " " in selected_cat["label"] else selected_cat["label"]
            st.markdown(f"**Event:** {selected_cat['icon']} {title}")
        
        # ----- Date and Timezone Row -----
        col1, col2 = st.columns(2)
        
        with col1:
            # Default to today
            today = datetime.now().date()
            event_date = st.date_input(
                "📅 Date",
                value=today,
                key="event_date"
            )
        
        with col2:
            # Reference timezone - sorted by our continent groups
            default_tz_idx = TIMEZONE_ORDER.index(settings.church_timezone) if settings.church_timezone in TIMEZONE_ORDER else 0
            ref_tz = st.selectbox(
                "🌍 Reference Timezone",
                options=TIMEZONE_ORDER,
                index=default_tz_idx,
                format_func=lambda x: AVAILABLE_TIMEZONES.get(x, x),
                key="event_ref_tz",
                help="The timezone in which you're specifying the time"
            )
        
        # ----- Time Row -----
        col3, col4, col5 = st.columns(3)
        
        with col3:
            # Generate time options based on minute step
            time_options = []
            for h in range(24):
                for m in range(0, 60, minute_step):
                    time_options.append(time(h, m))
            
            # Default start time based on category
            if selected_cat_id == "sleep":
                default_start = time(22, 0)  # 10 PM for sleep
            elif selected_cat_id == "gym":
                default_start = time(6, 0)   # 6 AM for gym
            elif selected_cat_id == "bible_reading":
                default_start = time(6, 30)  # 6:30 AM for bible reading
            elif selected_cat_id == "reflecting":
                default_start = time(21, 0)  # 9 PM for reflecting
            elif selected_cat_id == "evangelizing":
                default_start = time(14, 0)  # 2 PM for evangelizing
            else:
                # Next hour
                now = datetime.now()
                default_start = time((now.hour + 1) % 24, 0)
            
            # Find closest time in options
            default_idx = 0
            for i, t in enumerate(time_options):
                if t >= default_start:
                    default_idx = i
                    break
            
            start_time = st.selectbox(
                "🕐 Start Time",
                options=time_options,
                index=default_idx,
                format_func=lambda t: t.strftime("%H:%M"),
                key="event_start_time"
            )
        
        with col4:
            # Default duration based on category
            if selected_cat_id == "sleep":
                default_duration = 480  # 8 hours
            elif selected_cat_id == "gym":
                default_duration = 90   # 1.5 hours
            elif selected_cat_id == "bible_reading":
                default_duration = 30   # 30 minutes
            elif selected_cat_id == "break":
                default_duration = 15   # 15 minutes
            elif selected_cat_id == "work":
                default_duration = 480  # 8 hours
            elif selected_cat_id == "basket_meeting":
                default_duration = 120  # 2 hours
            elif selected_cat_id == "fellowship":
                default_duration = 60   # 1 hour
            elif selected_cat_id == "reflecting":
                default_duration = 30   # 30 minutes
            elif selected_cat_id == "evangelizing":
                default_duration = 120  # 2 hours
            else:
                default_duration = 60   # 1 hour default
            
            # Calculate default end time
            start_minutes = start_time.hour * 60 + start_time.minute
            default_end_minutes = (start_minutes + default_duration) % 1440
            default_end_time = time(default_end_minutes // 60, default_end_minutes % 60)
            
            # Find closest time in options
            default_end_idx = 0
            for i, t in enumerate(time_options):
                if t.hour * 60 + t.minute >= default_end_minutes:
                    default_end_idx = i
                    break
            
            end_time = st.selectbox(
                "🕑 End Time",
                options=time_options,
                index=default_end_idx,
                format_func=lambda t: t.strftime("%H:%M"),
                key="event_end_time"
            )
        
        with col5:
            # Calculate duration
            start_minutes = start_time.hour * 60 + start_time.minute
            end_minutes = end_time.hour * 60 + end_time.minute
            
            # Handle overnight events
            if end_minutes <= start_minutes:
                end_minutes += 1440  # Add 24 hours
            
            duration = end_minutes - start_minutes
            
            st.markdown(f"**Duration**")
            if duration >= 60:
                hours = duration // 60
                mins = duration % 60
                if mins > 0:
                    st.markdown(f"⏱️ {hours}h {mins}min")
                else:
                    st.markdown(f"⏱️ {hours}h")
            else:
                st.markdown(f"⏱️ {duration}min")
        
        # ----- Sleep Warning -----
        show_sleep_warning = False
        if selected_cat_id == "sleep":
            min_duration = selected_cat.get("min_duration_warning", 0)
            if duration < min_duration:
                show_sleep_warning = True
                st.warning(selected_cat.get("warning_message", "Warning: Short sleep duration"))
                st.info(selected_cat.get("warning_advice", ""))
        
        # ----- Recurrence -----
        st.markdown("**🔁 Recurrence**")
        
        recurrence = st.selectbox(
            "Repeat",
            options=list(RECURRENCE_TYPES.keys()),
            format_func=lambda x: RECURRENCE_TYPES[x],
            key="event_recurrence",
            label_visibility="collapsed"
        )
        
        # Show end date option for recurring events
        end_date_value = None
        if recurrence != "once":
            col_rec1, col_rec2 = st.columns(2)
            with col_rec1:
                has_end_date = st.checkbox("Set end date", key="event_has_end_date")
            with col_rec2:
                if has_end_date:
                    end_date_value = st.date_input(
                        "End date",
                        value=today + timedelta(days=30),
                        key="event_end_date",
                        label_visibility="collapsed"
                    )
        
        # ----- Reminders Info -----
        st.markdown(f"**🔔 Reminders:** {DEFAULT_REMINDERS_MIN[0]} min & {DEFAULT_REMINDERS_MIN[1]} min before")
        
        # ----- Submit Buttons -----
        st.markdown("---")
        col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
        
        with col_btn1:
            # Preview with selected color
            selected_color = st.session_state.get("selected_color", selected_cat["color"])
            if title:
                tz_name = AVAILABLE_TIMEZONES.get(ref_tz, ref_tz).split('(')[0].strip()
                st.markdown(
                    f"<small><span style='color:{selected_color};'>●</span> {selected_cat['icon']} {title} on {event_date.strftime('%a %d.%m.%Y')} "
                    f"at {start_time.strftime('%H:%M')} ({tz_name})</small>",
                    unsafe_allow_html=True
                )
        
        with col_btn2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        with col_btn3:
            if show_sleep_warning:
                create = st.form_submit_button("⚠️ Create Anyway", type="primary", use_container_width=True)
            else:
                create = st.form_submit_button("✅ Create", type="primary", use_container_width=True)
        
        # ----- Handle Form Submission -----
        if cancel:
            st.session_state["show_event_form"] = False
            st.session_state["selected_category"] = "work"
            st.session_state.pop("selected_color", None)
            st.rerun()
        
        if create:
            # Validate title
            final_title = title.strip() if title else selected_cat["label"]
            
            if selected_cat.get("has_custom_title") and not title.strip():
                st.error("Please enter an event title")
            elif selected_cat.get("has_name_input") and not fellowship_name.strip():
                st.error("Please enter a name for the fellowship")
            else:
                # Create the event
                tz = ZoneInfo(ref_tz)
                start_dt = datetime.combine(event_date, start_time).replace(tzinfo=tz)
                
                # Handle end date
                end_dt = None
                if end_date_value:
                    end_dt = datetime.combine(end_date_value, time(23, 59)).replace(tzinfo=tz)
                
                # Get selected color
                selected_color = st.session_state.get("selected_color", selected_cat["color"])
                
                event = create_event(
                    title=final_title,
                    category_id=selected_cat_id,
                    start_dt=start_dt,
                    duration_min=duration,
                    reference_tz=ref_tz,
                    color=selected_color,
                    recurrence=recurrence,
                    end_date=end_dt,
                )
                
                # Add to events list
                if "events" not in st.session_state:
                    st.session_state["events"] = []
                
                st.session_state["events"].append(event)
                st.session_state["show_event_form"] = False
                st.session_state["selected_category"] = "work"
                st.session_state.pop("selected_color", None)
                st.success(f"✅ Event '{final_title}' created!")
                st.rerun()


def render_event_list():
    """Render the list of existing events"""
    
    events = st.session_state.get("events", [])
    
    if not events:
        return
    
    with st.expander(f"📋 Events ({len(events)})", expanded=False):
        for i, event in enumerate(events):
            col1, col2, col3, col4 = st.columns([0.5, 2.5, 2, 0.5])
            
            with col1:
                cat = EVENT_CATEGORIES.get(event.category_id, EVENT_CATEGORIES["custom"])
                st.markdown(f"{cat['icon']}")
            
            with col2:
                st.markdown(
                    f"<span style='color:{event.color};'>●</span> **{event.title}**",
                    unsafe_allow_html=True
                )
            
            with col3:
                # Show time in reference timezone
                tz = ZoneInfo(event.reference_tz)
                start_local = event.start_utc.astimezone(tz)
                st.markdown(
                    f"<small>{start_local.strftime('%d.%m. %H:%M')} · {format_recurrence(event)}</small>",
                    unsafe_allow_html=True
                )
            
            with col4:
                if st.button("🗑️", key=f"delete_event_{i}", help="Delete event"):
                    st.session_state["events"].pop(i)
                    st.rerun()
        
        # Legend
        st.markdown("---")
        st.markdown("**🔔 Reminders:** All events have reminders at 30 min and 10 min before start")


def render_add_event_button():
    """Render the button to open the event form"""
    
    if st.button("➕ Add Event", key="add_event_btn", use_container_width=True):
        st.session_state["show_event_form"] = True
        st.rerun()
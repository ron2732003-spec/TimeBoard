import streamlit as st
from timeboard_core.settings import (
    TIMEZONE_GROUPS, 
    AVAILABLE_TIMEZONES, 
    TIMEZONE_ORDER,
    DEFAULT_TIMEZONES,
    ZOOM_LEVELS,
    MINUTE_STEPS,
)


def render_settings_panel():
    """Render the settings panel for timezone selection and trading sessions"""
    
    settings = st.session_state["settings"]
    
    with st.expander("⚙️ Settings", expanded=False):
        
        # -----------------------------------------------------
        # Timezone Selection
        # -----------------------------------------------------
        st.markdown("**Timezones**")
        
        # Current active timezones
        current_zones = settings.active_timezones.copy()
        
        # Multi-select with grouped options (sorted by continent)
        selected_zones = st.multiselect(
            "Select timezones to display",
            options=TIMEZONE_ORDER,
            default=[tz for tz in current_zones if tz in TIMEZONE_ORDER],
            format_func=lambda x: AVAILABLE_TIMEZONES.get(x, x),
            key="timezone_multiselect"
        )
        
        # Update settings if changed
        if selected_zones != current_zones:
            settings.active_timezones = selected_zones
        
        # -----------------------------------------------------
        # Quick Add by Region
        # -----------------------------------------------------
        st.markdown("**Quick Add by Region:**")
        
        for group_name, group_zones in TIMEZONE_GROUPS.items():
            with st.container():
                cols = st.columns([2] + [1] * min(4, len(group_zones)))
                
                with cols[0]:
                    st.markdown(f"<small>{group_name}</small>", unsafe_allow_html=True)
                
                # Show first 4 timezones as quick buttons
                zone_items = list(group_zones.items())[:4]
                for i, (tz_id, tz_name) in enumerate(zone_items):
                    with cols[i + 1]:
                        # Short label (city name only)
                        short_name = tz_name.split(" (")[0].split("/")[-1]
                        
                        if tz_id in settings.active_timezones:
                            if st.button(f"✓ {short_name}", key=f"q_{tz_id}", help=f"Remove {tz_name}"):
                                settings.active_timezones.remove(tz_id)
                                st.rerun()
                        else:
                            if st.button(f"+ {short_name}", key=f"q_{tz_id}", help=f"Add {tz_name}"):
                                settings.active_timezones.append(tz_id)
                                st.rerun()
        
        st.markdown("---")
        
        # -----------------------------------------------------
        # Timeline View Options
        # -----------------------------------------------------
        st.markdown("**Timeline View**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Zoom level
            zoom_options = list(ZOOM_LEVELS.keys())
            zoom_labels = [ZOOM_LEVELS[z]["label"] for z in zoom_options]
            current_zoom_idx = zoom_options.index(settings.zoom_level) if settings.zoom_level in zoom_options else 2
            
            selected_zoom = st.selectbox(
                "🔍 Zoom Level",
                options=zoom_options,
                index=current_zoom_idx,
                format_func=lambda x: ZOOM_LEVELS[x]["label"],
                key="zoom_select"
            )
            
            if selected_zoom != settings.zoom_level:
                settings.zoom_level = selected_zoom
        
        with col2:
            # Minute steps
            step_options = list(MINUTE_STEPS.keys())
            current_step_idx = step_options.index(settings.minute_step) if settings.minute_step in step_options else 1
            
            selected_step = st.selectbox(
                "⏱️ Time Steps",
                options=step_options,
                index=current_step_idx,
                format_func=lambda x: MINUTE_STEPS[x],
                key="step_select"
            )
            
            if selected_step != settings.minute_step:
                settings.minute_step = selected_step
        
        st.markdown("---")
        
        # -----------------------------------------------------
        # Visual Options
        # -----------------------------------------------------
        st.markdown("**Visual Options**")
        
        # Daylight visualization toggle
        show_daylight = st.checkbox(
            "☀️ Show daylight hours (sunrise/sunset gradients)",
            value=settings.show_daylight,
            key="show_daylight_checkbox",
            help="Display lighter areas for daytime hours with gradient transitions"
        )
        
        if show_daylight != settings.show_daylight:
            settings.show_daylight = show_daylight
        
        # Trading sessions toggle
        show_sessions = st.checkbox(
            "📈 Show trading sessions (London, New York, Tokyo)",
            value=settings.show_trading_sessions,
            key="show_trading_sessions_checkbox",
            help="Display trading session overlays for major financial markets"
        )
        
        if show_sessions != settings.show_trading_sessions:
            settings.show_trading_sessions = show_sessions
        
        st.markdown("---")
        
        # -----------------------------------------------------
        # Reset Button
        # -----------------------------------------------------
        if st.button("🔄 Reset to Defaults", key="reset_settings"):
            settings.active_timezones = DEFAULT_TIMEZONES.copy()
            settings.show_trading_sessions = False
            settings.show_daylight = False
            settings.zoom_level = "week"
            settings.minute_step = 5
            st.rerun()
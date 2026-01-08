from dataclasses import dataclass, field
from typing import List, Dict

# Available timezones organized by continent/region
# Only valid IANA timezone identifiers
TIMEZONE_GROUPS: Dict[str, Dict[str, str]] = {
    "🌍 Africa": {
        "Africa/Johannesburg": "Johannesburg (SAST)",
        "Africa/Cairo": "Cairo (EET)",
        "Africa/Lagos": "Lagos (WAT)",
        "Africa/Nairobi": "Nairobi (EAT)",
        "Africa/Casablanca": "Casablanca (WET)",
    },
    "🌎 Americas": {
        "America/Los_Angeles": "Los Angeles (PST)",
        "America/Denver": "Denver (MST)",
        "America/Chicago": "Chicago (CST)",
        "America/New_York": "New York (EST)",
        "America/Toronto": "Toronto (EST)",
        "America/Mexico_City": "Mexico City (CST)",
        "America/Sao_Paulo": "São Paulo (BRT)",
        "America/Buenos_Aires": "Buenos Aires (ART)",
    },
    "🌏 Asia": {
        "Asia/Dubai": "Dubai (GST)",
        "Asia/Kolkata": "Mumbai/Delhi (IST)",
        "Asia/Bangkok": "Bangkok (ICT)",
        "Asia/Singapore": "Singapore (SGT)",
        "Asia/Hong_Kong": "Hong Kong (HKT)",
        "Asia/Shanghai": "Shanghai (CST)",
        "Asia/Tokyo": "Tokyo (JST)",
        "Asia/Seoul": "Seoul (KST)",
    },
    "🌍 Europe": {
        "Europe/London": "London (GMT)",
        "Europe/Paris": "Paris (CET)",
        "Europe/Berlin": "Berlin (CET)",
        "Europe/Amsterdam": "Amsterdam (CET)",
        "Europe/Zurich": "Zurich (CET)",
        "Europe/Moscow": "Moscow (MSK)",
        "Europe/Istanbul": "Istanbul (TRT)",
    },
    "🌏 Oceania": {
        "Australia/Perth": "Perth (AWST)",
        "Australia/Sydney": "Sydney (AEST)",
        "Australia/Melbourne": "Melbourne (AEST)",
        "Pacific/Auckland": "Auckland (NZST)",
    },
    "🌐 Other": {
        "UTC": "UTC",
    },
}

# Flat dict for easy lookup (timezone_id -> display_name)
AVAILABLE_TIMEZONES: Dict[str, str] = {}
for group_zones in TIMEZONE_GROUPS.values():
    AVAILABLE_TIMEZONES.update(group_zones)

# Ordered list of all timezone IDs (by continent order)
TIMEZONE_ORDER: List[str] = []
for group_zones in TIMEZONE_GROUPS.values():
    TIMEZONE_ORDER.extend(group_zones.keys())

# Default timezone selection
DEFAULT_TIMEZONES = [
    "America/Los_Angeles",
    "Europe/Berlin",
    "America/New_York",
]

# Zoom levels
ZOOM_LEVELS = {
    "day": {"label": "Day (24h)", "days": 1, "width": 1200},
    "3day": {"label": "3 Days", "days": 3, "width": 1800},
    "week": {"label": "Week (7 Days)", "days": 7, "width": 2400},
}

# Minute step options
MINUTE_STEPS = {
    1: "1 min (precise)",
    5: "5 min",
    15: "15 min (fast)",
    30: "30 min",
}


@dataclass
class UserSettings:
    church_timezone: str = "America/Los_Angeles"
    visibility_mode: str = "public"  
    # public | privacy

    public_display_style: str = "timezone"
    # timezone | standard
    
    # Active timezones to display
    active_timezones: List[str] = field(default_factory=lambda: DEFAULT_TIMEZONES.copy())
    
    # Show trading sessions (default: off)
    show_trading_sessions: bool = False
    
    # Show daylight/sunrise/sunset visualization (default: off)
    show_daylight: bool = False
    
    # Daylight hours configuration
    daylight_start_hour: int = 7    # 07:00
    daylight_end_hour: int = 22     # 22:00
    transition_duration: float = 1.5  # hours for sunrise/sunset gradient
    
    # Timeline zoom level: "day", "3day", "week"
    zoom_level: str = "week"
    
    # Minute steps for time selection: 1, 5, 15, 30
    minute_step: int = 5
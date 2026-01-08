from zoneinfo import ZoneInfo

ZONES = {
    "Europe/Berlin": ZoneInfo("Europe/Berlin"),
    "America/Los_Angeles": ZoneInfo("America/Los_Angeles"),
    "Africa/Johannesburg": ZoneInfo("Africa/Johannesburg"),
    "America/New_York": ZoneInfo("America/New_York"),
    "Europe/London": ZoneInfo("Europe/London"),
    "Asia/Tokyo": ZoneInfo("Asia/Tokyo"),
}

STANDARD_ZONE_ORDER = [
    "Africa/Johannesburg",
    "America/New_York",
    "Europe/London",
    "Asia/Tokyo",
]

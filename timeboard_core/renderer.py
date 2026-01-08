from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Dict
from .settings import UserSettings

def format_zone_label(
    zone_name: str,
    is_church_zone: bool,
    settings: UserSettings
) -> str:

    city = zone_name.split("/")[-1].replace("_", " ")

    if not is_church_zone:
        return city

    if settings.visibility_mode == "privacy":
        return f"{city} ✝"

    if settings.visibility_mode == "public":
        if settings.public_display_style == "standard":
            return f"{city} (standard)"
        return city

    return city

def project_time(dt_utc: datetime, zone: str) -> datetime:
    return dt_utc.astimezone(ZoneInfo(zone))

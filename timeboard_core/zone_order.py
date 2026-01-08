from typing import List, Optional
from zoneinfo import ZoneInfo
from .zones import STANDARD_ZONE_ORDER

def resolve_local_zone() -> str:
    try:
        return ZoneInfo.key  # system-resolved
    except Exception:
        return "UTC"

def resolve_zone_order(
    local_zone: str,
    church_zone: str,
    user_override: Optional[List[str]] = None
) -> List[str]:

    if user_override:
        return user_override

    zones = [local_zone]

    if church_zone != local_zone:
        zones.append(church_zone)

    for z in STANDARD_ZONE_ORDER:
        if z not in zones:
            zones.append(z)

    return zones

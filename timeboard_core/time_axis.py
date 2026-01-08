# timeboard_core/time_axis.py

DAY_MINUTES = 24 * 60              # 1440
STEP_MINUTES = 1                   # Jede Minute wählbar (war vorher 5)
MAX_MINUTE = DAY_MINUTES - 1       # 1439 (23:59)

def clamp_minute(m: int) -> int:
    return max(0, min(MAX_MINUTE, int(m)))

def snap_minute(m: int) -> int:
    """Nicht mehr nötig, aber für Kompatibilität beibehalten"""
    return clamp_minute(m)

def hhmm_from_minute(m: int) -> str:
    m = clamp_minute(m)
    h = m // 60
    mm = m % 60
    return f"{h:02d}:{mm:02d}"
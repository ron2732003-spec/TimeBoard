from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from zoneinfo import ZoneInfo
import uuid

# --- Defaults -------------------------------------------------

DEFAULT_REMINDERS_MIN = [30, 10]  # 30 min & 10 min before event

# --- Color Presets --------------------------------------------

COLOR_PRESETS = {
    "blue": {"label": "Blue", "color": "#4A90D9"},
    "red": {"label": "Red", "color": "#E74C3C"},
    "green": {"label": "Green", "color": "#27AE60"},
    "purple": {"label": "Purple", "color": "#9B59B6"},
    "orange": {"label": "Orange", "color": "#F39C12"},
    "teal": {"label": "Teal", "color": "#1ABC9C"},
    "pink": {"label": "Pink", "color": "#E91E63"},
}

# --- Event Categories with Colors -----------------------------

EVENT_CATEGORIES: Dict[str, Dict] = {
    "work": {
        "label": "💼 Work",
        "color": "#4A90D9",  # Professional blue
        "icon": "💼",
    },
    "gym": {
        "label": "🏋️ Gym",
        "color": "#E74C3C",  # Energy red
        "icon": "🏋️",
    },
    "bible_reading": {
        "label": "📖 Bible Reading",
        "color": "#8E44AD",  # Spiritual purple
        "icon": "📖",
    },
    "basket_meeting": {
        "label": "🧺 Basket Meeting",
        "color": "#F39C12",  # Warm orange
        "icon": "🧺",
    },
    "fellowship": {
        "label": "🤝 Fellowship with...",
        "color": "#27AE60",  # Friendly green
        "icon": "🤝",
        "has_name_input": True,
    },
    "training": {
        "label": "📚 Training",
        "color": "#3498DB",  # Learning blue
        "icon": "📚",
    },
    "service": {
        "label": "🙏 Service",
        "color": "#9B59B6",  # Service purple
        "icon": "🙏",
    },
    "evangelizing": {
        "label": "✝️ Evangelizing",
        "color": "#E91E63",  # Passionate pink
        "icon": "✝️",
    },
    "reflecting": {
        "label": "🪞 Reflecting",
        "color": "#607D8B",  # Calm gray-blue
        "icon": "🪞",
    },
    "break": {
        "label": "☕ Break",
        "color": "#1ABC9C",  # Relaxing teal
        "icon": "☕",
    },
    "sleep": {
        "label": "😴 Sleep",
        "color": "#34495E",  # Night dark blue
        "icon": "😴",
        "min_duration_warning": 360,  # 6 hours in minutes
        "warning_message": "⚠️ Sleep scheduled for less than 6 hours.",
        "warning_advice": "💡 Plan time to nap the next day, and aim for 8 hours again tomorrow.",
    },
    "custom": {
        "label": "✏️ Custom",
        "color": "#00FFFF",  # Cyan default
        "icon": "✏️",
        "has_custom_title": True,
    },
}

# --- Recurrence Types -----------------------------------------

RECURRENCE_TYPES = {
    "once": "Once (no repeat)",
    "daily": "Daily",
    "weekly": "Weekly",
    "biweekly": "Every 2 weeks",
    "monthly_date": "Monthly (same date)",
    "monthly_weekday": "Monthly (same weekday)",
    "bimonthly": "2x per month (1st & 15th)",
}

WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


# --- Event Model ---------------------------------------------

@dataclass
class Event:
    id: str
    title: str
    category_id: str
    start_utc: datetime               # tz-aware, always UTC
    duration_min: int
    color: str = "#00FFFF"
    reminders_min: List[int] = field(
        default_factory=lambda: DEFAULT_REMINDERS_MIN.copy()
    )

    # Recurrence settings
    recurrence: str = "once"  # once | daily | weekly | biweekly | monthly_date | monthly_weekday | bimonthly
    weekday: Optional[int] = None     # 0=Mon .. 6=Sun (for weekly/biweekly/monthly_weekday)
    month_day: Optional[int] = None   # 1-31 (for monthly_date)
    
    # Reference timezone (for display purposes)
    reference_tz: str = "UTC"
    
    # Event date range (optional - for limiting recurrence)
    start_date: Optional[datetime] = None  # First occurrence
    end_date: Optional[datetime] = None    # Last occurrence (None = forever)

    @property
    def end_utc(self) -> datetime:
        return self.start_utc + timedelta(minutes=self.duration_min)
    
    # Legacy support for _color attribute
    @property
    def _color(self) -> str:
        return self.color
    
    @_color.setter
    def _color(self, value: str):
        self.color = value
    
    @property
    def category(self) -> Dict:
        """Get category info"""
        return EVENT_CATEGORIES.get(self.category_id, EVENT_CATEGORIES["custom"])


# --- Factory --------------------------------------------------

def create_event(
    title: str,
    category_id: str,
    start_dt: datetime,           # tz-aware datetime in reference timezone
    duration_min: int,
    reference_tz: str,
    color: Optional[str] = None,
    recurrence: str = "once",
    reminders_min: Optional[List[int]] = None,
    end_date: Optional[datetime] = None,
) -> Event:
    """
    Create an Event from a timezone-aware datetime.
    The datetime should be in the reference timezone.
    Internally converted to UTC.
    """
    if start_dt.tzinfo is None:
        raise ValueError("start_dt must be timezone-aware")

    start_utc = start_dt.astimezone(ZoneInfo("UTC"))
    
    # Use category color if not specified
    if color is None:
        color = EVENT_CATEGORIES.get(category_id, {}).get("color", "#00FFFF")
    
    # Determine weekday and month_day from the start date
    weekday = start_dt.weekday()
    month_day = start_dt.day

    return Event(
        id=str(uuid.uuid4()),
        title=title,
        category_id=category_id,
        start_utc=start_utc,
        duration_min=duration_min,
        color=color,
        reminders_min=(
            reminders_min.copy()
            if reminders_min is not None
            else DEFAULT_REMINDERS_MIN.copy()
        ),
        recurrence=recurrence,
        weekday=weekday,
        month_day=month_day,
        reference_tz=reference_tz,
        start_date=start_utc,
        end_date=end_date.astimezone(ZoneInfo("UTC")) if end_date else None,
    )


# Legacy factory for backwards compatibility
def create_event_from_local(
    title: str,
    category_id: str,
    start_local: datetime,
    duration_min: int,
    recurrence: Optional[str] = None,
    weekday: Optional[int] = None,
    reminders_min: Optional[List[int]] = None
) -> Event:
    """Legacy factory - use create_event instead"""
    if start_local.tzinfo is None:
        raise ValueError("start_local must be timezone-aware")

    return create_event(
        title=title,
        category_id=category_id,
        start_dt=start_local,
        duration_min=duration_min,
        reference_tz=str(start_local.tzinfo),
        recurrence=recurrence or "once",
        reminders_min=reminders_min,
    )


# --- Recurrence Expansion ------------------------------------

def _get_nth_weekday_of_month(year: int, month: int, weekday: int, n: int) -> Optional[datetime]:
    """Get the nth occurrence of a weekday in a month (n=1 for first, n=-1 for last)"""
    if n > 0:
        # First day of month
        first_day = datetime(year, month, 1, tzinfo=ZoneInfo("UTC"))
        # Days until the target weekday
        days_until = (weekday - first_day.weekday()) % 7
        # First occurrence
        first_occurrence = first_day + timedelta(days=days_until)
        # Nth occurrence
        target = first_occurrence + timedelta(weeks=n-1)
        # Check if still in same month
        if target.month == month:
            return target
        return None
    else:
        # Last occurrence - start from next month and go back
        if month == 12:
            next_month = datetime(year + 1, 1, 1, tzinfo=ZoneInfo("UTC"))
        else:
            next_month = datetime(year, month + 1, 1, tzinfo=ZoneInfo("UTC"))
        last_day = next_month - timedelta(days=1)
        # Days back to target weekday
        days_back = (last_day.weekday() - weekday) % 7
        return last_day - timedelta(days=days_back)


def instantiate_for_day(
    event: Event,
    day_utc: datetime
) -> Optional[Event]:
    """
    Returns a concrete Event instance for the given UTC day,
    or None if the event does not occur on that day.
    """
    
    # Check date range if set
    if event.start_date:
        if day_utc.date() < event.start_date.date():
            return None
    
    if event.end_date:
        if day_utc.date() > event.end_date.date():
            return None

    # --- ONCE (no recurrence) ---
    if event.recurrence == "once" or event.recurrence is None:
        # Check if this is the day of the event
        if event.start_utc.date() == day_utc.date():
            return event
        return None

    # --- DAILY ---
    if event.recurrence == "daily":
        start = event.start_utc.replace(
            year=day_utc.year,
            month=day_utc.month,
            day=day_utc.day
        )
        return Event(**{**event.__dict__, "start_utc": start})

    # --- WEEKLY ---
    if event.recurrence == "weekly":
        if event.weekday is None:
            return None

        if day_utc.weekday() != event.weekday:
            return None

        start = event.start_utc.replace(
            year=day_utc.year,
            month=day_utc.month,
            day=day_utc.day
        )
        return Event(**{**event.__dict__, "start_utc": start})

    # --- BIWEEKLY (every 2 weeks) ---
    if event.recurrence == "biweekly":
        if event.weekday is None or event.start_date is None:
            return None
        
        if day_utc.weekday() != event.weekday:
            return None
        
        # Calculate weeks since start
        days_diff = (day_utc.date() - event.start_date.date()).days
        weeks_diff = days_diff // 7
        
        # Check if it's an even week (0, 2, 4, ...)
        if weeks_diff % 2 != 0:
            return None
        
        start = event.start_utc.replace(
            year=day_utc.year,
            month=day_utc.month,
            day=day_utc.day
        )
        return Event(**{**event.__dict__, "start_utc": start})

    # --- MONTHLY (same date) ---
    if event.recurrence == "monthly_date":
        if event.month_day is None:
            return None
        
        if day_utc.day != event.month_day:
            return None
        
        try:
            start = event.start_utc.replace(
                year=day_utc.year,
                month=day_utc.month,
                day=day_utc.day
            )
            return Event(**{**event.__dict__, "start_utc": start})
        except ValueError:
            # Day doesn't exist in this month (e.g., 31st in February)
            return None

    # --- MONTHLY (same weekday, e.g., "2nd Tuesday") ---
    if event.recurrence == "monthly_weekday":
        if event.weekday is None or event.start_date is None:
            return None
        
        if day_utc.weekday() != event.weekday:
            return None
        
        # Determine which occurrence of this weekday in the month
        # the original event was (1st, 2nd, 3rd, 4th, or last)
        original_day = event.start_date.day
        original_week = (original_day - 1) // 7 + 1  # 1-based week number
        
        # Check if this day is the same week occurrence
        day_week = (day_utc.day - 1) // 7 + 1
        
        if day_week != original_week:
            return None
        
        start = event.start_utc.replace(
            year=day_utc.year,
            month=day_utc.month,
            day=day_utc.day
        )
        return Event(**{**event.__dict__, "start_utc": start})

    # --- BIMONTHLY (1st and 15th) ---
    if event.recurrence == "bimonthly":
        if day_utc.day not in [1, 15]:
            return None
        
        start = event.start_utc.replace(
            year=day_utc.year,
            month=day_utc.month,
            day=day_utc.day
        )
        return Event(**{**event.__dict__, "start_utc": start})

    return None


# --- Helper Functions ----------------------------------------

def get_event_time_in_zone(event: Event, tz: ZoneInfo) -> tuple[str, str]:
    """Get start and end time strings for an event in a specific timezone"""
    start_local = event.start_utc.astimezone(tz)
    end_local = event.end_utc.astimezone(tz)
    return (
        start_local.strftime("%H:%M"),
        end_local.strftime("%H:%M")
    )


def format_recurrence(event: Event) -> str:
    """Get a human-readable recurrence description"""
    if event.recurrence == "once" or event.recurrence is None:
        return "Once"
    elif event.recurrence == "daily":
        return "Daily"
    elif event.recurrence == "weekly":
        day_name = WEEKDAY_NAMES[event.weekday] if event.weekday is not None else "?"
        return f"Weekly on {day_name}"
    elif event.recurrence == "biweekly":
        day_name = WEEKDAY_NAMES[event.weekday] if event.weekday is not None else "?"
        return f"Every 2 weeks on {day_name}"
    elif event.recurrence == "monthly_date":
        return f"Monthly on the {event.month_day}th"
    elif event.recurrence == "monthly_weekday":
        day_name = WEEKDAY_NAMES[event.weekday] if event.weekday is not None else "?"
        if event.start_date:
            week_num = (event.start_date.day - 1) // 7 + 1
            ordinal = ["1st", "2nd", "3rd", "4th", "5th"][week_num - 1] if week_num <= 5 else f"{week_num}th"
            return f"Monthly on the {ordinal} {day_name}"
        return f"Monthly on {day_name}"
    elif event.recurrence == "bimonthly":
        return "Twice monthly (1st & 15th)"
    return event.recurrence


def get_upcoming_reminders(event: Event, now_utc: datetime) -> List[Dict]:
    """Get list of upcoming reminders for an event"""
    reminders = []
    
    for minutes_before in event.reminders_min:
        reminder_time = event.start_utc - timedelta(minutes=minutes_before)
        
        if reminder_time > now_utc:
            reminders.append({
                "time": reminder_time,
                "minutes_before": minutes_before,
                "event": event,
            })
    
    return reminders
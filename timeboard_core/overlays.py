from dataclasses import dataclass
from datetime import time

@dataclass(frozen=True)
class TradingSession:
    name: str
    zone: str
    start: time
    end: time
    color: str

TRADING_SESSIONS = [
    TradingSession("Tokyo Session",  "Asia/Tokyo", time(0, 0),  time(9, 0),  "#DADADA"),
    TradingSession("London Session", "Europe/London", time(8, 0),  time(17, 0), "#CFCFCF"),
    TradingSession("NY Session",     "America/New_York", time(13, 0), time(22, 0), "#BFBFBF"),
]

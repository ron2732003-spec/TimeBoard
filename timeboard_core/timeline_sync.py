# timeboard_core/timeline_sync.py
"""
Exakte Slider-Positionen durch Messung der Stunden-Übergänge
"""

SLIDER_MIN = 0
SLIDER_MAX = 1439

def measure_hour_positions():
    """
    Misst die exakten Positionen, wo sich Stunden im Slider ändern.
    
    Für jede Stunde H finden wir die Minute, wo die Anzeige von H-1 zu H wechselt.
    Diese Minute entspricht exakt H*60.
    
    Die Position dieser Minute im Slider-Range ist dann die exakte Position.
    """
    positions = {}
    
    for hour in range(24):
        # Die Stunde wechselt exakt bei hour * 60 Minuten
        minute = hour * 60
        
        # Position im Slider: Diese Minute durch den gesamten Range
        # Der Slider geht von 0 bis 1439, also ist die Position:
        position_fraction = minute / SLIDER_MAX
        position_pct = position_fraction * 100
        
        positions[hour] = position_pct
    
    return positions


# Gemessene Positionen
HOUR_POSITIONS = measure_hour_positions()


def get_minute_position_pct(minute: int) -> float:
    """
    Berechnet Position einer Minute basierend auf dem Slider-Range.
    """
    return (minute / SLIDER_MAX) * 100


# Lass uns die tatsächlichen Werte ausgeben
def print_positions():
    print("Gemessene Stunden-Positionen:")
    print("-" * 40)
    for h in range(24):
        minute = h * 60
        pos = HOUR_POSITIONS[h]
        print(f"Stunde {h:2d} ({minute:4d} min): {pos:6.3f}%")
    print("-" * 40)
    print(f"Problem-Check:")
    print(f"Stunde  1:  {HOUR_POSITIONS[1]:.3f}%")
    print(f"Stunde 10: {HOUR_POSITIONS[10]:.3f}%")  
    print(f"Stunde 20: {HOUR_POSITIONS[20]:.3f}%")
    print(f"Stunde 23: {HOUR_POSITIONS[23]:.3f}%")
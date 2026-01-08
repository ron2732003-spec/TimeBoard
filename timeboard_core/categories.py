from dataclasses import dataclass
import uuid

@dataclass
class Category:
    id: str
    name: str
    color: str

def _id():
    return str(uuid.uuid4())

PRESET_CATEGORIES = {
    "Gym":        Category(_id(), "Gym",        "#2ECC71"),
    "Work":       Category(_id(), "Work",       "#3498DB"),
    "Training":   Category(_id(), "Training",   "#9B59B6"),
    "Service":    Category(_id(), "Service",    "#E67E22"),
    "Center":     Category(_id(), "Center",     "#1ABC9C"),
    "Sleep":      Category(_id(), "Sleep",      "#2C3E50"),
    "Evangelize": Category(_id(), "Evangelize", "#E74C3C"),
    "Basket":     Category(_id(), "Basket",     "#F1C40F"),
    "Meetings":   Category(_id(), "Meetings",   "#95A5A6"),
}

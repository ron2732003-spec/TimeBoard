# 📅 TimeBoard

A multi-timezone productivity and scheduling tool built with Streamlit.

## Features

- **Multi-Timezone Timeline**: View and compare times across multiple timezones simultaneously
- **Daylight Visualization**: Optional sunrise/sunset gradients to visualize waking hours
- **Event Scheduling**: Create events with a reference timezone - automatically synced across all displayed timezones
- **Preset Event Types**: Work, Gym, Bible Reading, Fellowship, Sleep, and more
- **Recurrence Options**: Once, Daily, Weekly, Bi-weekly, Monthly
- **Trading Sessions**: Optional overlay for London, New York, Tokyo market hours
- **Flexible Zoom**: Day, 3-Day, or Week view
- **Configurable Time Steps**: 1, 5, 15, or 30 minute increments

## Quick Start

### Option 1: Streamlit Cloud (Recommended)
Visit: [your-app-url.streamlit.app](https://your-app-url.streamlit.app)

### Option 2: Run Locally

```bash
# Clone the repository
git clone https://github.com/ron2732003-spec/TimeBoard.git
cd TimeBoard

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run timeboard_app/app.py
```

## Project Structure

```
TimeBoard/
├── timeboard_app/          # Streamlit UI components
│   ├── app.py              # Main application entry point
│   └── ui/
│       ├── active_time.py  # Time slider component
│       ├── event_form.py   # Event creation form
│       ├── settings_panel.py
│       └── timeline.py     # Main timeline visualization
├── timeboard_core/         # Core logic
│   ├── events.py           # Event model & recurrence
│   ├── settings.py         # User settings & timezone data
│   ├── overlays.py         # Trading sessions
│   └── ...
├── state/
│   └── session.py          # Session state management
├── requirements.txt
└── README.md
```


## License

MIT License

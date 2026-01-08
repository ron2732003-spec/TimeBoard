import subprocess
import sys
import os

def main():
    app_path = os.path.join(
        os.path.dirname(__file__),
        "timeboard_app",
        "app.py"
    )

    subprocess.run([
        sys.executable,
        "-m", "streamlit",
        "run",
        app_path,
        "--server.headless=true",
        "--browser.gatherUsageStats=false"
    ])

if __name__ == "__main__":
    main()

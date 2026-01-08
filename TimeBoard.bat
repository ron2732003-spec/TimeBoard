@echo off
cd /d %~dp0

echo 🚀 Starting TimeBoard...
streamlit run timeboard_app/app.py

pause

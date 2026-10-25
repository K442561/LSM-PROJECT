@echo off
title Mobility Recovery Engine Launcher
echo ========================================================
echo   Launching Mobility Recovery Engine Full-Stack App
echo ========================================================

echo [1/3] Checking and installing Python backend dependencies...
pip install -r backend\requirements.txt

echo [2/3] Checking and installing Node frontend dependencies...
cd frontend
call npm install
cd ..

echo [3/3] Starting Backend & Frontend Servers...
start "Mobility Recovery Backend" cmd /k "python backend\run.py"
cd frontend
call npm run dev -- --open

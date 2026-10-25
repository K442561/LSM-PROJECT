#!/bin/bash
echo "========================================================"
echo "  Launching Mobility Recovery Engine Full-Stack App"
echo "========================================================"

echo "[1/3] Installing Python backend dependencies..."
pip install -r backend/requirements.txt

echo "[2/3] Installing Node frontend dependencies..."
cd frontend && npm install && cd ..

echo "[3/3] Starting Backend & Frontend..."
python backend/run.py &
cd frontend && npm run dev -- --open

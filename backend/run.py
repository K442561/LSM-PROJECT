"""One-command runner for Mobility Recovery Engine Backend.

Usage:
    python backend/run.py
"""

import os
import sys
from pathlib import Path
import uvicorn

# Add backend directory to sys.path and PYTHONPATH for reloader subprocesses
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))
os.environ["PYTHONPATH"] = str(backend_dir) + os.pathsep + os.environ.get("PYTHONPATH", "")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting Mobility Recovery Engine Backend")
    print("   Local API Docs:   http://127.0.0.1:8000/docs")
    print("   Network API Docs: http://0.0.0.0:8000/docs")
    print("=" * 60)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

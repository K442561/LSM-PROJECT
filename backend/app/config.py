"""Configuration settings for Mobility Recovery Engine.

Loads environment variables from .env if present and provides
default weights, paths, and geographic constants.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directories
BACKEND_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BACKEND_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"

# Ensure data and cache directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Normalized SQLite database file path
DEFAULT_DB_FILE = (DATA_DIR / "mobility.db").resolve().as_posix()


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    APP_NAME: str = "Mobility Recovery Engine"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = f"sqlite:///{DEFAULT_DB_FILE}"

    # Reliability scoring weights:
    # Score = buffer - (w1 * variability) - (w2 * waiting_time) - (w3 * transfers)
    WEIGHT_VARIABILITY: float = 0.5  # w1: penalty per minute of standard deviation
    WEIGHT_WAITING: float = 0.3      # w2: penalty per minute of waiting time
    WEIGHT_TRANSFERS: float = 5.0    # w3: penalty per transfer

    # Monte Carlo simulation parameters
    MONTE_CARLO_RUNS: int = 1000

    # Road Network Graph Cache
    GRAPH_CACHE_FILE: str = str((CACHE_DIR / "vellore_tiruvannamalai_graph.graphml").resolve())
    TIMETABLES_FILE: str = str((DATA_DIR / "timetables.json").resolve())

    # Bounding Box for Vellore - Tiruvannamalai corridor
    BBOX_NORTH: float = 13.05
    BBOX_SOUTH: float = 12.15
    BBOX_EAST: float = 79.38
    BBOX_WEST: float = 78.95

    # Max speed for Haversine A* admissibility in km/h
    MAX_ROAD_SPEED_KMH: float = 80.0

    # Key Landmarks
    VIT_COORDS: tuple[float, float] = (12.9692, 79.1559)  # (lat, lon)
    TVM_COORDS: tuple[float, float] = (12.2253, 79.0747)  # (lat, lon)

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "*"
    ]


settings = Settings()

# Ensure database parent directory exists if overridden
if settings.DATABASE_URL.startswith("sqlite:///"):
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

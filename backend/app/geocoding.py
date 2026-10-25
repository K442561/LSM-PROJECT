"""Pan-India Geocoding Module for Mobility Recovery Engine.

Resolves place names, stations, colleges, and landmarks across India to GPS coordinates
using OpenStreetMap Nominatim with an extensive offline fallback dictionary of major
Indian cities, transit hubs, and universities.
"""

from __future__ import annotations
import logging
import re
from typing import Dict, List, Optional, Tuple
import requests

logger = logging.getLogger(__name__)

# User agent for Nominatim compliance
NOMINATIM_HEADERS = {
    "User-Agent": "MobilityRecoveryEngine/2.0 (OpenStreetMap routing educational tool)",
}

# Extensive offline dictionary of major Indian cities, hubs, and universities
OFFLINE_INDIAN_LOCATIONS: Dict[str, Tuple[float, float, str]] = {
    # Tamil Nadu & Corridors
    "vit katpadi": (12.9692, 79.1559, "VIT Katpadi Main Gate, Vellore, Tamil Nadu"),
    "vit vellore": (12.9692, 79.1559, "Vellore Institute of Technology, Katpadi, Tamil Nadu"),
    "katpadi": (12.9710, 79.1384, "Katpadi Junction Railway Station, Vellore, Tamil Nadu"),
    "vellore": (12.9165, 79.1325, "Vellore Fort / City Center, Tamil Nadu"),
    "vellore new bus stand": (12.9264, 79.1352, "New Bus Stand, Vellore, Tamil Nadu"),
    "vellore old bus stand": (12.9180, 79.1330, "Old Bus Stand, Vellore, Tamil Nadu"),
    "tiruvannamalai": (12.2253, 79.0747, "Tiruvannamalai Annamalaiyar Temple, Tamil Nadu"),
    "tiruvannamalai bus stand": (12.2280, 79.0680, "Central Bus Stand, Tiruvannamalai, Tamil Nadu"),
    "arani": (12.6687, 79.2839, "Arani Bus Stand, Tiruvannamalai District, Tamil Nadu"),
    "polur": (12.5057, 79.1242, "Polur Town, Tiruvannamalai District, Tamil Nadu"),
    "chennai": (13.0827, 80.2707, "Chennai Central, Tamil Nadu"),
    "chennai central": (13.0827, 80.2754, "Puratchi Thalaivar Dr. M.G.R. Central Railway Station, Chennai"),
    "chennai airport": (12.9941, 80.1709, "Chennai International Airport, Meenambakkam, Tamil Nadu"),
    "tambaram": (12.9249, 80.1000, "Tambaram Railway Station, Chennai, Tamil Nadu"),
    "vit chennai": (12.8406, 80.1534, "VIT Chennai Campus, Vandalur-Kelambakkam Rd, Tamil Nadu"),
    "kanchipuram": (12.8342, 79.7036, "Kanchipuram Temple Town, Tamil Nadu"),
    "coimbatore": (11.0168, 76.9558, "Coimbatore Junction / Gandhipuram, Tamil Nadu"),
    "madurai": (9.9252, 78.1198, "Madurai Meenakshi Temple, Tamil Nadu"),
    "salem": (11.6643, 78.1460, "Salem Junction, Tamil Nadu"),
    "trichy": (10.7905, 78.7047, "Tiruchirappalli Junction, Tamil Nadu"),
    "tiruchirappalli": (10.7905, 78.7047, "Tiruchirappalli Junction, Tamil Nadu"),
    "tirupati": (13.6288, 79.4192, "Tirupati Temple City, Andhra Pradesh"),
    "pondicherry": (11.9416, 79.8083, "Puducherry White Town / Beach, Puducherry"),
    "puducherry": (11.9416, 79.8083, "Puducherry White Town / Beach, Puducherry"),

    # Karnataka
    "bengaluru": (12.9716, 77.5946, "Bengaluru Majestic, Karnataka"),
    "bangalore": (12.9716, 77.5946, "Bengaluru Majestic, Karnataka"),
    "bengaluru airport": (13.1986, 77.7066, "Kempegowda International Airport, Bengaluru, Karnataka"),
    "whitefield": (12.9698, 77.7500, "Whitefield, Bengaluru, Karnataka"),
    "electronic city": (12.8452, 77.6602, "Electronic City, Bengaluru, Karnataka"),
    "mysuru": (12.2958, 76.6394, "Mysuru Palace / City, Karnataka"),
    "mysore": (12.2958, 76.6394, "Mysuru Palace / City, Karnataka"),
    "mangaluru": (12.9141, 74.8560, "Mangaluru Central, Karnataka"),
    "mangalore": (12.9141, 74.8560, "Mangaluru Central, Karnataka"),
    "hubballi": (15.3647, 75.1240, "Hubballi Junction, Karnataka"),

    # Maharashtra & West
    "mumbai": (19.0760, 72.8777, "Chhatrapati Shivaji Maharaj Terminus, Mumbai, Maharashtra"),
    "pune": (18.5204, 73.8567, "Pune Railway Station, Maharashtra"),
    "hinjawadi": (18.5913, 73.7389, "Hinjawadi IT Park, Pune, Maharashtra"),
    "nagpur": (21.1458, 79.0882, "Nagpur Zero Mile, Maharashtra"),
    "nashik": (19.9975, 73.7898, "Nashik City, Maharashtra"),
    "ahmedabad": (23.0225, 72.5714, "Ahmedabad Kalupur Station, Gujarat"),
    "surat": (21.1702, 72.8311, "Surat Textile City, Gujarat"),
    "vadodara": (22.3072, 73.1812, "Vadodara Central, Gujarat"),
    "goa": (15.4909, 73.8278, "Panaji / North Goa, Goa"),
    "panaji": (15.4909, 73.8278, "Panaji, Goa"),

    # Delhi NCR & North
    "delhi": (28.6139, 77.2090, "New Delhi Railway Station / Connaught Place, Delhi"),
    "new delhi": (28.6139, 77.2090, "New Delhi Railway Station, Delhi"),
    "gurugram": (28.4595, 77.0266, "Cyber City, Gurugram, Haryana"),
    "gurgaon": (28.4595, 77.0266, "Cyber City, Gurugram, Haryana"),
    "noida": (28.5355, 77.3910, "Sector 18 / Center, Noida, Uttar Pradesh"),
    "agra": (27.1767, 78.0081, "Taj Mahal / Agra Cantt, Uttar Pradesh"),
    "jaipur": (26.9124, 75.7873, "Jaipur Pink City, Rajasthan"),
    "chandigarh": (30.7333, 76.7794, "Sector 17, Chandigarh"),
    "lucknow": (26.8467, 80.9462, "Charbagh Station, Lucknow, Uttar Pradesh"),
    "varanasi": (25.3176, 82.9739, "Kashi Vishwanath / Cantt, Varanasi, Uttar Pradesh"),
    "amritsar": (31.6340, 74.8723, "Golden Temple / City, Amritsar, Punjab"),

    # East & Central
    "hyderabad": (17.3850, 78.4867, "Secunderabad / Charminar, Hyderabad, Telangana"),
    "kolkata": (22.5726, 88.3639, "Howrah Station / Esplanade, Kolkata, West Bengal"),
    "bhubaneswar": (20.2961, 85.8245, "Bhubaneswar Smart City, Odisha"),
    "patna": (25.5941, 85.1376, "Patna Junction, Bihar"),
    "indore": (22.7196, 75.8577, "Indore Rajwada, Madhya Pradesh"),
    "bhopal": (23.2599, 77.4126, "Bhopal Junction, Madhya Pradesh"),
    "kochi": (9.9312, 76.2673, "Kochi Marine Drive / Ernakulam, Kerala"),
    "ernakulam": (9.9816, 76.2999, "Ernakulam South Station, Kerala"),
    "thiruvananthapuram": (8.5241, 76.9366, "Trivandrum Central, Kerala"),
}


def normalize_query(query: str) -> str:
    """Normalize text for consistent lookup."""
    q = query.lower().strip()
    q = re.sub(r"[^\w\s]", "", q)
    return " ".join(q.split())


def match_offline_database(query: str) -> Optional[Tuple[float, float, str]]:
    """Check if query matches a known landmark in the offline Indian database."""
    normalized = normalize_query(query)

    # Exact match
    if normalized in OFFLINE_INDIAN_LOCATIONS:
        return OFFLINE_INDIAN_LOCATIONS[normalized]

    # Partial / substring match
    for key, (lat, lon, desc) in OFFLINE_INDIAN_LOCATIONS.items():
        if key in normalized or normalized in key:
            return lat, lon, desc

    return None


def geocode_location(query: str) -> Tuple[float, float, str]:
    """Resolve any location query across India to (lat, lon, display_name).

    1. Checks offline dictionary for instant response.
    2. Queries OpenStreetMap Nominatim API for comprehensive Pan-India coverage.
    3. Gracefully falls back to offline match if network is slow/offline.
    """
    if not query or not query.strip():
        # Default to VIT Katpadi
        return 12.9692, 79.1559, "VIT Katpadi Main Gate, Vellore, Tamil Nadu"

    # Quick check for offline dictionary first to optimize latency
    offline_match = match_offline_database(query)

    # If internet is active, query OpenStreetMap Nominatim for precise user address
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": query.strip(),
            "format": "json",
            "countrycodes": "in",
            "limit": 1,
            "addressdetails": 1,
        }
        resp = requests.get(url, params=params, headers=NOMINATIM_HEADERS, timeout=3)
        if resp.status_code == 200:
            results = resp.json()
            if results and len(results) > 0:
                item = results[0]
                lat = float(item["lat"])
                lon = float(item["lon"])
                display_name = item.get("display_name", query)
                return lat, lon, display_name
    except Exception as e:
        logger.info(f"Nominatim online geocoding lookup bypassed ({e}).")

    if offline_match:
        return offline_match

    # Final fallback: default to Vellore/VIT
    return 12.9692, 79.1559, f"{query.title()} (Estimated coordinates)"


def reverse_geocode(lat: float, lon: float) -> str:
    """Convert (lat, lon) into a human-readable Indian location name."""
    # Find nearest known landmark in offline DB
    best_name = f"Point ({lat:.4f}, {lon:.4f})"
    min_dist = float("inf")

    for key, (k_lat, k_lon, desc) in OFFLINE_INDIAN_LOCATIONS.items():
        # Quick Euclidean approximation for nearest point
        dist_sq = (lat - k_lat) ** 2 + (lon - k_lon) ** 2
        if dist_sq < min_dist:
            min_dist = dist_sq
            best_name = desc

    return best_name

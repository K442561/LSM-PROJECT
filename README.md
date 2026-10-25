# Mobility Recovery Engine 🚀

A full-stack, mobile-first web application designed for students and working professionals facing strict deadlines and traffic uncertainty across **all of India**, with specialized local corridor modeling for **Vellore – Tiruvannamalai** (Tamil Nadu).

Instead of only calculating the shortest distance or static GPS ETA, this engine calculates the **probability of arriving before your deadline**, determines the **Latest Safe Departure (LSD)** time with a live countdown timer, recommends a **recovery plan** if you miss a bus or connection, locks your chosen route with touch confirmation so accidental taps never reroute you, and includes a **learning loop** that calibrates route estimates using real trip logs.

---

## 🇮🇳 Pan-India Features & Capabilities

- **Any Origin & Destination in India**: Type any Indian city, town, landmark, railway station, or street (e.g. *Chennai Central* to *Bengaluru*, *Mumbai* to *Pune*, *Delhi* to *Agra*, *Kolkata* to *Durgapur*). Powered by OpenStreetMap Nominatim with an instant offline fallback database.
- **📍 Interactive Map Pin Picking**: Click "📍 Pick on Map" to place origin or destination pins directly anywhere across the map of India.
- **⚡ Transportation Mode Selection**:
  - 🚗 **Driving / Cab**: Highway speed modeling with traffic variability.
  - 🚌 **Bus Transit**: Intercity & regional bus routing with realistic boarding and stop delays.
  - 🚆 **Train / Rail**: Indian Railways express and passenger routing speeds.
  - ⚡ **All Modes**: Compare all available transit and road options side-by-side.
- **Shortest + Alternative Routes**: Automatically generates the optimal shortest route and up to 3 distinct alternatives with zero API keys using OSRM and A* graph algorithms.
- **Deadline-Aware Monte Carlo Engine**: 1,000-run simulation calculates On-Time Probability (OTP %), safety buffers, and Latest Safe Departure countdown for every route.

---

## ⚡ Quick Start (One Command Each)

### 1. Start Backend (Terminal 1)
```bash
# From project root
python backend/run.py
```
> Backend runs at: **http://127.0.0.1:8000**  
> Interactive API Docs: **http://127.0.0.1:8000/docs**

### 2. Start Frontend (Terminal 2)
```bash
# Navigate to frontend and start Vite dev server
cd frontend
npm run dev
```
> Frontend runs at: **http://localhost:5173**

---

## 🧭 How to Test & Use the App

1. **Open the App**: Visit [http://localhost:5173](http://localhost:5173) in your browser.
2. **Enter Source & Destination**:
   - Type your origin and destination (e.g. `Chennai Central` to `Bengaluru`, `Mumbai` to `Pune`).
   - Or click **📍 Pick on Map** and click directly on the interactive Leaflet map to set your location coordinates!
   - Select your mode of transportation (⚡ All Modes, 🚗 Driving/Cab, 🚌 Bus, 🚆 Train).
3. **Explore Pre-Loaded Pan-India Scenarios**:
   - Use the quick chips: *Chennai → Bengaluru*, *Mumbai → Pune*, *Delhi → Agra*, *VIT → Tiruvannamalai*.
   - Adjust your departure and target deadline, then click **"Find Reliable Routes"**.
4. **Inspect the Map & Cards**:
   - The Leaflet map automatically centers and fits all routes across India with multi-colored polylines (royal blue, emerald green, amber orange).
   - Click on any route card or polyline to inspect travel time, waiting time, number of transfers, safety buffer, and **On-Time Probability (OTP %)**.
   - The top recommended route is highlighted with a one-line reason (e.g., *"Recommended: Highest reliability (97% OTP) with 34m buffer"*).
5. **Observe the Recovery Banner & Live Countdown**:
   - The banner dynamically displays:
     - 🟢 **You can make it**: Shows your Latest Safe Departure (LSD) and a live countdown timer.
     - 🟡 **Risky**: Recommends an alternative route to avoid congestion.
     - 🔴 **Cannot reach on time**: Indicates how many minutes late the earliest option will arrive.
   - If a bus or train is missed, an immediate recovery contingency plan appears.
6. **Test Route Lock (Touch Protection)**:
   - Click **"Confirm & Lock Route"** on any route card.
   - A confirmation dialog appears. Click **"Confirm & Lock"**.
   - Your route is now locked. Notice that accidental clicks or attempts to re-plan prompt an unlock confirmation dialog.
7. **Test Offline / Weak-Internet Mode**:
   - Open DevTools (`F12`), go to the **Network** tab, and toggle **Offline**.
   - Refresh the page or click around: the app immediately loads the cached plan with the label **"Offline Mode Active: Using saved route plan"**.
8. **Test the Learning Loop & History Page**:
   - Click the **"History & Logs"** tab in the header.
   - View the **Predicted vs Actual** duration comparison chart.
   - Fill out the **"Log Completed Trip"** form (e.g., Route 1 took 125 mins due to market traffic).
   - Click **"Submit Trip Log & Calibrate Engine"**.
   - The database instantly records the log and recalibrates the route's average duration and variability for future simulations!

---

## 🧪 Running the Automated Test Suite

Run the full pytest suite from the project root:
```bash
$env:PYTHONPATH="backend"
python -m pytest backend/tests/ -v
```
All **28 tests** across pathfinding, transit schedules, Monte Carlo simulation, recovery logic, and REST APIs will execute:
```
backend/tests/test_api.py::test_health_endpoint PASSED
backend/tests/test_api.py::test_plan_trip_endpoint_success PASSED
backend/tests/test_api.py::test_plan_trip_invalid_time_format PASSED
backend/tests/test_api.py::test_route_lock_and_unlock_flow PASSED
backend/tests/test_api.py::test_trip_logging_and_history_learning_loop PASSED
backend/tests/test_recovery.py::test_compute_latest_safe_departure PASSED
backend/tests/test_recovery.py::test_recovery_status_can_make_it PASSED
backend/tests/test_recovery.py::test_recovery_status_risky PASSED
backend/tests/test_recovery.py::test_recovery_status_cannot PASSED
backend/tests/test_recovery.py::test_attach_recommendation_reasons PASSED
backend/tests/test_reliability.py::test_monte_carlo_generous_deadline PASSED
backend/tests/test_reliability.py::test_monte_carlo_tight_deadline PASSED
backend/tests/test_reliability.py::test_monte_carlo_near_mean_deadline PASSED
backend/tests/test_reliability.py::test_reliability_scoring_formula PASSED
backend/tests/test_reliability.py::test_evaluate_route_reliability_integration PASSED
backend/tests/test_routing.py::test_database_models_initialization PASSED
backend/tests/test_routing.py::test_haversine_distance_between_vit_and_tiruvannamalai PASSED
backend/tests/test_routing.py::test_haversine_heuristic_admissibility PASSED
backend/tests/test_routing.py::test_a_star_search_finds_path PASSED
backend/tests/test_routing.py::test_a_star_same_source_and_target PASSED
backend/tests/test_routing.py::test_alternative_routes_penalty_method_and_overlap_filter PASSED
backend/tests/test_routing.py::test_nearest_node_lookup PASSED
backend/tests/test_transit.py::test_time_conversions PASSED
backend/tests/test_transit.py::test_timetables_json_loads_correctly PASSED
backend/tests/test_transit.py::test_find_next_departure PASSED
backend/tests/test_transit.py::test_transit_search_morning_query PASSED
backend/tests/test_transit.py::test_transit_search_late_night_returns_data_not_available PASSED
backend/tests/test_transit.py::test_missing_timetable_file_returns_data_not_available PASSED
============================== 28 passed in 2.5s ==============================
```

---

## 💡 How the Code Works (Plain Language Explanation)

### 1. Road Routing & Haversine A* (`backend/app/routing.py`)
- **Road Graph**: Downloads the regional road network around Vellore and Tiruvannamalai using **OSMnx** and caches it to disk (`vellore_tiruvannamalai_graph.graphml`). On later runs, it loads instantly from disk with zero external API calls.
- **A* Search**: Finds the quickest path using the **Haversine Distance Formula** divided by the maximum road speed ($80\text{ km/h}$). Because straight-line distance is always shorter than or equal to actual road paths, this heuristic never overestimates travel time (making it mathematically optimal).
- **Penalty Method for Alternatives**: To find alternative routes, it raises the "cost" of road edges used in earlier routes and runs A* again. Any candidate path that shares more than **80%** of its route with an earlier path is rejected, ensuring commuters receive genuinely distinct options.

### 2. Time-Dependent Transit Module (`backend/app/transit.py`)
- Reads bus and train timetables from `timetables.json`.
- When a user asks to leave at e.g. 08:15 AM, it calculates the next bus or train departure, the exact waiting time, and accounts for transfer buffers between multi-leg connections (e.g. VIT $\to$ New Bus Stand $\to$ Tiruvannamalai).
- If a route does not operate at that hour, it returns **`"data not available"`**. It **never invents timings**.

### 3. Reliability & 1,000-Run Monte Carlo Simulation (`backend/app/reliability.py`)
- Rather than assuming traffic is always predictable, every route segment has an expected duration and a delay spread (variability).
- The engine simulates **1,000 trips** per route with randomized traffic delays drawn from statistical distributions.
- It calculates:
  - **On-Time Probability (OTP)**: The exact percentage of the 1,000 runs that arrived before the deadline.
  - **90th Percentile Arrival Time ($P_{90}$)**: The arrival time under bad traffic conditions (90% worst-case).
  - **Reliability Score**:
    $$\text{Score} = \text{Buffer} - (w_1 \times \text{variability}) - (w_2 \times \text{waiting time}) - (w_3 \times \text{transfers})$$
    Weights can be customized in `backend/app/config.py` or `.env`.

### 4. Recovery & Latest Safe Departure (`backend/app/recovery.py`)
- **Latest Safe Departure (LSD)** is calculated as:
  $$\text{LSD} = \text{Deadline} - P_{90}\text{ Duration}$$
  Leaving before this time gives $\ge 90\%$ statistical confidence of arriving before your deadline.
- Status is classified as:
  - `can_make_it`: OTP $\ge 85\%$
  - `risky`: $50\% \le \text{OTP} < 85\%$
  - `cannot`: OTP $< 50\%$
- Includes **Missed Transit Contingency**: If the user misses the primary bus, it immediately suggests the backup option (e.g., take the Arani bypass or next scheduled bus).

### 5. Learning Loop (`backend/app/learning.py`)
- When a commuter completes a trip, they log their actual departure and arrival times.
- The engine computes the delay and uses running statistical updates (Welford's algorithm) to update the average travel time and variability in SQLite.
- Sample data defaults are automatically replaced with real, recorded road metrics over time.

### 6. Mobile-First Frontend & Offline PWA (`frontend/`)
- Built with **React** and **Vite** with **zero paid APIs** (uses OpenStreetMap tiles with Leaflet).
- **Large Tactile Buttons** ($\ge 48\text{px}$) designed for one-handed thumb use while walking or commuting.
- **Route Lock Dialog**: A modal confirmation guards against accidental taps on a crowded bus.
- **PWA Service Worker & Local Storage**: Caches the last planned route and locked route so the entire app works seamlessly even with weak or disconnected internet.

---

## 📊 Sample Corridor Data

**Vellore to Tiruvannamalai Corridor (~50–60 km):**
1. **Route 1: Bus via New Bus Stand**:
   - VIT Katpadi $\to$ Vellore New Bus Stand $\to$ Polur $\to$ Tiruvannamalai.
   - Travel time: ~2 hours. Moderate variability due to city traffic.
2. **Route 2: Bus via VIT 11 Gate & Arani**:
   - VIT Gate 11 $\to$ Arani Bypass $\to$ Santhavasal $\to$ Tiruvannamalai.
   - Travel time: ~1 hour 45 minutes maximum. Lower variability (bypasses city traffic).
3. **Route 3: Train (Katpadi Jn to Tiruvannamalai)**:
   - Infrequent daily passenger services. High delay spread, lower reliability.

*(Clearly labelled in `timetables.json` as sample data, calibrated dynamically when users submit real logs).*

---

## 🛠️ Tech Stack & Requirements

- **Backend**: Python 3.10+, FastAPI, SQLite (SQLAlchemy), NetworkX, OSMnx, NumPy, Pytest.
- **Frontend**: React 18, Vite, Leaflet, Lucide React, Plain CSS (Mobile-First), Service Worker (PWA).
- **Environment**: Fully local, 100% free open-source software, no credit cards or paid API keys required.

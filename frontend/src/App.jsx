import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import OfflineBadge from './components/OfflineBadge';
import InputForm from './components/InputForm';
import SideBySideRouteMaps from './components/SideBySideRouteMaps';
import RouteLockModal from './components/RouteLockModal';
import HistoryChart from './components/HistoryChart';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import ActiveTripCockpit from './components/ActiveTripCockpit';
import { api } from './services/api';
import { ShieldCheck, Unlock, AlertCircle } from 'lucide-react';

export default function App() {
  // Step/Tab navigation: 'input' -> 'routes' -> 'analytics' -> 'cockpit' -> 'history'
  const [activeTab, setActiveTab] = useState('input');
  const [planData, setPlanData] = useState(null);
  const [selectedRouteId, setSelectedRouteId] = useState(null);
  const [lockedRoute, setLockedRoute] = useState(null);
  const [isOfflineData, setIsOfflineData] = useState(false);
  const [savedAt, setSavedAt] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  // Interactive Map Pin Picking
  const [pickingTarget, setPickingTarget] = useState(null); // 'source' | 'destination' | null
  const [sourceInput, setSourceInput] = useState('VIT Katpadi');
  const [destInput, setDestInput] = useState('Tiruvannamalai');
  const [sourceCoords, setSourceCoords] = useState(null);
  const [destCoords, setDestCoords] = useState(null);

  // Lock Confirmation Modal state
  const [modalConfig, setModalConfig] = useState({
    isOpen: false,
    type: 'lock',
    targetRoute: null,
  });

  // Initial load: check for active lock and pre-fetch initial route plan
  useEffect(() => {
    async function init() {
      try {
        const lockRes = await api.getLockedRoute();
        if (lockRes.data && lockRes.data.is_active) {
          setLockedRoute(lockRes.data);
          setSelectedRouteId(lockRes.data.route_id);
          setActiveTab('cockpit'); // Resume active cockpit if route is locked
        }

        // Fetch initial plan silently (VIT Katpadi -> Tiruvannamalai)
        await handleFetchPlan(
          {
            source: 'VIT Katpadi',
            destination: 'Tiruvannamalai',
            current_time: '08:15',
            deadline: '10:30',
            mode: 'all',
          },
          false // do not force auto-tab jump on initial mount
        );
      } catch (err) {
        console.warn('Initial plan load error:', err);
      }
    }
    init();
  }, []);

  const handleFetchPlan = async (params, jumpToNextSlide = true) => {
    setIsLoading(true);
    setErrorMessage('');
    try {
      const payload = {
        ...params,
        source_coords: sourceCoords,
        dest_coords: destCoords,
      };

      const res = await api.planTrip(payload);
      setPlanData(res.data);
      setIsOfflineData(res.isOfflineData);
      setSavedAt(res.savedAt || null);

      if (res.data?.source_display) setSourceInput(res.data.source);
      if (res.data?.destination_display) setDestInput(res.data.destination);

      if (res.data?.routes?.length > 0) {
        const best = res.data.routes.find((r) => r.is_best) || res.data.routes[0];
        setSelectedRouteId(best.route_id);
      }

      // Automatically transition to Slide 2 (Side-by-Side Alternative Routes & Maps)
      if (jumpToNextSlide) {
        setActiveTab('routes');
      }
    } catch (err) {
      setErrorMessage(err.message || 'Error calculating routes.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTogglePicking = (target) => {
    setPickingTarget((prev) => (prev === target ? null : target));
  };

  const handleMapClick = (lat, lon, target) => {
    if (target === 'source') {
      setSourceCoords({ lat, lon });
      setSourceInput(`Pinned Location (${lat.toFixed(3)}, ${lon.toFixed(3)})`);
      setPickingTarget(null);
    } else if (target === 'destination') {
      setDestCoords({ lat, lon });
      setDestInput(`Pinned Location (${lat.toFixed(3)}, ${lon.toFixed(3)})`);
      setPickingTarget(null);
    }
  };

  // Lock workflow handlers
  const handleRequestLock = (route) => {
    setModalConfig({
      isOpen: true,
      type: 'lock',
      targetRoute: route,
    });
  };

  const handleRequestUnlock = () => {
    setModalConfig({
      isOpen: true,
      type: 'unlock',
      targetRoute: lockedRoute,
    });
  };

  const handleConfirmModal = async () => {
    if (modalConfig.type === 'lock' && modalConfig.targetRoute && planData) {
      try {
        const route = modalConfig.targetRoute;
        const lockPayload = {
          route_id: route.route_id,
          source: planData.source,
          destination: planData.destination,
          current_time: planData.current_time,
          deadline: planData.deadline,
          expected_arrival: route.expected_arrival,
          on_time_probability: route.on_time_probability,
          latest_safe_departure: planData.recovery?.latest_safe_departure || route.expected_departure,
          status: planData.recovery?.status || 'can_make_it',
          recovery_message: planData.recovery?.message || '',
          route_data: route,
        };

        const res = await api.lockRoute(lockPayload);
        setLockedRoute(res.data);
        setActiveTab('cockpit'); // Switch to active trip cockpit once locked
      } catch (e) {
        alert(`Failed to lock route: ${e.message}`);
      }
    } else if (modalConfig.type === 'unlock') {
      await api.unlockRoute();
      setLockedRoute(null);
    }

    setModalConfig({ isOpen: false, type: 'lock', targetRoute: null });
  };

  const handleCancelModal = () => {
    setModalConfig({ isOpen: false, type: 'lock', targetRoute: null });
  };

  return (
    <>
      <Navbar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        isLocked={Boolean(lockedRoute?.is_active)}
      />

      <main className="main-container">
        {/* Offline Badge */}
        {isOfflineData && <OfflineBadge savedAt={savedAt} />}

        {/* Active Route Locked Protection Notice */}
        {lockedRoute?.is_active && (
          <div className="locked-indicator-banner">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ShieldCheck size={20} />
              <span>
                Active Route Locked: <strong>{lockedRoute.route_name || lockedRoute.route_id}</strong>
              </span>
            </div>
            <button
              type="button"
              className="btn btn-secondary"
              style={{ minHeight: '34px', padding: '4px 10px', fontSize: '0.8rem' }}
              onClick={handleRequestUnlock}
            >
              <Unlock size={14} />
              <span>Unlock</span>
            </button>
          </div>
        )}

        {/* Error Alert */}
        {errorMessage && (
          <div
            style={{
              backgroundColor: 'var(--color-danger-bg)',
              border: '1px solid var(--color-danger)',
              color: '#fca5a5',
              padding: '12px 16px',
              borderRadius: 'var(--radius-sm)',
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              fontSize: '0.9rem',
            }}
          >
            <AlertCircle size={20} />
            <span>{errorMessage}</span>
          </div>
        )}

        {/* TAB 1: TRIP INPUT (MANUAL DATA ENTRY & MAP PINNING) */}
        {activeTab === 'input' && (
          <InputForm
            onSubmit={(params) => handleFetchPlan(params, true)}
            isLoading={isLoading}
            isLocked={Boolean(lockedRoute?.is_active)}
            onRequestUnlock={handleRequestUnlock}
            pickingTarget={pickingTarget}
            onTogglePicking={handleTogglePicking}
            onMapClick={handleMapClick}
            sourceVal={sourceInput}
            destVal={destInput}
          />
        )}

        {/* TAB 2: ROUTES & MAPS (NEXT SLIDE: 3+ ALTERNATIVES SIDE-BY-SIDE) */}
        {(activeTab === 'routes' || activeTab === 'planner') && (
          <SideBySideRouteMaps
            planData={planData}
            selectedRouteId={selectedRouteId}
            onSelectRoute={setSelectedRouteId}
            lockedRoute={lockedRoute}
            onRequestLock={handleRequestLock}
            onEditInput={() => setActiveTab('input')}
            onViewGraphs={() => setActiveTab('analytics')}
          />
        )}

        {/* TAB 3: RELIABILITY & GRAPHS */}
        {activeTab === 'analytics' && (
          <AnalyticsDashboard
            planData={planData}
            selectedRouteId={selectedRouteId}
            onSelectRoute={setSelectedRouteId}
          />
        )}

        {/* TAB 4: ACTIVE TRIP MONITOR (COCKPIT) */}
        {activeTab === 'cockpit' && (
          <ActiveTripCockpit
            lockedRoute={lockedRoute}
            planData={planData}
            onRequestUnlock={handleRequestUnlock}
            onSwitchToPlanner={() => setActiveTab('routes')}
          />
        )}

        {/* TAB 5: HISTORY & LOGS */}
        {activeTab === 'history' && <HistoryChart />}
      </main>

      {/* Confirmation Modal to Guard Against Accidental Screen Touches */}
      <RouteLockModal
        isOpen={modalConfig.isOpen}
        type={modalConfig.type}
        targetRoute={modalConfig.targetRoute}
        onConfirm={handleConfirmModal}
        onCancel={handleCancelModal}
      />
    </>
  );
}

import React, { useState, useEffect } from 'react';
import { 
  Navigation, 
  Wifi, 
  WifiOff, 
  History, 
  Compass, 
  BarChart3, 
  ShieldCheck, 
  Edit3, 
  Map
} from 'lucide-react';

export default function Navbar({ activeTab, onTabChange, isLocked, routeCount = 0 }) {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return (
    <header className="app-header">
      <div 
        className="brand-title" 
        onClick={() => onTabChange('input')} 
        style={{ cursor: 'pointer' }}
        title="Mobility Recovery Engine - Home"
      >
        <div className="brand-icon-wrapper">
          <Navigation className="brand-icon" size={20} />
        </div>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ fontWeight: 800, letterSpacing: '-0.3px' }}>Mobility Recovery</span>
            <span className="version-pill">Pan-India</span>
          </div>
          <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)', letterSpacing: '0.2px' }}>
            Reliability & Recovery Engine
          </span>
        </div>
      </div>

      <nav className="nav-links">
        {/* Tab 1: Trip Input */}
        <button
          className={`nav-btn ${activeTab === 'input' ? 'active' : ''}`}
          onClick={() => onTabChange('input')}
          title="Slide 1: Enter trip parameters & location data manually or via map"
        >
          <Edit3 size={16} />
          <span>1. Trip Input</span>
        </button>

        {/* Tab 2: Routes & Maps (Side-by-Side) */}
        <button
          className={`nav-btn ${activeTab === 'routes' || activeTab === 'planner' ? 'active' : ''}`}
          onClick={() => onTabChange('routes')}
          title="Slide 2: View 3+ alternative routes with individual maps side-by-side"
        >
          <Map size={16} />
          <span>2. Routes & Maps</span>
          <span className="nav-badge-pulse">Side-by-Side</span>
        </button>

        {/* Tab 3: Reliability & Graphs */}
        <button
          className={`nav-btn ${activeTab === 'analytics' ? 'active' : ''}`}
          onClick={() => onTabChange('analytics')}
          title="Slide 3: Monte Carlo probability density bell curves & comparative analytics"
        >
          <BarChart3 size={16} />
          <span>3. Reliability & Graphs</span>
        </button>

        {/* Tab 4: Active Trip Monitor */}
        <button
          className={`nav-btn ${activeTab === 'cockpit' ? 'active' : ''}`}
          onClick={() => onTabChange('cockpit')}
          title="Slide 4: Active trip monitor cockpit with live countdown"
        >
          <ShieldCheck size={16} />
          <span>4. Trip Monitor</span>
          {isLocked && <span className="active-lock-dot" title="Active Route Locked" />}
        </button>

        {/* Tab 5: History & Logs */}
        <button
          className={`nav-btn ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => onTabChange('history')}
          title="Slide 5: Historical travel logs & Bayesian learning loop"
        >
          <History size={16} />
          <span>5. History & Logs</span>
        </button>

        {/* Network Online/Offline Tag */}
        <div className="network-status-indicator">
          {isOnline ? (
            <span className="online-tag" title="Online: Live OSM & OSRM Routing Active">
              <span className="pulse-green-dot" />
              <Wifi size={14} />
              <span className="network-label">Live</span>
            </span>
          ) : (
            <span className="offline-tag" title="Offline: Cached PWA Mode Active">
              <WifiOff size={14} />
              <span className="network-label">Offline</span>
            </span>
          )}
        </div>
      </nav>
    </header>
  );
}

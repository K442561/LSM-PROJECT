import React, { useState, useEffect, useRef } from 'react';
import L from 'leaflet';
import { 
  Car, 
  Bus, 
  Train, 
  ShieldCheck, 
  Clock, 
  MapPin, 
  TrendingUp, 
  Award, 
  Compass, 
  Layers, 
  ChevronRight, 
  ArrowLeft, 
  Sparkles,
  Maximize2
} from 'lucide-react';
import RecoveryBanner from './RecoveryBanner';
import MapView from './MapView';

const ROUTE_COLORS = [
  '#2563eb', // Royal Blue (Route 1)
  '#10b981', // Emerald Green (Route 2)
  '#f59e0b', // Amber Orange (Route 3)
  '#8b5cf6', // Violet Purple (Route 4)
  '#ec4899', // Pink (Route 5)
];

function formatDuration(mins) {
  if (!mins && mins !== 0) return 'N/A';
  const h = Math.floor(mins / 60);
  const m = Math.round(mins % 60);
  if (h === 0) return `${m}m`;
  return `${h}h ${m > 0 ? `${m}m` : ''}`;
}

// Dedicated Single Route Leaflet Map component
function SingleRouteMap({ route, color, sourceLabel, destLabel }) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);

  useEffect(() => {
    if (!mapContainerRef.current) return;

    // Remove existing map instance if any
    if (mapInstanceRef.current) {
      mapInstanceRef.current.remove();
      mapInstanceRef.current = null;
    }

    try {
      const map = L.map(mapContainerRef.current, {
        zoomControl: false,
        attributionControl: false,
        scrollWheelZoom: false,
        dragging: true,
      });

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
      }).addTo(map);

      const coords = route.path_coordinates || [];
      if (coords.length > 0) {
        const polyline = L.polyline(coords, {
          color: color || '#2563eb',
          weight: 5,
          opacity: 0.95,
        }).addTo(map);

        // Origin marker (Green)
        L.circleMarker(coords[0], {
          radius: 6,
          fillColor: '#10b981',
          color: '#ffffff',
          weight: 2,
          fillOpacity: 1,
        }).bindPopup(`<strong>Origin:</strong> ${sourceLabel}`).addTo(map);

        // Destination marker (Red)
        L.circleMarker(coords[coords.length - 1], {
          radius: 6,
          fillColor: '#ef4444',
          color: '#ffffff',
          weight: 2,
          fillOpacity: 1,
        }).bindPopup(`<strong>Destination:</strong> ${destLabel}`).addTo(map);

        try {
          map.fitBounds(polyline.getBounds(), { padding: [22, 22], maxZoom: 13 });
        } catch (e) {
          map.setView(coords[0], 9);
        }
      } else {
        map.setView([13.0, 79.5], 8);
      }

      // Invalidate size to ensure crisp tile rendering in grid
      const timer = setTimeout(() => {
        if (mapInstanceRef.current) {
          mapInstanceRef.current.invalidateSize();
        }
      }, 250);

      mapInstanceRef.current = map;

      return () => {
        clearTimeout(timer);
        if (mapInstanceRef.current) {
          mapInstanceRef.current.remove();
          mapInstanceRef.current = null;
        }
      };
    } catch (err) {
      console.warn('SingleRouteMap init error:', err);
    }
  }, [route, color, sourceLabel, destLabel]);

  return (
    <div className="single-route-map-wrapper">
      <div ref={mapContainerRef} className="single-route-map-canvas" />
    </div>
  );
}

export default function SideBySideRouteMaps({
  planData,
  selectedRouteId,
  onSelectRoute,
  lockedRoute,
  onRequestLock,
  onEditInput,
  onViewGraphs,
}) {
  const [viewMode, setViewMode] = useState('side_by_side'); // 'side_by_side' | 'combined'

  if (!planData || !planData.routes || planData.routes.length === 0) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '40px 20px' }}>
        <p style={{ color: 'var(--text-muted)', marginBottom: '16px' }}>
          No route data calculated yet. Please enter your trip parameters to generate routes.
        </p>
        <button type="button" className="btn btn-primary" onClick={onEditInput}>
          <ArrowLeft size={16} />
          <span>Enter Trip Data</span>
        </button>
      </div>
    );
  }

  const routes = planData.routes;
  const sourceLabel = planData.source_display || planData.source || 'Origin';
  const destLabel = planData.destination_display || planData.destination || 'Destination';

  return (
    <div className="side-by-side-section">
      {/* Top Slide Navigation & Stepper Bar */}
      <div className="step-slide-nav">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <button
            type="button"
            className="btn btn-secondary"
            style={{ minHeight: '38px', padding: '6px 14px', fontSize: '0.85rem' }}
            onClick={onEditInput}
            title="Return to Slide 1 to edit trip parameters"
          >
            <ArrowLeft size={16} />
            <span>Edit Input Data</span>
          </button>

          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontSize: '0.92rem', fontWeight: 800, color: '#f8fafc' }}>
              Slide 2: 3+ Alternative Routes & Maps
            </span>
            <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
              {sourceLabel} ➔ {destLabel} • {routes.length} Distinct Corridors
            </span>
          </div>
        </div>

        {/* View Mode Switch & Proceed to Graphs Button */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div className="view-mode-toggle">
            <button
              type="button"
              className={`view-mode-btn ${viewMode === 'side_by_side' ? 'active' : ''}`}
              onClick={() => setViewMode('side_by_side')}
              title="Show 3+ alternative routes with individual maps side by side"
            >
              <Layers size={15} />
              <span>Side-by-Side Maps</span>
            </button>
            <button
              type="button"
              className={`view-mode-btn ${viewMode === 'combined' ? 'active' : ''}`}
              onClick={() => setViewMode('combined')}
              title="Overlay all routes onto one master map"
            >
              <Maximize2 size={15} />
              <span>Combined Map</span>
            </button>
          </div>

          <button
            type="button"
            className="btn btn-secondary"
            style={{ minHeight: '38px', padding: '6px 14px', fontSize: '0.85rem', color: 'var(--color-brand)' }}
            onClick={onViewGraphs}
            title="Advance to Slide 3: Monte Carlo Probability & Reliability Graphs"
          >
            <span>Graphs & Analytics</span>
            <ChevronRight size={16} />
          </button>
        </div>
      </div>

      {/* Recovery Decision Banner */}
      {planData.recovery && (
        <RecoveryBanner
          recovery={planData.recovery}
          currentTime={planData.current_time}
          deadline={planData.deadline}
        />
      )}

      {/* VIEW MODE 1: SIDE-BY-SIDE ALTERNATIVE ROUTE MAPS */}
      {viewMode === 'side_by_side' && (
        <div className="side-by-side-container">
          <div className="side-by-side-header">
            <div>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f8fafc', margin: 0 }}>
                Comparing {routes.length} Route Corridors Side-by-Side
              </h2>
              <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', margin: '4px 0 0 0' }}>
                Each card shows its dedicated map, shortest vs alternative trajectory, and on-time arrival reliability.
              </p>
            </div>
          </div>

          {/* Side-by-Side Multi-Column Grid */}
          <div className="side-by-side-grid">
            {routes.map((route, index) => {
              const color = ROUTE_COLORS[index % ROUTE_COLORS.length];
              const isSelected = route.route_id === selectedRouteId;
              const isRouteLocked = lockedRoute?.is_active && lockedRoute.route_id === route.route_id;

              return (
                <div
                  key={route.route_id}
                  className={`route-side-card ${isSelected ? 'selected' : ''} ${route.is_best ? 'best' : ''}`}
                  onClick={() => onSelectRoute(route.route_id)}
                >
                  {/* Card Header */}
                  <div className="route-side-header">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span
                        className="route-color-pill"
                        style={{ backgroundColor: color, boxShadow: `0 0 8px ${color}` }}
                      />
                      <div style={{ display: 'flex', flexDirection: 'column' }}>
                        <span className="route-side-title">{route.route_name}</span>
                        <span className="route-side-subtitle">
                          {route.mode === 'driving' && '🚗 Driving / Cab'}
                          {route.mode === 'bus' && '🚌 Bus Transit'}
                          {route.mode === 'train' && '🚆 Train / Rail'}
                          {route.mode !== 'driving' && route.mode !== 'bus' && route.mode !== 'train' && '⚡ Multi-Modal'}
                        </span>
                      </div>
                    </div>

                    {route.is_best && (
                      <span className="route-best-badge">
                        <Award size={12} style={{ display: 'inline', marginRight: '4px' }} />
                        Recommended
                      </span>
                    )}
                  </div>

                  {/* Dedicated Individual Route Map */}
                  <div className="route-side-map-container">
                    <SingleRouteMap
                      route={route}
                      color={color}
                      sourceLabel={sourceLabel}
                      destLabel={destLabel}
                    />
                    <div className="route-map-badge-tag" style={{ borderLeft: `3px solid ${color}` }}>
                      {route.total_distance_km} km • {formatDuration(route.total_expected_time_min)}
                    </div>
                  </div>

                  {/* Reliability Metric Bars */}
                  <div className="route-side-metrics">
                    <div className="metric-pill">
                      <span className="metric-pill-label">Expected Travel</span>
                      <strong className="metric-pill-val" style={{ color: color }}>
                        {formatDuration(route.total_expected_time_min)}
                      </strong>
                    </div>

                    <div className="metric-pill">
                      <span className="metric-pill-label">Distance</span>
                      <strong className="metric-pill-val">{route.total_distance_km} km</strong>
                    </div>

                    <div className="metric-pill">
                      <span className="metric-pill-label">Safety Buffer</span>
                      <strong className="metric-pill-val" style={{ color: route.safety_buffer_min >= 15 ? '#34d399' : '#fbbf24' }}>
                        +{route.safety_buffer_min}m
                      </strong>
                    </div>

                    <div className="metric-pill">
                      <span className="metric-pill-label">Reliability Score</span>
                      <strong className="metric-pill-val">{route.score?.toFixed(1) || 'N/A'}/100</strong>
                    </div>
                  </div>

                  {/* On-Time Probability Bar Gauge */}
                  <div className="otp-progress-block">
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '4px' }}>
                      <span style={{ color: 'var(--text-muted)' }}>On-Time Probability (OTP)</span>
                      <strong
                        style={{
                          color:
                            route.on_time_probability >= 85
                              ? '#34d399'
                              : route.on_time_probability >= 60
                              ? '#fbbf24'
                              : '#f87171',
                        }}
                      >
                        {route.on_time_probability}%
                      </strong>
                    </div>
                    <div className="neu-progress-track">
                      <div
                        className="neu-progress-fill"
                        style={{
                          width: `${Math.min(100, Math.max(0, route.on_time_probability))}%`,
                          backgroundColor:
                            route.on_time_probability >= 85
                              ? '#10b981'
                              : route.on_time_probability >= 60
                              ? '#f59e0b'
                              : '#ef4444',
                        }}
                      />
                    </div>
                  </div>

                  {/* Departure & Arrival Timings */}
                  <div className="route-timing-row">
                    <div className="timing-box">
                      <span className="timing-lbl">Start</span>
                      <span className="timing-val">{route.expected_departure || planData.current_time}</span>
                    </div>
                    <span className="timing-arrow">➔</span>
                    <div className="timing-box">
                      <span className="timing-lbl">Expected</span>
                      <span className="timing-val">{route.expected_arrival || 'N/A'}</span>
                    </div>
                    <span className="timing-arrow">➔</span>
                    <div className="timing-box">
                      <span className="timing-lbl">P90 Safe</span>
                      <span className="timing-val">{route.p90_arrival || 'N/A'}</span>
                    </div>
                  </div>

                  {/* AI Recommendation Reason */}
                  {route.recommendation_reason && (
                    <div className="recommendation-reason-box">
                      <Sparkles size={14} style={{ color: 'var(--color-brand)', flexShrink: 0, marginTop: '2px' }} />
                      <span style={{ fontSize: '0.78rem', color: '#cbd5e1' }}>
                        {route.recommendation_reason}
                      </span>
                    </div>
                  )}

                  {/* Lock Action Button */}
                  <div style={{ marginTop: 'auto', paddingTop: '10px' }}>
                    {isRouteLocked ? (
                      <div className="locked-badge-btn">
                        <ShieldCheck size={16} />
                        <span>Active Locked Route</span>
                      </div>
                    ) : (
                      <button
                        type="button"
                        className="btn btn-primary btn-block"
                        style={{ minHeight: '40px', fontSize: '0.85rem' }}
                        onClick={(e) => {
                          e.stopPropagation();
                          onRequestLock(route);
                        }}
                      >
                        <ShieldCheck size={16} />
                        <span>Lock This Route</span>
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* VIEW MODE 2: COMBINED OVERVIEW MAP */}
      {viewMode === 'combined' && (
        <div className="combined-map-view-block">
          <MapView
            routes={routes}
            selectedRouteId={selectedRouteId}
            onSelectRoute={onSelectRoute}
            sourceLabel={sourceLabel}
            destLabel={destLabel}
          />
        </div>
      )}
    </div>
  );
}

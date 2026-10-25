import React, { useState } from 'react';
import { BarChart3, Activity, Clock, ShieldCheck, Zap, AlertTriangle, TrendingUp, CheckCircle2, ChevronRight } from 'lucide-react';

const ROUTE_COLORS = ['#2563eb', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'];

export default function AnalyticsDashboard({ planData, selectedRouteId, onSelectRoute }) {
  const routes = planData?.routes || [];
  const activeRoute = routes.find((r) => r.route_id === selectedRouteId) || routes[0] || null;
  const [metricTab, setMetricTab] = useState('otp'); // 'otp' | 'duration' | 'buffer'

  if (!routes || routes.length === 0) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '40px 20px' }}>
        <Activity size={48} style={{ color: 'var(--color-brand)', margin: '0 auto 16px', opacity: 0.8 }} />
        <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '8px' }}>No Active Route Data</h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', maxWidth: '420px', margin: '0 auto' }}>
          Please go to the <strong>Planner</strong> tab and calculate routes to view the live Monte Carlo graph visualizations and comparative analytics.
        </p>
      </div>
    );
  }

  // Compute normal distribution bell curve points for Monte Carlo visualization
  const mu = activeRoute ? activeRoute.total_expected_time_min : 100;
  const sigma = activeRoute ? Math.max(3.0, activeRoute.delay_spread_min || 12.0) : 10;
  const deadlineMin = planData ? (() => {
    try {
      const [ch, cm] = planData.current_time.split(':').map(Number);
      const [dh, dm] = planData.deadline.split(':').map(Number);
      let diff = (dh * 60 + dm) - (ch * 60 + cm);
      if (diff < 0) diff += 1440;
      return diff;
    } catch {
      return mu + 15;
    }
  })() : mu + 15;

  // Chart range: [mu - 3.5*sigma, mu + 3.5*sigma]
  const minX = Math.max(10, Math.floor(mu - 3.5 * sigma));
  const maxX = Math.ceil(Math.max(mu + 3.5 * sigma, deadlineMin + 10));
  const rangeX = maxX - minX || 1;

  // Generate 60 points for smooth SVG bell curve
  const svgWidth = 600;
  const svgHeight = 220;
  const paddingX = 40;
  const paddingY = 25;
  const plotWidth = svgWidth - paddingX * 2;
  const plotHeight = svgHeight - paddingY * 2;

  const points = [];
  let maxDensity = 0;

  for (let i = 0; i <= 60; i++) {
    const xVal = minX + (i / 60) * rangeX;
    // Gaussian probability density function
    const z = (xVal - mu) / sigma;
    const density = (1 / (sigma * Math.sqrt(2 * Math.PI))) * Math.exp(-0.5 * z * z);
    if (density > maxDensity) maxDensity = density;
    points.push({ x: xVal, density });
  }

  // Scale coordinates to SVG viewBox
  const coords = points.map((p) => {
    const svgX = paddingX + ((p.x - minX) / rangeX) * plotWidth;
    const svgY = svgHeight - paddingY - (p.density / (maxDensity || 1)) * plotHeight;
    return { ...p, svgX, svgY };
  });

  // SVG path strings
  const curvePath = coords.map((c, i) => `${i === 0 ? 'M' : 'L'} ${c.svgX.toFixed(1)} ${c.svgY.toFixed(1)}`).join(' ');

  // Shaded area under the curve up to deadline
  const onTimeCoords = coords.filter((c) => c.x <= deadlineMin);
  let shadedPath = '';
  if (onTimeCoords.length > 0) {
    const first = onTimeCoords[0];
    const last = onTimeCoords[onTimeCoords.length - 1];
    const lastX = paddingX + ((Math.min(deadlineMin, maxX) - minX) / rangeX) * plotWidth;
    const baseY = svgHeight - paddingY;

    shadedPath = `M ${first.svgX.toFixed(1)} ${baseY} ` +
      onTimeCoords.map((c) => `L ${c.svgX.toFixed(1)} ${c.svgY.toFixed(1)}`).join(' ') +
      ` L ${lastX.toFixed(1)} ${baseY} Z`;
  }

  // Marker positions
  const deadlineSvgX = paddingX + ((deadlineMin - minX) / rangeX) * plotWidth;
  const muSvgX = paddingX + ((mu - minX) / rangeX) * plotWidth;
  const p90Duration = mu + 1.28 * sigma;
  const p90SvgX = paddingX + ((p90Duration - minX) / rangeX) * plotWidth;

  // Maximum metrics for comparative bar chart normalization
  const maxRouteDuration = Math.max(...routes.map((r) => r.total_expected_time_min), 1);
  const maxRouteBuffer = Math.max(...routes.map((r) => Math.abs(r.buffer_min || 0)), 1);

  return (
    <div className="analytics-dashboard-container" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Dashboard Top Highlights & Quick Stats */}
      <section className="dashboard-stats-grid">
        <div className="stat-card stat-card-brand">
          <div className="stat-card-header">
            <span className="stat-card-title">Top Reliability</span>
            <Activity size={18} className="stat-icon" />
          </div>
          <div className="stat-card-value">{activeRoute?.on_time_probability || 0}%</div>
          <div className="stat-card-sub">
            {activeRoute?.on_time_probability >= 80 ? '🟢 High Confidence' : activeRoute?.on_time_probability >= 50 ? '🟡 Moderate Risk' : '🔴 Critical Delay Risk'}
          </div>
        </div>

        <div className="stat-card stat-card-success">
          <div className="stat-card-header">
            <span className="stat-card-title">Latest Safe Departure</span>
            <Clock size={18} className="stat-icon" />
          </div>
          <div className="stat-card-value">{planData?.recovery?.latest_safe_departure || activeRoute?.expected_departure}</div>
          <div className="stat-card-sub">Target Arrival: {planData?.deadline}</div>
        </div>

        <div className="stat-card stat-card-warning">
          <div className="stat-card-header">
            <span className="stat-card-title">Safety Buffer</span>
            <ShieldCheck size={18} className="stat-icon" />
          </div>
          <div className="stat-card-value" style={{ color: (activeRoute?.buffer_min || 0) >= 0 ? '#10b981' : '#ef4444' }}>
            {(activeRoute?.buffer_min || 0) >= 0 ? `+${activeRoute?.buffer_min}m` : `${activeRoute?.buffer_min}m`}
          </div>
          <div className="stat-card-sub">P90 Margin: ~{Math.round(1.28 * sigma)}m buffer</div>
        </div>

        <div className="stat-card stat-card-purple">
          <div className="stat-card-header">
            <span className="stat-card-title">Corridor Variations</span>
            <Zap size={18} className="stat-icon" />
          </div>
          <div className="stat-card-value">{routes.length} Corridors</div>
          <div className="stat-card-sub">1 Shortest + {routes.length - 1} Alternatives</div>
        </div>
      </section>

      {/* Main Graph Visualization 1: Monte Carlo Probability Density Bell Curve */}
      <section className="card chart-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px', marginBottom: '14px' }}>
          <div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <TrendingUp size={20} style={{ color: 'var(--color-brand)' }} />
              Monte Carlo Probability Distribution Curve
            </h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: '2px' }}>
              Simulated travel time density based on 1,000 runs for: <strong>{activeRoute?.route_name}</strong>
            </p>
          </div>

          {/* Route Selector Pills */}
          <div className="chart-route-selector">
            {routes.map((r, i) => (
              <button
                key={r.route_id}
                type="button"
                className={`chart-route-pill ${r.route_id === activeRoute?.route_id ? 'active' : ''}`}
                style={{ borderColor: ROUTE_COLORS[i % ROUTE_COLORS.length] }}
                onClick={() => onSelectRoute(r.route_id)}
              >
                <span className="pill-dot" style={{ backgroundColor: ROUTE_COLORS[i % ROUTE_COLORS.length] }} />
                <span>{r.route_name.includes(':') ? r.route_name.split(':')[0] : `Route ${i + 1}`}</span>
              </button>
            ))}
          </div>
        </div>

        {/* SVG Bell Curve Graph */}
        <div className="svg-chart-wrapper">
          <svg viewBox={`0 0 ${svgWidth} ${svgHeight}`} className="density-svg-chart">
            <defs>
              <linearGradient id="onTimeGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#10b981" stopOpacity="0.45" />
                <stop offset="100%" stopColor="#10b981" stopOpacity="0.05" />
              </linearGradient>
              <linearGradient id="curveLineGrad" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#3b82f6" />
                <stop offset="50%" stopColor="#60a5fa" />
                <stop offset="100%" stopColor="#8b5cf6" />
              </linearGradient>
            </defs>

            {/* Horizontal Grid Baseline */}
            <line
              x1={paddingX}
              y1={svgHeight - paddingY}
              x2={svgWidth - paddingX}
              y2={svgHeight - paddingY}
              stroke="rgba(255,255,255,0.15)"
              strokeWidth="1.5"
            />

            {/* Shaded On-Time Probability Area */}
            {shadedPath && <path d={shadedPath} fill="url(#onTimeGrad)" />}

            {/* Bell Curve Line */}
            <path
              d={curvePath}
              fill="none"
              stroke="url(#curveLineGrad)"
              strokeWidth="3.5"
              strokeLinecap="round"
            />

            {/* Expected Duration Marker (Mean \mu) */}
            {muSvgX >= paddingX && muSvgX <= svgWidth - paddingX && (
              <g>
                <line
                  x1={muSvgX}
                  y1={paddingY}
                  x2={muSvgX}
                  y2={svgHeight - paddingY}
                  stroke="#38bdf8"
                  strokeWidth="2"
                  strokeDasharray="4 3"
                />
                <circle cx={muSvgX} cy={paddingY + 8} r="4" fill="#38bdf8" />
                <text x={muSvgX} y={paddingY - 5} fill="#38bdf8" fontSize="10" textAnchor="middle" fontWeight="bold">
                  Mean: {Math.round(mu)}m
                </text>
              </g>
            )}

            {/* P90 Duration Marker */}
            {p90SvgX >= paddingX && p90SvgX <= svgWidth - paddingX && (
              <g>
                <line
                  x1={p90SvgX}
                  y1={paddingY + 18}
                  x2={p90SvgX}
                  y2={svgHeight - paddingY}
                  stroke="#fbbf24"
                  strokeWidth="2"
                  strokeDasharray="3 3"
                />
                <text x={p90SvgX} y={paddingY + 14} fill="#fbbf24" fontSize="10" textAnchor="middle">
                  P90: {Math.round(p90Duration)}m
                </text>
              </g>
            )}

            {/* Deadline Vertical Threshold Line (Bright Neon Red) */}
            {deadlineSvgX >= paddingX && deadlineSvgX <= svgWidth - paddingX && (
              <g>
                <line
                  x1={deadlineSvgX}
                  y1={paddingY}
                  x2={deadlineSvgX}
                  y2={svgHeight - paddingY}
                  stroke="#ef4444"
                  strokeWidth="2.5"
                />
                <rect
                  x={deadlineSvgX - 35}
                  y={paddingY - 18}
                  width="70"
                  height="16"
                  rx="3"
                  fill="#ef4444"
                />
                <text x={deadlineSvgX} y={paddingY - 6} fill="#ffffff" fontSize="9.5" textAnchor="middle" fontWeight="bold">
                  DEADLINE
                </text>
              </g>
            )}

            {/* X-axis Minute Labels */}
            {[0, 0.25, 0.5, 0.75, 1.0].map((frac, idx) => {
              const xVal = Math.round(minX + frac * rangeX);
              const svgX = paddingX + frac * plotWidth;
              return (
                <text
                  key={idx}
                  x={svgX}
                  y={svgHeight - 6}
                  fill="rgba(255,255,255,0.4)"
                  fontSize="10"
                  textAnchor="middle"
                >
                  {xVal} min
                </text>
              );
            })}
          </svg>
        </div>

        {/* Legend for Distribution Chart */}
        <div className="chart-legend-row">
          <div className="chart-legend-badge">
            <span className="legend-indicator" style={{ backgroundColor: '#10b981' }} />
            <span>Green Area: <strong>{activeRoute?.on_time_probability}% On-Time</strong></span>
          </div>
          <div className="chart-legend-badge">
            <span className="legend-indicator" style={{ backgroundColor: '#38bdf8' }} />
            <span>Blue Line: <strong>Expected Duration (~{Math.round(mu)}m)</strong></span>
          </div>
          <div className="chart-legend-badge">
            <span className="legend-indicator" style={{ backgroundColor: '#fbbf24' }} />
            <span>Yellow Line: <strong>P90 Duration (~{Math.round(p90Duration)}m)</strong></span>
          </div>
          <div className="chart-legend-badge">
            <span className="legend-indicator" style={{ backgroundColor: '#ef4444' }} />
            <span>Red Line: <strong>Target Deadline Cutoff</strong></span>
          </div>
        </div>
      </section>

      {/* Main Graph Visualization 2: Multi-Route Comparative Bar Analysis */}
      <section className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px', marginBottom: '16px' }}>
          <div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <BarChart3 size={20} style={{ color: 'var(--color-brand)' }} />
              Comparative Multi-Route Corridor Analytics
            </h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: '2px' }}>
              Side-by-side performance comparison of all {routes.length} discovered corridors
            </p>
          </div>

          {/* Metric Filter Tabs */}
          <div className="chart-segmented-control">
            <button
              type="button"
              className={`segmented-btn ${metricTab === 'otp' ? 'active' : ''}`}
              onClick={() => setMetricTab('otp')}
            >
              On-Time Prob (%)
            </button>
            <button
              type="button"
              className={`segmented-btn ${metricTab === 'duration' ? 'active' : ''}`}
              onClick={() => setMetricTab('duration')}
            >
              Duration (m)
            </button>
            <button
              type="button"
              className={`segmented-btn ${metricTab === 'buffer' ? 'active' : ''}`}
              onClick={() => setMetricTab('buffer')}
            >
              Safety Buffer (m)
            </button>
          </div>
        </div>

        {/* Visual Bar Comparison Grid */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {routes.map((r, i) => {
            const isSelected = r.route_id === selectedRouteId;
            const color = ROUTE_COLORS[i % ROUTE_COLORS.length];

            let barPercent = 0;
            let displayVal = '';

            if (metricTab === 'otp') {
              barPercent = Math.min(100, Math.max(5, r.on_time_probability));
              displayVal = `${r.on_time_probability}%`;
            } else if (metricTab === 'duration') {
              barPercent = Math.min(100, Math.max(10, (r.total_expected_time_min / maxRouteDuration) * 100));
              displayVal = `~${r.total_expected_time_min} mins`;
            } else {
              const buf = r.buffer_min || 0;
              barPercent = Math.min(100, Math.max(5, (Math.abs(buf) / (maxRouteBuffer || 1)) * 100));
              displayVal = buf >= 0 ? `+${buf} mins` : `${buf} mins`;
            }

            return (
              <div
                key={r.route_id}
                className={`comparative-bar-row ${isSelected ? 'selected' : ''}`}
                onClick={() => onSelectRoute(r.route_id)}
                style={{
                  borderLeft: `5px solid ${color}`,
                  cursor: 'pointer',
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: isSelected ? 'rgba(59, 130, 246, 0.12)' : 'var(--bg-surface-elevated)',
                  transition: 'all 0.2s',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontWeight: 700, fontSize: '0.85rem', color: color }}>
                      {r.route_name.includes(':') ? r.route_name.split(':')[0] : `Route ${i + 1}`}
                    </span>
                    <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                      ({r.total_distance_km} km • {r.mode.toUpperCase()})
                    </span>
                    {r.is_best && (
                      <span className="route-best-badge" style={{ fontSize: '0.68rem', padding: '1px 6px' }}>
                        Recommended
                      </span>
                    )}
                  </div>
                  <span style={{ fontWeight: 700, fontSize: '0.88rem', color: '#f8fafc' }}>{displayVal}</span>
                </div>

                {/* Animated Progress Bar */}
                <div style={{ width: '100%', height: '8px', backgroundColor: 'rgba(255,255,255,0.08)', borderRadius: '4px', overflow: 'hidden' }}>
                  <div
                    style={{
                      width: `${barPercent}%`,
                      height: '100%',
                      backgroundColor: color,
                      borderRadius: '4px',
                      transition: 'width 0.4s ease',
                      boxShadow: `0 0 10px ${color}88`,
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Corridor Decision Matrix Table */}
      <section className="card">
        <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <CheckCircle2 size={20} style={{ color: 'var(--color-success)' }} />
          Decision Matrix & Reliability Rankings
        </h3>

        <div style={{ overflowX: 'auto' }}>
          <table className="decision-matrix-table">
            <thead>
              <tr>
                <th>Corridor</th>
                <th>Mode</th>
                <th>Distance</th>
                <th>Expected Travel</th>
                <th>P90 Arrival</th>
                <th>Safety Buffer</th>
                <th>On-Time Prob</th>
                <th>Score</th>
              </tr>
            </thead>
            <tbody>
              {routes.map((r, i) => (
                <tr
                  key={r.route_id}
                  className={r.route_id === selectedRouteId ? 'active-row' : ''}
                  onClick={() => onSelectRoute(r.route_id)}
                  style={{ cursor: 'pointer' }}
                >
                  <td style={{ fontWeight: 600 }}>
                    <span style={{ display: 'inline-block', width: '8px', height: '8px', borderRadius: '50%', backgroundColor: ROUTE_COLORS[i % ROUTE_COLORS.length], marginRight: '8px' }} />
                    {r.route_name.includes(':') ? r.route_name.split(':')[0] : `Route ${i + 1}`}
                  </td>
                  <td><span className="mode-badge">{r.mode}</span></td>
                  <td>{r.total_distance_km} km</td>
                  <td>~{r.total_expected_time_min}m</td>
                  <td style={{ color: '#93c5fd' }}>{r.p90_arrival}</td>
                  <td style={{ color: r.buffer_min >= 0 ? '#10b981' : '#ef4444', fontWeight: 700 }}>
                    {r.buffer_min >= 0 ? `+${r.buffer_min}m` : `${r.buffer_min}m`}
                  </td>
                  <td>
                    <span className={`otp-tag ${r.on_time_probability >= 80 ? 'high' : r.on_time_probability >= 50 ? 'med' : 'low'}`}>
                      {r.on_time_probability}%
                    </span>
                  </td>
                  <td style={{ fontWeight: 700 }}>{r.reliability_score}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

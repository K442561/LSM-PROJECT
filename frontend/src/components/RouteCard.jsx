import React, { useState } from 'react';
import { Lock, Check, ChevronDown, ChevronUp, Bus, Train, Car, ShieldAlert } from 'lucide-react';

export default function RouteCard({
  route,
  isSelected,
  isLocked,
  onSelect,
  onRequestLock,
  colorIndicator = '#3b82f6',
}) {
  const [isExpanded, setIsExpanded] = useState(false);

  const getOtpClass = (otp) => {
    if (otp >= 80) return 'high-prob';
    if (otp >= 50) return 'med-prob';
    return 'low-prob';
  };

  const getModeIcon = (mode) => {
    switch (mode) {
      case 'train':
        return <Train size={18} />;
      case 'car':
        return <Car size={18} />;
      default:
        return <Bus size={18} />;
    }
  };

  return (
    <article
      className={`route-card ${isSelected ? 'selected' : ''} ${route.is_best ? 'best-route' : ''}`}
      onClick={() => onSelect(route.route_id)}
      style={{ borderLeft: `6px solid ${colorIndicator}` }}
    >
      <div className="route-header">
        <div className="route-title-area">
          <div className="route-title">
            {getModeIcon(route.mode)}
            <span>{route.route_name}</span>
          </div>
          <div className="route-path-summary">{route.summary_path}</div>
        </div>

        {route.is_best && <span className="route-best-badge">Recommended</span>}
      </div>

      {/* One-Line Recommendation Reason */}
      {route.is_best && route.recommendation_reason && (
        <div className="recommendation-reason-box">
          {route.recommendation_reason}
        </div>
      )}

      {/* Primary Metrics Grid */}
      <div className="metrics-grid">
        <div className="metric-pill">
          <span className="metric-label">Travel Time</span>
          <span className="metric-value">~{route.total_expected_time_min}m</span>
        </div>

        <div className="metric-pill">
          <span className="metric-label">On-Time Prob</span>
          <span className={`metric-value ${getOtpClass(route.on_time_probability)}`}>
            {route.on_time_probability}%
          </span>
        </div>

        <div className="metric-pill">
          <span className="metric-label">Buffer</span>
          <span className="metric-value" style={{ color: route.buffer_min < 0 ? 'var(--color-danger)' : 'inherit' }}>
            {route.buffer_min > 0 ? `+${route.buffer_min}m` : `${route.buffer_min}m`}
          </span>
        </div>

        <div className="metric-pill">
          <span className="metric-label">Reliability Score</span>
          <span className="metric-value">{route.reliability_score}</span>
        </div>

        <div className="metric-pill">
          <span className="metric-label">Wait Time</span>
          <span className="metric-value">{route.waiting_time_min}m</span>
        </div>

        <div className="metric-pill">
          <span className="metric-label">Transfers</span>
          <span className="metric-value">{route.transfers}</span>
        </div>

        <div className="metric-pill">
          <span className="metric-label">Expected Arrival</span>
          <span className="metric-value">{route.expected_arrival}</span>
        </div>

        <div className="metric-pill">
          <span className="metric-label">P90 Arrival</span>
          <span className="metric-value" style={{ color: '#93c5fd' }}>
            {route.p90_arrival}
          </span>
        </div>
      </div>

      {/* Expandable Segment Legs */}
      {route.segments && route.segments.length > 0 && (
        <div>
          <button
            type="button"
            className="btn btn-secondary"
            style={{ minHeight: '36px', padding: '6px 12px', fontSize: '0.8rem', width: '100%' }}
            onClick={(e) => {
              e.stopPropagation();
              setIsExpanded(!isExpanded);
            }}
          >
            {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            <span>{isExpanded ? 'Hide Leg Details' : `View ${route.segments.length} Leg Details`}</span>
          </button>

          {isExpanded && (
            <div className="timeline-container">
              {route.segments.map((seg, i) => (
                <div key={i} className="timeline-step">
                  <span>
                    <strong>{seg.from_stop}</strong> → <strong>{seg.to_stop}</strong> ({seg.mode})
                  </span>
                  <span>
                    ~{seg.expected_time_min}m (±{seg.delay_spread_min}m)
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Lock Button */}
      <div style={{ marginTop: '4px' }}>
        {isLocked ? (
          <button
            type="button"
            className="btn btn-success btn-block"
            disabled
            style={{ opacity: 0.9 }}
          >
            <Check size={18} />
            <span>Route Locked</span>
          </button>
        ) : (
          <button
            type="button"
            className={`btn ${route.is_best ? 'btn-primary' : 'btn-secondary'} btn-block`}
            onClick={(e) => {
              e.stopPropagation();
              onRequestLock(route);
            }}
          >
            <Lock size={18} />
            <span>Confirm & Lock Route</span>
          </button>
        )}
      </div>
    </article>
  );
}

import React, { useState, useEffect } from 'react';
import { ShieldCheck, Clock, AlertTriangle, Navigation, CheckCircle2, Unlock, ArrowRight, Zap, RefreshCw } from 'lucide-react';

export default function ActiveTripCockpit({
  lockedRoute,
  planData,
  onRequestUnlock,
  onSwitchToPlanner,
}) {
  const [secondsRemaining, setSecondsRemaining] = useState(0);

  const activeRoute = lockedRoute?.route_data || planData?.routes?.find((r) => r.is_best) || planData?.routes?.[0] || null;
  const lsdTime = lockedRoute?.latest_safe_departure || planData?.recovery?.latest_safe_departure || activeRoute?.expected_departure || '08:45';
  const deadline = lockedRoute?.deadline || planData?.deadline || '10:30';
  const status = lockedRoute?.status || planData?.recovery?.status || 'can_make_it';

  // Live countdown to LSD
  useEffect(() => {
    const calculateSeconds = () => {
      try {
        const [targetH, targetM] = lsdTime.split(':').map(Number);
        const now = new Date();
        const curH = now.getHours();
        const curM = now.getMinutes();
        const curS = now.getSeconds();

        let diffSec = (targetH * 3600 + targetM * 60) - (curH * 3600 + curM * 60 + curS);
        // If query was earlier in the day, normalize
        if (diffSec < -43200) diffSec += 86400;
        setSecondsRemaining(diffSec);
      } catch {
        setSecondsRemaining(600);
      }
    };

    calculateSeconds();
    const interval = setInterval(calculateSeconds, 1000);
    return () => clearInterval(interval);
  }, [lsdTime]);

  const formatTimer = (totalSec) => {
    if (totalSec <= 0) return '00:00:00 (Depart Immediately)';
    const hrs = Math.floor(totalSec / 3600);
    const mins = Math.floor((totalSec % 3600) / 60);
    const secs = totalSec % 60;
    return `${String(hrs).padStart(2, '0')}:${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  };

  const isLocked = Boolean(lockedRoute?.is_active);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Cockpit Hero Card */}
      <section className="card cockpit-hero-card" style={{ borderLeft: '6px solid var(--color-success)', position: 'relative', overflow: 'hidden' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '14px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
              <span className={`status-pill ${status}`}>
                {status === 'can_make_it' ? '🟢 Safe On-Time Window' : status === 'risky' ? '🟡 Tight Buffer Risk' : '🔴 Action Required'}
              </span>
              {isLocked ? (
                <span className="locked-badge" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', background: 'rgba(16, 185, 129, 0.2)', color: '#34d399', padding: '3px 8px', borderRadius: '4px', fontSize: '0.78rem', fontWeight: 600 }}>
                  <ShieldCheck size={14} /> Screen Touch Lock Active
                </span>
              ) : (
                <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Unlocked Route Preview</span>
              )}
            </div>

            <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#f8fafc', marginBottom: '4px' }}>
              {activeRoute?.route_name || 'Active Commuter Route'}
            </h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
              {lockedRoute?.source || planData?.source || 'Origin'} → {lockedRoute?.destination || planData?.destination || 'Destination'}
            </p>
          </div>

          <div style={{ textAlign: 'right' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Latest Safe Departure (LSD)
            </span>
            <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--color-brand)', lineHeight: 1.2 }}>
              {lsdTime}
            </div>
            <div style={{ fontSize: '0.82rem', color: '#93c5fd', fontWeight: 600, fontFamily: 'monospace' }}>
              Countdown: {formatTimer(secondsRemaining)}
            </div>
          </div>
        </div>

        {/* Live Trip Progress Timeline Bar */}
        <div style={{ marginTop: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
            <span>Departure Window ({lsdTime})</span>
            <span>Expected Arrival ({activeRoute?.expected_arrival || '~10:15'})</span>
            <span>Hard Deadline ({deadline})</span>
          </div>

          <div className="cockpit-progress-track">
            <div
              className="cockpit-progress-fill"
              style={{
                width: '65%',
                backgroundColor: status === 'can_make_it' ? 'var(--color-success)' : status === 'risky' ? 'var(--color-warning)' : 'var(--color-danger)',
              }}
            />
          </div>
        </div>

        {/* Lock Controls */}
        <div style={{ display: 'flex', gap: '10px', marginTop: '18px', flexWrap: 'wrap' }}>
          {isLocked ? (
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onRequestUnlock}
              style={{ minHeight: '38px', padding: '6px 14px', fontSize: '0.85rem' }}
            >
              <Unlock size={16} />
              <span>Unlock Route</span>
            </button>
          ) : (
            <button
              type="button"
              className="btn btn-primary"
              onClick={onSwitchToPlanner}
              style={{ minHeight: '38px', padding: '6px 14px', fontSize: '0.85rem' }}
            >
              <Navigation size={16} />
              <span>Manage & Re-Plan in Map</span>
            </button>
          )}

          <button
            type="button"
            className="btn btn-secondary"
            onClick={onSwitchToPlanner}
            style={{ minHeight: '38px', padding: '6px 14px', fontSize: '0.85rem' }}
          >
            <span>View Alternatives on Map</span>
          </button>
        </div>
      </section>

      {/* Contingency Recovery Plan */}
      {planData?.recovery && (
        <section className="card">
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Zap size={20} style={{ color: 'var(--color-warning)' }} />
            Contingency Recovery Action Plan
          </h3>

          <div style={{ padding: '12px 16px', backgroundColor: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.25)', borderRadius: 'var(--radius-sm)', marginBottom: '14px' }}>
            <p style={{ fontSize: '0.9rem', color: '#fef3c7', fontWeight: 500, margin: 0 }}>
              {planData.recovery.message}
            </p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {planData.recovery.action_steps?.map((step, idx) => (
              <div
                key={idx}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '10px 14px',
                  backgroundColor: 'var(--bg-surface-elevated)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.88rem',
                }}
              >
                <div style={{ width: '24px', height: '24px', borderRadius: '50%', backgroundColor: 'var(--color-brand)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.75rem', fontWeight: 700, color: '#ffffff', flexShrink: 0 }}>
                  {idx + 1}
                </div>
                <span style={{ color: 'var(--text-main)', flex: 1 }}>{step}</span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Corridor Segment Checkpoints */}
      {activeRoute?.legs && activeRoute.legs.length > 0 && (
        <section className="card">
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Navigation size={20} style={{ color: 'var(--color-brand)' }} />
            Route Checkpoints & Transfer Protocol
          </h3>

          <div className="timeline-container">
            {activeRoute.legs.map((leg, i) => (
              <div key={i} className="timeline-step" style={{ padding: '12px 0' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
                  <div>
                    <strong style={{ fontSize: '0.95rem', color: '#f8fafc' }}>{leg.from}</strong>
                    <span style={{ color: 'var(--text-muted)', margin: '0 8px' }}>→</span>
                    <strong style={{ fontSize: '0.95rem', color: '#f8fafc' }}>{leg.to}</strong>
                    <div style={{ fontSize: '0.8rem', color: 'var(--color-brand)', marginTop: '2px', textTransform: 'uppercase', fontWeight: 600 }}>
                      Mode: {leg.mode} • Distance: {leg.distance_km} km
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#ffffff' }}>~{leg.duration_min} mins</div>
                    {leg.waiting_min > 0 && (
                      <div style={{ fontSize: '0.75rem', color: 'var(--color-warning)' }}>+{leg.waiting_min}m transfer buffer</div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

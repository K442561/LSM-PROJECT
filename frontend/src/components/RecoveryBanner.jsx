import React, { useState, useEffect } from 'react';
import { AlertTriangle, CheckCircle2, Clock, AlertCircle, ArrowRight } from 'lucide-react';

export default function RecoveryBanner({ recovery, currentTime, deadline }) {
  if (!recovery) return null;

  const { status, message, latest_safe_departure, minutes_until_lsd, missed_transit_fallback, action_steps } = recovery;

  // Real-time countdown timer in seconds
  const [secondsRemaining, setSecondsRemaining] = useState(() => Math.round(minutes_until_lsd * 60));

  useEffect(() => {
    setSecondsRemaining(Math.round(minutes_until_lsd * 60));
  }, [minutes_until_lsd, latest_safe_departure]);

  useEffect(() => {
    const interval = setInterval(() => {
      setSecondsRemaining((prev) => prev - 1);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const formatCountdown = (totalSec) => {
    const isOverdue = totalSec < 0;
    const absSec = Math.abs(totalSec);
    const m = Math.floor(absSec / 60);
    const s = absSec % 60;
    const formatted = `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    return isOverdue ? `-${formatted}` : formatted;
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'can_make_it':
        return <CheckCircle2 size={24} style={{ color: 'var(--color-success)' }} />;
      case 'risky':
        return <AlertTriangle size={24} style={{ color: 'var(--color-warning)' }} />;
      default:
        return <AlertCircle size={24} style={{ color: 'var(--color-danger)' }} />;
    }
  };

  return (
    <section className={`recovery-banner ${status}`}>
      <div className="recovery-header">
        <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
          {getStatusIcon()}
          <div>
            <div className="recovery-status-text">{message}</div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '4px' }}>
              Deadline: <strong>{deadline}</strong> | Latest Safe Departure: <strong>{latest_safe_departure}</strong>
            </div>
          </div>
        </div>
        <span className={`recovery-badge ${status}`}>{status.replace('_', ' ')}</span>
      </div>

      {/* Live Countdown Timer to Latest Safe Departure */}
      <div className="countdown-box">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Clock size={18} style={{ color: 'var(--color-brand)' }} />
          <span className="countdown-label">
            {secondsRemaining >= 0 ? 'Countdown to Safe Departure:' : 'Departure window elapsed by:'}
          </span>
        </div>
        <div
          className="countdown-timer"
          style={{ color: secondsRemaining < 300 ? 'var(--color-danger)' : '#ffffff' }}
        >
          {formatCountdown(secondsRemaining)}
        </div>
      </div>

      {/* Missed Transit Recovery Contingency */}
      {missed_transit_fallback && (
        <div className="recovery-contingency">
          <strong>⚡ Recovery Plan (if missed):</strong> {missed_transit_fallback}
        </div>
      )}

      {/* Action Guidance */}
      {action_steps && action_steps.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {action_steps.map((step, idx) => (
            <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.82rem' }}>
              <ArrowRight size={14} style={{ color: 'var(--color-brand)' }} />
              <span>{step}</span>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

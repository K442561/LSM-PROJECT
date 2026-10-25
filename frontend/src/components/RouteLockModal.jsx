import React from 'react';
import { Lock, Unlock, AlertTriangle } from 'lucide-react';

export default function RouteLockModal({
  isOpen,
  type = 'lock', // 'lock' or 'unlock'
  targetRoute,
  onConfirm,
  onCancel,
}) {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          {type === 'lock' ? (
            <div style={{ padding: '8px', background: 'rgba(59, 130, 246, 0.2)', borderRadius: '50%', color: 'var(--color-brand)' }}>
              <Lock size={24} />
            </div>
          ) : (
            <div style={{ padding: '8px', background: 'rgba(245, 158, 11, 0.2)', borderRadius: '50%', color: 'var(--color-warning)' }}>
              <AlertTriangle size={24} />
            </div>
          )}
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700 }}>
            {type === 'lock' ? 'Lock Selected Route?' : 'Unlock Active Route?'}
          </h2>
        </div>

        <div>
          {type === 'lock' ? (
            <>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.5 }}>
                Locking <strong>{targetRoute?.route_name}</strong> will freeze your trip plan.
                An accidental tap will never reroute you during travel.
              </p>
              <div
                style={{
                  background: 'var(--bg-surface-elevated)',
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-sm)',
                  marginTop: '10px',
                  fontSize: '0.85rem',
                }}
              >
                <div>Expected Arrival: <strong>{targetRoute?.expected_arrival}</strong></div>
                <div>On-Time Probability: <strong>{targetRoute?.on_time_probability}%</strong></div>
              </div>
            </>
          ) : (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.5 }}>
              Your current route is locked to prevent accidental changes.
              Are you sure you want to unlock or re-calculate routes?
            </p>
          )}
        </div>

        <div className="modal-actions">
          <button type="button" className="btn btn-secondary" onClick={onCancel}>
            Cancel
          </button>
          <button
            type="button"
            className={`btn ${type === 'lock' ? 'btn-primary' : 'btn-warning'}`}
            onClick={onConfirm}
          >
            {type === 'lock' ? 'Confirm & Lock' : 'Unlock Route'}
          </button>
        </div>
      </div>
    </div>
  );
}

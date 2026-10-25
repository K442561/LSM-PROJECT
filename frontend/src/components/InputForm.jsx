import React, { useState, useEffect } from 'react';
import { 
  Search, 
  MapPin, 
  Clock, 
  Car, 
  Bus, 
  Train, 
  Sparkles, 
  Navigation,
  ArrowRight,
  Crosshair
} from 'lucide-react';
import MapView from './MapView';

export default function InputForm({
  onSubmit,
  isLoading,
  isLocked,
  onRequestUnlock,
  pickingTarget,
  onTogglePicking,
  onMapClick,
  sourceVal,
  destVal,
}) {
  const now = new Date();
  const defaultCurrentTime = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
  const deadlineDate = new Date(now.getTime() + 150 * 60 * 1000);
  const defaultDeadline = `${String(deadlineDate.getHours()).padStart(2, '0')}:${String(deadlineDate.getMinutes()).padStart(2, '0')}`;

  const [source, setSource] = useState(sourceVal || 'VIT Katpadi');
  const [destination, setDestination] = useState(destVal || 'Tiruvannamalai');
  const [currentTime, setCurrentTime] = useState(defaultCurrentTime);
  const [deadline, setDeadline] = useState(defaultDeadline);
  const [mode, setMode] = useState('all');

  useEffect(() => {
    if (sourceVal) setSource(sourceVal);
  }, [sourceVal]);

  useEffect(() => {
    if (destVal) setDestination(destVal);
  }, [destVal]);

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    if (isLocked) {
      onRequestUnlock();
      return;
    }
    onSubmit({ source, destination, current_time: currentTime, deadline, mode });
  };

  const applyPreset = (src, dest, modeType = 'all', deadlineOffsetHours = 2.5) => {
    if (isLocked) {
      onRequestUnlock();
      return;
    }
    setSource(src);
    setDestination(dest);
    setMode(modeType);

    const nowD = new Date();
    const curStr = `${String(nowD.getHours()).padStart(2, '0')}:${String(nowD.getMinutes()).padStart(2, '0')}`;
    const targetD = new Date(nowD.getTime() + deadlineOffsetHours * 60 * 60 * 1000);
    const deadStr = `${String(targetD.getHours()).padStart(2, '0')}:${String(targetD.getMinutes()).padStart(2, '0')}`;

    setCurrentTime(curStr);
    setDeadline(deadStr);

    onSubmit({
      source: src,
      destination: dest,
      current_time: curStr,
      deadline: deadStr,
      mode: modeType,
    });
  };

  return (
    <section className="card input-slide-card">
      <div className="input-slide-header">
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f8fafc', margin: 0 }}>
            Slide 1: Enter Trip Parameters Manually
          </h2>
          <p style={{ fontSize: '0.84rem', color: 'var(--text-muted)', margin: '4px 0 0 0' }}>
            Type any source and destination in India, choose your transit mode, and proceed to the next slide to see 3+ alternative routes with individual maps side-by-side.
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} style={{ marginTop: '16px' }}>
        {/* Source & Destination Manual Inputs with Map Picker Buttons */}
        <div className="form-grid">
          <div className="form-group">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <label>
                <MapPin size={14} style={{ display: 'inline', marginRight: '4px', color: 'var(--color-success)' }} />
                Source Origin (Any place in India)
              </label>
              <button
                type="button"
                onClick={() => onTogglePicking('source')}
                style={{
                  background: pickingTarget === 'source' ? 'var(--color-success)' : 'transparent',
                  color: pickingTarget === 'source' ? '#ffffff' : 'var(--color-brand)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-pill)',
                  padding: '2px 8px',
                  fontSize: '0.72rem',
                  cursor: 'pointer',
                  fontWeight: 600,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                }}
              >
                <Crosshair size={12} />
                <span>{pickingTarget === 'source' ? '📍 Click on Map...' : '📍 Pick on Map'}</span>
              </button>
            </div>
            <input
              type="text"
              className="input-field"
              placeholder="e.g. VIT Katpadi, Chennai Central, Delhi Airport..."
              value={source}
              onChange={(e) => setSource(e.target.value)}
              required
              disabled={isLocked}
            />
          </div>

          <div className="form-group">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <label>
                <MapPin size={14} style={{ display: 'inline', marginRight: '4px', color: 'var(--color-danger)' }} />
                Destination (Any place in India)
              </label>
              <button
                type="button"
                onClick={() => onTogglePicking('destination')}
                style={{
                  background: pickingTarget === 'destination' ? 'var(--color-danger)' : 'transparent',
                  color: pickingTarget === 'destination' ? '#ffffff' : 'var(--color-brand)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-pill)',
                  padding: '2px 8px',
                  fontSize: '0.72rem',
                  cursor: 'pointer',
                  fontWeight: 600,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                }}
              >
                <Crosshair size={12} />
                <span>{pickingTarget === 'destination' ? '📍 Click on Map...' : '📍 Pick on Map'}</span>
              </button>
            </div>
            <input
              type="text"
              className="input-field"
              placeholder="e.g. Tiruvannamalai, Bengaluru, Pune..."
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              required
              disabled={isLocked}
            />
          </div>

          <div className="form-group">
            <label>
              <Clock size={14} style={{ display: 'inline', marginRight: '4px', color: 'var(--color-brand)' }} />
              Current Start Time (24h)
            </label>
            <input
              type="time"
              className="input-field"
              value={currentTime}
              onChange={(e) => setCurrentTime(e.target.value)}
              required
              disabled={isLocked}
            />
          </div>

          <div className="form-group">
            <label>
              <Clock size={14} style={{ display: 'inline', marginRight: '4px', color: '#f59e0b' }} />
              Arrival Deadline (24h)
            </label>
            <input
              type="time"
              className="input-field"
              value={deadline}
              onChange={(e) => setDeadline(e.target.value)}
              required
              disabled={isLocked}
            />
          </div>
        </div>

        {/* Transportation Mode Selector */}
        <div style={{ marginTop: '16px' }}>
          <label style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', display: 'block', marginBottom: '8px' }}>
            Transportation Mode:
          </label>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px' }}>
            <button
              type="button"
              className={`nav-btn ${mode === 'all' ? 'active' : ''}`}
              style={{ justifyContent: 'center', minHeight: '44px' }}
              onClick={() => setMode('all')}
              disabled={isLocked}
            >
              <Sparkles size={16} />
              <span>All Modes</span>
            </button>

            <button
              type="button"
              className={`nav-btn ${mode === 'driving' ? 'active' : ''}`}
              style={{ justifyContent: 'center', minHeight: '44px' }}
              onClick={() => setMode('driving')}
              disabled={isLocked}
            >
              <Car size={16} />
              <span>Driving / Cab</span>
            </button>

            <button
              type="button"
              className={`nav-btn ${mode === 'bus' ? 'active' : ''}`}
              style={{ justifyContent: 'center', minHeight: '44px' }}
              onClick={() => setMode('bus')}
              disabled={isLocked}
            >
              <Bus size={16} />
              <span>Bus Transit</span>
            </button>

            <button
              type="button"
              className={`nav-btn ${mode === 'train' ? 'active' : ''}`}
              style={{ justifyContent: 'center', minHeight: '44px' }}
              onClick={() => setMode('train')}
              disabled={isLocked}
            >
              <Train size={16} />
              <span>Train / Rail</span>
            </button>
          </div>
        </div>

        {/* Quick Presets for Popular Pan-India Routes */}
        <div style={{ marginTop: '16px' }}>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            ⚡ Popular Pan-India Routes (Instant Fill & Plan):
          </div>
          <div className="presets-container">
            <button
              type="button"
              className="preset-chip"
              onClick={() => applyPreset('VIT Katpadi', 'Tiruvannamalai', 'all', 2.2)}
            >
              VIT Katpadi → Tiruvannamalai
            </button>
            <button
              type="button"
              className="preset-chip"
              onClick={() => applyPreset('Chennai Central', 'Bengaluru Majestic', 'all', 5.0)}
            >
              Chennai → Bengaluru
            </button>
            <button
              type="button"
              className="preset-chip"
              onClick={() => applyPreset('Mumbai CSMT', 'Pune Junction', 'all', 3.5)}
            >
              Mumbai → Pune
            </button>
            <button
              type="button"
              className="preset-chip"
              onClick={() => applyPreset('New Delhi', 'Agra Cantt', 'driving', 3.5)}
            >
              Delhi → Agra
            </button>
            <button
              type="button"
              className="preset-chip"
              onClick={() => applyPreset('Coimbatore Junction', 'Madurai Meenakshi', 'bus', 4.5)}
            >
              Coimbatore → Madurai
            </button>
          </div>
        </div>

        {/* Optional Interactive Map Pinning Workspace (shown when user clicks Pick on Map) */}
        {pickingTarget && (
          <div style={{ marginTop: '16px' }}>
            <div style={{ 
              padding: '10px 14px', 
              background: 'var(--bg-surface-sunken)', 
              borderRadius: 'var(--radius-sm)', 
              marginBottom: '10px',
              border: '1px solid rgba(59, 130, 246, 0.3)',
              fontSize: '0.85rem',
              color: '#93c5fd'
            }}>
              📍 <strong>Pin Picker Active:</strong> Click anywhere on the map below to set your <strong>{pickingTarget.toUpperCase()}</strong> coordinates.
            </div>
            <MapView
              routes={[]}
              pickingTarget={pickingTarget}
              onMapClick={onMapClick}
              sourceLabel={source}
              destLabel={destination}
            />
          </div>
        )}

        {/* Primary Submit Button: Transitions to Next Slide */}
        <div style={{ marginTop: '20px' }}>
          <button
            type="submit"
            className="btn btn-primary btn-block"
            disabled={isLoading}
            style={{ minHeight: '50px', fontSize: '1rem' }}
          >
            {isLoading ? (
              <>
                <div className="spinner" />
                <span>Calculating Shortest & 3+ Alternative Routes Across India...</span>
              </>
            ) : isLocked ? (
              <span>Active Route Locked (Click to Unlock)</span>
            ) : (
              <>
                <Search size={20} />
                <span>Calculate Routes & View 3+ Alternatives Side-by-Side</span>
                <ArrowRight size={18} />
              </>
            )}
          </button>
        </div>
      </form>
    </section>
  );
}

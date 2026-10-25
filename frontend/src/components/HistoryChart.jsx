import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { TrendingUp, Clock, PlusCircle, CheckCircle2 } from 'lucide-react';

export default function HistoryChart() {
  const [historyData, setHistoryData] = useState({ total_trips: 0, average_delay_min: 0, logs: [] });
  const [isLoading, setIsLoading] = useState(true);
  const [successMessage, setSuccessMessage] = useState('');

  // Form State for logging a new trip
  const [routeId, setRouteId] = useState('ROUTE_BUS_NEW_BUS_STAND');
  const [routeName, setRouteName] = useState('Route 1: Bus via New Bus Stand');
  const [actualDeparture, setActualDeparture] = useState('08:20');
  const [actualArrival, setActualArrival] = useState('10:25');
  const [predictedDuration, setPredictedDuration] = useState('115');
  const [notes, setNotes] = useState('');

  const loadHistory = async () => {
    setIsLoading(true);
    try {
      const res = await api.getHistory();
      setHistoryData(res.data);
    } catch (e) {
      console.warn('Failed to load history', e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleRouteSelect = (id) => {
    setRouteId(id);
    if (id === 'ROUTE_BUS_NEW_BUS_STAND') {
      setRouteName('Route 1: Bus via New Bus Stand');
      setPredictedDuration('120');
    } else if (id === 'ROUTE_BUS_ARANI') {
      setRouteName('Route 2: Bus via VIT 11 Gate & Arani');
      setPredictedDuration('105');
    } else {
      setRouteName('Route 3: Train (Katpadi to Tiruvannamalai)');
      setPredictedDuration('90');
    }
  };

  const handleLogSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        route_id: routeId,
        route_name: routeName,
        source: 'VIT Katpadi',
        destination: 'Tiruvannamalai',
        actual_departure: actualDeparture,
        actual_arrival: actualArrival,
        predicted_duration_min: parseFloat(predictedDuration),
        notes: notes || undefined,
      };

      await api.logTrip(payload);
      setSuccessMessage('Trip successfully logged! Segment travel time and variability calibrated.');
      setNotes('');
      await loadHistory();
      setTimeout(() => setSuccessMessage(''), 4000);
    } catch (err) {
      alert(`Error recording trip: ${err.message}`);
    }
  };

  const logs = historyData.logs || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Accuracy Summary Stats */}
      <section className="card">
        <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <TrendingUp size={20} style={{ color: 'var(--color-brand)' }} />
          Learning Loop & Travel History
        </h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '16px' }}>
          Every logged trip automatically updates the Bayesian running average and standard deviation (variability)
          of route segments, improving future Monte Carlo simulation accuracy.
        </p>

        <div className="metrics-grid">
          <div className="metric-pill">
            <span className="metric-label">Total Logged Trips</span>
            <span className="metric-value">{historyData.total_trips}</span>
          </div>
          <div className="metric-pill">
            <span className="metric-label">Average Delay</span>
            <span
              className="metric-value"
              style={{
                color:
                  historyData.average_delay_min > 5
                    ? 'var(--color-danger)'
                    : historyData.average_delay_min < 0
                    ? 'var(--color-success)'
                    : 'inherit',
              }}
            >
              {historyData.average_delay_min > 0 ? `+${historyData.average_delay_min}m` : `${historyData.average_delay_min}m`}
            </span>
          </div>
        </div>

        {/* Visual SVG Comparison Chart */}
        {logs.length > 0 ? (
          <div className="history-chart-wrapper">
            <div style={{ fontSize: '0.85rem', fontWeight: 600, marginBottom: '8px', color: 'var(--text-muted)' }}>
              Predicted (Blue) vs Actual (Orange) Duration (mins):
            </div>
            <svg className="chart-svg" viewBox={`0 0 ${Math.max(400, logs.length * 80)} 180`}>
              {/* Baseline */}
              <line x1="10" y1="150" x2={Math.max(400, logs.length * 80) - 10} y2="150" stroke="#334155" strokeWidth="1" />

              {logs.slice(0, 8).map((log, i) => {
                const x = 30 + i * 75;
                const predH = Math.min(130, log.predicted_duration_min * 0.9);
                const actH = Math.min(130, log.actual_duration_min * 0.9);

                return (
                  <g key={log.id || i}>
                    {/* Predicted Bar */}
                    <rect
                      x={x}
                      y={150 - predH}
                      width="18"
                      height={predH}
                      fill="#3b82f6"
                      rx="3"
                    />
                    <text x={x + 9} y={145 - predH} fontSize="10" fill="#93c5fd" textAnchor="middle">
                      {Math.round(log.predicted_duration_min)}
                    </text>

                    {/* Actual Bar */}
                    <rect
                      x={x + 22}
                      y={150 - actH}
                      width="18"
                      height={actH}
                      fill={log.delay_min > 5 ? '#ef4444' : '#f59e0b'}
                      rx="3"
                    />
                    <text x={x + 31} y={145 - actH} fontSize="10" fill="#fcd34d" textAnchor="middle">
                      {Math.round(log.actual_duration_min)}
                    </text>

                    {/* Trip Label */}
                    <text x={x + 20} y="168" fontSize="9" fill="#94a3b8" textAnchor="middle">
                      Trip #{log.id}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '20px', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            No recorded trips yet. Log your first trip below to calibrate the simulation!
          </div>
        )}
      </section>

      {/* Form to Log a Real Trip */}
      <section className="card">
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <PlusCircle size={18} style={{ color: 'var(--color-brand)' }} />
          Log Completed Trip
        </h3>

        {successMessage && (
          <div
            style={{
              backgroundColor: 'var(--color-success-bg)',
              color: 'var(--color-success)',
              padding: '10px 14px',
              borderRadius: 'var(--radius-sm)',
              marginBottom: '12px',
              fontSize: '0.85rem',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            <CheckCircle2 size={18} />
            <span>{successMessage}</span>
          </div>
        )}

        <form onSubmit={handleLogSubmit} className="form-grid">
          <div className="form-group" style={{ gridColumn: 'span 2' }}>
            <label>Route Taken</label>
            <select
              className="input-field"
              value={routeId}
              onChange={(e) => handleRouteSelect(e.target.value)}
            >
              <option value="ROUTE_BUS_NEW_BUS_STAND">Route 1: Bus via New Bus Stand</option>
              <option value="ROUTE_BUS_ARANI">Route 2: Bus via VIT 11 Gate & Arani</option>
              <option value="ROUTE_TRAIN_KATPADI">Route 3: Train (Katpadi to Tiruvannamalai)</option>
            </select>
          </div>

          <div className="form-group">
            <label>Actual Departure Time</label>
            <input
              type="time"
              className="input-field"
              value={actualDeparture}
              onChange={(e) => setActualDeparture(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label>Actual Arrival Time</label>
            <input
              type="time"
              className="input-field"
              value={actualArrival}
              onChange={(e) => setActualArrival(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label>Predicted Duration (minutes)</label>
            <input
              type="number"
              className="input-field"
              value={predictedDuration}
              onChange={(e) => setPredictedDuration(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label>Traffic / Weather Notes</label>
            <input
              type="text"
              className="input-field"
              placeholder="e.g. Polur town market delay, clear highway"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
          </div>

          <div style={{ gridColumn: 'span 2', marginTop: '8px' }}>
            <button type="submit" className="btn btn-primary btn-block">
              Submit Trip Log & Calibrate Engine
            </button>
          </div>
        </form>
      </section>

      {/* Table of Past Logs */}
      {logs.length > 0 && (
        <section className="card">
          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '12px' }}>Recorded Trip History</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {logs.map((log) => (
              <div
                key={log.id}
                style={{
                  background: 'var(--bg-surface-elevated)',
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-sm)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  fontSize: '0.85rem',
                }}
              >
                <div>
                  <strong>{log.route_name.split(':')[0]}</strong> ({log.actual_departure} → {log.actual_arrival})
                  {log.notes && (
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.78rem', marginTop: '2px' }}>
                      "{log.notes}"
                    </div>
                  )}
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div>Duration: <strong>{log.actual_duration_min}m</strong></div>
                  <div
                    style={{
                      fontSize: '0.78rem',
                      color: log.delay_min > 0 ? 'var(--color-danger)' : 'var(--color-success)',
                    }}
                  >
                    {log.delay_min > 0 ? `+${log.delay_min}m delay` : `${log.delay_min}m early`}
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

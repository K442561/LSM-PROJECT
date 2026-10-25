import React, { useEffect, useRef } from 'react';
import L from 'leaflet';

const ROUTE_COLORS = [
  '#2563eb', // Royal Blue (Route 1)
  '#10b981', // Emerald Green (Route 2)
  '#f59e0b', // Amber Orange (Route 3)
  '#8b5cf6', // Violet
  '#ec4899', // Pink
];

export default function MapView({
  routes = [],
  selectedRouteId,
  onSelectRoute,
  pickingTarget,
  onMapClick,
  sourceLabel = 'Origin',
  destLabel = 'Destination',
}) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const layerGroupRef = useRef(null);

  // Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      // Centered on India by default
      const map = L.map(mapContainerRef.current, {
        center: [13.0, 79.5],
        zoom: 7,
        zoomControl: true,
      });

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 18,
      }).addTo(map);

      layerGroupRef.current = L.layerGroup().addTo(map);
      mapInstanceRef.current = map;
    }
  }, []);

  // Handle map click events for interactive point picking
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    const handleLeafletClick = (e) => {
      if (pickingTarget && onMapClick) {
        onMapClick(e.latlng.lat, e.latlng.lng, pickingTarget);
      }
    };

    map.on('click', handleLeafletClick);
    return () => {
      map.off('click', handleLeafletClick);
    };
  }, [pickingTarget, onMapClick]);

  // Render Routes and Markers
  useEffect(() => {
    const map = mapInstanceRef.current;
    const layerGroup = layerGroupRef.current;
    if (!map || !layerGroup) return;

    layerGroup.clearLayers();

    if (!routes || routes.length === 0) return;

    const allLatLons = [];

    // Render each route polyline
    routes.forEach((route, index) => {
      const isSelected = route.route_id === selectedRouteId;
      const color = ROUTE_COLORS[index % ROUTE_COLORS.length];
      const coords = route.path_coordinates || [];

      if (coords.length > 0) {
        coords.forEach((pt) => allLatLons.push(pt));

        const polyline = L.polyline(coords, {
          color: color,
          weight: isSelected ? 6 : 4,
          opacity: isSelected ? 0.95 : 0.65,
          dashArray: isSelected ? null : '6, 6',
        });

        polyline.bindPopup(`
          <div style="font-family: sans-serif; padding: 4px; font-size: 0.85rem;">
            <strong style="color: ${color};">${route.route_name}</strong><br/>
            <span>Distance: <strong>${route.total_distance_km} km</strong></span><br/>
            <span>Travel Time: ~${route.total_expected_time_min} mins</span><br/>
            <span>On-Time Probability: <strong>${route.on_time_probability}%</strong></span>
          </div>
        `);

        polyline.on('click', () => {
          if (onSelectRoute) onSelectRoute(route.route_id);
        });

        layerGroup.addLayer(polyline);
      }
    });

    // Add Start and End Pins if coordinates exist
    if (allLatLons.length > 0) {
      const startCoord = allLatLons[0];
      const endCoord = allLatLons[allLatLons.length - 1];

      // Origin Marker (Green)
      const startMarker = L.circleMarker(startCoord, {
        radius: 8,
        fillColor: '#10b981',
        color: '#ffffff',
        weight: 2,
        fillOpacity: 1,
      }).bindPopup(`<strong>Start:</strong> ${sourceLabel}`);
      layerGroup.addLayer(startMarker);

      // Destination Marker (Red)
      const endMarker = L.circleMarker(endCoord, {
        radius: 8,
        fillColor: '#ef4444',
        color: '#ffffff',
        weight: 2,
        fillOpacity: 1,
      }).bindPopup(`<strong>Destination:</strong> ${destLabel}`);
      layerGroup.addLayer(endMarker);

      // Fit map bounds to view all route corridors across India
      try {
        map.fitBounds(L.latLngBounds(allLatLons), { padding: [35, 35] });
      } catch (e) {}
    }
  }, [routes, selectedRouteId, sourceLabel, destLabel]);

  return (
    <div className="map-container-wrapper">
      {/* Visual Indicator when user is picking a location on the map */}
      {pickingTarget && (
        <div
          style={{
            position: 'absolute',
            top: '12px',
            left: '50%',
            transform: 'translateX(-50%)',
            zIndex: 1000,
            backgroundColor: pickingTarget === 'source' ? 'var(--color-success)' : 'var(--color-danger)',
            color: '#ffffff',
            padding: '8px 16px',
            borderRadius: 'var(--radius-pill)',
            fontSize: '0.85rem',
            fontWeight: 700,
            boxShadow: 'var(--shadow-elevated)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          <span>📍 Click anywhere on the map to set {pickingTarget === 'source' ? 'Source Origin' : 'Destination'}</span>
        </div>
      )}

      <div ref={mapContainerRef} className="leaflet-map" style={{ cursor: pickingTarget ? 'crosshair' : 'grab' }} />

      {routes && routes.length > 0 && (
        <div className="map-legend">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '4px', marginBottom: '4px' }}>
            <span style={{ fontWeight: 700, fontSize: '0.78rem' }}>Routes Overview ({routes.length})</span>
          </div>
          {routes.map((r, i) => {
            const isSelected = r.route_id === selectedRouteId;
            const label = r.route_name.includes(':')
              ? r.route_name.split(':')[0]
              : (i === 0 ? 'Shortest Route' : `Alternative ${i}`);
            return (
              <div
                key={r.route_id}
                className="legend-item"
                style={{
                  cursor: 'pointer',
                  fontWeight: isSelected ? 700 : 400,
                  padding: '3px 6px',
                  borderRadius: '4px',
                  backgroundColor: isSelected ? 'rgba(59, 130, 246, 0.25)' : 'transparent',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                }}
                onClick={() => onSelectRoute && onSelectRoute(r.route_id)}
                title={`Click to focus ${label}: ${r.total_distance_km} km`}
              >
                <div
                  className="legend-color-dot"
                  style={{
                    backgroundColor: ROUTE_COLORS[i % ROUTE_COLORS.length],
                    width: '14px',
                    height: '5px',
                    borderRadius: '2px',
                  }}
                />
                <span style={{ fontSize: '0.75rem', flex: 1 }}>{label}</span>
                <span style={{ fontSize: '0.70rem', color: '#94a3b8', marginLeft: '6px' }}>{r.total_distance_km} km</span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

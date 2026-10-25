import React from 'react';
import { WifiOff } from 'lucide-react';

export default function OfflineBadge({ savedAt }) {
  const formattedTime = savedAt
    ? new Date(savedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    : null;

  return (
    <div className="offline-banner">
      <WifiOff size={20} />
      <span>
        Offline Mode Active: Using saved route plan {formattedTime ? `(cached at ${formattedTime})` : ''}
      </span>
    </div>
  );
}

import React, { useState, useEffect } from 'react';
import { formatLatency, calculateUptime } from './utils.ts';

export function Dashboard() {
  const [metrics, setMetrics] = useState({ cpu: 0, memory: 0, latency: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/metrics')
      .then(res => res.json())
      .then(data => {
        setMetrics(data);
        setLoading(false);
      })
      .catch(err => console.error("Metrics fetch error:", err));
  }, []);

  if (loading) {
    return <div className="spinner">Loading Cluster Metrics...</div>;
  }

  return (
    <div className="metrics-grid">
      <div className="card">
        <h3>Latency</h3>
        <p>{formatLatency(metrics.latency)}</p>
      </div>
      <div className="card">
        <h3>Uptime</h3>
        <p>{calculateUptime(metrics.cpu)}</p>
      </div>
    </div>
  );
}

export default Dashboard;

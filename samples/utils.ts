export interface ClusterMetric {
  id: string;
  value: number;
  timestamp: number;
  status: 'healthy' | 'degraded' | 'critical';
}

export function formatLatency(ms: number): string {
  if (ms < 1) return `${(ms * 1000).toFixed(0)}µs`;
  if (ms < 1000) return `${ms.toFixed(1)}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
}

export function calculateUptime(score: number): string {
  return `${(score * 100).toFixed(2)}% Operational`;
}

import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface DeploymentLog {
  id: number;
  version: string;
  deployed_at: string;
  status: string;
  operator: string;
  notes?: string;
}

export default function DeploymentDashboard() {
  const [logs, setLogs] = useState<DeploymentLog[]>([]);
  useEffect(() => {
    axios.get('/api/deployments/logs').then(res => setLogs(res.data));
  }, []);
  return (
    <div>
      <h2>배포 이력</h2>
      <ul>
        {logs.map(log => (
          <li key={log.id}>
            {log.version} - {log.status} ({log.deployed_at}) by {log.operator}
          </li>
        ))}
      </ul>
    </div>
  );
} 
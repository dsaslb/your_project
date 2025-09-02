import { useState, useEffect } from 'react';
import { syncManager, SyncStatus } from '../services/SyncManager';

export function useSyncStatus() {
  const [syncStatus, setSyncStatus] = useState<SyncStatus>(syncManager.getCurrentStatus());

  useEffect(() => {
    const unsubscribe = syncManager.addListener(setSyncStatus);
    return unsubscribe;
  }, []);

  return {
    ...syncStatus,
    forceSync: syncManager.forceSync.bind(syncManager),
    pauseSync: syncManager.pauseSync.bind(syncManager),
    resumeSync: syncManager.resumeSync.bind(syncManager),
  };
}

'use client';

import { useWebSocket } from '@/hooks/useWebSocket';
import { Wifi, WifiOff, Loader2 } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

export function RealTimeStatus() {
  const { isConnected, isConnecting, connectionInfo } = useWebSocket();

  return (
    <div className="flex items-center gap-2">
      {isConnecting ? (
        <div className="flex items-center gap-2">
          <Loader2 className="h-4 w-4 animate-spin text-yellow-500" />
          <span className="text-sm text-yellow-600">연결 중...</span>
        </div>
      ) : isConnected ? (
        <div className="flex items-center gap-2">
          <Wifi className="h-4 w-4 text-green-500" />
          <span className="text-sm text-green-600">실시간 연결됨</span>
          <Badge variant="secondary" className="text-xs">
            {connectionInfo.rooms.length}개 룸
          </Badge>
        </div>
      ) : (
        <div className="flex items-center gap-2">
          <WifiOff className="h-4 w-4 text-red-500" />
          <span className="text-sm text-red-600">연결 끊김</span>
        </div>
      )}
    </div>
  );
} 
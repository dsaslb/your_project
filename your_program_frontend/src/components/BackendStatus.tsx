'use client';

import { useState, useEffect } from 'react';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { Wifi, WifiOff, AlertCircle } from 'lucide-react';

export default function BackendStatus() {
  const [isChecking, setIsChecking] = useState(false);

  const checkConnection = async () => {
    setIsChecking(true);
    try {
      // await checkBackendConnection();
    } catch (error) {
      console.error('Backend connection check failed:', error);
    } finally {
      setIsChecking(false);
    }
  };

  // 백엔드 연결 상태가 null인 경우에만 확인 (초기 로드 시)
  // useEffect(() => {
  //   if (backendConnected === null) {
  //     checkConnection();
  //   }
  // }, [backendConnected]);

  // if (backendConnected === null) {
  //   return (
  //     <div className="flex items-center gap-2">
  //       <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
  //       <span className="text-sm text-gray-500">연결 확인 중...</span>
  //     </div>
  //   );
  // }

  // if (backendConnected) {
  //   return (
  //     <div className="flex items-center gap-2">
  //       <Wifi className="w-4 h-4 text-green-500" />
  //       <Badge variant="secondary" className="text-green-700 bg-green-100">
  //         백엔드 연결됨
  //       </Badge>
  //     </div>
  //   );
  // }

  return (
    <Alert className="border-orange-200 bg-orange-50">
      <AlertCircle className="h-4 w-4 text-orange-600" />
      <AlertDescription className="text-orange-800">
        <div className="flex items-center gap-2">
          <WifiOff className="w-4 h-4" />
          <span>백엔드 서버에 연결할 수 없습니다. 더미 데이터를 표시합니다.</span>
          <button
            onClick={checkConnection}
            disabled={isChecking}
            className="text-xs px-2 py-1 bg-orange-200 rounded hover:bg-orange-300 disabled:opacity-50"
          >
            {isChecking ? '확인 중...' : '재시도'}
          </button>
        </div>
      </AlertDescription>
    </Alert>
  );
} 
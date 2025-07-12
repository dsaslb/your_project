"use client";

import React, { useEffect, useState, useRef } from 'react';
import { toast } from 'sonner';
import { AlertTriangle, X, CheckCircle, Info, AlertCircle } from 'lucide-react';

interface PluginAlert {
  id: string;
  plugin_id: string;
  plugin_name: string;
  level: 'info' | 'warning' | 'error' | 'critical';
  message: string;
  details: Record<string, any>;
  timestamp: string;
  resolved: boolean;
  resolved_at?: string;
}

interface PluginMetrics {
  plugin_id: string;
  plugin_name: string;
  cpu_usage: number;
  memory_usage: number;
  response_time: number;
  error_count: number;
  request_count: number;
  last_activity: string;
  status: string;
  uptime: number;
}

const PluginAlertToast: React.FC = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [alerts, setAlerts] = useState<PluginAlert[]>([]);
  const [metrics, setMetrics] = useState<Record<string, PluginMetrics>>({});
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // WebSocket 연결
  const connectWebSocket = () => {
    try {
      const ws = new WebSocket('ws://localhost:8765');
      
      ws.onopen = () => {
        setIsConnected(true);
        console.log('플러그인 알림 WebSocket 연결됨');
        
        // 인증 정보 전송 (실제 사용자 정보로 교체 필요)
        ws.send(JSON.stringify({
          type: 'auth',
          user_id: 'admin',
          role: 'admin'
        }));
        
        // 활성 알림 요청
        ws.send(JSON.stringify({ type: 'get_active_alerts' }));
        
        // 모든 메트릭 요청
        ws.send(JSON.stringify({ type: 'get_all_metrics' }));
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleWebSocketMessage(data);
        } catch (error) {
          console.error('WebSocket 메시지 파싱 오류:', error);
        }
      };
      
      ws.onclose = () => {
        setIsConnected(false);
        console.log('플러그인 알림 WebSocket 연결 끊어짐');
        
        // 재연결 시도
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
        }
        reconnectTimeoutRef.current = setTimeout(() => {
          connectWebSocket();
        }, 5000);
      };
      
      ws.onerror = (error) => {
        console.error('플러그인 알림 WebSocket 오류:', error);
        setIsConnected(false);
      };
      
      wsRef.current = ws;
    } catch (error) {
      console.error('플러그인 알림 WebSocket 연결 실패:', error);
      setIsConnected(false);
    }
  };

  // WebSocket 메시지 처리
  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'connected':
        console.log('WebSocket 연결 확인:', data);
        break;
        
      case 'auth_success':
        console.log('인증 성공');
        break;
        
      case 'alert':
        // 새로운 알림 수신
        const newAlert = data.data as PluginAlert;
        setAlerts(prev => [newAlert, ...prev]);
        showAlertToast(newAlert);
        break;
        
      case 'active_alerts':
        // 활성 알림 목록 수신
        setAlerts(data.data as PluginAlert[]);
        break;
        
      case 'all_metrics':
        // 모든 플러그인 메트릭 수신
        setMetrics(data.data as Record<string, PluginMetrics>);
        break;
        
      case 'metrics':
        // 특정 플러그인 메트릭 수신
        setMetrics(prev => ({
          ...prev,
          [data.plugin_id]: data.data as PluginMetrics
        }));
        break;
        
      case 'system_message':
        // 시스템 메시지
        showSystemToast(data.message, data.level);
        break;
        
      default:
        console.log('알 수 없는 메시지 타입:', data.type);
    }
  };

  // 알림 Toast 표시
  const showAlertToast = (alert: PluginAlert) => {
    const getIcon = () => {
      switch (alert.level) {
        case 'critical':
          return <AlertTriangle className="h-5 w-5 text-red-500" />;
        case 'error':
          return <AlertCircle className="h-5 w-5 text-red-500" />;
        case 'warning':
          return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
        default:
          return <Info className="h-5 w-5 text-blue-500" />;
      }
    };

    const getDuration = () => {
      switch (alert.level) {
        case 'critical':
          return 10000; // 10초
        case 'error':
          return 8000;  // 8초
        case 'warning':
          return 6000;  // 6초
        default:
          return 4000;  // 4초
      }
    };

    toast(
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-2">
          {getIcon()}
          <span className="font-semibold">{alert.plugin_name}</span>
        </div>
        <p className="text-sm">{alert.message}</p>
        {alert.details && Object.keys(alert.details).length > 0 && (
          <details className="text-xs text-gray-600">
            <summary className="cursor-pointer">상세 정보</summary>
            <pre className="mt-1 whitespace-pre-wrap">
              {JSON.stringify(alert.details, null, 2)}
            </pre>
          </details>
        )}
        <div className="flex justify-between items-center mt-2">
          <button
            onClick={() => resolveAlert(alert.id)}
            className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded hover:bg-green-200"
          >
            해결됨
          </button>
          <span className="text-xs text-gray-500">
            {new Date(alert.timestamp).toLocaleTimeString()}
          </span>
        </div>
      </div>,
      {
        duration: getDuration(),
        id: alert.id,
        action: {
          label: '해결',
          onClick: () => resolveAlert(alert.id),
        },
      }
    );
  };

  // 시스템 메시지 Toast 표시
  const showSystemToast = (message: string, level: string) => {
    const getIcon = () => {
      switch (level) {
        case 'error':
          return <AlertCircle className="h-5 w-5 text-red-500" />;
        case 'warning':
          return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
        case 'success':
          return <CheckCircle className="h-5 w-5 text-green-500" />;
        default:
          return <Info className="h-5 w-5 text-blue-500" />;
      }
    };

    toast(
      <div className="flex items-center gap-2">
        {getIcon()}
        <span>{message}</span>
      </div>,
      {
        duration: 4000,
      }
    );
  };

  // 알림 해결 처리
  const resolveAlert = (alertId: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'resolve_alert',
        alert_id: alertId
      }));
    }
    
    // 로컬 상태에서도 제거
    setAlerts(prev => prev.filter(alert => alert.id !== alertId));
  };

  // 연결 상태 표시
  useEffect(() => {
    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, []);

  // 페이지 가시성 변경 감지
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && !isConnected) {
        // 탭이 다시 활성화되면 WebSocket 재연결 시도
        connectWebSocket();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [isConnected]);

  // 연결 상태 표시 (개발용)
  if (process.env.NODE_ENV === 'development') {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        <div className={`px-3 py-2 rounded-lg text-sm font-medium ${
          isConnected 
            ? 'bg-green-100 text-green-800 border border-green-200' 
            : 'bg-red-100 text-red-800 border border-red-200'
        }`}>
          {isConnected ? '🔗 연결됨' : '❌ 연결 끊어짐'}
        </div>
        
        {/* 알림 통계 */}
        <div className="mt-2 bg-white border border-gray-200 rounded-lg p-3 shadow-lg">
          <div className="text-xs text-gray-600 mb-2">플러그인 알림</div>
          <div className="space-y-1">
            <div className="flex justify-between text-xs">
              <span>활성 알림:</span>
              <span className="font-medium">{alerts.filter(a => !a.resolved).length}</span>
            </div>
            <div className="flex justify-between text-xs">
              <span>모니터링 중인 플러그인:</span>
              <span className="font-medium">{Object.keys(metrics).length}</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return null;
};

export default PluginAlertToast; 
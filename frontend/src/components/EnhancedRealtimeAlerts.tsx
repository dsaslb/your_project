import React, { useState, useEffect, useRef } from 'react';
import { toast } from 'react-hot-toast';
import { Bell, X, AlertTriangle, AlertCircle, Info, CheckCircle } from 'lucide-react';

interface Alert {
  id: string;
  type: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  title: string;
  message: string;
  plugin_id?: string;
  plugin_name?: string;
  current_value?: number;
  threshold_value?: number;
  timestamp: string;
  resolved: boolean;
  resolved_at?: string;
  metadata?: Record<string, any>;
}

interface AlertStatistics {
  total_alerts: number;
  active_alerts: number;
  resolved_alerts: number;
  severity_distribution: Record<string, number>;
  type_distribution: Record<string, number>;
  last_24h_alerts: number;
}

interface NotificationConfig {
  user_id: string;
  channels: string[];
  alert_types: string[];
  severity_levels: string[];
  enabled: boolean;
  quiet_hours_start?: number;
  quiet_hours_end?: number;
}

const EnhancedRealtimeAlerts: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [statistics, setStatistics] = useState<AlertStatistics | null>(null);
  const [config, setConfig] = useState<NotificationConfig | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [showAlerts, setShowAlerts] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  
  const eventSourceRef = useRef<EventSource | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // 알림 심각도별 아이콘
  const severityIcons = {
    info: Info,
    warning: AlertTriangle,
    error: AlertCircle,
    critical: AlertCircle,
  };

  // 알림 심각도별 색상
  const severityColors = {
    info: 'bg-blue-500',
    warning: 'bg-yellow-500',
    error: 'bg-red-500',
    critical: 'bg-red-600',
  };

  // 알림 심각도별 배경색
  const severityBgColors = {
    info: 'bg-blue-50 border-blue-200',
    warning: 'bg-yellow-50 border-yellow-200',
    error: 'bg-red-50 border-red-200',
    critical: 'bg-red-100 border-red-300',
  };

  useEffect(() => {
    initializeAlerts();
    return () => {
      cleanupConnections();
    };
  }, []);

  const initializeAlerts = async () => {
    try {
      setIsLoading(true);
      
      // 알림 목록 로드
      await loadAlerts();
      
      // 통계 로드
      await loadStatistics();
      
      // 설정 로드
      await loadConfig();
      
      // 실시간 연결 설정
      setupRealtimeConnection();
      
    } catch (error) {
      console.error('알림 초기화 실패:', error);
      toast.error('알림 시스템 초기화에 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const loadAlerts = async () => {
    try {
      const response = await fetch('/api/enhanced-alerts/alerts?limit=50');
      const data = await response.json();
      
      if (data.success) {
        setAlerts(data.alerts);
        setUnreadCount(data.alerts.filter((alert: Alert) => !alert.resolved).length);
      }
    } catch (error) {
      console.error('알림 로드 실패:', error);
    }
  };

  const loadStatistics = async () => {
    try {
      const response = await fetch('/api/enhanced-alerts/alerts/statistics');
      const data = await response.json();
      
      if (data.success) {
        setStatistics(data.statistics);
      }
    } catch (error) {
      console.error('통계 로드 실패:', error);
    }
  };

  const loadConfig = async () => {
    try {
      const response = await fetch('/api/enhanced-alerts/notifications/config');
      const data = await response.json();
      
      if (data.success) {
        setConfig(data.config);
      }
    } catch (error) {
      console.error('설정 로드 실패:', error);
    }
  };

  const setupRealtimeConnection = () => {
    // Server-Sent Events 연결
    try {
      eventSourceRef.current = new EventSource('/api/enhanced-alerts/stream');
      
      eventSourceRef.current.onopen = () => {
        setIsConnected(true);
        console.log('실시간 알림 스트림 연결됨');
      };
      
      eventSourceRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleRealtimeData(data);
      };
      
      eventSourceRef.current.onerror = (error) => {
        console.error('실시간 알림 스트림 오류:', error);
        setIsConnected(false);
        // 재연결 시도
        setTimeout(setupRealtimeConnection, 5000);
      };
      
    } catch (error) {
      console.error('실시간 연결 설정 실패:', error);
    }
  };

  const handleRealtimeData = (data: any) => {
    switch (data.type) {
      case 'connected':
        console.log('실시간 알림 연결됨:', data.connection_id);
        break;
        
      case 'active_alerts':
        if (data.alerts) {
          setAlerts(data.alerts);
          setUnreadCount(data.alerts.filter((alert: Alert) => !alert.resolved).length);
        }
        break;
        
      case 'realtime_alert':
        if (data.alert) {
          handleNewAlert(data.alert);
        }
        break;
        
      case 'heartbeat':
        // 연결 유지 확인
        break;
        
      default:
        console.log('알 수 없는 실시간 데이터:', data);
    }
  };

  const handleNewAlert = (alert: Alert) => {
    // 새 알림 추가
    setAlerts(prev => [alert, ...prev]);
    setUnreadCount(prev => prev + 1);
    
    // 토스트 알림 표시
    const Icon = severityIcons[alert.severity];
    const bgColor = severityColors[alert.severity];
    
    toast.custom((t) => (
      <div className={`${t.visible ? 'animate-enter' : 'animate-leave'} max-w-md w-full ${bgColor} shadow-lg rounded-lg pointer-events-auto flex ring-1 ring-black ring-opacity-5`}>
        <div className="flex-1 w-0 p-4">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <Icon className="h-6 w-6 text-white" />
            </div>
            <div className="ml-3 flex-1">
              <p className="text-sm font-medium text-white">
                {alert.title}
              </p>
              <p className="mt-1 text-sm text-white opacity-90">
                {alert.message}
              </p>
              {alert.plugin_id && (
                <p className="mt-1 text-xs text-white opacity-75">
                  플러그인: {alert.plugin_name || alert.plugin_id}
                </p>
              )}
            </div>
          </div>
        </div>
        <div className="flex border-l border-white border-opacity-20">
          <button
            onClick={() => toast.dismiss(t.id)}
            className="w-full border border-transparent rounded-none rounded-r-lg p-4 flex items-center justify-center text-sm font-medium text-white hover:bg-white hover:bg-opacity-10 focus:outline-none focus:ring-2 focus:ring-white"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
      </div>
    ), {
      duration: 8000,
      position: 'top-right',
    });
  };

  const resolveAlert = async (alertId: string) => {
    try {
      const response = await fetch(`/api/enhanced-alerts/alerts/${alertId}/resolve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const data = await response.json();
      
      if (data.success) {
        setAlerts(prev => prev.map(alert => 
          alert.id === alertId 
            ? { ...alert, resolved: true, resolved_at: new Date().toISOString() }
            : alert
        ));
        setUnreadCount(prev => Math.max(0, prev - 1));
        toast.success('알림이 해결되었습니다.');
      }
    } catch (error) {
      console.error('알림 해결 실패:', error);
      toast.error('알림 해결에 실패했습니다.');
    }
  };

  const bulkResolveAlerts = async () => {
    const unresolvedAlerts = alerts.filter(alert => !alert.resolved);
    if (unresolvedAlerts.length === 0) {
      toast.info('해결할 알림이 없습니다.');
      return;
    }
    
    try {
      const response = await fetch('/api/enhanced-alerts/alerts/bulk-resolve', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          alert_ids: unresolvedAlerts.map(alert => alert.id)
        }),
      });
      
      const data = await response.json();
      
      if (data.success) {
        setAlerts(prev => prev.map(alert => ({ ...alert, resolved: true, resolved_at: new Date().toISOString() })));
        setUnreadCount(0);
        toast.success(`${data.resolved_count}개의 알림이 해결되었습니다.`);
      }
    } catch (error) {
      console.error('다중 알림 해결 실패:', error);
      toast.error('다중 알림 해결에 실패했습니다.');
    }
  };

  const cleanupConnections = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    setIsConnected(false);
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return '방금 전';
    if (diffMins < 60) return `${diffMins}분 전`;
    if (diffHours < 24) return `${diffHours}시간 전`;
    if (diffDays < 7) return `${diffDays}일 전`;
    
    return date.toLocaleDateString('ko-KR');
  };

  const getSeverityText = (severity: string) => {
    const severityMap = {
      info: '정보',
      warning: '경고',
      error: '오류',
      critical: '심각',
    };
    return severityMap[severity as keyof typeof severityMap] || severity;
  };

  const getTypeText = (type: string) => {
    const typeMap = {
      plugin_cpu_high: '플러그인 CPU 높음',
      plugin_memory_high: '플러그인 메모리 높음',
      plugin_error_rate_high: '플러그인 에러율 높음',
      plugin_response_slow: '플러그인 응답 느림',
      plugin_offline: '플러그인 오프라인',
      system_cpu_high: '시스템 CPU 높음',
      system_memory_high: '시스템 메모리 높음',
      system_disk_full: '디스크 공간 부족',
      security_breach: '보안 침해',
      custom_alert: '사용자 정의 알림',
    };
    return typeMap[type as keyof typeof typeMap] || type;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-4">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        <span className="ml-2 text-gray-600">알림 로딩 중...</span>
      </div>
    );
  }

  return (
    <div className="relative">
      {/* 알림 버튼 */}
      <button
        onClick={() => setShowAlerts(!showAlerts)}
        className="relative p-2 text-gray-600 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-lg"
      >
        <Bell className="h-6 w-6" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
        {isConnected && (
          <div className="absolute -bottom-1 -right-1 w-2 h-2 bg-green-500 rounded-full"></div>
        )}
      </button>

      {/* 알림 패널 */}
      {showAlerts && (
        <div className="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-lg border border-gray-200 z-50 max-h-96 overflow-hidden">
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">실시간 알림</h3>
              <div className="flex items-center space-x-2">
                {isConnected && (
                  <div className="flex items-center text-green-600 text-sm">
                    <div className="w-2 h-2 bg-green-500 rounded-full mr-1"></div>
                    연결됨
                  </div>
                )}
                <button
                  onClick={() => setShowAlerts(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            </div>
            
            {/* 통계 요약 */}
            {statistics && (
              <div className="mt-3 grid grid-cols-3 gap-2 text-xs">
                <div className="text-center">
                  <div className="font-semibold text-blue-600">{statistics.active_alerts}</div>
                  <div className="text-gray-500">활성</div>
                </div>
                <div className="text-center">
                  <div className="font-semibold text-green-600">{statistics.resolved_alerts}</div>
                  <div className="text-gray-500">해결됨</div>
                </div>
                <div className="text-center">
                  <div className="font-semibold text-orange-600">{statistics.last_24h_alerts}</div>
                  <div className="text-gray-500">24시간</div>
                </div>
              </div>
            )}
          </div>

          {/* 알림 목록 */}
          <div className="max-h-64 overflow-y-auto">
            {alerts.length === 0 ? (
              <div className="p-4 text-center text-gray-500">
                알림이 없습니다.
              </div>
            ) : (
              <div className="divide-y divide-gray-100">
                {alerts.map((alert) => {
                  const Icon = severityIcons[alert.severity];
                  const bgColor = severityBgColors[alert.severity];
                  
                  return (
                    <div
                      key={alert.id}
                      className={`p-4 ${bgColor} ${alert.resolved ? 'opacity-60' : ''}`}
                    >
                      <div className="flex items-start space-x-3">
                        <Icon className={`h-5 w-5 mt-0.5 ${severityColors[alert.severity].replace('bg-', 'text-')}`} />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <p className="text-sm font-medium text-gray-900">
                              {alert.title}
                            </p>
                            <div className="flex items-center space-x-2">
                              <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                                alert.severity === 'critical' ? 'bg-red-100 text-red-800' :
                                alert.severity === 'error' ? 'bg-red-100 text-red-800' :
                                alert.severity === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                                'bg-blue-100 text-blue-800'
                              }`}>
                                {getSeverityText(alert.severity)}
                              </span>
                              {!alert.resolved && (
                                <button
                                  onClick={() => resolveAlert(alert.id)}
                                  className="text-gray-400 hover:text-green-600"
                                  title="해결"
                                >
                                  <CheckCircle className="h-4 w-4" />
                                </button>
                              )}
                            </div>
                          </div>
                          <p className="mt-1 text-sm text-gray-600">
                            {alert.message}
                          </p>
                          {alert.plugin_id && (
                            <p className="mt-1 text-xs text-gray-500">
                              플러그인: {alert.plugin_name || alert.plugin_id}
                            </p>
                          )}
                          {alert.current_value !== undefined && alert.threshold_value !== undefined && (
                            <p className="mt-1 text-xs text-gray-500">
                              현재값: {alert.current_value.toFixed(1)} / 임계값: {alert.threshold_value.toFixed(1)}
                            </p>
                          )}
                          <p className="mt-1 text-xs text-gray-400">
                            {formatTimestamp(alert.timestamp)}
                          </p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* 액션 버튼 */}
          {alerts.length > 0 && (
            <div className="p-4 border-t border-gray-200">
              <div className="flex justify-between">
                <button
                  onClick={loadAlerts}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  새로고침
                </button>
                {unreadCount > 0 && (
                  <button
                    onClick={bulkResolveAlerts}
                    className="text-sm text-green-600 hover:text-green-800"
                  >
                    모두 해결
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default EnhancedRealtimeAlerts; 
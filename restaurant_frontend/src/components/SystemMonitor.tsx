"use client";

import { useSystemStatus } from "@/hooks/useMonitoring";
import { 
  Activity, 
  Cpu, 
  HardDrive, 
  Database, 
  Network, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  TrendingUp,
  TrendingDown
} from "lucide-react";

interface SystemMonitorProps {
  className?: string;
}

export default function SystemMonitor({ className = "" }: SystemMonitorProps) {
  const { data: systemData, isLoading, error } = useSystemStatus();

  if (isLoading) {
    return (
      <div className={`bg-white rounded-lg shadow-sm border p-6 ${className}`}>
        <h2 className="text-xl font-semibold text-gray-900 mb-6">시스템 모니터링</h2>
        <div className="space-y-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="animate-pulse">
              <div className="h-12 bg-gray-200 rounded-lg"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-white rounded-lg shadow-sm border p-6 ${className}`}>
        <h2 className="text-xl font-semibold text-gray-900 mb-6">시스템 모니터링</h2>
        <div className="flex items-center space-x-2 text-red-600">
          <AlertTriangle className="h-5 w-5" />
          <span>시스템 데이터를 불러올 수 없습니다</span>
        </div>
      </div>
    );
  }

  const getStatusColor = (percent: number) => {
    if (percent < 50) return 'text-green-600';
    if (percent < 80) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getStatusIcon = (percent: number) => {
    if (percent < 50) return <CheckCircle className="h-4 w-4 text-green-600" />;
    if (percent < 80) return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
    return <AlertTriangle className="h-4 w-4 text-red-600" />;
  };

  const getStatusText = (percent: number) => {
    if (percent < 50) return '정상';
    if (percent < 80) return '주의';
    return '위험';
  };

  const formatBytes = (bytes: number) => {
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    if (bytes === 0) return '0 B';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className={`bg-white rounded-lg shadow-sm border p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">시스템 모니터링</h2>
        <div className="flex items-center space-x-2 text-xs text-gray-500">
          <Clock className="h-3 w-3" />
          <span>실시간</span>
        </div>
      </div>
      
      <div className="space-y-4">
        {/* CPU 사용률 */}
        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center space-x-3">
            <Cpu className="h-5 w-5 text-gray-600" />
            <div>
              <span className="text-sm font-medium text-gray-900">CPU 사용률</span>
              <div className="text-xs text-gray-500">
                프로세서 성능
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className="flex items-center space-x-2">
              {getStatusIcon(systemData?.system?.cpu_percent || 0)}
              <span className={`text-lg font-bold ${getStatusColor(systemData?.system?.cpu_percent || 0)}`}>
                {systemData?.system?.cpu_percent || 0}%
              </span>
            </div>
            <div className="text-xs text-gray-500">
              {getStatusText(systemData?.system?.cpu_percent || 0)}
            </div>
          </div>
        </div>

        {/* 메모리 사용률 */}
        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center space-x-3">
            <Database className="h-5 w-5 text-gray-600" />
            <div>
              <span className="text-sm font-medium text-gray-900">메모리 사용률</span>
              <div className="text-xs text-gray-500">
                {systemData?.system?.memory?.used_gb || 0}GB / {systemData?.system?.memory?.total_gb || 0}GB
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className="flex items-center space-x-2">
              {getStatusIcon(systemData?.system?.memory?.percent || 0)}
              <span className={`text-lg font-bold ${getStatusColor(systemData?.system?.memory?.percent || 0)}`}>
                {systemData?.system?.memory?.percent || 0}%
              </span>
            </div>
            <div className="text-xs text-gray-500">
              {getStatusText(systemData?.system?.memory?.percent || 0)}
            </div>
          </div>
        </div>

        {/* 디스크 사용률 */}
        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center space-x-3">
            <HardDrive className="h-5 w-5 text-gray-600" />
            <div>
              <span className="text-sm font-medium text-gray-900">디스크 사용률</span>
              <div className="text-xs text-gray-500">
                {systemData?.system?.disk?.used_gb || 0}GB / {systemData?.system?.disk?.total_gb || 0}GB
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className="flex items-center space-x-2">
              {getStatusIcon(systemData?.system?.disk?.percent || 0)}
              <span className={`text-lg font-bold ${getStatusColor(systemData?.system?.disk?.percent || 0)}`}>
                {systemData?.system?.disk?.percent || 0}%
              </span>
            </div>
            <div className="text-xs text-gray-500">
              {getStatusText(systemData?.system?.disk?.percent || 0)}
            </div>
          </div>
        </div>

        {/* 네트워크 상태 */}
        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center space-x-3">
            <Network className="h-5 w-5 text-gray-600" />
            <div>
              <span className="text-sm font-medium text-gray-900">네트워크</span>
              <div className="text-xs text-gray-500">
                송신/수신
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm font-medium text-gray-900">
              {formatBytes(systemData?.system?.network?.bytes_sent || 0)}
            </div>
            <div className="text-xs text-gray-500">
              {formatBytes(systemData?.system?.network?.bytes_recv || 0)}
            </div>
          </div>
        </div>
      </div>

      {/* 서비스 상태 */}
      <div className="mt-6">
        <h3 className="text-sm font-medium text-gray-900 mb-3">서비스 상태</h3>
        <div className="space-y-2">
          <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
            <span className="text-sm text-gray-600">데이터베이스</span>
            <div className="flex items-center space-x-2">
              {systemData?.services?.database === 'healthy' ? (
                <CheckCircle className="h-4 w-4 text-green-600" />
              ) : (
                <AlertTriangle className="h-4 w-4 text-red-600" />
              )}
              <span className={`text-sm font-medium ${
                systemData?.services?.database === 'healthy' ? 'text-green-600' : 'text-red-600'
              }`}>
                {systemData?.services?.database === 'healthy' ? '정상' : '오류'}
              </span>
            </div>
          </div>
          
          <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
            <span className="text-sm text-gray-600">애플리케이션</span>
            <div className="flex items-center space-x-2">
              {systemData?.services?.application === 'running' ? (
                <CheckCircle className="h-4 w-4 text-green-600" />
              ) : (
                <AlertTriangle className="h-4 w-4 text-red-600" />
              )}
              <span className={`text-sm font-medium ${
                systemData?.services?.application === 'running' ? 'text-green-600' : 'text-red-600'
              }`}>
                {systemData?.services?.application === 'running' ? '실행중' : '중지됨'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 성능 추이 */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h3 className="text-sm font-medium text-blue-900 mb-2">성능 추이</h3>
        <div className="grid grid-cols-3 gap-2 text-xs">
          <div className="text-center">
            <div className="font-medium text-gray-900">CPU</div>
            <div className={`flex items-center justify-center space-x-1 ${
              (systemData?.system?.cpu_percent || 0) > 80 ? 'text-red-600' : 'text-green-600'
            }`}>
              {(systemData?.system?.cpu_percent || 0) > 80 ? (
                <TrendingUp className="h-3 w-3" />
              ) : (
                <TrendingDown className="h-3 w-3" />
              )}
              <span>{(systemData?.system?.cpu_percent || 0) > 80 ? '증가' : '안정'}</span>
            </div>
          </div>
          <div className="text-center">
            <div className="font-medium text-gray-900">메모리</div>
            <div className={`flex items-center justify-center space-x-1 ${
              (systemData?.system?.memory?.percent || 0) > 80 ? 'text-red-600' : 'text-green-600'
            }`}>
              {(systemData?.system?.memory?.percent || 0) > 80 ? (
                <TrendingUp className="h-3 w-3" />
              ) : (
                <TrendingDown className="h-3 w-3" />
              )}
              <span>{(systemData?.system?.memory?.percent || 0) > 80 ? '증가' : '안정'}</span>
            </div>
          </div>
          <div className="text-center">
            <div className="font-medium text-gray-900">디스크</div>
            <div className={`flex items-center justify-center space-x-1 ${
              (systemData?.system?.disk?.percent || 0) > 80 ? 'text-red-600' : 'text-green-600'
            }`}>
              {(systemData?.system?.disk?.percent || 0) > 80 ? (
                <TrendingUp className="h-3 w-3" />
              ) : (
                <TrendingDown className="h-3 w-3" />
              )}
              <span>{(systemData?.system?.disk?.percent || 0) > 80 ? '증가' : '안정'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* 마지막 업데이트 */}
      <div className="mt-4 text-xs text-gray-500 text-center">
        마지막 업데이트: {systemData?.timestamp ? 
          new Date(systemData.timestamp).toLocaleTimeString('ko-KR') : 
          '알 수 없음'
        }
      </div>
    </div>
  );
} 
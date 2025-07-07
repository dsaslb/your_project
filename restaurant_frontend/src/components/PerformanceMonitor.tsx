"use client";

import { usePerformanceMonitor } from "@/hooks/useOptimization";
import { Activity, Database, Zap, AlertTriangle, CheckCircle, Clock } from "lucide-react";

interface PerformanceMonitorProps {
  className?: string;
}

export default function PerformanceMonitor({ className = "" }: PerformanceMonitorProps) {
  const { data: performanceData, isLoading, error } = usePerformanceMonitor();

  if (isLoading) {
    return (
      <div className={`bg-white rounded-lg shadow-sm border p-6 ${className}`}>
        <h2 className="text-xl font-semibold text-gray-900 mb-6">성능 모니터링</h2>
        <div className="space-y-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="animate-pulse">
              <div className="h-8 bg-gray-200 rounded"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-white rounded-lg shadow-sm border p-6 ${className}`}>
        <h2 className="text-xl font-semibold text-gray-900 mb-6">성능 모니터링</h2>
        <div className="flex items-center space-x-2 text-red-600">
          <AlertTriangle className="h-5 w-5" />
          <span>성능 데이터를 불러올 수 없습니다</span>
        </div>
      </div>
    );
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
      case 'error':
        return <AlertTriangle className="h-4 w-4 text-red-600" />;
      default:
        return <Clock className="h-4 w-4 text-gray-600" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'healthy':
        return '정상';
      case 'warning':
        return '주의';
      case 'error':
        return '오류';
      default:
        return '알 수 없음';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-green-600';
      case 'warning':
        return 'text-yellow-600';
      case 'error':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className={`bg-white rounded-lg shadow-sm border p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">성능 모니터링</h2>
        <div className="flex items-center space-x-2 text-xs text-gray-500">
          <Clock className="h-3 w-3" />
          <span>실시간</span>
        </div>
      </div>
      
      <div className="space-y-4">
        {/* 데이터베이스 상태 */}
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center space-x-3">
            <Database className="h-5 w-5 text-gray-600" />
            <div>
              <span className="text-sm font-medium text-gray-900">데이터베이스</span>
              <div className="text-xs text-gray-500">
                연결 풀: {performanceData?.data?.database?.connection_pool_size || 0}
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {getStatusIcon(performanceData?.data?.database?.status || 'unknown')}
            <span className={`text-sm font-medium ${getStatusColor(performanceData?.data?.database?.status || 'unknown')}`}>
              {getStatusText(performanceData?.data?.database?.status || 'unknown')}
            </span>
          </div>
        </div>

        {/* 캐시 상태 */}
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center space-x-3">
            <Zap className="h-5 w-5 text-gray-600" />
            <div>
              <span className="text-sm font-medium text-gray-900">캐시</span>
              <div className="text-xs text-gray-500">
                항목: {performanceData?.data?.cache?.items_count || 0}개
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {getStatusIcon(performanceData?.data?.cache?.status || 'unknown')}
            <span className={`text-sm font-medium ${getStatusColor(performanceData?.data?.cache?.status || 'unknown')}`}>
              {getStatusText(performanceData?.data?.cache?.status || 'unknown')}
            </span>
          </div>
        </div>

        {/* 메모리 사용량 */}
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center space-x-3">
            <Activity className="h-5 w-5 text-gray-600" />
            <div>
              <span className="text-sm font-medium text-gray-900">메모리 사용량</span>
              <div className="text-xs text-gray-500">
                캐시 메모리
              </div>
            </div>
          </div>
          <div className="text-right">
            <span className="text-sm font-medium text-gray-900">
              {performanceData?.data?.cache?.memory_usage_kb || 0} KB
            </span>
            <div className="text-xs text-gray-500">
              {performanceData?.data?.cache?.memory_usage_kb > 1000 ? '높음' : '정상'}
            </div>
          </div>
        </div>

        {/* 시스템 정보 */}
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center space-x-3">
            <Activity className="h-5 w-5 text-gray-600" />
            <div>
              <span className="text-sm font-medium text-gray-900">시스템</span>
              <div className="text-xs text-gray-500">
                업타임: {performanceData?.data?.system?.uptime || '알 수 없음'}
              </div>
            </div>
          </div>
          <div className="text-right">
            <span className="text-sm font-medium text-gray-900">
              {performanceData?.data?.system?.timestamp ? 
                new Date(performanceData.data.system.timestamp).toLocaleTimeString('ko-KR') : 
                '알 수 없음'
              }
            </span>
          </div>
        </div>
      </div>

      {/* 성능 권장사항 */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h3 className="text-sm font-medium text-blue-900 mb-2">성능 권장사항</h3>
        <ul className="text-xs text-blue-800 space-y-1">
          {performanceData?.data?.cache?.memory_usage_kb > 1000 && (
            <li>• 캐시 메모리 사용량이 높습니다. 불필요한 캐시를 정리하세요.</li>
          )}
          {performanceData?.data?.cache?.status === 'warning' && (
            <li>• 캐시 상태에 주의가 필요합니다. 시스템을 모니터링하세요.</li>
          )}
          {performanceData?.data?.database?.status === 'error' && (
            <li>• 데이터베이스 연결에 문제가 있습니다. 즉시 확인하세요.</li>
          )}
          {performanceData?.data?.database?.status === 'healthy' && 
           performanceData?.data?.cache?.status === 'healthy' && (
            <li>• 모든 시스템이 정상적으로 작동하고 있습니다.</li>
          )}
        </ul>
      </div>
    </div>
  );
} 
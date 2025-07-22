"use client";

import React, { useEffect, useState } from 'react';
import { usePerformanceOptimization } from '../utils/performance';

interface SystemMetrics {
  cpu_percent: number;
  memory_percent: number;
  memory_used_gb: number;
  memory_total_gb: number;
  disk_usage_percent: number;
  disk_used_gb: number;
  disk_total_gb: number;
  active_connections: number;
  load_average: number[];
}

interface ApplicationMetrics {
  requests_per_minute: number;
  error_rate: number;
  avg_response_time: number;
  active_endpoints: number;
}

interface PerformanceDashboardProps {
  title?: string;
}

export const PerformanceDashboard: React.FC<PerformanceDashboardProps> = ({ 
  title = "성능 모니터링 대시보드" 
}) => {
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null);
  const [appMetrics, setAppMetrics] = useState<ApplicationMetrics | null>(null);
  const [frontendMetrics, setFrontendMetrics] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const { getPerformanceReport } = usePerformanceOptimization();

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        // 시스템 메트릭 조회
        const systemResponse = await fetch('/api/monitoring/system-metrics');
        if (systemResponse.ok) {
          const systemData = await systemResponse.json();
          setSystemMetrics(systemData);
        }

        // 애플리케이션 메트릭 조회
        const appResponse = await fetch('/api/monitoring/application-metrics');
        if (appResponse.ok) {
          const appData = await appResponse.json();
          setAppMetrics(appData);
        }

        // 프론트엔드 메트릭 조회
        const frontendReport = getPerformanceReport();
        setFrontendMetrics(frontendReport);

        setIsLoading(false);
      } catch (error) {
        console.error('메트릭 조회 실패:', error);
        setIsLoading(false);
      }
    };

    fetchMetrics();
    
    // 30초마다 메트릭 업데이트
    const interval = setInterval(fetchMetrics, 30000);
    
    return () => clearInterval(interval);
  }, [getPerformanceReport]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'critical': return 'text-red-600 bg-red-100';
      case 'warning': return 'text-yellow-600 bg-yellow-100';
      case 'optimal':
      case 'healthy': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'critical': return '🔴';
      case 'warning': return '🟡';
      case 'optimal':
      case 'healthy': return '🟢';
      default: return '⚪';
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
          <p className="text-sm text-gray-500">
            마지막 업데이트: {new Date().toLocaleString()}
          </p>
        </div>
        <div className="flex space-x-2">
          <button 
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            새로고침
          </button>
        </div>
      </div>

      {/* 시스템 성능 */}
      {systemMetrics && (
        <div className="mb-8">
          <h3 className="text-lg font-semibold mb-4">시스템 성능</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* CPU 사용률 */}
            <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg p-4 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-100 text-sm font-medium">CPU 사용률</p>
                  <p className="text-3xl font-bold">{systemMetrics.cpu_percent.toFixed(1)}%</p>
                </div>
                <div className="bg-blue-400 rounded-full p-3">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                  </svg>
                </div>
              </div>
              <div className="mt-2">
                <div className="w-full bg-blue-400 rounded-full h-2">
                  <div 
                    className="bg-white rounded-full h-2" 
                    style={{ width: `${systemMetrics.cpu_percent}%` }}
                  ></div>
                </div>
              </div>
            </div>

            {/* 메모리 사용률 */}
            <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg p-4 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-green-100 text-sm font-medium">메모리 사용률</p>
                  <p className="text-3xl font-bold">{systemMetrics.memory_percent.toFixed(1)}%</p>
                  <p className="text-sm text-green-100">
                    {systemMetrics.memory_used_gb.toFixed(1)}GB / {systemMetrics.memory_total_gb.toFixed(1)}GB
                  </p>
                </div>
                <div className="bg-green-400 rounded-full p-3">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
                  </svg>
                </div>
              </div>
              <div className="mt-2">
                <div className="w-full bg-green-400 rounded-full h-2">
                  <div 
                    className="bg-white rounded-full h-2" 
                    style={{ width: `${systemMetrics.memory_percent}%` }}
                  ></div>
                </div>
              </div>
            </div>

            {/* 디스크 사용률 */}
            <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg p-4 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-purple-100 text-sm font-medium">디스크 사용률</p>
                  <p className="text-3xl font-bold">{systemMetrics.disk_usage_percent.toFixed(1)}%</p>
                  <p className="text-sm text-purple-100">
                    {systemMetrics.disk_used_gb.toFixed(1)}GB / {systemMetrics.disk_total_gb.toFixed(1)}GB
                  </p>
                </div>
                <div className="bg-purple-400 rounded-full p-3">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
                  </svg>
                </div>
              </div>
              <div className="mt-2">
                <div className="w-full bg-purple-400 rounded-full h-2">
                  <div 
                    className="bg-white rounded-full h-2" 
                    style={{ width: `${systemMetrics.disk_usage_percent}%` }}
                  ></div>
                </div>
              </div>
            </div>

            {/* 활성 연결 */}
            <div className="bg-gradient-to-r from-orange-500 to-orange-600 rounded-lg p-4 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-orange-100 text-sm font-medium">활성 연결</p>
                  <p className="text-3xl font-bold">{systemMetrics.active_connections}</p>
                </div>
                <div className="bg-orange-400 rounded-full p-3">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 애플리케이션 성능 */}
      {appMetrics && (
        <div className="mb-8">
          <h3 className="text-lg font-semibold mb-4">애플리케이션 성능</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* 요청/분 */}
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">요청/분</p>
                  <p className="text-2xl font-bold text-gray-900">{appMetrics.requests_per_minute}</p>
                </div>
                <div className="text-blue-500">
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
              </div>
            </div>

            {/* 에러율 */}
            <div className="bg-red-50 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">에러율</p>
                  <p className="text-2xl font-bold text-gray-900">{(appMetrics.error_rate * 100).toFixed(2)}%</p>
                </div>
                <div className="text-red-500">
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
            </div>

            {/* 평균 응답시간 */}
            <div className="bg-green-50 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">평균 응답시간</p>
                  <p className="text-2xl font-bold text-gray-900">{appMetrics.avg_response_time.toFixed(2)}ms</p>
                </div>
                <div className="text-green-500">
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
            </div>

            {/* 활성 엔드포인트 */}
            <div className="bg-purple-50 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">활성 엔드포인트</p>
                  <p className="text-2xl font-bold text-gray-900">{appMetrics.active_endpoints}</p>
                </div>
                <div className="text-purple-500">
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 프론트엔드 성능 */}
      {frontendMetrics && (
        <div className="mb-8">
          <h3 className="text-lg font-semibold mb-4">프론트엔드 성능</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* 메모리 사용량 */}
            <div className="bg-indigo-50 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">메모리 사용량</p>
                  <p className="text-2xl font-bold text-gray-900">{frontendMetrics.memoryUsage.formatted}</p>
                </div>
                <div className="text-indigo-500">
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
                  </svg>
                </div>
              </div>
            </div>

            {/* 렌더링 성능 */}
            <div className="bg-yellow-50 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">평균 렌더링 시간</p>
                  <p className="text-2xl font-bold text-gray-900">{frontendMetrics.renderPerformance.formatted}</p>
                </div>
                <div className="text-yellow-500">
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
            </div>

            {/* 캐시 크기 */}
            <div className="bg-pink-50 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">캐시 크기</p>
                  <p className="text-2xl font-bold text-gray-900">{frontendMetrics.cache.size}</p>
                </div>
                <div className="text-pink-500">
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                  </svg>
                </div>
              </div>
            </div>

            {/* 캐시 히트율 */}
            <div className="bg-teal-50 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">캐시 히트율</p>
                  <p className="text-2xl font-bold text-gray-900">{(frontendMetrics.cache.hitRate * 100).toFixed(1)}%</p>
                </div>
                <div className="text-teal-500">
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 전체 상태 */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-4">전체 시스템 상태</h3>
        <div className="flex items-center space-x-4">
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor('healthy')}`}>
            {getStatusIcon('healthy')} 시스템: 정상
          </div>
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor('optimal')}`}>
            {getStatusIcon('optimal')} 애플리케이션: 최적
          </div>
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor('optimal')}`}>
            {getStatusIcon('optimal')} 프론트엔드: 최적
          </div>
        </div>
      </div>
    </div>
  );
}; 
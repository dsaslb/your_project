import React, { useEffect, useState } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

interface DashboardStats {
  active_users: number;
  orders: number;
  revenue: number;
  timestamp: string;
}

interface RealtimeDashboardProps {
  title?: string;
}

export const RealtimeDashboard: React.FC<RealtimeDashboardProps> = ({ 
  title = "실시간 대시보드" 
}) => {
  const [stats, setStats] = useState<DashboardStats>({
    active_users: 0,
    orders: 0,
    revenue: 0,
    timestamp: new Date().toISOString()
  });
  const [isConnected, setIsConnected] = useState(false);
  
  const { status, notifications } = useWebSocket({
    userId: 'dashboard_user',
    autoConnect: true
  });

  useEffect(() => {
    setIsConnected(status.connected);
  }, [status.connected]);

  useEffect(() => {
    // 실시간 데이터 업데이트를 위한 더미 데이터 (실제로는 WebSocket 메시지로 처리)
    const interval = setInterval(() => {
      setStats(prev => ({
        active_users: Math.floor(Math.random() * 100) + 50,
        orders: Math.floor(Math.random() * 50) + 10,
        revenue: Math.floor(Math.random() * 1000000) + 500000,
        timestamp: new Date().toISOString()
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('ko-KR').format(num);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW'
    }).format(amount);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
          <p className="text-sm text-gray-500">
            마지막 업데이트: {new Date(stats.timestamp).toLocaleString()}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-sm text-gray-500">
            {isConnected ? '실시간 연결됨' : '연결 중...'}
          </span>
        </div>
      </div>

      {/* 통계 카드들 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        {/* 활성 사용자 */}
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm font-medium">활성 사용자</p>
              <p className="text-3xl font-bold">{formatNumber(stats.active_users)}</p>
            </div>
            <div className="bg-blue-400 rounded-full p-3">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
              </svg>
            </div>
          </div>
        </div>

        {/* 주문 수 */}
        <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm font-medium">오늘 주문</p>
              <p className="text-3xl font-bold">{formatNumber(stats.orders)}</p>
            </div>
            <div className="bg-green-400 rounded-full p-3">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
              </svg>
            </div>
          </div>
        </div>

        {/* 매출 */}
        <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm font-medium">오늘 매출</p>
              <p className="text-3xl font-bold">{formatCurrency(stats.revenue)}</p>
            </div>
            <div className="bg-purple-400 rounded-full p-3">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* 실시간 업데이트 표시 */}
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-sm text-gray-600">실시간 데이터 업데이트 중...</span>
        </div>
      </div>

      {/* 연결 상태 상세 정보 */}
      {!isConnected && (
        <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-yellow-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <span className="text-sm text-yellow-800">
              실시간 연결이 끊어졌습니다. 데이터가 최신 상태가 아닐 수 있습니다.
            </span>
          </div>
        </div>
      )}
    </div>
  );
}; 
"use client";

import { useCachedStats } from "@/hooks/useOptimization";
import { Users, ShoppingCart, Calendar, Activity, Zap, TrendingUp } from "lucide-react";

interface OptimizedStatsProps {
  className?: string;
}

export default function OptimizedStats({ className = "" }: OptimizedStatsProps) {
  const { data: cachedStats, isLoading, error } = useCachedStats();

  if (isLoading) {
    return (
      <div className={`bg-white rounded-lg shadow-sm border p-6 ${className}`}>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">시스템 통계</h2>
        </div>
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
        <h2 className="text-xl font-semibold text-gray-900 mb-6">시스템 통계</h2>
        <div className="text-center text-red-600">
          통계 데이터를 불러올 수 없습니다
        </div>
      </div>
    );
  }

  const stats = [
    {
      title: "전체 사용자",
      value: cachedStats?.data?.total_users || 0,
      icon: <Users className="h-6 w-6 text-blue-600" />,
      color: "bg-blue-50",
      textColor: "text-blue-600",
      description: "등록된 사용자 수"
    },
    {
      title: "전체 주문",
      value: cachedStats?.data?.total_orders || 0,
      icon: <ShoppingCart className="h-6 w-6 text-green-600" />,
      color: "bg-green-50",
      textColor: "text-green-600",
      description: "처리된 주문 수"
    },
    {
      title: "전체 스케줄",
      value: cachedStats?.data?.total_schedules || 0,
      icon: <Calendar className="h-6 w-6 text-purple-600" />,
      color: "bg-purple-50",
      textColor: "text-purple-600",
      description: "등록된 스케줄 수"
    },
    {
      title: "출근 기록",
      value: cachedStats?.data?.total_attendance || 0,
      icon: <Activity className="h-6 w-6 text-orange-600" />,
      color: "bg-orange-50",
      textColor: "text-orange-600",
      description: "출근 기록 수"
    }
  ];

  return (
    <div className={`bg-white rounded-lg shadow-sm border p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">시스템 통계</h2>
        {cachedStats?.data?.cached && (
          <div className="flex items-center space-x-1 text-xs text-green-600">
            <Zap className="h-3 w-3" />
            <span>캐시됨</span>
          </div>
        )}
      </div>
      
      <div className="space-y-4">
        {stats.map((stat, index) => (
          <div key={index} className={`flex items-center justify-between p-4 ${stat.color} rounded-lg`}>
            <div className="flex items-center space-x-3">
              {stat.icon}
              <div>
                <p className="text-sm text-gray-600">{stat.title}</p>
                <p className="text-xs text-gray-500">{stat.description}</p>
              </div>
            </div>
            <div className="text-right">
              <p className={`text-2xl font-bold ${stat.textColor}`}>
                {stat.value.toLocaleString()}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* 캐시 정보 */}
      {cachedStats?.data?.cached && (
        <div className="mt-4 p-3 bg-green-50 rounded-lg">
          <div className="flex items-center space-x-2 text-xs text-green-700">
            <TrendingUp className="h-3 w-3" />
            <span>캐시된 데이터로 빠른 응답</span>
          </div>
          <div className="text-xs text-green-600 mt-1">
            마지막 업데이트: {cachedStats.data.cache_time ? 
              new Date(cachedStats.data.cache_time).toLocaleTimeString('ko-KR') : 
              '알 수 없음'
            }
          </div>
        </div>
      )}

      {/* 성능 지표 */}
      <div className="mt-4 grid grid-cols-2 gap-2 text-xs">
        <div className="text-center p-2 bg-gray-50 rounded">
          <div className="font-medium text-gray-900">응답 시간</div>
          <div className="text-green-600">최적화됨</div>
        </div>
        <div className="text-center p-2 bg-gray-50 rounded">
          <div className="font-medium text-gray-900">데이터 정확도</div>
          <div className="text-blue-600">실시간</div>
        </div>
      </div>
    </div>
  );
} 
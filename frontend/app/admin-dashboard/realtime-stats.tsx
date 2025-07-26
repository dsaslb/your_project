'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface RealtimeStatsProps {
  className?: string;
}

interface BrandStats {
  brand_id: number;
  brand_name: string;
  employee_count: number;
  manager_count: number;
  store_count: number;
  total_count: number;
  created_at?: string;
  status: string;
}

interface RealtimeData {
  brand_stats: BrandStats[];
  summary: {
    total_brands: number;
    total_employees: number;
    total_managers: number;
    total_stores: number;
    total_users: number;
  };
  realtime: {
    recent_changes: Array<{
      type: string;
      item_name: string;
      brand_name: string;
      time: string;
    }>;
    last_updated: string;
    update_interval: string;
  };
  source: string;
  timestamp: string;
}

export default function RealtimeStats({ className }: RealtimeStatsProps) {
  const [data, setData] = useState<RealtimeData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const loadRealtimeData = async () => {
    try {
      const response = await fetch('/api/admin/brand_stats/realtime');
      if (!response.ok) {
        throw new Error('실시간 데이터 로드 실패');
      }
      const realtimeData = await response.json();
      setData(realtimeData);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRealtimeData();

    if (autoRefresh) {
      const interval = setInterval(loadRealtimeData, 30000); // 30초마다 업데이트
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  if (loading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>실시간 브랜드 통계</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-4">데이터 로딩 중...</div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>실시간 브랜드 통계</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-red-500">오류: {error}</div>
          <button
            onClick={loadRealtimeData}
            className="mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            다시 시도
          </button>
        </CardContent>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>실시간 브랜드 통계</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-4">데이터가 없습니다.</div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle>실시간 브랜드 통계</CardTitle>
          <div className="flex gap-2 items-center">
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`px-2 py-1 text-xs border rounded ${
                autoRefresh ? 'bg-green-500 text-white' : 'bg-gray-200'
              }`}
            >
              {autoRefresh ? '자동 ON' : '자동 OFF'}
            </button>
            <button
              onClick={loadRealtimeData}
              className="px-2 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              새로고침
            </button>
          </div>
        </div>
        <div className="text-sm text-gray-500">
          마지막 업데이트: {new Date(data.timestamp).toLocaleString()}
        </div>
      </CardHeader>
      <CardContent>
        {/* 요약 통계 */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{data.summary.total_brands}</div>
            <div className="text-sm text-gray-600">총 브랜드</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{data.summary.total_stores}</div>
            <div className="text-sm text-gray-600">총 매장</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">{data.summary.total_employees}</div>
            <div className="text-sm text-gray-600">총 직원</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">{data.summary.total_managers}</div>
            <div className="text-sm text-gray-600">총 매니저</div>
          </div>
        </div>

        {/* 브랜드별 통계 */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3">브랜드별 통계</h3>
          <div className="space-y-2">
            {data.brand_stats.map((brand) => (
              <div
                key={brand.brand_id}
                className="flex justify-between items-center p-3 bg-gray-50 rounded-lg"
              >
                <div>
                  <div className="font-medium">{brand.brand_name}</div>
                  <div className="text-sm text-gray-600">
                    매장: {brand.store_count} | 직원: {brand.employee_count} | 매니저: {brand.manager_count}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-blue-600">{brand.total_count}</div>
                  <div className="text-xs text-gray-500">총 인원</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 최근 변경사항 */}
        {data.realtime.recent_changes.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold mb-3">최근 변경사항</h3>
            <div className="space-y-2 max-h-40 overflow-y-auto">
              {data.realtime.recent_changes.map((change, index) => (
                <div
                  key={index}
                  className="flex items-center gap-2 p-2 bg-yellow-50 rounded text-sm"
                >
                  <span className="text-yellow-600">🔄</span>
                  <span className="font-medium">{change.type === 'user' ? '직원' : '매장'}</span>
                  <span className="text-gray-600">{change.item_name}</span>
                  <span className="text-gray-500">({change.brand_name})</span>
                  <span className="text-xs text-gray-400 ml-auto">
                    {new Date(change.time).toLocaleString()}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 데이터 소스 정보 */}
        <div className="mt-4 pt-4 border-t text-xs text-gray-500">
          <div>데이터 소스: {data.source}</div>
          <div>업데이트 간격: {data.realtime.update_interval}</div>
        </div>
      </CardContent>
    </Card>
  );
} 
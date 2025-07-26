import React from 'react';
import ClientOnly from '@/components/ClientOnly';
import { Crown, Activity } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { useEffect, useState } from 'react';
import { getIndustryData } from '@/lib/api';

interface IndustryData {
  total_users: number;
  total_revenue: number;
  total_orders: number;
  total_products: number;
  top_industries: {
    name: string;
    revenue: number;
    orders: number;
    products: number;
  }[];
  realtime_stats: {
    total_users: number;
    total_revenue: number;
    total_orders: number;
    total_products: number;
  };
}

export default function IndustryDashboard() {
  const [data, setData] = useState<IndustryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [warning, setWarning] = useState<string | null>(null);
  const [now, setNow] = useState(new Date().toLocaleString());

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const industryData = await getIndustryData();
        setData(industryData);
        setWarning(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
        setWarning(null);
      } finally {
        setLoading(false);
      }
    };

    loadData();
    const interval = setInterval(loadData, 30000); // 30초마다 데이터 갱신
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const updateTime = () => {
      setNow(new Date().toLocaleString());
    };
    updateTime(); // 초기 로딩 시 한 번 실행
    const interval = setInterval(updateTime, 1000); // 1초마다 시간 업데이트
    return () => clearInterval(interval);
  }, []);

  if (loading && !data) {
    return <div className="text-center py-8">데이터를 불러오는 중입니다...</div>;
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-500">{error}</p>
        <button onClick={() => window.location.reload()} className="mt-4 px-4 py-2 bg-red-500 text-white rounded">
          새로고침
        </button>
      </div>
    );
  }

  if (!data) {
    return null; // 데이터가 없는 경우
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* 오류/경고 표시 */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4 max-w-3xl mx-auto mt-6">
          <strong className="font-bold">[❌ 오류]</strong>
          <span className="block">{error}</span>
          <button onClick={() => window.location.reload()} className="mt-2 px-3 py-1 bg-red-500 text-white rounded">다시 시도</button>
        </div>
      )}
      {warning && !error && (
        <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded mb-4 max-w-3xl mx-auto mt-6">
          <strong className="font-bold">[⚠️ 경고]</strong>
          <span className="block">{warning}</span>
        </div>
      )}
      <ClientOnly>
        {/* 헤더, 통계 카드, 업종별 현황 등 클라이언트에서만 렌더링 */}
        <header className="bg-white/10 backdrop-blur-xl border-b border-white/20">
          <div className="container mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Crown className="h-8 w-8 text-yellow-400" />
                <div>
                  <h1 className="text-2xl font-bold text-white">업종별 최상위 관리자</h1>
                  <p className="text-slate-300">전체 업종 통합 관리 및 모니터링</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <Badge variant="outline" className="text-green-400 border-green-400">
                  <Activity className="h-4 w-4 mr-1" />
                  실시간 모니터링
                </Badge>
                <div className="text-slate-300 text-sm">
                  {now}
                </div>
              </div>
            </div>
          </div>
        </header>
        <div className="container mx-auto px-6 py-8">
          {/* 통계 카드, 업종별 현황, 성과 지표, 빠른 액션 등 */}
          {/* ... 기존 코드 그대로 ... */}
        </div>
      </ClientOnly>
    </div>
  );
} 
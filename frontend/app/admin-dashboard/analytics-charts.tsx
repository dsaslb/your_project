'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface AnalyticsChartsProps {
  className?: string;
}

interface AnalyticsData {
  growth_analysis: Array<{
    brand_id: number;
    brand_name: string;
    current_count: number;
    previous_count: number;
    growth_rate: number;
  }>;
  monthly_trends: Record<string, Array<{
    month: string;
    new_users: number;
  }>>;
  avg_employees_per_store: Array<{
    brand_id: number;
    brand_name: string;
    store_count: number;
    employee_count: number;
    avg_employees_per_store: number;
  }>;
  activity_scores: Array<{
    brand_id: number;
    brand_name: string;
    recent_users: number;
    recent_stores: number;
    activity_score: number;
  }>;
  analysis_date: string;
  source: string;
}

export default function AnalyticsCharts({ className }: AnalyticsChartsProps) {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadAnalyticsData = async () => {
      try {
        const response = await fetch('/api/admin/brand_stats/analytics');
        if (!response.ok) {
          throw new Error('분석 데이터 로드 실패');
        }
        const analyticsData = await response.json();
        setData(analyticsData);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : '알 수 없는 오류');
      } finally {
        setLoading(false);
      }
    };

    loadAnalyticsData();
  }, []);

  if (loading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>브랜드 통계 분석</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-4">분석 데이터 로딩 중...</div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>브랜드 통계 분석</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-red-500">오류: {error}</div>
        </CardContent>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>브랜드 통계 분석</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-4">분석 데이터가 없습니다.</div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className={className}>
      {/* 성장률 분석 */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>브랜드별 성장률 (최근 30일)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {data.growth_analysis.map((brand) => (
              <div key={brand.brand_id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <div className="font-medium">{brand.brand_name}</div>
                  <div className="text-sm text-gray-600">
                    현재: {brand.current_count}명 | 이전: {brand.previous_count}명
                  </div>
                </div>
                <div className="text-right">
                  <div className={`text-lg font-bold ${
                    brand.growth_rate > 0 ? 'text-green-600' : 
                    brand.growth_rate < 0 ? 'text-red-600' : 'text-gray-600'
                  }`}>
                    {brand.growth_rate > 0 ? '+' : ''}{brand.growth_rate}%
                  </div>
                  <div className="text-xs text-gray-500">성장률</div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 평균 매장당 직원 수 */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>평균 매장당 직원 수</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {data.avg_employees_per_store.map((brand) => (
              <div key={brand.brand_id} className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
                <div>
                  <div className="font-medium">{brand.brand_name}</div>
                  <div className="text-sm text-gray-600">
                    매장: {brand.store_count}개 | 직원: {brand.employee_count}명
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-blue-600">
                    {brand.avg_employees_per_store}명
                  </div>
                  <div className="text-xs text-gray-500">평균</div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 활성도 점수 */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>브랜드 활성도 점수 (최근 7일)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {data.activity_scores.map((brand) => (
              <div key={brand.brand_id} className="flex items-center justify-between p-4 bg-purple-50 rounded-lg">
                <div>
                  <div className="font-medium">{brand.brand_name}</div>
                  <div className="text-sm text-gray-600">
                    신규 직원: {brand.recent_users}명 | 신규 매장: {brand.recent_stores}개
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-purple-600">
                    {brand.activity_score}
                  </div>
                  <div className="text-xs text-gray-500">활성도</div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 월별 트렌드 */}
      <Card>
        <CardHeader>
          <CardTitle>월별 사용자 등록 추이 (최근 6개월)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Object.entries(data.monthly_trends).map(([brandName, trends]) => (
              <div key={brandName} className="p-4 bg-green-50 rounded-lg">
                <div className="font-medium mb-2">{brandName}</div>
                <div className="flex gap-2 overflow-x-auto">
                  {trends.map((trend, index) => (
                    <div key={index} className="flex-shrink-0 text-center">
                      <div className="text-sm font-medium">{trend.month}</div>
                      <div className="text-lg font-bold text-green-600">{trend.new_users}</div>
                      <div className="text-xs text-gray-500">명</div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 분석 정보 */}
      <div className="mt-4 text-xs text-gray-500">
        <div>분석 기준일: {new Date(data.analysis_date).toLocaleString()}</div>
        <div>데이터 소스: {data.source}</div>
      </div>
    </div>
  );
} 
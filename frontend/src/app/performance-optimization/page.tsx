'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { toast } from 'sonner';
import { 
  Zap, 
  Database, 
  Cpu, 
  HardDrive, 
  Activity, 
  TrendingUp, 
  TrendingDown,
  RefreshCw,
  Settings,
  BarChart3,
  AlertTriangle,
  CheckCircle,
  Clock,
  Gauge
} from 'lucide-react';

interface CacheStats {
  hits: { l1: number; l2: number; l3: number };
  misses: { l1: number; l2: number; l3: number };
  writes: { l1: number; l2: number; l3: number };
  overall_hit_rate: number;
  level_hit_rates: { l1: number; l2: number; l3: number };
  cache_status: { l1_enabled: boolean; l2_enabled: boolean; l3_enabled: boolean };
}

interface QueryStats {
  total_queries: number;
  avg_execution_time: number;
  max_execution_time: number;
  slow_queries_count: number;
  slow_query_percentage: number;
  index_recommendations_count: number;
}

interface PoolStats {
  pool_size: number;
  checked_in: number;
  checked_out: number;
  overflow: number;
  total_connections: number;
}

interface PerformanceOverview {
  performance_score: number;
  cache_stats: CacheStats;
  query_stats: QueryStats;
  pool_stats: PoolStats;
  recommendations: string[];
  last_updated: string;
}

export default function PerformanceOptimizationPage() {
  const [overview, setOverview] = useState<PerformanceOverview | null>(null);
  const [cacheStats, setCacheStats] = useState<CacheStats | null>(null);
  const [queryAnalysis, setQueryAnalysis] = useState<any>(null);
  const [slowQueries, setSlowQueries] = useState<any[]>([]);
  const [poolStats, setPoolStats] = useState<PoolStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // 성능 개요 로드
      const overviewResponse = await fetch('/api/admin/performance/overview');
      const overviewData = await overviewResponse.json();
      if (overviewData.status === 'success') {
        setOverview(overviewData.data);
      }

      // 캐시 통계 로드
      const cacheResponse = await fetch('/api/admin/performance/cache/stats');
      const cacheData = await cacheResponse.json();
      if (cacheData.status === 'success') {
        setCacheStats(cacheData.data);
      }

      // 쿼리 분석 로드
      const queryResponse = await fetch('/api/admin/performance/queries/analysis');
      const queryData = await queryResponse.json();
      if (queryData.status === 'success') {
        setQueryAnalysis(queryData.data);
      }

      // 느린 쿼리 로드
      const slowResponse = await fetch('/api/admin/performance/queries/slow?limit=10');
      const slowData = await slowResponse.json();
      if (slowData.status === 'success') {
        setSlowQueries(slowData.data);
      }

      // 연결 풀 통계 로드
      const poolResponse = await fetch('/api/admin/performance/pool/stats');
      const poolData = await poolResponse.json();
      if (poolData.status === 'success') {
        setPoolStats(poolData.data);
      }

    } catch (error) {
      console.error('Failed to load performance data:', error);
      toast.error('데이터 로드에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const runOptimization = async () => {
    try {
      const response = await fetch('/api/admin/performance/optimize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          types: ['cache', 'queries', 'pool']
        }),
      });

      const data = await response.json();
      if (data.status === 'success') {
        toast.success('성능 최적화가 완료되었습니다.');
        loadData(); // 데이터 새로고침
      } else {
        toast.error('성능 최적화에 실패했습니다.');
      }
    } catch (error) {
      console.error('Failed to run optimization:', error);
      toast.error('성능 최적화에 실패했습니다.');
    }
  };

  const clearCache = async () => {
    try {
      const response = await fetch('/api/admin/performance/cache/clear', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();
      if (data.status === 'success') {
        toast.success('캐시가 삭제되었습니다.');
        loadData();
      } else {
        toast.error('캐시 삭제에 실패했습니다.');
      }
    } catch (error) {
      console.error('Failed to clear cache:', error);
      toast.error('캐시 삭제에 실패했습니다.');
    }
  };

  const getPerformanceColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getPerformanceIcon = (score: number) => {
    if (score >= 80) return <CheckCircle className="h-6 w-6 text-green-600" />;
    if (score >= 60) return <AlertTriangle className="h-6 w-6 text-yellow-600" />;
    return <AlertTriangle className="h-6 w-6 text-red-600" />;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">성능 최적화</h1>
        <div className="flex space-x-2">
          <Button onClick={loadData} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            새로고침
          </Button>
          <Button onClick={runOptimization}>
            <Zap className="h-4 w-4 mr-2" />
            최적화 실행
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">개요</TabsTrigger>
          <TabsTrigger value="cache">캐시</TabsTrigger>
          <TabsTrigger value="queries">쿼리</TabsTrigger>
          <TabsTrigger value="pool">연결 풀</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* 성능 점수 */}
          {overview && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  {getPerformanceIcon(overview.performance_score)}
                  <span>전체 성능 점수</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center space-x-4">
                  <div className="text-4xl font-bold">
                    <span className={getPerformanceColor(overview.performance_score)}>
                      {overview.performance_score}
                    </span>
                    <span className="text-2xl text-gray-500">/100</span>
                  </div>
                  <Progress value={overview.performance_score} className="flex-1" />
                </div>
                
                {overview.recommendations.length > 0 && (
                  <div className="mt-4">
                    <h4 className="font-medium mb-2">권장사항:</h4>
                    <ul className="space-y-1">
                      {overview.recommendations.map((rec, index) => (
                        <li key={index} className="text-sm text-gray-600 flex items-start">
                          <AlertTriangle className="h-4 w-4 mr-2 mt-0.5 text-yellow-500" />
                          {rec}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* 성능 지표 카드 */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">캐시 히트율</CardTitle>
                <HardDrive className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {cacheStats?.overall_hit_rate?.toFixed(1) || 0}%
                </div>
                <p className="text-xs text-muted-foreground">
                  전체 캐시 요청 중 히트율
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">평균 쿼리 시간</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {overview?.query_stats?.avg_execution_time?.toFixed(3) || 0}s
                </div>
                <p className="text-xs text-muted-foreground">
                  모든 쿼리의 평균 실행 시간
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">연결 풀 사용률</CardTitle>
                <Database className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {poolStats ? 
                    poolStats.total_connections > 0 ? 
                      ((poolStats.checked_out / poolStats.total_connections) * 100).toFixed(1) : 0 
                    : 0}%
                </div>
                <p className="text-xs text-muted-foreground">
                  활성 데이터베이스 연결 비율
                </p>
              </CardContent>
            </Card>
          </div>

          {/* 최근 업데이트 */}
          {overview && (
            <Card>
              <CardHeader>
                <CardTitle>최근 업데이트</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600">
                  마지막 업데이트: {new Date(overview.last_updated).toLocaleString()}
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="cache" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                캐시 통계
                <Button onClick={clearCache} variant="outline" size="sm">
                  캐시 삭제
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {cacheStats ? (
                <div className="space-y-6">
                  {/* 전체 히트율 */}
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium">전체 히트율</span>
                      <span className="text-sm text-gray-600">
                        {cacheStats.overall_hit_rate.toFixed(1)}%
                      </span>
                    </div>
                    <Progress value={cacheStats.overall_hit_rate} />
                  </div>

                  {/* 레벨별 통계 */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {Object.entries(cacheStats.level_hit_rates).map(([level, rate]) => (
                      <div key={level} className="p-4 border rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium">
                            {level.toUpperCase()} 캐시
                          </span>
                          <Badge
                            // pyright: ignore
                            variant={
                              cacheStats.cache_status[
                                (level + "_enabled") as keyof typeof cacheStats.cache_status
                              ]
                                ? "default"
                                : "secondary"
                            }
                          >
                            {
                              // pyright: ignore
                              cacheStats.cache_status[
                                (level + "_enabled") as keyof typeof cacheStats.cache_status
                              ]
                                ? "활성"
                                : "비활성"
                            }
                          </Badge>
                        </div>
                        <div className="text-2xl font-bold">{rate.toFixed(1)}%</div>
                        <div className="text-xs text-gray-600">
                          히트: {cacheStats.hits[level as keyof typeof cacheStats.hits]} / {/* pyright: ignore */}
                          미스: {cacheStats.misses[level as keyof typeof cacheStats.misses]} {/* pyright: ignore */}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* 상세 통계 */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-medium mb-2">캐시 작업</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm">쓰기 작업</span>
                          <span className="text-sm font-medium">
                            {Object.values(cacheStats.writes).reduce((a, b) => a + b, 0)}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm">총 요청</span>
                          <span className="text-sm font-medium">
                            {
                              // pyright: ignore
                              Object.values(cacheStats.hits).reduce((a, b) => a + b, 0) +
                              Object.values(cacheStats.misses).reduce((a, b) => a + b, 0)
                            }
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <p className="text-gray-600">캐시 통계를 불러올 수 없습니다.</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="queries" className="space-y-6">
          {/* 쿼리 통계 */}
          {overview?.query_stats && (
            <Card>
              <CardHeader>
                <CardTitle>쿼리 성능 통계</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold">{overview.query_stats.total_queries}</div>
                    <div className="text-sm text-gray-600">총 쿼리</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold">
                      {overview.query_stats.avg_execution_time.toFixed(3)}s
                    </div>
                    <div className="text-sm text-gray-600">평균 실행 시간</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-red-600">
                      {overview.query_stats.slow_queries_count}
                    </div>
                    <div className="text-sm text-gray-600">느린 쿼리</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {overview.query_stats.index_recommendations_count}
                    </div>
                    <div className="text-sm text-gray-600">인덱스 추천</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* 느린 쿼리 목록 */}
          <Card>
            <CardHeader>
              <CardTitle>느린 쿼리 목록</CardTitle>
            </CardHeader>
            <CardContent>
              {slowQueries.length > 0 ? (
                <div className="space-y-4">
                  {slowQueries.map((query, index) => (
                    <div key={index} className="p-4 border rounded-lg">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <Badge variant="destructive">
                            {query.execution_time.toFixed(3)}s
                          </Badge>
                          <Badge variant="outline">{query.operation}</Badge>
                        </div>
                        <span className="text-sm text-gray-600">
                          {new Date(query.timestamp).toLocaleString()}
                        </span>
                      </div>
                      <p className="text-sm font-mono bg-gray-100 p-2 rounded">
                        {query.sql}
                      </p>
                      <p className="text-xs text-gray-600 mt-1">
                        테이블: {query.table_name}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-600">느린 쿼리가 없습니다.</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="pool" className="space-y-6">
          {/* 연결 풀 통계 */}
          {poolStats && (
            <Card>
              <CardHeader>
                <CardTitle>연결 풀 상태</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-medium mb-4">연결 상태</h4>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-sm">풀 크기</span>
                        <span className="text-sm font-medium">{poolStats.pool_size}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">사용 중</span>
                        <span className="text-sm font-medium text-blue-600">
                          {poolStats.checked_out}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">사용 가능</span>
                        <span className="text-sm font-medium text-green-600">
                          {poolStats.checked_in}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">오버플로우</span>
                        <span className="text-sm font-medium text-yellow-600">
                          {poolStats.overflow}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium mb-4">사용률</h4>
                    <div className="space-y-4">
                      <div>
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm">연결 사용률</span>
                          <span className="text-sm text-gray-600">
                            {poolStats.total_connections > 0 ? 
                              ((poolStats.checked_out / poolStats.total_connections) * 100).toFixed(1) : 0}%
                          </span>
                        </div>
                        <Progress 
                          value={poolStats.total_connections > 0 ? 
                            (poolStats.checked_out / poolStats.total_connections) * 100 : 0} 
                        />
                      </div>
                      
                      <div className="text-sm text-gray-600">
                        <p>총 연결: {poolStats.total_connections}</p>
                        <p>활성 연결: {poolStats.checked_out}</p>
                        <p>대기 연결: {poolStats.checked_in}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
} 
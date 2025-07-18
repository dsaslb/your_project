import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  CheckCircle, 
  Brain,
  BarChart3,
  Users,
  ShoppingCart,
  Package,
  Target,
  RefreshCw,
  Lightbulb,
  Eye,
  Zap,
  ArrowUpRight,
  ArrowDownRight,
  Minus
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area } from 'recharts';

interface BusinessInsight {
  insight_id: string;
  category: string;
  title: string;
  description: string;
  impact_score: number;
  confidence: number;
  action_items: string[];
  metrics: Record<string, any>;
  created_at: string;
  expires_at?: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
}

interface MarketTrend {
  trend_id: string;
  category: string;
  trend_type: 'increasing' | 'decreasing' | 'stable' | 'volatile';
  description: string;
  confidence: number;
  data_points: Array<{date: string; value: number}>;
  prediction_horizon: number;
  impact_analysis: Record<string, any>;
}

interface CompetitiveAnalysis {
  competitor_id: string;
  competitor_name: string;
  analysis_date: string;
  market_share: number;
  pricing_strategy: string;
  strengths: string[];
  weaknesses: string[];
  opportunities: string[];
  threats: string[];
  recommendations: string[];
}

interface InsightSummary {
  total_insights: number;
  critical_insights: number;
  high_priority_insights: number;
  average_impact_score: number;
  insights_by_category: Record<string, number>;
  priority_distribution: Record<string, number>;
}

const COLORS = {
  critical: '#ef4444',
  high: '#f59e0b',
  medium: '#3b82f6',
  low: '#10b981',
  increasing: '#10b981',
  decreasing: '#ef4444',
  stable: '#6b7280',
  volatile: '#f59e0b'
};

const CATEGORY_ICONS = {
  sales: ShoppingCart,
  inventory: Package,
  customer: Users,
  operations: Target,
  market: BarChart3
};

const BusinessIntelligenceDashboard: React.FC = () => {
  const [insights, setInsights] = useState<Record<string, BusinessInsight[]>>({});
  const [summary, setSummary] = useState<InsightSummary | null>(null);
  const [prioritizedInsights, setPrioritizedInsights] = useState<BusinessInsight[]>([]);
  const [trends, setTrends] = useState<Record<string, MarketTrend>>({});
  const [competition, setCompetition] = useState<CompetitiveAnalysis[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [lastUpdate, setLastUpdate] = useState<string>('');

  useEffect(() => {
    fetchBusinessIntelligenceData();
    const interval = setInterval(fetchBusinessIntelligenceData, 300000); // 5분마다 업데이트
    return () => clearInterval(interval);
  }, []);

  const fetchBusinessIntelligenceData = async () => {
    try {
      setIsLoading(true);
      setError('');

      // 비즈니스 인사이트 조회
      const insightsResponse = await fetch('/api/bi/insights', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (insightsResponse.ok) {
        const insightsData = await insightsResponse.json();
        if (insightsData.success) {
          setInsights(insightsData.insights);
          setSummary(insightsData.summary);
          setPrioritizedInsights(insightsData.prioritized_insights || []);
        }
      }

      // 시장 트렌드 조회
      const trendsResponse = await fetch('/api/bi/trends', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (trendsResponse.ok) {
        const trendsData = await trendsResponse.json();
        if (trendsData.success) {
          setTrends(trendsData.trends);
        }
      }

      // 경쟁사 분석 조회
      const competitionResponse = await fetch('/api/bi/competition', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (competitionResponse.ok) {
        const competitionData = await competitionResponse.json();
        if (competitionData.success) {
          setCompetition(competitionData.analyses);
        }
      }

      setLastUpdate(new Date().toLocaleString());
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류');
    } finally {
      setIsLoading(false);
    }
  };

  const generateNewInsights = async () => {
    try {
      setIsLoading(true);
      setError('');

      const response = await fetch('/api/bi/insights/generate', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setInsights(data.insights);
          setSummary(data.summary);
          setPrioritizedInsights(data.prioritized_insights || []);
          setLastUpdate(new Date().toLocaleString());
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '인사이트 생성 실패');
    } finally {
      setIsLoading(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    return COLORS[priority as keyof typeof COLORS] || COLORS.medium;
  };

  const getTrendIcon = (trendType: string) => {
    switch (trendType) {
      case 'increasing': return <ArrowUpRight className="w-4 h-4" />;
      case 'decreasing': return <ArrowDownRight className="w-4 h-4" />;
      case 'stable': return <Minus className="w-4 h-4" />;
      case 'volatile': return <AlertTriangle className="w-4 h-4" />;
      default: return <Minus className="w-4 h-4" />;
    }
  };

  const getTrendColor = (trendType: string) => {
    return COLORS[trendType as keyof typeof COLORS] || COLORS.stable;
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW'
    }).format(value);
  };

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  if (isLoading && !summary) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
            <p>비즈니스 인텔리전스 데이터를 불러오는 중...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">비즈니스 인텔리전스 대시보드</h1>
          <p className="text-muted-foreground">
            마지막 업데이트: {lastUpdate}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button 
            variant="outline" 
            onClick={fetchBusinessIntelligenceData}
            disabled={isLoading}
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            새로고침
          </Button>
          <Button 
            onClick={generateNewInsights}
            disabled={isLoading}
          >
            <Lightbulb className="w-4 h-4 mr-2" />
            인사이트 생성
          </Button>
        </div>
      </div>

      {/* 요약 통계 */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="w-4 h-4" />
                총 인사이트
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {summary.total_insights}개
              </div>
              <div className="text-sm text-muted-foreground">
                생성된 인사이트 수
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4" />
                긴급 인사이트
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {summary.critical_insights}개
              </div>
              <div className="text-sm text-muted-foreground">
                즉시 대응 필요
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="w-4 h-4" />
                평균 영향도
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatPercentage(summary.average_impact_score)}
              </div>
              <div className="text-sm text-muted-foreground">
                전체 인사이트 평균
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="w-4 h-4" />
                고우선순위
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">
                {summary.high_priority_insights}개
              </div>
              <div className="text-sm text-muted-foreground">
                높은 우선순위
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 우선순위별 인사이트 */}
      {prioritizedInsights.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Eye className="w-4 h-4" />
              우선순위별 인사이트
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {prioritizedInsights.slice(0, 5).map((insight) => {
                const CategoryIcon = CATEGORY_ICONS[insight.category as keyof typeof CATEGORY_ICONS] || Brain;
                return (
                  <div key={insight.insight_id} className="p-4 border rounded-lg">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <CategoryIcon className="w-4 h-4" />
                        <span className="font-medium">{insight.title}</span>
                      </div>
                      <Badge 
                        style={{ backgroundColor: getPriorityColor(insight.priority) }}
                        className="text-white"
                      >
                        {insight.priority}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-3">
                      {insight.description}
                    </p>
                    <div className="flex items-center gap-4 mb-3">
                      <div className="flex items-center gap-1">
                        <span className="text-xs">영향도:</span>
                        <span className="text-sm font-medium">{formatPercentage(insight.impact_score)}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <span className="text-xs">신뢰도:</span>
                        <span className="text-sm font-medium">{formatPercentage(insight.confidence)}</span>
                      </div>
                    </div>
                    <div className="space-y-1">
                      <div className="text-xs font-medium">권장사항:</div>
                      <ul className="text-xs text-muted-foreground space-y-1">
                        {insight.action_items.slice(0, 3).map((action, index) => (
                          <li key={index} className="flex items-center gap-1">
                            <div className="w-1 h-1 bg-primary rounded-full" />
                            {action}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 카테고리별 인사이트 */}
      <Tabs defaultValue="sales" className="space-y-4">
        <TabsList>
          <TabsTrigger value="sales">매출</TabsTrigger>
          <TabsTrigger value="inventory">재고</TabsTrigger>
          <TabsTrigger value="customer">고객</TabsTrigger>
          <TabsTrigger value="operations">운영</TabsTrigger>
          <TabsTrigger value="market">시장</TabsTrigger>
        </TabsList>

        {Object.entries(insights).map(([category, categoryInsights]) => (
          <TabsContent key={category} value={category} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {categoryInsights.map((insight) => {
                const CategoryIcon = CATEGORY_ICONS[category as keyof typeof CATEGORY_ICONS] || Brain;
                return (
                  <Card key={insight.insight_id} className="h-full">
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <CategoryIcon className="w-4 h-4" />
                          <span className="text-sm">{insight.title}</span>
                        </div>
                        <Badge 
                          style={{ backgroundColor: getPriorityColor(insight.priority) }}
                          className="text-white text-xs"
                        >
                          {insight.priority}
                        </Badge>
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <p className="text-sm text-muted-foreground">
                        {insight.description}
                      </p>
                      
                      <div className="flex items-center justify-between text-xs">
                        <span>영향도</span>
                        <span className="font-medium">{formatPercentage(insight.impact_score)}</span>
                      </div>
                      <Progress value={insight.impact_score * 100} className="h-2" />
                      
                      <div className="flex items-center justify-between text-xs">
                        <span>신뢰도</span>
                        <span className="font-medium">{formatPercentage(insight.confidence)}</span>
                      </div>
                      <Progress value={insight.confidence * 100} className="h-2" />
                      
                      <div className="text-xs">
                        <div className="font-medium mb-1">주요 지표:</div>
                        {Object.entries(insight.metrics).slice(0, 3).map(([key, value]) => (
                          <div key={key} className="flex justify-between">
                            <span>{key}:</span>
                            <span className="font-medium">
                              {typeof value === 'number' && value > 1000 
                                ? formatCurrency(value) 
                                : typeof value === 'number' && value < 1 
                                ? formatPercentage(value)
                                : value}
                            </span>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </TabsContent>
        ))}
      </Tabs>

      {/* 시장 트렌드 */}
      {Object.keys(trends).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              시장 트렌드 분석
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {Object.entries(trends).map(([category, trend]) => (
                <div key={trend.trend_id} className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium capitalize">{category} 트렌드</h4>
                    <div className="flex items-center gap-2">
                      <div 
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: getTrendColor(trend.trend_type) }}
                      />
                      <span className="text-sm capitalize">{trend.trend_type}</span>
                      {getTrendIcon(trend.trend_type)}
                    </div>
                  </div>
                  
                  <p className="text-sm text-muted-foreground">
                    {trend.description}
                  </p>
                  
                  <div className="flex items-center justify-between text-xs">
                    <span>신뢰도</span>
                    <span className="font-medium">{formatPercentage(trend.confidence)}</span>
                  </div>
                  <Progress value={trend.confidence * 100} className="h-2" />
                  
                  {trend.data_points.length > 0 && (
                    <ResponsiveContainer width="100%" height={200}>
                      <AreaChart data={trend.data_points}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Area 
                          type="monotone" 
                          dataKey="value" 
                          stroke={getTrendColor(trend.trend_type)}
                          fill={getTrendColor(trend.trend_type)}
                          fillOpacity={0.3}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 경쟁사 분석 */}
      {competition.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="w-4 h-4" />
              경쟁사 분석
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {competition.map((comp) => (
                <div key={comp.competitor_id} className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium">{comp.competitor_name}</h4>
                    <Badge variant="outline">
                      {formatPercentage(comp.market_share)}
                    </Badge>
                  </div>
                  
                  <div className="space-y-3">
                    <div>
                      <div className="text-xs font-medium mb-1">강점:</div>
                      <ul className="text-xs text-muted-foreground space-y-1">
                        {comp.strengths.slice(0, 3).map((strength, index) => (
                          <li key={index} className="flex items-center gap-1">
                            <CheckCircle className="w-3 h-3 text-green-600" />
                            {strength}
                          </li>
                        ))}
                      </ul>
                    </div>
                    
                    <div>
                      <div className="text-xs font-medium mb-1">약점:</div>
                      <ul className="text-xs text-muted-foreground space-y-1">
                        {comp.weaknesses.slice(0, 2).map((weakness, index) => (
                          <li key={index} className="flex items-center gap-1">
                            <AlertTriangle className="w-3 h-3 text-red-600" />
                            {weakness}
                          </li>
                        ))}
                      </ul>
                    </div>
                    
                    <div>
                      <div className="text-xs font-medium mb-1">권장사항:</div>
                      <ul className="text-xs text-muted-foreground space-y-1">
                        {comp.recommendations.slice(0, 2).map((rec, index) => (
                          <li key={index} className="flex items-center gap-1">
                            <div className="w-1 h-1 bg-blue-600 rounded-full" />
                            {rec}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default BusinessIntelligenceDashboard; 
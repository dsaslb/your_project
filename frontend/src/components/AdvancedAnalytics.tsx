"use client";

import { useState, useEffect, useMemo } from 'react';
import { cn } from '@/lib/utils';
import { useAdvancedAnalytics } from '@/hooks/useAdvancedAnalytics';
import { 
  TrendingUp, 
  TrendingDown, 
  BarChart3, 
  PieChart, 
  Activity,
  Users,
  ShoppingCart,
  DollarSign,
  Calendar,
  Target,
  Award,
  AlertTriangle,
  CheckCircle,
  Clock,
  Zap
} from 'lucide-react';
import { Button } from '@/components/ui/button';

// 예측 분석 카드
export const PredictionCard = ({ 
  title, 
  currentValue, 
  predictedValue, 
  confidence, 
  trend,
  icon: Icon,
  color = 'cyan'
}: {
  title: string;
  currentValue: number;
  predictedValue: number;
  confidence: number;
  trend: 'up' | 'down' | 'stable';
  icon: any;
  color?: string;
}) => {
  const getTrendColor = () => {
    switch (trend) {
      case 'up': return 'text-green-400';
      case 'down': return 'text-red-400';
      default: return 'text-yellow-400';
    }
  };

  const getTrendIcon = () => {
    switch (trend) {
      case 'up': return <TrendingUp className="w-4 h-4" />;
      case 'down': return <TrendingDown className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  const changePercent = ((predictedValue - currentValue) / currentValue) * 100;

  return (
    <div className="p-4 rounded-lg border border-cyan-500/20 bg-black/30 backdrop-blur-sm">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <div className={cn(
            "p-2 rounded-lg",
            color === 'cyan' && "bg-cyan-500/20",
            color === 'green' && "bg-green-500/20",
            color === 'yellow' && "bg-yellow-500/20",
            color === 'red' && "bg-red-500/20"
          )}>
            <Icon className={cn(
              "w-4 h-4",
              color === 'cyan' && "text-cyan-400",
              color === 'green' && "text-green-400",
              color === 'yellow' && "text-yellow-400",
              color === 'red' && "text-red-400"
            )} />
          </div>
          <span className="text-sm font-medium text-white">{title}</span>
        </div>
        <div className={cn("flex items-center space-x-1", getTrendColor())}>
          {getTrendIcon()}
        </div>
      </div>
      
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">현재</span>
          <span className="text-sm font-bold text-white">{currentValue.toLocaleString()}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">예측</span>
          <span className="text-sm font-bold text-cyan-400">{predictedValue.toLocaleString()}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">변화율</span>
          <span className={cn("text-xs font-mono", getTrendColor())}>
            {changePercent > 0 ? '+' : ''}{changePercent.toFixed(1)}%
          </span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">신뢰도</span>
          <span className="text-xs text-white">{confidence}%</span>
        </div>
      </div>
    </div>
  );
};

// 패턴 분석 카드
export const PatternAnalysisCard = () => {
  const [patterns, setPatterns] = useState([
    {
      id: 1,
      type: 'seasonal',
      title: '계절성 패턴',
      description: '매주 월요일 오전에 주문량이 30% 증가',
      confidence: 85,
      impact: 'high'
    },
    {
      id: 2,
      type: 'trend',
      title: '상승 트렌드',
      description: '모바일 주문이 지난 3개월간 15% 증가',
      confidence: 92,
      impact: 'medium'
    },
    {
      id: 3,
      type: 'anomaly',
      title: '이상 패턴',
      description: '어제 오후 3시에 비정상적인 트래픽 발생',
      confidence: 78,
      impact: 'high'
    }
  ]);

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high': return 'text-red-400';
      case 'medium': return 'text-yellow-400';
      case 'low': return 'text-green-400';
      default: return 'text-slate-400';
    }
  };

  const getPatternIcon = (type: string) => {
    switch (type) {
      case 'seasonal': return <Calendar className="w-4 h-4 text-blue-400" />;
      case 'trend': return <TrendingUp className="w-4 h-4 text-green-400" />;
      case 'anomaly': return <AlertTriangle className="w-4 h-4 text-red-400" />;
      default: return <Activity className="w-4 h-4 text-slate-400" />;
    }
  };

  return (
    <div className="p-4 rounded-lg border border-cyan-500/20 bg-black/30 backdrop-blur-sm">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-white">패턴 분석</h3>
        <Button
          variant="ghost"
          size="sm"
          className="text-slate-400 hover:text-white"
        >
          <BarChart3 className="w-4 h-4" />
        </Button>
      </div>
      
      <div className="space-y-3">
        {patterns.map((pattern) => (
          <div key={pattern.id} className="p-3 bg-black/20 rounded-lg border border-cyan-500/10">
            <div className="flex items-start space-x-2">
              {getPatternIcon(pattern.type)}
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-white">{pattern.title}</span>
                  <span className={cn("text-xs", getImpactColor(pattern.impact))}>
                    {pattern.impact.toUpperCase()}
                  </span>
                </div>
                <p className="text-xs text-slate-400 mb-2">{pattern.description}</p>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400">신뢰도: <span className="text-white">{pattern.confidence}%</span></span>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-cyan-400 hover:text-cyan-300 text-xs"
                  >
                    자세히 보기
                  </Button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// KPI 대시보드
export const KPIDashboard = () => {
  const [kpis, setKpis] = useState([
    {
      id: 1,
      name: '매출 목표 달성률',
      current: 78,
      target: 100,
      unit: '%',
      trend: 'up',
      icon: Target
    },
    {
      id: 2,
      name: '고객 만족도',
      current: 4.2,
      target: 4.5,
      unit: '/5',
      trend: 'stable',
      icon: Award
    },
    {
      id: 3,
      name: '평균 응답시간',
      current: 120,
      target: 100,
      unit: 'ms',
      trend: 'down',
      icon: Clock
    },
    {
      id: 4,
      name: '시스템 가동률',
      current: 99.8,
      target: 99.9,
      unit: '%',
      trend: 'up',
      icon: Zap
    }
  ]);

  const getProgressColor = (current: number, target: number) => {
    const ratio = current / target;
    if (ratio >= 1) return 'bg-green-400';
    if (ratio >= 0.8) return 'bg-yellow-400';
    return 'bg-red-400';
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return <TrendingUp className="w-3 h-3 text-green-400" />;
      case 'down': return <TrendingDown className="w-3 h-3 text-red-400" />;
      default: return <Activity className="w-3 h-3 text-yellow-400" />;
    }
  };

  return (
    <div className="p-4 rounded-lg border border-cyan-500/20 bg-black/30 backdrop-blur-sm">
      <h3 className="text-sm font-semibold text-white mb-4">KPI 대시보드</h3>
      
      <div className="space-y-4">
        {kpis.map((kpi) => (
          <div key={kpi.id} className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <kpi.icon className="w-4 h-4 text-cyan-400" />
                <span className="text-sm text-white">{kpi.name}</span>
              </div>
              <div className="flex items-center space-x-2">
                {getTrendIcon(kpi.trend)}
                <span className="text-sm font-bold text-white">
                  {kpi.current}{kpi.unit}
                </span>
              </div>
            </div>
            
            <div className="w-full bg-slate-700 rounded-full h-2">
              <div
                className={cn("h-2 rounded-full transition-all duration-300", getProgressColor(kpi.current, kpi.target))}
                style={{ width: `${Math.min((kpi.current / kpi.target) * 100, 100)}%` }}
              />
            </div>
            
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-400">목표: {kpi.target}{kpi.unit}</span>
              <span className="text-slate-400">
                {((kpi.current / kpi.target) * 100).toFixed(1)}% 달성
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// 실시간 인사이트 카드
export const RealTimeInsights = () => {
  const [insights, setInsights] = useState([
    {
      id: 1,
      type: 'opportunity',
      title: '매출 기회',
      message: '오후 2-4시 주문량이 평소보다 25% 높습니다. 프로모션을 고려해보세요.',
      priority: 'high',
      timestamp: '2분 전'
    },
    {
      id: 2,
      type: 'warning',
      title: '성능 경고',
      message: '서버 응답시간이 평균보다 20% 느려집니다. 모니터링이 필요합니다.',
      priority: 'medium',
      timestamp: '5분 전'
    },
    {
      id: 3,
      type: 'success',
      title: '목표 달성',
      message: '이번 주 매출 목표를 3일 일찍 달성했습니다!',
      priority: 'low',
      timestamp: '10분 전'
    }
  ]);

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'opportunity': return <TrendingUp className="w-4 h-4 text-green-400" />;
      case 'warning': return <AlertTriangle className="w-4 h-4 text-yellow-400" />;
      case 'success': return <CheckCircle className="w-4 h-4 text-blue-400" />;
      default: return <Activity className="w-4 h-4 text-slate-400" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'border-red-400/30';
      case 'medium': return 'border-yellow-400/30';
      case 'low': return 'border-green-400/30';
      default: return 'border-slate-400/30';
    }
  };

  return (
    <div className="p-4 rounded-lg border border-cyan-500/20 bg-black/30 backdrop-blur-sm">
      <h3 className="text-sm font-semibold text-white mb-4">실시간 인사이트</h3>
      
      <div className="space-y-3">
        {insights.map((insight) => (
          <div 
            key={insight.id} 
            className={cn(
              "p-3 bg-black/20 rounded-lg border",
              getPriorityColor(insight.priority)
            )}
          >
            <div className="flex items-start space-x-2">
              {getInsightIcon(insight.type)}
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-white">{insight.title}</span>
                  <span className="text-xs text-slate-400">{insight.timestamp}</span>
                </div>
                <p className="text-xs text-slate-400">{insight.message}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// 고급 분석 대시보드
export const AdvancedAnalyticsDashboard = () => {
  const { data, loading, error } = useAdvancedAnalytics();
  
  const predictions = useMemo(() => {
    if (!data.predictions) return [];
    
    const predictionMap = [
      { key: 'sales', title: '다음 주 매출', icon: DollarSign, color: 'green' },
      { key: 'users', title: '활성 사용자', icon: Users, color: 'cyan' },
      { key: 'orders', title: '평균 주문액', icon: ShoppingCart, color: 'yellow' },
      { key: 'system_load', title: '시스템 부하', icon: Activity, color: 'red' }
    ];
    
    return predictionMap
      .map(({ key, title, icon, color }) => {
        const prediction = data.predictions[key];
        if (!prediction) return null;
        
        return {
          title,
          currentValue: prediction.current,
          predictedValue: prediction.predicted,
          confidence: prediction.confidence,
          trend: prediction.trend,
          icon,
          color
        };
      })
      .filter((item): item is NonNullable<typeof item> => item !== null);
  }, [data.predictions]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">고급 분석 대시보드</h2>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-slate-400">AI 기반 분석</span>
          <Button
            variant="ghost"
            size="sm"
            className="text-slate-400 hover:text-white"
          >
            <BarChart3 className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* 예측 분석 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {predictions.map((prediction) => (
          <PredictionCard
            key={prediction.title}
            title={prediction.title}
            currentValue={prediction.currentValue}
            predictedValue={prediction.predictedValue}
            confidence={prediction.confidence}
            trend={prediction.trend}
            icon={prediction.icon}
            color={prediction.color}
          />
        ))}
      </div>

      {/* 패턴 분석 및 KPI */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PatternAnalysisCard />
        <KPIDashboard />
      </div>

      {/* 실시간 인사이트 */}
      <RealTimeInsights />
    </div>
  );
}; 
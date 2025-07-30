'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
import { cn } from '@/lib/utils';
import { 
  Zap, 
  Cpu, 
  MemoryStick, 
  HardDrive, 
  Network, 
  Settings,
  RefreshCw,
  TrendingUp,
  TrendingDown,
  AlertTriangle
} from 'lucide-react';
import { Button } from '@/components/ui/button';

// 성능 모니터링 훅
export const usePerformanceMonitor = () => {
  const [metrics, setMetrics] = useState({
    cpu: 0,
    memory: 0,
    disk: 0,
    network: 0,
    responseTime: 0
  });

  const [history, setHistory] = useState<Array<{
    timestamp: number;
    cpu: number;
    memory: number;
    disk: number;
    network: number;
    responseTime: number;
  }>>([]);

  const updateMetrics = useCallback(() => {
    const newMetrics = {
      cpu: Math.floor(Math.random() * 100),
      memory: Math.floor(Math.random() * 100),
      disk: Math.floor(Math.random() * 100),
      network: Math.floor(Math.random() * 100),
      responseTime: Math.floor(Math.random() * 500) + 50
    };

    setMetrics(newMetrics);
    setHistory(prev => {
      const newHistory = [...prev, { timestamp: Date.now(), ...newMetrics }];
      return newHistory.slice(-50); // 최근 50개 데이터만 유지
    });
  }, []);

  useEffect(() => {
    updateMetrics();
    const interval = setInterval(updateMetrics, 5000);
    return () => clearInterval(interval);
  }, [updateMetrics]);

  const getAverage = useCallback((key: keyof typeof metrics) => {
    if (history.length === 0) return 0;
    const sum = history.reduce((acc, item) => acc + item[key], 0);
    return Math.round(sum / history.length);
  }, [history]);

  const getTrend = useCallback((key: keyof typeof metrics): 'up' | 'down' | 'stable' => {
    if (history.length < 2) return 'stable';
    const recent = history.slice(-5);
    const older = history.slice(-10, -5);
    
    if (recent.length === 0 || older.length === 0) return 'stable';
    
    const recentAvg = recent.reduce((acc, item) => acc + item[key], 0) / recent.length;
    const olderAvg = older.reduce((acc, item) => acc + item[key], 0) / older.length;
    
    if (recentAvg > olderAvg * 1.1) return 'up';
    if (recentAvg < olderAvg * 0.9) return 'down';
    return 'stable';
  }, [history]);

  return {
    metrics,
    history,
    getAverage,
    getTrend,
    updateMetrics
  };
};

// 성능 지표 카드
export const PerformanceMetricCard = ({ 
  title, 
  value, 
  unit = '', 
  icon: Icon,
  trend,
  threshold = 80,
  color = 'cyan'
}: {
  title: string;
  value: number;
  unit?: string;
  icon: any;
  trend: 'up' | 'down' | 'stable';
  threshold?: number;
  color?: string;
}) => {
  const getStatusColor = () => {
    if (value > threshold) return 'text-red-400';
    if (value > threshold * 0.8) return 'text-yellow-400';
    return 'text-green-400';
  };

  const getTrendIcon = () => {
    switch (trend) {
      case 'up': return <TrendingUp className="w-3 h-3 text-red-400" />;
      case 'down': return <TrendingDown className="w-3 h-3 text-green-400" />;
      default: return null;
    }
  };

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
        {getTrendIcon()}
      </div>
      
      <div className="mb-2">
        <span className={cn("text-2xl font-bold", getStatusColor())}>
          {value}{unit}
        </span>
      </div>
      
      <div className="w-full bg-slate-700 rounded-full h-2">
        <div
          className={cn(
            "h-2 rounded-full transition-all duration-300",
            value > threshold && "bg-red-400",
            value > threshold * 0.8 && value <= threshold && "bg-yellow-400",
            value <= threshold * 0.8 && "bg-green-400"
          )}
          style={{ width: `${Math.min(value, 100)}%` }}
        />
      </div>
    </div>
  );
};

// 성능 최적화 제안 컴포넌트
export const PerformanceOptimizationSuggestions = () => {
  const [suggestions, setSuggestions] = useState([
    {
      id: 1,
      type: 'cpu',
      title: 'CPU 사용률 최적화',
      description: '불필요한 백그라운드 프로세스를 종료하여 CPU 사용률을 줄이세요.',
      priority: 'high',
      impact: '높음'
    },
    {
      id: 2,
      type: 'memory',
      title: '메모리 캐시 정리',
      description: '메모리 캐시를 정리하여 사용 가능한 메모리를 늘리세요.',
      priority: 'medium',
      impact: '중간'
    },
    {
      id: 3,
      type: 'disk',
      title: '디스크 공간 확보',
      description: '불필요한 파일을 삭제하여 디스크 공간을 확보하세요.',
      priority: 'low',
      impact: '낮음'
    }
  ]);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-400';
      case 'medium': return 'text-yellow-400';
      case 'low': return 'text-green-400';
      default: return 'text-slate-400';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high': return <AlertTriangle className="w-4 h-4 text-red-400" />;
      case 'medium': return <AlertTriangle className="w-4 h-4 text-yellow-400" />;
      case 'low': return <AlertTriangle className="w-4 h-4 text-green-400" />;
      default: return <AlertTriangle className="w-4 h-4 text-slate-400" />;
    }
  };

  return (
    <div className="p-4 rounded-lg border border-cyan-500/20 bg-black/30 backdrop-blur-sm">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-white">성능 최적화 제안</h3>
        <Button
          variant="ghost"
          size="sm"
          className="text-slate-400 hover:text-white"
        >
          <Settings className="w-4 h-4" />
        </Button>
      </div>
      
      <div className="space-y-3">
        {suggestions.map((suggestion) => (
          <div key={suggestion.id} className="p-3 bg-black/20 rounded-lg border border-cyan-500/10">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-1">
                  {getPriorityIcon(suggestion.priority)}
                  <span className="text-sm font-medium text-white">{suggestion.title}</span>
                  <span className={cn("text-xs", getPriorityColor(suggestion.priority))}>
                    {suggestion.priority.toUpperCase()}
                  </span>
                </div>
                <p className="text-xs text-slate-400 mb-2">{suggestion.description}</p>
                <div className="flex items-center space-x-4 text-xs">
                  <span className="text-slate-400">영향도: <span className="text-white">{suggestion.impact}</span></span>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                className="text-cyan-400 hover:text-cyan-300"
              >
                적용
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// 성능 대시보드
export const PerformanceDashboard = () => {
  const { metrics, getAverage, getTrend } = usePerformanceMonitor();

  const performanceMetrics = useMemo(() => [
    {
      title: 'CPU 사용률',
      value: metrics.cpu,
      unit: '%',
      icon: Cpu,
      trend: getTrend('cpu'),
      threshold: 80,
      color: 'red'
    },
    {
      title: '메모리 사용률',
      value: metrics.memory,
      unit: '%',
      icon: MemoryStick,
      trend: getTrend('memory'),
      threshold: 85,
      color: 'yellow'
    },
    {
      title: '디스크 사용률',
      value: metrics.disk,
      unit: '%',
      icon: HardDrive,
      trend: getTrend('disk'),
      threshold: 90,
      color: 'cyan'
    },
    {
      title: '네트워크 사용률',
      value: metrics.network,
      unit: '%',
      icon: Network,
      trend: getTrend('network'),
      threshold: 75,
      color: 'green'
    }
  ], [metrics, getTrend]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">시스템 성능 모니터링</h2>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-slate-400">응답시간: {metrics.responseTime}ms</span>
          <Button
            variant="ghost"
            size="sm"
            className="text-slate-400 hover:text-white"
          >
            <RefreshCw className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {performanceMetrics.map((metric) => (
          <PerformanceMetricCard
            key={metric.title}
            title={metric.title}
            value={metric.value}
            unit={metric.unit}
            icon={metric.icon}
            trend={metric.trend}
            threshold={metric.threshold}
            color={metric.color}
          />
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PerformanceOptimizationSuggestions />
        
        <div className="p-4 rounded-lg border border-cyan-500/20 bg-black/30 backdrop-blur-sm">
          <h3 className="text-sm font-semibold text-white mb-4">성능 통계</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-400">평균 CPU 사용률</span>
              <span className="text-white">{getAverage('cpu')}%</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-400">평균 메모리 사용률</span>
              <span className="text-white">{getAverage('memory')}%</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-400">평균 응답시간</span>
              <span className="text-white">{getAverage('responseTime')}ms</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-400">시스템 상태</span>
              <span className="text-green-400">정상</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}; 
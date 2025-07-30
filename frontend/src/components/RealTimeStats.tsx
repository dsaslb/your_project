'use client';

import { useState, useEffect } from 'react';
import { useSystemStatus } from '@/hooks/useSystemStatus';
import { cn } from '@/lib/utils';
import { TrendingUp, TrendingDown, Activity, Users, ShoppingCart, DollarSign } from 'lucide-react';

interface StatsData {
  totalUsers: number;
  activeUsers: number;
  totalOrders: number;
  pendingOrders: number;
  revenue: number;
  revenueChange: number;
  systemLoad: number;
  systemLoadChange: number;
}

export const RealTimeStats = () => {
  const { status } = useSystemStatus();
  const [stats, setStats] = useState<StatsData>({
    totalUsers: 0,
    activeUsers: 0,
    totalOrders: 0,
    pendingOrders: 0,
    revenue: 0,
    revenueChange: 0,
    systemLoad: 0,
    systemLoadChange: 0,
  });

  useEffect(() => {
    // 실시간 통계 데이터 가져오기
    const fetchStats = async () => {
      try {
        const response = await fetch('/api/stats/realtime');
        if (response.ok) {
          const data = await response.json();
          setStats(data);
        }
      } catch (error) {
        console.error('실시간 통계 로드 실패:', error);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 10000); // 10초마다 업데이트

    return () => clearInterval(interval);
  }, []);

  const StatCard = ({ 
    title, 
    value, 
    change, 
    icon: Icon, 
    color = 'cyan',
    format = 'number'
  }: {
    title: string;
    value: number;
    change: number;
    icon: any;
    color?: string;
    format?: 'number' | 'currency' | 'percentage';
  }) => {
    const formatValue = (val: number) => {
      switch (format) {
        case 'currency':
          return new Intl.NumberFormat('ko-KR', { 
            style: 'currency', 
            currency: 'KRW' 
          }).format(val);
        case 'percentage':
          return `${val.toFixed(1)}%`;
        default:
          return val.toLocaleString();
      }
    };

    return (
      <div className={cn(
        "p-4 rounded-lg border border-cyan-500/20 bg-black/30 backdrop-blur-sm",
        "hover:border-cyan-500/40 transition-all duration-300"
      )}>
        <div className="flex items-center justify-between mb-2">
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
          <div className="flex items-center space-x-1">
            {change > 0 ? (
              <TrendingUp className="w-3 h-3 text-green-400" />
            ) : (
              <TrendingDown className="w-3 h-3 text-red-400" />
            )}
            <span className={cn(
              "text-xs font-mono",
              change > 0 ? "text-green-400" : "text-red-400"
            )}>
              {change > 0 ? '+' : ''}{change.toFixed(1)}%
            </span>
          </div>
        </div>
        
        <div className="mb-1">
          <span className="text-2xl font-bold text-white">
            {formatValue(value)}
          </span>
        </div>
        
        <div className="text-xs text-slate-400">
          {title}
        </div>
      </div>
    );
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        title="총 사용자"
        value={stats.totalUsers}
        change={stats.totalUsers > 0 ? 5.2 : 0}
        icon={Users}
        color="cyan"
      />
      
      <StatCard
        title="활성 사용자"
        value={stats.activeUsers}
        change={stats.activeUsers > 0 ? 12.5 : 0}
        icon={Activity}
        color="green"
      />
      
      <StatCard
        title="총 주문"
        value={stats.totalOrders}
        change={stats.totalOrders > 0 ? 8.7 : 0}
        icon={ShoppingCart}
        color="yellow"
      />
      
      <StatCard
        title="매출"
        value={stats.revenue}
        change={stats.revenueChange}
        icon={DollarSign}
        color="green"
        format="currency"
      />
    </div>
  );
};

// 시스템 성능 카드
export const SystemPerformanceCard = () => {
  const { status } = useSystemStatus();

  const getPerformanceColor = (value: number, threshold: number) => {
    if (value > threshold * 0.8) return 'text-red-400';
    if (value > threshold * 0.6) return 'text-yellow-400';
    return 'text-green-400';
  };

  return (
    <div className="p-4 rounded-lg border border-cyan-500/20 bg-black/30 backdrop-blur-sm">
      <h3 className="text-lg font-semibold text-white mb-4">시스템 성능</h3>
      
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-sm text-slate-400">CPU 사용률</span>
          <div className="flex items-center space-x-2">
            <div className="w-16 h-2 bg-slate-700 rounded-full overflow-hidden">
              <div 
                className={cn(
                  "h-full transition-all duration-300",
                  getPerformanceColor(status.performance.cpu, 100) === 'text-red-400' && "bg-red-500",
                  getPerformanceColor(status.performance.cpu, 100) === 'text-yellow-400' && "bg-yellow-500",
                  getPerformanceColor(status.performance.cpu, 100) === 'text-green-400' && "bg-green-500"
                )}
                style={{ width: `${status.performance.cpu}%` }}
              />
            </div>
            <span className={cn(
              "text-sm font-mono w-12 text-right",
              getPerformanceColor(status.performance.cpu, 100)
            )}>
              {status.performance.cpu}%
            </span>
          </div>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-sm text-slate-400">메모리 사용률</span>
          <div className="flex items-center space-x-2">
            <div className="w-16 h-2 bg-slate-700 rounded-full overflow-hidden">
              <div 
                className={cn(
                  "h-full transition-all duration-300",
                  getPerformanceColor(status.performance.memory, 100) === 'text-red-400' && "bg-red-500",
                  getPerformanceColor(status.performance.memory, 100) === 'text-yellow-400' && "bg-yellow-500",
                  getPerformanceColor(status.performance.memory, 100) === 'text-green-400' && "bg-green-500"
                )}
                style={{ width: `${status.performance.memory}%` }}
              />
            </div>
            <span className={cn(
              "text-sm font-mono w-12 text-right",
              getPerformanceColor(status.performance.memory, 100)
            )}>
              {status.performance.memory}%
            </span>
          </div>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-sm text-slate-400">응답시간</span>
          <span className={cn(
            "text-sm font-mono",
            getPerformanceColor(status.performance.responseTime, 1000)
          )}>
            {status.performance.responseTime}ms
          </span>
        </div>
      </div>
    </div>
  );
}; 
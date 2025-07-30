'use client';

import { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { 
  TrendingUp, 
  TrendingDown, 
  Users, 
  ShoppingCart, 
  DollarSign, 
  Activity,
  Clock,
  AlertTriangle,
  CheckCircle,
  XCircle,
  RefreshCw,
  Settings
} from 'lucide-react';
import { Button } from '@/components/ui/button';

// 실시간 카운터 위젯
export const LiveCounter = ({ 
  title, 
  value, 
  change, 
  icon: Icon,
  color = 'cyan',
  refreshInterval = 5000 
}: {
  title: string;
  value: number;
  change?: number;
  icon: any;
  color?: string;
  refreshInterval?: number;
}) => {
  const [currentValue, setCurrentValue] = useState(value);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentValue(prev => prev + Math.floor(Math.random() * 10) - 5);
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [refreshInterval]);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => {
      setCurrentValue(value);
      setIsRefreshing(false);
    }, 1000);
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
        <Button
          variant="ghost"
          size="sm"
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="text-slate-400 hover:text-white"
        >
          <RefreshCw className={cn("w-3 h-3", isRefreshing && "animate-spin")} />
        </Button>
      </div>
      
      <div className="mb-2">
        <span className="text-2xl font-bold text-white">
          {currentValue.toLocaleString()}
        </span>
      </div>
      
      {change !== undefined && (
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
            {change > 0 ? '+' : ''}{change}%
          </span>
        </div>
      )}
    </div>
  );
};

// 시스템 상태 위젯
export const SystemStatusWidget = () => {
  const [status, setStatus] = useState<'online' | 'warning' | 'error'>('online');
  const [lastUpdate, setLastUpdate] = useState(new Date());

  useEffect(() => {
    const interval = setInterval(() => {
      setLastUpdate(new Date());
      // 상태 시뮬레이션
      const random = Math.random();
      if (random > 0.9) setStatus('error');
      else if (random > 0.7) setStatus('warning');
      else setStatus('online');
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = () => {
    switch (status) {
      case 'online': return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'warning': return <AlertTriangle className="w-4 h-4 text-yellow-400" />;
      case 'error': return <XCircle className="w-4 h-4 text-red-400" />;
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'online': return '정상';
      case 'warning': return '주의';
      case 'error': return '오류';
    }
  };

  return (
    <div className="p-4 rounded-lg border border-cyan-500/20 bg-black/30 backdrop-blur-sm">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-white">시스템 상태</h3>
        <div className="flex items-center space-x-2">
          {getStatusIcon()}
          <span className={cn(
            "text-xs font-medium",
            status === 'online' && "text-green-400",
            status === 'warning' && "text-yellow-400",
            status === 'error' && "text-red-400"
          )}>
            {getStatusText()}
          </span>
        </div>
      </div>
      
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-400">마지막 업데이트</span>
          <span className="text-white">{lastUpdate.toLocaleTimeString()}</span>
        </div>
        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-400">응답시간</span>
          <span className="text-white">{(Math.random() * 100 + 50).toFixed(0)}ms</span>
        </div>
        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-400">가동시간</span>
          <span className="text-white">15일 8시간</span>
        </div>
      </div>
    </div>
  );
};

// 알림 요약 위젯
export const AlertSummaryWidget = () => {
  const [alerts, setAlerts] = useState({
    total: 12,
    unread: 3,
    error: 1,
    warning: 2,
    info: 9
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setAlerts(prev => ({
        ...prev,
        total: prev.total + Math.floor(Math.random() * 3),
        unread: Math.min(prev.unread + Math.floor(Math.random() * 2), prev.total)
      }));
    }, 15000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-4 rounded-lg border border-cyan-500/20 bg-black/30 backdrop-blur-sm">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-white">알림 요약</h3>
        <div className="flex items-center space-x-1">
          <AlertTriangle className="w-3 h-3 text-yellow-400" />
          <span className="text-xs text-white">{alerts.unread}</span>
        </div>
      </div>
      
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-400">전체</span>
          <span className="text-white">{alerts.total}</span>
        </div>
        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-400">읽지 않음</span>
          <span className="text-red-400">{alerts.unread}</span>
        </div>
        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-400">오류</span>
          <span className="text-red-400">{alerts.error}</span>
        </div>
        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-400">경고</span>
          <span className="text-yellow-400">{alerts.warning}</span>
        </div>
      </div>
    </div>
  );
};

// 빠른 액션 위젯
export const QuickActionsWidget = () => {
  const actions = [
    { name: '새 사용자', icon: Users, color: 'cyan' },
    { name: '주문 확인', icon: ShoppingCart, color: 'green' },
    { name: '매출 보고', icon: DollarSign, color: 'yellow' },
    { name: '시스템 점검', icon: Activity, color: 'red' },
  ];

  return (
    <div className="p-4 rounded-lg border border-cyan-500/20 bg-black/30 backdrop-blur-sm">
      <h3 className="text-sm font-semibold text-white mb-3">빠른 액션</h3>
      
      <div className="grid grid-cols-2 gap-2">
        {actions.map((action) => (
          <Button
            key={action.name}
            variant="ghost"
            size="sm"
            className="h-12 flex flex-col space-y-1 text-xs hover:bg-cyan-500/10"
          >
            <action.icon className="w-4 h-4" />
            <span>{action.name}</span>
          </Button>
        ))}
      </div>
    </div>
  );
};

// 실시간 활동 피드 위젯
export const ActivityFeedWidget = () => {
  const [activities, setActivities] = useState([
    { id: 1, user: '김철수', action: '새 주문 접수', time: '2분 전', type: 'order' },
    { id: 2, user: '이영희', action: '재고 업데이트', time: '5분 전', type: 'inventory' },
    { id: 3, user: '박민수', action: '매출 보고서 생성', time: '8분 전', type: 'report' },
    { id: 4, user: '최지영', action: '시스템 로그인', time: '12분 전', type: 'login' },
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      const newActivity = {
        id: Date.now(),
        user: ['김철수', '이영희', '박민수', '최지영'][Math.floor(Math.random() * 4)],
        action: ['새 주문 접수', '재고 업데이트', '매출 보고서 생성', '시스템 로그인'][Math.floor(Math.random() * 4)],
        time: '방금 전',
        type: ['order', 'inventory', 'report', 'login'][Math.floor(Math.random() * 4)]
      };
      
      setActivities(prev => [newActivity, ...prev.slice(0, 3)]);
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const getActionIcon = (type: string) => {
    switch (type) {
      case 'order': return <ShoppingCart className="w-3 h-3 text-green-400" />;
      case 'inventory': return <Activity className="w-3 h-3 text-blue-400" />;
      case 'report': return <DollarSign className="w-3 h-3 text-yellow-400" />;
      case 'login': return <Users className="w-3 h-3 text-cyan-400" />;
      default: return <Clock className="w-3 h-3 text-slate-400" />;
    }
  };

  return (
    <div className="p-4 rounded-lg border border-cyan-500/20 bg-black/30 backdrop-blur-sm">
      <h3 className="text-sm font-semibold text-white mb-3">실시간 활동</h3>
      
      <div className="space-y-2">
        {activities.map((activity) => (
          <div key={activity.id} className="flex items-center space-x-2 text-xs">
            {getActionIcon(activity.type)}
            <div className="flex-1 min-w-0">
              <span className="text-white font-medium">{activity.user}</span>
              <span className="text-slate-400"> {activity.action}</span>
            </div>
            <span className="text-slate-500">{activity.time}</span>
          </div>
        ))}
      </div>
    </div>
  );
}; 
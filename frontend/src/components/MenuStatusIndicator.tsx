'use client';

import { cn } from '@/lib/utils';
import { Circle, AlertCircle, XCircle, Clock } from 'lucide-react';

interface MenuStatusIndicatorProps {
  status: 'online' | 'offline' | 'warning' | 'error';
  message?: string;
  lastUpdated?: Date;
  showDetails?: boolean;
}

export const MenuStatusIndicator = ({
  status,
  message,
  lastUpdated,
  showDetails = false,
}: MenuStatusIndicatorProps) => {
  const getStatusConfig = () => {
    switch (status) {
      case 'online':
        return {
          icon: Circle,
          color: 'text-green-400',
          bgColor: 'bg-green-400/20',
          borderColor: 'border-green-400/30',
          pulse: false,
        };
      case 'warning':
        return {
          icon: AlertCircle,
          color: 'text-yellow-400',
          bgColor: 'bg-yellow-400/20',
          borderColor: 'border-yellow-400/30',
          pulse: true,
        };
      case 'error':
        return {
          icon: XCircle,
          color: 'text-red-400',
          bgColor: 'bg-red-400/20',
          borderColor: 'border-red-400/30',
          pulse: true,
        };
      case 'offline':
        return {
          icon: Clock,
          color: 'text-slate-400',
          bgColor: 'bg-slate-400/20',
          borderColor: 'border-slate-400/30',
          pulse: false,
        };
      default:
        return {
          icon: Circle,
          color: 'text-slate-400',
          bgColor: 'bg-slate-400/20',
          borderColor: 'border-slate-400/30',
          pulse: false,
        };
    }
  };

  const config = getStatusConfig();
  const Icon = config.icon;

  const formatLastUpdated = (date?: Date) => {
    if (!date) return '';
    
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / (1000 * 60));
    
    if (minutes < 1) return '방금 전';
    if (minutes < 60) return `${minutes}분 전`;
    
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}시간 전`;
    
    const days = Math.floor(hours / 24);
    return `${days}일 전`;
  };

  return (
    <div className="flex items-center space-x-2">
      {/* 상태 아이콘 */}
      <div
        className={cn(
          'flex items-center justify-center w-4 h-4 rounded-full border',
          config.bgColor,
          config.borderColor,
          config.pulse && 'animate-pulse'
        )}
      >
        <Icon className={cn('w-2 h-2', config.color)} />
      </div>

      {/* 상태 메시지 */}
      {showDetails && message && (
        <span className={cn('text-xs', config.color)}>
          {message}
        </span>
      )}

      {/* 마지막 업데이트 시간 */}
      {showDetails && lastUpdated && (
        <span className="text-xs text-slate-400">
          {formatLastUpdated(lastUpdated)}
        </span>
      )}
    </div>
  );
};

// 상태 배지 컴포넌트 (작은 크기)
export const StatusBadge = ({ status }: { status: 'online' | 'offline' | 'warning' | 'error' }) => {
  const config = {
    online: 'bg-green-500',
    warning: 'bg-yellow-500',
    error: 'bg-red-500',
    offline: 'bg-slate-500',
  };

  return (
    <div
      className={cn(
        'w-2 h-2 rounded-full',
        config[status],
        (status === 'warning' || status === 'error') && 'animate-pulse'
      )}
    />
  );
};

// 상태 툴팁 컴포넌트
export const StatusTooltip = ({
  status,
  message,
  lastUpdated,
}: {
  status: 'online' | 'offline' | 'warning' | 'error';
  message?: string;
  lastUpdated?: Date;
}) => {
  const getStatusText = () => {
    switch (status) {
      case 'online': return '정상 작동';
      case 'warning': return '성능 저하';
      case 'error': return '오류 발생';
      case 'offline': return '서비스 중단';
      default: return '상태 불명';
    }
  };

  return (
    <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-black/90 backdrop-blur-xl border border-cyan-500/30 rounded-lg text-xs text-white whitespace-nowrap z-50">
      <div className="flex items-center space-x-2">
        <StatusBadge status={status} />
        <span>{getStatusText()}</span>
      </div>
      {message && (
        <div className="mt-1 text-slate-300">
          {message}
        </div>
      )}
      {lastUpdated && (
        <div className="mt-1 text-slate-400">
          업데이트: {formatLastUpdated(lastUpdated)}
        </div>
      )}
    </div>
  );
};

const formatLastUpdated = (date: Date) => {
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / (1000 * 60));
  
  if (minutes < 1) return '방금 전';
  if (minutes < 60) return `${minutes}분 전`;
  
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}시간 전`;
  
  const days = Math.floor(hours / 24);
  return `${days}일 전`;
}; 
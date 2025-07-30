'use client';

import { useSystemStatus } from '@/hooks/useSystemStatus';
import { MenuStatusIndicator } from '@/components/MenuStatusIndicator';
import { cn } from '@/lib/utils';
import { Activity, Wifi, Database, Brain } from 'lucide-react';

export const SystemStatusHeader = () => {
  const { status, loading, error } = useSystemStatus();

  if (loading) {
    return (
      <div className="p-3 border-b border-cyan-500/20 bg-black/30">
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">시스템 상태 로딩 중...</span>
          <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-3 border-b border-red-500/20 bg-red-500/10">
        <div className="flex items-center justify-between">
          <span className="text-xs text-red-400">시스템 상태 확인 실패</span>
          <div className="w-2 h-2 bg-red-400 rounded-full"></div>
        </div>
      </div>
    );
  }

  const getOverallStatus = () => {
    const statuses = [status.backend, status.frontend, status.database, status.aiModels];
    if (statuses.includes('error')) return 'error';
    if (statuses.includes('offline')) return 'offline';
    if (statuses.includes('warning')) return 'warning';
    return 'online';
  };

  const overallStatus = getOverallStatus();

  return (
    <div className="p-3 border-b border-cyan-500/20 bg-black/30">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-medium text-slate-300">시스템 상태</span>
        <MenuStatusIndicator status={overallStatus} showDetails={false} />
      </div>
      
      <div className="grid grid-cols-2 gap-2">
        <div className="flex items-center space-x-2">
          <Wifi className="w-3 h-3 text-slate-400" />
          <span className="text-xs text-slate-400">백엔드</span>
          <MenuStatusIndicator status={status.backend} showDetails={false} />
        </div>
        
        <div className="flex items-center space-x-2">
          <Activity className="w-3 h-3 text-slate-400" />
          <span className="text-xs text-slate-400">프론트엔드</span>
          <MenuStatusIndicator status={status.frontend} showDetails={false} />
        </div>
        
        <div className="flex items-center space-x-2">
          <Database className="w-3 h-3 text-slate-400" />
          <span className="text-xs text-slate-400">데이터베이스</span>
          <MenuStatusIndicator status={status.database} showDetails={false} />
        </div>
        
        <div className="flex items-center space-x-2">
          <Brain className="w-3 h-3 text-slate-400" />
          <span className="text-xs text-slate-400">AI 모델</span>
          <MenuStatusIndicator status={status.aiModels} showDetails={false} />
        </div>
      </div>

      {/* 성능 지표 */}
      <div className="mt-2 pt-2 border-t border-cyan-500/10">
        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-400">CPU</span>
          <span className={cn(
            "font-mono",
            status.performance.cpu > 80 ? "text-red-400" :
            status.performance.cpu > 60 ? "text-yellow-400" : "text-green-400"
          )}>
            {status.performance.cpu}%
          </span>
        </div>
        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-400">메모리</span>
          <span className={cn(
            "font-mono",
            status.performance.memory > 80 ? "text-red-400" :
            status.performance.memory > 60 ? "text-yellow-400" : "text-green-400"
          )}>
            {status.performance.memory}%
          </span>
        </div>
        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-400">응답시간</span>
          <span className={cn(
            "font-mono",
            status.performance.responseTime > 1000 ? "text-red-400" :
            status.performance.responseTime > 500 ? "text-yellow-400" : "text-green-400"
          )}>
            {status.performance.responseTime}ms
          </span>
        </div>
      </div>

      {/* 알림 개수 */}
      {status.alerts.length > 0 && (
        <div className="mt-2 pt-2 border-t border-cyan-500/10">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400">활성 알림</span>
            <span className="text-xs bg-red-500/20 text-red-400 px-2 py-1 rounded-full">
              {status.alerts.length}개
            </span>
          </div>
        </div>
      )}
    </div>
  );
}; 
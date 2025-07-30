'use client';

import { PerformanceDashboard } from '@/components/PerformanceOptimizer';
import { SystemStatusWidget, AlertSummaryWidget } from '@/components/DashboardWidgets';
import { MobileBottomNavigation } from '@/components/MobileOptimized';
import { useSystemStatus } from '@/hooks/useSystemStatus';
import { cn } from '@/lib/utils';
import { 
  Server, 
  Database, 
  Monitor, 
  Wifi, 
  CheckCircle, 
  AlertTriangle, 
  XCircle,
  Activity,
  Clock,
  Settings
} from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function SystemHealthPage() {
  const { status, loading, error } = useSystemStatus();

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online': return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'warning': return <AlertTriangle className="w-5 h-5 text-yellow-400" />;
      case 'error': return <XCircle className="w-5 h-5 text-red-400" />;
      default: return <Activity className="w-5 h-5 text-slate-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'text-green-400';
      case 'warning': return 'text-yellow-400';
      case 'error': return 'text-red-400';
      default: return 'text-slate-400';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'online': return '정상';
      case 'warning': return '주의';
      case 'error': return '오류';
      default: return '확인 중';
    }
  };

  const services = [
    {
      name: '백엔드 서버',
      status: status.backend,
      icon: Server,
      description: 'API 서버 및 비즈니스 로직'
    },
    {
      name: '프론트엔드',
      status: status.frontend,
      icon: Monitor,
      description: '웹 인터페이스 및 사용자 경험'
    },
    {
      name: '데이터베이스',
      status: status.database,
      icon: Database,
      description: '데이터 저장 및 관리'
    },
    {
      name: 'AI 모델',
      status: status.aiModels,
      icon: Activity,
      description: '머신러닝 모델 및 예측'
    }
  ];

  return (
    <div className="container mx-auto p-6 pb-20">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white mb-2">시스템 상태</h1>
        <p className="text-slate-400">전체 시스템의 실시간 상태를 모니터링하세요</p>
      </div>

      {/* 전체 시스템 상태 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <SystemStatusWidget />
        <AlertSummaryWidget />
        
        <div className="p-4 rounded-lg border border-cyan-500/20 bg-black/30 backdrop-blur-sm">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-white">전체 상태</h3>
            <div className="flex items-center space-x-2">
              {getStatusIcon(status.backend)}
              <span className={cn("text-xs font-medium", getStatusColor(status.backend))}>
                {getStatusText(status.backend)}
              </span>
            </div>
          </div>
          
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-400">마지막 업데이트</span>
              <span className="text-white">{new Date().toLocaleTimeString()}</span>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-400">가동시간</span>
              <span className="text-white">15일 8시간</span>
            </div>
          </div>
        </div>

        <div className="p-4 rounded-lg border border-cyan-500/20 bg-black/30 backdrop-blur-sm">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-white">빠른 액션</h3>
            <Settings className="w-4 h-4 text-slate-400" />
          </div>
          
          <div className="space-y-2">
            <Button
              variant="ghost"
              size="sm"
              className="w-full justify-start text-xs hover:bg-cyan-500/10"
            >
              <Activity className="w-3 h-3 mr-2" />
              성능 최적화
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="w-full justify-start text-xs hover:bg-cyan-500/10"
            >
              <Clock className="w-3 h-3 mr-2" />
              백업 실행
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="w-full justify-start text-xs hover:bg-cyan-500/10"
            >
              <Wifi className="w-3 h-3 mr-2" />
              네트워크 점검
            </Button>
          </div>
        </div>
      </div>

      {/* 서비스별 상태 */}
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-white mb-4">서비스별 상태</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {services.map((service) => (
            <div key={service.name} className="p-4 rounded-lg border border-cyan-500/20 bg-black/30 backdrop-blur-sm">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <service.icon className="w-5 h-5 text-cyan-400" />
                  <span className="text-sm font-medium text-white">{service.name}</span>
                </div>
                {getStatusIcon(service.status)}
              </div>
              
              <p className="text-xs text-slate-400 mb-3">{service.description}</p>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400">상태</span>
                  <span className={cn("font-medium", getStatusColor(service.status))}>
                    {getStatusText(service.status)}
                  </span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400">응답시간</span>
                  <span className="text-white">{(Math.random() * 100 + 50).toFixed(0)}ms</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 성능 모니터링 */}
      <PerformanceDashboard />
      
      {/* 모바일 하단 네비게이션 */}
      <MobileBottomNavigation />
    </div>
  );
} 
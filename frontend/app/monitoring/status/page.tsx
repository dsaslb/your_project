'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Activity, 
  Server, 
  Database, 
  Globe, 
  Shield,
  Cpu,
  HardDrive,
  Wifi,
  AlertTriangle,
  CheckCircle,
  XCircle,
  RefreshCw
} from 'lucide-react';

interface SystemStatus {
  id: string;
  name: string;
  type: 'server' | 'database' | 'api' | 'network' | 'security';
  status: 'online' | 'offline' | 'warning' | 'error';
  response_time: number;
  uptime: number;
  last_check: string;
  details: {
    cpu_usage: number;
    memory_usage: number;
    disk_usage: number;
    network_latency: number;
  };
}

export default function SystemStatusPage() {
  const [systems, setSystems] = useState<SystemStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  useEffect(() => {
    loadSystemStatus();
    const interval = setInterval(loadSystemStatus, 30000); // 30초마다 업데이트
    return () => clearInterval(interval);
  }, []);

  const loadSystemStatus = async () => {
    try {
      // 실제 API 호출 대신 샘플 데이터 사용
      const sampleData: SystemStatus[] = [
        {
          id: 'main-server',
          name: '메인 서버',
          type: 'server',
          status: 'online',
          response_time: 45,
          uptime: 99.8,
          last_check: new Date().toISOString(),
          details: {
            cpu_usage: 23,
            memory_usage: 67,
            disk_usage: 45,
            network_latency: 12
          }
        },
        {
          id: 'database',
          name: '데이터베이스',
          type: 'database',
          status: 'online',
          response_time: 12,
          uptime: 99.9,
          last_check: new Date().toISOString(),
          details: {
            cpu_usage: 15,
            memory_usage: 78,
            disk_usage: 62,
            network_latency: 5
          }
        },
        {
          id: 'api-gateway',
          name: 'API 게이트웨이',
          type: 'api',
          status: 'online',
          response_time: 28,
          uptime: 99.7,
          last_check: new Date().toISOString(),
          details: {
            cpu_usage: 31,
            memory_usage: 45,
            disk_usage: 23,
            network_latency: 18
          }
        },
        {
          id: 'cdn',
          name: 'CDN 서비스',
          type: 'network',
          status: 'warning',
          response_time: 89,
          uptime: 98.5,
          last_check: new Date().toISOString(),
          details: {
            cpu_usage: 8,
            memory_usage: 23,
            disk_usage: 12,
            network_latency: 45
          }
        },
        {
          id: 'security',
          name: '보안 시스템',
          type: 'security',
          status: 'online',
          response_time: 15,
          uptime: 99.9,
          last_check: new Date().toISOString(),
          details: {
            cpu_usage: 12,
            memory_usage: 34,
            disk_usage: 18,
            network_latency: 8
          }
        }
      ];

      setSystems(sampleData);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('시스템 상태 로드 오류:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'online':
        return <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/50">온라인</Badge>;
      case 'warning':
        return <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/50">경고</Badge>;
      case 'error':
        return <Badge className="bg-red-500/20 text-red-400 border-red-500/50">오류</Badge>;
      case 'offline':
        return <Badge className="bg-slate-500/20 text-slate-400 border-slate-500/50">오프라인</Badge>;
      default:
        return <Badge className="bg-slate-500/20 text-slate-400 border-slate-500/50">알 수 없음</Badge>;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
        return <CheckCircle className="h-5 w-5 text-emerald-400" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-400" />;
      case 'error':
      case 'offline':
        return <XCircle className="h-5 w-5 text-red-400" />;
      default:
        return <Activity className="h-5 w-5 text-slate-400" />;
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'server':
        return <Server className="h-4 w-4" />;
      case 'database':
        return <Database className="h-4 w-4" />;
      case 'api':
        return <Globe className="h-4 w-4" />;
      case 'network':
        return <Wifi className="h-4 w-4" />;
      case 'security':
        return <Shield className="h-4 w-4" />;
      default:
        return <Activity className="h-4 w-4" />;
    }
  };

  const getPerformanceColor = (value: number) => {
    if (value < 50) return 'text-emerald-400';
    if (value < 80) return 'text-yellow-400';
    return 'text-red-400';
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-400"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-purple-600 bg-clip-text text-transparent">
            실시간 시스템 상태
          </h1>
          <p className="text-slate-400 mt-2">시스템 모니터링 및 상태 확인</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="text-sm text-slate-400">마지막 업데이트</p>
            <p className="text-sm text-white">
              {lastUpdate.toLocaleTimeString('ko-KR')}
            </p>
          </div>
          <Button 
            onClick={loadSystemStatus}
            className="bg-cyan-500/20 text-cyan-400 border-cyan-500/50 hover:bg-cyan-500/30"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            새로고침
          </Button>
        </div>
      </div>

      {/* 전체 상태 요약 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="bg-black/50 border-emerald-500/20 backdrop-blur-xl">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">온라인</CardTitle>
            <CheckCircle className="h-4 w-4 text-emerald-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-emerald-400">
              {systems.filter(s => s.status === 'online').length}
            </div>
            <p className="text-xs text-emerald-400">정상 작동</p>
          </CardContent>
        </Card>

        <Card className="bg-black/50 border-yellow-500/20 backdrop-blur-xl">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">경고</CardTitle>
            <AlertTriangle className="h-4 w-4 text-yellow-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-400">
              {systems.filter(s => s.status === 'warning').length}
            </div>
            <p className="text-xs text-yellow-400">주의 필요</p>
          </CardContent>
        </Card>

        <Card className="bg-black/50 border-red-500/20 backdrop-blur-xl">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">오류</CardTitle>
            <XCircle className="h-4 w-4 text-red-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-400">
              {systems.filter(s => s.status === 'error' || s.status === 'offline').length}
            </div>
            <p className="text-xs text-red-400">문제 발생</p>
          </CardContent>
        </Card>

        <Card className="bg-black/50 border-cyan-500/20 backdrop-blur-xl">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">평균 응답시간</CardTitle>
            <Activity className="h-4 w-4 text-cyan-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-cyan-400">
              {Math.round(systems.reduce((acc, s) => acc + s.response_time, 0) / systems.length)}ms
            </div>
            <p className="text-xs text-cyan-400">전체 시스템</p>
          </CardContent>
        </Card>
      </div>

      {/* 시스템 목록 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {systems.map((system) => (
          <Card key={system.id} className="bg-black/50 border-slate-500/20 backdrop-blur-xl hover:border-cyan-500/50 transition-all duration-300">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {getStatusIcon(system.status)}
                  <div>
                    <CardTitle className="text-white flex items-center gap-2">
                      {getTypeIcon(system.type)}
                      {system.name}
                    </CardTitle>
                    <p className="text-sm text-slate-400">
                      응답시간: {system.response_time}ms | 가동률: {system.uptime}%
                    </p>
                  </div>
                </div>
                {getStatusBadge(system.status)}
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* 성능 지표 */}
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-3 bg-slate-800/30 rounded-lg">
                  <div className="flex items-center justify-center gap-1 mb-1">
                    <Cpu className="h-4 w-4 text-blue-400" />
                    <span className={`text-sm font-semibold ${getPerformanceColor(system.details.cpu_usage)}`}>
                      {system.details.cpu_usage}%
                    </span>
                  </div>
                  <p className="text-xs text-slate-400">CPU</p>
                </div>
                <div className="text-center p-3 bg-slate-800/30 rounded-lg">
                  <div className="flex items-center justify-center gap-1 mb-1">
                    <HardDrive className="h-4 w-4 text-purple-400" />
                    <span className={`text-sm font-semibold ${getPerformanceColor(system.details.memory_usage)}`}>
                      {system.details.memory_usage}%
                    </span>
                  </div>
                  <p className="text-xs text-slate-400">메모리</p>
                </div>
                <div className="text-center p-3 bg-slate-800/30 rounded-lg">
                  <div className="flex items-center justify-center gap-1 mb-1">
                    <Database className="h-4 w-4 text-emerald-400" />
                    <span className={`text-sm font-semibold ${getPerformanceColor(system.details.disk_usage)}`}>
                      {system.details.disk_usage}%
                    </span>
                  </div>
                  <p className="text-xs text-slate-400">디스크</p>
                </div>
                <div className="text-center p-3 bg-slate-800/30 rounded-lg">
                  <div className="flex items-center justify-center gap-1 mb-1">
                    <Wifi className="h-4 w-4 text-orange-400" />
                    <span className={`text-sm font-semibold ${getPerformanceColor(system.details.network_latency)}`}>
                      {system.details.network_latency}ms
                    </span>
                  </div>
                  <p className="text-xs text-slate-400">네트워크</p>
                </div>
              </div>

              {/* 액션 버튼 */}
              <div className="flex gap-2">
                <Button size="sm" className="flex-1 bg-blue-500/20 text-blue-400 border-blue-500/50 hover:bg-blue-500/30">
                  상세 보기
                </Button>
                <Button size="sm" variant="outline" className="border-slate-500/50 text-slate-400 hover:bg-slate-500/10">
                  로그 확인
                </Button>
              </div>

              <div className="text-xs text-slate-400">
                마지막 확인: {new Date(system.last_check).toLocaleTimeString('ko-KR')}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
} 
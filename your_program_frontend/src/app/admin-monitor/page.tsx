'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Shield, 
  Server, 
  Database, 
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  Users,
  BarChart3,
  HardDrive,
  Network,
  Cpu,
  MemoryStick
} from 'lucide-react';
import useUserStore from '@/store/useUserStore';
import { useRouter } from 'next/navigation';

export default function AdminMonitorPage() {
  const { user, isSuperAdmin } = useUserStore();
  const router = useRouter();

  // 권한 확인
  if (!user || !isSuperAdmin()) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="w-96">
          <CardHeader>
            <CardTitle className="text-red-600">접근 권한 없음</CardTitle>
            <CardDescription>
              슈퍼 관리자 권한이 필요합니다.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => router.push('/dashboard')}>
              대시보드로 돌아가기
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // 더미 데이터
  const systemStatus = {
    overall: "정상",
    uptime: "15일 8시간 32분",
    lastBackup: "2024-01-15 02:00:00",
    nextBackup: "2024-01-16 02:00:00",
    services: [
      { name: "웹 서버", status: "정상", uptime: "15일 8시간", response: "45ms" },
      { name: "데이터베이스", status: "정상", uptime: "15일 8시간", response: "12ms" },
      { name: "캐시 서버", status: "정상", uptime: "15일 8시간", response: "3ms" },
      { name: "이메일 서비스", status: "정상", uptime: "15일 8시간", response: "120ms" },
      { name: "백업 서비스", status: "점검 필요", uptime: "2일 5시간", response: "N/A" },
    ],
    resources: {
      cpu: { usage: 23, status: "정상" },
      memory: { usage: 67, status: "정상" },
      disk: { usage: 45, status: "정상" },
      network: { usage: 12, status: "정상" },
    },
    alerts: [
      { id: 1, level: "warning", message: "백업 서비스 점검 필요", time: "1시간 전" },
      { id: 2, level: "info", message: "시스템 업데이트 완료", time: "3시간 전" },
      { id: 3, level: "info", message: "데이터베이스 최적화 완료", time: "6시간 전" },
    ],
    logs: [
      { id: 1, level: "INFO", message: "사용자 로그인: admin", time: "2분 전" },
      { id: 2, level: "INFO", message: "새 사용자 등록: user123", time: "5분 전" },
      { id: 3, level: "WARNING", message: "백업 서비스 응답 지연", time: "10분 전" },
      { id: 4, level: "INFO", message: "시스템 점검 완료", time: "15분 전" },
    ]
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "정상": return "bg-green-500";
      case "점검 필요": return "bg-yellow-500";
      case "오류": return "bg-red-500";
      default: return "bg-gray-500";
    }
  };

  const getLevelColor = (level: string) => {
    switch (level) {
      case "error": return "bg-red-500";
      case "warning": return "bg-yellow-500";
      case "info": return "bg-blue-500";
      default: return "bg-gray-500";
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center space-x-3">
            <Shield className="w-8 h-8 text-blue-600" />
            <span>시스템 모니터링</span>
          </h1>
          <p className="text-gray-600 mt-2">
            전체 시스템 상태 및 성능 모니터링
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="default" className="bg-blue-600">
            <Shield className="w-3 h-3 mr-1" />
            시스템 관리자
          </Badge>
          <Badge variant="outline">
            {user.name}
          </Badge>
        </div>
      </div>

      {/* 전체 상태 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">전체 상태</CardTitle>
            <div className={`w-3 h-3 rounded-full ${getStatusColor(systemStatus.overall)}`}></div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{systemStatus.overall}</div>
            <p className="text-xs text-muted-foreground">
              모든 시스템 정상
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">가동 시간</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemStatus.uptime}</div>
            <p className="text-xs text-muted-foreground">
              마지막 재시작 이후
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">마지막 백업</CardTitle>
            <HardDrive className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemStatus.lastBackup}</div>
            <p className="text-xs text-muted-foreground">
              다음 백업: {systemStatus.nextBackup}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">활성 세션</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">23</div>
            <p className="text-xs text-muted-foreground">
              현재 접속 중
            </p>
          </CardContent>
        </Card>
      </div>

      {/* 리소스 사용량 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Cpu className="h-5 w-5" />
            <span>리소스 사용량</span>
          </CardTitle>
          <CardDescription>
            시스템 리소스 실시간 모니터링
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">CPU</span>
                <span className="text-sm text-muted-foreground">{systemStatus.resources.cpu.usage}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full" 
                  style={{width: `${systemStatus.resources.cpu.usage}%`}}
                ></div>
              </div>
              <Badge variant={systemStatus.resources.cpu.status === "정상" ? "default" : "destructive"}>
                {systemStatus.resources.cpu.status}
              </Badge>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">메모리</span>
                <span className="text-sm text-muted-foreground">{systemStatus.resources.memory.usage}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-green-600 h-2 rounded-full" 
                  style={{width: `${systemStatus.resources.memory.usage}%`}}
                ></div>
              </div>
              <Badge variant={systemStatus.resources.memory.status === "정상" ? "default" : "destructive"}>
                {systemStatus.resources.memory.status}
              </Badge>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">디스크</span>
                <span className="text-sm text-muted-foreground">{systemStatus.resources.disk.usage}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-yellow-600 h-2 rounded-full" 
                  style={{width: `${systemStatus.resources.disk.usage}%`}}
                ></div>
              </div>
              <Badge variant={systemStatus.resources.disk.status === "정상" ? "default" : "destructive"}>
                {systemStatus.resources.disk.status}
              </Badge>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">네트워크</span>
                <span className="text-sm text-muted-foreground">{systemStatus.resources.network.usage}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-purple-600 h-2 rounded-full" 
                  style={{width: `${systemStatus.resources.network.usage}%`}}
                ></div>
              </div>
              <Badge variant={systemStatus.resources.network.status === "정상" ? "default" : "destructive"}>
                {systemStatus.resources.network.status}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 서비스 상태 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Server className="h-5 w-5" />
              <span>서비스 상태</span>
            </CardTitle>
            <CardDescription>
              각 서비스의 현재 상태 및 응답 시간
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {systemStatus.services.map((service) => (
                <div key={service.name} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${getStatusColor(service.status)}`}></div>
                    <div>
                      <h3 className="font-medium">{service.name}</h3>
                      <p className="text-sm text-muted-foreground">가동시간: {service.uptime}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">{service.response}</p>
                    <Badge variant={service.status === "정상" ? "default" : "destructive"}>
                      {service.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* 시스템 알림 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5" />
              <span>시스템 알림</span>
            </CardTitle>
            <CardDescription>
              주의가 필요한 시스템 알림들
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {systemStatus.alerts.map((alert) => (
                <div key={alert.id} className="flex items-center justify-between p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                  <div>
                    <p className="font-medium text-sm">{alert.message}</p>
                    <p className="text-xs text-muted-foreground">{alert.time}</p>
                  </div>
                  <Badge variant={alert.level === "warning" ? "destructive" : "secondary"}>
                    {alert.level === "warning" ? "경고" : "정보"}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 시스템 로그 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Activity className="h-5 w-5" />
            <span>시스템 로그</span>
          </CardTitle>
          <CardDescription>
            최근 시스템 로그 (실시간)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {systemStatus.logs.map((log) => (
              <div key={log.id} className="flex items-center space-x-3 p-2 bg-gray-50 dark:bg-gray-800 rounded">
                <div className={`w-2 h-2 rounded-full ${getLevelColor(log.level.toLowerCase())}`}></div>
                <div className="flex-1">
                  <p className="text-sm font-medium">{log.message}</p>
                  <p className="text-xs text-muted-foreground">{log.time}</p>
                </div>
                <Badge variant="outline" className="text-xs">
                  {log.level}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 빠른 액션 */}
      <Card>
        <CardHeader>
          <CardTitle>빠른 액션</CardTitle>
          <CardDescription>
            시스템 관리 기능들
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Button variant="outline" className="h-16 flex flex-col space-y-2">
              <HardDrive className="h-5 w-5" />
              <span className="text-sm">백업 실행</span>
            </Button>
            <Button variant="outline" className="h-16 flex flex-col space-y-2">
              <Server className="h-5 w-5" />
              <span className="text-sm">서비스 재시작</span>
            </Button>
            <Button variant="outline" className="h-16 flex flex-col space-y-2">
              <Database className="h-5 w-5" />
              <span className="text-sm">DB 최적화</span>
            </Button>
            <Button variant="outline" className="h-16 flex flex-col space-y-2">
              <Network className="h-5 w-5" />
              <span className="text-sm">네트워크 점검</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 
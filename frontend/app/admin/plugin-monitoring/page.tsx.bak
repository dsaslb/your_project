"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { toast } from "sonner";
import { 
  Activity, AlertTriangle, CheckCircle, Clock, Cpu, 
  Database, HardDrive, Network, Server, Shield, 
  TrendingUp, TrendingDown, Loader2, RefreshCw, 
  Eye, EyeOff, Bell, BellOff, Settings, BarChart3
} from "lucide-react";

const dummySystemStatus = {
  system_status: "healthy",
  total_plugins: 15,
  active_plugins: 12,
  error_plugins: 1,
  avg_response_time_ms: 245.6,
  avg_cpu_usage_percent: 23.4,
  avg_memory_usage_mb: 156.8,
  total_api_calls: 1247,
  error_rate_percent: 2.1,
  network_latency_ms: 45.2,
  network_throughput_mbps: 125.6,
  last_updated: "2024-07-26 16:30:00"
};

const dummyPlugins = [
  {
    id: 1,
    name: "ai_schedule_optimizer",
    display_name: "AI 스케줄 최적화",
    status: "healthy",
    response_time_ms: 180.5,
    cpu_usage_percent: 15.2,
    memory_usage_mb: 45.6,
    api_calls_count: 156,
    api_errors_count: 2,
    error_rate_percent: 1.3,
    last_health_check: "2024-07-26 16:29:45",
    uptime_hours: 72.5
  },
  {
    id: 2,
    name: "review_auto_summary",
    display_name: "리뷰 자동 요약",
    status: "warning",
    response_time_ms: 850.2,
    cpu_usage_percent: 45.8,
    memory_usage_mb: 89.3,
    api_calls_count: 89,
    api_errors_count: 5,
    error_rate_percent: 5.6,
    last_health_check: "2024-07-26 16:29:30",
    uptime_hours: 48.2
  },
  {
    id: 3,
    name: "qsc_analyzer",
    display_name: "QSC 분석기",
    status: "unhealthy",
    response_time_ms: 2500.0,
    cpu_usage_percent: 78.9,
    memory_usage_mb: 234.1,
    api_calls_count: 23,
    api_errors_count: 8,
    error_rate_percent: 34.8,
    last_health_check: "2024-07-26 16:28:15",
    uptime_hours: 12.3
  }
];

const dummyAlerts = [
  {
    id: 1,
    plugin_id: 2,
    plugin_name: "리뷰 자동 요약",
    alert_type: "performance",
    alert_level: "warning",
    alert_title: "응답 시간 초과",
    alert_message: "응답 시간이 850ms로 임계값 500ms를 초과했습니다.",
    threshold_value: 500,
    current_value: 850.2,
    is_acknowledged: false,
    created_at: "2024-07-26 16:25:30"
  },
  {
    id: 2,
    plugin_id: 3,
    plugin_name: "QSC 분석기",
    alert_type: "error",
    alert_level: "critical",
    alert_title: "오류율 초과",
    alert_message: "오류율이 34.8%로 임계값 5%를 초과했습니다.",
    threshold_value: 5,
    current_value: 34.8,
    is_acknowledged: false,
    created_at: "2024-07-26 16:20:15"
  },
  {
    id: 3,
    plugin_id: 3,
    plugin_name: "QSC 분석기",
    alert_type: "resource",
    alert_level: "error",
    alert_title: "메모리 사용량 초과",
    alert_message: "메모리 사용량이 234MB로 임계값 200MB를 초과했습니다.",
    threshold_value: 200,
    current_value: 234.1,
    is_acknowledged: true,
    created_at: "2024-07-26 16:15:45"
  }
];

const dummyErrorLogs = [
  {
    id: 1,
    plugin_id: 3,
    plugin_name: "QSC 분석기",
    error_type: "timeout",
    error_message: "API 요청 타임아웃 (30초 초과)",
    severity_level: "error",
    occurred_at: "2024-07-26 16:28:15",
    is_resolved: false
  },
  {
    id: 2,
    plugin_id: 2,
    plugin_name: "리뷰 자동 요약",
    error_type: "permission_denied",
    error_message: "데이터베이스 접근 권한 없음",
    severity_level: "warning",
    occurred_at: "2024-07-26 16:25:30",
    is_resolved: true
  },
  {
    id: 3,
    plugin_id: 1,
    plugin_name: "AI 스케줄 최적화",
    error_type: "resource_limit",
    error_message: "메모리 사용량 제한 초과",
    severity_level: "info",
    occurred_at: "2024-07-26 16:20:00",
    is_resolved: true
  }
];

const statusMap = {
  healthy: { label: "정상", color: "bg-green-100 text-green-700", icon: CheckCircle },
  warning: { label: "경고", color: "bg-yellow-100 text-yellow-700", icon: AlertTriangle },
  unhealthy: { label: "비정상", color: "bg-red-100 text-red-700", icon: AlertTriangle },
  critical: { label: "위험", color: "bg-red-100 text-red-700", icon: AlertTriangle },
  maintenance: { label: "점검", color: "bg-blue-100 text-blue-700", icon: Clock }
};

const alertLevelMap = {
  info: { label: "정보", color: "bg-blue-100 text-blue-700" },
  warning: { label: "경고", color: "bg-yellow-100 text-yellow-700" },
  error: { label: "오류", color: "bg-red-100 text-red-700" },
  critical: { label: "위험", color: "bg-red-100 text-red-700" }
};

export default function AdminPluginMonitoringPage() {
  const [systemStatus, setSystemStatus] = useState(dummySystemStatus);
  const [plugins, setPlugins] = useState(dummyPlugins);
  const [alerts, setAlerts] = useState(dummyAlerts);
  const [errorLogs, setErrorLogs] = useState(dummyErrorLogs);
  const [activeTab, setActiveTab] = useState("overview");
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  // 실시간 데이터 업데이트 시뮬레이션
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      // 시스템 상태 업데이트
      setSystemStatus(prev => ({
        ...prev,
        total_api_calls: prev.total_api_calls + Math.floor(Math.random() * 10),
        avg_response_time_ms: prev.avg_response_time_ms + (Math.random() - 0.5) * 10,
        last_updated: new Date().toLocaleString()
      }));

      // 플러그인 상태 업데이트
      setPlugins(prev => prev.map(plugin => ({
        ...plugin,
        response_time_ms: plugin.response_time_ms + (Math.random() - 0.5) * 20,
        cpu_usage_percent: Math.max(0, Math.min(100, plugin.cpu_usage_percent + (Math.random() - 0.5) * 5)),
        last_health_check: new Date().toLocaleString()
      })));
    }, 5000); // 5초마다 업데이트

    return () => clearInterval(interval);
  }, [autoRefresh]);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      toast.success("모니터링 데이터가 새로고침되었습니다.");
    } catch (error) {
      toast.error("데이터 새로고침 중 오류가 발생했습니다.");
    } finally {
      setRefreshing(false);
    }
  };

  const handleAcknowledgeAlert = async (alertId: number) => {
    try {
      setAlerts(prev => prev.map(alert => 
        alert.id === alertId 
          ? { ...alert, is_acknowledged: true }
          : alert
      ));
      toast.success("알림이 확인되었습니다.");
    } catch (error) {
      toast.error("알림 확인 처리 중 오류가 발생했습니다.");
    }
  };

  const handleResolveError = async (errorId: number) => {
    try {
      setErrorLogs(prev => prev.map(error => 
        error.id === errorId 
          ? { ...error, is_resolved: true }
          : error
      ));
      toast.success("오류가 해결되었습니다.");
    } catch (error) {
      toast.error("오류 해결 처리 중 오류가 발생했습니다.");
    }
  };

  const tabs = [
    { id: "overview", label: "시스템 개요", icon: Activity },
    { id: "plugins", label: "플러그인 상태", icon: Server },
    { id: "alerts", label: "알림 관리", icon: Bell },
    { id: "errors", label: "오류 로그", icon: AlertTriangle },
    { id: "metrics", label: "성능 메트릭", icon: BarChart3 },
  ];

  return (
    <div className="container mx-auto p-6 max-w-7xl space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">플러그인 모니터링 대시보드</h1>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setAutoRefresh(!autoRefresh)}
            className="flex items-center gap-2"
          >
            {autoRefresh ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
            {autoRefresh ? "실시간" : "수동"}
          </Button>
          <Button
            onClick={handleRefresh}
            disabled={refreshing}
            className="flex items-center gap-2"
          >
            {refreshing ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
            새로고침
          </Button>
        </div>
      </div>

      {/* 탭 네비게이션 */}
      <div className="flex border-b">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 border-b-2 transition-colors ${
              activeTab === tab.id
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            <tab.icon className="h-4 w-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* 시스템 개요 탭 */}
      {activeTab === "overview" && (
        <div className="space-y-6">
          {/* 시스템 상태 카드 */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">시스템 상태</CardTitle>
                <Badge className={statusMap[systemStatus.system_status].color}>
                  <statusMap[systemStatus.system_status].icon className="h-3 w-3 mr-1" />
                  {statusMap[systemStatus.system_status].label}
                </Badge>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{systemStatus.total_plugins}</div>
                <p className="text-xs text-muted-foreground">
                  활성: {systemStatus.active_plugins} | 오류: {systemStatus.error_plugins}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">평균 응답 시간</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{systemStatus.avg_response_time_ms.toFixed(1)}ms</div>
                <p className="text-xs text-muted-foreground">
                  마지막 업데이트: {systemStatus.last_updated}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">오류율</CardTitle>
                <AlertTriangle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{systemStatus.error_rate_percent.toFixed(1)}%</div>
                <p className="text-xs text-muted-foreground">
                  총 API 호출: {systemStatus.total_api_calls}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">리소스 사용량</CardTitle>
                <Cpu className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{systemStatus.avg_cpu_usage_percent.toFixed(1)}%</div>
                <p className="text-xs text-muted-foreground">
                  메모리: {systemStatus.avg_memory_usage_mb.toFixed(1)}MB
                </p>
              </CardContent>
            </Card>
          </div>

          {/* 성능 메트릭 차트 */}
          <Card>
            <CardHeader>
              <CardTitle>실시간 성능 메트릭</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">CPU 사용량</span>
                    <span className="text-sm text-muted-foreground">{systemStatus.avg_cpu_usage_percent.toFixed(1)}%</span>
                  </div>
                  <Progress value={systemStatus.avg_cpu_usage_percent} className="h-2" />
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">메모리 사용량</span>
                    <span className="text-sm text-muted-foreground">{systemStatus.avg_memory_usage_mb.toFixed(1)}MB</span>
                  </div>
                  <Progress value={(systemStatus.avg_memory_usage_mb / 512) * 100} className="h-2" />
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">네트워크 지연</span>
                    <span className="text-sm text-muted-foreground">{systemStatus.network_latency_ms.toFixed(1)}ms</span>
                  </div>
                  <Progress value={(systemStatus.network_latency_ms / 100) * 100} className="h-2" />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 최근 알림 */}
          <Card>
            <CardHeader>
              <CardTitle>최근 알림</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {alerts.slice(0, 3).map((alert) => (
                  <div key={alert.id} className="flex items-center justify-between p-3 border rounded">
                    <div className="flex items-center gap-3">
                      <Badge className={alertLevelMap[alert.alert_level].color}>
                        {alertLevelMap[alert.alert_level].label}
                      </Badge>
                      <div>
                        <div className="font-medium">{alert.alert_title}</div>
                        <div className="text-sm text-muted-foreground">{alert.plugin_name}</div>
                      </div>
                    </div>
                    <div className="text-sm text-muted-foreground">{alert.created_at}</div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 플러그인 상태 탭 */}
      {activeTab === "plugins" && (
        <Card>
          <CardHeader>
            <CardTitle>플러그인 상태 모니터링</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {plugins.map((plugin) => (
                <div key={plugin.id} className="border rounded p-4">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="font-semibold">{plugin.display_name}</h3>
                      <div className="text-sm text-muted-foreground">
                        마지막 헬스체크: {plugin.last_health_check} | 가동시간: {plugin.uptime_hours.toFixed(1)}시간
                      </div>
                    </div>
                    <Badge className={statusMap[plugin.status].color}>
                      <statusMap[plugin.status].icon className="h-3 w-3 mr-1" />
                      {statusMap[plugin.status].label}
                    </Badge>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <div className="text-muted-foreground">응답 시간</div>
                      <div className="font-medium">{plugin.response_time_ms.toFixed(1)}ms</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">CPU 사용량</div>
                      <div className="font-medium">{plugin.cpu_usage_percent.toFixed(1)}%</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">메모리 사용량</div>
                      <div className="font-medium">{plugin.memory_usage_mb.toFixed(1)}MB</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">오류율</div>
                      <div className="font-medium">{plugin.error_rate_percent.toFixed(1)}%</div>
                    </div>
                  </div>

                  <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs">CPU</span>
                        <span className="text-xs">{plugin.cpu_usage_percent.toFixed(1)}%</span>
                      </div>
                      <Progress value={plugin.cpu_usage_percent} className="h-1" />
                    </div>
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs">메모리</span>
                        <span className="text-xs">{plugin.memory_usage_mb.toFixed(1)}MB</span>
                      </div>
                      <Progress value={(plugin.memory_usage_mb / 512) * 100} className="h-1" />
                    </div>
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs">오류율</span>
                        <span className="text-xs">{plugin.error_rate_percent.toFixed(1)}%</span>
                      </div>
                      <Progress value={plugin.error_rate_percent} className="h-1" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 알림 관리 탭 */}
      {activeTab === "alerts" && (
        <Card>
          <CardHeader>
            <CardTitle>알림 관리</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {alerts.map((alert) => (
                <div key={alert.id} className="border rounded p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <Badge className={alertLevelMap[alert.alert_level].color}>
                        {alertLevelMap[alert.alert_level].label}
                      </Badge>
                      <div>
                        <div className="font-medium">{alert.alert_title}</div>
                        <div className="text-sm text-muted-foreground">{alert.plugin_name}</div>
                      </div>
                    </div>
                    <div className="text-sm text-muted-foreground">{alert.created_at}</div>
                  </div>
                  
                  <div className="mb-3">
                    <p className="text-sm">{alert.alert_message}</p>
                    <div className="text-xs text-muted-foreground mt-1">
                      임계값: {alert.threshold_value} | 현재값: {alert.current_value}
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <Badge variant={alert.is_acknowledged ? "default" : "secondary"}>
                      {alert.is_acknowledged ? "확인됨" : "미확인"}
                    </Badge>
                    {!alert.is_acknowledged && (
                      <Button
                        size="sm"
                        onClick={() => handleAcknowledgeAlert(alert.id)}
                      >
                        확인
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 오류 로그 탭 */}
      {activeTab === "errors" && (
        <Card>
          <CardHeader>
            <CardTitle>오류 로그</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="bg-muted">
                    <th className="p-2 text-left">시간</th>
                    <th className="p-2 text-left">플러그인</th>
                    <th className="p-2 text-left">오류 타입</th>
                    <th className="p-2 text-left">메시지</th>
                    <th className="p-2 text-left">심각도</th>
                    <th className="p-2 text-left">상태</th>
                    <th className="p-2 text-left">조치</th>
                  </tr>
                </thead>
                <tbody>
                  {errorLogs.map((error) => (
                    <tr key={error.id} className="border-b">
                      <td className="p-2">{error.occurred_at}</td>
                      <td className="p-2 font-medium">{error.plugin_name}</td>
                      <td className="p-2">{error.error_type}</td>
                      <td className="p-2">{error.error_message}</td>
                      <td className="p-2">
                        <Badge className={alertLevelMap[error.severity_level].color}>
                          {alertLevelMap[error.severity_level].label}
                        </Badge>
                      </td>
                      <td className="p-2">
                        <Badge variant={error.is_resolved ? "default" : "secondary"}>
                          {error.is_resolved ? "해결됨" : "미해결"}
                        </Badge>
                      </td>
                      <td className="p-2">
                        {!error.is_resolved && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleResolveError(error.id)}
                          >
                            해결
                          </Button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 성능 메트릭 탭 */}
      {activeTab === "metrics" && (
        <Card>
          <CardHeader>
            <CardTitle>성능 메트릭 분석</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-semibold mb-4">응답 시간 트렌드</h3>
                <div className="space-y-2">
                  {plugins.map((plugin) => (
                    <div key={plugin.id} className="flex items-center justify-between">
                      <span className="text-sm">{plugin.display_name}</span>
                      <div className="flex items-center gap-2">
                        <div className="w-20 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full" 
                            style={{ width: `${Math.min((plugin.response_time_ms / 1000) * 100, 100)}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium">{plugin.response_time_ms.toFixed(0)}ms</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="font-semibold mb-4">리소스 사용량</h3>
                <div className="space-y-4">
                  {plugins.map((plugin) => (
                    <div key={plugin.id}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm">{plugin.display_name}</span>
                        <span className="text-sm font-medium">{plugin.cpu_usage_percent.toFixed(1)}%</span>
                      </div>
                      <Progress value={plugin.cpu_usage_percent} className="h-2" />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
} 
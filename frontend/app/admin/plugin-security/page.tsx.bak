"use client";

import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { Shield, AlertTriangle, CheckCircle, XCircle, Settings, Activity, Lock } from "lucide-react";

const dummyPlugins = [
  {
    id: 1,
    name: "ai_schedule_optimizer",
    display_name: "AI 스케줄 최적화",
    status: "active",
    security_level: "high",
    permissions: {
      data_access: {
        schedule: true,
        employee: false,
        sales: false,
        inventory: false,
        reviews: false,
        qsc: false,
        contracts: false,
      },
      api_access: {
        read: true,
        write: false,
        delete: false,
        admin: false,
        external: false,
      },
      execution_limits: {
        max_execution_time: 30,
        max_memory_mb: 512,
        max_db_queries: 100,
        max_file_size_mb: 10,
        allow_file_upload: false,
        allow_network: false,
      },
    },
  },
  {
    id: 2,
    name: "review_auto_summary",
    display_name: "리뷰 자동 요약",
    status: "active",
    security_level: "medium",
    permissions: {
      data_access: {
        schedule: false,
        employee: false,
        sales: false,
        inventory: false,
        reviews: true,
        qsc: false,
        contracts: false,
      },
      api_access: {
        read: true,
        write: true,
        delete: false,
        admin: false,
        external: true,
      },
      execution_limits: {
        max_execution_time: 60,
        max_memory_mb: 1024,
        max_db_queries: 200,
        max_file_size_mb: 50,
        allow_file_upload: true,
        allow_network: true,
      },
    },
  },
];

const dummySecurityLogs = [
  {
    id: 1,
    plugin_id: 1,
    event_type: "permission_violation",
    security_level: "warning",
    details: "직원 정보 접근 시도",
    timestamp: "2024-07-26 15:30:00",
    status: "resolved",
  },
  {
    id: 2,
    plugin_id: 2,
    event_type: "resource_limit",
    security_level: "error",
    details: "메모리 사용량 초과 (1.2GB/1GB)",
    timestamp: "2024-07-26 14:45:00",
    status: "pending",
  },
  {
    id: 3,
    plugin_id: 1,
    event_type: "suspicious_activity",
    security_level: "critical",
    details: "외부 API 호출 시도",
    timestamp: "2024-07-26 13:20:00",
    status: "reviewed",
  },
];

const dummyResourceUsage = [
  {
    plugin_id: 1,
    cpu_usage_percent: 15,
    memory_usage_mb: 256,
    execution_time_seconds: 5,
    db_queries_count: 45,
    is_over_limit: false,
  },
  {
    plugin_id: 2,
    cpu_usage_percent: 85,
    memory_usage_mb: 950,
    execution_time_seconds: 45,
    db_queries_count: 180,
    is_over_limit: true,
  },
];

export default function AdminPluginSecurityPage() {
  const [plugins, setPlugins] = useState(dummyPlugins);
  const [securityLogs, setSecurityLogs] = useState(dummySecurityLogs);
  const [resourceUsage, setResourceUsage] = useState(dummyResourceUsage);
  const [selectedPlugin, setSelectedPlugin] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState("overview");

  const securityLevelMap = {
    high: { label: "높음", color: "bg-green-100 text-green-700", icon: CheckCircle },
    medium: { label: "보통", color: "bg-yellow-100 text-yellow-700", icon: AlertTriangle },
    low: { label: "낮음", color: "bg-red-100 text-red-700", icon: XCircle },
  };

  const securityLevelMap2 = {
    info: { label: "정보", color: "bg-blue-100 text-blue-700" },
    warning: { label: "경고", color: "bg-yellow-100 text-yellow-700" },
    error: { label: "오류", color: "bg-red-100 text-red-700" },
    critical: { label: "심각", color: "bg-red-200 text-red-800" },
  };

  const handlePermissionChange = (pluginId: number, permissionType: string, resource: string, value: boolean) => {
    setPlugins(prev =>
      prev.map(p =>
        p.id === pluginId
          ? {
              ...p,
              permissions: {
                ...p.permissions,
                [permissionType]: {
                  ...p.permissions[permissionType],
                  [resource]: value,
                },
              },
            }
          : p
      )
    );
    toast.success("권한 설정이 업데이트되었습니다.");
  };

  const handleSecurityLogAction = (logId: number, action: string) => {
    setSecurityLogs(prev =>
      prev.map(log =>
        log.id === logId
          ? { ...log, status: action }
          : log
      )
    );
    toast.success(`보안 로그 상태가 ${action}로 변경되었습니다.`);
  };

  const tabs = [
    { id: "overview", label: "보안 개요", icon: Shield },
    { id: "permissions", label: "권한 관리", icon: Lock },
    { id: "logs", label: "보안 로그", icon: Activity },
    { id: "resources", label: "리소스 모니터링", icon: Settings },
  ];

  return (
    <div className="container mx-auto p-6 max-w-6xl space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">플러그인 보안 관리</h1>
        <Button className="flex items-center gap-2">
          <Shield className="h-4 w-4" />
          보안 정책 설정
        </Button>
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

      {/* 보안 개요 탭 */}
      {activeTab === "overview" && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                보안 상태
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>활성 플러그인</span>
                  <span className="font-bold">{plugins.filter(p => p.status === "active").length}</span>
                </div>
                <div className="flex justify-between">
                  <span>높은 보안 레벨</span>
                  <span className="font-bold text-green-600">
                    {plugins.filter(p => p.security_level === "high").length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>보안 위반</span>
                  <span className="font-bold text-red-600">
                    {securityLogs.filter(log => log.security_level === "critical").length}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                리소스 사용량
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>정상 플러그인</span>
                  <span className="font-bold text-green-600">
                    {resourceUsage.filter(r => !r.is_over_limit).length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>제한 초과</span>
                  <span className="font-bold text-red-600">
                    {resourceUsage.filter(r => r.is_over_limit).length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>평균 CPU 사용률</span>
                  <span className="font-bold">
                    {(resourceUsage.reduce((sum, r) => sum + r.cpu_usage_percent, 0) / resourceUsage.length).toFixed(1)}%
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" />
                최근 보안 이벤트
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {securityLogs.slice(0, 3).map((log) => (
                  <div key={log.id} className="flex items-center justify-between text-sm">
                    <span className="truncate">{log.details}</span>
                    <Badge className={securityLevelMap2[log.security_level].color}>
                      {securityLevelMap2[log.security_level].label}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 권한 관리 탭 */}
      {activeTab === "permissions" && (
        <Card>
          <CardHeader>
            <CardTitle>플러그인 권한 관리</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {plugins.map((plugin) => (
                <div key={plugin.id} className="border rounded p-4">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="font-semibold">{plugin.display_name}</h3>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge className={securityLevelMap[plugin.security_level].color}>
                          <securityLevelMap[plugin.security_level].icon className="h-3 w-3 mr-1" />
                          {securityLevelMap[plugin.security_level].label}
                        </Badge>
                        <span className="text-sm text-muted-foreground">{plugin.name}</span>
                      </div>
                    </div>
                    <Button
                      size="sm"
                      variant={selectedPlugin === plugin.id ? "default" : "outline"}
                      onClick={() => setSelectedPlugin(selectedPlugin === plugin.id ? null : plugin.id)}
                    >
                      {selectedPlugin === plugin.id ? "접기" : "권한 설정"}
                    </Button>
                  </div>

                  {selectedPlugin === plugin.id && (
                    <div className="space-y-4">
                      {/* 데이터 접근 권한 */}
                      <div>
                        <h4 className="font-medium mb-2">데이터 접근 권한</h4>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                          {Object.entries(plugin.permissions.data_access).map(([resource, allowed]) => (
                            <label key={resource} className="flex items-center space-x-2">
                              <input
                                type="checkbox"
                                checked={allowed}
                                onChange={(e) => handlePermissionChange(plugin.id, "data_access", resource, e.target.checked)}
                                className="h-4 w-4"
                              />
                              <span className="text-sm">{resource}</span>
                            </label>
                          ))}
                        </div>
                      </div>

                      {/* API 접근 권한 */}
                      <div>
                        <h4 className="font-medium mb-2">API 접근 권한</h4>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                          {Object.entries(plugin.permissions.api_access).map(([resource, allowed]) => (
                            <label key={resource} className="flex items-center space-x-2">
                              <input
                                type="checkbox"
                                checked={allowed}
                                onChange={(e) => handlePermissionChange(plugin.id, "api_access", resource, e.target.checked)}
                                className="h-4 w-4"
                              />
                              <span className="text-sm">{resource}</span>
                            </label>
                          ))}
                        </div>
                      </div>

                      {/* 실행 제한 */}
                      <div>
                        <h4 className="font-medium mb-2">실행 제한</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <label className="block text-sm font-medium mb-1">최대 실행시간 (초)</label>
                            <input
                              type="number"
                              value={plugin.permissions.execution_limits.max_execution_time}
                              onChange={(e) => {
                                const newValue = parseInt(e.target.value);
                                setPlugins(prev =>
                                  prev.map(p =>
                                    p.id === plugin.id
                                      ? {
                                          ...p,
                                          permissions: {
                                            ...p.permissions,
                                            execution_limits: {
                                              ...p.permissions.execution_limits,
                                              max_execution_time: newValue,
                                            },
                                          },
                                        }
                                      : p
                                  )
                                );
                              }}
                              className="border rounded px-2 py-1 w-full"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium mb-1">최대 메모리 (MB)</label>
                            <input
                              type="number"
                              value={plugin.permissions.execution_limits.max_memory_mb}
                              onChange={(e) => {
                                const newValue = parseInt(e.target.value);
                                setPlugins(prev =>
                                  prev.map(p =>
                                    p.id === plugin.id
                                      ? {
                                          ...p,
                                          permissions: {
                                            ...p.permissions,
                                            execution_limits: {
                                              ...p.permissions.execution_limits,
                                              max_memory_mb: newValue,
                                            },
                                          },
                                        }
                                      : p
                                  )
                                );
                              }}
                              className="border rounded px-2 py-1 w-full"
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 보안 로그 탭 */}
      {activeTab === "logs" && (
        <Card>
          <CardHeader>
            <CardTitle>보안 로그</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="bg-muted">
                    <th className="p-2 text-left">시간</th>
                    <th className="p-2 text-left">플러그인</th>
                    <th className="p-2 text-left">이벤트</th>
                    <th className="p-2 text-left">상세</th>
                    <th className="p-2 text-left">레벨</th>
                    <th className="p-2 text-left">상태</th>
                    <th className="p-2 text-left">액션</th>
                  </tr>
                </thead>
                <tbody>
                  {securityLogs.map((log) => (
                    <tr key={log.id} className="border-b">
                      <td className="p-2">{log.timestamp}</td>
                      <td className="p-2 font-medium">
                        {plugins.find(p => p.id === log.plugin_id)?.display_name || "알 수 없음"}
                      </td>
                      <td className="p-2">{log.event_type}</td>
                      <td className="p-2">{log.details}</td>
                      <td className="p-2">
                        <Badge className={securityLevelMap2[log.security_level].color}>
                          {securityLevelMap2[log.security_level].label}
                        </Badge>
                      </td>
                      <td className="p-2">
                        <Badge variant="outline">{log.status}</Badge>
                      </td>
                      <td className="p-2">
                        <div className="flex gap-1">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleSecurityLogAction(log.id, "resolved")}
                          >
                            해결
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleSecurityLogAction(log.id, "ignored")}
                          >
                            무시
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 리소스 모니터링 탭 */}
      {activeTab === "resources" && (
        <Card>
          <CardHeader>
            <CardTitle>리소스 사용량 모니터링</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {resourceUsage.map((usage) => {
                const plugin = plugins.find(p => p.id === usage.plugin_id);
                return (
                  <div key={usage.plugin_id} className="border rounded p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold">{plugin?.display_name || "알 수 없음"}</h3>
                      <Badge variant={usage.is_over_limit ? "destructive" : "default"}>
                        {usage.is_over_limit ? "제한 초과" : "정상"}
                      </Badge>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div>
                        <div className="text-sm text-muted-foreground">CPU 사용률</div>
                        <div className="font-bold">{usage.cpu_usage_percent}%</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted-foreground">메모리 사용량</div>
                        <div className="font-bold">{usage.memory_usage_mb}MB</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted-foreground">실행시간</div>
                        <div className="font-bold">{usage.execution_time_seconds}초</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted-foreground">DB 쿼리</div>
                        <div className="font-bold">{usage.db_queries_count}회</div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
} 
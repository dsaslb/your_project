"use client";

import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { 
  Save, RotateCcw, History, Clock, Download, Upload, 
  Trash2, CheckCircle, AlertTriangle, Loader2, Settings 
} from "lucide-react";

const dummyPlugins = [
  {
    id: 1,
    name: "ai_schedule_optimizer",
    display_name: "AI 스케줄 최적화",
    current_version: "2.1.0",
    status: "active",
  },
  {
    id: 2,
    name: "review_auto_summary",
    display_name: "리뷰 자동 요약",
    current_version: "1.5.0",
    status: "active",
  },
];

const dummySnapshots = [
  {
    id: "snapshot_1_1234567890",
    plugin_id: 1,
    snapshot_name: "설치 전 백업",
    snapshot_type: "install",
    version: "2.0.0",
    created_at: "2024-07-26 15:30:00",
    backup_size: "15.2MB",
    is_verified: true,
  },
  {
    id: "snapshot_1_1234567891",
    plugin_id: 1,
    snapshot_name: "업데이트 전 백업",
    snapshot_type: "update",
    version: "2.1.0",
    created_at: "2024-07-26 14:20:00",
    backup_size: "16.8MB",
    is_verified: true,
  },
  {
    id: "snapshot_2_1234567892",
    plugin_id: 2,
    snapshot_name: "수동 백업",
    snapshot_type: "manual",
    version: "1.5.0",
    created_at: "2024-07-26 13:15:00",
    backup_size: "8.5MB",
    is_verified: true,
  },
];

const dummyVersionHistory = [
  {
    version: "2.1.0",
    version_type: "minor",
    release_date: "2024-07-26",
    changelog: "성능 최적화, UI 개선, 버그 수정",
    breaking_changes: false,
    security_updates: true,
  },
  {
    version: "2.0.0",
    version_type: "major",
    release_date: "2024-07-20",
    changelog: "메이저 업데이트, 새로운 기능 추가",
    breaking_changes: true,
    security_updates: false,
  },
  {
    version: "1.5.0",
    version_type: "patch",
    release_date: "2024-07-15",
    changelog: "안정성 개선, 마이너 버그 수정",
    breaking_changes: false,
    security_updates: false,
  },
];

const dummyRollbackHistory = [
  {
    id: 1,
    plugin_id: 1,
    from_version: "2.1.0",
    to_version: "2.0.0",
    rollback_reason: "성능 문제 발생",
    rollback_type: "manual",
    status: "completed",
    success: true,
    executed_at: "2024-07-26 16:00:00",
    rollback_duration: 45,
  },
  {
    id: 2,
    plugin_id: 2,
    from_version: "1.6.0",
    to_version: "1.5.0",
    rollback_reason: "호환성 문제",
    rollback_type: "automatic",
    status: "completed",
    success: true,
    executed_at: "2024-07-25 10:30:00",
    rollback_duration: 30,
  },
];

export default function AdminPluginBackupPage() {
  const [plugins, setPlugins] = useState(dummyPlugins);
  const [snapshots, setSnapshots] = useState(dummySnapshots);
  const [versionHistory, setVersionHistory] = useState(dummyVersionHistory);
  const [rollbackHistory, setRollbackHistory] = useState(dummyRollbackHistory);
  const [selectedPlugin, setSelectedPlugin] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState("overview");
  const [creatingSnapshot, setCreatingSnapshot] = useState(false);
  const [rollingBack, setRollingBack] = useState(false);

  const snapshotTypeMap = {
    install: { label: "설치", color: "bg-blue-100 text-blue-700", icon: Download },
    update: { label: "업데이트", color: "bg-green-100 text-green-700", icon: Upload },
    manual: { label: "수동", color: "bg-purple-100 text-purple-700", icon: Save },
    auto: { label: "자동", color: "bg-gray-100 text-gray-700", icon: Clock },
  };

  const rollbackTypeMap = {
    manual: { label: "수동", color: "bg-blue-100 text-blue-700" },
    automatic: { label: "자동", color: "bg-green-100 text-green-700" },
    emergency: { label: "긴급", color: "bg-red-100 text-red-700" },
  };

  const handleCreateSnapshot = async (pluginId: number) => {
    setCreatingSnapshot(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const newSnapshot = {
        id: `snapshot_${pluginId}_${Date.now()}`,
        plugin_id: pluginId,
        snapshot_name: "수동 백업",
        snapshot_type: "manual",
        version: plugins.find(p => p.id === pluginId)?.current_version || "1.0.0",
        created_at: new Date().toLocaleString(),
        backup_size: "12.5MB",
        is_verified: true,
      };
      
      setSnapshots(prev => [newSnapshot, ...prev]);
      toast.success("스냅샷이 생성되었습니다!");
      toast("[실시간] 플러그인 백업 완료");
    } catch (error) {
      toast.error("스냅샷 생성 중 오류가 발생했습니다.");
    } finally {
      setCreatingSnapshot(false);
    }
  };

  const handleRollback = async (snapshotId: string, pluginId: number, targetVersion: string) => {
    setRollingBack(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      const newRollback = {
        id: rollbackHistory.length + 1,
        plugin_id: pluginId,
        from_version: plugins.find(p => p.id === pluginId)?.current_version || "1.0.0",
        to_version: targetVersion,
        rollback_reason: "수동 롤백",
        rollback_type: "manual",
        status: "completed",
        success: true,
        executed_at: new Date().toLocaleString(),
        rollback_duration: 35,
      };
      
      setRollbackHistory(prev => [newRollback, ...prev]);
      
      // 플러그인 버전 업데이트
      setPlugins(prev =>
        prev.map(p =>
          p.id === pluginId
            ? { ...p, current_version: targetVersion }
            : p
        )
      );
      
      toast.success("롤백이 완료되었습니다!");
      toast("[실시간] 플러그인 롤백 완료");
    } catch (error) {
      toast.error("롤백 중 오류가 발생했습니다.");
    } finally {
      setRollingBack(false);
    }
  };

  const tabs = [
    { id: "overview", label: "백업 개요", icon: Save },
    { id: "snapshots", label: "스냅샷 관리", icon: History },
    { id: "rollback", label: "롤백 관리", icon: RotateCcw },
    { id: "versions", label: "버전 히스토리", icon: Clock },
    { id: "schedule", label: "자동 백업", icon: Settings },
  ];

  return (
    <div className="container mx-auto p-6 max-w-6xl space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">플러그인 백업/롤백 관리</h1>
        <Button className="flex items-center gap-2">
          <Settings className="h-4 w-4" />
          백업 정책 설정
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

      {/* 백업 개요 탭 */}
      {activeTab === "overview" && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Save className="h-5 w-5" />
                백업 현황
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>총 스냅샷</span>
                  <span className="font-bold">{snapshots.length}</span>
                </div>
                <div className="flex justify-between">
                  <span>검증된 백업</span>
                  <span className="font-bold text-green-600">
                    {snapshots.filter(s => s.is_verified).length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>총 백업 크기</span>
                  <span className="font-bold">
                    {snapshots.reduce((sum, s) => sum + parseFloat(s.backup_size), 0).toFixed(1)}MB
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <RotateCcw className="h-5 w-5" />
                롤백 현황
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>총 롤백</span>
                  <span className="font-bold">{rollbackHistory.length}</span>
                </div>
                <div className="flex justify-between">
                  <span>성공한 롤백</span>
                  <span className="font-bold text-green-600">
                    {rollbackHistory.filter(r => r.success).length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>평균 롤백 시간</span>
                  <span className="font-bold">
                    {(rollbackHistory.reduce((sum, r) => sum + r.rollback_duration, 0) / rollbackHistory.length).toFixed(0)}초
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <History className="h-5 w-5" />
                최근 활동
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {snapshots.slice(0, 3).map((snapshot) => (
                  <div key={snapshot.id} className="flex items-center justify-between text-sm">
                    <span className="truncate">{snapshot.snapshot_name}</span>
                    <Badge className={snapshotTypeMap[snapshot.snapshot_type].color}>
                      {snapshotTypeMap[snapshot.snapshot_type].label}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 스냅샷 관리 탭 */}
      {activeTab === "snapshots" && (
        <Card>
          <CardHeader>
            <CardTitle>스냅샷 관리</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {plugins.map((plugin) => (
                <div key={plugin.id} className="border rounded p-4">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="font-semibold">{plugin.display_name}</h3>
                      <div className="text-sm text-muted-foreground">
                        현재 버전: {plugin.current_version}
                      </div>
                    </div>
                    <Button
                      onClick={() => handleCreateSnapshot(plugin.id)}
                      disabled={creatingSnapshot}
                      className="flex items-center gap-2"
                    >
                      {creatingSnapshot ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                      스냅샷 생성
                    </Button>
                  </div>

                  <div className="space-y-2">
                    {snapshots
                      .filter(s => s.plugin_id === plugin.id)
                      .map((snapshot) => (
                        <div key={snapshot.id} className="flex items-center justify-between p-3 border rounded">
                          <div className="flex items-center gap-3">
                            <Badge className={snapshotTypeMap[snapshot.snapshot_type].color}>
                              <snapshotTypeMap[snapshot.snapshot_type].icon className="h-3 w-3 mr-1" />
                              {snapshotTypeMap[snapshot.snapshot_type].label}
                            </Badge>
                            <div>
                              <div className="font-medium">{snapshot.snapshot_name}</div>
                              <div className="text-sm text-muted-foreground">
                                버전: {snapshot.version} • {snapshot.created_at}
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-sm text-muted-foreground">{snapshot.backup_size}</span>
                            {snapshot.is_verified && <CheckCircle className="h-4 w-4 text-green-500" />}
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleRollback(snapshot.id, plugin.id, snapshot.version)}
                              disabled={rollingBack}
                            >
                              {rollingBack ? <Loader2 className="h-4 w-4 animate-spin" /> : "롤백"}
                            </Button>
                          </div>
                        </div>
                      ))}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 롤백 관리 탭 */}
      {activeTab === "rollback" && (
        <Card>
          <CardHeader>
            <CardTitle>롤백 관리</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="bg-muted">
                    <th className="p-2 text-left">시간</th>
                    <th className="p-2 text-left">플러그인</th>
                    <th className="p-2 text-left">버전 변경</th>
                    <th className="p-2 text-left">사유</th>
                    <th className="p-2 text-left">타입</th>
                    <th className="p-2 text-left">상태</th>
                    <th className="p-2 text-left">소요시간</th>
                  </tr>
                </thead>
                <tbody>
                  {rollbackHistory.map((rollback) => (
                    <tr key={rollback.id} className="border-b">
                      <td className="p-2">{rollback.executed_at}</td>
                      <td className="p-2 font-medium">
                        {plugins.find(p => p.id === rollback.plugin_id)?.display_name || "알 수 없음"}
                      </td>
                      <td className="p-2">
                        <span className="text-red-600">{rollback.from_version}</span>
                        <span className="mx-2">→</span>
                        <span className="text-green-600">{rollback.to_version}</span>
                      </td>
                      <td className="p-2">{rollback.rollback_reason}</td>
                      <td className="p-2">
                        <Badge className={rollbackTypeMap[rollback.rollback_type].color}>
                          {rollbackTypeMap[rollback.rollback_type].label}
                        </Badge>
                      </td>
                      <td className="p-2">
                        <Badge variant={rollback.success ? "default" : "destructive"}>
                          {rollback.status}
                        </Badge>
                      </td>
                      <td className="p-2">{rollback.rollback_duration}초</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 버전 히스토리 탭 */}
      {activeTab === "versions" && (
        <Card>
          <CardHeader>
            <CardTitle>버전 히스토리</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {versionHistory.map((version, index) => (
                <div key={index} className="border rounded p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <Badge variant="outline" className="font-mono">v{version.version}</Badge>
                      <Badge variant="secondary">{version.version_type}</Badge>
                      {version.breaking_changes && (
                        <Badge variant="destructive">Breaking Changes</Badge>
                      )}
                      {version.security_updates && (
                        <Badge className="bg-orange-100 text-orange-700">Security</Badge>
                      )}
                    </div>
                    <div className="text-sm text-muted-foreground">{version.release_date}</div>
                  </div>
                  <div className="text-sm">{version.changelog}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 자동 백업 탭 */}
      {activeTab === "schedule" && (
        <Card>
          <CardHeader>
            <CardTitle>자동 백업 스케줄</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {plugins.map((plugin) => (
                <div key={plugin.id} className="border rounded p-4">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="font-semibold">{plugin.display_name}</h3>
                      <div className="text-sm text-muted-foreground">
                        자동 백업: 매일 02:00
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className="bg-green-100 text-green-700">활성</Badge>
                      <Button size="sm" variant="outline">설정</Button>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <div className="text-muted-foreground">보관 기간</div>
                      <div className="font-medium">30일</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">최대 백업 수</div>
                      <div className="font-medium">10개</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">마지막 백업</div>
                      <div className="font-medium">2024-07-26 02:00</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">다음 백업</div>
                      <div className="font-medium">2024-07-27 02:00</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
} 
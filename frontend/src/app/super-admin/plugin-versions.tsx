"use client";
import React, { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { History, RotateCcw, RefreshCw, Package } from "lucide-react";

interface PluginVersion {
  current_version: string;
  update_history: Array<{
    from_version: string;
    to_version: string;
    updated_at: string;
  }>;
  rollback_history: Array<{
    from_version: string;
    to_version: string;
    rolled_back_at: string;
  }>;
  available_versions: string[];
}

interface Plugin {
  id: string;
  name: string;
  version: string;
  description: string;
}

export default function PluginVersionsPage() {
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [selectedPlugin, setSelectedPlugin] = useState<string | null>(null);
  const [versionData, setVersionData] = useState<PluginVersion | null>(null);
  const [loading, setLoading] = useState(true);
  const [versionLoading, setVersionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPlugins = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/plugins");
      const data = await res.json();
      if (data.success) {
        setPlugins(data.plugins);
      } else {
        setError(data.error || "플러그인 목록을 불러올 수 없습니다");
      }
    } catch (e) {
      setError("네트워크 오류");
    }
    setLoading(false);
  };

  const fetchVersionHistory = async (pluginId: string) => {
    setVersionLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/plugins/${pluginId}/versions`);
      const data = await res.json();
      if (data.success) {
        setVersionData(data.versions);
      } else {
        setError(data.error || "버전 정보를 불러올 수 없습니다");
      }
    } catch (e) {
      setError("네트워크 오류");
    }
    setVersionLoading(false);
  };

  useEffect(() => {
    fetchPlugins();
  }, []);

  useEffect(() => {
    if (selectedPlugin) {
      fetchVersionHistory(selectedPlugin);
    }
  }, [selectedPlugin]);

  const updatePlugin = async (targetVersion: string) => {
    if (!selectedPlugin) return;
    
    try {
      const res = await fetch(`/api/plugins/${selectedPlugin}/update`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ version: targetVersion }),
      });
      const data = await res.json();
      if (!data.success) {
        setError(data.error || "업데이트 실패");
      } else {
        fetchVersionHistory(selectedPlugin);
        fetchPlugins();
      }
    } catch (e) {
      setError("네트워크 오류");
    }
  };

  const rollbackPlugin = async (targetVersion: string) => {
    if (!selectedPlugin) return;
    
    try {
      const res = await fetch(`/api/plugins/${selectedPlugin}/rollback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ version: targetVersion }),
      });
      const data = await res.json();
      if (!data.success) {
        setError(data.error || "롤백 실패");
      } else {
        fetchVersionHistory(selectedPlugin);
        fetchPlugins();
      }
    } catch (e) {
      setError("네트워크 오류");
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString("ko-KR");
  };

  return (
    <div className="max-w-6xl mx-auto py-8 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">플러그인 버전 관리</h1>
        <Button onClick={fetchPlugins} disabled={loading}>
          <RefreshCw className="w-4 h-4 mr-2" />
          새로고침
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 플러그인 목록 */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>플러그인 목록</CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-2">
                  {[1, 2, 3].map((i) => (
                    <Skeleton key={i} className="h-12 w-full" />
                  ))}
                </div>
              ) : (
                <div className="space-y-2">
                  {plugins.map((plugin) => (
                    <div
                      key={plugin.id}
                      className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                        selectedPlugin === plugin.id
                          ? "bg-primary text-primary-foreground"
                          : "hover:bg-muted"
                      }`}
                      onClick={() => setSelectedPlugin(plugin.id)}
                    >
                      <div className="font-medium">{plugin.name}</div>
                      <div className="text-sm opacity-80">v{plugin.version}</div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* 버전 정보 */}
        <div className="lg:col-span-2">
          {selectedPlugin ? (
            <div className="space-y-6">
              {versionLoading ? (
                <div className="space-y-4">
                  <Skeleton className="h-8 w-full" />
                  <Skeleton className="h-32 w-full" />
                  <Skeleton className="h-32 w-full" />
                </div>
              ) : versionData ? (
                <>
                  {/* 현재 버전 */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Package className="w-5 h-5" />
                        현재 버전
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center justify-between">
                        <div>
                          <Badge variant="default" className="text-lg px-3 py-1">
                            v{versionData.current_version}
                          </Badge>
                        </div>
                        <div className="text-sm text-muted-foreground">
                          현재 설치된 버전
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* 사용 가능한 버전 */}
                  <Card>
                    <CardHeader>
                      <CardTitle>사용 가능한 버전</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                        {versionData.available_versions.map((version) => (
                          <Button
                            key={version}
                            variant="outline"
                            size="sm"
                            onClick={() => updatePlugin(version)}
                            disabled={version === versionData.current_version}
                          >
                            <RefreshCw className="w-3 h-3 mr-1" />
                            v{version}
                          </Button>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  {/* 업데이트 히스토리 */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <History className="w-5 h-5" />
                        업데이트 히스토리
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      {versionData.update_history.length > 0 ? (
                        <div className="space-y-3">
                          {versionData.update_history.map((update, index) => (
                            <div
                              key={index}
                              className="flex items-center justify-between p-3 border rounded-lg"
                            >
                              <div className="flex items-center gap-2">
                                <Badge variant="outline">
                                  v{update.from_version}
                                </Badge>
                                <span>→</span>
                                <Badge variant="default">
                                  v{update.to_version}
                                </Badge>
                              </div>
                              <div className="text-sm text-muted-foreground">
                                {formatDate(update.updated_at)}
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-muted-foreground text-center py-4">
                          업데이트 기록이 없습니다
                        </div>
                      )}
                    </CardContent>
                  </Card>

                  {/* 롤백 히스토리 */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <RotateCcw className="w-5 h-5" />
                        롤백 히스토리
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      {versionData.rollback_history.length > 0 ? (
                        <div className="space-y-3">
                          {versionData.rollback_history.map((rollback, index) => (
                            <div
                              key={index}
                              className="flex items-center justify-between p-3 border rounded-lg"
                            >
                              <div className="flex items-center gap-2">
                                <Badge variant="destructive">
                                  v{rollback.from_version}
                                </Badge>
                                <span>→</span>
                                <Badge variant="outline">
                                  v{rollback.to_version}
                                </Badge>
                              </div>
                              <div className="text-sm text-muted-foreground">
                                {formatDate(rollback.rolled_back_at)}
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-muted-foreground text-center py-4">
                          롤백 기록이 없습니다
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </>
              ) : (
                <Card>
                  <CardContent className="text-center py-8">
                    <div className="text-muted-foreground">
                      버전 정보를 불러올 수 없습니다
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          ) : (
            <Card>
              <CardContent className="text-center py-8">
                <div className="text-muted-foreground">
                  버전 정보를 확인할 플러그인을 선택해주세요
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {error && (
        <div className="text-red-500 text-center">{error}</div>
      )}
    </div>
  );
} 
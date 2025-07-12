"use client";
import React, { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

interface PluginInfo {
  id: string;
  name: string;
  version: string;
  description: string;
  author: string;
  category: string;
  enabled: boolean;
  dependencies: string[];
  permissions: string[];
  routes_count: number;
  menus_count: number;
  health_status: any;
  created_at?: string;
  updated_at?: string;
}

export default function PluginManagementPage() {
  const [plugins, setPlugins] = useState<PluginInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updating, setUpdating] = useState<string | null>(null);

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

  useEffect(() => {
    fetchPlugins();
    const interval = setInterval(fetchPlugins, 5000); // 5초마다 실시간 갱신
    return () => clearInterval(interval);
  }, []);

  const togglePlugin = async (plugin: PluginInfo) => {
    setUpdating(plugin.id);
    try {
      const res = await fetch(`/api/plugins/${plugin.id}/${plugin.enabled ? "disable" : "enable"}`, {
        method: "POST",
      });
      const data = await res.json();
      if (!data.success) {
        setError(data.error || "상태 변경 실패");
      } else {
        fetchPlugins();
      }
    } catch (e) {
      setError("네트워크 오류");
    }
    setUpdating(null);
  };

  return (
    <div className="max-w-3xl mx-auto py-8 space-y-6">
      <h1 className="text-3xl font-bold mb-4">플러그인/메뉴 실시간 관리</h1>
      {loading ? (
        <Skeleton className="h-32 w-full" />
      ) : error ? (
        <div className="text-red-500">{error}</div>
      ) : (
        <div className="space-y-4">
          {plugins.map((plugin) => (
            <Card key={plugin.id} className="border">
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle className="text-lg">{plugin.name} <span className="text-xs text-muted-foreground">v{plugin.version}</span></CardTitle>
                  <div className="text-sm text-muted-foreground">{plugin.description}</div>
                  <div className="text-xs mt-1">카테고리: <Badge>{plugin.category}</Badge></div>
                </div>
                <div className="flex flex-col items-end gap-2">
                  <Switch
                    checked={plugin.enabled}
                    onCheckedChange={() => togglePlugin(plugin)}
                    disabled={updating === plugin.id}
                  />
                  <span className="text-xs">{plugin.enabled ? "활성화" : "비활성화"}</span>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2 text-xs mb-2">
                  <Badge variant="outline">라우트 {plugin.routes_count}</Badge>
                  <Badge variant="outline">메뉴 {plugin.menus_count}</Badge>
                  <Badge variant={plugin.health_status?.initialized ? "default" : "destructive"}>
                    {plugin.health_status?.initialized ? "정상" : "오류"}
                  </Badge>
                </div>
                <div className="text-xs text-muted-foreground">작성자: {plugin.author}</div>
                <div className="text-xs text-muted-foreground">생성: {plugin.created_at?.slice(0, 10)}</div>
                <div className="text-xs text-muted-foreground">수정: {plugin.updated_at?.slice(0, 10)}</div>
                {/* 상세/설정/스키마 관리 등은 추후 모달/탭으로 확장 */}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
} 
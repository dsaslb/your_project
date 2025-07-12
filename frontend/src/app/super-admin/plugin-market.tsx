"use client";
import React, { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Star, Download, Package, RefreshCw, RotateCcw } from "lucide-react";

interface MarketPlugin {
  id: string;
  name: string;
  version: string;
  description: string;
  author: string;
  category: string;
  installed: boolean;
  installed_version: string;
  latest_version: string;
  rating: number;
  downloads: number;
  price: number;
  tags: string[];
  screenshots: string[];
  dependencies: string[];
  health_status: any;
}

export default function PluginMarketPage() {
  const [plugins, setPlugins] = useState<MarketPlugin[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actioning, setActioning] = useState<string | null>(null);

  const fetchMarket = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/plugins/market");
      const data = await res.json();
      if (data.success) {
        setPlugins(data.plugins);
      } else {
        setError(data.error || "마켓 목록을 불러올 수 없습니다");
      }
    } catch (e) {
      setError("네트워크 오류");
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchMarket();
  }, []);

  const installPlugin = async (plugin: MarketPlugin) => {
    setActioning(plugin.id);
    try {
      const res = await fetch(`/api/plugins/${plugin.id}/install`, {
        method: "POST",
      });
      const data = await res.json();
      if (!data.success) {
        setError(data.error || "설치 실패");
      } else {
        fetchMarket();
      }
    } catch (e) {
      setError("네트워크 오류");
    }
    setActioning(null);
  };

  const uninstallPlugin = async (plugin: MarketPlugin) => {
    setActioning(plugin.id);
    try {
      const res = await fetch(`/api/plugins/${plugin.id}/uninstall`, {
        method: "POST",
      });
      const data = await res.json();
      if (!data.success) {
        setError(data.error || "제거 실패");
      } else {
        fetchMarket();
      }
    } catch (e) {
      setError("네트워크 오류");
    }
    setActioning(null);
  };

  const updatePlugin = async (plugin: MarketPlugin) => {
    setActioning(plugin.id);
    try {
      const res = await fetch(`/api/plugins/${plugin.id}/update`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ version: plugin.latest_version }),
      });
      const data = await res.json();
      if (!data.success) {
        setError(data.error || "업데이트 실패");
      } else {
        fetchMarket();
      }
    } catch (e) {
      setError("네트워크 오류");
    }
    setActioning(null);
  };

  const rollbackPlugin = async (plugin: MarketPlugin) => {
    setActioning(plugin.id);
    try {
      const res = await fetch(`/api/plugins/${plugin.id}/rollback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ version: "1.0.0" }), // 이전 버전으로 롤백
      });
      const data = await res.json();
      if (!data.success) {
        setError(data.error || "롤백 실패");
      } else {
        fetchMarket();
      }
    } catch (e) {
      setError("네트워크 오류");
    }
    setActioning(null);
  };

  return (
    <div className="max-w-6xl mx-auto py-8 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">플러그인 마켓/스토어</h1>
        <Button onClick={fetchMarket} disabled={loading}>
          <RefreshCw className="w-4 h-4 mr-2" />
          새로고침
        </Button>
      </div>
      
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-48 w-full" />
          ))}
        </div>
      ) : error ? (
        <div className="text-red-500">{error}</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {plugins.map((plugin) => (
            <Card key={plugin.id} className="border hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg">{plugin.name}</CardTitle>
                    <div className="text-sm text-muted-foreground mt-1">{plugin.description}</div>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge variant="outline">{plugin.category}</Badge>
                      <div className="flex items-center text-xs text-muted-foreground">
                        <Star className="w-3 h-3 fill-yellow-400 text-yellow-400 mr-1" />
                        {plugin.rating}
                      </div>
                      <div className="flex items-center text-xs text-muted-foreground">
                        <Download className="w-3 h-3 mr-1" />
                        {plugin.downloads}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium">v{plugin.version}</div>
                    <div className="text-xs text-muted-foreground">
                      {plugin.price === 0 ? "무료" : `₩${plugin.price}`}
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="text-xs text-muted-foreground">
                    작성자: {plugin.author}
                  </div>
                  
                  {plugin.installed && (
                    <div className="text-xs">
                      <Badge variant="default" className="mr-2">설치됨</Badge>
                      <span className="text-muted-foreground">
                        v{plugin.installed_version}
                      </span>
                    </div>
                  )}
                  
                  <div className="flex flex-wrap gap-2">
                    {plugin.installed ? (
                      <>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => updatePlugin(plugin)}
                          disabled={actioning === plugin.id || plugin.installed_version === plugin.latest_version}
                        >
                          <RefreshCw className="w-3 h-3 mr-1" />
                          업데이트
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => rollbackPlugin(plugin)}
                          disabled={actioning === plugin.id}
                        >
                          <RotateCcw className="w-3 h-3 mr-1" />
                          롤백
                        </Button>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => uninstallPlugin(plugin)}
                          disabled={actioning === plugin.id}
                        >
                          제거
                        </Button>
                      </>
                    ) : (
                      <Button
                        size="sm"
                        onClick={() => installPlugin(plugin)}
                        disabled={actioning === plugin.id}
                      >
                        <Package className="w-3 h-3 mr-1" />
                        설치
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
} 
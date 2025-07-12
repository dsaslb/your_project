"use client";
import React, { useEffect, useState, useCallback } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { RefreshCw, CheckCircle, XCircle, AlertCircle, Zap } from "lucide-react";

interface Suggestion {
  id: number;
  plugin_id: string;
  suggestion_type: string;
  description: string;
  created_at: string;
  details: Record<string, any>;
  executed: boolean;
  executed_at?: string;
  result?: string;
}

interface HistoryItem {
  plugin_id: string;
  suggestion_type: string;
  description: string;
  executed_at: string;
  result: string;
}

const PluginOptimizationDashboard: React.FC = () => {
  const [tab, setTab] = useState("suggestions");
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [executing, setExecuting] = useState<number | null>(null);

  const fetchSuggestions = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/plugin-optimization/suggestions");
      const data = await res.json();
      if (data.success) {
        setSuggestions(data.data);
      } else {
        setError(data.message);
      }
    } catch (e) {
      setError("최적화 제안 조회 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchHistory = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/plugin-optimization/history");
      const data = await res.json();
      if (data.success) {
        setHistory(data.data);
      } else {
        setError(data.message);
      }
    } catch (e) {
      setError("최적화 이력 조회 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (tab === "suggestions") fetchSuggestions();
    if (tab === "history") fetchHistory();
  }, [tab, fetchSuggestions, fetchHistory]);

  const handleExecute = async (id: number) => {
    setExecuting(id);
    setError("");
    try {
      const res = await fetch(`/api/plugin-optimization/execute/${id}`, { method: "POST" });
      const data = await res.json();
      if (data.success) {
        fetchSuggestions();
        fetchHistory();
      } else {
        setError(data.message);
      }
    } catch (e) {
      setError("최적화 제안 실행 중 오류가 발생했습니다.");
    } finally {
      setExecuting(null);
    }
  };

  const getStatusIcon = (executed: boolean) =>
    executed ? <CheckCircle className="h-4 w-4 text-green-500" /> : <Zap className="h-4 w-4 text-blue-500" />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">플러그인 성능 최적화 대시보드</h1>
          <p className="text-muted-foreground">자동 분석, 최적화 제안, 실행, 이력 관리</p>
        </div>
        <Button onClick={tab === "suggestions" ? fetchSuggestions : fetchHistory} disabled={loading}>
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
          새로고침
        </Button>
      </div>
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      <Tabs value={tab} onValueChange={setTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="suggestions">최적화 제안</TabsTrigger>
          <TabsTrigger value="history">실행 이력</TabsTrigger>
        </TabsList>
        <TabsContent value="suggestions">
          <Card>
            <CardHeader>
              <CardTitle>최적화 제안 목록</CardTitle>
            </CardHeader>
            <CardContent>
              {suggestions.length === 0 ? (
                <div className="text-center text-muted-foreground py-8">최적화 제안이 없습니다.</div>
              ) : (
                <div className="space-y-4">
                  {suggestions.map((s) => (
                    <div key={s.id} className="p-4 border rounded flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {getStatusIcon(s.executed)}
                        <span className="font-semibold">{s.plugin_id}</span>
                        <Badge>{s.suggestion_type}</Badge>
                        <span className="text-sm text-muted-foreground">{s.description}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        {!s.executed && (
                          <Button size="sm" onClick={() => handleExecute(s.id)} disabled={executing === s.id}>
                            {executing === s.id ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Zap className="h-4 w-4" />}
                            실행
                          </Button>
                        )}
                        {s.executed && (
                          <span className="text-green-600 text-xs">실행됨</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="history">
          <Card>
            <CardHeader>
              <CardTitle>최적화 실행 이력</CardTitle>
            </CardHeader>
            <CardContent>
              {history.length === 0 ? (
                <div className="text-center text-muted-foreground py-8">실행 이력이 없습니다.</div>
              ) : (
                <div className="space-y-4">
                  {history.map((h, idx) => (
                    <div key={idx} className="p-4 border rounded flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <CheckCircle className="h-4 w-4 text-green-500" />
                        <span className="font-semibold">{h.plugin_id}</span>
                        <Badge>{h.suggestion_type}</Badge>
                        <span className="text-sm text-muted-foreground">{h.description}</span>
                      </div>
                      <div className="flex flex-col items-end">
                        <span className="text-xs text-muted-foreground">{new Date(h.executed_at).toLocaleString("ko-KR")}</span>
                        <span className="text-xs text-blue-600">{h.result}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default PluginOptimizationDashboard; 
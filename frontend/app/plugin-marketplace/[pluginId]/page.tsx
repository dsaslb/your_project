"use client";

import React, { useEffect, useState, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Download, Trash2, Star, Loader2, Settings, RefreshCw, History } from "lucide-react";
import { toast } from "sonner";

interface Plugin {
  id: number;
  name: string;
  display_name: string;
  description: string;
  version: string;
  author: string;
  category: string;
  tags: string[];
  icon: string;
  ui_schema: any;
  download_count: number;
  rating: number;
  review_count: number;
  is_installed: boolean;
}

const dummyReviews = [
  { user: "홍길동", rating: 5, comment: "정말 유용합니다!" },
  { user: "김철수", rating: 4, comment: "AI 스케줄 추천이 신기해요." },
  { user: "이영희", rating: 3, comment: "조금 더 개선되면 좋겠어요." },
];

const dummyVersionHistory = [
  { version: "2.1.0", date: "2024-01-15", changes: ["성능 최적화", "UI 개선", "버그 수정"] },
  { version: "2.0.0", date: "2023-12-01", changes: ["메이저 업데이트", "새로운 기능 추가"] },
  { version: "1.5.0", date: "2023-10-20", changes: ["안정성 개선", "마이너 버그 수정"] },
  { version: "1.0.0", date: "2023-08-01", changes: ["초기 릴리즈"] },
];

const dummySettings = {
  autoUpdate: true,
  notifications: true,
  dataCollection: false,
  performanceMode: "balanced",
  theme: "auto",
};

export default function PluginDetailPage() {
  const { pluginId } = useParams<{ pluginId: string }>();
  const router = useRouter();
  const [plugin, setPlugin] = useState<Plugin | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [installing, setInstalling] = useState(false);
  const [reviews, setReviews] = useState(dummyReviews);
  const [reviewForm, setReviewForm] = useState({ user: "", rating: 5, comment: "" });
  const [submitting, setSubmitting] = useState(false);
  const [activeTab, setActiveTab] = useState("info");
  const [settings, setSettings] = useState(dummySettings);
  const [updating, setUpdating] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  // 실시간 알림(WebSocket 더미)
  useEffect(() => {
    const timer = setTimeout(() => {
      toast.info("[실시간 알림] 플러그인 마켓플레이스에 새로운 플러그인이 등록되었습니다.");
    }, 8000);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    const fetchPlugin = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch("/api/plugin/test");
        const data = await res.json();
        const found = data.data.plugins.find((p: Plugin) => String(p.id) === pluginId || p.name === pluginId);
        if (found) {
          setPlugin(found);
        } else {
          setError("플러그인을 찾을 수 없습니다.");
        }
      } catch (e) {
        setError("플러그인 정보를 불러오는 중 오류가 발생했습니다.");
      } finally {
        setLoading(false);
      }
    };
    fetchPlugin();
  }, [pluginId]);

  const handleInstall = async () => {
    if (!plugin) return;
    setInstalling(true);
    try {
      const res = await fetch("/api/plugin/install", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ plugin_id: plugin.id }),
      });
      const result = await res.json();
      if (result.success) {
        setPlugin({ ...plugin, is_installed: true });
        toast.success("플러그인 설치 완료!");
        toast("[실시간] 플러그인 설치됨: " + plugin.display_name);
      } else {
        toast.error(result.error || "설치 실패");
      }
    } catch (e) {
      toast.error("설치 중 오류 발생");
    } finally {
      setInstalling(false);
    }
  };

  const handleUninstall = async () => {
    if (!plugin) return;
    setInstalling(true);
    try {
      const res = await fetch("/api/plugin/uninstall", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ installation_id: `install_${plugin.id}_12345` }),
      });
      const result = await res.json();
      if (result.success) {
        setPlugin({ ...plugin, is_installed: false });
        toast.success("플러그인 제거 완료!");
        toast("[실시간] 플러그인 제거됨: " + plugin.display_name);
      } else {
        toast.error(result.error || "제거 실패");
      }
    } catch (e) {
      toast.error("제거 중 오류 발생");
    } finally {
      setInstalling(false);
    }
  };

  const handleReviewSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reviewForm.user.trim() || !reviewForm.comment.trim()) {
      toast.error("이름과 리뷰 내용을 입력해주세요.");
      return;
    }
    setSubmitting(true);
    try {
      await new Promise((res) => setTimeout(res, 700));
      setReviews([
        { ...reviewForm },
        ...reviews,
      ]);
      setReviewForm({ user: "", rating: 5, comment: "" });
      toast.success("리뷰가 등록되었습니다!");
      toast("[실시간] 새 리뷰가 등록됨");
    } catch {
      toast.error("리뷰 등록 중 오류 발생");
    } finally {
      setSubmitting(false);
    }
  };

  const handleUpdate = async () => {
    if (!plugin) return;
    setUpdating(true);
    try {
      await new Promise((res) => setTimeout(res, 1500));
      toast.success("플러그인 업데이트 완료!");
      toast("[실시간] 플러그인 업데이트됨: " + plugin.display_name);
    } catch {
      toast.error("업데이트 중 오류 발생");
    } finally {
      setUpdating(false);
    }
  };

  const handleSettingsSave = async () => {
    try {
      await new Promise((res) => setTimeout(res, 500));
      toast.success("설정이 저장되었습니다!");
      toast("[실시간] 플러그인 설정 변경됨");
    } catch {
      toast.error("설정 저장 중 오류 발생");
    }
  };

  if (loading) return <div className="p-8 flex items-center gap-2"><Loader2 className="animate-spin" />로딩 중...</div>;
  if (error) return <div className="p-8 text-red-500">{error}</div>;
  if (!plugin) return null;

  const tabs = [
    { id: "info", label: "정보", icon: null },
    { id: "settings", label: "설정", icon: Settings },
    { id: "update", label: "업데이트", icon: RefreshCw },
    { id: "history", label: "버전 히스토리", icon: History },
  ];

  return (
    <div className="container mx-auto p-6 max-w-4xl space-y-6">
      <Button variant="ghost" size="sm" onClick={() => router.back()} className="mb-2 flex items-center space-x-2">
        <ArrowLeft className="h-4 w-4" />
        <span>뒤로가기</span>
      </Button>
      
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
            {tab.icon && <tab.icon className="h-4 w-4" />}
            {tab.label}
          </button>
        ))}
      </div>

      {/* 정보 탭 */}
      {activeTab === "info" && (
        <Card>
          <CardHeader>
            <div className="flex items-center space-x-4">
              <div className="text-4xl">{plugin.icon ? <span className={`icon-${plugin.icon}`} /> : "🧩"}</div>
              <div>
                <CardTitle className="text-2xl">{plugin.display_name}</CardTitle>
                <div className="text-muted-foreground text-sm">{plugin.name}</div>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-lg font-medium">{plugin.description}</div>
            <div className="flex flex-wrap gap-2">
              <Badge variant="outline">버전: {plugin.version}</Badge>
              <Badge variant="outline">카테고리: {plugin.category}</Badge>
              <Badge variant="outline">개발자: {plugin.author}</Badge>
              <Badge variant="outline">다운로드: {plugin.download_count}</Badge>
              <Badge variant="outline">평점: {plugin.rating} ({plugin.review_count}건)</Badge>
              {plugin.tags.map((tag) => (
                <Badge key={tag} variant="secondary">#{tag}</Badge>
              ))}
            </div>
            <div className="flex gap-4 mt-4">
              {plugin.is_installed ? (
                <Button variant="destructive" onClick={handleUninstall} disabled={installing} className="flex items-center space-x-2">
                  {installing ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
                  <span>플러그인 제거</span>
                </Button>
              ) : (
                <Button onClick={handleInstall} disabled={installing} className="flex items-center space-x-2">
                  {installing ? <Loader2 className="h-4 w-4 animate-spin" /> : <Download className="h-4 w-4" />}
                  <span>플러그인 설치</span>
                </Button>
              )}
            </div>
            <div className="mt-6">
              <h3 className="font-semibold mb-2">UI 스키마 미리보기</h3>
              <div className="bg-muted p-4 rounded text-xs overflow-x-auto mb-2">
                <pre>{JSON.stringify(plugin.ui_schema, null, 2)}</pre>
              </div>
              <div className="border rounded p-4 bg-white mb-2">
                <div className="font-bold mb-1">메뉴: {plugin.ui_schema?.menu?.title || "-"}</div>
                <div className="text-sm text-muted-foreground mb-2">아이콘: {plugin.ui_schema?.menu?.icon || "-"}, 순서: {plugin.ui_schema?.menu?.position || "-"}</div>
                <div className="font-bold mb-1">대시보드 컴포넌트: {plugin.ui_schema?.dashboard?.component || "-"}</div>
                <div className="text-sm text-muted-foreground">타입: {plugin.ui_schema?.dashboard?.type || "-"}, 크기: {plugin.ui_schema?.dashboard?.size || "-"}</div>
              </div>
            </div>
            <div className="mt-6">
              <h3 className="font-semibold mb-2">리뷰/평점</h3>
              <form onSubmit={handleReviewSubmit} className="mb-4 flex flex-col gap-2 bg-muted p-3 rounded">
                <div className="flex gap-2 items-center">
                  <input
                    className="border rounded px-2 py-1 text-sm"
                    placeholder="이름"
                    value={reviewForm.user}
                    onChange={e => setReviewForm(f => ({ ...f, user: e.target.value }))}
                    disabled={submitting}
                    maxLength={12}
                    style={{ width: 100 }}
                  />
                  <span className="flex items-center gap-1">
                    {[1,2,3,4,5].map((n) => (
                      <Star
                        key={n}
                        className={
                          "h-4 w-4 cursor-pointer " +
                          (reviewForm.rating >= n ? "fill-yellow-400 text-yellow-500" : "text-gray-300")
                        }
                        onClick={() => setReviewForm(f => ({ ...f, rating: n }))}
                      />
                    ))}
                  </span>
                  <button
                    type="submit"
                    className="ml-auto px-3 py-1 rounded bg-primary text-white text-xs font-semibold disabled:opacity-60"
                    disabled={submitting}
                  >
                    {submitting ? <Loader2 className="h-4 w-4 animate-spin inline" /> : "리뷰 등록"}
                  </button>
                </div>
                <textarea
                  className="border rounded px-2 py-1 text-sm resize-none"
                  placeholder="리뷰를 입력하세요"
                  value={reviewForm.comment}
                  onChange={e => setReviewForm(f => ({ ...f, comment: e.target.value }))}
                  rows={2}
                  maxLength={100}
                  disabled={submitting}
                />
              </form>
              <div className="space-y-2">
                {reviews.map((r, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm">
                    <span className="font-bold">{r.user}</span>
                    <span className="flex items-center text-yellow-500">
                      {[...Array(r.rating)].map((_, idx) => <Star key={idx} className="h-3 w-3 fill-yellow-400" />)}
                    </span>
                    <span>{r.comment}</span>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 설정 탭 */}
      {activeTab === "settings" && (
        <Card>
          <CardHeader>
            <CardTitle>플러그인 설정</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">자동 업데이트</div>
                  <div className="text-sm text-muted-foreground">새 버전이 있을 때 자동으로 업데이트합니다</div>
                </div>
                <input
                  type="checkbox"
                  checked={settings.autoUpdate}
                  onChange={(e) => setSettings(s => ({ ...s, autoUpdate: e.target.checked }))}
                  className="h-4 w-4"
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">알림</div>
                  <div className="text-sm text-muted-foreground">플러그인 관련 알림을 받습니다</div>
                </div>
                <input
                  type="checkbox"
                  checked={settings.notifications}
                  onChange={(e) => setSettings(s => ({ ...s, notifications: e.target.checked }))}
                  className="h-4 w-4"
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">데이터 수집</div>
                  <div className="text-sm text-muted-foreground">사용 통계 데이터를 수집합니다</div>
                </div>
                <input
                  type="checkbox"
                  checked={settings.dataCollection}
                  onChange={(e) => setSettings(s => ({ ...s, dataCollection: e.target.checked }))}
                  className="h-4 w-4"
                />
              </div>
              <div>
                <div className="font-medium mb-2">성능 모드</div>
                <select
                  value={settings.performanceMode}
                  onChange={(e) => setSettings(s => ({ ...s, performanceMode: e.target.value }))}
                  className="border rounded px-3 py-1"
                >
                  <option value="balanced">균형</option>
                  <option value="performance">성능 우선</option>
                  <option value="battery">배터리 절약</option>
                </select>
              </div>
            </div>
            <Button onClick={handleSettingsSave} className="w-full">
              설정 저장
            </Button>
          </CardContent>
        </Card>
      )}

      {/* 업데이트 탭 */}
      {activeTab === "update" && (
        <Card>
          <CardHeader>
            <CardTitle>플러그인 업데이트</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="bg-muted p-4 rounded">
              <div className="font-medium mb-2">현재 버전: {plugin.version}</div>
              <div className="text-sm text-muted-foreground">최신 버전: 2.2.0 (업데이트 가능)</div>
            </div>
            <div className="space-y-2">
              <h4 className="font-medium">업데이트 내용 (v2.2.0)</h4>
              <ul className="text-sm space-y-1">
                <li>• 새로운 AI 기능 추가</li>
                <li>• 성능 최적화</li>
                <li>• UI/UX 개선</li>
                <li>• 버그 수정</li>
              </ul>
            </div>
            <Button onClick={handleUpdate} disabled={updating} className="w-full flex items-center justify-center gap-2">
              {updating ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
              {updating ? "업데이트 중..." : "업데이트"}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* 버전 히스토리 탭 */}
      {activeTab === "history" && (
        <Card>
          <CardHeader>
            <CardTitle>버전 히스토리</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {dummyVersionHistory.map((version, index) => (
                <div key={index} className="border rounded p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="font-medium">v{version.version}</div>
                    <div className="text-sm text-muted-foreground">{version.date}</div>
                  </div>
                  <ul className="text-sm space-y-1">
                    {version.changes.map((change, changeIndex) => (
                      <li key={changeIndex}>• {change}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
} 
"use client";

import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { Loader2, CheckCircle, XCircle, Trash2, ShieldCheck } from "lucide-react";

const dummyPlugins = [
  {
    id: 1,
    name: "ai_schedule_optimizer",
    display_name: "AI 스케줄 최적화",
    author: "AI Team",
    version: "1.0.0",
    status: "pending", // pending, approved, disabled, deleted
    created_at: "2024-07-01",
  },
  {
    id: 2,
    name: "review_auto_summary",
    display_name: "리뷰 자동 요약",
    author: "NLP Team",
    version: "2.1.0",
    status: "approved",
    created_at: "2024-06-20",
  },
  {
    id: 3,
    name: "qsc_auto_analyzer",
    display_name: "QSC 자동 분석",
    author: "Quality Team",
    version: "1.5.0",
    status: "disabled",
    created_at: "2024-05-10",
  },
  {
    id: 4,
    name: "contract_manager",
    display_name: "계약 관리",
    author: "Legal Team",
    version: "0.9.0",
    status: "deleted",
    created_at: "2024-04-01",
  },
];

const statusMap: Record<string, { label: string; color: string; icon: any }> = {
  pending: { label: "대기", color: "bg-yellow-100 text-yellow-700", icon: ShieldCheck },
  approved: { label: "승인", color: "bg-green-100 text-green-700", icon: CheckCircle },
  disabled: { label: "비활성화", color: "bg-gray-200 text-gray-600", icon: XCircle },
  deleted: { label: "삭제됨", color: "bg-red-100 text-red-700", icon: Trash2 },
};

export default function AdminPluginManagementPage() {
  const [plugins, setPlugins] = useState(dummyPlugins);
  const [loadingId, setLoadingId] = useState<number | null>(null);

  const handleAction = (id: number, action: "approve" | "disable" | "delete") => {
    setLoadingId(id);
    setTimeout(() => {
      setPlugins((prev) =>
        prev.map((p) =>
          p.id === id
            ? {
                ...p,
                status:
                  action === "approve"
                    ? "approved"
                    : action === "disable"
                    ? "disabled"
                    : "deleted",
              }
            : p
        )
      );
      setLoadingId(null);
      if (action === "approve") {
        toast.success("플러그인이 승인되었습니다!");
        toast("[실시간] 플러그인 승인됨");
      } else if (action === "disable") {
        toast("플러그인이 비활성화되었습니다.");
        toast("[실시간] 플러그인 비활성화됨");
      } else {
        toast.error("플러그인이 삭제되었습니다.");
        toast("[실시간] 플러그인 삭제됨");
      }
    }, 900);
  };

  return (
    <div className="container mx-auto p-6 max-w-3xl space-y-6">
      <h1 className="text-2xl font-bold mb-4">플러그인 관리 (관리자)</h1>
      <Card>
        <CardHeader>
          <CardTitle>플러그인 목록</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm border">
              <thead>
                <tr className="bg-muted">
                  <th className="p-2 border">ID</th>
                  <th className="p-2 border">이름</th>
                  <th className="p-2 border">버전</th>
                  <th className="p-2 border">개발자</th>
                  <th className="p-2 border">등록일</th>
                  <th className="p-2 border">상태</th>
                  <th className="p-2 border">관리</th>
                </tr>
              </thead>
              <tbody>
                {plugins.map((p) => {
                  const status = statusMap[p.status];
                  return (
                    <tr key={p.id} className="border-b">
                      <td className="p-2 border text-center">{p.id}</td>
                      <td className="p-2 border font-semibold">{p.display_name}</td>
                      <td className="p-2 border text-center">{p.version}</td>
                      <td className="p-2 border text-center">{p.author}</td>
                      <td className="p-2 border text-center">{p.created_at}</td>
                      <td className="p-2 border text-center">
                        <span className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium ${status.color}`}>
                          <status.icon className="h-4 w-4" />
                          {status.label}
                        </span>
                      </td>
                      <td className="p-2 border text-center">
                        {p.status === "pending" && (
                          <Button
                            size="sm"
                            className="mr-1"
                            disabled={loadingId === p.id}
                            onClick={() => handleAction(p.id, "approve")}
                          >
                            {loadingId === p.id ? <Loader2 className="h-4 w-4 animate-spin" /> : "승인"}
                          </Button>
                        )}
                        {p.status !== "deleted" && (
                          <Button
                            size="sm"
                            variant="secondary"
                            className="mr-1"
                            disabled={loadingId === p.id || p.status === "pending"}
                            onClick={() => handleAction(p.id, "disable")}
                          >
                            {loadingId === p.id ? <Loader2 className="h-4 w-4 animate-spin" /> : "비활성화"}
                          </Button>
                        )}
                        {p.status !== "deleted" && (
                          <Button
                            size="sm"
                            variant="destructive"
                            disabled={loadingId === p.id}
                            onClick={() => handleAction(p.id, "delete")}
                          >
                            {loadingId === p.id ? <Loader2 className="h-4 w-4 animate-spin" /> : "삭제"}
                          </Button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 
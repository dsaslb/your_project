"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { TrendingUp, Download, Users, Activity, RefreshCw } from "lucide-react";

const dummyStats = {
  totalPlugins: 15,
  activePlugins: 12,
  totalDownloads: 1250,
  totalUsers: 89,
  monthlyGrowth: 23,
};

const dummyInstallTrend = [
  { month: "1월", installs: 45, uninstalls: 12 },
  { month: "2월", installs: 67, uninstalls: 8 },
  { month: "3월", installs: 89, uninstalls: 15 },
  { month: "4월", installs: 123, uninstalls: 22 },
  { month: "5월", installs: 156, uninstalls: 18 },
  { month: "6월", installs: 189, uninstalls: 25 },
  { month: "7월", installs: 234, uninstalls: 31 },
];

const dummyPopularPlugins = [
  { name: "AI 스케줄 최적화", downloads: 234, rating: 4.5, users: 45 },
  { name: "리뷰 자동 요약", downloads: 189, rating: 4.2, users: 32 },
  { name: "QSC 자동 분석", downloads: 156, rating: 4.7, users: 28 },
  { name: "계약 관리", downloads: 123, rating: 4.1, users: 19 },
  { name: "재고 관리", downloads: 98, rating: 4.3, users: 15 },
];

const dummyUsageStats = [
  { plugin: "AI 스케줄 최적화", daily: 89, weekly: 456, monthly: 1890 },
  { plugin: "리뷰 자동 요약", daily: 67, weekly: 345, monthly: 1234 },
  { plugin: "QSC 자동 분석", daily: 45, weekly: 234, monthly: 890 },
  { plugin: "계약 관리", daily: 34, weekly: 178, monthly: 567 },
  { plugin: "재고 관리", daily: 23, weekly: 123, monthly: 456 },
];

export default function AdminPluginStatisticsPage() {
  const [stats, setStats] = useState(dummyStats);
  const [installTrend, setInstallTrend] = useState(dummyInstallTrend);
  const [popularPlugins, setPopularPlugins] = useState(dummyPopularPlugins);
  const [usageStats, setUsageStats] = useState(dummyUsageStats);
  const [refreshing, setRefreshing] = useState(false);

  // 실시간 데이터 업데이트 시뮬레이션
  useEffect(() => {
    const interval = setInterval(() => {
      setStats(prev => ({
        ...prev,
        totalDownloads: prev.totalDownloads + Math.floor(Math.random() * 3),
        totalUsers: prev.totalUsers + Math.floor(Math.random() * 2),
      }));
    }, 10000); // 10초마다 업데이트

    return () => clearInterval(interval);
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    setTimeout(() => {
      setStats(dummyStats);
      setInstallTrend(dummyInstallTrend);
      setPopularPlugins(dummyPopularPlugins);
      setUsageStats(dummyUsageStats);
      setRefreshing(false);
      toast.success("통계가 새로고침되었습니다!");
    }, 1000);
  };

  const maxDownloads = Math.max(...installTrend.map(t => t.installs));
  const maxUsage = Math.max(...usageStats.map(u => u.monthly));

  return (
    <div className="container mx-auto p-6 max-w-6xl space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">플러그인 통계 (관리자)</h1>
        <Button onClick={handleRefresh} disabled={refreshing} className="flex items-center gap-2">
          {refreshing ? <RefreshCw className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
          새로고침
        </Button>
      </div>

      {/* 주요 지표 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">총 플러그인</p>
                <p className="text-2xl font-bold">{stats.totalPlugins}</p>
              </div>
              <Activity className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">활성 플러그인</p>
                <p className="text-2xl font-bold">{stats.activePlugins}</p>
              </div>
              <TrendingUp className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">총 다운로드</p>
                <p className="text-2xl font-bold">{stats.totalDownloads.toLocaleString()}</p>
              </div>
              <Download className="h-8 w-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">사용자 수</p>
                <p className="text-2xl font-bold">{stats.totalUsers}</p>
              </div>
              <Users className="h-8 w-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 설치/제거 추이 차트 */}
      <Card>
        <CardHeader>
          <CardTitle>월별 설치/제거 추이</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64 flex items-end justify-between gap-2 p-4">
            {installTrend.map((trend, index) => (
              <div key={index} className="flex flex-col items-center flex-1">
                <div className="flex flex-col items-center gap-1 mb-2">
                  <div
                    className="bg-green-500 rounded-t"
                    style={{
                      height: `${(trend.installs / maxDownloads) * 200}px`,
                      width: "20px",
                    }}
                  />
                  <div
                    className="bg-red-500 rounded-t"
                    style={{
                      height: `${(trend.uninstalls / maxDownloads) * 200}px`,
                      width: "20px",
                    }}
                  />
                </div>
                <div className="text-xs text-center">
                  <div className="font-medium">{trend.month}</div>
                  <div className="text-green-600">+{trend.installs}</div>
                  <div className="text-red-600">-{trend.uninstalls}</div>
                </div>
              </div>
            ))}
          </div>
          <div className="flex justify-center gap-4 text-sm">
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-green-500 rounded"></div>
              <span>설치</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-red-500 rounded"></div>
              <span>제거</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 인기 플러그인 */}
      <Card>
        <CardHeader>
          <CardTitle>인기 플러그인 TOP 5</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {popularPlugins.map((plugin, index) => (
              <div key={index} className="flex items-center justify-between p-3 border rounded">
                <div className="flex items-center gap-3">
                  <Badge variant="outline" className="w-8 h-8 flex items-center justify-center">
                    {index + 1}
                  </Badge>
                  <div>
                    <div className="font-medium">{plugin.name}</div>
                    <div className="text-sm text-muted-foreground">
                      ⭐ {plugin.rating} • {plugin.users}명 사용
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-bold">{plugin.downloads.toLocaleString()}</div>
                  <div className="text-sm text-muted-foreground">다운로드</div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 사용량 통계 */}
      <Card>
        <CardHeader>
          <CardTitle>플러그인별 사용량 통계</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {usageStats.map((stat, index) => (
              <div key={index} className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="font-medium">{stat.plugin}</span>
                  <span className="text-sm text-muted-foreground">
                    일: {stat.daily} • 주: {stat.weekly} • 월: {stat.monthly}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full"
                    style={{ width: `${(stat.monthly / maxUsage) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 
"use client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown,
  DollarSign,
  Users,
  Building2,
  Activity,
  Calendar
} from "lucide-react";

export default function AdminAnalytics() {
  // 더미 데이터
  const analytics = {
    overview: {
      totalRevenue: "₩2,450,000,000",
      totalStores: 8,
      totalUsers: 156,
      growthRate: "+12.5%"
    },
    monthlyData: [
      { month: "1월", revenue: 180, users: 120, orders: 4500 },
      { month: "2월", revenue: 200, users: 135, orders: 5200 },
      { month: "3월", revenue: 220, users: 145, orders: 5800 },
      { month: "4월", revenue: 240, users: 150, orders: 6200 },
      { month: "5월", revenue: 260, users: 155, orders: 6800 },
      { month: "6월", revenue: 280, users: 160, orders: 7200 },
    ],
    storePerformance: [
      { name: "강남점", revenue: "₩350,000,000", growth: "+15%", status: "excellent" },
      { name: "홍대점", revenue: "₩280,000,000", growth: "+8%", status: "good" },
      { name: "부산점", revenue: "₩220,000,000", growth: "+5%", status: "good" },
      { name: "대구점", revenue: "₩200,000,000", growth: "+2%", status: "warning" },
      { name: "인천점", revenue: "₩180,000,000", growth: "-1%", status: "poor" },
    ],
    userStats: {
      activeUsers: 142,
      newUsers: 23,
      churnRate: "2.1%",
      avgSessionTime: "45분"
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "excellent": return "bg-green-100 text-green-800";
      case "good": return "bg-blue-100 text-blue-800";
      case "warning": return "bg-yellow-100 text-yellow-800";
      case "poor": return "bg-red-100 text-red-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const getGrowthIcon = (growth: string) => {
    const isPositive = growth.startsWith('+');
    return isPositive ? 
      <TrendingUp className="h-4 w-4 text-green-600" /> : 
      <TrendingDown className="h-4 w-4 text-red-600" />;
  };

  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            브랜드 분석
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            전체 매장 통계 및 성과 분석
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="outline" className="flex items-center space-x-1">
            <BarChart3 className="h-4 w-4" />
            <span>슈퍼 관리자</span>
          </Badge>
        </div>
      </div>

      {/* 개요 통계 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 매출</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.overview.totalRevenue}</div>
            <p className="text-xs text-muted-foreground">
              {analytics.overview.growthRate} from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">전체 매장</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.overview.totalStores}</div>
            <p className="text-xs text-muted-foreground">
              운영 중인 매장
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">전체 사용자</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.overview.totalUsers}</div>
            <p className="text-xs text-muted-foreground">
              등록된 사용자
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">성장률</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{analytics.overview.growthRate}</div>
            <p className="text-xs text-muted-foreground">
              월간 성장률
            </p>
          </CardContent>
        </Card>
      </div>

      {/* 매장별 성과 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Building2 className="h-5 w-5" />
            <span>매장별 성과</span>
          </CardTitle>
          <CardDescription>
            각 매장의 매출 및 성장률 현황
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {analytics.storePerformance.map((store) => (
              <div key={store.name} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <div className="flex items-center space-x-4">
                  <div>
                    <h3 className="font-medium">{store.name}</h3>
                    <p className="text-sm text-muted-foreground">월 매출</p>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <p className="font-medium">{store.revenue}</p>
                    <div className="flex items-center space-x-1">
                      {getGrowthIcon(store.growth)}
                      <span className="text-sm">{store.growth}</span>
                    </div>
                  </div>
                  <Badge className={getStatusColor(store.status)}>
                    {store.status === "excellent" ? "우수" : 
                     store.status === "good" ? "양호" : 
                     store.status === "warning" ? "주의" : "개선 필요"}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 사용자 통계 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Users className="h-5 w-5" />
              <span>사용자 통계</span>
            </CardTitle>
            <CardDescription>
              사용자 활동 및 참여도 분석
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm">활성 사용자</span>
                <Badge variant="default">{analytics.userStats.activeUsers}명</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">신규 사용자</span>
                <Badge variant="secondary">{analytics.userStats.newUsers}명</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">이탈률</span>
                <Badge variant="outline">{analytics.userStats.churnRate}</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">평균 세션 시간</span>
                <Badge variant="outline">{analytics.userStats.avgSessionTime}</Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Activity className="h-5 w-5" />
              <span>월별 추이</span>
            </CardTitle>
            <CardDescription>
              최근 6개월 매출 및 사용자 추이
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {analytics.monthlyData.map((data) => (
                <div key={data.month} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div>
                    <h3 className="font-medium">{data.month}</h3>
                    <p className="text-sm text-muted-foreground">매출: ₩{data.revenue}M</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium">{data.users}명</p>
                    <p className="text-xs text-muted-foreground">{data.orders}건 주문</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 빠른 액션 */}
      <Card>
        <CardHeader>
          <CardTitle>분석 도구</CardTitle>
          <CardDescription>
            상세 분석 및 리포트 생성
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Button variant="outline" className="h-16 flex flex-col space-y-2">
              <BarChart3 className="h-5 w-5" />
              <span className="text-sm">상세 리포트</span>
            </Button>
            <Button variant="outline" className="h-16 flex flex-col space-y-2">
              <TrendingUp className="h-5 w-5" />
              <span className="text-sm">성장 분석</span>
            </Button>
            <Button variant="outline" className="h-16 flex flex-col space-y-2">
              <Users className="h-5 w-5" />
              <span className="text-sm">사용자 분석</span>
            </Button>
            <Button variant="outline" className="h-16 flex flex-col space-y-2">
              <Calendar className="h-5 w-5" />
              <span className="text-sm">기간별 비교</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 
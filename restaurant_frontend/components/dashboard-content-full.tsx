"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { 
  TrendingUp, 
  TrendingDown, 
  Users, 
  ShoppingCart, 
  Clock, 
  DollarSign,
  Calendar,
  AlertTriangle
} from "lucide-react"

export function DashboardContentFull() {
  // 더미 데이터 (나중에 백엔드 API로 교체)
  const stats = [
    {
      title: "오늘 매출",
      value: "₩2,450,000",
      change: "+12.5%",
      trend: "up",
      icon: DollarSign,
      color: "text-green-600"
    },
    {
      title: "주문 수",
      value: "156",
      change: "+8.2%",
      trend: "up",
      icon: ShoppingCart,
      color: "text-blue-600"
    },
    {
      title: "고객 수",
      value: "89",
      change: "+15.3%",
      trend: "up",
      icon: Users,
      color: "text-purple-600"
    },
    {
      title: "평균 대기시간",
      value: "12분",
      change: "-5.2%",
      trend: "down",
      icon: Clock,
      color: "text-orange-600"
    }
  ]

  const recentOrders = [
    { id: 1, customer: "김철수", items: "스테이크 2개, 와인 1병", total: "₩85,000", status: "완료", time: "5분 전" },
    { id: 2, customer: "이영희", items: "파스타 1개, 샐러드 1개", total: "₩32,000", status: "조리중", time: "12분 전" },
    { id: 3, customer: "박민수", items: "피자 1개, 콜라 2개", total: "₩28,000", status: "대기중", time: "18분 전" },
    { id: 4, customer: "최지영", items: "스테이크 1개, 와인 1병", total: "₩65,000", status: "완료", time: "25분 전" },
  ]

  const alerts = [
    { type: "재고부족", message: "소고기 재고가 부족합니다", priority: "high" },
    { type: "근무변경", message: "오늘 야간 근무자가 변경되었습니다", priority: "medium" },
    { type: "시스템", message: "백업이 완료되었습니다", priority: "low" },
  ]

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "완료":
        return <Badge variant="default" className="bg-green-100 text-green-800">완료</Badge>
      case "조리중":
        return <Badge variant="secondary" className="bg-blue-100 text-blue-800">조리중</Badge>
      case "대기중":
        return <Badge variant="outline" className="bg-yellow-100 text-yellow-800">대기중</Badge>
      default:
        return <Badge variant="outline">{status}</Badge>
    }
  }

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case "high":
        return <AlertTriangle className="h-4 w-4 text-red-500" />
      case "medium":
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />
      case "low":
        return <AlertTriangle className="h-4 w-4 text-green-500" />
      default:
        return <AlertTriangle className="h-4 w-4" />
    }
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Welcome Section */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">대시보드</h1>
          <p className="text-muted-foreground">
            오늘의 매장 현황을 한눈에 확인하세요
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Calendar className="h-5 w-5 text-muted-foreground" />
          <span className="text-sm text-muted-foreground">
            {new Date().toLocaleDateString('ko-KR', { 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric',
              weekday: 'long'
            })}
          </span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, index) => {
          const Icon = stat.icon
          return (
            <Card key={index}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {stat.title}
                </CardTitle>
                <Icon className={`h-4 w-4 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <div className="flex items-center text-xs text-muted-foreground">
                  {stat.trend === "up" ? (
                    <TrendingUp className="mr-1 h-3 w-3 text-green-500" />
                  ) : (
                    <TrendingDown className="mr-1 h-3 w-3 text-red-500" />
                  )}
                  {stat.change} 지난주 대비
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Main Content Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Recent Orders */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>최근 주문</CardTitle>
            <CardDescription>
              오늘 들어온 주문 현황입니다
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentOrders.map((order) => (
                <div key={order.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="space-y-1">
                    <p className="text-sm font-medium">{order.customer}</p>
                    <p className="text-xs text-muted-foreground">{order.items}</p>
                    <p className="text-xs text-muted-foreground">{order.time}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium">{order.total}</p>
                    {getStatusBadge(order.status)}
                  </div>
                </div>
              ))}
            </div>
            <Button variant="outline" className="w-full mt-4">
              모든 주문 보기
            </Button>
          </CardContent>
        </Card>

        {/* Alerts */}
        <Card>
          <CardHeader>
            <CardTitle>알림</CardTitle>
            <CardDescription>
              중요한 알림사항입니다
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {alerts.map((alert, index) => (
                <div key={index} className="flex items-start gap-3 p-3 border rounded-lg">
                  {getPriorityIcon(alert.priority)}
                  <div className="flex-1">
                    <p className="text-sm font-medium">{alert.type}</p>
                    <p className="text-xs text-muted-foreground">{alert.message}</p>
                  </div>
                </div>
              ))}
            </div>
            <Button variant="outline" className="w-full mt-4">
              모든 알림 보기
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Progress Section */}
      <Card>
        <CardHeader>
          <CardTitle>오늘의 목표</CardTitle>
          <CardDescription>
            매출 목표 달성률을 확인하세요
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">매출 목표</span>
              <span className="text-sm text-muted-foreground">₩2,450,000 / ₩3,000,000</span>
            </div>
            <Progress value={82} className="w-full" />
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">주문 목표</span>
              <span className="text-sm text-muted-foreground">156 / 200</span>
            </div>
            <Progress value={78} className="w-full" />
          </div>
        </CardContent>
      </Card>
    </div>
  )
} 
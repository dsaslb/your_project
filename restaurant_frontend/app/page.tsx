"use client"

import { useState } from "react"
import { AppLayout } from "@/components/app-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { 
  DollarSign, 
  Users, 
  ShoppingCart, 
  ChefHat,
  Utensils,
  Package,
  TrendingUp,
  Clock,
  BarChart3
} from "lucide-react"

export default function DashboardPage() {
  const [currentTime] = useState(new Date())

  return (
    <AppLayout>
      <div className="bg-gray-50 dark:bg-gray-900 p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* 헤더 */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">레스토랑 대시보드</h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {currentTime.toLocaleDateString("ko-KR")} {currentTime.toLocaleTimeString("ko-KR")}
              </p>
            </div>
          </div>

          {/* 상단 통계 카드 */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                title: "오늘 매출",
                value: "₩1,250,000",
                change: "+15.2%",
                icon: DollarSign,
                color: "text-green-600",
                bgColor: "bg-green-100 dark:bg-green-900/20",
              },
              {
                title: "활성 주문",
                value: "23건",
                change: "+5건",
                icon: ShoppingCart,
                color: "text-blue-600",
                bgColor: "bg-blue-100 dark:bg-blue-900/20",
              },
              {
                title: "테이블 점유율",
                value: "85%",
                change: "+12%",
                icon: Utensils,
                color: "text-purple-600",
                bgColor: "bg-purple-100 dark:bg-purple-900/20",
              },
              {
                title: "근무 직원",
                value: "12명",
                change: "정상",
                icon: Users,
                color: "text-orange-600",
                bgColor: "bg-orange-100 dark:bg-orange-900/20",
              },
            ].map((stat, index) => (
              <Card key={index} className="hover:shadow-lg transition-all duration-200">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{stat.title}</p>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{stat.value}</p>
                      <div className="flex items-center mt-1">
                        <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
                        <span className="text-sm font-medium text-green-600">{stat.change}</span>
                      </div>
                    </div>
                    <div className={`p-3 rounded-full ${stat.bgColor}`}>
                      <stat.icon className={`w-6 h-6 ${stat.color}`} />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
          
          {/* 중단 그리드 섹션 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 실시간 주문 현황 */}
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center text-lg">
                  <ChefHat className="w-5 h-5 mr-2" />
                  실시간 주문 현황
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="space-y-3">
                  {[
                    { id: "ORD-001", table: "테이블 5", items: ["불고기 정식", "김치찌개"], status: "조리중", time: "15분 전" },
                    { id: "ORD-002", table: "테이블 12", items: ["비빔밥", "된장찌개"], status: "대기중", time: "5분 전" },
                    { id: "ORD-003", table: "테이블 3", items: ["갈비탕", "냉면"], status: "서빙대기", time: "2분 전" },
                  ].map((order) => (
                    <div
                      key={order.id}
                      className="flex items-start space-x-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-800 border-l-2 border-blue-500"
                    >
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-1">
                          <div className="flex items-center space-x-2">
                            <span className="text-sm font-medium text-gray-900 dark:text-white">{order.id}</span>
                            <Badge variant="outline" className="text-xs">
                              {order.table}
                            </Badge>
                          </div>
                          <Badge className={`text-xs ${
                            order.status === "조리중" ? "bg-blue-100 text-blue-800" :
                            order.status === "대기중" ? "bg-yellow-100 text-yellow-800" :
                            "bg-orange-100 text-orange-800"
                          }`}>
                            {order.status}
                          </Badge>
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                          {order.items.join(", ")}
                        </div>
                        <div className="flex items-center">
                          <Clock className="w-3 h-3 text-gray-500 mr-1" />
                          <span className="text-xs text-gray-500">{order.time}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* 테이블 현황 */}
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center text-lg">
                  <Utensils className="w-5 h-5 mr-2" />
                  테이블 현황
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="grid grid-cols-4 gap-2">
                  {[
                    { number: 1, status: "occupied", guests: 4 },
                    { number: 2, status: "available", guests: 0 },
                    { number: 3, status: "occupied", guests: 2 },
                    { number: 4, status: "reserved", guests: 6 },
                    { number: 5, status: "occupied", guests: 3 },
                    { number: 6, status: "cleaning", guests: 0 },
                    { number: 7, status: "available", guests: 0 },
                    { number: 8, status: "occupied", guests: 2 },
                  ].map((table) => (
                    <div
                      key={table.number}
                      className="relative p-2 rounded-lg border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow"
                    >
                      <div
                        className={`absolute top-1 right-1 w-2 h-2 rounded-full ${
                          table.status === "occupied" ? "bg-red-500" :
                          table.status === "available" ? "bg-green-500" :
                          table.status === "reserved" ? "bg-blue-500" :
                          "bg-yellow-500"
                        }`}
                      />
                      <div className="text-center">
                        <div className="text-sm font-bold text-gray-900 dark:text-white">{table.number}</div>
                        <div className="text-xs text-gray-600 dark:text-gray-400">
                          {table.status === "occupied" && `${table.guests}명`}
                          {table.status === "reserved" && `${table.guests}명`}
                          {table.status === "available" && "빈 테이블"}
                          {table.status === "cleaning" && "정리중"}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="mt-3 flex items-center justify-between text-xs">
                  <div className="flex items-center space-x-3">
                    <div className="flex items-center">
                      <div className="w-2 h-2 bg-red-500 rounded-full mr-1" />
                      <span>사용중</span>
                    </div>
                    <div className="flex items-center">
                      <div className="w-2 h-2 bg-green-500 rounded-full mr-1" />
                      <span>빈 테이블</span>
                    </div>
                    <div className="flex items-center">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mr-1" />
                      <span>예약</span>
                    </div>
                    <div className="flex items-center">
                      <div className="w-2 h-2 bg-yellow-500 rounded-full mr-1" />
                      <span>정리중</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 하단 섹션 */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* 재고 알림 */}
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center text-lg">
                  <Package className="w-5 h-5 mr-2" />
                  재고 알림
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="space-y-3">
                  {[
                    { item: "돼지고기", status: "부족", quantity: "2kg", threshold: "5kg" },
                    { item: "양파", status: "부족", quantity: "1kg", threshold: "3kg" },
                    { item: "고추가루", status: "부족", quantity: "500g", threshold: "1kg" },
                  ].map((stock, index) => (
                    <div key={index} className="flex items-center justify-between p-2 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
                      <div>
                        <p className="text-sm font-medium text-gray-900 dark:text-white">{stock.item}</p>
                        <p className="text-xs text-red-600">{stock.quantity} / {stock.threshold}</p>
                      </div>
                      <Badge variant="destructive" className="text-xs">
                        {stock.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* 오늘의 일정 */}
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center text-lg">
                  <Clock className="w-5 h-5 mr-2" />
                  오늘의 일정
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="space-y-3">
                  {[
                    { time: "09:00", event: "직원 출근", type: "근무" },
                    { time: "11:00", event: "재고 점검", type: "관리" },
                    { time: "14:00", event: "청소", type: "청소" },
                    { time: "16:00", event: "재료 발주", type: "발주" },
                    { time: "22:00", event: "마감 정리", type: "근무" },
                  ].map((schedule, index) => (
                    <div key={index} className="flex items-center space-x-3 p-2 rounded-lg bg-gray-50 dark:bg-gray-800">
                      <div className="text-sm font-medium text-gray-900 dark:text-white min-w-[50px]">
                        {schedule.time}
                      </div>
                      <div className="flex-1">
                        <p className="text-sm text-gray-900 dark:text-white">{schedule.event}</p>
                      </div>
                      <Badge variant="outline" className="text-xs">
                        {schedule.type}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* 빠른 액션 */}
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">빠른 액션</CardTitle>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="space-y-3">
                  <Button className="w-full justify-start" variant="outline">
                    <ShoppingCart className="w-4 h-4 mr-2" />
                    새 주문 등록
                  </Button>
                  <Button className="w-full justify-start" variant="outline">
                    <Package className="w-4 h-4 mr-2" />
                    재고 발주
                  </Button>
                  <Button className="w-full justify-start" variant="outline">
                    <Users className="w-4 h-4 mr-2" />
                    직원 관리
                  </Button>
                  <Button className="w-full justify-start" variant="outline">
                    <BarChart3 className="w-4 h-4 mr-2" />
                    매출 보고서
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </AppLayout>
  )
} 
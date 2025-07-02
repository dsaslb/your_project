"use client"

import React, { useState, useEffect } from 'react'
import { AppLayout } from "@/components/app-layout"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  DollarSign, 
  Users, 
  ShoppingCart, 
  ChefHat,
  Utensils,
  Package,
  TrendingUp,
  TrendingDown,
  Clock,
  Bell,
  AlertCircle,
  AlertTriangle,
  Settings,
  FileText,
  CheckCircle,
  Activity
} from "lucide-react"
import { useUser } from '@/components/UserContext'
import { toast } from '@/lib/toast'
import NotificationService from '@/lib/notification-service'
import { useRealtime, useRealtimeEvent } from '@/lib/realtime-service'
import { useNotifications } from '@/components/NotificationSystem'
import { apiClient } from '@/lib/api-client'

interface DashboardStats {
  totalOrders: number;
  pendingOrders: number;
  completedOrders: number;
  totalRevenue: number;
  totalStaff: number;
  activeStaff: number;
  inventoryItems: number;
  lowStockItems: number;
  todaySales: number;
  weeklyGrowth: number;
}

interface RecentActivity {
  id: string;
  type: string;
  title: string;
  description: string;
  timestamp: string;
  status: 'success' | 'warning' | 'error' | 'info';
}

export default function DashboardPage() {
  const { user } = useUser()
  const [currentTime] = useState(new Date())
  const [notificationStats, setNotificationStats] = useState<any>(null)
  const [noticeStats, setNoticeStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState<DashboardStats>({
    totalOrders: 0,
    pendingOrders: 0,
    completedOrders: 0,
    totalRevenue: 0,
    totalStaff: 0,
    activeStaff: 0,
    inventoryItems: 0,
    lowStockItems: 0,
    todaySales: 0,
    weeklyGrowth: 0,
  })
  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>([])

  // 실시간 서비스 연결
  const { isConnected, lastEvent } = useRealtime()
  const { addNotification } = useNotifications()

  // 실시간 이벤트 구독
  const orderEvent = useRealtimeEvent('order.created')
  const inventoryEvent = useRealtimeEvent('inventory.low')
  const staffEvent = useRealtimeEvent('staff.attendance')

  // 알림 통계 로드
  useEffect(() => {
    const loadNotificationStats = async () => {
      try {
        const stats = await NotificationService.getNotificationStats()
        setNotificationStats(stats)
      } catch (error) {
        console.error('알림 통계 로드 실패:', error)
      }
    }

    const loadNoticeStats = async () => {
      try {
        const stats = await NotificationService.getNoticeStats()
        setNoticeStats(stats)
      } catch (error) {
        console.error('공지사항 통계 로드 실패:', error)
      }
    }

    loadNotificationStats()
    loadNoticeStats()
    setLoading(false)
  }, [])

  // 초기 데이터 로드
  useEffect(() => {
    loadDashboardData()
  }, [])

  // 실시간 이벤트 처리
  useEffect(() => {
    if (orderEvent) {
      handleOrderEvent(orderEvent)
    }
  }, [orderEvent])

  useEffect(() => {
    if (inventoryEvent) {
      handleInventoryEvent(inventoryEvent)
    }
  }, [inventoryEvent])

  useEffect(() => {
    if (staffEvent) {
      handleStaffEvent(staffEvent)
    }
  }, [staffEvent])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      
      // 대시보드 통계 로드
      const statsData = await apiClient.get<DashboardStats>('/dashboard/stats')
      setStats(statsData)
      
      // 최근 활동 로드
      const activitiesData = await apiClient.get<RecentActivity[]>('/dashboard/activities')
      setRecentActivities(activitiesData)
      
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
      addNotification({
        type: 'error',
        title: '데이터 로드 실패',
        message: '대시보드 데이터를 불러오는데 실패했습니다.',
      })
    } finally {
      setLoading(false)
    }
  }

  const handleOrderEvent = (event: any) => {
    // 주문 통계 업데이트
    setStats(prev => ({
      ...prev,
      totalOrders: prev.totalOrders + 1,
      pendingOrders: prev.pendingOrders + 1,
    }))

    // 최근 활동에 추가
    const newActivity: RecentActivity = {
      id: Date.now().toString(),
      type: 'order',
      title: '새 주문 등록',
      description: `새로운 주문이 등록되었습니다.`,
      timestamp: new Date().toISOString(),
      status: 'info',
    }

    setRecentActivities(prev => [newActivity, ...prev.slice(0, 9)])
  }

  const handleInventoryEvent = (event: any) => {
    // 재고 통계 업데이트
    setStats(prev => ({
      ...prev,
      lowStockItems: prev.lowStockItems + 1,
    }))

    // 알림 추가
    addNotification({
      type: 'warning',
      title: '재고 부족',
      message: '일부 재고가 부족합니다. 확인해주세요.',
      action: {
        label: '재고 확인',
        url: '/inventory',
      },
    })
  }

  const handleStaffEvent = (event: any) => {
    // 직원 통계 업데이트
    setStats(prev => ({
      ...prev,
      activeStaff: prev.activeStaff + 1,
    }))

    // 최근 활동에 추가
    const newActivity: RecentActivity = {
      id: Date.now().toString(),
      type: 'staff',
      title: '직원 출근',
      description: `직원이 출근했습니다.`,
      timestamp: new Date().toISOString(),
      status: 'success',
    }

    setRecentActivities(prev => [newActivity, ...prev.slice(0, 9)])
  }

  // 시스템 알림 테스트
  const handleTestSystemNotification = async (type: 'maintenance' | 'backup' | 'error' | 'update') => {
    try {
      const systemData = {
        scheduledTime: new Date().toLocaleString(),
        version: '1.0.0',
        message: '테스트 시스템 알림입니다.'
      }

      await NotificationService.createSystemNotification(type, systemData)
      toast.success(`${type} 알림이 생성되었습니다.`)
    } catch (error) {
      console.error('시스템 알림 생성 실패:', error)
      toast.error('시스템 알림 생성에 실패했습니다.')
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />
      case 'error':
        return <AlertTriangle className="h-4 w-4 text-red-500" />
      default:
        return <Activity className="h-4 w-4 text-blue-500" />
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW',
    }).format(amount)
  }

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('ko-KR', {
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      </div>
    )
  }

  return (
    <AppLayout>
      <div className="w-full h-full bg-gray-50 dark:bg-gray-900 p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* 헤더 */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">레스토랑 대시보드</h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {user?.name}님, 환영합니다! 오늘도 좋은 하루 되세요.
              </p>
            </div>
            <div className="flex space-x-2">
              <Button 
                variant="outline" 
                onClick={() => handleTestSystemNotification('maintenance')}
              >
                점검 알림 테스트
              </Button>
              <Button 
                variant="outline" 
                onClick={() => handleTestSystemNotification('update')}
              >
                업데이트 알림 테스트
              </Button>
            </div>
          </div>

          {/* 실시간 상태 표시 */}
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold">대시보드</h1>
            <div className="flex items-center gap-2">
              <Badge variant={isConnected ? "default" : "secondary"}>
                {isConnected ? "실시간 연결됨" : "연결 끊김"}
              </Badge>
              {lastEvent && (
                <span className="text-sm text-muted-foreground">
                  마지막 업데이트: {formatTime(lastEvent.timestamp)}
                </span>
              )}
            </div>
          </div>

          {/* 알림 통계 카드 */}
          {notificationStats && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400">총 알림</p>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white">
                        {notificationStats.total}개
                      </p>
                    </div>
                    <Bell className="w-8 h-8 text-blue-600" />
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400">읽지 않은 알림</p>
                      <p className="text-2xl font-bold text-red-600">
                        {notificationStats.unread}개
                      </p>
                    </div>
                    <AlertCircle className="w-8 h-8 text-red-600" />
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400">긴급 알림</p>
                      <p className="text-2xl font-bold text-orange-600">
                        {notificationStats.byPriority.high}개
                      </p>
                    </div>
                    <AlertTriangle className="w-8 h-8 text-orange-600" />
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400">시스템 알림</p>
                      <p className="text-2xl font-bold text-purple-600">
                        {notificationStats.byType.system}개
                      </p>
                    </div>
                    <Settings className="w-8 h-8 text-purple-600" />
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* 공지사항 통계 카드 */}
          {noticeStats && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400">총 공지사항</p>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white">
                        {noticeStats.total}개
                      </p>
                    </div>
                    <FileText className="w-8 h-8 text-green-600" />
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400">긴급 공지</p>
                      <p className="text-2xl font-bold text-red-600">
                        {noticeStats.byPriority.high}개
                      </p>
                    </div>
                    <AlertTriangle className="w-8 h-8 text-red-600" />
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400">시스템 공지</p>
                      <p className="text-2xl font-bold text-blue-600">
                        {noticeStats.byCategory.시스템}개
                      </p>
                    </div>
                    <Settings className="w-8 h-8 text-blue-600" />
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

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
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 직원 근무 현황 */}
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center text-lg">
                  <Users className="w-5 h-5 mr-2" />
                  직원 근무 현황
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="space-y-3">
                  {[
                    { name: "김주방장", position: "주방장", status: "근무중", shift: "09:00-18:00" },
                    { name: "박요리사", position: "요리사", status: "근무중", shift: "10:00-19:00" },
                    { name: "이서버", position: "서버", status: "휴게시간", shift: "11:00-20:00" },
                    { name: "최캐셔", position: "캐셔", status: "근무중", shift: "09:00-18:00" },
                  ].map((staff, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-800"
                    >
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/20 rounded-full flex items-center justify-center">
                          <Users className="w-5 h-5 text-blue-600" />
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-900 dark:text-white">{staff.name}</p>
                          <p className="text-xs text-gray-600 dark:text-gray-400">{staff.position}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <Badge
                          className={`text-xs ${staff.status === "근무중" ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"}`}
                        >
                          {staff.status}
                        </Badge>
                        <p className="text-xs text-gray-500">{staff.shift}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* 재고 알림 */}
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center text-lg">
                  <Package className="w-5 h-5 mr-2" />
                  재고 현황
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="space-y-3">
                  {[
                    { item: "돼지고기", level: "2kg", unit: "kg", status: "부족" },
                    { item: "양파", level: "5개", unit: "개", status: "주의" },
                    { item: "김치", level: "1kg", unit: "kg", status: "부족" },
                  ].map((item, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 rounded-lg border border-gray-200 dark:border-gray-700"
                    >
                      <div className="flex items-center space-x-3">
                        <div
                          className={`w-2 h-2 rounded-full ${item.status === "부족" ? "bg-red-500" : "bg-yellow-500"}`}
                        />
                        <div>
                          <p className="text-sm font-medium text-gray-900 dark:text-white">{item.item}</p>
                          <p className="text-xs text-gray-600 dark:text-gray-400">
                            {item.level} {item.unit} 남음
                          </p>
                        </div>
                      </div>
                      <Badge
                        variant="outline"
                        className={`text-xs ${item.status === "부족" ? "border-red-200 text-red-700" : "border-yellow-200 text-yellow-700"}`}
                      >
                        {item.status}
                      </Badge>
                    </div>
                  ))}
                </div>
                <Button className="w-full mt-3 bg-transparent" variant="outline" size="sm">
                  전체 재고 보기
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* 주요 통계 카드 */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">총 주문</CardTitle>
                <ShoppingCart className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.totalOrders}</div>
                <p className="text-xs text-muted-foreground">
                  대기: {stats.pendingOrders} | 완료: {stats.completedOrders}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">총 매출</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatCurrency(stats.totalRevenue)}</div>
                <p className="text-xs text-muted-foreground">
                  오늘: {formatCurrency(stats.todaySales)}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">직원</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.activeStaff}</div>
                <p className="text-xs text-muted-foreground">
                  전체: {stats.totalStaff}명
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">재고</CardTitle>
                <Package className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.inventoryItems}</div>
                <p className="text-xs text-muted-foreground">
                  부족: {stats.lowStockItems}개
                </p>
              </CardContent>
            </Card>
          </div>

          {/* 성장률 및 진행률 */}
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>주간 성장률</CardTitle>
                <CardDescription>이번 주 매출 성장률</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  {stats.weeklyGrowth >= 0 ? (
                    <TrendingUp className="h-4 w-4 text-green-500" />
                  ) : (
                    <TrendingDown className="h-4 w-4 text-red-500" />
                  )}
                  <span className={`text-2xl font-bold ${
                    stats.weeklyGrowth >= 0 ? 'text-green-500' : 'text-red-500'
                  }`}>
                    {stats.weeklyGrowth >= 0 ? '+' : ''}{stats.weeklyGrowth}%
                  </span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>주문 완료율</CardTitle>
                <CardDescription>전체 주문 대비 완료율</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>완료율</span>
                    <span>{stats.totalOrders > 0 ? Math.round((stats.completedOrders / stats.totalOrders) * 100) : 0}%</span>
                  </div>
                  <Progress 
                    value={stats.totalOrders > 0 ? (stats.completedOrders / stats.totalOrders) * 100 : 0} 
                    className="w-full" 
                  />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 최근 활동 */}
          <Card>
            <CardHeader>
              <CardTitle>최근 활동</CardTitle>
              <CardDescription>실시간으로 업데이트되는 최근 활동</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentActivities.length === 0 ? (
                  <p className="text-center text-muted-foreground py-8">
                    아직 활동이 없습니다.
                  </p>
                ) : (
                  recentActivities.map((activity) => (
                    <div key={activity.id} className="flex items-start gap-3 p-3 rounded-lg border">
                      {getStatusIcon(activity.status)}
                      <div className="flex-1 min-w-0">
                        <h4 className="font-medium text-sm">{activity.title}</h4>
                        <p className="text-sm text-muted-foreground">{activity.description}</p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {formatTime(activity.timestamp)}
                        </p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>

          {/* 빠른 액션 */}
          <Card>
            <CardHeader>
              <CardTitle>빠른 액션</CardTitle>
              <CardDescription>자주 사용하는 기능에 빠르게 접근</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Button variant="outline" className="h-20 flex-col gap-2" onClick={() => window.location.href = '/orders'}>
                  <ShoppingCart className="h-6 w-6" />
                  <span>주문 관리</span>
                </Button>
                <Button variant="outline" className="h-20 flex-col gap-2" onClick={() => window.location.href = '/inventory'}>
                  <Package className="h-6 w-6" />
                  <span>재고 관리</span>
                </Button>
                <Button variant="outline" className="h-20 flex-col gap-2" onClick={() => window.location.href = '/staff'}>
                  <Users className="h-6 w-6" />
                  <span>직원 관리</span>
                </Button>
                <Button variant="outline" className="h-20 flex-col gap-2" onClick={() => window.location.href = '/schedule'}>
                  <Calendar className="h-6 w-6" />
                  <span>스케줄 관리</span>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppLayout>
  )
} 
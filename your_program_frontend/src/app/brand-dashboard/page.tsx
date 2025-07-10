"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { 
  Building2, 
  TrendingUp, 
  Users, 
  DollarSign, 
  ShoppingCart, 
  Calendar,
  LogOut,
  BarChart3,
  Store,
  ChefHat,
  Clock,
  AlertTriangle
} from "lucide-react"

interface AuthState {
  isAuthenticated: boolean
  username: string
  selectedRole: string | null
}

export default function BrandDashboard() {
  const router = useRouter()
  const [authState, setAuthState] = useState<AuthState | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // 인증 상태 확인
    const savedAuth = localStorage.getItem("authState")
    if (savedAuth) {
      const parsedAuth = JSON.parse(savedAuth)
      setAuthState(parsedAuth)
      
      // 인증되지 않았거나 권한이 없는 경우 로그인 페이지로 리다이렉트
      if (!parsedAuth.isAuthenticated) {
        router.push("/login")
        return
      }
      
      // admin 또는 brand 계정만 접근 가능
      const allowedUsers = ["admin", "brand"]
      if (!allowedUsers.includes(parsedAuth.username)) {
        router.push("/login")
        return
      }
      
      // admin이지만 다른 역할을 선택한 경우 해당 역할의 대시보드로 리다이렉트
      if (parsedAuth.username === "admin" && parsedAuth.selectedRole && parsedAuth.selectedRole !== "brand-admin") {
        const roleRoutes = {
          "store-manager": "/manager-dashboard",
          "employee": "/employee-dashboard"
        }
        const targetRoute = roleRoutes[parsedAuth.selectedRole as keyof typeof roleRoutes]
        if (targetRoute) {
          router.push(targetRoute)
          return
        }
      }
    } else {
      router.push("/login")
      return
    }
    
    setIsLoading(false)
  }, [router])

  const handleLogout = () => {
    localStorage.removeItem("authState")
    router.push("/login")
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-400">로딩 중...</p>
        </div>
      </div>
    )
  }

  if (!authState?.isAuthenticated) {
    return null
  }

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {/* 헤더 */}
      <header className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-gradient-to-r from-purple-600 to-purple-700 rounded-lg flex items-center justify-center">
                <Building2 className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">브랜드 관리자 대시보드</h1>
                <p className="text-sm text-slate-400">
                  {authState.username === "admin" ? "최고 관리자" : "브랜드 관리자"} - 전체 매장 관리
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Badge variant="secondary" className="bg-purple-500/20 text-purple-300 border-purple-500/30">
                {authState.username === "admin" ? "최고 관리자" : "브랜드 관리자"}
              </Badge>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={handleLogout}
                className="text-slate-400 hover:text-white"
              >
                <LogOut className="h-4 w-4 mr-2" />
                로그아웃
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* 메인 콘텐츠 */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="bg-slate-800 border-slate-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-400">총 매장 수</p>
                  <p className="text-2xl font-bold text-white">24</p>
                </div>
                <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
                  <Store className="h-6 w-6 text-blue-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800 border-slate-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-400">총 직원 수</p>
                  <p className="text-2xl font-bold text-white">342</p>
                </div>
                <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
                  <Users className="h-6 w-6 text-green-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800 border-slate-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-400">월 매출</p>
                  <p className="text-2xl font-bold text-white">₩2.4억</p>
                </div>
                <div className="w-12 h-12 bg-yellow-500/20 rounded-lg flex items-center justify-center">
                  <DollarSign className="h-6 w-6 text-yellow-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800 border-slate-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-400">평균 주문</p>
                  <p className="text-2xl font-bold text-white">₩18,500</p>
                </div>
                <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center">
                  <ShoppingCart className="h-6 w-6 text-purple-400" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 매장별 현황 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-blue-400" />
                매장별 매출 현황
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { name: "강남점", sales: "₩3,200만", growth: "+12%", status: "success" },
                  { name: "홍대점", sales: "₩2,800만", growth: "+8%", status: "success" },
                  { name: "부산점", sales: "₩2,100만", growth: "+5%", status: "warning" },
                  { name: "대구점", sales: "₩1,900만", growth: "-2%", status: "error" }
                ].map((store, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-slate-600 rounded-full flex items-center justify-center">
                        <Store className="h-4 w-4 text-slate-300" />
                      </div>
                      <div>
                        <p className="font-medium text-white">{store.name}</p>
                        <p className="text-sm text-slate-400">{store.sales}</p>
                      </div>
                    </div>
                    <Badge 
                      variant={store.status === "success" ? "default" : store.status === "warning" ? "secondary" : "destructive"}
                      className={
                        store.status === "success" ? "bg-green-500/20 text-green-300 border-green-500/30" :
                        store.status === "warning" ? "bg-yellow-500/20 text-yellow-300 border-yellow-500/30" :
                        "bg-red-500/20 text-red-300 border-red-500/30"
                      }
                    >
                      {store.growth}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800 border-slate-700">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5 text-green-400" />
                실시간 알림
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { type: "warning", message: "강남점 재고 부족 - 치킨 가슴살", time: "5분 전" },
                  { type: "info", message: "홍대점 신규 직원 등록 완료", time: "15분 전" },
                  { type: "success", message: "부산점 월 매출 목표 달성", time: "1시간 전" },
                  { type: "error", message: "대구점 시스템 오류 발생", time: "2시간 전" }
                ].map((alert, index) => (
                  <div key={index} className="flex items-start gap-3 p-3 bg-slate-700/50 rounded-lg">
                    <div className={`w-2 h-2 rounded-full mt-2 ${
                      alert.type === "warning" ? "bg-yellow-400" :
                      alert.type === "info" ? "bg-blue-400" :
                      alert.type === "success" ? "bg-green-400" :
                      "bg-red-400"
                    }`}></div>
                    <div className="flex-1">
                      <p className="text-sm text-white">{alert.message}</p>
                      <p className="text-xs text-slate-400 mt-1">{alert.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 빠른 액션 */}
        <div className="mt-8">
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader>
              <CardTitle>빠른 액션</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Button className="h-auto p-4 flex flex-col items-center gap-2 bg-blue-600 hover:bg-blue-700">
                  <Store className="h-6 w-6" />
                  <span>매장 관리</span>
                </Button>
                <Button className="h-auto p-4 flex flex-col items-center gap-2 bg-green-600 hover:bg-green-700">
                  <Users className="h-6 w-6" />
                  <span>직원 관리</span>
                </Button>
                <Button className="h-auto p-4 flex flex-col items-center gap-2 bg-purple-600 hover:bg-purple-700">
                  <BarChart3 className="h-6 w-6" />
                  <span>매출 분석</span>
                </Button>
                <Button className="h-auto p-4 flex flex-col items-center gap-2 bg-yellow-600 hover:bg-yellow-700">
                  <Calendar className="h-6 w-6" />
                  <span>스케줄 관리</span>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
} 
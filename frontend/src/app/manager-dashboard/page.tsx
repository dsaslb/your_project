"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { 
  Store, 
  TrendingUp, 
  Users, 
  DollarSign, 
  ShoppingCart, 
  Calendar,
  LogOut,
  BarChart3,
  ChefHat,
  Clock,
  AlertTriangle,
  MapPin,
  Star
} from "lucide-react"

interface AuthState {
  isAuthenticated: boolean
  username: string
  selectedRole: string | null
}

export default function ManagerDashboard() {
  const router = useRouter()
  const [authState, setAuthState] = useState<AuthState | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // JWT 토큰 확인
    const token = localStorage.getItem('jwt_token')
    const savedAuth = localStorage.getItem("authState")
    
    if (token && savedAuth) {
      try {
        const parsedAuth = JSON.parse(savedAuth)
        setAuthState(parsedAuth)
        
        // 인증되지 않았거나 권한이 없는 경우 로그인 페이지로 리다이렉트
        if (!parsedAuth.isAuthenticated) {
          router.push("/login")
          return
        }
        
        // store_admin 또는 admin 역할만 접근 가능
        const allowedRoles = ["store_admin", "admin"]
        if (!allowedRoles.includes(parsedAuth.selectedRole)) {
          router.push("/login")
          return
        }
        
        // admin이지만 다른 역할을 선택한 경우 해당 역할의 대시보드로 리다이렉트
        if (parsedAuth.selectedRole === "admin") {
          router.push("/admin-dashboard")
          return
        }
      } catch (error) {
        console.error("인증 상태 파싱 오류:", error)
        router.push("/login")
        return
      }
    } else {
      router.push("/login")
      return
    }
    
    setIsLoading(false)
  }, [router])

  const handleLogout = () => {
    localStorage.removeItem("authState")
    localStorage.removeItem("jwt_token")
    router.push("/login")
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
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
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg flex items-center justify-center">
                <Store className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">매장 관리자 대시보드</h1>
                <p className="text-sm text-slate-400">
                  {authState.username === "admin" ? "업종별 관리자" : "매장 관리자"} - 강남점 운영 관리
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Badge variant="secondary" className="bg-blue-500/20 text-blue-300 border-blue-500/30">
                {authState.username === "admin" ? "업종별 관리자" : "매장 관리자"}
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
                  <p className="text-sm font-medium text-slate-400">오늘 매출</p>
                  <p className="text-2xl font-bold text-white">₩2,450,000</p>
                </div>
                <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
                  <DollarSign className="h-6 w-6 text-green-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800 border-slate-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-400">오늘 주문</p>
                  <p className="text-2xl font-bold text-white">132</p>
                </div>
                <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
                  <ShoppingCart className="h-6 w-6 text-blue-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800 border-slate-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-400">출근 직원</p>
                  <p className="text-2xl font-bold text-white">8/12</p>
                </div>
                <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center">
                  <Users className="h-6 w-6 text-purple-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800 border-slate-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-400">고객 평점</p>
                  <p className="text-2xl font-bold text-white">4.8</p>
                </div>
                <div className="w-12 h-12 bg-yellow-500/20 rounded-lg flex items-center justify-center">
                  <Star className="h-6 w-6 text-yellow-400" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 매장 현황 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-blue-400" />
                실시간 주문 현황
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { order: "#1234", items: "치킨버거 2개, 콜라 2개", time: "5분 전", status: "preparing" },
                  { order: "#1233", items: "피자 1개, 감자튀김 1개", time: "8분 전", status: "ready" },
                  { order: "#1232", items: "샐러드 1개, 주스 1개", time: "12분 전", status: "completed" },
                  { order: "#1231", items: "스테이크 1개, 와인 1개", time: "15분 전", status: "completed" }
                ].map((order, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-slate-600 rounded-full flex items-center justify-center">
                        <ShoppingCart className="h-4 w-4 text-slate-300" />
                      </div>
                      <div>
                        <p className="font-medium text-white">{order.order}</p>
                        <p className="text-sm text-slate-400">{order.items}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge 
                        variant={
                          order.status === "preparing" ? "secondary" :
                          order.status === "ready" ? "default" :
                          "outline"
                        }
                        className={
                          order.status === "preparing" ? "bg-yellow-500/20 text-yellow-300 border-yellow-500/30" :
                          order.status === "ready" ? "bg-green-500/20 text-green-300 border-green-500/30" :
                          "bg-slate-500/20 text-slate-300 border-slate-500/30"
                        }
                      >
                        {order.status === "preparing" ? "조리중" :
                         order.status === "ready" ? "완료" : "배달완료"}
                      </Badge>
                      <p className="text-xs text-slate-400 mt-1">{order.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800 border-slate-700">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5 text-green-400" />
                직원 근무 현황
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { name: "김철수", role: "주방장", status: "on", time: "08:00-18:00" },
                  { name: "이영희", role: "서버", status: "on", time: "09:00-17:00" },
                  { name: "박민수", role: "주방보조", status: "break", time: "10:00-19:00" },
                  { name: "정수진", role: "캐셔", status: "off", time: "오늘 휴무" }
                ].map((employee, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-slate-600 rounded-full flex items-center justify-center">
                        <ChefHat className="h-4 w-4 text-slate-300" />
                      </div>
                      <div>
                        <p className="font-medium text-white">{employee.name}</p>
                        <p className="text-sm text-slate-400">{employee.role}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge 
                        variant={
                          employee.status === "on" ? "default" :
                          employee.status === "break" ? "secondary" :
                          "outline"
                        }
                        className={
                          employee.status === "on" ? "bg-green-500/20 text-green-300 border-green-500/30" :
                          employee.status === "break" ? "bg-yellow-500/20 text-yellow-300 border-yellow-500/30" :
                          "bg-slate-500/20 text-slate-300 border-slate-500/30"
                        }
                      >
                        {employee.status === "on" ? "근무중" :
                         employee.status === "break" ? "휴식중" : "휴무"}
                      </Badge>
                      <p className="text-xs text-slate-400 mt-1">{employee.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 매장 정보 */}
        <div className="mt-8">
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MapPin className="h-5 w-5 text-red-400" />
                매장 정보
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="space-y-3">
                  <h4 className="font-semibold text-white">기본 정보</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-slate-400">매장명:</span>
                      <span className="text-white">강남점</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">주소:</span>
                      <span className="text-white">서울 강남구 테헤란로 123</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">전화:</span>
                      <span className="text-white">02-1234-5678</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">영업시간:</span>
                      <span className="text-white">10:00-22:00</span>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-3">
                  <h4 className="font-semibold text-white">오늘 현황</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-slate-400">평균 대기시간:</span>
                      <span className="text-white">15분</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">테이블 점유율:</span>
                      <span className="text-white">75%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">재고 상태:</span>
                      <span className="text-green-400">양호</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">시스템 상태:</span>
                      <span className="text-green-400">정상</span>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-3">
                  <h4 className="font-semibold text-white">알림</h4>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm">
                      <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                      <span className="text-yellow-300">치킨 가슴살 재고 부족</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                      <span className="text-blue-300">신규 직원 등록 완료</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                      <span className="text-green-300">오늘 매출 목표 달성</span>
                    </div>
                  </div>
                </div>
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
                  <ShoppingCart className="h-6 w-6" />
                  <span>주문 관리</span>
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
"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { 
  ChefHat, 
  Clock, 
  Calendar,
  LogOut,
  BarChart3,
  Users,
  DollarSign,
  ShoppingCart,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Timer,
  MapPin,
  Star
} from "lucide-react"

interface AuthState {
  isAuthenticated: boolean
  username: string
  selectedRole: string | null
}

export default function EmployeeDashboard() {
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
      
      // admin 또는 employee 계정만 접근 가능
      const allowedUsers = ["admin", "employee"]
      if (!allowedUsers.includes(parsedAuth.username)) {
        router.push("/login")
        return
      }
      
      // admin이지만 다른 역할을 선택한 경우 해당 역할의 대시보드로 리다이렉트
      if (parsedAuth.username === "admin" && parsedAuth.selectedRole && parsedAuth.selectedRole !== "employee") {
        const roleRoutes = {
          "brand-admin": "/brand-dashboard",
          "store-manager": "/manager-dashboard"
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
          <div className="w-8 h-8 border-4 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
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
              <div className="w-10 h-10 bg-gradient-to-r from-green-600 to-green-700 rounded-lg flex items-center justify-center">
                <ChefHat className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">직원 대시보드</h1>
                <p className="text-sm text-slate-400">
                  {authState.username === "admin" ? "최고 관리자" : "직원"} - 개인 업무 관리
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Badge variant="secondary" className="bg-green-500/20 text-green-300 border-green-500/30">
                {authState.username === "admin" ? "최고 관리자" : "직원"}
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
                  <p className="text-sm font-medium text-slate-400">오늘 근무시간</p>
                  <p className="text-2xl font-bold text-white">8시간</p>
                </div>
                <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
                  <Clock className="h-6 w-6 text-blue-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800 border-slate-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-400">처리한 주문</p>
                  <p className="text-2xl font-bold text-white">45</p>
                </div>
                <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
                  <ShoppingCart className="h-6 w-6 text-green-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800 border-slate-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-400">평균 평점</p>
                  <p className="text-2xl font-bold text-white">4.9</p>
                </div>
                <div className="w-12 h-12 bg-yellow-500/20 rounded-lg flex items-center justify-center">
                  <Star className="h-6 w-6 text-yellow-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800 border-slate-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-400">이번 달 급여</p>
                  <p className="text-2xl font-bold text-white">₩2,800,000</p>
                </div>
                <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center">
                  <DollarSign className="h-6 w-6 text-purple-400" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 개인 현황 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5 text-blue-400" />
                오늘 스케줄
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { time: "09:00-12:00", task: "오전 근무", status: "completed" },
                  { time: "12:00-13:00", task: "점심 휴식", status: "completed" },
                  { time: "13:00-18:00", task: "오후 근무", status: "current" },
                  { time: "18:00-19:00", task: "저녁 휴식", status: "upcoming" },
                  { time: "19:00-22:00", task: "야간 근무", status: "upcoming" }
                ].map((schedule, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-slate-600 rounded-full flex items-center justify-center">
                        <Timer className="h-4 w-4 text-slate-300" />
                      </div>
                      <div>
                        <p className="font-medium text-white">{schedule.time}</p>
                        <p className="text-sm text-slate-400">{schedule.task}</p>
                      </div>
                    </div>
                    <Badge 
                      variant={
                        schedule.status === "completed" ? "outline" :
                        schedule.status === "current" ? "default" :
                        "secondary"
                      }
                      className={
                        schedule.status === "completed" ? "bg-green-500/20 text-green-300 border-green-500/30" :
                        schedule.status === "current" ? "bg-blue-500/20 text-blue-300 border-blue-500/30" :
                        "bg-slate-500/20 text-slate-300 border-slate-500/30"
                      }
                    >
                      {schedule.status === "completed" ? "완료" :
                       schedule.status === "current" ? "진행중" : "예정"}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800 border-slate-700">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-green-400" />
                업무 성과
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { metric: "주문 처리 속도", value: "8.5분", target: "10분", status: "excellent" },
                  { metric: "고객 만족도", value: "4.9/5.0", target: "4.5/5.0", status: "excellent" },
                  { metric: "출근률", value: "95%", target: "90%", status: "good" },
                  { metric: "팀워크 평가", value: "A+", target: "A", status: "excellent" }
                ].map((performance, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
                    <div>
                      <p className="font-medium text-white">{performance.metric}</p>
                      <p className="text-sm text-slate-400">목표: {performance.target}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-white">{performance.value}</p>
                      <Badge 
                        variant="outline"
                        className={
                          performance.status === "excellent" ? "bg-green-500/20 text-green-300 border-green-500/30" :
                          "bg-blue-500/20 text-blue-300 border-blue-500/30"
                        }
                      >
                        {performance.status === "excellent" ? "우수" : "양호"}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 개인 정보 */}
        <div className="mt-8">
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5 text-purple-400" />
                개인 정보
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="space-y-3">
                  <h4 className="font-semibold text-white">기본 정보</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-slate-400">이름:</span>
                      <span className="text-white">김철수</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">직책:</span>
                      <span className="text-white">주방장</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">사번:</span>
                      <span className="text-white">EMP-001</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">입사일:</span>
                      <span className="text-white">2023-03-15</span>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-3">
                  <h4 className="font-semibold text-white">근무 정보</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-slate-400">근무 매장:</span>
                      <span className="text-white">강남점</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">근무 형태:</span>
                      <span className="text-white">정규직</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">시급:</span>
                      <span className="text-white">₩12,000</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">월 근무시간:</span>
                      <span className="text-white">160시간</span>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-3">
                  <h4 className="font-semibold text-white">알림</h4>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm">
                      <CheckCircle className="h-4 w-4 text-green-400" />
                      <span className="text-green-300">오늘 근무 완료</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                      <span className="text-blue-300">내일 휴무일</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                      <span className="text-yellow-300">급여 지급 예정</span>
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
                  <Clock className="h-6 w-6" />
                  <span>출퇴근 기록</span>
                </Button>
                <Button className="h-auto p-4 flex flex-col items-center gap-2 bg-green-600 hover:bg-green-700">
                  <Calendar className="h-6 w-6" />
                  <span>스케줄 확인</span>
                </Button>
                <Button className="h-auto p-4 flex flex-col items-center gap-2 bg-purple-600 hover:bg-purple-700">
                  <BarChart3 className="h-6 w-6" />
                  <span>성과 확인</span>
                </Button>
                <Button className="h-auto p-4 flex flex-col items-center gap-2 bg-yellow-600 hover:bg-yellow-700">
                  <Users className="h-6 w-6" />
                  <span>팀원 연락처</span>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
} 
"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { 
  Building2, 
  Store, 
  Users, 
  TrendingUp, 
  Calendar, 
  BarChart3,
  Settings,
  LogOut,
  Eye,
  DollarSign,
  ShoppingCart,
  ChefHat
} from "lucide-react"

interface AuthState {
  isAuthenticated: boolean
  username: string
  selectedRole: string | null
}

export default function BrandDashboard() {
  const router = useRouter()
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    username: "",
    selectedRole: null
  })

  useEffect(() => {
    // URL 파라미터에서 JWT 토큰 확인
    const urlParams = new URLSearchParams(window.location.search)
    const token = urlParams.get('token')
    
    if (token) {
      // JWT 토큰이 있으면 localStorage에 저장
      localStorage.setItem('jwt_token', token)
      console.log("JWT 토큰을 URL에서 받아서 저장:", token)
    }

    // localStorage에서 인증 상태 확인
    const storedAuth = localStorage.getItem("authState")
    if (storedAuth) {
      try {
        const parsedAuth = JSON.parse(storedAuth)
        console.log("저장된 인증 상태:", parsedAuth)
        
        // brand_admin 또는 admin 역할만 접근 가능
        const allowedRoles = ["brand_admin", "admin"]
        if (!allowedRoles.includes(parsedAuth.selectedRole)) {
          router.push("/login")
          return
        }
        
        // admin이지만 다른 역할을 선택한 경우 해당 역할의 대시보드로 리다이렉트
        if (parsedAuth.selectedRole === "admin") {
          router.push("/admin-dashboard")
          return
        }
        
        setAuthState(parsedAuth)
      } catch (error) {
        console.error("인증 상태 파싱 오류:", error)
        router.push("/login")
      }
    } else {
      console.log("저장된 인증 상태 없음")
      router.push("/login")
    }
  }, [router])

  const handleLogout = () => {
    localStorage.removeItem("authState")
    localStorage.removeItem("jwt_token")
    router.push("/login")
  }

  if (!authState.isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-white text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-white mx-auto"></div>
          <p className="mt-4">인증 확인 중...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* 헤더 */}
      <header className="bg-white/10 backdrop-blur-md border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <Building2 className="h-8 w-8 text-purple-400" />
              <div>
                <h1 className="text-xl font-bold text-white">브랜드 관리자 대시보드</h1>
                <p className="text-sm text-slate-400">
                  {authState.username === "admin" ? "업종별 관리자" : "브랜드 관리자"} - 전체 매장 관리
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Badge variant="secondary" className="bg-purple-500/20 text-purple-300 border-purple-500/30">
                {authState.username === "admin" ? "업종별 관리자" : "브랜드 관리자"}
              </Badge>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={handleLogout}
                className="text-white hover:bg-white/10"
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
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">총 매장 수</CardTitle>
              <Store className="h-4 w-4 text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">24</div>
              <p className="text-xs text-slate-400">+2 이번 달</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">총 직원 수</CardTitle>
              <Users className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">156</div>
              <p className="text-xs text-slate-400">+12 이번 달</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">월 매출</CardTitle>
              <DollarSign className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">₩2.4M</div>
              <p className="text-xs text-slate-400">+8.2% 지난 달 대비</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">평균 주문</CardTitle>
              <ShoppingCart className="h-4 w-4 text-orange-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">₩28K</div>
              <p className="text-xs text-slate-400">+5.1% 지난 주 대비</p>
            </CardContent>
          </Card>
        </div>

        {/* 매장 관리 섹션 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 매장 목록 */}
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <Store className="h-5 w-5 mr-2 text-purple-400" />
                매장 목록
              </CardTitle>
              <CardDescription className="text-slate-400">
                전체 매장 현황 및 관리
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { name: "강남점", status: "운영중", sales: "₩450K", employees: 8 },
                  { name: "홍대점", status: "운영중", sales: "₩380K", employees: 6 },
                  { name: "부산점", status: "운영중", sales: "₩520K", employees: 10 },
                  { name: "대구점", status: "준비중", sales: "₩0", employees: 0 }
                ].map((store, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                    <div>
                      <h4 className="font-medium text-white">{store.name}</h4>
                      <p className="text-sm text-slate-400">{store.employees}명</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-white">{store.sales}</p>
                      <Badge 
                        variant={store.status === "운영중" ? "default" : "secondary"}
                        className={store.status === "운영중" ? "bg-green-500/20 text-green-300" : "bg-yellow-500/20 text-yellow-300"}
                      >
                        {store.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* 브랜드 통계 */}
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <BarChart3 className="h-5 w-5 mr-2 text-blue-400" />
                브랜드 통계
              </CardTitle>
              <CardDescription className="text-slate-400">
                전체 브랜드 성과 지표
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-slate-300">매출 달성률</span>
                    <span className="text-sm text-white">85%</span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div className="bg-purple-500 h-2 rounded-full" style={{ width: '85%' }}></div>
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-slate-300">고객 만족도</span>
                    <span className="text-sm text-white">4.8/5.0</span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div className="bg-green-500 h-2 rounded-full" style={{ width: '96%' }}></div>
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-slate-300">직원 만족도</span>
                    <span className="text-sm text-white">4.2/5.0</span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div className="bg-blue-500 h-2 rounded-full" style={{ width: '84%' }}></div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 빠른 액션 */}
        <div className="mt-8">
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader>
              <CardTitle className="text-white">빠른 액션</CardTitle>
              <CardDescription className="text-slate-400">
                자주 사용하는 기능들
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Button variant="outline" className="h-20 flex flex-col items-center justify-center bg-white/5 border-white/20 text-white hover:bg-white/10">
                  <Store className="h-6 w-6 mb-2 text-purple-400" />
                  <span className="text-sm">매장 추가</span>
                </Button>
                <Button variant="outline" className="h-20 flex flex-col items-center justify-center bg-white/5 border-white/20 text-white hover:bg-white/10">
                  <Users className="h-6 w-6 mb-2 text-blue-400" />
                  <span className="text-sm">직원 관리</span>
                </Button>
                <Button variant="outline" className="h-20 flex flex-col items-center justify-center bg-white/5 border-white/20 text-white hover:bg-white/10">
                  <BarChart3 className="h-6 w-6 mb-2 text-green-400" />
                  <span className="text-sm">성과 분석</span>
                </Button>
                <Button variant="outline" className="h-20 flex flex-col items-center justify-center bg-white/5 border-white/20 text-white hover:bg-white/10">
                  <Settings className="h-6 w-6 mb-2 text-orange-400" />
                  <span className="text-sm">설정</span>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
} 
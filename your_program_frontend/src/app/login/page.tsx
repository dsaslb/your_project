"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { 
  User, 
  Lock, 
  Eye, 
  EyeOff, 
  Building2, 
  Store, 
  ChefHat,
  AlertTriangle,
  CheckCircle,
  LogOut,
  Sparkles,
  Shield,
  Zap,
  TrendingUp
} from "lucide-react"

interface UserRole {
  id: string
  name: string
  description: string
  icon: React.ReactNode
  color: string
  route: string
}

interface AuthState {
  isAuthenticated: boolean
  username: string
  selectedRole: string | null
}

// 사용자별 기본 역할 매핑
const userRoleMapping: { [key: string]: string } = {
  "admin": "role-selector", // admin은 역할 선택 화면
  "brand": "brand-admin",   // brand는 브랜드 관리자
  "manager": "store-manager", // manager는 매장 관리자
  "employee": "employee"    // employee는 직원
}

export default function LoginPage() {
  const router = useRouter()
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const [showRoleSelector, setShowRoleSelector] = useState(false)
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    username: "",
    selectedRole: null
  })

  const userRoles: UserRole[] = [
    {
      id: "super-admin",
      name: "슈퍼 관리자",
      description: "시스템 전체 관리 및 설정",
      icon: <Shield className="h-6 w-6" />,
      color: "from-pink-600 to-pink-700",
      route: "/super-admin"
    },
    {
      id: "brand-admin",
      name: "브랜드 관리자",
      description: "전체 매장 관리 및 통계",
      icon: <Building2 className="h-6 w-6" />,
      color: "from-purple-600 to-purple-700",
      route: "/brand-dashboard"
    },
    {
      id: "store-manager",
      name: "매장 관리자",
      description: "개별 매장 운영 관리",
      icon: <Store className="h-6 w-6" />,
      color: "from-blue-600 to-blue-700",
      route: "/manager-dashboard"
    },
    {
      id: "employee",
      name: "직원",
      description: "개인 업무 및 스케줄",
      icon: <ChefHat className="h-6 w-6" />,
      color: "from-green-600 to-green-700",
      route: "/employee-dashboard"
    }
  ]

  // 페이지 로드 시 인증 상태 확인
  useEffect(() => {
    // 페이지 로드 시 항상 localStorage 클리어 (개발용)
    localStorage.removeItem("authState")
    console.log("localStorage 클리어됨")
    
    setAuthState({
      isAuthenticated: false,
      username: "",
      selectedRole: null
    })
    setShowRoleSelector(false)
  }, [])

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setIsLoading(true)

    console.log("로그인 시도:", username)

    // 허용된 계정들 확인
    const allowedAccounts = {
      "admin": "admin123",
      "brand": "brand123", 
      "manager": "manager123",
      "employee": "employee123"
    }

    if (username in allowedAccounts && password === allowedAccounts[username as keyof typeof allowedAccounts]) {
      console.log("로그인 성공:", username)
      
      if (username === "admin") {
        // admin인 경우 역할 선택 화면 표시
        console.log("admin 계정 - 역할 선택 화면 표시")
        setAuthState({
          isAuthenticated: true,
          username: username,
          selectedRole: null
        })
        setShowRoleSelector(true)
        setIsLoading(false)
      } else {
        // 다른 계정들은 자동으로 해당 역할의 대시보드로 이동
        const roleId = userRoleMapping[username]
        console.log("다른 계정 - 역할 ID:", roleId)
        const role = userRoles.find(r => r.id === roleId)
        if (role) {
          const authState: AuthState = {
            isAuthenticated: true,
            username: username,
            selectedRole: roleId
          }
          setAuthState(authState)
          localStorage.setItem("authState", JSON.stringify(authState))
          console.log("대시보드로 이동:", role.route)
          router.push(role.route)
        }
      }
    } else {
      console.log("로그인 실패")
      setError("아이디 또는 비밀번호가 올바르지 않습니다.")
      setIsLoading(false)
    }
  }

  const handleRoleSelect = (role: UserRole) => {
    // 선택한 역할을 인증 상태에 저장
    const updatedAuthState: AuthState = {
      ...authState,
      selectedRole: role.id
    }
    setAuthState(updatedAuthState)
    localStorage.setItem("authState", JSON.stringify(updatedAuthState))
    
    // 선택한 역할에 따라 해당 대시보드로 이동
    router.push(role.route)
  }

  const handleBackToLogin = () => {
    setShowRoleSelector(false)
    setError("")
  }

  const handleLogout = () => {
    // 인증 상태 초기화
    setAuthState({
      isAuthenticated: false,
      username: "",
      selectedRole: null
    })
    localStorage.removeItem("authState")
    setShowRoleSelector(false)
    setUsername("")
    setPassword("")
    setError("")
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-900/20 to-slate-900 flex items-center justify-center p-4 relative overflow-hidden">
      {/* 배경 애니메이션 효과 */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-indigo-500/5 rounded-full blur-3xl animate-pulse delay-500"></div>
      </div>

      <div className="w-full max-w-md relative z-10">
        {!showRoleSelector ? (
          // 로그인 폼
          <Card className="bg-slate-800/60 border-slate-700/50 backdrop-blur-xl shadow-2xl">
            <CardHeader className="space-y-1 text-center pb-8">
              <div className="mx-auto w-16 h-16 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 rounded-full flex items-center justify-center mb-6 shadow-lg">
                <Sparkles className="h-8 w-8 text-white" />
              </div>
              <CardTitle className="text-3xl font-bold bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                Your Program Manager
              </CardTitle>
              <p className="text-slate-400 text-lg">AI 기반 스마트 레스토랑 관리 시스템</p>
              
              {/* 기능 하이라이트 */}
              <div className="flex justify-center gap-4 mt-6">
                <div className="flex items-center gap-2 text-xs text-slate-400">
                  <Shield className="h-3 w-3 text-green-400" />
                  <span>보안</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-slate-400">
                  <Zap className="h-3 w-3 text-yellow-400" />
                  <span>실시간</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-slate-400">
                  <TrendingUp className="h-3 w-3 text-blue-400" />
                  <span>분석</span>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <form onSubmit={handleLogin} className="space-y-6">
                <div className="space-y-3">
                  <Label htmlFor="username" className="text-slate-300 font-medium">아이디</Label>
                  <div className="relative group">
                    <User className="absolute left-4 top-3 h-5 w-5 text-slate-400 group-focus-within:text-indigo-400 transition-colors" />
                    <Input
                      id="username"
                      type="text"
                      placeholder="아이디를 입력하세요"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      className="pl-12 pr-4 h-12 bg-slate-700/50 border-slate-600/50 text-white placeholder:text-slate-400 focus:border-indigo-500 focus:ring-indigo-500/20 transition-all duration-200"
                      required
                    />
                  </div>
                </div>
                
                <div className="space-y-3">
                  <Label htmlFor="password" className="text-slate-300 font-medium">비밀번호</Label>
                  <div className="relative group">
                    <Lock className="absolute left-4 top-3 h-5 w-5 text-slate-400 group-focus-within:text-indigo-400 transition-colors" />
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      placeholder="비밀번호를 입력하세요"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="pl-12 pr-12 h-12 bg-slate-700/50 border-slate-600/50 text-white placeholder:text-slate-400 focus:border-indigo-500 focus:ring-indigo-500/20 transition-all duration-200"
                      required
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent text-slate-400 hover:text-indigo-400"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? (
                        <EyeOff className="h-5 w-5" />
                      ) : (
                        <Eye className="h-5 w-5" />
                      )}
                    </Button>
                  </div>
                </div>

                {error && (
                  <Alert className="border-red-500/50 bg-red-500/10 backdrop-blur-sm">
                    <AlertTriangle className="h-4 w-4 text-red-400" />
                    <AlertDescription className="text-red-400">{error}</AlertDescription>
                  </Alert>
                )}

                <Button 
                  type="submit" 
                  className="w-full h-12 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 hover:from-indigo-700 hover:via-purple-700 hover:to-pink-700 text-white font-semibold rounded-lg transition-all duration-200 transform hover:scale-[1.02] shadow-lg"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      <span>로그인 중...</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2">
                      <Sparkles className="h-4 w-4" />
                      <span>로그인</span>
                    </div>
                  )}
                </Button>
              </form>

              {/* 테스트 계정 정보 */}
              <div className="text-center space-y-3 pt-6 border-t border-slate-700/50">
                <p className="text-sm text-slate-400 font-medium">테스트 계정</p>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="bg-slate-700/30 rounded p-2">
                    <span className="text-indigo-400 font-mono">admin</span> / <span className="text-indigo-400 font-mono">admin123</span>
                    <p className="text-slate-500 mt-1">역할 선택</p>
                  </div>
                  <div className="bg-slate-700/30 rounded p-2">
                    <span className="text-purple-400 font-mono">brand</span> / <span className="text-purple-400 font-mono">brand123</span>
                    <p className="text-slate-500 mt-1">브랜드 관리자</p>
                  </div>
                  <div className="bg-slate-700/30 rounded p-2">
                    <span className="text-blue-400 font-mono">manager</span> / <span className="text-blue-400 font-mono">manager123</span>
                    <p className="text-slate-500 mt-1">매장 관리자</p>
                  </div>
                  <div className="bg-slate-700/30 rounded p-2">
                    <span className="text-green-400 font-mono">employee</span> / <span className="text-green-400 font-mono">employee123</span>
                    <p className="text-slate-500 mt-1">직원</p>
                  </div>
                </div>
                
                {/* 디버깅용 버튼 */}
                <div className="pt-2">
                  <Button 
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      localStorage.clear()
                      window.location.reload()
                    }}
                    className="text-xs text-slate-400 border-slate-600 hover:text-white hover:border-slate-500"
                  >
                    캐시 클리어 & 새로고침
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ) : (
          // 역할 선택 화면
          <Card className="bg-slate-800/60 border-slate-700/50 backdrop-blur-xl shadow-2xl">
            <CardHeader className="space-y-1 text-center">
              <div className="mx-auto w-16 h-16 bg-gradient-to-r from-green-600 to-blue-600 rounded-full flex items-center justify-center mb-6 shadow-lg">
                <CheckCircle className="h-8 w-8 text-white" />
              </div>
              <CardTitle className="text-2xl font-bold text-white">역할을 선택하세요</CardTitle>
              <p className="text-slate-400">접속할 대시보드를 선택해주세요</p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                {userRoles.map((role) => (
                  <Button
                    key={role.id}
                    variant="outline"
                    className={`w-full h-auto p-4 border-slate-600/50 bg-slate-700/30 hover:bg-slate-700/50 transition-all duration-200 group`}
                    onClick={() => handleRoleSelect(role)}
                  >
                    <div className="flex items-center gap-3 w-full">
                      <div className={`p-3 rounded-lg bg-gradient-to-r ${role.color} shadow-lg group-hover:scale-110 transition-transform duration-200`}>
                        {role.icon}
                      </div>
                      <div className="flex-1 text-left">
                        <div className="font-semibold text-white group-hover:text-indigo-300 transition-colors">{role.name}</div>
                        <div className="text-sm text-slate-400">{role.description}</div>
                      </div>
                    </div>
                  </Button>
                ))}
              </div>

              <div className="flex gap-2 pt-4">
                <Button 
                  variant="ghost" 
                  className="flex-1 text-slate-400 hover:text-white"
                  onClick={handleBackToLogin}
                >
                  다른 계정으로 로그인
                </Button>
                <Button 
                  variant="ghost" 
                  className="text-red-400 hover:text-red-300"
                  onClick={handleLogout}
                >
                  <LogOut className="h-4 w-4 mr-2" />
                  로그아웃
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
} 
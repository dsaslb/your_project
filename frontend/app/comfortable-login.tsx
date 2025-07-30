"use client"
import { useState } from "react"
import { useRouter } from "next/navigation"
import { ChefHat } from "lucide-react"
import { useAuth } from "@/hooks/useAuth"
import { useAuthStore } from "@/store/auth-store"

export default function ComfortableLoginPage() {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const router = useRouter()
  
  // 새로운 API 훅과 인증 스토어 사용
  const { login, isLoading } = useAuth()
  const { setUser } = useAuthStore()

  const handleSubmit = async (e: any) => {
    e.preventDefault()
    setError("")
    
    if (!username || !password) {
      setError("아이디와 비밀번호를 입력해주세요")
      return
    }

    try {
      const result = await login({ username, password })
      
      if (result.success) {
        // 인증 스토어에 사용자 정보 저장
        setUser(result.data.user)
        
        // 권한에 따라 리다이렉트
        if (result.data.user.role === 'admin' || result.data.user.role === 'super_admin') {
          router.push("/dashboard")
        } else if (result.data.user.role === 'brand_manager') {
          router.push("/brand-dashboard")
        } else if (result.data.user.role === 'store_manager') {
          router.push("/store-dashboard")
        } else {
          router.push("/dashboard")
        }
      } else {
        setError(result.error || "로그인에 실패했습니다.")
      }
    } catch (error: any) {
      console.error('Login error:', error)
      setError("서버 연결에 실패했습니다. 다시 시도해주세요.")
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* 헤더 */}
          <div className="text-center mb-8">
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center">
                <ChefHat className="h-8 w-8 text-blue-600" />
              </div>
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              your_program Manager
            </h1>
            <p className="text-gray-600">로그인하여 시작하세요</p>
          </div>

          {/* 폼 */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                아이디
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="아이디를 입력하세요"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                disabled={isLoading}
                required
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                비밀번호
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="비밀번호를 입력하세요"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                disabled={isLoading}
                required
              />
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold py-3 px-4 rounded-lg transition-colors duration-200"
            >
              {isLoading ? "로그인 중..." : "로그인"}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
} 

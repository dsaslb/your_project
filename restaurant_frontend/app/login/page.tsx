"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useUser } from "@/components/UserContext"

export default function LoginPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const router = useRouter()
  const { setUser } = useUser()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError("")

    try {
      if (email === "admin" && password === "admin123!") {
        const userData = {
          id: '1',
          name: '김매니저',
          role: 'manager',
          storeId: 'store_001',
          storeName: '강남점',
          permissions: {
            dashboard: true,
            schedule: true,
            orders: true,
            inventory: true,
            reports: true,
            settings: false,
          },
        }
        
        setUser(userData)
        localStorage.setItem('isAuthenticated', 'true')
        localStorage.setItem('userData', JSON.stringify(userData))
        router.push('/dashboard')
      } else {
        setError("아이디 또는 비밀번호가 올바르지 않습니다.")
      }
    } catch (err) {
      setError("로그인 중 오류가 발생했습니다.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-primary rounded-2xl flex items-center justify-center mx-auto mb-4">
            <span className="text-primary-foreground font-bold text-2xl">R</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            레스토랑 관리 시스템
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            매장 관리자 로그인
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
          <form onSubmit={handleLogin} className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                아이디
              </label>
              <input
                id="email"
                type="text"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                placeholder="아이디를 입력하세요"
                required
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                비밀번호
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                placeholder="비밀번호를 입력하세요"
                required
              />
            </div>

            {error && (
              <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 bg-primary hover:bg-primary/90 text-primary-foreground font-medium rounded-lg transition-colors disabled:opacity-50"
            >
              {isLoading ? "로그인 중..." : "로그인"}
            </button>
          </form>

          <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
            <h3 className="text-sm font-medium text-blue-800 dark:text-blue-200 mb-2">
              데모 계정
            </h3>
            <p className="text-xs text-blue-600 dark:text-blue-300">
              아이디: admin<br />
              비밀번호: admin123!
            </p>
          </div>
        </div>
      </div>
    </div>
  )
} 
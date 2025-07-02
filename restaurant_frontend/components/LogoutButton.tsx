"use client"

import { useRouter } from "next/navigation"
import { useUser } from "./UserContext"
import { LogOut } from "lucide-react"

export function LogoutButton() {
  const router = useRouter()
  const { setUser } = useUser()

  const handleLogout = () => {
    // 로그인 상태 초기화
    setUser({
      id: '',
      name: '',
      role: 'employee',
      permissions: {
        dashboard: false,
        schedule: false,
        orders: false,
        inventory: false,
        reports: false,
        settings: false,
      },
    })

    // localStorage 클리어
    localStorage.removeItem('isAuthenticated')
    localStorage.removeItem('userData')

    // 로그인 페이지로 리디렉션
    router.push('/login')
  }

  return (
    <button
      onClick={handleLogout}
      className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100 transition-colors"
    >
      <LogOut className="h-4 w-4" />
      로그아웃
    </button>
  )
} 
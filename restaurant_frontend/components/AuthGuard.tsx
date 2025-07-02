"use client"

import { useEffect, useState } from "react"
import { useRouter, usePathname } from "next/navigation"
import { useUser } from "./UserContext"

interface AuthGuardProps {
  children: React.ReactNode
}

export function AuthGuard({ children }: AuthGuardProps) {
  const { user, login } = useUser()
  const router = useRouter()
  const pathname = usePathname()
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // 로그인 페이지는 인증 없이 접근 가능
    if (pathname === '/login') {
      setIsLoading(false)
      return
    }

    // localStorage에서 사용자 정보 확인
    const savedUser = localStorage.getItem('user')

    if (!savedUser) {
      // 기본 사용자 정보 설정 (개발용)
      const defaultUser = {
        id: 1,
        name: "관리자",
        email: "admin@restaurant.com",
        role: "admin" as const,
        permissions: ["manage_staff", "manage_orders", "manage_inventory", "manage_schedule", "view_reports", "manage_notices", "view_orders", "view_schedule", "process_payment", "manage_menu"],
        storeName: "맛있는집 본점"
      }
      login(defaultUser)
      setIsLoading(false)
      return
    }

    try {
      const userData = JSON.parse(savedUser)
      if (!user) {
        login(userData)
      }
    } catch (error) {
      console.error('Failed to parse user data:', error)
      localStorage.removeItem('user')
      router.push('/login')
      return
    }

    setIsLoading(false)
  }, [router, pathname, user, login])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">로딩 중...</p>
        </div>
      </div>
    )
  }

  return <>{children}</>
} 
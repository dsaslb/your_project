"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { ThemeToggle } from "@/components/theme-toggle"
import { useUser } from "@/components/UserContext"
import { useNotifications } from "@/components/NotificationSystem"
import { NotificationButton } from "@/components/NotificationSystem"
import { LogOut, Menu, X, Crown, Building2, User } from "lucide-react"
import Link from "next/link"
import { usePathname } from "next/navigation"

interface DashboardLayoutProps {
  children: React.ReactNode
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const { user, logout } = useUser()
  const pathname = usePathname()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  if (!user) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-2"></div>
          <p className="text-sm text-muted-foreground">로딩 중...</p>
        </div>
      </div>
    )
  }

  const getRoleIcon = () => {
    switch (user.role) {
      case 'admin':
        return <Crown className="h-4 w-4 text-yellow-500" />
      case 'manager':
        return <Building2 className="h-4 w-4 text-blue-500" />
      default:
        return <User className="h-4 w-4 text-gray-500" />
    }
  }

  const getRoleText = () => {
    switch (user.role) {
      case 'admin':
        return '최고관리자'
      case 'manager':
        return '매장관리자'
      default:
        return '직원'
    }
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Top Navigation Bar */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="w-full px-4 h-16 flex items-center justify-between">
          {/* Left side - Logo and Mobile Menu */}
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            >
              {isMobileMenuOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
            </Button>
            
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <span className="text-primary-foreground font-bold text-sm">R</span>
              </div>
              <div className="hidden sm:block">
                <h1 className="text-lg font-semibold">레스토랑 관리</h1>
                <p className="text-xs text-muted-foreground">대시보드</p>
              </div>
            </div>
          </div>

          {/* Center - Quick Navigation (Desktop) */}
          <nav className="hidden md:flex items-center gap-2">
            <Link href="/dashboard">
              <Button variant={pathname === "/dashboard" ? "default" : "ghost"} size="sm">
                대시보드
              </Button>
            </Link>
            <Link href="/staff">
              <Button variant={pathname === "/staff" ? "default" : "ghost"} size="sm">
                직원관리
              </Button>
            </Link>
            <Link href="/inventory">
              <Button variant={pathname === "/inventory" ? "default" : "ghost"} size="sm">
                재고관리
              </Button>
            </Link>
            <Link href="/schedule">
              <Button variant={pathname === "/schedule" ? "default" : "ghost"} size="sm">
                스케줄
              </Button>
            </Link>
            <Link href="/reports">
              <Button variant={pathname === "/reports" ? "default" : "ghost"} size="sm">
                보고서
              </Button>
            </Link>
          </nav>

          {/* Right side - User info and actions */}
          <div className="flex items-center gap-2">
            <NotificationButton />
            <ThemeToggle variant="button" size="sm" />
            
            <div className="hidden sm:flex items-center gap-2 px-3 py-1 rounded-md bg-muted/50">
              <div className="flex items-center gap-1">
                {getRoleIcon()}
                <span className="text-sm font-medium">{user.name}</span>
                <span className="text-xs text-muted-foreground">({getRoleText()})</span>
              </div>
            </div>
            
            <Button 
              variant="ghost" 
              size="icon" 
              onClick={logout}
              title="로그아웃"
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </header>

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden border-b bg-background">
          <nav className="w-full px-4 py-2">
            <div className="flex flex-col gap-1">
              <Link href="/dashboard">
                <Button variant={pathname === "/dashboard" ? "default" : "ghost"} className="w-full justify-start">
                  대시보드
                </Button>
              </Link>
              <Link href="/staff">
                <Button variant={pathname === "/staff" ? "default" : "ghost"} className="w-full justify-start">
                  직원관리
                </Button>
              </Link>
              <Link href="/inventory">
                <Button variant={pathname === "/inventory" ? "default" : "ghost"} className="w-full justify-start">
                  재고관리
                </Button>
              </Link>
              <Link href="/schedule">
                <Button variant={pathname === "/schedule" ? "default" : "ghost"} className="w-full justify-start">
                  스케줄
                </Button>
              </Link>
              <Link href="/reports">
                <Button variant={pathname === "/reports" ? "default" : "ghost"} className="w-full justify-start">
                  보고서
                </Button>
              </Link>
            </div>
          </nav>
        </div>
      )}

      {/* Main Content */}
      <main className="flex-1">
        {children}
      </main>
    </div>
  )
} 
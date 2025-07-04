"use client"

import { Bell, Search, Sun, Moon, Menu, Settings, User, LogOut, Crown, Building2 } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ThemeToggle } from "@/components/theme-toggle"
import { useTheme } from "next-themes"
import { NotificationButton } from "./NotificationSystem"
import { useUser } from "./UserContext"
import { usePathname } from "next/navigation"
import Link from "next/link"

interface DashboardHeaderFullProps {
  onToggleNav: () => void
}

export function DashboardHeader({ onToggleNav }: DashboardHeaderFullProps) {
  const { user } = useUser()
  const pathname = usePathname()

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="w-full px-4 h-16 flex items-center justify-between">
        {/* Left side - Logo and Mobile Menu */}
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={onToggleNav}
          >
            <Menu className="h-4 w-4" />
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
              {user?.role === 'admin' && <Crown className="h-4 w-4 text-yellow-500" />}
              {user?.role === 'manager' && <Building2 className="h-4 w-4 text-blue-500" />}
              <span className="text-sm font-medium">{user?.name}</span>
              <span className="text-xs text-muted-foreground">
                ({user?.role === 'admin' ? '최고관리자' : user?.role === 'manager' ? '매장관리자' : '직원'})
              </span>
            </div>
          </div>
          
          <Button 
            variant="ghost" 
            size="icon" 
            onClick={() => {/* logout logic */}}
            title="로그아웃"
          >
            <LogOut className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </header>
  )
} 
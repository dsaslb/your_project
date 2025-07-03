"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { ThemeToggle } from "@/components/theme-toggle"
import { useUser } from "@/components/UserContext"
import { usePathname } from "next/navigation"
import Link from "next/link"
import {
  ChevronLeft,
  ChevronRight,
  Search,
  User,
  LogOut,
  Crown,
  Building2,
  Home,
  Users,
  ShoppingCart,
  Package,
  Calendar,
  Bell,
  BarChart3,
  Settings
} from "lucide-react"

const menuItems = [
  { icon: Home, label: "대시보드", href: "/dashboard", description: "전체 현황 및 통계", roles: ["admin", "manager", "employee"] },
  { icon: Users, label: "직원 관리", href: "/staff", description: "직원 정보 및 권한 관리", roles: ["admin", "manager"] },
  { icon: ShoppingCart, label: "발주 관리", href: "/orders", description: "재료 발주 및 승인", roles: ["admin", "manager"] },
  { icon: Package, label: "재고 관리", href: "/inventory", description: "재고 현황 및 관리", roles: ["admin", "manager", "employee"] },
  { icon: Calendar, label: "스케줄", href: "/schedule", description: "근무 및 청소 스케줄", roles: ["admin", "manager", "employee"] },
  { icon: Bell, label: "알림/공지", href: "/notifications", description: "공지사항 및 알림", roles: ["admin", "manager", "employee"] },
  { icon: BarChart3, label: "보고서", href: "/reports", description: "매출 및 통계 보고서", roles: ["admin", "manager"] },
  { icon: Settings, label: "설정", href: "/settings", description: "시스템 설정", roles: ["admin"] }
]

interface SidebarProps {
  isCollapsed?: boolean
  onToggle?: () => void
  className?: string
}

export function Sidebar({ isCollapsed = false, onToggle, className }: SidebarProps) {
  const { user, logout } = useUser()
  const pathname = usePathname()
  const [searchTerm, setSearchTerm] = React.useState("")

  if (!user) {
    return (
      <aside className={cn(
        "flex h-full flex-col border-r bg-background transition-all duration-300",
        isCollapsed ? "w-16" : "w-80",
        className
      )}>
        <div className="flex h-16 items-center justify-between border-b px-4">
          {!isCollapsed && <h1 className="text-lg font-semibold">레스토랑 관리</h1>}
          <Button 
            variant="ghost" 
            size="icon" 
            onClick={onToggle} 
            className="h-8 w-8 hover:bg-accent"
            title={isCollapsed ? "사이드바 펼치기" : "사이드바 접기"}
          >
            {isCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </Button>
        </div>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-2"></div>
            <p className="text-sm text-muted-foreground">로딩 중...</p>
          </div>
        </div>
      </aside>
    )
  }

  const filteredMenuItems = menuItems.filter(item =>
    item.roles.includes(user.role) &&
    (item.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.description.toLowerCase().includes(searchTerm.toLowerCase()))
  )

  return (
    <aside className={cn(
      "flex h-full flex-col border-r bg-background transition-all duration-300",
      isCollapsed ? "w-16" : "w-80",
      className
    )}>
      {/* Header */}
      <div className="flex h-16 items-center justify-between px-4 border-b">
        {!isCollapsed && (
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <span className="text-primary-foreground font-bold text-sm">R</span>
            </div>
            <div>
              <h2 className="text-lg font-semibold">레스토랑 관리</h2>
              <div className="flex items-center gap-1">
                <p className="text-xs text-muted-foreground">{user.name}</p>
                {user.role === 'admin' && <Crown className="h-3 w-3 text-yellow-500" />}
                {user.role === 'manager' && <Building2 className="h-3 w-3 text-blue-500" />}
              </div>
              {user.storeName && (
                <p className="text-xs text-muted-foreground">{user.storeName}</p>
              )}
            </div>
          </div>
        )}
        <div className="flex items-center gap-2">
          <ThemeToggle variant="button" size="sm" />
          <Button 
            variant="ghost" 
            size="icon" 
            onClick={onToggle} 
            className="h-8 w-8 hover:bg-accent"
            title={isCollapsed ? "사이드바 펼치기" : "사이드바 접기"}
          >
            {isCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </Button>
        </div>
      </div>

      {/* Search Bar */}
      {!isCollapsed && (
        <div className="p-4 border-b">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="메뉴 검색..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 text-sm border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 p-4 overflow-y-auto">
        <ul className="space-y-2">
          {filteredMenuItems.map((item) => {
            const isActive = pathname === item.href
            const Icon = item.icon
            
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground group",
                    isActive && "bg-accent text-accent-foreground",
                    isCollapsed && "justify-center"
                  )}
                  title={isCollapsed ? item.label : undefined}
                >
                  <Icon className={cn("h-4 w-4", isActive && "text-primary")} />
                  {!isCollapsed && (
                    <div className="flex-1 min-w-0">
                      <span className="truncate">{item.label}</span>
                      <p className="text-xs text-muted-foreground truncate">{item.description}</p>
                    </div>
                  )}
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-muted rounded-full flex items-center justify-center">
            <User className="h-4 w-4" />
          </div>
          {!isCollapsed && (
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{user.name}</p>
              <p className="text-xs text-muted-foreground truncate">
                {user.role === 'admin' ? '최고관리자' : 
                 user.role === 'manager' ? '매장관리자' : '직원'}
              </p>
            </div>
          )}
          <Button 
            variant="ghost" 
            size="icon" 
            className="h-8 w-8 hover:bg-accent" 
            onClick={logout}
            title="로그아웃"
          >
            <LogOut className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </aside>
  )
} 
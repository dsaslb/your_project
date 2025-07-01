"use client"

import * as React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { 
  ChevronLeft, 
  ChevronRight, 
  Calendar, 
  Users, 
  Package, 
  Settings, 
  BarChart3,
  ClipboardList,
  Home,
  LogOut,
  Menu,
  X,
  User,
  Bell,
  Search
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { ThemeToggle } from "@/components/theme-toggle"
import { hasPermission, type User, type Permission } from "@/lib/utils"
import { useUser } from "@/components/UserContext"

interface SidebarProps {
  isCollapsed?: boolean
  onToggle?: () => void
  className?: string
  user?: User
  showMobileMenu?: boolean
  onMobileMenuToggle?: () => void
}

// 메뉴 아이템 정의
const menuItems = [
  { 
    icon: Home, 
    label: "대시보드", 
    href: "/dashboard", 
    permissions: ['schedule', 'staff', 'orders', 'inventory', 'reports', 'settings'] as Permission[],
    description: "메인 대시보드"
  },
  { 
    icon: Calendar, 
    label: "스케줄 관리", 
    href: "/schedule", 
    permissions: ['schedule'] as Permission[],
    description: "근무 및 청소 스케줄"
  },
  { 
    icon: Users, 
    label: "직원 관리", 
    href: "/staff", 
    permissions: ['staff'] as Permission[],
    description: "직원 정보 및 관리"
  },
  { 
    icon: Package, 
    label: "발주 관리", 
    href: "/orders", 
    permissions: ['orders'] as Permission[],
    description: "재료 발주 및 관리"
  },
  { 
    icon: ClipboardList, 
    label: "재고 관리", 
    href: "/inventory", 
    permissions: ['inventory'] as Permission[],
    description: "재고 현황 및 관리"
  },
  { 
    icon: BarChart3, 
    label: "통계/리포트", 
    href: "/reports", 
    permissions: ['reports'] as Permission[],
    description: "매출 및 통계 분석"
  },
  { 
    icon: Settings, 
    label: "설정", 
    href: "/settings", 
    permissions: ['settings'] as Permission[],
    description: "시스템 설정"
  },
]

export function Sidebar({ 
  isCollapsed = false, 
  onToggle, 
  className,
  user: userProp,
  showMobileMenu = false,
  onMobileMenuToggle
}: SidebarProps) {
  const { user } = useUser();
  const pathname = usePathname()
  const [searchTerm, setSearchTerm] = React.useState("")

  // 권한별 메뉴 분기
  const filteredMenuItems = menuItems.filter(item => {
    if (user.role === "admin") return true; // 전체 메뉴
    if (user.role === "manager") {
      // 매장관리자: 매장 관리/근무/발주 등
      return ["dashboard","schedule","orders","inventory","reports"].some(key => user.permissions[key]);
    }
    if (user.role === "employee") {
      // 직원: 근무/스케줄/본인 업무만
      return ["dashboard","schedule"].some(key => user.permissions[key]);
    }
    return false;
  })

  // 검색어에 따른 메뉴 필터링
  const searchedMenuItems = filteredMenuItems.filter(item =>
    item.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.description.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const SidebarContent = () => (
    <>
      {/* Header */}
      <div className="flex h-16 items-center justify-between px-4 border-b">
        {!isCollapsed && (
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <span className="text-primary-foreground font-bold text-sm">R</span>
            </div>
            <div>
              <h2 className="text-lg font-semibold">레스토랑 관리</h2>
              <p className="text-xs text-muted-foreground">{user.name}</p>
            </div>
          </div>
        )}
        <div className="flex items-center gap-2">
          <ThemeToggle variant="button" size="sm" />
          <Button
            variant="ghost"
            size="icon"
            onClick={onToggle}
            className="h-8 w-8"
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
          {searchedMenuItems.map((item) => {
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
                  <Icon className={cn(
                    "h-4 w-4",
                    isActive && "text-primary"
                  )} />
                  {!isCollapsed && (
                    <div className="flex-1 min-w-0">
                      <span className="truncate">{item.label}</span>
                      <p className="text-xs text-muted-foreground truncate">
                        {item.description}
                      </p>
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
        {!isCollapsed ? (
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm">
              <User className="h-4 w-4 text-muted-foreground" />
              <span className="text-muted-foreground">{user.name}</span>
            </div>
            <Button variant="ghost" size="sm" className="w-full justify-start">
              <LogOut className="h-4 w-4 mr-2" />
              로그아웃
            </Button>
          </div>
        ) : (
          <div className="flex justify-center">
            <Button variant="ghost" size="icon" className="h-8 w-8">
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        )}
      </div>
    </>
  )

  // 모바일 메뉴
  if (showMobileMenu !== undefined) {
    return (
      <>
        {/* Mobile Menu Overlay */}
        {showMobileMenu && (
          <div 
            className="fixed inset-0 bg-black/50 z-40 lg:hidden"
            onClick={onMobileMenuToggle}
          />
        )}
        
        {/* Mobile Sidebar */}
        <div className={cn(
          "fixed top-0 left-0 h-full bg-background border-r z-50 transition-transform duration-300 lg:hidden",
          showMobileMenu ? "translate-x-0" : "-translate-x-full",
          "w-80"
        )}>
          <SidebarContent />
        </div>
        
        {/* Mobile Menu Toggle */}
        <Button
          variant="ghost"
          size="icon"
          onClick={onMobileMenuToggle}
          className="fixed top-4 left-4 z-50 lg:hidden"
        >
          {showMobileMenu ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </Button>
      </>
    )
  }

  // 데스크탑 사이드바
  return (
    <div className={cn(
      "flex h-full flex-col bg-background border-r transition-all duration-300",
      isCollapsed ? "w-16" : "w-64",
      className
    )}>
      <SidebarContent />
    </div>
  )
} 
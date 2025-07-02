"use client"

import { Bell, Search, Sun, Moon, Menu, Settings, User } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useTheme } from "next-themes"
import { DropdownMenu, DropdownMenuContent, DropdownMenuTrigger, DropdownMenuItem } from "@/components/ui/dropdown-menu"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

interface DashboardHeaderFullProps {
  onToggleNav: () => void
}

export function DashboardHeader({ onToggleNav }: DashboardHeaderFullProps) {
  const { setTheme, theme } = useTheme()

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60 dark:bg-gray-950/95">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          {/* 왼쪽: 브랜드 + 네비게이션 */}
          <div className="flex items-center gap-4">
            {/* 브랜드 로고 */}
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 text-white text-lg font-bold shadow-lg">
                🍽️
              </div>
              <div className="hidden sm:flex flex-col">
                <span className="text-lg font-bold text-gray-900 dark:text-white">맛있는집</span>
                <span className="text-xs text-gray-500 dark:text-gray-400">매장 관리 시스템</span>
              </div>
            </div>
          </div>

          {/* 중앙: 검색 */}
          <div className="hidden md:flex flex-1 max-w-md mx-8">
            <div className="relative w-full">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                type="text"
                placeholder="검색..."
                className="w-full pl-10 pr-4 py-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-amber-500"
              />
            </div>
          </div>

          {/* 오른쪽: 액션 버튼들 */}
          <div className="flex items-center gap-2">
            {/* 테마 토글 */}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setTheme(theme === "light" ? "dark" : "light")}
              className="h-9 w-9"
            >
              <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
              <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
            </Button>

            {/* 알림 */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="relative h-9 w-9">
                  <Bell className="h-4 w-4" />
                  <Badge 
                    variant="destructive" 
                    className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 text-xs"
                  >
                    3
                  </Badge>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-80">
                <div className="p-4">
                  <h3 className="text-sm font-semibold mb-2">알림</h3>
                  <div className="space-y-3">
                    <div className="flex items-start gap-3 p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800">
                      <div className="w-2 h-2 bg-red-500 rounded-full mt-2"></div>
                      <div className="flex-1">
                        <p className="text-sm font-medium">새로운 주문이 들어왔습니다</p>
                        <p className="text-xs text-gray-500">5분 전</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3 p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800">
                      <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2"></div>
                      <div className="flex-1">
                        <p className="text-sm font-medium">재고 부족 알림</p>
                        <p className="text-xs text-gray-500">10분 전</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3 p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800">
                      <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                      <div className="flex-1">
                        <p className="text-sm font-medium">근무표 업데이트 완료</p>
                        <p className="text-xs text-gray-500">1시간 전</p>
                      </div>
                    </div>
                  </div>
                </div>
              </DropdownMenuContent>
            </DropdownMenu>

            {/* 사용자 메뉴 */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-9 w-9 rounded-full">
                  <Avatar className="h-8 w-8">
                    <AvatarImage src="/avatars/01.png" alt="관리자" />
                    <AvatarFallback className="bg-amber-500 text-white">관</AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56" align="end">
                <div className="p-4">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium">매장 관리자</p>
                    <p className="text-xs text-gray-500">admin@restaurant.com</p>
                  </div>
                </div>
                <div className="border-t">
                  <DropdownMenuItem className="flex items-center gap-2 p-3">
                    <User className="h-4 w-4" />
                    <span>프로필</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem className="flex items-center gap-2 p-3">
                    <Settings className="h-4 w-4" />
                    <span>설정</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem className="flex items-center gap-2 p-3 text-red-600">
                    <span>로그아웃</span>
                  </DropdownMenuItem>
                </div>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </div>
    </header>
  )
} 
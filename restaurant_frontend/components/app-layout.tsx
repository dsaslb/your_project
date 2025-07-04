"use client"

import { useState } from "react"
import { Sidebar } from "@/components/sidebar"
import { Button } from "@/components/ui/button"
import { ChevronRight } from "lucide-react"

interface AppLayoutProps {
  children: React.ReactNode
}

export function AppLayout({ children }: AppLayoutProps) {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)

  return (
    <div className="flex min-h-screen bg-background">
      {/* Sidebar - 고정 너비, 최소 너비 보장 */}
      <Sidebar 
        isCollapsed={isSidebarCollapsed}
        onToggle={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        className={isSidebarCollapsed ? "w-16 min-w-[64px]" : "w-64 min-w-[256px]"}
      />
      
      {/* Main Content - 남은 공간 모두 사용, 최대 너비 */}
      <main className="flex-1 w-full min-w-0 max-w-none bg-background">
        {/* 사이드바가 접혀있을 때 펼치기 버튼 */}
        {isSidebarCollapsed && (
          <div className="absolute top-4 left-4 z-10">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsSidebarCollapsed(false)}
              className="bg-background/80 backdrop-blur-sm border shadow-sm hover:bg-background"
              title="사이드바 펼치기"
            >
              <ChevronRight className="h-4 w-4 mr-1" />
              메뉴
            </Button>
          </div>
        )}
        
        {/* 컨텐츠 영역 - 패딩과 스크롤, 전체 너비 사용 */}
        <div className="w-full p-6 overflow-y-auto min-h-screen">
          {children}
        </div>
      </main>
    </div>
  )
} 
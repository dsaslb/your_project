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
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <Sidebar 
        isCollapsed={isSidebarCollapsed}
        onToggle={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
      />
      
      {/* Main Content */}
      <main className="flex-1 overflow-y-auto relative min-h-screen w-full">
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
        
        {children}
      </main>
    </div>
  )
} 
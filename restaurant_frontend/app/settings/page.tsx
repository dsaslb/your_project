"use client"

import { useState } from "react"
import { ResizableLayout } from "@/components/resizable-layout"
import { Sidebar } from "@/components/sidebar"
import { Button } from "@/components/ui/button"
import { Settings, User, Bell, Shield } from "lucide-react"

export default function SettingsPage() {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)

  return (
    <ResizableLayout
      sidebar={
        <Sidebar
          isCollapsed={isSidebarCollapsed}
          onToggle={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        />
      }
      defaultSidebarWidth={20}
      minSidebarWidth={10}
      maxSidebarWidth={35}
    >
      <div className="flex h-full flex-col">
        {/* Header */}
        <header className="flex h-16 items-center justify-between border-b px-6">
          <h1 className="text-2xl font-bold">설정</h1>
          <Button>
            <Settings className="h-4 w-4 mr-2" />
            설정 저장
          </Button>
        </header>

        {/* Main Content */}
        <main className="flex-1 p-6 space-y-6">
          {/* 설정 카테고리 */}
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            <div className="rounded-lg border bg-card p-6">
              <div className="flex items-center gap-3 mb-4">
                <User className="h-6 w-6 text-primary" />
                <h3 className="text-lg font-semibold">계정 설정</h3>
              </div>
              <p className="text-sm text-muted-foreground mb-4">
                개인 정보 및 계정 관련 설정
              </p>
              <Button variant="outline" className="w-full">
                설정 변경
              </Button>
            </div>
            
            <div className="rounded-lg border bg-card p-6">
              <div className="flex items-center gap-3 mb-4">
                <Bell className="h-6 w-6 text-orange-500" />
                <h3 className="text-lg font-semibold">알림 설정</h3>
              </div>
              <p className="text-sm text-muted-foreground mb-4">
                알림 및 메시지 관련 설정
              </p>
              <Button variant="outline" className="w-full">
                설정 변경
              </Button>
            </div>
            
            <div className="rounded-lg border bg-card p-6">
              <div className="flex items-center gap-3 mb-4">
                <Shield className="h-6 w-6 text-green-500" />
                <h3 className="text-lg font-semibold">보안 설정</h3>
              </div>
              <p className="text-sm text-muted-foreground mb-4">
                비밀번호 및 보안 관련 설정
              </p>
              <Button variant="outline" className="w-full">
                설정 변경
              </Button>
            </div>
          </div>

          {/* 시스템 정보 */}
          <div className="rounded-lg border">
            <div className="p-6">
              <h2 className="text-xl font-semibold mb-4">시스템 정보</h2>
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <p className="text-sm text-muted-foreground">버전</p>
                  <p className="font-medium">v1.0.0</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">마지막 업데이트</p>
                  <p className="font-medium">2024-01-15</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">라이선스</p>
                  <p className="font-medium">MIT License</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">지원</p>
                  <p className="font-medium">support@restaurant.com</p>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </ResizableLayout>
  )
} 
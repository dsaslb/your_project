"use client"

import { useState } from "react"
import { ResizableLayout } from "@/components/resizable-layout"
import { Sidebar } from "@/components/sidebar"
import { Button } from "@/components/ui/button"
import { BarChart3, TrendingUp, Users, DollarSign } from "lucide-react"

export default function ReportsPage() {
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
          <h1 className="text-2xl font-bold">통계 및 리포트</h1>
          <Button>
            <BarChart3 className="h-4 w-4 mr-2" />
            리포트 생성
          </Button>
        </header>

        {/* Main Content */}
        <main className="flex-1 p-6 space-y-6">
          {/* 통계 카드들 */}
          <div className="grid gap-6 md:grid-cols-3">
            <div className="rounded-lg border bg-card p-6">
              <div className="flex items-center gap-2">
                <DollarSign className="h-5 w-5 text-primary" />
                <h3 className="text-lg font-semibold">이번 달 매출</h3>
              </div>
              <p className="text-3xl font-bold text-primary mt-2">₩45,200,000</p>
              <p className="text-sm text-muted-foreground mt-2">
                지난 달 대비 +8.5%
              </p>
            </div>
            
            <div className="rounded-lg border bg-card p-6">
              <div className="flex items-center gap-2">
                <Users className="h-5 w-5 text-orange-500" />
                <h3 className="text-lg font-semibold">평균 근무시간</h3>
              </div>
              <p className="text-3xl font-bold text-orange-500 mt-2">8.2시간</p>
              <p className="text-sm text-muted-foreground mt-2">
                이번 주 평균
              </p>
            </div>
            
            <div className="rounded-lg border bg-card p-6">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-green-500" />
                <h3 className="text-lg font-semibold">고객 만족도</h3>
              </div>
              <p className="text-3xl font-bold text-green-500 mt-2">4.8/5.0</p>
              <p className="text-sm text-muted-foreground mt-2">
                지난 주 평균
              </p>
            </div>
          </div>

          {/* 차트 영역 */}
          <div className="grid gap-6 md:grid-cols-2">
            <div className="rounded-lg border p-6">
              <h2 className="text-xl font-semibold mb-4">매출 추이</h2>
              <div className="h-64 flex items-center justify-center bg-muted/50 rounded-lg">
                <p className="text-muted-foreground">차트 영역 (구현 예정)</p>
              </div>
            </div>
            
            <div className="rounded-lg border p-6">
              <h2 className="text-xl font-semibold mb-4">직원별 근무시간</h2>
              <div className="h-64 flex items-center justify-center bg-muted/50 rounded-lg">
                <p className="text-muted-foreground">차트 영역 (구현 예정)</p>
              </div>
            </div>
          </div>
        </main>
      </div>
    </ResizableLayout>
  )
} 
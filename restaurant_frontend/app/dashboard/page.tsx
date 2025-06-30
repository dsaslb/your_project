"use client"

import { useState } from "react"
import { ResizableLayout } from "@/components/resizable-layout"
import { Sidebar } from "@/components/sidebar"

export default function DashboardPage() {
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
          <h1 className="text-2xl font-bold">대시보드</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground">
              매장 관리자님 환영합니다
            </span>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 p-6 space-y-6">
          {/* 통계 카드들 */}
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            <div className="rounded-lg border bg-card p-6">
              <h3 className="text-lg font-semibold">오늘 근무자</h3>
              <p className="text-3xl font-bold text-primary">12명</p>
              <p className="text-sm text-muted-foreground mt-2">
                정상 출근: 10명, 지각: 2명
              </p>
            </div>
            
            <div className="rounded-lg border bg-card p-6">
              <h3 className="text-lg font-semibold">대기 주문</h3>
              <p className="text-3xl font-bold text-orange-500">8건</p>
              <p className="text-sm text-muted-foreground mt-2">
                평균 대기시간: 15분
              </p>
            </div>
            
            <div className="rounded-lg border bg-card p-6">
              <h3 className="text-lg font-semibold">오늘 매출</h3>
              <p className="text-3xl font-bold text-green-500">₩2,450,000</p>
              <p className="text-sm text-muted-foreground mt-2">
                어제 대비 +12.5%
              </p>
            </div>
          </div>

          {/* 최근 활동 테이블 */}
          <div className="rounded-lg border">
            <div className="p-6">
              <h2 className="text-xl font-semibold mb-4">최근 활동</h2>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-2">시간</th>
                      <th className="text-left p-2">활동</th>
                      <th className="text-left p-2">담당자</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b">
                      <td className="p-2">14:30</td>
                      <td className="p-2">신규 주문 접수</td>
                      <td className="p-2">김철수</td>
                    </tr>
                    <tr className="border-b">
                      <td className="p-2">14:25</td>
                      <td className="p-2">재료 발주 완료</td>
                      <td className="p-2">이영희</td>
                    </tr>
                    <tr>
                      <td className="p-2">14:20</td>
                      <td className="p-2">근무 시작</td>
                      <td className="p-2">박민수</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </main>
      </div>
    </ResizableLayout>
  )
} 
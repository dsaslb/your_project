"use client"

import { useState } from "react"
import { ResizableLayout } from "@/components/resizable-layout"
import { Sidebar } from "@/components/sidebar"
import { ResizableCard } from "@/components/resizable-card"
import { ResizableTable } from "@/components/resizable-table"

export default function Home() {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 w-full px-6 py-8">
      <div className="w-full space-y-8">
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
              {/* 통계 카드들 - 리사이즈 가능 */}
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                <ResizableCard className="bg-card">
                  <div className="h-full">
                    <h3 className="text-lg font-semibold mb-2">오늘 근무자</h3>
                    <p className="text-3xl font-bold text-primary">12명</p>
                    <p className="text-sm text-muted-foreground mt-2">
                      정상 출근: 10명, 지각: 2명
                    </p>
                  </div>
                </ResizableCard>
                
                <ResizableCard className="bg-card">
                  <div className="h-full">
                    <h3 className="text-lg font-semibold mb-2">대기 주문</h3>
                    <p className="text-3xl font-bold text-orange-500">8건</p>
                    <p className="text-sm text-muted-foreground mt-2">
                      평균 대기시간: 15분
                    </p>
                  </div>
                </ResizableCard>
                
                <ResizableCard className="bg-card">
                  <div className="h-full">
                    <h3 className="text-lg font-semibold mb-2">오늘 매출</h3>
                    <p className="text-3xl font-bold text-green-500">₩2,450,000</p>
                    <p className="text-sm text-muted-foreground mt-2">
                      어제 대비 +12.5%
                    </p>
                  </div>
                </ResizableCard>
              </div>

              {/* 최근 활동 테이블 - 리사이즈 가능 */}
              <div className="space-y-4">
                <h2 className="text-xl font-semibold">최근 활동</h2>
                <ResizableTable>
                  <table className="w-full">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="text-left p-3 font-medium">시간</th>
                        <th className="text-left p-3 font-medium">활동</th>
                        <th className="text-left p-3 font-medium">담당자</th>
                        <th className="text-left p-3 font-medium">상태</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-b hover:bg-muted/50 transition-colors">
                        <td className="p-3">14:30</td>
                        <td className="p-3">신규 주문 접수</td>
                        <td className="p-3">김철수</td>
                        <td className="p-3">
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                            완료
                          </span>
                        </td>
                      </tr>
                      <tr className="border-b hover:bg-muted/50 transition-colors">
                        <td className="p-3">14:25</td>
                        <td className="p-3">재료 발주 완료</td>
                        <td className="p-3">이영희</td>
                        <td className="p-3">
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                            진행중
                          </span>
                        </td>
                      </tr>
                      <tr className="border-b hover:bg-muted/50 transition-colors">
                        <td className="p-3">14:20</td>
                        <td className="p-3">근무 시작</td>
                        <td className="p-3">박민수</td>
                        <td className="p-3">
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                            완료
                          </span>
                        </td>
                      </tr>
                      <tr className="hover:bg-muted/50 transition-colors">
                        <td className="p-3">14:15</td>
                        <td className="p-3">청소 작업 완료</td>
                        <td className="p-3">최지영</td>
                        <td className="p-3">
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                            완료
                          </span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </ResizableTable>
              </div>

              {/* 추가 정보 섹션 */}
              <div className="grid gap-6 md:grid-cols-2">
                <ResizableCard direction="vertical" className="bg-card">
                  <div className="h-full">
                    <h3 className="text-lg font-semibold mb-4">오늘의 스케줄</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center p-3 bg-muted/50 rounded-lg">
                        <span>오전 근무</span>
                        <span className="text-sm text-muted-foreground">08:00 - 16:00</span>
                      </div>
                      <div className="flex justify-between items-center p-3 bg-muted/50 rounded-lg">
                        <span>오후 근무</span>
                        <span className="text-sm text-muted-foreground">16:00 - 24:00</span>
                      </div>
                      <div className="flex justify-between items-center p-3 bg-muted/50 rounded-lg">
                        <span>청소 시간</span>
                        <span className="text-sm text-muted-foreground">22:00 - 23:00</span>
                      </div>
                    </div>
                  </div>
                </ResizableCard>

                <ResizableCard direction="vertical" className="bg-card">
                  <div className="h-full">
                    <h3 className="text-lg font-semibold mb-4">알림사항</h3>
                    <div className="space-y-3">
                      <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                        <p className="text-sm text-yellow-800 dark:text-yellow-200">
                          재료 발주 마감시간이 1시간 남았습니다.
                        </p>
                      </div>
                      <div className="p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                        <p className="text-sm text-blue-800 dark:text-blue-200">
                          새로운 직원 교육이 예정되어 있습니다.
                        </p>
                      </div>
                    </div>
                  </div>
                </ResizableCard>
              </div>
            </main>
          </div>
        </ResizableLayout>
      </div>
    </div>
  )
}

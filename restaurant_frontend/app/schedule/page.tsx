"use client"

import { useState } from "react"
import { ResizableLayout } from "@/components/resizable-layout"
import { Sidebar } from "@/components/sidebar"
import { Button } from "@/components/ui/button"
import { Calendar, Plus, Users, Clock } from "lucide-react"

export default function SchedulePage() {
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
          <h1 className="text-2xl font-bold">스케줄 관리</h1>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            새 스케줄 추가
          </Button>
        </header>

        {/* Main Content */}
        <main className="flex-1 p-6 space-y-6">
          {/* 통계 카드들 */}
          <div className="grid gap-6 md:grid-cols-3">
            <div className="rounded-lg border bg-card p-6">
              <div className="flex items-center gap-2">
                <Users className="h-5 w-5 text-primary" />
                <h3 className="text-lg font-semibold">오늘 근무자</h3>
              </div>
              <p className="text-3xl font-bold text-primary mt-2">12명</p>
            </div>
            
            <div className="rounded-lg border bg-card p-6">
              <div className="flex items-center gap-2">
                <Clock className="h-5 w-5 text-orange-500" />
                <h3 className="text-lg font-semibold">총 근무시간</h3>
              </div>
              <p className="text-3xl font-bold text-orange-500 mt-2">96시간</p>
            </div>
            
            <div className="rounded-lg border bg-card p-6">
              <div className="flex items-center gap-2">
                <Calendar className="h-5 w-5 text-green-500" />
                <h3 className="text-lg font-semibold">청소 스케줄</h3>
              </div>
              <p className="text-3xl font-bold text-green-500 mt-2">3건</p>
            </div>
          </div>

          {/* 스케줄 테이블 */}
          <div className="rounded-lg border">
            <div className="p-6">
              <h2 className="text-xl font-semibold mb-4">이번 주 스케줄</h2>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-3">날짜</th>
                      <th className="text-left p-3">시간</th>
                      <th className="text-left p-3">직원</th>
                      <th className="text-left p-3">업무</th>
                      <th className="text-left p-3">상태</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b">
                      <td className="p-3">월요일</td>
                      <td className="p-3">08:00 - 16:00</td>
                      <td className="p-3">김철수</td>
                      <td className="p-3">주방</td>
                      <td className="p-3">
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                          완료
                        </span>
                      </td>
                    </tr>
                    <tr className="border-b">
                      <td className="p-3">화요일</td>
                      <td className="p-3">16:00 - 24:00</td>
                      <td className="p-3">이영희</td>
                      <td className="p-3">홀서빙</td>
                      <td className="p-3">
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                          진행중
                        </span>
                      </td>
                    </tr>
                    <tr>
                      <td className="p-3">수요일</td>
                      <td className="p-3">22:00 - 23:00</td>
                      <td className="p-3">박민수</td>
                      <td className="p-3">청소</td>
                      <td className="p-3">
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200">
                          대기
                        </span>
                      </td>
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
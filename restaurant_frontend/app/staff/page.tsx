"use client"

import { useState } from "react"
import { ResizableLayout } from "@/components/resizable-layout"
import { Sidebar } from "@/components/sidebar"
import { Button } from "@/components/ui/button"
import { Plus, Users, Clock, TrendingUp } from "lucide-react"

export default function StaffPage() {
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
          <h1 className="text-2xl font-bold">직원 관리</h1>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            새 직원 추가
          </Button>
        </header>

        {/* Main Content */}
        <main className="flex-1 p-6 space-y-6">
          {/* 통계 카드들 */}
          <div className="grid gap-6 md:grid-cols-3">
            <div className="rounded-lg border bg-card p-6">
              <div className="flex items-center gap-2">
                <Users className="h-5 w-5 text-primary" />
                <h3 className="text-lg font-semibold">전체 직원</h3>
              </div>
              <p className="text-3xl font-bold text-primary mt-2">15명</p>
            </div>
            
            <div className="rounded-lg border bg-card p-6">
              <div className="flex items-center gap-2">
                <Clock className="h-5 w-5 text-orange-500" />
                <h3 className="text-lg font-semibold">평균 근무시간</h3>
              </div>
              <p className="text-3xl font-bold text-orange-500 mt-2">8.5시간</p>
            </div>
            
            <div className="rounded-lg border bg-card p-6">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-green-500" />
                <h3 className="text-lg font-semibold">출근률</h3>
              </div>
              <p className="text-3xl font-bold text-green-500 mt-2">95%</p>
            </div>
          </div>

          {/* 직원 목록 테이블 */}
          <div className="rounded-lg border">
            <div className="p-6">
              <h2 className="text-xl font-semibold mb-4">직원 목록</h2>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-3">이름</th>
                      <th className="text-left p-3">직책</th>
                      <th className="text-left p-3">연락처</th>
                      <th className="text-left p-3">입사일</th>
                      <th className="text-left p-3">상태</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b">
                      <td className="p-3">김철수</td>
                      <td className="p-3">주방장</td>
                      <td className="p-3">010-1234-5678</td>
                      <td className="p-3">2023-01-15</td>
                      <td className="p-3">
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                          재직중
                        </span>
                      </td>
                    </tr>
                    <tr className="border-b">
                      <td className="p-3">이영희</td>
                      <td className="p-3">서버</td>
                      <td className="p-3">010-2345-6789</td>
                      <td className="p-3">2023-03-20</td>
                      <td className="p-3">
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                          재직중
                        </span>
                      </td>
                    </tr>
                    <tr>
                      <td className="p-3">박민수</td>
                      <td className="p-3">청소원</td>
                      <td className="p-3">010-3456-7890</td>
                      <td className="p-3">2023-06-10</td>
                      <td className="p-3">
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                          재직중
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
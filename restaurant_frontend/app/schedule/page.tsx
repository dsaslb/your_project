"use client"

import { useState } from "react"
import { ResizableLayout } from "@/components/resizable-layout"
import { Sidebar } from "@/components/sidebar"
import { Button } from "@/components/ui/button"
import { Calendar, Plus, Users, Clock } from "lucide-react"
import { useUser } from "@/components/UserContext"

export default function SchedulePage() {
  const { user, setUser } = useUser()
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)
  // 더미 매장 데이터
  const stores = [
    { id: "1", name: "강남점" },
    { id: "2", name: "홍대점" },
    { id: "3", name: "잠실점" },
  ]
  // 최고관리자용 매장 선택 state
  const [selectedStore, setSelectedStore] = useState(stores[0].id)

  return (
    <ResizableLayout
      sidebar={
        <Sidebar
          isCollapsed={isSidebarCollapsed}
          onToggle={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
          user={user}
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
          <div className="flex items-center gap-4">
            {user.role === "admin" ? (
              <select
                className="border rounded px-2 py-1 text-sm"
                value={selectedStore}
                onChange={e => setSelectedStore(e.target.value)}
              >
                {stores.map(store => (
                  <option key={store.id} value={store.id}>{store.name}</option>
                ))}
              </select>
            ) : (
              <span className="text-sm text-muted-foreground">{user.name}님 환영합니다</span>
            )}
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              새 스케줄 추가
            </Button>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 p-6 space-y-6">
          {/* 상단 요약 카드 섹션 */}
          <div className="grid gap-6 md:grid-cols-3 mb-8">
            <div className="rounded-lg border bg-card p-6 flex flex-col items-start">
              <span className="text-muted-foreground text-xs mb-1">오늘 근무자</span>
              <span className="text-3xl font-bold text-primary mt-2">12명</span>
            </div>
            <div className="rounded-lg border bg-card p-6 flex flex-col items-start">
              <span className="text-muted-foreground text-xs mb-1">총 근무시간</span>
              <span className="text-3xl font-bold text-orange-500 mt-2">96시간</span>
            </div>
            <div className="rounded-lg border bg-card p-6 flex flex-col items-start">
              <span className="text-muted-foreground text-xs mb-1">청소 스케줄</span>
              <span className="text-3xl font-bold text-green-500 mt-2">3건</span>
            </div>
          </div>

          {/* 주간 스케줄 표 섹션 */}
          <div className="rounded-lg border bg-card mb-8">
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
"use client"

import { useState } from "react"
import { ResizableLayout } from "@/components/resizable-layout"
import { Sidebar } from "@/components/sidebar"
import { Button } from "@/components/ui/button"
import { Package, Plus, Clock, DollarSign } from "lucide-react"

export default function OrdersPage() {
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
          <h1 className="text-2xl font-bold">발주 관리</h1>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            새 발주 추가
          </Button>
        </header>

        {/* Main Content */}
        <main className="flex-1 p-6 space-y-6">
          {/* 통계 카드들 */}
          <div className="grid gap-6 md:grid-cols-3">
            <div className="rounded-lg border bg-card p-6">
              <div className="flex items-center gap-2">
                <Package className="h-5 w-5 text-primary" />
                <h3 className="text-lg font-semibold">이번 달 발주</h3>
              </div>
              <p className="text-3xl font-bold text-primary mt-2">24건</p>
            </div>
            
            <div className="rounded-lg border bg-card p-6">
              <div className="flex items-center gap-2">
                <Clock className="h-5 w-5 text-orange-500" />
                <h3 className="text-lg font-semibold">대기 중</h3>
              </div>
              <p className="text-3xl font-bold text-orange-500 mt-2">3건</p>
            </div>
            
            <div className="rounded-lg border bg-card p-6">
              <div className="flex items-center gap-2">
                <DollarSign className="h-5 w-5 text-green-500" />
                <h3 className="text-lg font-semibold">총 발주액</h3>
              </div>
              <p className="text-3xl font-bold text-green-500 mt-2">₩5,200,000</p>
            </div>
          </div>

          {/* 발주 목록 테이블 */}
          <div className="rounded-lg border">
            <div className="p-6">
              <h2 className="text-xl font-semibold mb-4">발주 목록</h2>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-3">발주번호</th>
                      <th className="text-left p-3">품목</th>
                      <th className="text-left p-3">수량</th>
                      <th className="text-left p-3">금액</th>
                      <th className="text-left p-3">상태</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b">
                      <td className="p-3">#ORD-001</td>
                      <td className="p-3">신선 채소</td>
                      <td className="p-3">50kg</td>
                      <td className="p-3">₩150,000</td>
                      <td className="p-3">
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                          완료
                        </span>
                      </td>
                    </tr>
                    <tr className="border-b">
                      <td className="p-3">#ORD-002</td>
                      <td className="p-3">육류</td>
                      <td className="p-3">30kg</td>
                      <td className="p-3">₩450,000</td>
                      <td className="p-3">
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                          배송중
                        </span>
                      </td>
                    </tr>
                    <tr>
                      <td className="p-3">#ORD-003</td>
                      <td className="p-3">조미료</td>
                      <td className="p-3">20개</td>
                      <td className="p-3">₩80,000</td>
                      <td className="p-3">
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
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
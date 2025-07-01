"use client"

import { useState } from "react"
import { useUser } from "@/components/UserContext"
import { Sidebar } from "@/components/sidebar"
import { Button } from "@/components/ui/button"

// 더미 주문 데이터
const dummyOrders = [
  { id: 1, item: "쌀", quantity: 10, reason: "재고 부족", status: "대기", requester: "김철수", date: "2024-05-01 10:00" },
  { id: 2, item: "고기", quantity: 5, reason: "행사 준비", status: "승인", requester: "이영희", date: "2024-05-02 11:00" },
  { id: 3, item: "야채", quantity: 20, reason: "정기 발주", status: "완료", requester: "박민수", date: "2024-05-03 09:30" },
]

export default function OrdersPage() {
  const { user } = useUser()
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)
  const [showOrderForm, setShowOrderForm] = useState(false)
  const [orders, setOrders] = useState(dummyOrders)

  // 권한별 노출 분기
  const canRequestOrder = user.role === "admin" || user.role === "manager" || user.role === "employee"
  const canViewAll = user.role === "admin"

  // 필터/검색 등은 추후 구현

  return (
    <div className="flex h-screen">
      <Sidebar isCollapsed={isSidebarCollapsed} onToggle={() => setIsSidebarCollapsed(!isSidebarCollapsed)} />
      <main className="flex-1 p-6 space-y-6 bg-background">
        {/* 상단: 발주 요청 버튼/필터 */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
          <h1 className="text-2xl font-bold">발주 관리</h1>
          <div className="flex gap-2">
            {/* 필터(상태/기간 등) - 추후 구현 */}
            {canRequestOrder && (
              <Button onClick={() => setShowOrderForm(true)}>
                + 발주 요청
          </Button>
            )}
          </div>
        </div>
        {/* 중단: 발주 리스트(테이블/카드) */}
        <div className="rounded-lg border bg-card overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                <th className="p-3 text-left">품목</th>
                <th className="p-3 text-left">수량</th>
                <th className="p-3 text-left">요청사유</th>
                <th className="p-3 text-left">상태</th>
                <th className="p-3 text-left">담당자</th>
                <th className="p-3 text-left">일시</th>
                <th className="p-3 text-left">액션</th>
                    </tr>
                  </thead>
                  <tbody>
              {orders.map(order => (
                <tr key={order.id} className="border-b">
                  <td className="p-3">{order.item}</td>
                  <td className="p-3">{order.quantity}</td>
                  <td className="p-3">{order.reason}</td>
                      <td className="p-3">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium 
                      ${order.status === "대기" ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200" : ""}
                      ${order.status === "승인" ? "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200" : ""}
                      ${order.status === "완료" ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200" : ""}
                    `}>{order.status}</span>
                      </td>
                  <td className="p-3">{order.requester}</td>
                  <td className="p-3">{order.date}</td>
                      <td className="p-3">
                    {/* 승인/거절/상세 등 액션 버튼 - 추후 구현 */}
                    <Button size="sm" variant="outline">상세</Button>
                      </td>
                    </tr>
              ))}
                  </tbody>
                </table>
              </div>
        {/* 하단: 더보기/페이징 */}
        <div className="flex justify-center mt-4">
          <Button variant="ghost">더보기</Button>
        </div>
        {/* 발주 요청 폼/모달 - 추후 구현 */}
        {showOrderForm && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-900 rounded-lg p-8 w-full max-w-md">
              <h2 className="text-xl font-bold mb-4">발주 요청 등록</h2>
              {/* 폼 내용 - 추후 OrderForm 컴포넌트로 분리 */}
              <form onSubmit={e => { e.preventDefault(); setShowOrderForm(false); }}>
                <div className="mb-4">
                  <label className="block mb-1 text-sm">품목</label>
                  <input className="w-full border rounded px-2 py-1" required />
                </div>
                <div className="mb-4">
                  <label className="block mb-1 text-sm">수량</label>
                  <input type="number" className="w-full border rounded px-2 py-1" required />
                </div>
                <div className="mb-4">
                  <label className="block mb-1 text-sm">요청사유</label>
                  <input className="w-full border rounded px-2 py-1" required />
                </div>
                <div className="flex gap-2 justify-end">
                  <Button type="button" variant="ghost" onClick={() => setShowOrderForm(false)}>취소</Button>
                  <Button type="submit">등록</Button>
                </div>
              </form>
            </div>
          </div>
        )}
        </main>
      </div>
  )
} 
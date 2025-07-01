"use client";
import { useState } from "react";
import { useUser } from "@/components/UserContext";
import { Sidebar } from "@/components/sidebar";
import { Button } from "@/components/ui/button";

// 더미 재고 데이터
const dummyInventory = [
  { id: 1, name: "쌀", quantity: 50, unit: "kg", status: "정상", category: "곡물", expiry: "2024-07-01" },
  { id: 2, name: "고기", quantity: 10, unit: "kg", status: "임박", category: "육류", expiry: "2024-05-10" },
  { id: 3, name: "야채", quantity: 0, unit: "kg", status: "출고", category: "채소", expiry: "2024-05-03" },
  { id: 4, name: "소스", quantity: 5, unit: "L", status: "폐기", category: "조미료", expiry: "2024-04-30" },
];

// 이력 타입
const dummyHistory = [
  { id: 1, type: "입고", quantity: 10, user: "관리자", date: "2024-05-01", reason: "정기 입고" },
  { id: 2, type: "출고", quantity: 5, user: "직원A", date: "2024-05-02", reason: "주방 사용" },
  { id: 3, type: "폐기", quantity: 2, user: "관리자", date: "2024-05-03", reason: "유통기한 경과" },
];

const statusColors = {
  "정상": "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  "임박": "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  "출고": "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  "폐기": "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
};

function InventoryHistoryModal({ open, onClose, item }) {
  const [history, setHistory] = useState(dummyHistory);
  if (!open || !item) return null;
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-900 rounded-lg p-6 w-full max-w-lg">
        <h2 className="text-xl font-bold mb-4">이력 조회 - {item.name}</h2>
        <table className="w-full mb-4">
          <thead>
            <tr className="border-b">
              <th className="p-2 text-left">구분</th>
              <th className="p-2 text-left">수량</th>
              <th className="p-2 text-left">담당자</th>
              <th className="p-2 text-left">일시</th>
              <th className="p-2 text-left">사유</th>
            </tr>
          </thead>
          <tbody>
            {history.map(h => (
              <tr key={h.id} className="border-b">
                <td className="p-2">{h.type}</td>
                <td className="p-2">{h.quantity}</td>
                <td className="p-2">{h.user}</td>
                <td className="p-2">{h.date}</td>
                <td className="p-2">{h.reason}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <button className="mt-2 px-4 py-2 rounded bg-gray-200 dark:bg-gray-700" onClick={onClose}>닫기</button>
      </div>
    </div>
  );
}

function InventoryActionModal({ open, onClose, type, item, onSubmit }) {
  const [quantity, setQuantity] = useState(1);
  const [reason, setReason] = useState("");
  if (!open || !item) return null;
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-900 rounded-lg p-6 w-full max-w-md">
        <h2 className="text-xl font-bold mb-4">{type} 등록 - {item.name}</h2>
        <form onSubmit={e => { e.preventDefault(); onSubmit(quantity, reason); }}>
          <div className="mb-4">
            <label className="block mb-1 text-sm">수량</label>
            <input type="number" className="w-full border rounded px-2 py-1" value={quantity} min={1} onChange={e => setQuantity(Number(e.target.value))} required />
          </div>
          <div className="mb-4">
            <label className="block mb-1 text-sm">사유</label>
            <input className="w-full border rounded px-2 py-1" value={reason} onChange={e => setReason(e.target.value)} required />
          </div>
          <div className="flex gap-2 justify-end">
            <Button type="button" variant="ghost" onClick={onClose}>취소</Button>
            <Button type="submit">등록</Button>
          </div>
        </form>
      </div>
    </div>
  );
}

const sortOptions = [
  { key: "name", label: "품목명" },
  { key: "quantity", label: "수량" },
  { key: "expiry", label: "유통기한" },
  { key: "status", label: "상태" },
];

export default function InventoryPage() {
  const { user } = useUser();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [inventory, setInventory] = useState(dummyInventory);
  const [filter, setFilter] = useState("");
  const [historyModal, setHistoryModal] = useState({ open: false, item: null });
  const [actionModal, setActionModal] = useState({ open: false, type: "", item: null });
  const [categoryFilter, setCategoryFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [sortKey, setSortKey] = useState("name");
  const [sortOrder, setSortOrder] = useState("asc");

  // 권한별 노출 분기
  const canManage = user.role === "admin" || user.role === "manager";

  // 카테고리 목록 추출
  const categoryList = Array.from(new Set(inventory.map(i => i.category)));
  const statusList = Array.from(new Set(inventory.map(i => i.status)));

  // 다중 조건 필터/정렬 적용
  const filtered = inventory
    .filter(item =>
      (!filter || item.name.includes(filter)) &&
      (!categoryFilter || item.category === categoryFilter) &&
      (!statusFilter || item.status === statusFilter)
    )
    .sort((a, b) => {
      let aVal = a[sortKey];
      let bVal = b[sortKey];
      if (sortKey === "expiry") {
        aVal = aVal.replace(/-/g, "");
        bVal = bVal.replace(/-/g, "");
      }
      if (sortKey === "quantity") {
        aVal = Number(aVal);
        bVal = Number(bVal);
      }
      if (aVal < bVal) return sortOrder === "asc" ? -1 : 1;
      if (aVal > bVal) return sortOrder === "asc" ? 1 : -1;
      return 0;
    });

  return (
    <div className="flex h-screen">
      <Sidebar isCollapsed={isSidebarCollapsed} onToggle={() => setIsSidebarCollapsed(!isSidebarCollapsed)} />
      <main className="flex-1 p-6 space-y-6 bg-background">
        {/* 상단: 입고/출고/폐기/이력 등록 버튼 */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
          <h1 className="text-2xl font-bold">재고 관리</h1>
          <div className="flex gap-2">
            {canManage && <Button onClick={() => setShowForm(true)}>+ 재고 등록</Button>}
            {canManage && <Button variant="outline" onClick={() => setActionModal({ open: true, type: "입고", item: null })}>입고</Button>}
            {canManage && <Button variant="outline" onClick={() => setActionModal({ open: true, type: "출고", item: null })}>출고</Button>}
            {canManage && <Button variant="outline" onClick={() => setActionModal({ open: true, type: "폐기", item: null })}>폐기</Button>}
            <Button variant="ghost">이력</Button>
          </div>
        </div>
        {/* 중단: 재고 리스트(테이블) + 필터/정렬 UI */}
        <div className="flex flex-wrap gap-2 mb-2">
          <input
            className="border rounded px-2 py-1 text-sm"
            placeholder="품목명 검색"
            value={filter}
            onChange={e => setFilter(e.target.value)}
          />
          <select className="border rounded px-2 py-1 text-sm" value={categoryFilter} onChange={e => setCategoryFilter(e.target.value)}>
            <option value="">전체 카테고리</option>
            {categoryList.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
          <select className="border rounded px-2 py-1 text-sm" value={statusFilter} onChange={e => setStatusFilter(e.target.value)}>
            <option value="">전체 상태</option>
            {statusList.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
          <select className="border rounded px-2 py-1 text-sm" value={sortKey} onChange={e => setSortKey(e.target.value)}>
            {sortOptions.map(opt => <option key={opt.key} value={opt.key}>{opt.label}</option>)}
          </select>
          <Button size="sm" variant="ghost" onClick={() => setSortOrder(o => o === "asc" ? "desc" : "asc")}>{sortOrder === "asc" ? "오름차순" : "내림차순"}</Button>
        </div>
        <div className="rounded-lg border bg-card overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="p-3 text-left">품목명</th>
                <th className="p-3 text-left">수량</th>
                <th className="p-3 text-left">단위</th>
                <th className="p-3 text-left">카테고리</th>
                <th className="p-3 text-left">유통기한</th>
                <th className="p-3 text-left">상태</th>
                <th className="p-3 text-left">액션</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(item => (
                <tr key={item.id} className="border-b">
                  <td className="p-3">{item.name}</td>
                  <td className="p-3">{item.quantity}</td>
                  <td className="p-3">{item.unit}</td>
                  <td className="p-3">{item.category}</td>
                  <td className="p-3">{item.expiry}</td>
                  <td className="p-3">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${statusColors[item.status]}`}>{item.status}</span>
                  </td>
                  <td className="p-3 flex gap-1">
                    {canManage && <Button size="sm" variant="outline" onClick={() => setShowForm(true)}>수정</Button>}
                    {canManage && <Button size="sm" variant="destructive" onClick={() => setActionModal({ open: true, type: "폐기", item })}>폐기</Button>}
                    {canManage && <Button size="sm" variant="outline" onClick={() => setActionModal({ open: true, type: "입고", item })}>입고</Button>}
                    {canManage && <Button size="sm" variant="outline" onClick={() => setActionModal({ open: true, type: "출고", item })}>출고</Button>}
                    <Button size="sm" variant="ghost" onClick={() => setHistoryModal({ open: true, item })}>이력</Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {/* 재고 등록/수정 폼/모달 - 추후 분리 */}
        {showForm && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-900 rounded-lg p-8 w-full max-w-md">
              <h2 className="text-xl font-bold mb-4">재고 등록</h2>
              <form onSubmit={e => { e.preventDefault(); setShowForm(false); }}>
                <div className="mb-4">
                  <label className="block mb-1 text-sm">품목명</label>
                  <input className="w-full border rounded px-2 py-1" required />
                </div>
                <div className="mb-4">
                  <label className="block mb-1 text-sm">수량</label>
                  <input type="number" className="w-full border rounded px-2 py-1" required />
                </div>
                <div className="mb-4">
                  <label className="block mb-1 text-sm">단위</label>
                  <input className="w-full border rounded px-2 py-1" required />
                </div>
                <div className="mb-4">
                  <label className="block mb-1 text-sm">카테고리</label>
                  <input className="w-full border rounded px-2 py-1" required />
                </div>
                <div className="mb-4">
                  <label className="block mb-1 text-sm">유통기한</label>
                  <input type="date" className="w-full border rounded px-2 py-1" required />
                </div>
                <div className="flex gap-2 justify-end">
                  <Button type="button" variant="ghost" onClick={() => setShowForm(false)}>취소</Button>
                  <Button type="submit">등록</Button>
                </div>
              </form>
            </div>
          </div>
        )}
        {/* 입고/출고/폐기 폼/모달 */}
        <InventoryActionModal
          open={actionModal.open}
          onClose={() => setActionModal({ open: false, type: "", item: null })}
          type={actionModal.type}
          item={actionModal.item}
          onSubmit={(quantity, reason) => {
            // 수량/상태 실시간 반영 예시(입고/출고/폐기)
            if (!actionModal.item) return;
            setInventory(inv => inv.map(i => {
              if (i.id !== actionModal.item.id) return i;
              let newQty = i.quantity;
              if (actionModal.type === "입고") newQty += quantity;
              if (actionModal.type === "출고") newQty = Math.max(0, newQty - quantity);
              if (actionModal.type === "폐기") newQty = Math.max(0, newQty - quantity);
              // 상태 자동 변경 예시
              let newStatus = i.status;
              if (newQty === 0) newStatus = actionModal.type === "폐기" ? "폐기" : "출고";
              else if (i.expiry < new Date().toISOString().slice(0,10)) newStatus = "임박";
              else newStatus = "정상";
              return { ...i, quantity: newQty, status: newStatus };
            }));
            setActionModal({ open: false, type: "", item: null });
          }}
        />
        {/* 이력 모달 */}
        <InventoryHistoryModal
          open={historyModal.open}
          onClose={() => setHistoryModal({ open: false, item: null })}
          item={historyModal.item}
        />
      </main>
    </div>
  );
} 
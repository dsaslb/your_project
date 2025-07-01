import { useState, useMemo } from "react";
import { Button } from "@/components/ui/button";
import { getOrderStatusBadge, formatDate } from "@/lib/utils";
import { User } from "@/components/UserContext";
import { Order } from "./OrderCard";
import { OrderStatusBadge } from "@/components/OrderStatusBadge";

type OrderTableProps = {
  orders: Order[];
  user: User;
  onApprove?: (id: number) => void;
  onReject?: (id: number) => void;
  onDetail?: (id: number) => void;
  loading?: boolean;
  error?: string | null;
  onRetry?: () => void;
};

const statusOptions = ["전체", "대기", "승인", "완료", "거절"];

export function OrderTable({ orders, user, onApprove, onReject, onDetail, loading, error, onRetry }: OrderTableProps) {
  // 필터/검색/정렬 상태
  const [status, setStatus] = useState("전체");
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState<"desc"|"asc">("desc");
  const [sortKey, setSortKey] = useState<keyof Order>("date");
  // 권한별 담당자 필터 옵션
  const 담당자목록 = useMemo(() => Array.from(new Set(orders.map(o => o.requester))), [orders]);
  const [requester, setRequester] = useState("전체");

  // 필터/검색/정렬 적용
  const filtered = useMemo(() => {
    let data = orders;
    if (status !== "전체") data = data.filter(o => o.status === status);
    if (requester !== "전체") data = data.filter(o => o.requester === requester);
    if (search.trim()) data = data.filter(o => o.item.includes(search) || o.reason.includes(search));
    data = [...data].sort((a, b) => {
      if (sortKey === "date") {
        return sort === "desc" ? b.date.localeCompare(a.date) : a.date.localeCompare(b.date);
      }
      return 0;
    });
    return data;
  }, [orders, status, requester, search, sort, sortKey]);

  // 권한별 필터 옵션 분기(예시)
  const showRequesterFilter = user.role === "admin" || user.role === "manager";

  // 로딩/에러/empty UX
  if (loading) return <div className="py-8 text-center text-muted-foreground">로딩 중...</div>;
  if (error) return <div className="py-8 text-center text-red-500">에러 발생: {error} <Button onClick={onRetry}>다시 시도</Button></div>;
  if (filtered.length === 0) return <div className="py-8 text-center text-muted-foreground">주문 내역이 없습니다.</div>;

  return (
    <div className="overflow-x-auto rounded-lg border bg-card" aria-label="발주 테이블">
      {/* 상단 필터/검색/정렬 UI */}
      <div className="flex flex-wrap gap-2 p-3 items-center border-b bg-background">
        <select className="border rounded px-2 py-1 text-sm" value={status} onChange={e => setStatus(e.target.value)}>
          {statusOptions.map(opt => <option key={opt} value={opt}>{opt}</option>)}
        </select>
        {showRequesterFilter && (
          <select className="border rounded px-2 py-1 text-sm" value={requester} onChange={e => setRequester(e.target.value)}>
            <option value="전체">전체 담당자</option>
            {담당자목록.map(r => <option key={r} value={r}>{r}</option>)}
          </select>
        )}
        <input
          className="border rounded px-2 py-1 text-sm"
          placeholder="품목/사유 검색"
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <Button size="sm" variant="ghost" onClick={() => { setSort(s => s === "desc" ? "asc" : "desc"); }}>
          {sort === "desc" ? "최신순" : "오래된순"}
        </Button>
      </div>
      <table className="w-full">
        <thead>
          <tr className="border-b">
            <th className="p-3 text-left cursor-pointer" onClick={() => setSortKey("item")}>품목</th>
            <th className="p-3 text-left">수량</th>
            <th className="p-3 text-left">요청사유</th>
            <th className="p-3 text-left cursor-pointer" onClick={() => setSortKey("status")}>상태</th>
            <th className="p-3 text-left">담당자</th>
            <th className="p-3 text-left cursor-pointer" onClick={() => setSortKey("date")}>일시</th>
            <th className="p-3 text-left">액션</th>
          </tr>
        </thead>
        <tbody>
          {filtered.map(order => (
            <tr key={order.id} className="border-b">
              <td className="p-3">{order.item}</td>
              <td className="p-3">{order.quantity}</td>
              <td className="p-3">{order.reason}</td>
              <td className="p-3"><OrderStatusBadge status={order.status} /></td>
              <td className="p-3">{order.requester}</td>
              <td className="p-3">{formatDate(order.date)}</td>
              <td className="p-3">
                <div className="flex gap-2">
                  {/* 권한별 액션 분기 */}
                  {(user.role === "admin" || user.role === "manager" || (user.role === "employee" && user.name === order.requester)) && (
                    <Button size="sm" variant="outline" onClick={() => onDetail?.(order.id)}>상세</Button>
                  )}
                  {(user.role === "admin" || user.role === "manager") && order.status === "대기" && (
                    <Button size="sm" onClick={() => onApprove?.(order.id)}>승인</Button>
                  )}
                  {(user.role === "admin" || user.role === "manager") && order.status === "대기" && (
                    <Button size="sm" variant="destructive" onClick={() => onReject?.(order.id)}>거절</Button>
                  )}
                  {(user.role === "employee" && user.name === order.requester && order.status === "대기") && (
                    <Button size="sm" variant="destructive">취소</Button>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
} 
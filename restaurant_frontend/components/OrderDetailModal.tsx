import React from "react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { getOrderStatusBadgeClass, formatDate } from "@/lib/utils";
import { User } from "@/components/UserContext";
import { Order } from "./OrderCard";
import { OrderStatusBadge } from "@/components/OrderStatusBadge";

// 더미 이력/댓글 fetch 함수 (실제 API로 교체 가능)
async function fetchOrderHistory(orderId: number) {
  // 실제 API 연동 시 fetch(`/api/orders/${orderId}/history`)
  return [
    { id: 1, status: "대기", user: "김철수", date: "2024-05-01 10:00", reason: "신규 요청" },
    { id: 2, status: "승인", user: "관리자", date: "2024-05-01 11:00", reason: "재고 확인 후 승인" },
  ];
}
async function fetchOrderComments(orderId: number) {
  return [
    { id: 1, user: "김철수", comment: "빠른 승인 부탁드립니다", date: "2024-05-01 10:05" },
    { id: 2, user: "관리자", comment: "확인 중입니다", date: "2024-05-01 10:10" },
  ];
}
async function postOrderComment(orderId: number, user: string, comment: string) {
  // 실제 API 연동 시 POST 요청
  return { id: Math.random(), user, comment, date: new Date().toISOString() };
}

type OrderDetailModalProps = {
  order: Order | null;
  open: boolean;
  onClose: () => void;
  user: User;
};

export function OrderDetailModal({ order, open, onClose, user }: OrderDetailModalProps) {
  const [history, setHistory] = useState<any[]>([]);
  const [comments, setComments] = useState<any[]>([]);
  const [commentInput, setCommentInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [commentLoading, setCommentLoading] = useState(false);

  // 모달 열릴 때 이력/댓글 fetch
  React.useEffect(() => {
    if (open && order) {
      setLoading(true);
      Promise.all([
        fetchOrderHistory(order.id),
        fetchOrderComments(order.id)
      ]).then(([h, c]) => {
        setHistory(h);
        setComments(c);
        setLoading(false);
      });
    }
  }, [open, order]);

  // 댓글 등록
  const handleCommentSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!commentInput.trim() || !order) return;
    setCommentLoading(true);
    const newComment = await postOrderComment(order.id, user.name, commentInput);
    setComments([...comments, newComment]);
    setCommentInput("");
    setCommentLoading(false);
  };

  if (!open || !order) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" aria-modal="true" role="dialog" aria-labelledby="order-detail-title">
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow-lg w-full max-w-2xl p-6 relative">
        <button className="absolute top-2 right-2 text-xl" onClick={onClose} aria-label="닫기">×</button>
        <h2 id="order-detail-title" className="text-2xl font-bold mb-4">발주 상세 정보</h2>
        {loading ? (
          <div className="text-center py-8">로딩 중...</div>
        ) : (
          <>
            {/* 상세 정보 */}
            <div className="mb-4">
              <div className="flex gap-4 items-center mb-2">
                <span className="font-semibold text-lg">{order.item}</span>
                <OrderStatusBadge status={order.status} />
              </div>
              <div className="text-sm text-muted-foreground">수량: {order.quantity}</div>
              <div className="text-sm text-muted-foreground">요청사유: {order.reason}</div>
              <div className="text-sm text-muted-foreground">요청자: {order.requester}</div>
              <div className="text-sm text-muted-foreground">요청일시: {formatDate(order.date)}</div>
            </div>
            {/* 상태변경 이력 */}
            <div className="mb-4">
              <h3 className="font-semibold mb-2">상태변경 이력</h3>
              <ul className="space-y-1">
                {history.map(h => (
                  <li key={h.id} className="text-xs flex gap-2 items-center">
                    <OrderStatusBadge status={h.status} />
                    <span>{h.user}</span>
                    <span>{formatDate(h.date)}</span>
                    <span className="text-muted-foreground">{h.reason}</span>
                  </li>
                ))}
              </ul>
            </div>
            {/* 댓글/메모 */}
            <div className="mb-2">
              <h3 className="font-semibold mb-2">댓글/메모</h3>
              <ul className="space-y-1 max-h-32 overflow-y-auto mb-2">
                {comments.map(c => (
                  <li key={c.id} className="text-xs flex gap-2 items-center">
                    <span className="font-semibold">{c.user}</span>
                    <span>{c.comment}</span>
                    <span className="text-muted-foreground">{formatDate(c.date)}</span>
                  </li>
                ))}
              </ul>
              <form onSubmit={handleCommentSubmit} className="flex gap-2">
                <input
                  className="flex-1 border rounded px-2 py-1 text-sm"
                  value={commentInput}
                  onChange={e => setCommentInput(e.target.value)}
                  placeholder="댓글을 입력하세요"
                  aria-label="댓글 입력"
                  required
                />
                <Button type="submit" size="sm" disabled={commentLoading}>
                  {commentLoading ? "등록 중..." : "등록"}
                </Button>
              </form>
            </div>
          </>
        )}
      </div>
    </div>
  );
} 
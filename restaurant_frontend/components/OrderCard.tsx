import { Button } from "@/components/ui/button";
import { getOrderStatusBadgeClass, formatDate } from "@/lib/utils";
import { User } from "@/components/UserContext";
import { OrderStatusBadge } from "@/components/OrderStatusBadge";

export type Order = {
  id: number;
  item: string;
  quantity: number;
  reason: string;
  status: string;
  requester: string;
  date: string;
};

type OrderCardProps = {
  order: Order;
  user: User;
  onApprove?: (id: number) => void;
  onReject?: (id: number) => void;
  onDetail?: (id: number) => void;
};

export function OrderCard({ order, user, onApprove, onReject, onDetail }: OrderCardProps) {
  // 권한별 액션 분기
  const canApprove = user.role === "admin" || user.role === "manager";
  const canReject = user.role === "admin" || user.role === "manager";
  const canDetail = true;

  return (
    <div className="rounded-lg border bg-card p-4 flex flex-col gap-2 shadow-sm" aria-label="발주 카드">
      <div className="flex items-center justify-between">
        <div className="font-semibold text-lg">{order.item}</div>
        <OrderStatusBadge status={order.status} />
      </div>
      <div className="text-sm text-muted-foreground">수량: {order.quantity}</div>
      <div className="text-sm text-muted-foreground">요청사유: {order.reason}</div>
      <div className="flex justify-between items-center mt-2">
        <span className="text-xs text-muted-foreground">{order.requester} | {formatDate(order.date)}</span>
        <div className="flex gap-2">
          {canDetail && <Button size="sm" variant="outline" onClick={() => onDetail?.(order.id)}>상세</Button>}
          {canApprove && order.status === "대기" && <Button size="sm" onClick={() => onApprove?.(order.id)}>승인</Button>}
          {canReject && order.status === "대기" && <Button size="sm" variant="destructive" onClick={() => onReject?.(order.id)}>거절</Button>}
        </div>
      </div>
    </div>
  );
} 
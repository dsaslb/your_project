"use client";
import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { useNotifications } from "@/components/NotificationSystem";
import estimateCookingTime from "../estimate-cooking-time";

const initialOrders = [
  { id: 1, table: "A1", menu: "김치찌개", status: "주문", orderedAt: Date.now() },
  { id: 2, table: "B2", menu: "불고기", status: "주문", orderedAt: Date.now() },
];

const statusSteps = ["주문", "조리중", "서빙중", "완료"];

export default function KitchenMonitorPage() {
  const [orders, setOrders] = useState(initialOrders);
  const { addNotification } = useNotifications();

  const handleNextStatus = (orderId: number) => {
    setOrders(prev => prev.map(order => {
      if (order.id === orderId) {
        const nextIdx = statusSteps.indexOf(order.status) + 1;
        const newStatus = statusSteps[nextIdx] || order.status;
        if (newStatus !== order.status) {
          addNotification({
            type: "info",
            title: `${order.menu} ${newStatus}`,
            message: `${order.table} 테이블 ${order.menu} ${newStatus} 처리됨.`
          });
        }
        return { ...order, status: newStatus };
      }
      return order;
    }));
  };

  // 혼잡도: 조리중 주문 수
  const busyLevel = orders.filter(o => o.status === "조리중").length;

  return (
    <div className="max-w-2xl mx-auto p-4 bg-white dark:bg-gray-900 rounded-lg shadow mt-4">
      <h2 className="text-xl font-bold mb-2">주문-조리-서빙 실시간 모니터링</h2>
      <div className="mb-4 flex gap-2">
        <Badge variant={busyLevel > 2 ? "destructive" : busyLevel > 0 ? "warning" : "success"}>
          주방 혼잡도: {busyLevel > 2 ? "혼잡" : busyLevel > 0 ? "보통" : "여유"}
        </Badge>
      </div>
      <div className="space-y-4">
        {orders.map(order => (
          <Card key={order.id}>
            <CardHeader>
              <CardTitle>
                {order.menu} <span className="text-sm text-gray-400">({order.table})</span>
                <Badge className="ml-2" variant={order.status === "완료" ? "success" : order.status === "조리중" ? "warning" : "default"}>{order.status}</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <Button size="sm" onClick={() => handleNextStatus(order.id)} disabled={order.status === "완료"}>
                  다음 단계
                </Button>
                <span className="ml-4 text-xs text-gray-500">
                  예상 조리시간: {estimateCookingTime(orders.length)}분
                </span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Clock, CheckCircle, XCircle, DollarSign, Package, TrendingUp, Users } from "lucide-react";

export function OrderManagement() {
  const [statusFilter, setStatusFilter] = useState("all");
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const orderData = [
    {
      id: "ORD-001",
      tableNumber: 5,
      items: ["불고기 정식", "김치찌개", "콜라 2잔"],
      total: 32000,
      status: "preparing",
      orderTime: new Date(Date.now() - 15 * 60 * 1000),
      estimatedTime: 10,
      customer: "김고객",
      paymentMethod: "카드",
    },
    {
      id: "ORD-002",
      tableNumber: 3,
      items: ["비빔밥", "된장찌개"],
      total: 18000,
      status: "ready",
      orderTime: new Date(Date.now() - 25 * 60 * 1000),
      estimatedTime: 0,
      customer: "이고객",
      paymentMethod: "현금",
    },
    {
      id: "ORD-003",
      tableNumber: 8,
      items: ["갈비탕", "공기밥"],
      total: 17000,
      status: "completed",
      orderTime: new Date(Date.now() - 45 * 60 * 1000),
      estimatedTime: 0,
      customer: "박고객",
      paymentMethod: "카드",
    },
    {
      id: "ORD-004",
      tableNumber: 12,
      items: ["냉면", "만두"],
      total: 20000,
      status: "cancelled",
      orderTime: new Date(Date.now() - 30 * 60 * 1000),
      estimatedTime: 0,
      customer: "최고객",
      paymentMethod: "카드",
    },
    {
      id: "ORD-005",
      tableNumber: 7,
      items: ["불고기 정식", "비빔밥", "사이다 3잔"],
      total: 42000,
      status: "preparing",
      orderTime: new Date(Date.now() - 8 * 60 * 1000),
      estimatedTime: 15,
      customer: "정고객",
      paymentMethod: "카드",
    },
  ];

  const filteredOrders = orderData.filter((order) => statusFilter === "all" || order.status === statusFilter);

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      preparing: {
        label: "준비중",
        className: "bg-yellow-100 text-yellow-700 border-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-300",
        icon: Clock,
      },
      ready: {
        label: "완료",
        className: "bg-green-100 text-green-700 border-green-200 dark:bg-green-900/30 dark:text-green-300",
        icon: CheckCircle,
      },
      completed: {
        label: "서빙완료",
        className: "bg-blue-100 text-blue-700 border-blue-200 dark:bg-blue-900/30 dark:text-blue-300",
        icon: CheckCircle,
      },
      cancelled: {
        label: "취소",
        className: "bg-red-100 text-red-700 border-red-200 dark:bg-red-900/30 dark:text-red-300",
        icon: XCircle,
      },
    };

    const config = statusConfig[status as keyof typeof statusConfig];
    const Icon = config.icon;

    return (
      <Badge variant="outline" className={config.className}>
        <Icon className="h-3 w-3 mr-1" />
        {config.label}
      </Badge>
    );
  };

  const getElapsedTime = (orderTime: Date) => {
    const elapsed = Math.floor((currentTime.getTime() - orderTime.getTime()) / 1000 / 60);
    return elapsed;
  };

  const getTimeColor = (elapsed: number, status: string) => {
    if (status === "completed" || status === "cancelled") return "text-gray-500";
    if (elapsed > 30) return "text-red-600";
    if (elapsed > 20) return "text-orange-600";
    return "text-green-600";
  };

  const stats = {
    total: orderData.length,
    preparing: orderData.filter((o) => o.status === "preparing").length,
    ready: orderData.filter((o) => o.status === "ready").length,
    completed: orderData.filter((o) => o.status === "completed").length,
    totalRevenue: orderData.filter((o) => o.status !== "cancelled").reduce((sum, o) => sum + o.total, 0),
    avgOrderValue:
      orderData.filter((o) => o.status !== "cancelled").reduce((sum, o) => sum + o.total, 0) /
      orderData.filter((o) => o.status !== "cancelled").length,
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
            주문 관리
          </h2>
          <p className="text-gray-500 dark:text-gray-400 mt-1">실시간 주문 현황을 확인하고 관리하세요</p>
        </div>
        <div className="flex items-center space-x-3">
          <div className="text-sm text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-800 px-3 py-2 rounded-lg">
            <Clock className="h-4 w-4 inline mr-1" />
            {currentTime.toLocaleTimeString("ko-KR")}
          </div>
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="상태 필터" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">전체</SelectItem>
              <SelectItem value="preparing">준비중</SelectItem>
              <SelectItem value="ready">완료</SelectItem>
              <SelectItem value="completed">서빙완료</SelectItem>
              <SelectItem value="cancelled">취소</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
        <Card className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-0 shadow-lg">
          <CardContent className="p-4">
            <div className="text-center">
              <div className="p-2 rounded-lg bg-gradient-to-r from-blue-500 to-cyan-500 w-fit mx-auto mb-2">
                <Package className="h-4 w-4 text-white" />
              </div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">총 주문</p>
              <p className="text-2xl font-bold text-blue-600">{stats.total}</p>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-0 shadow-lg">
          <CardContent className="p-4">
            <div className="text-center">
              <div className="p-2 rounded-lg bg-gradient-to-r from-yellow-500 to-orange-500 w-fit mx-auto mb-2">
                <Clock className="h-4 w-4 text-white" />
              </div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">준비중</p>
              <p className="text-2xl font-bold text-yellow-600">{stats.preparing}</p>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-0 shadow-lg">
          <CardContent className="p-4">
            <div className="text-center">
              <div className="p-2 rounded-lg bg-gradient-to-r from-green-500 to-emerald-500 w-fit mx-auto mb-2">
                <CheckCircle className="h-4 w-4 text-white" />
              </div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">완료</p>
              <p className="text-2xl font-bold text-green-600">{stats.ready}</p>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-0 shadow-lg">
          <CardContent className="p-4">
            <div className="text-center">
              <div className="p-2 rounded-lg bg-gradient-to-r from-purple-500 to-pink-500 w-fit mx-auto mb-2">
                <Users className="h-4 w-4 text-white" />
              </div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">서빙완료</p>
              <p className="text-2xl font-bold text-purple-600">{stats.completed}</p>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-0 shadow-lg">
          <CardContent className="p-4">
            <div className="text-center">
              <div className="p-2 rounded-lg bg-gradient-to-r from-green-500 to-blue-500 w-fit mx-auto mb-2">
                <DollarSign className="h-4 w-4 text-white" />
              </div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">총 매출</p>
              <p className="text-xl font-bold text-green-600">₩{stats.totalRevenue.toLocaleString()}</p>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-0 shadow-lg">
          <CardContent className="p-4">
            <div className="text-center">
              <div className="p-2 rounded-lg bg-gradient-to-r from-indigo-500 to-purple-500 w-fit mx-auto mb-2">
                <TrendingUp className="h-4 w-4 text-white" />
              </div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">평균 주문액</p>
              <p className="text-xl font-bold text-indigo-600">₩{Math.round(stats.avgOrderValue).toLocaleString()}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-0 shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Package className="h-6 w-6 text-green-500" />
            <span>주문 현황</span>
          </CardTitle>
          <CardDescription>실시간 주문 상태를 확인하고 관리하세요</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>주문 정보</TableHead>
                  <TableHead>테이블</TableHead>
                  <TableHead>주문 내역</TableHead>
                  <TableHead className="text-right">금액</TableHead>
                  <TableHead>경과 시간</TableHead>
                  <TableHead>예상 시간</TableHead>
                  <TableHead className="text-center">상태</TableHead>
                  <TableHead className="text-center">액션</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredOrders.map((order) => {
                  const elapsed = getElapsedTime(order.orderTime);
                  return (
                    <TableRow key={order.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                      <TableCell>
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white">{order.id}</p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">{order.customer}</p>
                          <p className="text-xs text-gray-400 dark:text-gray-500">{order.paymentMethod}</p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="text-center">
                          <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-full flex items-center justify-center font-bold text-sm">
                            {order.tableNumber}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="max-w-48">
                          {order.items.map((item, index) => (
                            <p key={index} className="text-sm text-gray-600 dark:text-gray-400">
                              • {item}
                            </p>
                          ))}
                        </div>
                      </TableCell>
                      <TableCell className="text-right font-mono font-semibold">
                        ₩{order.total.toLocaleString()}
                      </TableCell>
                      <TableCell>
                        <span className={`font-medium ${getTimeColor(elapsed, order.status)}`}>{elapsed}분</span>
                      </TableCell>
                      <TableCell>
                        {order.estimatedTime > 0 ? (
                          <span className="text-orange-600 font-medium">{order.estimatedTime}분</span>
                        ) : (
                          <span className="text-gray-400">-</span>
                        )}
                      </TableCell>
                      <TableCell className="text-center">{getStatusBadge(order.status)}</TableCell>
                      <TableCell className="text-center">
                        <div className="flex space-x-1 justify-center">
                          {order.status === "preparing" && (
                            <Button
                              size="sm"
                              variant="outline"
                              className="text-green-600 border-green-600 hover:bg-green-50 bg-transparent"
                            >
                              완료
                            </Button>
                          )}
                          {order.status === "ready" && (
                            <Button
                              size="sm"
                              variant="outline"
                              className="text-blue-600 border-blue-600 hover:bg-blue-50 bg-transparent"
                            >
                              서빙
                            </Button>
                          )}
                          {(order.status === "preparing" || order.status === "ready") && (
                            <Button
                              size="sm"
                              variant="outline"
                              className="text-red-600 border-red-600 hover:bg-red-50 bg-transparent"
                            >
                              취소
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 
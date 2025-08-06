"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ShoppingCart, Users, DollarSign, TrendingUp, Clock, Package } from 'lucide-react';
import { toast } from 'sonner';

interface Order {
  id: number;
  customer_name: string;
  customer_email: string;
  order_date: string;
  total_amount: number;
  status: 'pending' | 'confirmed' | 'preparing' | 'ready' | 'delivered' | 'cancelled';
  items: OrderItem[];
  branch_id: number;
}

interface OrderItem {
  id: number;
  product_name: string;
  quantity: number;
  unit_price: number;
}

interface OrderStats {
  totalOrders: number;
  pendingOrders: number;
  totalRevenue: number;
  averageOrderValue: number;
  totalCustomers: number;
  activeCustomers: number;
}

export default function OrderManagementPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [stats, setStats] = useState<OrderStats>({
    totalOrders: 0,
    pendingOrders: 0,
    totalRevenue: 0,
    averageOrderValue: 0,
    totalCustomers: 0,
    activeCustomers: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOrderData();
  }, []);

  const fetchOrderData = async () => {
    try {
      setLoading(true);
      
      // 샘플 주문 데이터 (실제로는 API에서 가져와야 함)
      const sampleOrders: Order[] = [
        {
          id: 1,
          customer_name: '김고객',
          customer_email: 'kim@example.com',
          order_date: '2024-01-15 14:30:00',
          total_amount: 15000,
          status: 'confirmed',
          branch_id: 1,
          items: [
            { id: 1, product_name: '아메리카노', quantity: 2, unit_price: 4500 },
            { id: 2, product_name: '카페라떼', quantity: 1, unit_price: 6000 }
          ]
        },
        {
          id: 2,
          customer_name: '이고객',
          customer_email: 'lee@example.com',
          order_date: '2024-01-15 15:15:00',
          total_amount: 12000,
          status: 'preparing',
          branch_id: 1,
          items: [
            { id: 3, product_name: '카푸치노', quantity: 1, unit_price: 5500 },
            { id: 4, product_name: '에스프레소', quantity: 1, unit_price: 3500 },
            { id: 5, product_name: '티라떼', quantity: 1, unit_price: 3000 }
          ]
        },
        {
          id: 3,
          customer_name: '박고객',
          customer_email: 'park@example.com',
          order_date: '2024-01-15 16:00:00',
          total_amount: 8000,
          status: 'ready',
          branch_id: 2,
          items: [
            { id: 6, product_name: '아메리카노', quantity: 1, unit_price: 4500 },
            { id: 7, product_name: '크로아상', quantity: 1, unit_price: 3500 }
          ]
        },
        {
          id: 4,
          customer_name: '최고객',
          customer_email: 'choi@example.com',
          order_date: '2024-01-15 16:45:00',
          total_amount: 25000,
          status: 'delivered',
          branch_id: 1,
          items: [
            { id: 8, product_name: '카페모카', quantity: 2, unit_price: 6500 },
            { id: 9, product_name: '바닐라라떼', quantity: 1, unit_price: 6000 },
            { id: 10, product_name: '치즈케이크', quantity: 1, unit_price: 6000 }
          ]
        }
      ];

      setOrders(sampleOrders);

      // 통계 계산
      const totalOrders = sampleOrders.length;
      const pendingOrders = sampleOrders.filter(order => 
        ['pending', 'confirmed', 'preparing'].includes(order.status)
      ).length;
      const totalRevenue = sampleOrders.reduce((sum, order) => sum + order.total_amount, 0);
      const averageOrderValue = totalOrders > 0 ? totalRevenue / totalOrders : 0;
      const uniqueCustomers = new Set(sampleOrders.map(order => order.customer_email));
      const totalCustomers = uniqueCustomers.size;
      const activeCustomers = totalCustomers; // 샘플 데이터에서는 모든 고객을 활성으로 간주

      setStats({
        totalOrders,
        pendingOrders,
        totalRevenue,
        averageOrderValue,
        totalCustomers,
        activeCustomers
      });

    } catch (error) {
      console.error('주문 데이터 로딩 오류:', error);
      toast.error('데이터를 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'text-yellow-600';
      case 'confirmed': return 'text-blue-600';
      case 'preparing': return 'text-orange-600';
      case 'ready': return 'text-green-600';
      case 'delivered': return 'text-gray-600';
      case 'cancelled': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending': return '대기중';
      case 'confirmed': return '확인됨';
      case 'preparing': return '준비중';
      case 'ready': return '준비완료';
      case 'delivered': return '배달완료';
      case 'cancelled': return '취소됨';
      default: return '알 수 없음';
    }
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="text-lg mb-2">로딩 중...</div>
            <div className="text-sm text-gray-500">주문 데이터를 가져오는 중입니다</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">주문 관리</h1>
        <p className="text-gray-600">주문 및 고객 관리</p>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 주문</CardTitle>
            <ShoppingCart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalOrders}건</div>
            <p className="text-xs text-muted-foreground">대기중: {stats.pendingOrders}건</p>
          </CardContent>
        </Card>

        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 매출</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">₩{stats.totalRevenue.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">오늘 총 매출</p>
          </CardContent>
        </Card>

        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">평균 주문액</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">₩{Math.round(stats.averageOrderValue).toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">주문당 평균</p>
          </CardContent>
        </Card>

        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">고객 수</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalCustomers}명</div>
            <p className="text-xs text-muted-foreground">활성 고객</p>
          </CardContent>
        </Card>
      </div>

      {/* 주문 목록 */}
      <Card className="border border-gray-100">
        <CardHeader>
          <CardTitle>주문 현황</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {orders.map((order) => (
              <div key={order.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h4 className="font-semibold text-lg">주문 #{order.id}</h4>
                    <p className="text-sm text-gray-600">{order.customer_name} ({order.customer_email})</p>
                  </div>
                  <div className="text-right">
                    <span className={`text-sm px-2 py-1 rounded ${getStatusColor(order.status)}`}>
                      {getStatusText(order.status)}
                    </span>
                    <p className="text-lg font-bold mt-1">₩{order.total_amount.toLocaleString()}</p>
                  </div>
                </div>
                <div className="space-y-2">
                  <p className="text-sm text-gray-600">주문 시간: {order.order_date}</p>
                  <div className="border-t pt-2">
                    <p className="text-sm font-medium mb-1">주문 상품:</p>
                    <div className="space-y-1">
                      {order.items.map((item) => (
                        <div key={item.id} className="flex justify-between text-sm text-gray-600">
                          <span>{item.product_name} x {item.quantity}</span>
                          <span>₩{(item.unit_price * item.quantity).toLocaleString()}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
            {orders.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                등록된 주문이 없습니다.
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 
'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  Package, 
  Search, 
  Filter,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  DollarSign,
  User,
  MapPin
} from 'lucide-react';

interface Order {
  id: number;
  order_number: string;
  customer_name: string;
  customer_phone: string;
  items: Array<{
    name: string;
    quantity: number;
    price: number;
  }>;
  total_amount: number;
  status: 'pending' | 'preparing' | 'ready' | 'completed' | 'cancelled';
  order_time: string;
  estimated_delivery: string;
  delivery_address: string;
  payment_method: string;
}

export default function OrdersPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  // 샘플 데이터
  const orders: Order[] = [
    {
      id: 1,
      order_number: 'ORD-2024-001',
      customer_name: '김철수',
      customer_phone: '010-1234-5678',
      items: [
        { name: '아메리카노', quantity: 2, price: 4500 },
        { name: '카페라떼', quantity: 1, price: 5000 }
      ],
      total_amount: 14000,
      status: 'preparing',
      order_time: '2024-01-15T14:30:00',
      estimated_delivery: '2024-01-15T15:00:00',
      delivery_address: '서울시 강남구 테헤란로 123',
      payment_method: '카드'
    },
    {
      id: 2,
      order_number: 'ORD-2024-002',
      customer_name: '이영희',
      customer_phone: '010-9876-5432',
      items: [
        { name: '카푸치노', quantity: 1, price: 5500 },
        { name: '티라떼', quantity: 1, price: 4800 }
      ],
      total_amount: 10300,
      status: 'ready',
      order_time: '2024-01-15T14:15:00',
      estimated_delivery: '2024-01-15T14:45:00',
      delivery_address: '서울시 서초구 서초대로 456',
      payment_method: '현금'
    },
    {
      id: 3,
      order_number: 'ORD-2024-003',
      customer_name: '박민수',
      customer_phone: '010-5555-1234',
      items: [
        { name: '에스프레소', quantity: 1, price: 3500 },
        { name: '아메리카노', quantity: 1, price: 4500 },
        { name: '크로아상', quantity: 2, price: 3500 }
      ],
      total_amount: 15000,
      status: 'completed',
      order_time: '2024-01-15T13:45:00',
      estimated_delivery: '2024-01-15T14:15:00',
      delivery_address: '서울시 마포구 홍대로 789',
      payment_method: '카드'
    }
  ];

  const filteredOrders = orders.filter(order => {
    const matchesSearch = order.order_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         order.customer_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || order.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/50">대기</Badge>;
      case 'preparing':
        return <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/50">준비중</Badge>;
      case 'ready':
        return <Badge className="bg-green-500/20 text-green-400 border-green-500/50">준비완료</Badge>;
      case 'completed':
        return <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/50">완료</Badge>;
      case 'cancelled':
        return <Badge className="bg-red-500/20 text-red-400 border-red-500/50">취소</Badge>;
      default:
        return <Badge className="bg-slate-500/20 text-slate-400 border-slate-500/50">알 수 없음</Badge>;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-400" />;
      case 'preparing':
        return <AlertCircle className="h-4 w-4 text-blue-400" />;
      case 'ready':
        return <CheckCircle className="h-4 w-4 text-green-400" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-emerald-400" />;
      case 'cancelled':
        return <XCircle className="h-4 w-4 text-red-400" />;
      default:
        return <Clock className="h-4 w-4 text-slate-400" />;
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-purple-600 bg-clip-text text-transparent">
            주문 관리
          </h1>
          <p className="text-slate-400 mt-2">실시간 주문 현황 및 관리</p>
        </div>
        <div className="flex items-center gap-4">
          <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/50">
            실시간
          </Badge>
          <Button className="bg-cyan-500/20 text-cyan-400 border-cyan-500/50 hover:bg-cyan-500/30">
            새로고침
          </Button>
        </div>
      </div>

      {/* 필터 및 검색 */}
      <Card className="bg-black/50 border-cyan-500/20 backdrop-blur-xl">
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
              <Input
                placeholder="주문번호 또는 고객명으로 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 bg-slate-800/50 border-slate-600 text-white"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 bg-slate-800/50 border border-slate-600 rounded-md text-white"
            >
              <option value="all">전체 상태</option>
              <option value="pending">대기</option>
              <option value="preparing">준비중</option>
              <option value="ready">준비완료</option>
              <option value="completed">완료</option>
              <option value="cancelled">취소</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* 주문 목록 */}
      <div className="space-y-4">
        {filteredOrders.map((order) => (
          <Card key={order.id} className="bg-black/50 border-slate-500/20 backdrop-blur-xl hover:border-cyan-500/50 transition-all duration-300">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  {getStatusIcon(order.status)}
                  <div>
                    <CardTitle className="text-white">{order.order_number}</CardTitle>
                    <p className="text-sm text-slate-400">
                      {new Date(order.order_time).toLocaleString('ko-KR')}
                    </p>
                  </div>
                </div>
                {getStatusBadge(order.status)}
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* 고객 정보 */}
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2 text-slate-300">
                  <User className="h-4 w-4" />
                  <span>{order.customer_name}</span>
                </div>
                <div className="flex items-center gap-2 text-slate-300">
                  <MapPin className="h-4 w-4" />
                  <span className="text-sm">{order.delivery_address}</span>
                </div>
              </div>

              {/* 주문 상품 */}
              <div className="bg-slate-800/30 rounded-lg p-4">
                <h4 className="text-sm font-medium text-slate-300 mb-2">주문 상품</h4>
                <div className="space-y-2">
                  {order.items.map((item, index) => (
                    <div key={index} className="flex justify-between items-center">
                      <span className="text-sm text-slate-300">
                        {item.name} x {item.quantity}
                      </span>
                      <span className="text-sm text-slate-300">
                        ₩{(item.price * item.quantity).toLocaleString()}
                      </span>
                    </div>
                  ))}
                </div>
                <div className="border-t border-slate-600 mt-3 pt-3 flex justify-between items-center">
                  <span className="font-semibold text-white">총 금액</span>
                  <span className="font-semibold text-emerald-400">
                    ₩{order.total_amount.toLocaleString()}
                  </span>
                </div>
              </div>

              {/* 주문 정보 */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <p className="text-slate-400">결제 방법</p>
                  <p className="text-white">{order.payment_method}</p>
                </div>
                <div>
                  <p className="text-slate-400">예상 배달</p>
                  <p className="text-white">
                    {new Date(order.estimated_delivery).toLocaleTimeString('ko-KR', { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  </p>
                </div>
                <div>
                  <p className="text-slate-400">고객 연락처</p>
                  <p className="text-white">{order.customer_phone}</p>
                </div>
                <div>
                  <p className="text-slate-400">주문 시간</p>
                  <p className="text-white">
                    {new Date(order.order_time).toLocaleTimeString('ko-KR', { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  </p>
                </div>
              </div>

              {/* 액션 버튼 */}
              <div className="flex gap-2">
                {order.status === 'pending' && (
                  <Button size="sm" className="bg-blue-500/20 text-blue-400 border-blue-500/50 hover:bg-blue-500/30">
                    준비 시작
                  </Button>
                )}
                {order.status === 'preparing' && (
                  <Button size="sm" className="bg-green-500/20 text-green-400 border-green-500/50 hover:bg-green-500/30">
                    준비 완료
                  </Button>
                )}
                {order.status === 'ready' && (
                  <Button size="sm" className="bg-emerald-500/20 text-emerald-400 border-emerald-500/50 hover:bg-emerald-500/30">
                    배달 시작
                  </Button>
                )}
                <Button size="sm" variant="outline" className="border-slate-500/50 text-slate-400 hover:bg-slate-500/10">
                  상세 보기
                </Button>
                {order.status === 'pending' && (
                  <Button size="sm" variant="outline" className="border-red-500/50 text-red-400 hover:bg-red-500/10">
                    주문 취소
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredOrders.length === 0 && (
        <Card className="bg-black/50 border-slate-500/20 backdrop-blur-xl">
          <CardContent className="p-12 text-center">
            <Package className="h-12 w-12 text-slate-400 mx-auto mb-4" />
            <p className="text-slate-400">주문이 없습니다.</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
} 
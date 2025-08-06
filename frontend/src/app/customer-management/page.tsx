"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Users, Star, ShoppingCart, TrendingUp, Mail, Phone } from 'lucide-react';
import { toast } from 'sonner';

interface Customer {
  id: number;
  name: string;
  email: string;
  phone: string;
  join_date: string;
  total_orders: number;
  total_spent: number;
  last_order_date: string;
  satisfaction_rating: number;
  status: 'active' | 'inactive' | 'vip';
}

interface CustomerStats {
  totalCustomers: number;
  activeCustomers: number;
  vipCustomers: number;
  averageSatisfaction: number;
  totalRevenue: number;
  averageOrderValue: number;
}

export default function CustomerManagementPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [stats, setStats] = useState<CustomerStats>({
    totalCustomers: 0,
    activeCustomers: 0,
    vipCustomers: 0,
    averageSatisfaction: 0,
    totalRevenue: 0,
    averageOrderValue: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCustomerData();
  }, []);

  const fetchCustomerData = async () => {
    try {
      setLoading(true);
      
      // 샘플 고객 데이터 (실제로는 API에서 가져와야 함)
      const sampleCustomers: Customer[] = [
        {
          id: 1,
          name: '김고객',
          email: 'kim@example.com',
          phone: '010-1234-5678',
          join_date: '2023-01-15',
          total_orders: 25,
          total_spent: 450000,
          last_order_date: '2024-01-15',
          satisfaction_rating: 4.8,
          status: 'vip'
        },
        {
          id: 2,
          name: '이고객',
          email: 'lee@example.com',
          phone: '010-2345-6789',
          join_date: '2023-03-20',
          total_orders: 15,
          total_spent: 280000,
          last_order_date: '2024-01-14',
          satisfaction_rating: 4.5,
          status: 'active'
        },
        {
          id: 3,
          name: '박고객',
          email: 'park@example.com',
          phone: '010-3456-7890',
          join_date: '2023-06-10',
          total_orders: 8,
          total_spent: 120000,
          last_order_date: '2024-01-10',
          satisfaction_rating: 4.2,
          status: 'active'
        },
        {
          id: 4,
          name: '최고객',
          email: 'choi@example.com',
          phone: '010-4567-8901',
          join_date: '2023-09-05',
          total_orders: 3,
          total_spent: 45000,
          last_order_date: '2024-01-05',
          satisfaction_rating: 4.0,
          status: 'inactive'
        },
        {
          id: 5,
          name: '정고객',
          email: 'jung@example.com',
          phone: '010-5678-9012',
          join_date: '2023-12-01',
          total_orders: 12,
          total_spent: 220000,
          last_order_date: '2024-01-12',
          satisfaction_rating: 4.7,
          status: 'vip'
        }
      ];

      setCustomers(sampleCustomers);

      // 통계 계산
      const totalCustomers = sampleCustomers.length;
      const activeCustomers = sampleCustomers.filter(customer => customer.status === 'active').length;
      const vipCustomers = sampleCustomers.filter(customer => customer.status === 'vip').length;
      const averageSatisfaction = sampleCustomers.reduce((sum, customer) => sum + customer.satisfaction_rating, 0) / totalCustomers;
      const totalRevenue = sampleCustomers.reduce((sum, customer) => sum + customer.total_spent, 0);
      const averageOrderValue = totalRevenue / sampleCustomers.reduce((sum, customer) => sum + customer.total_orders, 0);

      setStats({
        totalCustomers,
        activeCustomers,
        vipCustomers,
        averageSatisfaction,
        totalRevenue,
        averageOrderValue
      });

    } catch (error) {
      console.error('고객 데이터 로딩 오류:', error);
      toast.error('데이터를 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-600';
      case 'vip': return 'text-purple-600';
      case 'inactive': return 'text-gray-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return '활성';
      case 'vip': return 'VIP';
      case 'inactive': return '비활성';
      default: return '알 수 없음';
    }
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="text-lg mb-2">로딩 중...</div>
            <div className="text-sm text-gray-500">고객 데이터를 가져오는 중입니다</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">고객 관리</h1>
        <p className="text-gray-600">고객 정보 및 만족도 관리</p>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 고객</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalCustomers}명</div>
            <p className="text-xs text-muted-foreground">활성: {stats.activeCustomers}명</p>
          </CardContent>
        </Card>

        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">VIP 고객</CardTitle>
            <Star className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.vipCustomers}명</div>
            <p className="text-xs text-muted-foreground">프리미엄 고객</p>
          </CardContent>
        </Card>

        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">평균 만족도</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.averageSatisfaction.toFixed(1)}/5.0</div>
            <p className="text-xs text-muted-foreground">고객 만족도</p>
          </CardContent>
        </Card>

        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 매출</CardTitle>
            <ShoppingCart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">₩{stats.totalRevenue.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">고객 총 매출</p>
          </CardContent>
        </Card>
      </div>

      {/* 고객 목록 */}
      <Card className="border border-gray-100">
        <CardHeader>
          <CardTitle>고객 현황</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {customers.map((customer) => (
              <div key={customer.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h4 className="font-semibold text-lg">{customer.name}</h4>
                    <span className={`text-xs px-2 py-1 rounded ${getStatusColor(customer.status)}`}>
                      {getStatusText(customer.status)}
                    </span>
                  </div>
                  <div className="text-right">
                    <div className="flex items-center text-sm text-yellow-600">
                      <Star className="w-4 h-4 mr-1" />
                      {customer.satisfaction_rating}
                    </div>
                  </div>
                </div>
                <div className="space-y-2 text-sm text-gray-600">
                  <div className="flex items-center">
                    <Mail className="w-4 h-4 mr-2" />
                    <span>{customer.email}</span>
                  </div>
                  <div className="flex items-center">
                    <Phone className="w-4 h-4 mr-2" />
                    <span>{customer.phone}</span>
                  </div>
                  <p>가입일: {customer.join_date}</p>
                  <p>총 주문: {customer.total_orders}건</p>
                  <p>총 구매액: ₩{customer.total_spent.toLocaleString()}</p>
                  <p>마지막 주문: {customer.last_order_date}</p>
                </div>
              </div>
            ))}
            {customers.length === 0 && (
              <div className="col-span-full text-center py-8 text-gray-500">
                등록된 고객이 없습니다.
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 
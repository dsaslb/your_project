'use client';

import React, { useState } from 'react';
import { useStores, useEmployees, useOrders, useInventory } from '@/hooks/useDashboard';
import DashboardLayout, { StatCard } from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Store, 
  Users, 
  DollarSign, 
  TrendingUp, 
  Activity,
  Package,
  Calendar,
  AlertTriangle,
  RefreshCw
} from 'lucide-react';

export default function StoreDashboard() {
  const [selectedStoreId, setSelectedStoreId] = useState<number | undefined>(1); // 기본값 설정

  // API 훅 사용
  const { stores, loading: storesLoading, error: storesError, refetch: refetchStores } = useStores(1, 10);
  const { employees, loading: employeesLoading, error: employeesError, refetch: refetchEmployees } = useEmployees(1, 10, '', '', selectedStoreId);
  const { orders, loading: ordersLoading, error: ordersError, refetch: refetchOrders } = useOrders(1, 10, '', '', selectedStoreId);
  const { inventory, loading: inventoryLoading, error: inventoryError, refetch: refetchInventory } = useInventory(1, 10, '', '', selectedStoreId);

  const loading = storesLoading || employeesLoading || ordersLoading || inventoryLoading;
  const error = storesError || employeesError || ordersError || inventoryError;

  // 통계 데이터
  const stats = [
    {
      label: '총 매출',
      value: `₩${orders.reduce((total, order) => total + (order.total_amount || 0), 0).toLocaleString()}`,
      icon: <DollarSign className="w-4 h-4" />,
      color: 'text-emerald-400',
      trend: '+12.5%',
      trendValue: '지난달 대비'
    },
    {
      label: '직원 수',
      value: `${employees.length}명`,
      icon: <Users className="w-4 h-4" />,
      color: 'text-purple-400',
      trend: '+2명',
      trendValue: '이번 주'
    },
    {
      label: '주문 수',
      value: `${orders.length}건`,
      icon: <Package className="w-4 h-4" />,
      color: 'text-blue-400',
      trend: '오늘 기준',
      trendValue: ''
    },
    {
      label: '재고 알림',
      value: `${inventory.filter(item => (item.quantity || 0) < (item.min_quantity || 0)).length}건`,
      icon: <AlertTriangle className="w-4 h-4" />,
      color: 'text-orange-400',
      trend: '발주 필요',
      trendValue: ''
    }
  ];

  const actions = [
    {
      label: '새로고침',
      icon: <RefreshCw className="w-4 h-4" />,
      onClick: () => {
        refetchStores();
        refetchEmployees();
        refetchOrders();
        refetchInventory();
      }
    }
  ];

  const handleRefresh = () => {
    refetchStores();
    refetchEmployees();
    refetchOrders();
    refetchInventory();
  };

  return (
    <DashboardLayout
      title="매장 대시보드"
      subtitle="매장 운영 현황 및 관리"
      icon={<Store className="w-6 h-6" />}
      stats={stats}
      actions={actions}
      onRefresh={handleRefresh}
      loading={loading}
    >
      {/* 메인 콘텐츠 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 실시간 활동 */}
        <Card className="bg-black/50 border-cyan-500/20 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="text-cyan-400 flex items-center gap-2">
              <Activity className="h-5 w-5" />
              실시간 활동
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {orders.slice(0, 5).map((order, index) => (
              <div key={order.id || index} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
                  <span className="text-sm text-slate-300">주문 #{order.id}</span>
                </div>
                <span className="text-sm text-slate-400">₩{order.total_amount?.toLocaleString()}</span>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* 직원 현황 */}
        <Card className="bg-black/50 border-purple-500/20 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="text-purple-400 flex items-center gap-2">
              <Users className="h-5 w-5" />
              직원 현황
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {employees.slice(0, 5).map((employee, index) => (
              <div key={employee.id || index} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center">
                    <span className="text-sm font-medium text-white">
                      {employee.name?.charAt(0) || 'U'}
                    </span>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-300">{employee.name}</p>
                    <p className="text-xs text-slate-400">{employee.position}</p>
                  </div>
                </div>
                <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/50">
                  근무 중
                </Badge>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* 재고 현황 */}
      <Card className="bg-black/50 border-orange-500/20 backdrop-blur-xl">
        <CardHeader>
          <CardTitle className="text-orange-400 flex items-center gap-2">
            <Package className="h-5 w-5" />
            재고 현황
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {inventory.slice(0, 6).map((item, index) => (
              <div key={item.id || index} className="p-4 bg-slate-800/50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-sm font-medium text-slate-300">{item.name}</h4>
                  <Badge 
                    className={
                      (item.quantity || 0) < (item.min_quantity || 0) 
                        ? 'bg-red-500/20 text-red-400 border-red-500/50'
                        : 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50'
                    }
                  >
                    {item.quantity}/{item.max_quantity}
                  </Badge>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-cyan-400 to-purple-600 h-2 rounded-full transition-all duration-300"
                    style={{ 
                      width: `${Math.min(100, ((item.quantity || 0) / (item.max_quantity || 1)) * 100)}%` 
                    }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </DashboardLayout>
  );
} 
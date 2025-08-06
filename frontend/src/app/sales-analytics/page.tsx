"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart3, TrendingUp, DollarSign, Target, Users, Calendar } from 'lucide-react';
import { toast } from 'sonner';

interface SalesData {
  id: number;
  date: string;
  revenue: number;
  orders: number;
  customers: number;
  average_order: number;
  category: string;
}

interface SalesStats {
  totalRevenue: number;
  totalOrders: number;
  totalCustomers: number;
  averageOrderValue: number;
  growthRate: number;
  targetAchievement: number;
  monthlyRevenue: number;
  weeklyRevenue: number;
}

export default function SalesAnalyticsPage() {
  const [salesData, setSalesData] = useState<SalesData[]>([]);
  const [stats, setStats] = useState<SalesStats>({
    totalRevenue: 0,
    totalOrders: 0,
    totalCustomers: 0,
    averageOrderValue: 0,
    growthRate: 0,
    targetAchievement: 0,
    monthlyRevenue: 0,
    weeklyRevenue: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSalesData();
  }, []);

  const fetchSalesData = async () => {
    try {
      setLoading(true);
      
      // 샘플 매출 데이터 (실제로는 API에서 가져와야 함)
      const sampleSalesData: SalesData[] = [
        {
          id: 1,
          date: '2024-01-15',
          revenue: 1250000,
          orders: 45,
          customers: 38,
          average_order: 27778,
          category: '음료'
        },
        {
          id: 2,
          date: '2024-01-14',
          revenue: 980000,
          orders: 32,
          customers: 28,
          average_order: 30625,
          category: '음료'
        },
        {
          id: 3,
          date: '2024-01-13',
          revenue: 1450000,
          orders: 52,
          customers: 45,
          average_order: 27885,
          category: '음료'
        },
        {
          id: 4,
          date: '2024-01-12',
          revenue: 890000,
          orders: 28,
          customers: 25,
          average_order: 31786,
          category: '음료'
        },
        {
          id: 5,
          date: '2024-01-11',
          revenue: 1120000,
          orders: 38,
          customers: 32,
          average_order: 29474,
          category: '음료'
        }
      ];

      setSalesData(sampleSalesData);

      // 통계 계산
      const totalRevenue = sampleSalesData.reduce((sum, data) => sum + data.revenue, 0);
      const totalOrders = sampleSalesData.reduce((sum, data) => sum + data.orders, 0);
      const totalCustomers = sampleSalesData.reduce((sum, data) => sum + data.customers, 0);
      const averageOrderValue = totalOrders > 0 ? totalRevenue / totalOrders : 0;
      const growthRate = 12.5; // 샘플 데이터
      const targetAchievement = 85; // 샘플 데이터
      const monthlyRevenue = totalRevenue * 6; // 샘플 데이터 (6일치 기준)
      const weeklyRevenue = totalRevenue; // 샘플 데이터 (5일치 기준)

      setStats({
        totalRevenue,
        totalOrders,
        totalCustomers,
        averageOrderValue,
        growthRate,
        targetAchievement,
        monthlyRevenue,
        weeklyRevenue
      });

    } catch (error) {
      console.error('매출 데이터 로딩 오류:', error);
      toast.error('데이터를 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="text-lg mb-2">로딩 중...</div>
            <div className="text-sm text-gray-500">매출 데이터를 가져오는 중입니다</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">매출 분석</h1>
        <p className="text-gray-600">매출 및 성과 분석</p>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 매출</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">₩{stats.totalRevenue.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">이번 주 총 매출</p>
          </CardContent>
        </Card>

        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 주문</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalOrders}건</div>
            <p className="text-xs text-muted-foreground">이번 주 주문</p>
          </CardContent>
        </Card>

        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">성장률</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">+{stats.growthRate}%</div>
            <p className="text-xs text-muted-foreground">전주 대비</p>
          </CardContent>
        </Card>

        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">목표 달성</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.targetAchievement}%</div>
            <p className="text-xs text-muted-foreground">월 목표 달성률</p>
          </CardContent>
        </Card>
      </div>

      {/* 추가 통계 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">평균 주문액</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
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
            <p className="text-xs text-muted-foreground">이번 주 고객</p>
          </CardContent>
        </Card>

        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">월 매출 예상</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">₩{stats.monthlyRevenue.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">이번 달 예상</p>
          </CardContent>
        </Card>
      </div>

      {/* 매출 상세 */}
      <Card className="border border-gray-100">
        <CardHeader>
          <CardTitle>일별 매출 현황</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {salesData.map((data) => (
              <div key={data.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h4 className="font-semibold text-lg">{data.date}</h4>
                    <p className="text-sm text-gray-600">카테고리: {data.category}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold">₩{data.revenue.toLocaleString()}</p>
                    <p className="text-sm text-gray-600">{data.orders}건 주문</p>
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-4 text-sm text-gray-600">
                  <div>
                    <p className="font-medium">고객 수</p>
                    <p>{data.customers}명</p>
                  </div>
                  <div>
                    <p className="font-medium">평균 주문액</p>
                    <p>₩{data.average_order.toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="font-medium">주문당 고객</p>
                    <p>{(data.orders / data.customers).toFixed(1)}건</p>
                  </div>
                </div>
              </div>
            ))}
            {salesData.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                매출 데이터가 없습니다.
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 
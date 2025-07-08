"use client";
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Building2, 
  Store, 
  Users, 
  BarChart3, 
  Settings, 
  Bell,
  TrendingUp,
  CheckCircle,
  Clock,
  MapPin,
  DollarSign,
  AlertTriangle,
  ShoppingCart,
  Star,
  Target,
  Award,
  Calendar,
  AlertCircle,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react';
import useUserStore from '@/store/useUserStore';
import { useRouter } from 'next/navigation';

interface StoreData {
  id: number;
  name: string;
  location: string;
  status: 'active' | 'inactive' | 'maintenance';
  revenue: number;
  orders: number;
  customers: number;
  rating: number;
  staff: number;
  growth: number;
  lastUpdated: string;
}

interface BrandMetrics {
  totalStores: number;
  totalRevenue: number;
  totalOrders: number;
  totalCustomers: number;
  averageRating: number;
  totalStaff: number;
  monthlyGrowth: number;
  topPerformingStore: string;
}

export default function BrandAdminDashboard() {
  const { user, isBrandManager } = useUserStore();
  const router = useRouter();
  const [stores, setStores] = useState<StoreData[]>([
    {
      id: 1,
      name: "강남점",
      location: "서울시 강남구",
      status: 'active',
      revenue: 12500000,
      orders: 1247,
      customers: 892,
      rating: 4.8,
      staff: 15,
      growth: 12.5,
      lastUpdated: "2024-01-15"
    },
    {
      id: 2,
      name: "홍대점",
      location: "서울시 마포구",
      status: 'active',
      revenue: 9800000,
      orders: 987,
      customers: 654,
      rating: 4.6,
      staff: 12,
      growth: 8.3,
      lastUpdated: "2024-01-15"
    },
    {
      id: 3,
      name: "부산점",
      location: "부산시 해운대구",
      status: 'active',
      revenue: 11200000,
      orders: 1156,
      customers: 789,
      rating: 4.7,
      staff: 14,
      growth: 15.2,
      lastUpdated: "2024-01-15"
    },
    {
      id: 4,
      name: "대구점",
      location: "대구시 중구",
      status: 'maintenance',
      revenue: 7500000,
      orders: 654,
      customers: 432,
      rating: 4.4,
      staff: 10,
      growth: -2.1,
      lastUpdated: "2024-01-15"
    },
    {
      id: 5,
      name: "인천점",
      location: "인천시 연수구",
      status: 'active',
      revenue: 8900000,
      orders: 876,
      customers: 567,
      rating: 4.5,
      staff: 11,
      growth: 6.8,
      lastUpdated: "2024-01-15"
    }
  ]);

  const [brandMetrics, setBrandMetrics] = useState<BrandMetrics>({
    totalStores: 5,
    totalRevenue: 49900000,
    totalOrders: 4920,
    totalCustomers: 3334,
    averageRating: 4.6,
    totalStaff: 62,
    monthlyGrowth: 8.1,
    topPerformingStore: "강남점"
  });

  // 권한 확인
  if (!user || !isBrandManager()) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="w-96">
          <CardHeader>
            <CardTitle className="text-red-600">접근 권한 없음</CardTitle>
            <CardDescription>
              브랜드 관리자 권한이 필요합니다.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => router.push('/dashboard')}>
              대시보드로 돌아가기
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500';
      case 'inactive': return 'bg-red-500';
      case 'maintenance': return 'bg-yellow-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return '운영중';
      case 'inactive': return '휴점';
      case 'maintenance': return '점검중';
      default: return '알 수 없음';
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW'
    }).format(amount);
  };

  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">브랜드 관리자 대시보드</h1>
          <p className="text-gray-600 dark:text-gray-400">전체 매장 현황 및 브랜드 성과 관리</p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline">
            <Calendar className="h-4 w-4 mr-2" />
            월간 리포트
          </Button>
          <Button>
            <BarChart3 className="h-4 w-4 mr-2" />
            상세 분석
          </Button>
        </div>
      </div>

      {/* 브랜드 전체 통계 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 매장 수</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{brandMetrics.totalStores}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-600">+2</span> 이번 달 신규 오픈
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 매출</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(brandMetrics.totalRevenue)}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-600">+{brandMetrics.monthlyGrowth}%</span> 전월 대비
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 주문 수</CardTitle>
            <ShoppingCart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{brandMetrics.totalOrders.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-600">+15.2%</span> 전월 대비
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">평균 평점</CardTitle>
            <Star className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{brandMetrics.averageRating}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-600">+0.2</span> 전월 대비
            </p>
          </CardContent>
        </Card>
      </div>

      {/* 매장별 상세 정보 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Building2 className="h-5 w-5 mr-2" />
            매장별 현황
          </CardTitle>
          <CardDescription>각 매장의 실시간 성과 및 운영 상태</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {stores.map((store) => (
              <div key={store.id} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <div className={`w-3 h-3 rounded-full ${getStatusColor(store.status)}`} />
                    <span className="font-medium">{store.name}</span>
                  </div>
                  <div className="flex items-center space-x-1 text-sm text-muted-foreground">
                    <MapPin className="h-3 w-3" />
                    <span>{store.location}</span>
                  </div>
                  <Badge variant={store.status === 'active' ? 'default' : 'secondary'}>
                    {getStatusText(store.status)}
                  </Badge>
                </div>
                
                <div className="flex items-center space-x-6">
                  <div className="text-right">
                    <p className="text-sm font-medium">{formatCurrency(store.revenue)}</p>
                    <p className="text-xs text-muted-foreground">월 매출</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium">{store.orders.toLocaleString()}</p>
                    <p className="text-xs text-muted-foreground">주문 수</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium">{store.rating}</p>
                    <p className="text-xs text-muted-foreground">평점</p>
                  </div>
                  <div className="text-right">
                    <div className="flex items-center space-x-1">
                      {store.growth > 0 ? (
                        <ArrowUpRight className="h-3 w-3 text-green-500" />
                      ) : (
                        <ArrowDownRight className="h-3 w-3 text-red-500" />
                      )}
                      <span className={`text-sm font-medium ${store.growth > 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {store.growth > 0 ? '+' : ''}{store.growth}%
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground">성장률</p>
                  </div>
                  <Button variant="outline" size="sm">
                    상세보기
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 성과 분석 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <TrendingUp className="h-5 w-5 mr-2" />
              매장별 성과 비교
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stores
                .sort((a, b) => b.revenue - a.revenue)
                .map((store, index) => (
                  <div key={store.id} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                        index === 0 ? 'bg-yellow-100 text-yellow-800' :
                        index === 1 ? 'bg-gray-100 text-gray-800' :
                        index === 2 ? 'bg-orange-100 text-orange-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {index + 1}
                      </div>
                      <div>
                        <p className="font-medium">{store.name}</p>
                        <p className="text-sm text-muted-foreground">{store.location}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">{formatCurrency(store.revenue)}</p>
                      <p className="text-sm text-muted-foreground">{store.orders} 주문</p>
                    </div>
                  </div>
                ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Target className="h-5 w-5 mr-2" />
              목표 달성 현황
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm">매출 목표 달성률</span>
                <span className="font-medium">87%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-blue-600 h-2 rounded-full" style={{ width: '87%' }}></div>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm">고객 만족도 목표</span>
                <span className="font-medium">92%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-600 h-2 rounded-full" style={{ width: '92%' }}></div>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm">직원 만족도 목표</span>
                <span className="font-medium">78%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-yellow-600 h-2 rounded-full" style={{ width: '78%' }}></div>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm">신규 고객 유치 목표</span>
                <span className="font-medium">105%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-purple-600 h-2 rounded-full" style={{ width: '100%' }}></div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 알림 및 이슈 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <AlertCircle className="h-5 w-5 mr-2" />
            브랜드 알림
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center space-x-3 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
              <AlertCircle className="h-4 w-4 text-yellow-600" />
              <div>
                <p className="font-medium">대구점 점검 완료</p>
                <p className="text-sm text-muted-foreground">시스템 점검이 완료되어 정상 운영을 재개합니다.</p>
              </div>
            </div>
            <div className="flex items-center space-x-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <div>
                <p className="font-medium">강남점 목표 달성</p>
                <p className="text-sm text-muted-foreground">이번 달 매출 목표를 120% 달성했습니다.</p>
              </div>
            </div>
            <div className="flex items-center space-x-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <Award className="h-4 w-4 text-blue-600" />
              <div>
                <p className="font-medium">브랜드 인증 획득</p>
                <p className="text-sm text-muted-foreground">우수 브랜드 인증을 새로 획득했습니다.</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 
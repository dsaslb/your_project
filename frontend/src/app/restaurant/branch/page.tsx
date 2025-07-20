'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Building2, 
  Users, 
  TrendingUp, 
  DollarSign, 
  ShoppingCart,
  ArrowLeft,
  Home,
  Clock,
  AlertTriangle,
  Package,
  Calendar,
  Target,
  Activity
} from 'lucide-react';
import Link from 'next/link';

interface Branch {
  id: number;
  name: string;
  brand_name: string;
  location: string;
  today_revenue: number;
  staff_count: number;
  today_orders: number;
  avg_order_value: number;
}

interface Staff {
  id: number;
  name: string;
  position: string;
  branch_name: string;
  brand_name: string;
  today_orders: number;
  today_revenue: number;
  avg_order_value: number;
}

interface Order {
  id: number;
  order_number: string;
  customer_name: string;
  total_amount: number;
  status: string;
  created_at: string;
  items: OrderItem[];
}

interface OrderItem {
  name: string;
  quantity: number;
  price: number;
}

export default function BranchManagerPage() {
  const [branches, setBranches] = useState<Branch[]>([]);
  const [staff, setStaff] = useState<Staff[]>([]);
  const [selectedBranch, setSelectedBranch] = useState<Branch | null>(null);
  const [recentOrders, setRecentOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // 매장 데이터 로드
      const branchesResponse = await fetch('/api/admin/restaurant/industry/branches');
      const branchesData = await branchesResponse.json();
      setBranches(branchesData);

      // 직원 데이터 로드
      const staffResponse = await fetch('/api/admin/restaurant/industry/staff');
      const staffData = await staffResponse.json();
      setStaff(staffData);

      // 최근 주문 데이터 (샘플)
      const sampleOrders: Order[] = [
        {
          id: 1,
          order_number: "#001",
          customer_name: "김철수",
          total_amount: 25000,
          status: "준비중",
          created_at: "2024-01-15T14:30:00",
          items: [
            { name: "아메리카노", quantity: 2, price: 4500 },
            { name: "카페라떼", quantity: 1, price: 5000 },
            { name: "티라떼", quantity: 1, price: 5500 }
          ]
        },
        {
          id: 2,
          order_number: "#002",
          customer_name: "이영희",
          total_amount: 18000,
          status: "완료",
          created_at: "2024-01-15T14:25:00",
          items: [
            { name: "카푸치노", quantity: 1, price: 5000 },
            { name: "에스프레소", quantity: 1, price: 3000 },
            { name: "크로아상", quantity: 2, price: 5000 }
          ]
        }
      ];
      setRecentOrders(sampleOrders);

    } catch (error) {
      console.error('데이터 로드 오류:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW'
    }).format(amount);
  };

  const getStaffByBranch = (branchId: number) => {
    return staff.filter(s => 
      s.branch_name === branches.find(b => b.id === branchId)?.name
    );
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case '준비중': return 'bg-yellow-100 text-yellow-800';
      case '완료': return 'bg-green-100 text-green-800';
      case '취소': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 헤더 */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="text-3xl mr-4">🏢</div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">매장 관리자 대시보드</h1>
                <p className="text-sm text-gray-500">매장별 실시간 현황 및 직원 관리</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/restaurant/hierarchy">
                <Button variant="outline" size="sm">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  계층 관리
                </Button>
              </Link>
              <Link href="/">
                <Button variant="outline" size="sm">
                  <Home className="h-4 w-4 mr-2" />
                  홈으로
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* 브레드크럼 */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center space-x-2 py-3">
            <Link href="/" className="text-gray-500 hover:text-gray-700">
              홈
            </Link>
            <ArrowLeft className="h-4 w-4 text-gray-400" />
            <Link href="/restaurant/hierarchy" className="text-gray-500 hover:text-gray-700">
              레스토랑 계층 관리
            </Link>
            <ArrowLeft className="h-4 w-4 text-gray-400" />
            <span className="text-gray-900 font-medium">매장 관리</span>
          </div>
        </div>
      </nav>

      {/* 메인 콘텐츠 */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* 매장별 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">총 매장 수</CardTitle>
              <Building2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{branches.length}개</div>
              <p className="text-xs text-muted-foreground">
                운영 중인 매장
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">총 직원 수</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{staff.length}명</div>
              <p className="text-xs text-muted-foreground">
                근무 중인 직원
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">오늘 총 매출</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatCurrency(branches.reduce((sum, branch) => sum + branch.today_revenue, 0))}
              </div>
              <p className="text-xs text-muted-foreground">
                전체 매장 합계
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">오늘 총 주문</CardTitle>
              <ShoppingCart className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {branches.reduce((sum, branch) => sum + branch.today_orders, 0)}건
              </div>
              <p className="text-xs text-muted-foreground">
                전체 매장 합계
              </p>
            </CardContent>
          </Card>
        </div>

        {/* 매장 목록 */}
        <div className="bg-white rounded-lg shadow mb-8">
          <div className="px-6 py-4 border-b">
            <h2 className="text-lg font-semibold">매장별 현황</h2>
            <p className="text-sm text-gray-600">각 매장의 실시간 운영 현황</p>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {branches.map((branch) => (
                <Card key={branch.id} className="hover:shadow-lg transition-shadow cursor-pointer"
                      onClick={() => setSelectedBranch(branch)}>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span className="text-lg font-semibold">{branch.name}</span>
                      <Badge variant="outline">{branch.brand_name}</Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="text-sm text-gray-600">{branch.location}</div>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div className="flex items-center gap-1">
                        <DollarSign className="h-4 w-4 text-green-600" />
                        <span className="text-gray-600">오늘 매출:</span>
                      </div>
                      <div className="font-semibold">{formatCurrency(branch.today_revenue)}</div>
                      
                      <div className="flex items-center gap-1">
                        <ShoppingCart className="h-4 w-4 text-blue-600" />
                        <span className="text-gray-600">주문 수:</span>
                      </div>
                      <div className="font-semibold">{branch.today_orders}건</div>
                      
                      <div className="flex items-center gap-1">
                        <Users className="h-4 w-4 text-purple-600" />
                        <span className="text-gray-600">직원 수:</span>
                      </div>
                      <div className="font-semibold">{branch.staff_count}명</div>
                      
                      <div className="flex items-center gap-1">
                        <TrendingUp className="h-4 w-4 text-orange-600" />
                        <span className="text-gray-600">평균 주문:</span>
                      </div>
                      <div className="font-semibold">{formatCurrency(branch.avg_order_value)}</div>
                    </div>
                    
                    <Button className="w-full" variant="outline">
                      직원 보기
                      <ArrowLeft className="h-4 w-4 ml-2" />
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>

        {/* 선택된 매장의 상세 정보 */}
        {selectedBranch && (
          <div className="space-y-6">
            {/* 매장 상세 현황 */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold">
                    {selectedBranch.name} - 상세 현황
                  </h3>
                  <Button variant="ghost" onClick={() => setSelectedBranch(null)}>
                    닫기
                  </Button>
                </div>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* 실시간 주문 현황 */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Clock className="h-5 w-5" />
                        실시간 주문 현황
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {recentOrders.map((order) => (
                          <div key={order.id} className="border rounded-lg p-3">
                            <div className="flex items-center justify-between mb-2">
                              <span className="font-medium">{order.order_number}</span>
                              <Badge className={getStatusColor(order.status)}>
                                {order.status}
                              </Badge>
                            </div>
                            <div className="text-sm text-gray-600 mb-2">
                              {order.customer_name} • {formatCurrency(order.total_amount)}
                            </div>
                            <div className="text-xs text-gray-500">
                              {new Date(order.created_at).toLocaleTimeString()}
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  {/* 직원 현황 */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Users className="h-5 w-5" />
                        직원 현황
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {getStaffByBranch(selectedBranch.id).map((staffMember) => (
                          <div key={staffMember.id} className="border rounded-lg p-3">
                            <div className="flex items-center justify-between mb-2">
                              <span className="font-medium">{staffMember.name}</span>
                              <Badge variant="secondary">{staffMember.position}</Badge>
                            </div>
                            <div className="text-sm text-gray-600">
                              오늘 주문: {staffMember.today_orders}건 • 
                              매출: {formatCurrency(staffMember.today_revenue)}
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </div>

            {/* 재고 알림 */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b">
                <h3 className="text-lg font-semibold flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-orange-500" />
                  재고 부족 알림
                </h3>
              </div>
              <div className="p-6">
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <Package className="h-5 w-5 text-orange-500" />
                      <div>
                        <div className="font-medium">토마토 소스</div>
                        <div className="text-sm text-gray-600">현재 재고: 2개</div>
                      </div>
                    </div>
                    <Button size="sm" variant="outline">발주하기</Button>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <Package className="h-5 w-5 text-orange-500" />
                      <div>
                        <div className="font-medium">우유</div>
                        <div className="text-sm text-gray-600">현재 재고: 5개</div>
                      </div>
                    </div>
                    <Button size="sm" variant="outline">발주하기</Button>
                  </div>
                </div>
              </div>
            </div>

            {/* 빠른 액션 */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b">
                <h3 className="text-lg font-semibold">빠른 액션</h3>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <Button variant="outline" className="flex flex-col items-center p-4 h-auto">
                    <ShoppingCart className="h-6 w-6 mb-2" />
                    <span className="text-sm">새 주문</span>
                  </Button>
                  <Button variant="outline" className="flex flex-col items-center p-4 h-auto">
                    <Package className="h-6 w-6 mb-2" />
                    <span className="text-sm">재고 발주</span>
                  </Button>
                  <Button variant="outline" className="flex flex-col items-center p-4 h-auto">
                    <Users className="h-6 w-6 mb-2" />
                    <span className="text-sm">직원 관리</span>
                  </Button>
                  <Button variant="outline" className="flex flex-col items-center p-4 h-auto">
                    <Activity className="h-6 w-6 mb-2" />
                    <span className="text-sm">성과 분석</span>
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 매장 성과 분석 */}
        <div className="bg-white rounded-lg shadow mb-8">
          <div className="px-6 py-4 border-b">
            <h3 className="text-lg font-semibold">매장 성과 분석</h3>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <DollarSign className="h-5 w-5" />
                    매출 순위
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {branches
                      .sort((a, b) => b.today_revenue - a.today_revenue)
                      .slice(0, 5)
                      .map((branch, index) => (
                        <div key={branch.id} className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Badge variant={index === 0 ? "default" : "secondary"}>
                              {index + 1}
                            </Badge>
                            <span className="font-medium">{branch.name}</span>
                          </div>
                          <span className="text-sm font-semibold">
                            {formatCurrency(branch.today_revenue)}
                          </span>
                        </div>
                      ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <ShoppingCart className="h-5 w-5" />
                    주문 순위
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {branches
                      .sort((a, b) => b.today_orders - a.today_orders)
                      .slice(0, 5)
                      .map((branch, index) => (
                        <div key={branch.id} className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Badge variant={index === 0 ? "default" : "secondary"}>
                              {index + 1}
                            </Badge>
                            <span className="font-medium">{branch.name}</span>
                          </div>
                          <span className="text-sm font-semibold">
                            {branch.today_orders}건
                          </span>
                        </div>
                      ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="h-5 w-5" />
                    효율성 순위
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {branches
                      .sort((a, b) => b.avg_order_value - a.avg_order_value)
                      .slice(0, 5)
                      .map((branch, index) => (
                        <div key={branch.id} className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Badge variant={index === 0 ? "default" : "secondary"}>
                              {index + 1}
                            </Badge>
                            <span className="font-medium">{branch.name}</span>
                          </div>
                          <span className="text-sm font-semibold">
                            {formatCurrency(branch.avg_order_value)}
                          </span>
                        </div>
                      ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
} 
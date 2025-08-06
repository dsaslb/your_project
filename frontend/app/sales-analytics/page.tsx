'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../src/components/ui/card';
import { Button } from '../../src/components/ui/button';
import { Input } from '../../src/components/ui/input';
import { Badge } from '../../src/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '../../src/components/ui/dialog';
import { Label } from '../../src/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../src/components/ui/select';
import { apiClient } from '../../src/lib/api-client';
import { useLoadingState } from '../../src/hooks/useLoadingState';
import { useErrorHandler } from '../../src/hooks/useErrorHandler';
import { toast } from 'sonner';
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  ShoppingCart, 
  Users, 
  Store, 
  Calendar,
  BarChart3,
  PieChart,
  Download,
  Filter,
  RefreshCw,
  Eye,
  Target,
  Award,
  AlertTriangle
} from 'lucide-react';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart as RechartsPieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface SalesData {
  id: number;
  date: string;
  store_id: number;
  store_name: string;
  total_amount: number;
  order_count: number;
  customer_count: number;
  average_order_value: number;
  payment_method: 'cash' | 'card' | 'mobile' | 'online';
  category: string;
  created_at: string;
}

interface StoreType {
  id: number;
  name: string;
  address: string;
}

interface SalesSummary {
  total_revenue: number;
  total_orders: number;
  total_customers: number;
  average_order_value: number;
  growth_rate: number;
  top_performing_store: string;
  top_category: string;
}



export default function SalesAnalytics() {
  const [salesData, setSalesData] = useState<SalesData[]>([]);
  const [stores, setStores] = useState<StoreType[]>([]);
  const [summary, setSummary] = useState<SalesSummary>({
    total_revenue: 0,
    total_orders: 0,
    total_customers: 0,
    average_order_value: 0,
    growth_rate: 0,
    top_performing_store: '',
    top_category: ''
  });
  
  const [selectedPeriod, setSelectedPeriod] = useState<string>('month');
  const [selectedStore, setSelectedStore] = useState<string>('all');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  
  const { handleError } = useErrorHandler();

  // 매출 데이터 조회
  const fetchSalesData = async () => {
    try {
      setIsLoading(true);
      const response = await apiClient.get('/api/sales');
      if (response.success && response.data) {
        setSalesData(response.data);
        calculateSummary(response.data);
      }
    } catch (error) {
      handleError(error as Error);
    } finally {
      setIsLoading(false);
    }
  };

  // 매장 목록 조회
  const fetchStores = async () => {
    try {
      const response = await apiClient.get('/api/stores');
      if (response.success && response.data) {
        setStores(response.data);
      }
    } catch (error) {
      handleError(error as Error);
    }
  };

  // 초기 데이터 로드
  useEffect(() => {
    fetchSalesData();
    fetchStores();
    
    // 기본 날짜 범위 설정 (최근 30일)
    const end = new Date();
    const start = new Date();
    start.setDate(start.getDate() - 30);
    
    setEndDate(end.toISOString().split('T')[0]);
    setStartDate(start.toISOString().split('T')[0]);
  }, []);

  // 매출 요약 계산
  const calculateSummary = (data: SalesData[]) => {
    const totalRevenue = data.reduce((sum, item) => sum + item.total_amount, 0);
    const totalOrders = data.reduce((sum, item) => sum + item.order_count, 0);
    const totalCustomers = data.reduce((sum, item) => sum + item.customer_count, 0);
    const averageOrderValue = totalOrders > 0 ? totalRevenue / totalOrders : 0;
    
    // 성장률 계산 (이전 기간 대비)
    const currentPeriod = data.filter(item => {
      const itemDate = new Date(item.date);
      const start = new Date(startDate);
      const end = new Date(endDate);
      return itemDate >= start && itemDate <= end;
    });
    
    const previousPeriod = data.filter(item => {
      const itemDate = new Date(item.date);
      const start = new Date(startDate);
      const end = new Date(endDate);
      const periodLength = end.getTime() - start.getTime();
      const previousStart = new Date(start.getTime() - periodLength);
      const previousEnd = new Date(start);
      return itemDate >= previousStart && itemDate < previousEnd;
    });
    
    const currentRevenue = currentPeriod.reduce((sum, item) => sum + item.total_amount, 0);
    const previousRevenue = previousPeriod.reduce((sum, item) => sum + item.total_amount, 0);
    const growthRate = previousRevenue > 0 ? ((currentRevenue - previousRevenue) / previousRevenue) * 100 : 0;
    
    // 최고 성과 매장
    const storePerformance = data.reduce((acc, item) => {
      acc[item.store_name] = (acc[item.store_name] || 0) + item.total_amount;
      return acc;
    }, {} as Record<string, number>);
    
    const topStore = Object.entries(storePerformance)
      .sort(([,a], [,b]) => b - a)[0]?.[0] || '';
    
    // 최고 카테고리
    const categoryPerformance = data.reduce((acc, item) => {
      acc[item.category] = (acc[item.category] || 0) + item.total_amount;
      return acc;
    }, {} as Record<string, number>);
    
    const topCategory = Object.entries(categoryPerformance)
      .sort(([,a], [,b]) => b - a)[0]?.[0] || '';
    
    setSummary({
      total_revenue: totalRevenue,
      total_orders: totalOrders,
      total_customers: totalCustomers,
      average_order_value: averageOrderValue,
      growth_rate: growthRate,
      top_performing_store: topStore,
      top_category: topCategory
    });
  };

  // 필터링된 매출 데이터
  const filteredSalesData = salesData.filter(item => {
    const matchesStore = selectedStore === 'all' || item.store_id.toString() === selectedStore;
    const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory;
    
    const itemDate = new Date(item.date);
    const start = startDate ? new Date(startDate) : null;
    const end = endDate ? new Date(endDate) : null;
    
    const matchesDate = (!start || itemDate >= start) && (!end || itemDate <= end);
    
    return matchesStore && matchesCategory && matchesDate;
  });

  // 차트 데이터 생성
  const generateChartData = () => {
    const dailyData = filteredSalesData.reduce((acc, item) => {
      const date = new Date(item.date).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' });
      acc[date] = (acc[date] || 0) + item.total_amount;
      return acc;
    }, {} as Record<string, number>);

    const sortedDates = Object.keys(dailyData).sort((a, b) => {
      return new Date(a).getTime() - new Date(b).getTime();
    });

    return sortedDates.map(date => ({
      date,
      revenue: dailyData[date]
    }));
  };

  // 카테고리별 매출 데이터
  const generateCategoryData = () => {
    const categoryData = filteredSalesData.reduce((acc, item) => {
      acc[item.category] = (acc[item.category] || 0) + item.total_amount;
      return acc;
    }, {} as Record<string, number>);

    return Object.entries(categoryData).map(([name, value]) => ({
      name,
      value
    }));
  };

  // 매장별 매출 데이터
  const generateStoreData = () => {
    const storeData = filteredSalesData.reduce((acc, item) => {
      acc[item.store_name] = (acc[item.store_name] || 0) + item.total_amount;
      return acc;
    }, {} as Record<string, number>);

    return Object.entries(storeData).map(([name, revenue]) => ({
      name,
      revenue
    }));
  };

  // 리포트 다운로드
  const handleDownloadReport = () => {
    const csvContent = [
      ['날짜', '매장', '총 매출', '주문 수', '고객 수', '평균 주문 금액', '결제 방법', '카테고리'],
      ...filteredSalesData.map(item => [
        item.date,
        item.store_name,
        item.total_amount.toLocaleString(),
        item.order_count,
        item.customer_count,
        item.average_order_value.toLocaleString(),
        item.payment_method,
        item.category
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `sales_report_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // 성장률 색상
  const getGrowthColor = (rate: number) => {
    if (rate > 0) return 'text-green-600';
    if (rate < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  // 성장률 아이콘
  const getGrowthIcon = (rate: number) => {
    if (rate > 0) return <TrendingUp className="h-4 w-4" />;
    if (rate < 0) return <TrendingDown className="h-4 w-4" />;
    return <Target className="h-4 w-4" />;
  };

  // 차트 색상
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <BarChart3 className="h-8 w-8 text-blue-600" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">매출 분석</h1>
            <p className="text-gray-600">매출 데이터를 분석하고 인사이트를 도출하세요</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={fetchSalesData} disabled={isLoading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            새로고침
          </Button>
          <Button onClick={handleDownloadReport} className="bg-green-600 hover:bg-green-700">
            <Download className="h-4 w-4 mr-2" />
            리포트 다운로드
          </Button>
        </div>
      </div>

      {/* 필터 */}
      <Card>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
            <div>
              <Label>기간</Label>
              <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="week">이번 주</SelectItem>
                  <SelectItem value="month">이번 달</SelectItem>
                  <SelectItem value="quarter">이번 분기</SelectItem>
                  <SelectItem value="year">이번 년도</SelectItem>
                  <SelectItem value="custom">사용자 정의</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label>시작일</Label>
              <Input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>
            
            <div>
              <Label>종료일</Label>
              <Input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
            
            <div>
              <Label>매장</Label>
              <Select value={selectedStore} onValueChange={setSelectedStore}>
                <SelectTrigger>
                  <SelectValue placeholder="전체 매장" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">전체 매장</SelectItem>
                  {stores.map(store => (
                    <SelectItem key={store.id} value={store.id.toString()}>
                      {store.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label>카테고리</Label>
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger>
                  <SelectValue placeholder="전체 카테고리" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">전체 카테고리</SelectItem>
                  <SelectItem value="음식">음식</SelectItem>
                  <SelectItem value="음료">음료</SelectItem>
                  <SelectItem value="디저트">디저트</SelectItem>
                  <SelectItem value="기타">기타</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="flex items-end">
              <Button variant="outline" onClick={() => {
                setSelectedPeriod('month');
                setSelectedStore('all');
                setSelectedCategory('all');
                const end = new Date();
                const start = new Date();
                start.setDate(start.getDate() - 30);
                setEndDate(end.toISOString().split('T')[0]);
                setStartDate(start.toISOString().split('T')[0]);
              }}>
                <Filter className="h-4 w-4 mr-2" />
                초기화
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 주요 지표 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <DollarSign className="h-8 w-8 text-green-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">총 매출</p>
                <p className="text-2xl font-bold text-gray-900">₩{summary.total_revenue.toLocaleString()}</p>
                <div className={`flex items-center text-sm ${getGrowthColor(summary.growth_rate)}`}>
                  {getGrowthIcon(summary.growth_rate)}
                  <span className="ml-1">{summary.growth_rate.toFixed(1)}%</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <ShoppingCart className="h-8 w-8 text-blue-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">총 주문</p>
                <p className="text-2xl font-bold text-gray-900">{summary.total_orders.toLocaleString()}</p>
                <p className="text-sm text-gray-500">평균 ₩{summary.average_order_value.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <Users className="h-8 w-8 text-purple-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">총 고객</p>
                <p className="text-2xl font-bold text-gray-900">{summary.total_customers.toLocaleString()}</p>
                <p className="text-sm text-gray-500">고유 고객</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <Award className="h-8 w-8 text-orange-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">최고 매장</p>
                <p className="text-lg font-semibold text-gray-900">{summary.top_performing_store}</p>
                <p className="text-sm text-gray-500">최고 카테고리: {summary.top_category}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 차트 영역 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 매출 트렌드 차트 */}
        <Card>
          <CardHeader>
            <CardTitle>매출 트렌드</CardTitle>
            <CardDescription>일별 매출 추이</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={generateChartData()}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip 
                    formatter={(value: number) => [`₩${value.toLocaleString()}`, '매출']}
                    labelFormatter={(label) => `날짜: ${label}`}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="revenue" 
                    stroke="#3B82F6" 
                    fill="#3B82F6" 
                    fillOpacity={0.3}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* 카테고리별 매출 */}
        <Card>
          <CardHeader>
            <CardTitle>카테고리별 매출</CardTitle>
            <CardDescription>카테고리별 매출 분포</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <RechartsPieChart>
                  <Pie
                    data={generateCategoryData()}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {generateCategoryData().map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(value: number) => [`₩${value.toLocaleString()}`, '매출']}
                  />
                </RechartsPieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 매장별 매출 */}
      <Card>
        <CardHeader>
          <CardTitle>매장별 매출</CardTitle>
          <CardDescription>매장별 매출 비교</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={generateStoreData()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip 
                  formatter={(value: number) => [`₩${value.toLocaleString()}`, '매출']}
                  labelFormatter={(label) => `매장: ${label}`}
                />
                <Bar dataKey="revenue" fill="#22C55E" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* 상세 매출 데이터 */}
      <Card>
        <CardHeader>
          <CardTitle>상세 매출 데이터</CardTitle>
          <CardDescription>
            총 {filteredSalesData.length}건의 매출 데이터
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">날짜</th>
                  <th className="text-left p-2">매장</th>
                  <th className="text-right p-2">총 매출</th>
                  <th className="text-center p-2">주문 수</th>
                  <th className="text-center p-2">고객 수</th>
                  <th className="text-right p-2">평균 주문</th>
                  <th className="text-center p-2">결제 방법</th>
                  <th className="text-center p-2">카테고리</th>
                </tr>
              </thead>
              <tbody>
                {filteredSalesData.slice(0, 20).map((item) => (
                  <tr key={item.id} className="border-b hover:bg-gray-50">
                    <td className="p-2">{new Date(item.date).toLocaleDateString('ko-KR')}</td>
                    <td className="p-2 font-medium">{item.store_name}</td>
                    <td className="p-2 text-right font-semibold">₩{item.total_amount.toLocaleString()}</td>
                    <td className="p-2 text-center">{item.order_count}</td>
                    <td className="p-2 text-center">{item.customer_count}</td>
                    <td className="p-2 text-right">₩{item.average_order_value.toLocaleString()}</td>
                    <td className="p-2 text-center">
                      <Badge variant="outline">
                        {item.payment_method === 'cash' && '현금'}
                        {item.payment_method === 'card' && '카드'}
                        {item.payment_method === 'mobile' && '모바일'}
                        {item.payment_method === 'online' && '온라인'}
                      </Badge>
                    </td>
                    <td className="p-2 text-center">
                      <Badge variant="secondary">{item.category}</Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            {filteredSalesData.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <AlertTriangle className="h-12 w-12 mx-auto mb-2" />
                <p>매출 데이터가 없습니다.</p>
              </div>
            )}
            
            {filteredSalesData.length > 20 && (
              <div className="text-center py-4 text-gray-500">
                <p>총 {filteredSalesData.length}건 중 최근 20건만 표시됩니다.</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 
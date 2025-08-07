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
  
  const { isLoading, setLoading } = useLoadingState();
  const { handleError } = useErrorHandler();

  // 매출 데이터 조회
  const fetchSalesData = async () => {
    try {
      setLoading(true);
      // 임시로 샘플 데이터 사용
      const sampleSalesData: SalesData[] = [
        {
          id: 1,
          date: '2024-01-15',
          store_id: 1,
          store_name: '강남점',
          total_amount: 1250000,
          order_count: 45,
          customer_count: 38,
          average_order_value: 27778,
          payment_method: 'card',
          category: '음료',
          created_at: '2024-01-15T00:00:00Z'
        },
        {
          id: 2,
          date: '2024-01-14',
          store_id: 1,
          store_name: '강남점',
          total_amount: 980000,
          order_count: 32,
          customer_count: 28,
          average_order_value: 30625,
          payment_method: 'card',
          category: '음료',
          created_at: '2024-01-14T00:00:00Z'
        },
        {
          id: 3,
          date: '2024-01-13',
          store_id: 2,
          store_name: '홍대점',
          total_amount: 850000,
          order_count: 28,
          customer_count: 25,
          average_order_value: 30357,
          payment_method: 'mobile',
          category: '음료',
          created_at: '2024-01-13T00:00:00Z'
        },
        {
          id: 4,
          date: '2024-01-12',
          store_id: 2,
          store_name: '홍대점',
          total_amount: 720000,
          order_count: 24,
          customer_count: 22,
          average_order_value: 30000,
          payment_method: 'cash',
          category: '음료',
          created_at: '2024-01-12T00:00:00Z'
        },
        {
          id: 5,
          date: '2024-01-11',
          store_id: 1,
          store_name: '강남점',
          total_amount: 1100000,
          order_count: 40,
          customer_count: 35,
          average_order_value: 27500,
          payment_method: 'card',
          category: '음료',
          created_at: '2024-01-11T00:00:00Z'
        }
      ];
      
      setSalesData(sampleSalesData);
      calculateSummary(sampleSalesData);
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 매장 목록 조회
  const fetchStores = async () => {
    try {
      const sampleStores: StoreType[] = [
        { id: 1, name: '강남점', address: '서울 강남구' },
        { id: 2, name: '홍대점', address: '서울 마포구' },
        { id: 3, name: '명동점', address: '서울 중구' }
      ];
      setStores(sampleStores);
    } catch (error) {
      handleError(error as Error);
    }
  };

  // 요약 계산
  const calculateSummary = (data: SalesData[]) => {
    if (data.length === 0) return;

    const totalRevenue = data.reduce((sum, item) => sum + item.total_amount, 0);
    const totalOrders = data.reduce((sum, item) => sum + item.order_count, 0);
    const totalCustomers = data.reduce((sum, item) => sum + item.customer_count, 0);
    const averageOrderValue = totalOrders > 0 ? totalRevenue / totalOrders : 0;

    // 성장률 계산 (간단한 예시)
    const growthRate = 12.5; // 임시 값

    // 최고 성과 매장
    const storePerformance = data.reduce((acc, item) => {
      acc[item.store_name] = (acc[item.store_name] || 0) + item.total_amount;
      return acc;
    }, {} as Record<string, number>);

    const topStore = Object.entries(storePerformance)
      .sort(([, a], [, b]) => b - a)[0]?.[0] || '';

    // 최고 카테고리
    const categoryPerformance = data.reduce((acc, item) => {
      acc[item.category] = (acc[item.category] || 0) + item.total_amount;
      return acc;
    }, {} as Record<string, number>);

    const topCategory = Object.entries(categoryPerformance)
      .sort(([, a], [, b]) => b - a)[0]?.[0] || '';

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

  // 차트 데이터 생성
  const generateChartData = () => {
    return salesData.map(item => ({
      date: new Date(item.date).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' }),
      매출: item.total_amount,
      주문수: item.order_count,
      고객수: item.customer_count
    }));
  };

  // 카테고리별 데이터
  const generateCategoryData = () => {
    const categoryData = salesData.reduce((acc, item) => {
      acc[item.category] = (acc[item.category] || 0) + item.total_amount;
      return acc;
    }, {} as Record<string, number>);

    return Object.entries(categoryData).map(([name, value]) => ({
      name,
      value
    }));
  };

  // 매장별 데이터
  const generateStoreData = () => {
    const storeData = salesData.reduce((acc, item) => {
      acc[item.store_name] = (acc[item.store_name] || 0) + item.total_amount;
      return acc;
    }, {} as Record<string, number>);

    return Object.entries(storeData).map(([name, value]) => ({
      name,
      value
    }));
  };

  // 리포트 다운로드
  const handleDownloadReport = () => {
    toast.success('리포트 다운로드가 시작되었습니다.');
  };

  // 성장률 색상
  const getGrowthColor = (rate: number) => {
    if (rate > 0) return 'text-green-500';
    if (rate < 0) return 'text-red-500';
    return 'text-gray-500';
  };

  // 성장률 아이콘
  const getGrowthIcon = (rate: number) => {
    if (rate > 0) return <TrendingUp className="h-4 w-4" />;
    if (rate < 0) return <TrendingDown className="h-4 w-4" />;
    return <Target className="h-4 w-4" />;
  };

  // 차트 색상
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

  useEffect(() => {
    fetchSalesData();
    fetchStores();
    
    // 기본 날짜 설정
    const end = new Date();
    const start = new Date();
    start.setDate(start.getDate() - 30);
    setEndDate(end.toISOString().split('T')[0]);
    setStartDate(start.toISOString().split('T')[0]);
  }, []);

  return (
    <div className="min-h-screen p-6">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <BarChart3 className="w-6 h-6" />
          매출 분석
        </h1>
        <p className="text-gray-300 mt-2">매출 데이터를 분석하고 인사이트를 도출하세요</p>
      </div>

      {/* 액션 버튼 */}
      <div className="flex gap-4 mb-8">
        <Button
          onClick={fetchSalesData}
          disabled={isLoading}
          className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          새로고침
        </Button>
        <Button
          onClick={handleDownloadReport}
          className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700"
        >
          <Download className="w-4 h-4 mr-2" />
          리포트 다운로드
        </Button>
      </div>

      {/* 요약 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">총 매출</p>
                <p className="text-2xl font-bold text-white">₩{summary.total_revenue.toLocaleString()}</p>
                <div className="flex items-center gap-1 mt-1">
                  {getGrowthIcon(summary.growth_rate)}
                  <span className={`text-sm ${getGrowthColor(summary.growth_rate)}`}>
                    {summary.growth_rate > 0 ? '+' : ''}{summary.growth_rate}%
                  </span>
                </div>
              </div>
              <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
                <DollarSign className="w-6 h-6 text-green-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">총 주문</p>
                <p className="text-2xl font-bold text-white">{summary.total_orders.toLocaleString()}</p>
                <p className="text-gray-400 text-sm">평균 ₩{summary.average_order_value.toLocaleString()}</p>
              </div>
              <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
                <ShoppingCart className="w-6 h-6 text-blue-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">총 고객</p>
                <p className="text-2xl font-bold text-white">{summary.total_customers.toLocaleString()}</p>
                <p className="text-gray-400 text-sm">고유 고객 수</p>
              </div>
              <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center">
                <Users className="w-6 h-6 text-purple-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">최고 매장</p>
                <p className="text-2xl font-bold text-white">{summary.top_performing_store}</p>
                <p className="text-gray-400 text-sm">최고 성과</p>
              </div>
              <div className="w-12 h-12 bg-orange-500/20 rounded-lg flex items-center justify-center">
                <Award className="w-6 h-6 text-orange-400" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 필터 */}
      <Card className="bg-white/10 backdrop-blur-sm border border-white/20 mb-8">
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
            <div>
              <Label className="text-gray-300 text-sm">기간</Label>
              <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
                <SelectTrigger className="mt-1 bg-white/10 border-white/20 text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-white/10 border-white/20">
                  <SelectItem value="week">이번 주</SelectItem>
                  <SelectItem value="month">이번 달</SelectItem>
                  <SelectItem value="quarter">이번 분기</SelectItem>
                  <SelectItem value="year">이번 년도</SelectItem>
                  <SelectItem value="custom">사용자 정의</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label className="text-gray-300 text-sm">시작일</Label>
              <Input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="mt-1 bg-white/10 border-white/20 text-white"
              />
            </div>
            
            <div>
              <Label className="text-gray-300 text-sm">종료일</Label>
              <Input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="mt-1 bg-white/10 border-white/20 text-white"
              />
            </div>
            
            <div>
              <Label className="text-gray-300 text-sm">매장</Label>
              <Select value={selectedStore} onValueChange={setSelectedStore}>
                <SelectTrigger className="mt-1 bg-white/10 border-white/20 text-white">
                  <SelectValue placeholder="전체 매장" />
                </SelectTrigger>
                <SelectContent className="bg-white/10 border-white/20">
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
              <Label className="text-gray-300 text-sm">카테고리</Label>
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger className="mt-1 bg-white/10 border-white/20 text-white">
                  <SelectValue placeholder="전체 카테고리" />
                </SelectTrigger>
                <SelectContent className="bg-white/10 border-white/20">
                  <SelectItem value="all">전체 카테고리</SelectItem>
                  <SelectItem value="음식">음식</SelectItem>
                  <SelectItem value="음료">음료</SelectItem>
                  <SelectItem value="디저트">디저트</SelectItem>
                  <SelectItem value="기타">기타</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="flex items-end">
              <Button
                variant="outline"
                onClick={() => {
                  setSelectedPeriod('month');
                  setSelectedStore('all');
                  setSelectedCategory('all');
                  const end = new Date();
                  const start = new Date();
                  start.setDate(start.getDate() - 30);
                  setEndDate(end.toISOString().split('T')[0]);
                  setStartDate(start.toISOString().split('T')[0]);
                }}
                className="border-white/20 text-white hover:bg-white/10"
              >
                <Filter className="w-4 h-4 mr-2" />
                초기화
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 차트 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* 매출 트렌드 */}
        <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
          <CardHeader>
            <CardTitle className="text-white">매출 트렌드</CardTitle>
            <CardDescription className="text-gray-300">일별 매출 변화</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={generateChartData()}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="date" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(0, 0, 0, 0.8)', 
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    borderRadius: '8px',
                    color: 'white'
                  }}
                />
                <Legend />
                <Line type="monotone" dataKey="매출" stroke="#10B981" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* 카테고리별 매출 */}
        <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
          <CardHeader>
            <CardTitle className="text-white">카테고리별 매출</CardTitle>
            <CardDescription className="text-gray-300">카테고리별 매출 분포</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
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
                  contentStyle={{ 
                    backgroundColor: 'rgba(0, 0, 0, 0.8)', 
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    borderRadius: '8px',
                    color: 'white'
                  }}
                />
              </RechartsPieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* 매장별 매출 */}
      <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
        <CardHeader>
          <CardTitle className="text-white">매장별 매출</CardTitle>
          <CardDescription className="text-gray-300">매장별 매출 비교</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={generateStoreData()}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'rgba(0, 0, 0, 0.8)', 
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  borderRadius: '8px',
                  color: 'white'
                }}
              />
              <Legend />
              <Bar dataKey="value" fill="#3B82F6" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
} 
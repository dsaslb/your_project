'use client'

import React, { useState, useEffect } from 'react'
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, AreaChart, Area
} from 'recharts'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  TrendingUp, TrendingDown, Users, DollarSign, 
  ShoppingCart, Star, Calendar, Filter, Download,
  Building2, BarChart3, PieChart as PieChartIcon,
  Activity, Target, Award
} from 'lucide-react'

interface BrandAnalytics {
  id: string
  name: string
  totalRevenue: number
  totalOrders: number
  totalCustomers: number
  averageRating: number
  growth: number
  marketShare: number
  stores: number
  monthlyData: Array<{
    month: string
    revenue: number
    orders: number
    customers: number
  }>
  categoryData: Array<{
    name: string
    value: number
    color: string
  }>
  performanceMetrics: {
    customerSatisfaction: number
    orderFulfillment: number
    deliveryTime: number
    returnRate: number
  }
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D']

export default function BrandsAnalyticsPage() {
  const [analytics, setAnalytics] = useState<BrandAnalytics[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedBrand, setSelectedBrand] = useState<string | null>(null)
  const [timeRange, setTimeRange] = useState('30d')
  const [chartType, setChartType] = useState<'revenue' | 'orders' | 'customers'>('revenue')

  useEffect(() => {
    loadAnalytics()
  }, [timeRange])

  const loadAnalytics = async () => {
    try {
      setLoading(true)
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'
      const response = await fetch(`${apiUrl}/api/brands/analytics?timeRange=${timeRange}`)
      const data = await response.json()
      
      if (data.success) {
        setAnalytics(data.analytics || [])
      }
    } catch (error) {
      console.error('분석 데이터 로드 실패:', error)
      // 데모 데이터로 대체
      setAnalytics(generateDemoData())
    } finally {
      setLoading(false)
    }
  }

  const generateDemoData = (): BrandAnalytics[] => {
    return [
      {
        id: '1',
        name: '스타벅스',
        totalRevenue: 2850000000,
        totalOrders: 145000,
        totalCustomers: 89000,
        averageRating: 4.5,
        growth: 12.5,
        marketShare: 35.2,
        stores: 1580,
        monthlyData: [
          { month: '1월', revenue: 230000000, orders: 12000, customers: 7500 },
          { month: '2월', revenue: 245000000, orders: 12800, customers: 7800 },
          { month: '3월', revenue: 252000000, orders: 13200, customers: 8100 },
          { month: '4월', revenue: 248000000, orders: 12900, customers: 7900 },
          { month: '5월', revenue: 265000000, orders: 13800, customers: 8400 },
          { month: '6월', revenue: 270000000, orders: 14100, customers: 8600 }
        ],
        categoryData: [
          { name: '커피', value: 45, color: '#0088FE' },
          { name: '디저트', value: 25, color: '#00C49F' },
          { name: '음료', value: 20, color: '#FFBB28' },
          { name: '기타', value: 10, color: '#FF8042' }
        ],
        performanceMetrics: {
          customerSatisfaction: 4.5,
          orderFulfillment: 98.5,
          deliveryTime: 12.3,
          returnRate: 1.2
        }
      },
      {
        id: '2',
        name: '카페베네',
        totalRevenue: 1850000000,
        totalOrders: 98000,
        totalCustomers: 62000,
        averageRating: 4.2,
        growth: 8.3,
        marketShare: 23.8,
        stores: 980,
        monthlyData: [
          { month: '1월', revenue: 150000000, orders: 8000, customers: 5200 },
          { month: '2월', revenue: 160000000, orders: 8400, customers: 5400 },
          { month: '3월', revenue: 165000000, orders: 8700, customers: 5600 },
          { month: '4월', revenue: 162000000, orders: 8500, customers: 5500 },
          { month: '5월', revenue: 175000000, orders: 9200, customers: 5900 },
          { month: '6월', revenue: 180000000, orders: 9500, customers: 6100 }
        ],
        categoryData: [
          { name: '커피', value: 50, color: '#0088FE' },
          { name: '브런치', value: 30, color: '#00C49F' },
          { name: '음료', value: 15, color: '#FFBB28' },
          { name: '기타', value: 5, color: '#FF8042' }
        ],
        performanceMetrics: {
          customerSatisfaction: 4.2,
          orderFulfillment: 96.8,
          deliveryTime: 15.2,
          returnRate: 1.8
        }
      }
    ]
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW',
      minimumFractionDigits: 0
    }).format(value)
  }

  const formatNumber = (value: number) => {
    return new Intl.NumberFormat('ko-KR').format(value)
  }

  const selectedBrandData = selectedBrand 
    ? analytics.find(brand => brand.id === selectedBrand)
    : null

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
              ))}
            </div>
            <div className="h-96 bg-gray-200 rounded-lg"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* 헤더 */}
        <div className="mb-8">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">브랜드 분석</h1>
              <p className="text-gray-600">브랜드별 성과 분석 및 비교</p>
            </div>
            <div className="flex gap-3">
              <select 
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="7d">최근 7일</option>
                <option value="30d">최근 30일</option>
                <option value="90d">최근 90일</option>
                <option value="1y">최근 1년</option>
              </select>
              <Button variant="outline" size="sm">
                <Download className="w-4 h-4 mr-2" />
                보고서 다운로드
              </Button>
            </div>
          </div>
        </div>

        {/* 브랜드 선택 */}
        <div className="mb-8">
          <div className="flex flex-wrap gap-3">
            <Button
              variant={selectedBrand === null ? "default" : "outline"}
              onClick={() => setSelectedBrand(null)}
              className="mb-2"
            >
              전체 브랜드
            </Button>
            {analytics.map(brand => (
              <Button
                key={brand.id}
                variant={selectedBrand === brand.id ? "default" : "outline"}
                onClick={() => setSelectedBrand(brand.id)}
                className="mb-2"
              >
                {brand.name}
              </Button>
            ))}
          </div>
        </div>

        {/* 전체 브랜드 개요 */}
        {!selectedBrand && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">총 매출</CardTitle>
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {formatCurrency(analytics.reduce((sum, brand) => sum + brand.totalRevenue, 0))}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    +{((analytics.reduce((sum, brand) => sum + brand.growth, 0) / analytics.length) || 0).toFixed(1)}% 전월 대비
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">총 주문</CardTitle>
                  <ShoppingCart className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {formatNumber(analytics.reduce((sum, brand) => sum + brand.totalOrders, 0))}
                  </div>
                  <p className="text-xs text-muted-foreground">전체 브랜드 합계</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">총 고객</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {formatNumber(analytics.reduce((sum, brand) => sum + brand.totalCustomers, 0))}
                  </div>
                  <p className="text-xs text-muted-foreground">활성 고객 수</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">평균 평점</CardTitle>
                  <Star className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {((analytics.reduce((sum, brand) => sum + brand.averageRating, 0) / analytics.length) || 0).toFixed(1)}
                  </div>
                  <p className="text-xs text-muted-foreground">전체 브랜드 평균</p>
                </CardContent>
              </Card>
            </div>

            {/* 브랜드별 성과 비교 */}
            <Card className="mb-8">
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle>브랜드별 성과 비교</CardTitle>
                    <CardDescription>매출, 주문, 고객 데이터 비교</CardDescription>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant={chartType === 'revenue' ? "default" : "outline"}
                      size="sm"
                      onClick={() => setChartType('revenue')}
                    >
                      매출
                    </Button>
                    <Button
                      variant={chartType === 'orders' ? "default" : "outline"}
                      size="sm"
                      onClick={() => setChartType('orders')}
                    >
                      주문
                    </Button>
                    <Button
                      variant={chartType === 'customers' ? "default" : "outline"}
                      size="sm"
                      onClick={() => setChartType('customers')}
                    >
                      고객
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={analytics}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip 
                      formatter={(value, name) => [
                        chartType === 'revenue' ? formatCurrency(Number(value)) : formatNumber(Number(value)),
                        chartType === 'revenue' ? '매출' : chartType === 'orders' ? '주문' : '고객'
                      ]}
                    />
                    <Legend />
                    <Bar 
                      dataKey={chartType === 'revenue' ? 'totalRevenue' : chartType === 'orders' ? 'totalOrders' : 'totalCustomers'}
                      fill="#8884d8"
                      name={chartType === 'revenue' ? '매출' : chartType === 'orders' ? '주문' : '고객'}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* 브랜드 목록 */}
            <Card>
              <CardHeader>
                <CardTitle>브랜드 성과 순위</CardTitle>
                <CardDescription>매출 기준 브랜드 순위</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {analytics
                    .sort((a, b) => b.totalRevenue - a.totalRevenue)
                    .map((brand, index) => (
                    <div key={brand.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center gap-4">
                        <div className="text-2xl font-bold text-gray-400">#{index + 1}</div>
                        <div>
                          <h3 className="font-semibold text-lg">{brand.name}</h3>
                          <p className="text-sm text-gray-600">
                            {formatNumber(brand.stores)}개 매장 • 시장점유율 {brand.marketShare}%
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-xl font-bold">{formatCurrency(brand.totalRevenue)}</div>
                        <div className="flex items-center gap-2">
                          {brand.growth > 0 ? (
                            <TrendingUp className="w-4 h-4 text-green-500" />
                          ) : (
                            <TrendingDown className="w-4 h-4 text-red-500" />
                          )}
                          <span className={`text-sm ${brand.growth > 0 ? 'text-green-500' : 'text-red-500'}`}>
                            {brand.growth > 0 ? '+' : ''}{brand.growth}%
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </>
        )}

        {/* 선택된 브랜드 상세 분석 */}
        {selectedBrandData && (
          <>
            {/* 브랜드 KPI */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">총 매출</CardTitle>
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{formatCurrency(selectedBrandData.totalRevenue)}</div>
                  <p className="text-xs text-muted-foreground flex items-center">
                    {selectedBrandData.growth > 0 ? (
                      <TrendingUp className="w-3 h-3 text-green-500 mr-1" />
                    ) : (
                      <TrendingDown className="w-3 h-3 text-red-500 mr-1" />
                    )}
                    {selectedBrandData.growth > 0 ? '+' : ''}{selectedBrandData.growth}% 전월 대비
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">총 주문</CardTitle>
                  <ShoppingCart className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{formatNumber(selectedBrandData.totalOrders)}</div>
                  <p className="text-xs text-muted-foreground">시장점유율 {selectedBrandData.marketShare}%</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">활성 고객</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{formatNumber(selectedBrandData.totalCustomers)}</div>
                  <p className="text-xs text-muted-foreground">{formatNumber(selectedBrandData.stores)}개 매장</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">평균 평점</CardTitle>
                  <Star className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{selectedBrandData.averageRating.toFixed(1)}</div>
                  <p className="text-xs text-muted-foreground">고객 만족도</p>
                </CardContent>
              </Card>
            </div>

            {/* 월별 트렌드 */}
            <Card className="mb-8">
              <CardHeader>
                <CardTitle>{selectedBrandData.name} 월별 트렌드</CardTitle>
                <CardDescription>매출, 주문, 고객 수 변화</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart data={selectedBrandData.monthlyData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis yAxisId="left" />
                    <YAxis yAxisId="right" orientation="right" />
                    <Tooltip 
                      formatter={(value, name) => [
                        name === 'revenue' ? formatCurrency(Number(value)) : formatNumber(Number(value)),
                        name === 'revenue' ? '매출' : name === 'orders' ? '주문' : '고객'
                      ]}
                    />
                    <Legend />
                    <Area yAxisId="left" type="monotone" dataKey="revenue" stackId="1" stroke="#8884d8" fill="#8884d8" name="매출" />
                    <Line yAxisId="right" type="monotone" dataKey="orders" stroke="#82ca9d" name="주문" />
                    <Line yAxisId="right" type="monotone" dataKey="customers" stroke="#ffc658" name="고객" />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              {/* 카테고리별 매출 */}
              <Card>
                <CardHeader>
                  <CardTitle>카테고리별 매출 비중</CardTitle>
                  <CardDescription>제품 카테고리별 매출 분포</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={selectedBrandData.categoryData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, value }) => `${name} ${value}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {selectedBrandData.categoryData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* 성과 지표 */}
              <Card>
                <CardHeader>
                  <CardTitle>주요 성과 지표</CardTitle>
                  <CardDescription>운영 효율성 및 고객 만족도</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium">고객 만족도</span>
                      <div className="flex items-center gap-2">
                        <div className="w-24 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-green-500 h-2 rounded-full" 
                            style={{ width: `${(selectedBrandData.performanceMetrics.customerSatisfaction / 5) * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm">{selectedBrandData.performanceMetrics.customerSatisfaction}/5.0</span>
                      </div>
                    </div>
                    
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium">주문 처리율</span>
                      <div className="flex items-center gap-2">
                        <div className="w-24 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-500 h-2 rounded-full" 
                            style={{ width: `${selectedBrandData.performanceMetrics.orderFulfillment}%` }}
                          ></div>
                        </div>
                        <span className="text-sm">{selectedBrandData.performanceMetrics.orderFulfillment}%</span>
                      </div>
                    </div>
                    
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium">평균 배송시간</span>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline">{selectedBrandData.performanceMetrics.deliveryTime}분</Badge>
                      </div>
                    </div>
                    
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium">반품률</span>
                      <div className="flex items-center gap-2">
                        <Badge variant={selectedBrandData.performanceMetrics.returnRate < 2 ? "default" : "destructive"}>
                          {selectedBrandData.performanceMetrics.returnRate}%
                        </Badge>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
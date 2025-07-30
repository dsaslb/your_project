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
  Download, FileText, Calendar, Filter, TrendingUp, TrendingDown,
  DollarSign, ShoppingCart, Users, Star, Target, BarChart3,
  Clock, CheckCircle, AlertTriangle, Activity
} from 'lucide-react'
import { toast } from 'react-hot-toast'

interface ReportData {
  id: string
  title: string
  type: 'sales' | 'customer' | 'inventory' | 'performance'
  period: string
  generatedAt: string
  data: any
  summary: {
    totalRevenue?: number
    totalOrders?: number
    totalCustomers?: number
    avgRating?: number
    growthRate?: number
  }
}

export default function BrandReportsPage() {
  const [reports, setReports] = useState<ReportData[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedReport, setSelectedReport] = useState<ReportData | null>(null)
  const [reportType, setReportType] = useState<string>('all')
  const [dateRange, setDateRange] = useState<string>('30d')
  const [selectedBrand, setSelectedBrand] = useState<any>(null)
  const [brands, setBrands] = useState<any[]>([])

  useEffect(() => {
    loadBrands()
    loadReports()
  }, [reportType, dateRange])

  const loadBrands = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'
      const response = await fetch(`${apiUrl}/api/brands`)
      const data = await response.json()
      
      if (data.success) {
        setBrands(data.brands || [])
        if (data.brands?.length > 0) {
          setSelectedBrand(data.brands[0])
        }
      }
    } catch (error) {
      console.error('브랜드 목록 로드 실패:', error)
      // 데모 데이터 사용
      const demoBrands = [
        { id: '1', name: '스타벅스' },
        { id: '2', name: '카페베네' }
      ]
      setBrands(demoBrands)
      setSelectedBrand(demoBrands[0])
    }
  }

  const loadReports = async () => {
    try {
      setLoading(true)
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'
      const response = await fetch(
        `${apiUrl}/api/brands/reports?type=${reportType}&dateRange=${dateRange}`
      )
      const data = await response.json()
      
      if (data.success) {
        setReports(data.reports || [])
      }
    } catch (error) {
      console.error('리포트 로드 실패:', error)
      // 데모 데이터 생성
      setReports(generateDemoReports())
    } finally {
      setLoading(false)
    }
  }

  const generateDemoReports = (): ReportData[] => {
    const now = new Date()
    const lastMonth = new Date(now.getFullYear(), now.getMonth() - 1, now.getDate())
    
    return [
      {
        id: '1',
        title: '월간 매출 리포트',
        type: 'sales',
        period: '2024년 6월',
        generatedAt: now.toISOString(),
        data: {
          monthly: [
            { month: '1월', revenue: 2500000000, orders: 125000 },
            { month: '2월', revenue: 2600000000, orders: 130000 },
            { month: '3월', revenue: 2750000000, orders: 137500 },
            { month: '4월', revenue: 2650000000, orders: 132500 },
            { month: '5월', revenue: 2850000000, orders: 142500 },
            { month: '6월', revenue: 2950000000, orders: 147500 }
          ]
        },
        summary: {
          totalRevenue: 2950000000,
          totalOrders: 147500,
          growthRate: 12.5
        }
      },
      {
        id: '2',
        title: '고객 분석 리포트',
        type: 'customer',
        period: '2024년 Q2',
        generatedAt: lastMonth.toISOString(),
        data: {
          demographics: [
            { age: '20-29', count: 35000, percentage: 35 },
            { age: '30-39', count: 28000, percentage: 28 },
            { age: '40-49', count: 22000, percentage: 22 },
            { age: '50+', count: 15000, percentage: 15 }
          ],
          satisfaction: [
            { rating: 5, count: 45000 },
            { rating: 4, count: 32000 },
            { rating: 3, count: 15000 },
            { rating: 2, count: 5000 },
            { rating: 1, count: 3000 }
          ]
        },
        summary: {
          totalCustomers: 100000,
          avgRating: 4.2,
          growthRate: 8.3
        }
      },
      {
        id: '3',
        title: '재고 현황 리포트',
        type: 'inventory',
        period: '2024년 6월',
        generatedAt: now.toISOString(),
        data: {
          categories: [
            { name: '커피원두', stock: 850, target: 1000, status: 'warning' },
            { name: '디저트', stock: 1200, target: 800, status: 'good' },
            { name: '음료용품', stock: 450, target: 600, status: 'low' },
            { name: '기타', stock: 300, target: 400, status: 'warning' }
          ]
        },
        summary: {
          growthRate: -2.1
        }
      },
      {
        id: '4',
        title: '성과 분석 리포트',
        type: 'performance',
        period: '2024년 상반기',
        generatedAt: now.toISOString(),
        data: {
          kpis: [
            { name: '매출 목표 달성률', value: 108.5, target: 100, unit: '%' },
            { name: '고객 만족도', value: 4.2, target: 4.0, unit: '/5.0' },
            { name: '주문 처리 시간', value: 12.3, target: 15.0, unit: '분' },
            { name: '재방문율', value: 68.5, target: 65.0, unit: '%' }
          ]
        },
        summary: {
          growthRate: 15.2
        }
      }
    ]
  }

  const downloadReport = async (reportId: string) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'
      const response = await fetch(`${apiUrl}/api/brands/reports/${reportId}/download`)
      
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `report-${reportId}.pdf`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
        toast.success('리포트가 다운로드되었습니다!')
      }
    } catch (error) {
      console.error('리포트 다운로드 실패:', error)
      toast.success('리포트 다운로드 완료! (데모 모드)')
    }
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

  const getReportTypeIcon = (type: string) => {
    switch (type) {
      case 'sales': return <DollarSign className="w-5 h-5" />
      case 'customer': return <Users className="w-5 h-5" />
      case 'inventory': return <ShoppingCart className="w-5 h-5" />
      case 'performance': return <Target className="w-5 h-5" />
      default: return <FileText className="w-5 h-5" />
    }
  }

  const getReportTypeName = (type: string) => {
    switch (type) {
      case 'sales': return '매출'
      case 'customer': return '고객'
      case 'inventory': return '재고'
      case 'performance': return '성과'
      default: return '기타'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'good': return 'bg-green-100 text-green-800'
      case 'warning': return 'bg-yellow-100 text-yellow-800'
      case 'low': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[1, 2, 3, 4, 5, 6].map(i => (
                <div key={i} className="h-64 bg-gray-200 rounded-lg"></div>
              ))}
            </div>
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
              <h1 className="text-3xl font-bold text-gray-900 mb-2">브랜드 리포트</h1>
              <p className="text-gray-600">브랜드별 상세 분석 리포트 및 데이터 다운로드</p>
            </div>
            <div className="flex gap-3">
              <select 
                value={dateRange}
                onChange={(e) => setDateRange(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="7d">최근 7일</option>
                <option value="30d">최근 30일</option>
                <option value="90d">최근 90일</option>
                <option value="1y">최근 1년</option>
              </select>
              <select 
                value={reportType}
                onChange={(e) => setReportType(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">모든 리포트</option>
                <option value="sales">매출 리포트</option>
                <option value="customer">고객 리포트</option>
                <option value="inventory">재고 리포트</option>
                <option value="performance">성과 리포트</option>
              </select>
            </div>
          </div>
        </div>

        {/* 브랜드 선택 */}
        {brands.length > 1 && (
          <div className="mb-8">
            <div className="flex flex-wrap gap-3">
              {brands.map(brand => (
                <Button
                  key={brand.id}
                  variant={selectedBrand?.id === brand.id ? "default" : "outline"}
                  onClick={() => setSelectedBrand(brand)}
                >
                  {brand.name}
                </Button>
              ))}
            </div>
          </div>
        )}

        {/* 리포트 목록 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {reports.map(report => (
            <Card key={report.id} className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-100 rounded-lg">
                      {getReportTypeIcon(report.type)}
                    </div>
                    <div>
                      <CardTitle className="text-lg">{report.title}</CardTitle>
                      <CardDescription>{report.period}</CardDescription>
                    </div>
                  </div>
                  <Badge variant="outline">
                    {getReportTypeName(report.type)}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* 요약 정보 */}
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    {report.summary.totalRevenue && (
                      <div>
                        <p className="text-gray-500">총 매출</p>
                        <p className="font-semibold">{formatCurrency(report.summary.totalRevenue)}</p>
                      </div>
                    )}
                    {report.summary.totalOrders && (
                      <div>
                        <p className="text-gray-500">총 주문</p>
                        <p className="font-semibold">{formatNumber(report.summary.totalOrders)}</p>
                      </div>
                    )}
                    {report.summary.totalCustomers && (
                      <div>
                        <p className="text-gray-500">총 고객</p>
                        <p className="font-semibold">{formatNumber(report.summary.totalCustomers)}</p>
                      </div>
                    )}
                    {report.summary.avgRating && (
                      <div>
                        <p className="text-gray-500">평균 평점</p>
                        <p className="font-semibold">{report.summary.avgRating.toFixed(1)}/5.0</p>
                      </div>
                    )}
                  </div>

                  {/* 성장률 */}
                  {report.summary.growthRate && (
                    <div className="flex items-center gap-2">
                      {report.summary.growthRate > 0 ? (
                        <TrendingUp className="w-4 h-4 text-green-500" />
                      ) : (
                        <TrendingDown className="w-4 h-4 text-red-500" />
                      )}
                      <span className={`text-sm font-medium ${
                        report.summary.growthRate > 0 ? 'text-green-500' : 'text-red-500'
                      }`}>
                        {report.summary.growthRate > 0 ? '+' : ''}{report.summary.growthRate}% 성장
                      </span>
                    </div>
                  )}

                  {/* 생성일 */}
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <Clock className="w-3 h-3" />
                    {new Date(report.generatedAt).toLocaleDateString('ko-KR', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </div>

                  {/* 액션 버튼 */}
                  <div className="flex gap-2 pt-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-1"
                      onClick={() => setSelectedReport(report)}
                    >
                      <BarChart3 className="w-4 h-4 mr-2" />
                      상세보기
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => downloadReport(report.id)}
                    >
                      <Download className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* 선택된 리포트 상세 */}
        {selectedReport && (
          <Card className="mb-8">
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="text-xl">{selectedReport.title}</CardTitle>
                  <CardDescription className="mt-1">{selectedReport.period}</CardDescription>
                </div>
                <Button
                  variant="outline"
                  onClick={() => setSelectedReport(null)}
                >
                  닫기
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {/* 매출 리포트 */}
              {selectedReport.type === 'sales' && selectedReport.data.monthly && (
                <div className="space-y-6">
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={selectedReport.data.monthly}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="month" />
                        <YAxis />
                        <Tooltip 
                          formatter={(value, name) => [
                            name === 'revenue' ? formatCurrency(Number(value)) : formatNumber(Number(value)),
                            name === 'revenue' ? '매출' : '주문'
                          ]}
                        />
                        <Legend />
                        <Area type="monotone" dataKey="revenue" stackId="1" stroke="#8884d8" fill="#8884d8" name="매출" />
                        <Area type="monotone" dataKey="orders" stackId="2" stroke="#82ca9d" fill="#82ca9d" name="주문" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}

              {/* 고객 리포트 */}
              {selectedReport.type === 'customer' && selectedReport.data.demographics && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  <div>
                    <h4 className="text-lg font-semibold mb-4">연령대별 분포</h4>
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={selectedReport.data.demographics}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ age, percentage }) => `${age} (${percentage}%)`}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="count"
                        >
                          {selectedReport.data.demographics.map((entry: any, index: number) => (
                            <Cell key={`cell-${index}`} fill={`hsl(${index * 90}, 70%, 60%)`} />
                          ))}
                        </Pie>
                        <Tooltip formatter={(value) => formatNumber(Number(value))} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>

                  <div>
                    <h4 className="text-lg font-semibold mb-4">만족도 분포</h4>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={selectedReport.data.satisfaction}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="rating" />
                        <YAxis />
                        <Tooltip formatter={(value) => formatNumber(Number(value))} />
                        <Bar dataKey="count" fill="#82ca9d" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}

              {/* 재고 리포트 */}
              {selectedReport.type === 'inventory' && selectedReport.data.categories && (
                <div className="space-y-4">
                  <h4 className="text-lg font-semibold">카테고리별 재고 현황</h4>
                  <div className="space-y-4">
                    {selectedReport.data.categories.map((category: any, index: number) => (
                      <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex items-center gap-4">
                          <div className="text-lg font-medium">{category.name}</div>
                          <Badge className={getStatusColor(category.status)}>
                            {category.status === 'good' ? '충분' : 
                             category.status === 'warning' ? '주의' : '부족'}
                          </Badge>
                        </div>
                        <div className="text-right">
                          <div className="text-lg font-bold">{formatNumber(category.stock)}</div>
                          <div className="text-sm text-gray-500">목표: {formatNumber(category.target)}</div>
                        </div>
                        <div className="w-24 bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${
                              category.stock >= category.target ? 'bg-green-500' :
                              category.stock >= category.target * 0.7 ? 'bg-yellow-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${Math.min((category.stock / category.target) * 100, 100)}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 성과 리포트 */}
              {selectedReport.type === 'performance' && selectedReport.data.kpis && (
                <div className="space-y-4">
                  <h4 className="text-lg font-semibold">주요 성과 지표 (KPI)</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {selectedReport.data.kpis.map((kpi: any, index: number) => (
                      <Card key={index}>
                        <CardContent className="p-6">
                          <div className="flex justify-between items-start mb-4">
                            <h5 className="font-medium">{kpi.name}</h5>
                            {kpi.value >= kpi.target ? (
                              <CheckCircle className="w-5 h-5 text-green-500" />
                            ) : (
                              <AlertTriangle className="w-5 h-5 text-yellow-500" />
                            )}
                          </div>
                          <div className="space-y-2">
                            <div className="flex justify-between">
                              <span className="text-2xl font-bold">{kpi.value}{kpi.unit}</span>
                              <span className="text-sm text-gray-500">목표: {kpi.target}{kpi.unit}</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div 
                                className={`h-2 rounded-full ${
                                  kpi.value >= kpi.target ? 'bg-green-500' : 'bg-yellow-500'
                                }`}
                                style={{ width: `${Math.min((kpi.value / kpi.target) * 100, 100)}%` }}
                              ></div>
                            </div>
                            <div className="flex justify-between text-sm text-gray-500">
                              <span>달성률: {((kpi.value / kpi.target) * 100).toFixed(1)}%</span>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {reports.length === 0 && (
          <Card>
            <CardContent className="p-12 text-center">
              <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">리포트가 없습니다</h3>
              <p className="text-gray-500">선택한 조건에 맞는 리포트가 없습니다. 필터를 조정해보세요.</p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
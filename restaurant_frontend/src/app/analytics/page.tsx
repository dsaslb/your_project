"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Users,
  Clock,
  Calendar,
  Target,
  Award,
  Star,
  Eye,
  Download,
  Filter,
  Search,
  RefreshCw,
  Plus,
  Edit,
  Trash2,
  FileText,
  Camera,
  Upload,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Info,
  HelpCircle,
  PieChart,
  LineChart,
  Activity,
  ShoppingCart,
  Receipt,
  CreditCard,
  Gift,
  Percent,
  Hash,
  HashIcon,
  ArrowUp,
  ArrowDown,
  Minus,
  Equal,
  Clock4,
  Timer,
  Zap,
  Flame,
  Snowflake,
  Sun,
  Moon,
  Cloud,
  CloudRain,
  Wind,
  Thermometer,
  Droplets,
  Gauge,
  BarChart,
  PieChart as PieChartIcon,
  LineChart as LineChartIcon,
  ScatterChart,
  AreaChart,
  CandlestickChart,
  Radar,
  Funnel,
} from "lucide-react";

// 더미 데이터
const salesData = {
  daily: [
    { date: "2024-01-10", sales: 1250000, orders: 45, customers: 38 },
    { date: "2024-01-11", sales: 1380000, orders: 52, customers: 45 },
    { date: "2024-01-12", sales: 1420000, orders: 58, customers: 49 },
    { date: "2024-01-13", sales: 1560000, orders: 62, customers: 54 },
    { date: "2024-01-14", sales: 1680000, orders: 68, customers: 58 },
    { date: "2024-01-15", sales: 1450000, orders: 55, customers: 47 },
    { date: "2024-01-16", sales: 1320000, orders: 48, customers: 41 },
  ],
  monthly: [
    { month: "1월", sales: 42000000, orders: 1800, customers: 1500 },
    { month: "2월", sales: 38000000, orders: 1650, customers: 1400 },
    { month: "3월", sales: 45000000, orders: 1950, customers: 1600 },
    { month: "4월", sales: 48000000, orders: 2100, customers: 1750 },
    { month: "5월", sales: 52000000, orders: 2250, customers: 1850 },
    { month: "6월", sales: 55000000, orders: 2400, customers: 1950 },
  ]
};

const menuSalesData = [
  { name: "스테이크", sales: 12500000, orders: 450, percentage: 25.5 },
  { name: "파스타", sales: 9800000, orders: 680, percentage: 20.0 },
  { name: "피자", sales: 8700000, orders: 520, percentage: 17.8 },
  { name: "샐러드", sales: 6500000, orders: 890, percentage: 13.3 },
  { name: "스프", sales: 4200000, orders: 320, percentage: 8.6 },
  { name: "디저트", sales: 3800000, orders: 280, percentage: 7.8 },
  { name: "음료", sales: 2800000, orders: 450, percentage: 5.7 },
  { name: "기타", sales: 1500000, orders: 120, percentage: 3.1 },
];

const employeePerformance = [
  { name: "김영희", role: "주방장", orders: 45, rating: 4.8, efficiency: 95 },
  { name: "박철수", role: "서버", orders: 38, rating: 4.6, efficiency: 88 },
  { name: "이민수", role: "청소담당", orders: 0, rating: 4.9, efficiency: 92 },
  { name: "최지영", role: "매니저", orders: 52, rating: 4.7, efficiency: 90 },
  { name: "정현우", role: "서버", orders: 41, rating: 4.5, efficiency: 85 },
];

const cleaningReports = [
  {
    id: 1,
    employee: "이민수",
    area: "주방",
    date: "2024-01-15",
    time: "22:00-23:15",
    rating: 5,
    status: "completed",
    description: "주방 전체 청소 완료. 조리대, 가스레인지, 냉장고, 바닥 모두 청소 및 소독 완료.",
    checklist: [
      { item: "조리대 청소", completed: true },
      { item: "가스레인지 청소", completed: true },
      { item: "냉장고 정리", completed: true },
      { item: "바닥 청소", completed: true },
      { item: "쓰레기통 비우기", completed: true },
    ],
    photos: ["kitchen_clean_1.jpg", "kitchen_clean_2.jpg"],
  },
  {
    id: 2,
    employee: "박철수",
    area: "매장 내부",
    date: "2024-01-15",
    time: "21:30-22:15",
    rating: 4,
    status: "completed",
    description: "매장 내부 청소 완료. 테이블, 의자, 바닥 청소 완료. 창문 청소는 내일 진행 예정.",
    checklist: [
      { item: "테이블 청소", completed: true },
      { item: "의자 청소", completed: true },
      { item: "바닥 청소", completed: true },
      { item: "창문 청소", completed: false },
      { item: "화장실 청소", completed: true },
    ],
    photos: ["dining_clean_1.jpg"],
  },
];

const paymentMethods = [
  { method: "카드", amount: 8500000, percentage: 58.6 },
  { method: "현금", amount: 3200000, percentage: 22.1 },
  { method: "모바일 결제", amount: 2800000, percentage: 19.3 },
];

const customerSatisfaction = {
  overall: 4.6,
  categories: [
    { category: "음식 품질", rating: 4.8 },
    { category: "서비스", rating: 4.5 },
    { category: "청결도", rating: 4.7 },
    { category: "가격", rating: 4.3 },
    { category: "분위기", rating: 4.6 },
  ]
};

export default function AnalyticsPage() {
  const [activeTab, setActiveTab] = useState("overview");
  const [dateRange, setDateRange] = useState("week");
  const [selectedReport, setSelectedReport] = useState<any>(null);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW'
    }).format(amount);
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('ko-KR').format(num);
  };

  const getGrowthRate = (current: number, previous: number) => {
    if (previous === 0) return 0;
    return ((current - previous) / previous) * 100;
  };

  const getGrowthIcon = (rate: number) => {
    if (rate > 0) return <ArrowUp className="h-4 w-4 text-green-600" />;
    if (rate < 0) return <ArrowDown className="h-4 w-4 text-red-600" />;
    return <Minus className="h-4 w-4 text-gray-600" />;
  };

  const getGrowthColor = (rate: number) => {
    if (rate > 0) return "text-green-600";
    if (rate < 0) return "text-red-600";
    return "text-gray-600";
  };

  const currentSales = salesData.daily[salesData.daily.length - 1]?.sales || 0;
  const previousSales = salesData.daily[salesData.daily.length - 2]?.sales || 0;
  const salesGrowth = getGrowthRate(currentSales, previousSales);

  const currentOrders = salesData.daily[salesData.daily.length - 1]?.orders || 0;
  const previousOrders = salesData.daily[salesData.daily.length - 2]?.orders || 0;
  const ordersGrowth = getGrowthRate(currentOrders, previousOrders);

  const currentCustomers = salesData.daily[salesData.daily.length - 1]?.customers || 0;
  const previousCustomers = salesData.daily[salesData.daily.length - 2]?.customers || 0;
  const customersGrowth = getGrowthRate(currentCustomers, previousCustomers);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">매장 종합 정보</h1>
          <p className="text-muted-foreground">매장의 모든 정보를 한눈에 확인하세요.</p>
        </div>
        <div className="flex items-center gap-2">
          <Select value={dateRange} onValueChange={setDateRange}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="today">오늘</SelectItem>
              <SelectItem value="week">이번 주</SelectItem>
              <SelectItem value="month">이번 달</SelectItem>
              <SelectItem value="quarter">이번 분기</SelectItem>
              <SelectItem value="year">올해</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            보고서 다운로드
          </Button>
        </div>
      </div>

      {/* 주요 지표 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">총 매출</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(currentSales)}</div>
            <div className="flex items-center gap-1 text-sm">
              {getGrowthIcon(salesGrowth)}
              <span className={getGrowthColor(salesGrowth)}>
                {salesGrowth > 0 ? '+' : ''}{salesGrowth.toFixed(1)}%
              </span>
              <span className="text-muted-foreground">전일 대비</span>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">주문 수</CardTitle>
            <ShoppingCart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(currentOrders)}</div>
            <div className="flex items-center gap-1 text-sm">
              {getGrowthIcon(ordersGrowth)}
              <span className={getGrowthColor(ordersGrowth)}>
                {ordersGrowth > 0 ? '+' : ''}{ordersGrowth.toFixed(1)}%
              </span>
              <span className="text-muted-foreground">전일 대비</span>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">고객 수</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(currentCustomers)}</div>
            <div className="flex items-center gap-1 text-sm">
              {getGrowthIcon(customersGrowth)}
              <span className={getGrowthColor(customersGrowth)}>
                {customersGrowth > 0 ? '+' : ''}{customersGrowth.toFixed(1)}%
              </span>
              <span className="text-muted-foreground">전일 대비</span>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">평균 주문 금액</CardTitle>
            <Receipt className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {currentOrders > 0 ? formatCurrency(currentSales / currentOrders) : formatCurrency(0)}
            </div>
            <p className="text-xs text-muted-foreground">고객당 평균</p>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">종합 현황</TabsTrigger>
          <TabsTrigger value="sales">매출 분석</TabsTrigger>
          <TabsTrigger value="cleaning">청소 현황</TabsTrigger>
          <TabsTrigger value="performance">업무 성과</TabsTrigger>
        </TabsList>

        {/* 종합 현황 탭 */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 매출 트렌드 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  일일 매출 트렌드
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {salesData.daily.slice(-7).map((day, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-3 h-3 bg-blue-600 rounded-full"></div>
                        <span className="text-sm">{day.date}</span>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold">{formatCurrency(day.sales)}</div>
                        <div className="text-xs text-muted-foreground">
                          {day.orders}주문 / {day.customers}고객
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* 메뉴 판매 현황 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PieChartIcon className="h-5 w-5" />
                  메뉴별 판매 현황
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {menuSalesData.slice(0, 5).map((menu, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-3 h-3 rounded-full" style={{
                          backgroundColor: `hsl(${index * 60}, 70%, 50%)`
                        }}></div>
                        <span className="text-sm font-medium">{menu.name}</span>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold">{formatCurrency(menu.sales)}</div>
                        <div className="text-xs text-muted-foreground">
                          {menu.percentage}% ({menu.orders}주문)
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 결제 방법별 현황 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CreditCard className="h-5 w-5" />
                결제 방법별 현황
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {paymentMethods.map((method, index) => (
                  <div key={index} className="text-center">
                    <div className="text-2xl font-bold">{formatCurrency(method.amount)}</div>
                    <div className="text-sm text-muted-foreground">{method.method}</div>
                    <div className="text-xs text-muted-foreground">{method.percentage}%</div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* 고객 만족도 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Star className="h-5 w-5" />
                고객 만족도
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="text-center">
                  <div className="text-4xl font-bold text-yellow-600">{customerSatisfaction.overall}</div>
                  <div className="text-sm text-muted-foreground">전체 평점</div>
                </div>
                <div className="space-y-2">
                  {customerSatisfaction.categories.map((category, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <span className="text-sm">{category.category}</span>
                      <div className="flex items-center gap-1">
                        <span className="font-semibold">{category.rating}</span>
                        <Star className="h-3 w-3 text-yellow-500 fill-current" />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 매출 분석 탭 */}
        <TabsContent value="sales" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 월별 매출 현황 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  월별 매출 현황
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {salesData.monthly.map((month, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-3 h-3 bg-green-600 rounded-full"></div>
                        <span className="text-sm font-medium">{month.month}</span>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold">{formatCurrency(month.sales)}</div>
                        <div className="text-xs text-muted-foreground">
                          {formatNumber(month.orders)}주문 / {formatNumber(month.customers)}고객
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* 메뉴별 상세 분석 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PieChartIcon className="h-5 w-5" />
                  메뉴별 상세 분석
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {menuSalesData.map((menu, index) => (
                    <div key={index} className="border rounded-lg p-3">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium">{menu.name}</span>
                        <Badge variant="outline">{menu.percentage}%</Badge>
                      </div>
                      <div className="space-y-1 text-sm">
                        <div className="flex justify-between">
                          <span>매출</span>
                          <span className="font-semibold">{formatCurrency(menu.sales)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>주문 수</span>
                          <span>{formatNumber(menu.orders)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>평균 단가</span>
                          <span>{formatCurrency(menu.sales / menu.orders)}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* 청소 현황 탭 */}
        <TabsContent value="cleaning" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 청소 완료 현황 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5" />
                  청소 완료 현황
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {cleaningReports.map((report) => (
                    <div key={report.id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div>
                          <h4 className="font-semibold">{report.area}</h4>
                          <p className="text-sm text-muted-foreground">
                            {report.employee} • {report.date} {report.time}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge className="bg-green-100 text-green-800">완료</Badge>
                          <div className="flex items-center gap-1">
                            <Star className="h-4 w-4 text-yellow-500 fill-current" />
                            <span className="text-sm font-semibold">{report.rating}</span>
                          </div>
                        </div>
                      </div>
                      
                      <p className="text-sm mb-3">{report.description}</p>
                      
                      <div className="space-y-2">
                        <p className="text-sm font-medium">체크리스트:</p>
                        <div className="grid grid-cols-2 gap-2">
                          {report.checklist.map((item, index) => (
                            <div key={index} className="flex items-center gap-2 text-sm">
                              {item.completed ? (
                                <CheckCircle className="h-3 w-3 text-green-600" />
                              ) : (
                                <XCircle className="h-3 w-3 text-red-600" />
                              )}
                              <span className={item.completed ? "" : "line-through text-gray-500"}>
                                {item.item}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                      
                      {report.photos.length > 0 && (
                        <div className="mt-3">
                          <p className="text-sm font-medium mb-2">첨부 사진:</p>
                          <div className="flex gap-2">
                            {report.photos.map((photo, index) => (
                              <div key={index} className="w-16 h-16 bg-gray-200 rounded flex items-center justify-center">
                                <Camera className="h-6 w-6 text-gray-500" />
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* 청소 통계 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  청소 통계
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-600">
                      {cleaningReports.filter(r => r.status === "completed").length}
                    </div>
                    <div className="text-sm text-muted-foreground">완료된 청소</div>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">평균 평점</span>
                      <div className="flex items-center gap-1">
                        <span className="font-semibold">
                          {(cleaningReports.reduce((sum, r) => sum + r.rating, 0) / cleaningReports.length).toFixed(1)}
                        </span>
                        <Star className="h-4 w-4 text-yellow-500 fill-current" />
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-sm">총 청소 시간</span>
                      <span className="font-semibold">2시간 45분</span>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-sm">평균 청소 시간</span>
                      <span className="font-semibold">1시간 22분</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* 업무 성과 탭 */}
        <TabsContent value="performance" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                직원 업무 성과
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {employeePerformance.map((employee, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <h4 className="font-semibold">{employee.name}</h4>
                        <p className="text-sm text-muted-foreground">{employee.role}</p>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="text-center">
                          <div className="text-lg font-bold">{employee.orders}</div>
                          <div className="text-xs text-muted-foreground">주문</div>
                        </div>
                        <div className="text-center">
                          <div className="flex items-center gap-1">
                            <span className="text-lg font-bold">{employee.rating}</span>
                            <Star className="h-4 w-4 text-yellow-500 fill-current" />
                          </div>
                          <div className="text-xs text-muted-foreground">평점</div>
                        </div>
                        <div className="text-center">
                          <div className="text-lg font-bold">{employee.efficiency}%</div>
                          <div className="text-xs text-muted-foreground">효율성</div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-green-600 h-2 rounded-full" 
                        style={{ width: `${employee.efficiency}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
} 
"use client";
import { useState, useEffect } from "react";
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Users,
  ShoppingCart,
  Package,
  Calendar,
  Download,
  Filter,
  Building2,
} from "lucide-react";

interface BrandStats {
  totalSales: number;
  totalOrders: number;
  totalEmployees: number;
  totalBranches: number;
  monthlySales: number[];
  monthlyOrders: number[];
  branchPerformance: Array<{
    id: number;
    name: string;
    sales: number;
    orders: number;
    employees: number;
    growth: number;
  }>;
  topProducts: Array<{
    name: string;
    sales: number;
    quantity: number;
  }>;
  employeeStats: {
    total: number;
    active: number;
    new: number;
    turnover: number;
  };
}

export default function ReportsPage() {
  const [stats, setStats] = useState<BrandStats | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [selectedPeriod, setSelectedPeriod] = useState("month");

  useEffect(() => {
    loadBrandStats();
  }, [selectedPeriod]);

  const loadBrandStats = async () => {
    // 실제로는 API 호출
    const mockStats: BrandStats = {
      totalSales: 36400000,
      totalOrders: 697,
      totalEmployees: 50,
      totalBranches: 5,
      monthlySales: [32000000, 34000000, 35000000, 36000000, 36500000, 36400000],
      monthlyOrders: [580, 620, 650, 680, 690, 697],
      branchPerformance: [
        {
          id: 1,
          name: "강남점",
          sales: 9200000,
          orders: 175,
          employees: 12,
          growth: 8.5,
        },
        {
          id: 2,
          name: "홍대점",
          sales: 7800000,
          orders: 142,
          employees: 10,
          growth: 5.2,
        },
        {
          id: 3,
          name: "부산점",
          sales: 6800000,
          orders: 98,
          employees: 8,
          growth: 3.8,
        },
        {
          id: 4,
          name: "대구점",
          sales: 6100000,
          orders: 87,
          employees: 9,
          growth: 2.1,
        },
        {
          id: 5,
          name: "인천점",
          sales: 7800000,
          orders: 142,
          employees: 11,
          growth: 6.7,
        },
      ],
      topProducts: [
        { name: "스테이크", sales: 8500000, quantity: 425 },
        { name: "파스타", sales: 7200000, quantity: 1200 },
        { name: "피자", sales: 6800000, quantity: 850 },
        { name: "샐러드", sales: 4500000, quantity: 900 },
        { name: "음료", sales: 3800000, quantity: 1900 },
      ],
      employeeStats: {
        total: 50,
        active: 45,
        new: 3,
        turnover: 4.2,
      },
    };

    setStats(mockStats);
    setIsLoaded(true);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ko-KR').format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${value > 0 ? '+' : ''}${value.toFixed(1)}%`;
  };

  if (!isLoaded || !stats) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">통계 데이터 로딩 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      {/* 헤더 */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">브랜드 통계 리포트</h1>
            <p className="text-gray-600 mt-2">전체 브랜드 성과 및 분석 리포트</p>
          </div>
          <div className="flex items-center space-x-4">
            <select
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="week">주간</option>
              <option value="month">월간</option>
              <option value="quarter">분기</option>
              <option value="year">연간</option>
            </select>
            <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors">
              <Download className="h-4 w-4" />
              리포트 다운로드
            </button>
          </div>
        </div>
      </div>

      {/* 주요 지표 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">총 매출</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(stats.totalSales)}원
              </p>
              <p className="text-sm text-green-600 flex items-center">
                <TrendingUp className="h-4 w-4 mr-1" />
                +5.2% 전월 대비
              </p>
            </div>
            <DollarSign className="h-8 w-8 text-green-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">총 주문</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats.totalOrders}건
              </p>
              <p className="text-sm text-green-600 flex items-center">
                <TrendingUp className="h-4 w-4 mr-1" />
                +3.8% 전월 대비
              </p>
            </div>
            <ShoppingCart className="h-8 w-8 text-blue-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">총 직원</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats.totalEmployees}명
              </p>
              <p className="text-sm text-blue-600 flex items-center">
                <Users className="h-4 w-4 mr-1" />
                +2명 신규 채용
              </p>
            </div>
            <Users className="h-8 w-8 text-purple-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">평균 주문</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(Math.round(stats.totalSales / stats.totalOrders))}원
              </p>
              <p className="text-sm text-green-600 flex items-center">
                <TrendingUp className="h-4 w-4 mr-1" />
                +1.3% 전월 대비
              </p>
            </div>
            <BarChart3 className="h-8 w-8 text-indigo-600" />
          </div>
        </div>
      </div>

      {/* 매장별 성과 */}
      <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">매장별 성과</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  매장
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  매출
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  주문
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  직원
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  성장률
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {stats.branchPerformance.map((branch) => (
                <tr key={branch.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="flex items-center">
                      <Building2 className="h-5 w-5 text-gray-400 mr-3" />
                      <div className="text-sm font-medium text-gray-900">
                        {branch.name}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {formatCurrency(branch.sales)}원
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {branch.orders}건
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {branch.employees}명
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      branch.growth > 0 
                        ? "text-green-600 bg-green-100" 
                        : "text-red-600 bg-red-100"
                    }`}>
                      {formatPercentage(branch.growth)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 상세 통계 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* 인기 상품 */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">인기 상품 TOP 5</h3>
          <div className="space-y-4">
            {stats.topProducts.map((product, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-sm font-medium text-blue-600">{index + 1}</span>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{product.name}</p>
                    <p className="text-xs text-gray-500">{product.quantity}개 판매</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">
                    {formatCurrency(product.sales)}원
                  </p>
                  <p className="text-xs text-gray-500">
                    {Math.round((product.sales / stats.totalSales) * 100)}% 비중
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 직원 통계 */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">직원 통계</h3>
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <p className="text-2xl font-bold text-blue-600">{stats.employeeStats.total}</p>
              <p className="text-sm text-gray-600">전체 직원</p>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <p className="text-2xl font-bold text-green-600">{stats.employeeStats.active}</p>
              <p className="text-sm text-gray-600">활성 직원</p>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <p className="text-2xl font-bold text-purple-600">{stats.employeeStats.new}</p>
              <p className="text-sm text-gray-600">신규 채용</p>
            </div>
            <div className="text-center p-4 bg-yellow-50 rounded-lg">
              <p className="text-2xl font-bold text-yellow-600">{stats.employeeStats.turnover}%</p>
              <p className="text-sm text-gray-600">이직률</p>
            </div>
          </div>
          
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">직원 만족도</span>
              <span className="text-sm font-medium text-gray-900">4.2/5.0</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-blue-600 h-2 rounded-full" style={{ width: '84%' }}></div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">평균 근무 시간</span>
              <span className="text-sm font-medium text-gray-900">8.5시간</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-green-600 h-2 rounded-full" style={{ width: '85%' }}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 
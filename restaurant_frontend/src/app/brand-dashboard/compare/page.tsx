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
  Building2,
  Target,
  Award,
  AlertTriangle,
} from "lucide-react";

interface BranchComparison {
  id: number;
  name: string;
  sales: number;
  orders: number;
  employees: number;
  avgOrder: number;
  growth: number;
  efficiency: number;
  customerSatisfaction: number;
  monthlyData: {
    sales: number[];
    orders: number[];
    customers: number[];
  };
}

export default function ComparePage() {
  const [branches, setBranches] = useState<BranchComparison[]>([]);
  const [selectedBranches, setSelectedBranches] = useState<number[]>([1, 2]);
  const [isLoaded, setIsLoaded] = useState(false);
  const [compareMetric, setCompareMetric] = useState("sales");

  useEffect(() => {
    loadBranchData();
  }, []);

  const loadBranchData = async () => {
    // 실제로는 API 호출
    const mockBranches: BranchComparison[] = [
      {
        id: 1,
        name: "강남점",
        sales: 9200000,
        orders: 175,
        employees: 12,
        avgOrder: 52571,
        growth: 8.5,
        efficiency: 92,
        customerSatisfaction: 4.6,
        monthlyData: {
          sales: [8500000, 8700000, 8900000, 9000000, 9100000, 9200000],
          orders: [160, 165, 168, 170, 172, 175],
          customers: [1200, 1250, 1280, 1300, 1320, 1350],
        },
      },
      {
        id: 2,
        name: "홍대점",
        sales: 7800000,
        orders: 142,
        employees: 10,
        avgOrder: 54930,
        growth: 5.2,
        efficiency: 88,
        customerSatisfaction: 4.4,
        monthlyData: {
          sales: [7200000, 7400000, 7500000, 7600000, 7700000, 7800000],
          orders: [130, 135, 138, 140, 141, 142],
          customers: [1100, 1120, 1140, 1160, 1180, 1200],
        },
      },
      {
        id: 3,
        name: "부산점",
        sales: 6800000,
        orders: 98,
        employees: 8,
        avgOrder: 69388,
        growth: 3.8,
        efficiency: 85,
        customerSatisfaction: 4.3,
        monthlyData: {
          sales: [6500000, 6600000, 6650000, 6700000, 6750000, 6800000],
          orders: [90, 92, 94, 95, 97, 98],
          customers: [800, 820, 840, 860, 880, 900],
        },
      },
      {
        id: 4,
        name: "대구점",
        sales: 6100000,
        orders: 87,
        employees: 9,
        avgOrder: 70115,
        growth: 2.1,
        efficiency: 82,
        customerSatisfaction: 4.2,
        monthlyData: {
          sales: [5900000, 5950000, 6000000, 6050000, 6080000, 6100000],
          orders: [82, 83, 84, 85, 86, 87],
          customers: [750, 760, 770, 780, 790, 800],
        },
      },
      {
        id: 5,
        name: "인천점",
        sales: 7800000,
        orders: 142,
        employees: 11,
        avgOrder: 54930,
        growth: 6.7,
        efficiency: 90,
        customerSatisfaction: 4.5,
        monthlyData: {
          sales: [7200000, 7400000, 7500000, 7600000, 7700000, 7800000],
          orders: [130, 135, 138, 140, 141, 142],
          customers: [1100, 1120, 1140, 1160, 1180, 1200],
        },
      },
    ];

    setBranches(mockBranches);
    setIsLoaded(true);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ko-KR').format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${value > 0 ? '+' : ''}${value.toFixed(1)}%`;
  };

  const getMetricValue = (branch: BranchComparison, metric: string) => {
    switch (metric) {
      case "sales":
        return branch.sales;
      case "orders":
        return branch.orders;
      case "employees":
        return branch.employees;
      case "avgOrder":
        return branch.avgOrder;
      case "growth":
        return branch.growth;
      case "efficiency":
        return branch.efficiency;
      case "satisfaction":
        return branch.customerSatisfaction;
      default:
        return branch.sales;
    }
  };

  const getMetricLabel = (metric: string) => {
    switch (metric) {
      case "sales":
        return "매출";
      case "orders":
        return "주문 수";
      case "employees":
        return "직원 수";
      case "avgOrder":
        return "평균 주문";
      case "growth":
        return "성장률";
      case "efficiency":
        return "효율성";
      case "satisfaction":
        return "고객 만족도";
      default:
        return "매출";
    }
  };

  const getMetricUnit = (metric: string) => {
    switch (metric) {
      case "sales":
      case "avgOrder":
        return "원";
      case "orders":
      case "employees":
        return "개/명";
      case "growth":
      case "efficiency":
        return "%";
      case "satisfaction":
        return "/5.0";
      default:
        return "";
    }
  };

  const getMetricIcon = (metric: string) => {
    switch (metric) {
      case "sales":
        return <DollarSign className="h-5 w-5" />;
      case "orders":
        return <ShoppingCart className="h-5 w-5" />;
      case "employees":
        return <Users className="h-5 w-5" />;
      case "avgOrder":
        return <BarChart3 className="h-5 w-5" />;
      case "growth":
        return <TrendingUp className="h-5 w-5" />;
      case "efficiency":
        return <Target className="h-5 w-5" />;
      case "satisfaction":
        return <Award className="h-5 w-5" />;
      default:
        return <BarChart3 className="h-5 w-5" />;
    }
  };

  const getComparisonResult = (branch1: BranchComparison, branch2: BranchComparison, metric: string) => {
    const value1 = getMetricValue(branch1, metric);
    const value2 = getMetricValue(branch2, metric);
    const diff = value1 - value2;
    const percentage = value2 > 0 ? (diff / value2) * 100 : 0;

    if (diff > 0) {
      return { type: "better", value: diff, percentage };
    } else if (diff < 0) {
      return { type: "worse", value: Math.abs(diff), percentage: Math.abs(percentage) };
    } else {
      return { type: "equal", value: 0, percentage: 0 };
    }
  };

  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">비교 데이터 로딩 중...</p>
        </div>
      </div>
    );
  }

  const selectedBranchData = branches.filter(b => selectedBranches.includes(b.id));
  const branch1 = selectedBranchData[0];
  const branch2 = selectedBranchData[1];

  return (
    <div className="p-8">
      {/* 헤더 */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">매장 비교 분석</h1>
            <p className="text-gray-600 mt-2">매장 간 성과 비교 및 분석</p>
          </div>
          <div className="flex items-center space-x-4">
            <select
              value={compareMetric}
              onChange={(e) => setCompareMetric(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="sales">매출</option>
              <option value="orders">주문 수</option>
              <option value="employees">직원 수</option>
              <option value="avgOrder">평균 주문</option>
              <option value="growth">성장률</option>
              <option value="efficiency">효율성</option>
              <option value="satisfaction">고객 만족도</option>
            </select>
          </div>
        </div>
      </div>

      {/* 매장 선택 */}
      <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">비교할 매장 선택</h3>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {branches.map((branch) => (
            <button
              key={branch.id}
              onClick={() => {
                if (selectedBranches.includes(branch.id)) {
                  setSelectedBranches(selectedBranches.filter(id => id !== branch.id));
                } else if (selectedBranches.length < 2) {
                  setSelectedBranches([...selectedBranches, branch.id]);
                }
              }}
              className={`p-4 border rounded-lg transition-colors ${
                selectedBranches.includes(branch.id)
                  ? "border-blue-500 bg-blue-50"
                  : "border-gray-200 hover:border-gray-300"
              }`}
            >
              <div className="flex items-center space-x-2">
                <Building2 className="h-4 w-4 text-gray-400" />
                <span className="text-sm font-medium text-gray-900">{branch.name}</span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {selectedBranchData.length === 2 && (
        <>
          {/* 비교 결과 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            {selectedBranchData.map((branch) => (
              <div key={branch.id} className="bg-white rounded-lg shadow-sm border p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">{branch.name}</h3>
                  <div className="flex items-center space-x-2">
                    {getMetricIcon(compareMetric)}
                    <span className="text-sm text-gray-600">{getMetricLabel(compareMetric)}</span>
                  </div>
                </div>
                
                <div className="text-center mb-6">
                  <p className="text-3xl font-bold text-gray-900">
                    {compareMetric === "sales" || compareMetric === "avgOrder"
                      ? formatCurrency(getMetricValue(branch, compareMetric))
                      : getMetricValue(branch, compareMetric).toFixed(1)}
                    {getMetricUnit(compareMetric)}
                  </p>
                  {compareMetric === "growth" && (
                    <p className={`text-sm ${branch.growth > 0 ? "text-green-600" : "text-red-600"}`}>
                      {formatPercentage(branch.growth)}
                    </p>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-600">매출</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {formatCurrency(branch.sales)}원
                    </p>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-600">주문</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {branch.orders}건
                    </p>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-600">직원</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {branch.employees}명
                    </p>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-600">효율성</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {branch.efficiency}%
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* 비교 분석 */}
          <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">비교 분석 결과</h3>
            {branch1 && branch2 && (
              <div className="space-y-4">
                {(() => {
                  const result = getComparisonResult(branch1, branch2, compareMetric);
                  return (
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-gray-600">차이점</p>
                          <p className="text-lg font-semibold text-gray-900">
                            {result.type === "better" && `${branch1.name}이(가) ${branch2.name}보다`}
                            {result.type === "worse" && `${branch2.name}이(가) ${branch1.name}보다`}
                            {result.type === "equal" && "두 매장이 동일한 성과"}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-gray-600">차이</p>
                          <p className={`text-lg font-semibold ${
                            result.type === "better" ? "text-green-600" : 
                            result.type === "worse" ? "text-red-600" : "text-gray-600"
                          }`}>
                            {compareMetric === "sales" || compareMetric === "avgOrder"
                              ? formatCurrency(result.value)
                              : result.value.toFixed(1)}
                            {getMetricUnit(compareMetric)}
                          </p>
                          {result.percentage > 0 && (
                            <p className="text-sm text-gray-500">
                              ({result.percentage.toFixed(1)}% 차이)
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })()}

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 border border-gray-200 rounded-lg">
                    <h4 className="font-medium text-gray-900 mb-2">고객 만족도</h4>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">{branch1.name}</span>
                      <span className="text-sm font-medium">{branch1.customerSatisfaction}/5.0</span>
                    </div>
                    <div className="flex items-center justify-between mt-1">
                      <span className="text-sm text-gray-600">{branch2.name}</span>
                      <span className="text-sm font-medium">{branch2.customerSatisfaction}/5.0</span>
                    </div>
                  </div>

                  <div className="p-4 border border-gray-200 rounded-lg">
                    <h4 className="font-medium text-gray-900 mb-2">성장률</h4>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">{branch1.name}</span>
                      <span className={`text-sm font-medium ${branch1.growth > 0 ? "text-green-600" : "text-red-600"}`}>
                        {formatPercentage(branch1.growth)}
                      </span>
                    </div>
                    <div className="flex items-center justify-between mt-1">
                      <span className="text-sm text-gray-600">{branch2.name}</span>
                      <span className={`text-sm font-medium ${branch2.growth > 0 ? "text-green-600" : "text-red-600"}`}>
                        {formatPercentage(branch2.growth)}
                      </span>
                    </div>
                  </div>

                  <div className="p-4 border border-gray-200 rounded-lg">
                    <h4 className="font-medium text-gray-900 mb-2">효율성</h4>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">{branch1.name}</span>
                      <span className="text-sm font-medium">{branch1.efficiency}%</span>
                    </div>
                    <div className="flex items-center justify-between mt-1">
                      <span className="text-sm text-gray-600">{branch2.name}</span>
                      <span className="text-sm font-medium">{branch2.efficiency}%</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </>
      )}

      {selectedBranchData.length < 2 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <AlertTriangle className="h-8 w-8 text-yellow-600 mx-auto mb-2" />
          <p className="text-yellow-800">비교할 매장을 2개 선택해주세요.</p>
        </div>
      )}
    </div>
  );
} 
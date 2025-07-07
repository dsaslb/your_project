"use client";
import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  Building2,
  Users,
  Calendar,
  ShoppingCart,
  Package,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Clock,
  MapPin,
  Phone,
  Mail,
  ArrowLeft,
  BarChart3,
  AlertTriangle,
  CheckCircle,
  XCircle,
} from "lucide-react";

interface BranchDetail {
  id: number;
  name: string;
  address: string;
  phone: string;
  email: string;
  manager: string;
  status: string;
  employees: number;
  sales: number;
  orders: number;
  monthlySales: number[];
  monthlyOrders: number[];
  employeeStats: {
    total: number;
    active: number;
    onLeave: number;
    new: number;
  };
  inventoryStats: {
    total: number;
    low: number;
    out: number;
  };
  recentActivities: Array<{
    id: number;
    type: string;
    message: string;
    time: string;
    status: string;
  }>;
}

export default function BranchDetailPage() {
  const params = useParams();
  const router = useRouter();
  const branchId = Number(params.id);
  const [branch, setBranch] = useState<BranchDetail | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    loadBranchDetail();
  }, [branchId]);

  const loadBranchDetail = async () => {
    // 실제로는 API 호출
    const mockBranch: BranchDetail = {
      id: branchId,
      name: `${getBranchName(branchId)}`,
      address: getBranchAddress(branchId),
      phone: getBranchPhone(branchId),
      email: `${getBranchName(branchId).toLowerCase()}@restaurant.com`,
      manager: getBranchManager(branchId),
      status: "운영중",
      employees: 12,
      sales: 8500000,
      orders: 156,
      monthlySales: [7200000, 7800000, 8200000, 8500000, 8800000, 9200000],
      monthlyOrders: [120, 135, 142, 156, 168, 175],
      employeeStats: {
        total: 12,
        active: 10,
        onLeave: 1,
        new: 1,
      },
      inventoryStats: {
        total: 150,
        low: 8,
        out: 2,
      },
      recentActivities: [
        {
          id: 1,
          type: "order",
          message: "새로운 발주 요청",
          time: "5분 전",
          status: "pending",
        },
        {
          id: 2,
          type: "employee",
          message: "김철수 직원 출근",
          time: "10분 전",
          status: "completed",
        },
        {
          id: 3,
          type: "inventory",
          message: "토마토 재고 부족",
          time: "30분 전",
          status: "warning",
        },
        {
          id: 4,
          type: "sales",
          message: "일일 매출 목표 달성",
          time: "1시간 전",
          status: "completed",
        },
      ],
    };

    setBranch(mockBranch);
    setIsLoaded(true);
  };

  const getBranchName = (id: number) => {
    const names = ["", "강남점", "홍대점", "부산점", "대구점", "인천점"];
    return names[id] || "알 수 없음";
  };

  const getBranchAddress = (id: number) => {
    const addresses = [
      "",
      "서울시 강남구 테헤란로 123",
      "서울시 마포구 홍대로 456",
      "부산시 해운대구 해운대로 789",
      "대구시 중구 동성로 321",
      "인천시 연수구 송도대로 654",
    ];
    return addresses[id] || "주소 없음";
  };

  const getBranchPhone = (id: number) => {
    const phones = [
      "",
      "02-1234-5678",
      "02-2345-6789",
      "051-3456-7890",
      "053-4567-8901",
      "032-5678-9012",
    ];
    return phones[id] || "전화번호 없음";
  };

  const getBranchManager = (id: number) => {
    const managers = ["", "김강남", "이홍대", "박부산", "최대구", "정인천"];
    return managers[id] || "관리자 없음";
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ko-KR').format(amount);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "text-green-600 bg-green-100";
      case "pending":
        return "text-yellow-600 bg-yellow-100";
      case "warning":
        return "text-orange-600 bg-orange-100";
      case "error":
        return "text-red-600 bg-red-100";
      default:
        return "text-gray-600 bg-gray-100";
    }
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case "order":
        return <ShoppingCart className="h-4 w-4" />;
      case "employee":
        return <Users className="h-4 w-4" />;
      case "inventory":
        return <Package className="h-4 w-4" />;
      case "sales":
        return <DollarSign className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  if (!isLoaded || !branch) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">매장 정보 로딩 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      {/* 헤더 */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => router.push("/brand-dashboard/branches")}
              className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <ArrowLeft className="h-5 w-5" />
            </button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{branch.name} 상세 대시보드</h1>
              <p className="text-gray-600 mt-2">매장별 상세 정보 및 실시간 현황</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(branch.status === "운영중" ? "completed" : "warning")}`}>
              {branch.status}
            </span>
          </div>
        </div>
      </div>

      {/* 매장 정보 카드 */}
      <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-blue-100 rounded-full">
              <Building2 className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">{branch.name}</h2>
              <p className="text-gray-600 flex items-center">
                <MapPin className="h-4 w-4 mr-1" />
                {branch.address}
              </p>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <Users className="h-4 w-4 text-gray-400" />
              <span className="text-sm text-gray-600">매장 관리자: {branch.manager}</span>
            </div>
            <div className="flex items-center space-x-2">
              <Phone className="h-4 w-4 text-gray-400" />
              <span className="text-sm text-gray-600">{branch.phone}</span>
            </div>
            <div className="flex items-center space-x-2">
              <Mail className="h-4 w-4 text-gray-400" />
              <span className="text-sm text-gray-600">{branch.email}</span>
            </div>
          </div>
        </div>
      </div>

      {/* 주요 통계 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">총 매출</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(branch.sales)}원
              </p>
            </div>
            <TrendingUp className="h-8 w-8 text-green-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">총 주문</p>
              <p className="text-2xl font-bold text-gray-900">
                {branch.orders}건
              </p>
            </div>
            <ShoppingCart className="h-8 w-8 text-blue-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">직원 수</p>
              <p className="text-2xl font-bold text-gray-900">
                {branch.employees}명
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
                {formatCurrency(Math.round(branch.sales / branch.orders))}원
              </p>
            </div>
            <BarChart3 className="h-8 w-8 text-indigo-600" />
          </div>
        </div>
      </div>

      {/* 상세 통계 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* 직원 현황 */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">직원 현황</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <p className="text-2xl font-bold text-blue-600">{branch.employeeStats.total}</p>
              <p className="text-sm text-gray-600">전체 직원</p>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <p className="text-2xl font-bold text-green-600">{branch.employeeStats.active}</p>
              <p className="text-sm text-gray-600">활성 직원</p>
            </div>
            <div className="text-center p-4 bg-yellow-50 rounded-lg">
              <p className="text-2xl font-bold text-yellow-600">{branch.employeeStats.onLeave}</p>
              <p className="text-sm text-gray-600">휴가 중</p>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <p className="text-2xl font-bold text-purple-600">{branch.employeeStats.new}</p>
              <p className="text-sm text-gray-600">신규 직원</p>
            </div>
          </div>
        </div>

        {/* 재고 현황 */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">재고 현황</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <p className="text-2xl font-bold text-green-600">{branch.inventoryStats.total}</p>
              <p className="text-sm text-gray-600">전체 품목</p>
            </div>
            <div className="text-center p-4 bg-yellow-50 rounded-lg">
              <p className="text-2xl font-bold text-yellow-600">{branch.inventoryStats.low}</p>
              <p className="text-sm text-gray-600">재고 부족</p>
            </div>
            <div className="text-center p-4 bg-red-50 rounded-lg">
              <p className="text-2xl font-bold text-red-600">{branch.inventoryStats.out}</p>
              <p className="text-sm text-gray-600">품절</p>
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <p className="text-2xl font-bold text-blue-600">
                {Math.round(((branch.inventoryStats.total - branch.inventoryStats.low - branch.inventoryStats.out) / branch.inventoryStats.total) * 100)}%
              </p>
              <p className="text-sm text-gray-600">재고율</p>
            </div>
          </div>
        </div>
      </div>

      {/* 최근 활동 */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">최근 활동</h3>
        <div className="space-y-3">
          {branch.recentActivities.map((activity) => (
            <div key={activity.id} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
              <div className="flex-shrink-0">
                {getActivityIcon(activity.type)}
              </div>
              <div className="flex-1">
                <p className="text-sm text-gray-900">{activity.message}</p>
                <p className="text-xs text-gray-500">{activity.time}</p>
              </div>
              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(activity.status)}`}>
                {activity.status === "completed" && "완료"}
                {activity.status === "pending" && "대기"}
                {activity.status === "warning" && "경고"}
                {activity.status === "error" && "오류"}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
} 
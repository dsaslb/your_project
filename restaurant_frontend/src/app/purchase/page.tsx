"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  Plus,
  Search,
  Package,
  AlertTriangle,
  CheckCircle,
  Clock,
  X,
  Calendar,
  User,
  DollarSign,
  Truck,
  FileText,
} from "lucide-react";
import NotificationPopup from "@/components/NotificationPopup";

export default function PurchasePage() {
  const router = useRouter();
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    setIsLoaded(true);
  }, []);

  // 발주 데이터
  const purchases = [
    {
      id: 1,
      item: "소고기",
      quantity: 50,
      unit: "kg",
      order_date: "2025-03-03",
      ordered_by: "홍길동",
      status: "대기중",
      detail: "한우 등급 소고기",
      memo: "급하게 필요합니다",
      supplier: "한우공급업체",
      estimated_cost: 2250000,
      created_at: "2025-03-03T10:00:00Z"
    },
    {
      id: 2,
      item: "양파",
      quantity: 100,
      unit: "kg",
      order_date: "2025-03-02",
      ordered_by: "김철수",
      status: "승인됨",
      detail: "신선한 양파",
      memo: "",
      supplier: "채소공급업체",
      estimated_cost: 300000,
      created_at: "2025-03-02T14:30:00Z"
    },
    {
      id: 3,
      item: "고추장",
      quantity: 20,
      unit: "kg",
      order_date: "2025-03-01",
      ordered_by: "이영희",
      status: "배송완료",
      detail: "전통 고추장",
      memo: "이미 배송완료",
      supplier: "조미료공급업체",
      estimated_cost: 240000,
      created_at: "2025-03-01T09:15:00Z"
    },
    {
      id: 4,
      item: "김치",
      quantity: 30,
      unit: "kg",
      order_date: "2025-02-28",
      ordered_by: "박민수",
      status: "거절됨",
      detail: "맛김치",
      memo: "예산 초과로 거절",
      supplier: "김치공급업체",
      estimated_cost: 240000,
      created_at: "2025-02-28T16:45:00Z"
    },
    {
      id: 5,
      item: "돼지고기",
      quantity: 80,
      unit: "kg",
      order_date: "2025-03-03",
      ordered_by: "최지영",
      status: "대기중",
      detail: "삼겹살용 돼지고기",
      memo: "신선도 중요",
      supplier: "돈육공급업체",
      estimated_cost: 2240000,
      created_at: "2025-03-03T11:20:00Z"
    },
    {
      id: 6,
      item: "쌀",
      quantity: 200,
      unit: "kg",
      order_date: "2025-03-02",
      ordered_by: "정현우",
      status: "배송중",
      detail: "고급 쌀",
      memo: "배송 예정일 확인 필요",
      supplier: "쌀공급업체",
      estimated_cost: 900000,
      created_at: "2025-03-02T13:10:00Z"
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case "대기중":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400";
      case "승인됨":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400";
      case "배송중":
        return "bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400";
      case "배송완료":
        return "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400";
      case "거절됨":
        return "bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "대기중":
        return <Clock className="h-4 w-4" />;
      case "승인됨":
        return <CheckCircle className="h-4 w-4" />;
      case "배송중":
        return <Truck className="h-4 w-4" />;
      case "배송완료":
        return <Package className="h-4 w-4" />;
      case "거절됨":
        return <X className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">발주 관리</h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            재료 발주 현황을 확인하고 새로운 발주를 관리하세요.
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 dark:bg-yellow-900/20 rounded-lg">
                <Clock className="h-6 w-6 text-yellow-600 dark:text-yellow-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">대기 발주</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {purchases.filter(p => p.status === "대기중").length}건
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
                <CheckCircle className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">승인됨</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {purchases.filter(p => p.status === "승인됨").length}건
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 dark:bg-purple-900/20 rounded-lg">
                <Truck className="h-6 w-6 text-purple-600 dark:text-purple-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">배송중</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {purchases.filter(p => p.status === "배송중").length}건
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg">
                <DollarSign className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">총 발주액</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  ₩{purchases.reduce((sum, p) => sum + p.estimated_cost, 0).toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6">
          <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
            <div className="flex flex-col sm:flex-row gap-4 flex-1">
              {/* Search */}
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="발주 검색..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>

              {/* Filter */}
              <select className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white">
                <option value="">전체 상태</option>
                <option value="pending">대기중</option>
                <option value="approved">승인됨</option>
                <option value="shipping">배송중</option>
                <option value="delivered">배송완료</option>
                <option value="rejected">거절됨</option>
              </select>
            </div>

            {/* Add Button */}
            <button 
              onClick={() => router.push('/purchase/add')}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <Plus className="h-4 w-4" />
              발주 추가
            </button>
          </div>
        </div>

        {/* Purchases List */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">발주 목록</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    발주번호
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    품목
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    수량
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    공급업체
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    발주자
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    상태
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    발주일
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    예상비용
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    작업
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {purchases.map((purchase) => (
                  <tr key={purchase.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                      #{purchase.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900 dark:text-white">{purchase.item}</div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">{purchase.detail}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {purchase.quantity} {purchase.unit}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {purchase.supplier}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {purchase.ordered_by}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(purchase.status)}`}>
                        {getStatusIcon(purchase.status)}
                        <span className="ml-1">{purchase.status}</span>
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {purchase.order_date}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      ₩{purchase.estimated_cost.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end space-x-2">
                        {purchase.status === "대기중" && (
                          <>
                            <button className="text-green-600 hover:text-green-900 dark:hover:text-green-400">
                              승인
                            </button>
                            <button className="text-red-600 hover:text-red-900 dark:hover:text-red-400">
                              거절
                            </button>
                          </>
                        )}
                        {purchase.status === "승인됨" && (
                          <button className="text-blue-600 hover:text-blue-900 dark:hover:text-blue-400">
                            배송시작
                          </button>
                        )}
                        {purchase.status === "배송중" && (
                          <button className="text-green-600 hover:text-green-900 dark:hover:text-green-400">
                            배송완료
                          </button>
                        )}
                        <button className="text-gray-600 hover:text-gray-900 dark:hover:text-gray-400">
                          상세보기
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* 알림창 */}
      <NotificationPopup 
        message="새로운 발주 요청이 있습니다! 빠르게 확인해보세요." 
        delay={1000}
      />
    </div>
  );
} 
"use client";
import { useState, useEffect } from "react";
import Image from "next/image";
import {
  ChevronLeft,
  ChevronRight,
  Plus,
  Search,
  Settings,
  Menu,
  Clock,
  MapPin,
  Users,
  Calendar,
  Pause,
  Sparkles,
  X,
  User,
  Phone,
  Mail,
  ShoppingCart,
  CheckCircle,
  AlertCircle,
  Clock as ClockIcon,
} from "lucide-react";
import NotificationPopup from "@/components/NotificationPopup";

export default function OrdersPage() {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    setIsLoaded(true);
  }, []);

  const togglePlay = () => {
    setIsPlaying(!isPlaying);
  };

  // 주문 데이터
  const orders = [
    {
      id: "ORD-001",
      customerName: "김철수",
      phone: "010-1234-5678",
      items: [
        { name: "불고기", quantity: 2, price: 15000 },
        { name: "김치찌개", quantity: 1, price: 12000 },
      ],
      total: 42000,
      status: "대기중",
      orderTime: "2025-03-03 12:30",
      estimatedTime: "13:00",
      table: "A-3",
      notes: "매운맛으로 해주세요",
    },
    {
      id: "ORD-002",
      customerName: "이영희",
      phone: "010-2345-6789",
      items: [
        { name: "제육볶음", quantity: 1, price: 14000 },
        { name: "된장찌개", quantity: 1, price: 11000 },
        { name: "공기밥", quantity: 2, price: 1000 },
      ],
      total: 37000,
      status: "조리중",
      orderTime: "2025-03-03 12:25",
      estimatedTime: "12:55",
      table: "B-1",
      notes: "",
    },
    {
      id: "ORD-003",
      customerName: "박민수",
      phone: "010-3456-7890",
      items: [
        { name: "삼겹살", quantity: 2, price: 18000 },
        { name: "소주", quantity: 2, price: 4000 },
      ],
      total: 44000,
      status: "완료",
      orderTime: "2025-03-03 12:20",
      estimatedTime: "12:50",
      table: "C-2",
      notes: "양념장 많이 주세요",
    },
    {
      id: "ORD-004",
      customerName: "최지영",
      phone: "010-4567-8901",
      items: [
        { name: "치킨", quantity: 1, price: 20000 },
        { name: "콜라", quantity: 1, price: 2000 },
      ],
      total: 22000,
      status: "대기중",
      orderTime: "2025-03-03 12:35",
      estimatedTime: "13:05",
      table: "A-1",
      notes: "양념치킨으로 해주세요",
    },
    {
      id: "ORD-005",
      customerName: "정현우",
      phone: "010-5678-9012",
      items: [
        { name: "파스타", quantity: 1, price: 16000 },
        { name: "샐러드", quantity: 1, price: 8000 },
        { name: "와인", quantity: 1, price: 12000 },
      ],
      total: 36000,
      status: "조리중",
      orderTime: "2025-03-03 12:15",
      estimatedTime: "12:45",
      table: "D-4",
      notes: "와인은 차갑게",
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case "대기중":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400";
      case "조리중":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400";
      case "완료":
        return "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400";
      case "취소":
        return "bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "대기중":
        return <ClockIcon className="h-4 w-4" />;
      case "조리중":
        return <AlertCircle className="h-4 w-4" />;
      case "완료":
        return <CheckCircle className="h-4 w-4" />;
      case "취소":
        return <X className="h-4 w-4" />;
      default:
        return <ClockIcon className="h-4 w-4" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">주문 관리</h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            주문 현황을 실시간으로 확인하고 관리하세요.
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 dark:bg-yellow-900/20 rounded-lg">
                <ClockIcon className="h-6 w-6 text-yellow-600 dark:text-yellow-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">대기 주문</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {orders.filter(o => o.status === "대기중").length}건
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
                <AlertCircle className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">조리중</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {orders.filter(o => o.status === "조리중").length}건
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg">
                <CheckCircle className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">완료</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {orders.filter(o => o.status === "완료").length}건
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 dark:bg-purple-900/20 rounded-lg">
                <ShoppingCart className="h-6 w-6 text-purple-600 dark:text-purple-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">오늘 매출</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  ₩{orders.reduce((sum, order) => sum + order.total, 0).toLocaleString()}
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
                  placeholder="주문 검색..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>

              {/* Filter */}
              <select className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white">
                <option value="">전체 상태</option>
                <option value="waiting">대기중</option>
                <option value="cooking">조리중</option>
                <option value="completed">완료</option>
                <option value="cancelled">취소</option>
              </select>
            </div>

            {/* Add Button */}
            <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2">
              <Plus className="h-4 w-4" />
              주문 추가
            </button>
          </div>
        </div>

        {/* Orders List */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">주문 목록</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    주문번호
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    고객정보
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    주문내용
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    금액
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    상태
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    주문시간
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    테이블
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    작업
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {orders.map((order) => (
                  <tr key={order.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                      {order.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900 dark:text-white">{order.customerName}</div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">{order.phone}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900 dark:text-white">
                        {order.items.map(item => `${item.name} x${item.quantity}`).join(", ")}
                      </div>
                      {order.notes && (
                        <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          요청사항: {order.notes}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      ₩{order.total.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(order.status)}`}>
                        {getStatusIcon(order.status)}
                        <span className="ml-1">{order.status}</span>
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900 dark:text-white">{order.orderTime}</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        예상완료: {order.estimatedTime}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {order.table}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end space-x-2">
                        {order.status === "대기중" && (
                          <button className="text-blue-600 hover:text-blue-900 dark:hover:text-blue-400">
                            조리시작
                          </button>
                        )}
                        {order.status === "조리중" && (
                          <button className="text-green-600 hover:text-green-900 dark:hover:text-green-400">
                            완료
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
        message="새로운 주문이 들어왔습니다! 빠르게 확인해보세요." 
        delay={1000}
      />
    </div>
  );
} 
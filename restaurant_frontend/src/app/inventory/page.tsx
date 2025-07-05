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
  Package,
  AlertTriangle,
  TrendingDown,
  TrendingUp,
} from "lucide-react";
import NotificationPopup from "@/components/NotificationPopup";

export default function InventoryPage() {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    setIsLoaded(true);
  }, []);

  const togglePlay = () => {
    setIsPlaying(!isPlaying);
  };

  // 재고 데이터
  const inventory = [
    {
      id: 1,
      name: "소고기",
      category: "육류",
      currentStock: 15,
      minStock: 20,
      unit: "kg",
      price: 45000,
      supplier: "한우공급업체",
      lastUpdated: "2025-03-03",
      status: "부족",
    },
    {
      id: 2,
      name: "돼지고기",
      category: "육류",
      currentStock: 25,
      minStock: 15,
      unit: "kg",
      price: 28000,
      supplier: "돈육공급업체",
      lastUpdated: "2025-03-03",
      status: "충분",
    },
    {
      id: 3,
      name: "닭고기",
      category: "육류",
      currentStock: 30,
      minStock: 20,
      unit: "kg",
      price: 15000,
      supplier: "닭고기공급업체",
      lastUpdated: "2025-03-02",
      status: "충분",
    },
    {
      id: 4,
      name: "양파",
      category: "채소",
      currentStock: 8,
      minStock: 10,
      unit: "kg",
      price: 3000,
      supplier: "채소공급업체",
      lastUpdated: "2025-03-03",
      status: "부족",
    },
    {
      id: 5,
      name: "당근",
      category: "채소",
      currentStock: 12,
      minStock: 8,
      unit: "kg",
      price: 2500,
      supplier: "채소공급업체",
      lastUpdated: "2025-03-02",
      status: "충분",
    },
    {
      id: 6,
      name: "김치",
      category: "반찬",
      currentStock: 5,
      minStock: 8,
      unit: "kg",
      price: 8000,
      supplier: "김치공급업체",
      lastUpdated: "2025-03-01",
      status: "부족",
    },
    {
      id: 7,
      name: "쌀",
      category: "곡물",
      currentStock: 50,
      minStock: 30,
      unit: "kg",
      price: 45000,
      supplier: "쌀공급업체",
      lastUpdated: "2025-03-02",
      status: "충분",
    },
    {
      id: 8,
      name: "고추장",
      category: "조미료",
      currentStock: 3,
      minStock: 5,
      unit: "kg",
      price: 12000,
      supplier: "조미료공급업체",
      lastUpdated: "2025-03-03",
      status: "부족",
    },
    {
      id: 9,
      name: "된장",
      category: "조미료",
      currentStock: 6,
      minStock: 4,
      unit: "kg",
      price: 8000,
      supplier: "조미료공급업체",
      lastUpdated: "2025-03-02",
      status: "충분",
    },
    {
      id: 10,
      name: "간장",
      category: "조미료",
      currentStock: 4,
      minStock: 6,
      unit: "L",
      price: 15000,
      supplier: "조미료공급업체",
      lastUpdated: "2025-03-01",
      status: "부족",
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case "부족":
        return "bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400";
      case "충분":
        return "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400";
      case "위험":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400";
    }
  };

  const getStockLevel = (current: number, min: number) => {
    const ratio = current / min;
    if (ratio < 0.8) return "부족";
    if (ratio < 1.2) return "위험";
    return "충분";
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">재고 관리</h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            재고 현황을 실시간으로 확인하고 발주를 관리하세요.
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
                <Package className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">전체 품목</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{inventory.length}개</p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-red-100 dark:bg-red-900/20 rounded-lg">
                <AlertTriangle className="h-6 w-6 text-red-600 dark:text-red-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">부족 품목</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {inventory.filter(item => item.status === "부족").length}개
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg">
                <TrendingUp className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">충분 품목</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {inventory.filter(item => item.status === "충분").length}개
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 dark:bg-purple-900/20 rounded-lg">
                <TrendingDown className="h-6 w-6 text-purple-600 dark:text-purple-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">총 재고가치</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  ₩{inventory.reduce((sum, item) => sum + (item.currentStock * item.price), 0).toLocaleString()}
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
                  placeholder="품목 검색..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>

              {/* Filter */}
              <select className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white">
                <option value="">전체 카테고리</option>
                <option value="육류">육류</option>
                <option value="채소">채소</option>
                <option value="반찬">반찬</option>
                <option value="곡물">곡물</option>
                <option value="조미료">조미료</option>
              </select>

              <select className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white">
                <option value="">전체 상태</option>
                <option value="부족">부족</option>
                <option value="충분">충분</option>
                <option value="위험">위험</option>
              </select>
            </div>

            {/* Add Button */}
            <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2">
              <Plus className="h-4 w-4" />
              품목 추가
            </button>
          </div>
        </div>

        {/* Inventory List */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">재고 목록</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    품목명
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    카테고리
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    현재재고
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    최소재고
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    단가
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    상태
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    공급업체
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    최종업데이트
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    작업
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {inventory.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900 dark:text-white">{item.name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {item.category}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900 dark:text-white">
                        {item.currentStock} {item.unit}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {item.minStock} {item.unit}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      ₩{item.price.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(item.status)}`}>
                        {item.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {item.supplier}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {item.lastUpdated}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end space-x-2">
                        {item.status === "부족" && (
                          <button className="text-blue-600 hover:text-blue-900 dark:hover:text-blue-400">
                            발주
                          </button>
                        )}
                        <button className="text-gray-600 hover:text-gray-900 dark:hover:text-gray-400">
                          수정
                        </button>
                        <button className="text-red-600 hover:text-red-900 dark:hover:text-red-400">
                          삭제
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
        message="재고 부족 알림: 소고기, 양파, 김치, 고추장, 간장이 부족합니다. 발주를 진행해주세요." 
        delay={2500}
      />
    </div>
  );
} 
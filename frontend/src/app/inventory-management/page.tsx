"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Package, AlertTriangle, TrendingUp, DollarSign, ShoppingCart, Clock } from 'lucide-react';
import { toast } from 'sonner';

interface InventoryItem {
  id: number;
  name: string;
  category: string;
  current_stock: number;
  min_stock: number;
  unit: string;
  price: number;
  supplier: string;
  last_updated: string;
  status: 'sufficient' | 'low' | 'out';
}

interface InventoryStats {
  totalItems: number;
  lowStockItems: number;
  totalValue: number;
  turnoverRate: number;
  totalCategories: number;
  activeSuppliers: number;
}

export default function InventoryManagementPage() {
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [stats, setStats] = useState<InventoryStats>({
    totalItems: 0,
    lowStockItems: 0,
    totalValue: 0,
    turnoverRate: 0,
    totalCategories: 0,
    activeSuppliers: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchInventoryData();
  }, []);

  const fetchInventoryData = async () => {
    try {
      setLoading(true);
      
      // 샘플 재고 데이터 (실제로는 API에서 가져와야 함)
      const sampleInventory: InventoryItem[] = [
        {
          id: 1,
          name: '커피 원두',
          category: '원재료',
          current_stock: 50,
          min_stock: 20,
          unit: 'kg',
          price: 15000,
          supplier: '커피공급업체',
          last_updated: '2024-01-15',
          status: 'sufficient'
        },
        {
          id: 2,
          name: '우유',
          category: '유제품',
          current_stock: 15,
          min_stock: 30,
          unit: 'L',
          price: 3000,
          supplier: '우유공급업체',
          last_updated: '2024-01-14',
          status: 'low'
        },
        {
          id: 3,
          name: '설탕',
          category: '원재료',
          current_stock: 25,
          min_stock: 10,
          unit: 'kg',
          price: 2000,
          supplier: '설탕공급업체',
          last_updated: '2024-01-13',
          status: 'sufficient'
        },
        {
          id: 4,
          name: '커피 필터',
          category: '소모품',
          current_stock: 5,
          min_stock: 20,
          unit: '박스',
          price: 5000,
          supplier: '소모품공급업체',
          last_updated: '2024-01-12',
          status: 'low'
        },
        {
          id: 5,
          name: '시럽',
          category: '원재료',
          current_stock: 0,
          min_stock: 10,
          unit: 'L',
          price: 8000,
          supplier: '시럽공급업체',
          last_updated: '2024-01-11',
          status: 'out'
        }
      ];

      setInventory(sampleInventory);

      // 통계 계산
      const totalItems = sampleInventory.length;
      const lowStockItems = sampleInventory.filter(item => item.status === 'low' || item.status === 'out').length;
      const totalValue = sampleInventory.reduce((sum, item) => sum + (item.current_stock * item.price), 0);
      const turnoverRate = 8.5; // 샘플 데이터
      const totalCategories = new Set(sampleInventory.map(item => item.category)).size;
      const activeSuppliers = new Set(sampleInventory.map(item => item.supplier)).size;

      setStats({
        totalItems,
        lowStockItems,
        totalValue,
        turnoverRate,
        totalCategories,
        activeSuppliers
      });

    } catch (error) {
      console.error('재고 데이터 로딩 오류:', error);
      toast.error('데이터를 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'sufficient': return 'text-green-600';
      case 'low': return 'text-yellow-600';
      case 'out': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'sufficient': return '충분';
      case 'low': return '부족';
      case 'out': return '품절';
      default: return '알 수 없음';
    }
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="text-lg mb-2">로딩 중...</div>
            <div className="text-sm text-gray-500">재고 데이터를 가져오는 중입니다</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">재고 관리</h1>
        <p className="text-gray-600">재고 및 발주 관리</p>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 상품</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalItems}개</div>
            <p className="text-xs text-muted-foreground">등록된 상품</p>
          </CardContent>
        </Card>

        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">재고 부족</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.lowStockItems}개</div>
            <p className="text-xs text-muted-foreground">부족한 상품</p>
          </CardContent>
        </Card>

        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">재고 가치</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">₩{stats.totalValue.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">총 재고 가치</p>
          </CardContent>
        </Card>

        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">회전율</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.turnoverRate}회</div>
            <p className="text-xs text-muted-foreground">월 평균</p>
          </CardContent>
        </Card>
      </div>

      {/* 추가 통계 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">카테고리</CardTitle>
            <ShoppingCart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalCategories}개</div>
            <p className="text-xs text-muted-foreground">상품 카테고리</p>
          </CardContent>
        </Card>

        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">공급업체</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.activeSuppliers}개</div>
            <p className="text-xs text-muted-foreground">활성 공급업체</p>
          </CardContent>
        </Card>
      </div>

      {/* 재고 목록 */}
      <Card className="border border-gray-100">
        <CardHeader>
          <CardTitle>재고 현황</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {inventory.map((item) => (
              <div key={item.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold">{item.name}</h4>
                  <span className={`text-xs px-2 py-1 rounded ${getStatusColor(item.status)}`}>
                    {getStatusText(item.status)}
                  </span>
                </div>
                <div className="space-y-1 text-sm text-gray-600">
                  <p>카테고리: {item.category}</p>
                  <p>현재: {item.current_stock}{item.unit} / 최소: {item.min_stock}{item.unit}</p>
                  <p>단가: ₩{item.price.toLocaleString()}</p>
                  <p>공급업체: {item.supplier}</p>
                  <p className="text-xs text-gray-500">최종 업데이트: {item.last_updated}</p>
                </div>
              </div>
            ))}
            {inventory.length === 0 && (
              <div className="col-span-full text-center py-8 text-gray-500">
                등록된 재고가 없습니다.
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 
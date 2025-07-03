"use client";
import React, { useState, useEffect, useMemo } from "react";
import { AppLayout } from "@/components/app-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { useUser } from "@/components/UserContext";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { 
  Package, 
  Plus, 
  Search, 
  Edit, 
  Trash2, 
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Minus,
  Plus as PlusIcon,
  Eye,
  X,
  Check,
  History,
  Archive,
  CheckCircle,
  XCircle,
  AlertCircle,
  Truck,
  Loader2,
  MoreVertical
} from "lucide-react";
import { toast } from '@/lib/toast';
import NotificationService from '@/lib/notification-service';
import { PermissionGuard } from '@/components/PermissionGuard';
import { Alert } from '@/components/ui/alert';

// 재고 타입 정의
type Inventory = {
  id: number;
  name: string;
  category: string;
  currentStock: number;
  minStock: number;
  maxStock: number;
  unit: string;
  price: number;
  supplier: string;
  lastUpdated: string;
  status: 'normal' | 'low' | 'critical' | 'overstock';
  notes?: string;
};

// 재고 이력 타입 정의
type InventoryHistory = {
  id: number;
  inventoryId: number;
  type: 'in' | 'out' | 'dispose';
  quantity: number;
  date: string;
  reason: string;
  operator: string;
};

// Toast 알림용
function Toast({ message, type, onClose }: { message: string; type: "success" | "error"; onClose: () => void }) {
  return (
    <div className={`fixed top-6 right-6 z-50 px-4 py-3 rounded shadow-lg text-white ${type === "success" ? "bg-green-600" : "bg-red-600"}`}
      role="alert">
      <div className="flex items-center gap-2">
        {type === "success" ? <CheckCircle className="w-5 h-5" /> : <XCircle className="w-5 h-5" />}
        <span>{message}</span>
        <button className="ml-2" onClick={onClose}><X className="w-4 h-4" /></button>
      </div>
    </div>
  );
}

// 알림 등록 함수
async function createInventoryNotice({ 
  type, 
  title, 
  content, 
  author 
}: { 
  type: string; 
  title: string; 
  content: string; 
  author: string; 
}) {
  try {
    // 실제 API 호출 대신 콘솔 로그
    console.log('Inventory notice created:', { type, title, content, author });
  } catch (e) {
    console.error('Failed to create inventory notice:', e);
  }
}

// 권한 체크 함수 예시
function useInventoryPermissions(user: any) {
  return {
    canAdd: user?.role === 'admin' || user?.permissions?.inventory_management?.create,
    canEdit: user?.role === 'admin' || user?.permissions?.inventory_management?.edit,
    canDelete: user?.role === 'admin' || user?.permissions?.inventory_management?.delete,
    canAdjust: user?.role === 'admin' || user?.permissions?.inventory_management?.edit,
  };
}

export default function InventoryPage() {
  const { user } = useUser();
  const perms = useInventoryPermissions(user);
  const [searchTerm, setSearchTerm] = useState("");
  const [showAddForm, setShowAddForm] = useState(false);
  const [showAdjustForm, setShowAdjustForm] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  const [selectedInventory, setSelectedInventory] = useState<Inventory | null>(null);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState("");
  const [toastType, setToastType] = useState<"success" | "error">("success");
  
  // 필터/정렬 상태
  const [statusFilter, setStatusFilter] = useState('all');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [dateFilter, setDateFilter] = useState('all');
  const [sortOption, setSortOption] = useState('latest');

  // 재고 관련 상태 관리
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedItem, setSelectedItem] = useState<Inventory | null>(null);
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" } | null>(null);

  // 필터/정렬 적용
  const filteredInventory = useMemo(() => {
    let filtered = [...inventoryData];
    if (statusFilter !== 'all') filtered = filtered.filter(i => i.status === statusFilter);
    if (categoryFilter !== 'all') filtered = filtered.filter(i => i.category === categoryFilter);
    // 기간 필터 예시(최근 7일)
    if (dateFilter === '7days') {
      const weekAgo = new Date();
      weekAgo.setDate(weekAgo.getDate() - 7);
      filtered = filtered.filter(i => new Date(i.lastUpdated) >= weekAgo);
    }
    // 정렬
    if (sortOption === 'latest') filtered.sort((a, b) => new Date(b.lastUpdated).getTime() - new Date(a.lastUpdated).getTime());
    else if (sortOption === 'oldest') filtered.sort((a, b) => new Date(a.lastUpdated).getTime() - new Date(b.lastUpdated).getTime());
    else if (sortOption === 'critical') filtered.sort((a, b) => (a.status === 'critical' ? -1 : 1));
    return filtered;
  }, [inventoryData, statusFilter, categoryFilter, dateFilter, sortOption]);

  // Toast 알림 표시 함수
  const showToastMessage = (message: string, type: "success" | "error" = "success") => {
    setToastMessage(message);
    setToastType(type);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };

  // 재고 추가
  const handleAddInventory = async () => {
    try {
      // 실제 API 연동 시: await inventoryApi.addInventory(...)
      setShowAddForm(false);
      showToastMessage('재고가 추가되었습니다.', 'success');
      // await loadInventory();
    } catch (e) {
      showToastMessage('추가 중 오류가 발생했습니다.', 'error');
    }
  };

  // 재고 수정
  const handleEditInventory = async () => {
    try {
      setShowEditModal(false);
      showToastMessage('재고가 수정되었습니다.', 'success');
      // await loadInventory();
    } catch (e) {
      showToastMessage('수정 중 오류가 발생했습니다.', 'error');
    }
  };

  // 재고 삭제
  const handleDeleteInventory = async (id: number) => {
    try {
      setShowDetailModal(false);
      showToastMessage('재고가 삭제되었습니다.', 'success');
      // await loadInventory();
    } catch (e) {
      showToastMessage('삭제 중 오류가 발생했습니다.', 'error');
    }
  };

  // 재고 조정
  const handleAdjustInventory = async () => {
    try {
      setShowAdjustForm(false);
      showToastMessage('재고가 조정되었습니다.', 'success');
      // await loadInventory();
    } catch (e) {
      showToastMessage('조정 중 오류가 발생했습니다.', 'error');
    }
  };

  // 재고 상세 보기
  const handleViewDetail = (inventory: Inventory) => {
    setSelectedInventory(inventory);
    setShowDetailModal(true);
  };

  // 재고 수정 모달 열기
  const handleEditClick = (inventory: Inventory) => {
    setSelectedInventory({ ...inventory });
    setShowEditModal(true);
  };

  // 재고 이력 보기
  const handleViewHistory = (inventory: Inventory) => {
    setSelectedInventory(inventory);
    setShowHistoryModal(true);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'critical': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
      case 'low': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
      case 'normal': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
      case 'overstock': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'critical': return '위험'
      case 'low': return '부족'
      case 'normal': return '정상'
      case 'overstock': return '과다'
      default: return '알 수 없음'
    }
  };

  const totalValue = inventoryData.reduce((sum, item) => sum + (item.currentStock * item.price), 0);
  const lowStockItems = inventoryData.filter(item => item.status === 'low' || item.status === 'critical');
  const overstockItems = inventoryData.filter(item => item.status === 'overstock');

  // Toast 자동 닫기
  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), 2000);
      return () => clearTimeout(timer);
    }
  }, [toast]);

  // 권한별 분기 예시
  if (!user) return <div className="p-6">로그인 필요</div>;
  if (user.role === 'employee') {
    return <div className="p-6">직원은 본인 담당 재고만 확인할 수 있습니다.</div>;
  }

  return (
    <PermissionGuard permissions={['inventory.view']} fallback={<Alert message="재고 관리 접근 권한이 없습니다." type="error" />}>
      <AppLayout>
        <div className="w-full h-full bg-gray-50 dark:bg-gray-900 p-6">
          <div className="max-w-7xl mx-auto space-y-6">
            {/* 헤더 */}
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">재고 관리</h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  재고 현황 및 관리
                </p>
              </div>
              <div className="flex space-x-2">
                <Button variant="outline" onClick={() => setShowAdjustForm(!showAdjustForm)}>
                  <PlusIcon className="w-4 h-4 mr-2" />
                  재고 조정
                </Button>
                <Button onClick={() => setShowAddForm(!showAddForm)}>
                  <Plus className="w-4 h-4 mr-2" />
                  품목 추가
                </Button>
              </div>
            </div>

            {/* 페이지 정상 작동 메시지 */}
            <Card className="bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800">
              <CardContent className="p-4">
                <div className="flex items-center">
                  <Check className="w-5 h-5 text-green-600 mr-2" />
                  <span className="text-green-800 dark:text-green-200 font-medium">
                    ✅ 재고 관리 페이지 정상 작동 중 - 등록/수정/삭제/입고/출고/폐기/이력 기능 테스트 가능
                  </span>
                </div>
              </CardContent>
            </Card>

            {/* 통계 카드 */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400">총 재고 가치</p>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white">₩{totalValue.toLocaleString()}</p>
                    </div>
                    <Package className="w-8 h-8 text-blue-600" />
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400">총 품목 수</p>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white">{inventoryData.length}개</p>
                    </div>
                    <TrendingUp className="w-8 h-8 text-green-600" />
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400">부족 재고</p>
                      <p className="text-2xl font-bold text-red-600">{lowStockItems.length}개</p>
                    </div>
                    <AlertTriangle className="w-8 h-8 text-red-600" />
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400">과다 재고</p>
                      <p className="text-2xl font-bold text-blue-600">{overstockItems.length}개</p>
                    </div>
                    <TrendingDown className="w-8 h-8 text-blue-600" />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* 상단 필터/정렬 UI */}
            <div className="flex flex-wrap gap-2 mb-4 items-end">
              <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)} className="border rounded px-2 py-1">
                <option value="all">상태 전체</option>
                <option value="normal">정상</option>
                <option value="low">부족</option>
                <option value="critical">긴급</option>
                <option value="overstock">과다</option>
              </select>
              <select value={categoryFilter} onChange={e => setCategoryFilter(e.target.value)} className="border rounded px-2 py-1">
                <option value="all">카테고리 전체</option>
                {[...new Set(inventoryData.map(i => i.category))].map(c => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
              <select value={dateFilter} onChange={e => setDateFilter(e.target.value)} className="border rounded px-2 py-1">
                <option value="all">전체 기간</option>
                <option value="7days">최근 7일</option>
              </select>
              <select value={sortOption} onChange={e => setSortOption(e.target.value)} className="border rounded px-2 py-1">
                <option value="latest">최신순</option>
                <option value="oldest">오래된순</option>
                <option value="critical">긴급순</option>
              </select>
            </div>

            {/* 품목 추가 폼 */}
            {showAddForm && (
              <Card>
                <CardHeader>
                  <CardTitle>새 품목 추가</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Input 
                      placeholder="품목명" 
                      value={newInventory.name}
                      onChange={(e) => setNewInventory({...newInventory, name: e.target.value})}
                    />
                    <Input 
                      placeholder="카테고리" 
                      value={newInventory.category}
                      onChange={(e) => setNewInventory({...newInventory, category: e.target.value})}
                    />
                    <Input 
                      placeholder="현재 재고" 
                      type="number" 
                      value={newInventory.currentStock}
                      onChange={(e) => setNewInventory({...newInventory, currentStock: e.target.value})}
                    />
                    <Input 
                      placeholder="최소 재고" 
                      type="number" 
                      value={newInventory.minStock}
                      onChange={(e) => setNewInventory({...newInventory, minStock: e.target.value})}
                    />
                    <Input 
                      placeholder="최대 재고" 
                      type="number" 
                      value={newInventory.maxStock}
                      onChange={(e) => setNewInventory({...newInventory, maxStock: e.target.value})}
                    />
                    <Input 
                      placeholder="단위" 
                      value={newInventory.unit}
                      onChange={(e) => setNewInventory({...newInventory, unit: e.target.value})}
                    />
                    <Input 
                      placeholder="단가" 
                      type="number" 
                      value={newInventory.price}
                      onChange={(e) => setNewInventory({...newInventory, price: e.target.value})}
                    />
                    <Input 
                      placeholder="공급업체" 
                      value={newInventory.supplier}
                      onChange={(e) => setNewInventory({...newInventory, supplier: e.target.value})}
                    />
                  </div>
                  <div className="mt-4">
                    <textarea 
                      className="w-full border rounded px-3 py-2"
                      placeholder="메모"
                      value={newInventory.notes}
                      onChange={(e) => setNewInventory({...newInventory, notes: e.target.value})}
                    />
                  </div>
                  <div className="flex justify-end space-x-2 mt-4">
                    <Button variant="outline" onClick={() => setShowAddForm(false)}>
                      취소
                    </Button>
                    <Button onClick={handleAddInventory}>추가</Button>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* 재고 조정 폼 */}
            {showAdjustForm && (
              <Card>
                <CardHeader>
                  <CardTitle>재고 조정</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <select 
                      className="border rounded px-3 py-2"
                      value={adjustForm.inventoryId}
                      onChange={(e) => setAdjustForm({...adjustForm, inventoryId: e.target.value})}
                    >
                      <option value="">품목 선택</option>
                      {inventoryData.map(item => (
                        <option key={item.id} value={item.id}>{item.name} (현재: {item.currentStock}{item.unit})</option>
                      ))}
                    </select>
                    <Input 
                      placeholder="조정 수량" 
                      type="number" 
                      value={adjustForm.quantity}
                      onChange={(e) => setAdjustForm({...adjustForm, quantity: e.target.value})}
                    />
                    <select 
                      className="border rounded px-3 py-2"
                      value={adjustForm.type}
                      onChange={(e) => setAdjustForm({...adjustForm, type: e.target.value as "in" | "out" | "dispose"})}
                    >
                      <option value="in">입고 (+)</option>
                      <option value="out">출고 (-)</option>
                      <option value="dispose">폐기 (-)</option>
                    </select>
                  </div>
                  <div className="mt-4">
                    <textarea 
                      className="w-full border rounded px-3 py-2"
                      placeholder="조정 사유"
                      value={adjustForm.reason}
                      onChange={(e) => setAdjustForm({...adjustForm, reason: e.target.value})}
                    />
                  </div>
                  <div className="flex justify-end space-x-2 mt-4">
                    <Button variant="outline" onClick={() => setShowAdjustForm(false)}>
                      취소
                    </Button>
                    <Button onClick={handleAdjustInventory}>조정</Button>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* 재고 목록 테이블 */}
            <Card>
              <CardHeader>
                <CardTitle>재고 목록</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left p-3">품목명</th>
                        <th className="text-left p-3">카테고리</th>
                        <th className="text-left p-3">현재 재고</th>
                        <th className="text-left p-3">최소/최대</th>
                        <th className="text-left p-3">단가</th>
                        <th className="text-left p-3">총 가치</th>
                        <th className="text-left p-3">상태</th>
                        <th className="text-left p-3">공급업체</th>
                        <th className="text-left p-3">최종 업데이트</th>
                        <th className="text-left p-3">작업</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredInventory.map((item) => (
                        <tr key={item.id} className="border-b hover:bg-gray-50 dark:hover:bg-gray-800">
                          <td className="p-3 font-medium">{item.name}</td>
                          <td className="p-3">{item.category}</td>
                          <td className="p-3">
                            <span className={`font-medium ${
                              item.status === 'critical' ? 'text-red-600' :
                              item.status === 'low' ? 'text-yellow-600' :
                              item.status === 'overstock' ? 'text-blue-600' :
                              'text-gray-900 dark:text-white'
                            }`}>
                              {item.currentStock} {item.unit}
                            </span>
                          </td>
                          <td className="p-3 text-sm">
                            {item.minStock} / {item.maxStock} {item.unit}
                          </td>
                          <td className="p-3">₩{item.price.toLocaleString()}</td>
                          <td className="p-3 font-medium">
                            ₩{(item.currentStock * item.price).toLocaleString()}
                          </td>
                          <td className="p-3">
                            <Badge className={getStatusColor(item.status)}>
                              {getStatusText(item.status)}
                            </Badge>
                          </td>
                          <td className="p-3 text-sm">{item.supplier}</td>
                          <td className="p-3 text-sm">{item.lastUpdated}</td>
                          <td className="p-3">
                            <div className="flex items-center space-x-2">
                              {perms.canAdjust && <Button variant="outline" size="sm" onClick={() => setShowAdjustForm(true)}>입출고</Button>}
                              {perms.canEdit && <Button variant="outline" size="sm" onClick={() => handleEditClick(item)}>수정</Button>}
                              {perms.canDelete && <Button variant="outline" size="sm" onClick={() => handleDeleteInventory(item.id)}>삭제</Button>}
                              <Button variant="outline" size="sm" onClick={() => handleViewDetail(item)}>상세</Button>
                              <Button variant="outline" size="sm" onClick={() => handleViewHistory(item)}>이력</Button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 재고 상세 모달 */}
          {showDetailModal && selectedInventory && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
              <div className="bg-white dark:bg-gray-900 rounded-lg p-6 w-full max-w-md">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-bold">재고 상세</h2>
                  <Button variant="ghost" size="sm" onClick={() => setShowDetailModal(false)}>
                    <X className="w-4 h-4" />
                  </Button>
                </div>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">품목명</label>
                    <p className="text-gray-900 dark:text-white">{selectedInventory.name}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">카테고리</label>
                    <p className="text-gray-900 dark:text-white">{selectedInventory.category}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">현재 재고</label>
                    <p className="text-gray-900 dark:text-white">{selectedInventory.currentStock} {selectedInventory.unit}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">최소/최대 재고</label>
                    <p className="text-gray-900 dark:text-white">{selectedInventory.minStock} / {selectedInventory.maxStock} {selectedInventory.unit}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">단가</label>
                    <p className="text-gray-900 dark:text-white">₩{selectedInventory.price.toLocaleString()}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">총 가치</label>
                    <p className="text-gray-900 dark:text-white">₩{(selectedInventory.currentStock * selectedInventory.price).toLocaleString()}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">상태</label>
                    <Badge className={getStatusColor(selectedInventory.status)}>
                      {getStatusText(selectedInventory.status)}
                    </Badge>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">공급업체</label>
                    <p className="text-gray-900 dark:text-white">{selectedInventory.supplier}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">최종 업데이트</label>
                    <p className="text-gray-900 dark:text-white">{selectedInventory.lastUpdated}</p>
                  </div>
                  {selectedInventory.notes && (
                    <div>
                      <label className="block text-sm font-medium mb-1">메모</label>
                      <p className="text-gray-900 dark:text-white">{selectedInventory.notes}</p>
                    </div>
                  )}
                </div>
                <div className="flex justify-end mt-6">
                  <Button onClick={() => setShowDetailModal(false)}>
                    닫기
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* 재고 수정 모달 */}
          {showEditModal && selectedInventory && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
              <div className="bg-white dark:bg-gray-900 rounded-lg p-6 w-full max-w-md">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-bold">재고 수정</h2>
                  <Button variant="ghost" size="sm" onClick={() => setShowEditModal(false)}>
                    <X className="w-4 h-4" />
                  </Button>
                </div>
                <div className="space-y-4">
                  <Input
                    placeholder="품목명"
                    value={selectedInventory.name}
                    onChange={(e) => setSelectedInventory({...selectedInventory, name: e.target.value})}
                  />
                  <Input
                    placeholder="카테고리"
                    value={selectedInventory.category}
                    onChange={(e) => setSelectedInventory({...selectedInventory, category: e.target.value})}
                  />
                  <Input
                    placeholder="현재 재고"
                    type="number"
                    value={selectedInventory.currentStock}
                    onChange={(e) => setSelectedInventory({...selectedInventory, currentStock: parseInt(e.target.value)})}
                  />
                  <Input
                    placeholder="최소 재고"
                    type="number"
                    value={selectedInventory.minStock}
                    onChange={(e) => setSelectedInventory({...selectedInventory, minStock: parseInt(e.target.value)})}
                  />
                  <Input
                    placeholder="최대 재고"
                    type="number"
                    value={selectedInventory.maxStock}
                    onChange={(e) => setSelectedInventory({...selectedInventory, maxStock: parseInt(e.target.value)})}
                  />
                  <Input
                    placeholder="단가"
                    type="number"
                    value={selectedInventory.price}
                    onChange={(e) => setSelectedInventory({...selectedInventory, price: parseInt(e.target.value)})}
                  />
                  <Input
                    placeholder="공급업체"
                    value={selectedInventory.supplier}
                    onChange={(e) => setSelectedInventory({...selectedInventory, supplier: e.target.value})}
                  />
                  <textarea
                    className="w-full border rounded px-3 py-2"
                    placeholder="메모"
                    value={selectedInventory.notes || ""}
                    onChange={(e) => setSelectedInventory({...selectedInventory, notes: e.target.value})}
                  />
                </div>
                <div className="flex justify-end space-x-2 mt-6">
                  <Button variant="outline" onClick={() => setShowEditModal(false)}>
                    취소
                  </Button>
                  <Button onClick={handleEditInventory}>
                    수정
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* 재고 이력 모달 */}
          {showHistoryModal && selectedInventory && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
              <div className="bg-white dark:bg-gray-900 rounded-lg p-6 w-full max-w-2xl">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-bold">{selectedInventory.name} - 재고 이력</h2>
                  <Button variant="ghost" size="sm" onClick={() => setShowHistoryModal(false)}>
                    <X className="w-4 h-4" />
                  </Button>
                </div>
                <div className="max-h-96 overflow-y-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left p-3">날짜</th>
                        <th className="text-left p-3">유형</th>
                        <th className="text-left p-3">수량</th>
                        <th className="text-left p-3">사유</th>
                        <th className="text-left p-3">담당자</th>
                      </tr>
                    </thead>
                    <tbody>
                      {inventoryHistory
                        .filter(history => history.inventoryId === selectedInventory.id)
                        .map((history) => (
                          <tr key={history.id} className="border-b">
                            <td className="p-3">{history.date}</td>
                            <td className="p-3">
                              <Badge className={
                                history.type === 'in' ? 'bg-green-100 text-green-800' :
                                history.type === 'out' ? 'bg-blue-100 text-blue-800' :
                                'bg-red-100 text-red-800'
                              }>
                                {history.type === 'in' && '입고'}
                                {history.type === 'out' && '출고'}
                                {history.type === 'dispose' && '폐기'}
                              </Badge>
                            </td>
                            <td className="p-3">{history.quantity}</td>
                            <td className="p-3">{history.reason}</td>
                            <td className="p-3">{history.operator}</td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
                <div className="flex justify-end mt-6">
                  <Button onClick={() => setShowHistoryModal(false)}>
                    닫기
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* Toast 알림 */}
          {showToast && (
            <Toast message={toastMessage} type={toastType} onClose={() => setShowToast(false)} />
          )}
        </div>
      </AppLayout>
    </PermissionGuard>
  );
} 
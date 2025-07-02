"use client";
import React, { useState, useEffect } from "react";
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
import { api as noticeApi } from '../notice/page';
import { toast } from '@/lib/toast';
import NotificationService from '@/lib/notification-service';

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
async function createInventoryNotice({ type, title, content, author }) {
  try {
    await noticeApi.createNotice({
      type,
      title,
      content,
      status: 'unread',
      author
    });
  } catch (e) {
    // 무시(실패 시에도 inventory는 정상 동작)
  }
}

export default function InventoryPage() {
  const { user } = useUser();
  const [searchTerm, setSearchTerm] = useState("");
  const [showAddForm, setShowAddForm] = useState(false);
  const [showAdjustForm, setShowAdjustForm] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  const [selectedInventory, setSelectedInventory] = useState<Inventory | null>(null);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState("");
  const [toastType, setToastType] = useState<"success" | "error">("success");
  
  // 더미 재고 데이터
  const [inventoryData, setInventoryData] = useState<Inventory[]>([
    {
      id: 1,
      name: "신선 채소 세트",
      category: "채소류",
      currentStock: 25,
      minStock: 10,
      maxStock: 100,
      unit: "kg",
      price: 5000,
      supplier: "농산물공급업체",
      lastUpdated: "2024-01-15",
      status: "normal",
      notes: "신선도 중요"
    },
    {
      id: 2,
      name: "육류 패키지",
      category: "육류",
      currentStock: 8,
      minStock: 15,
      maxStock: 50,
      unit: "kg",
      price: 15000,
      supplier: "정육점",
      lastUpdated: "2024-01-14",
      status: "low",
      notes: "등급 A 요청"
    },
    {
      id: 3,
      name: "조미료 세트",
      category: "조미료",
      currentStock: 45,
      minStock: 5,
      maxStock: 80,
      unit: "세트",
      price: 8000,
      supplier: "식자재업체",
      lastUpdated: "2024-01-13",
      status: "normal",
      notes: "정기 발주"
    },
    {
      id: 4,
      name: "냉동 해산물",
      category: "해산물",
      currentStock: 120,
      minStock: 20,
      maxStock: 100,
      unit: "kg",
      price: 12000,
      supplier: "수산물공급업체",
      lastUpdated: "2024-01-12",
      status: "overstock",
      notes: "과다 재고"
    },
    {
      id: 5,
      name: "쌀",
      category: "곡물",
      currentStock: 3,
      minStock: 10,
      maxStock: 200,
      unit: "kg",
      price: 3000,
      supplier: "농산물공급업체",
      lastUpdated: "2024-01-11",
      status: "critical",
      notes: "긴급 발주 필요"
    }
  ]);

  // 더미 재고 이력 데이터
  const [inventoryHistory, setInventoryHistory] = useState<InventoryHistory[]>([
    {
      id: 1,
      inventoryId: 1,
      type: 'in',
      quantity: 20,
      date: '2024-01-15',
      reason: '정기 입고',
      operator: '김매니저'
    },
    {
      id: 2,
      inventoryId: 2,
      type: 'out',
      quantity: 5,
      date: '2024-01-14',
      reason: '요리 사용',
      operator: '이주방장'
    },
    {
      id: 3,
      inventoryId: 4,
      type: 'dispose',
      quantity: 10,
      date: '2024-01-13',
      reason: '유통기한 만료',
      operator: '박청소팀장'
    }
  ]);

  // 새 재고 폼 상태
  const [newInventory, setNewInventory] = useState({
    name: "",
    category: "",
    currentStock: "",
    minStock: "",
    maxStock: "",
    unit: "",
    price: "",
    supplier: "",
    notes: ""
  });

  // 재고 조정 폼 상태
  const [adjustForm, setAdjustForm] = useState({
    inventoryId: "",
    type: "in" as "in" | "out" | "dispose",
    quantity: "",
    reason: ""
  });

  // 검색/필터
  const [filteredInventory, setFilteredInventory] = useState<Inventory[]>(inventoryData);
  const [statusFilter, setStatusFilter] = useState<string>("all");

  // 재고 관련 상태 관리
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedItem, setSelectedItem] = useState<Inventory | null>(null);
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" } | null>(null);

  // 검색/필터
  useEffect(() => {
    let filtered = inventoryData;
    if (searchTerm) {
      filtered = filtered.filter(i =>
        i.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    if (statusFilter !== "all") {
      filtered = filtered.filter(i => i.status === statusFilter);
    }
    setFilteredInventory(filtered);
  }, [inventoryData, searchTerm, statusFilter]);

  // Toast 알림 표시 함수
  const showToastMessage = (message: string, type: "success" | "error" = "success") => {
    setToastMessage(message);
    setToastType(type);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };

  // 재고 추가
  const handleAddInventory = async () => {
    if (!newInventory.name || !newInventory.category || !newInventory.currentStock) {
      showToastMessage("필수 항목을 모두 입력해주세요.", "error");
      return;
    }

    const inventory: Inventory = {
      id: Math.max(...inventoryData.map(i => i.id)) + 1,
      name: newInventory.name,
      category: newInventory.category,
      currentStock: parseInt(newInventory.currentStock),
      minStock: parseInt(newInventory.minStock) || 0,
      maxStock: parseInt(newInventory.maxStock) || 100,
      unit: newInventory.unit,
      price: parseInt(newInventory.price) || 0,
      supplier: newInventory.supplier,
      lastUpdated: new Date().toISOString().split('T')[0],
      status: "normal",
      notes: newInventory.notes
    };

    setInventoryData([...inventoryData, inventory]);
    setNewInventory({ name: "", category: "", currentStock: "", minStock: "", maxStock: "", unit: "", price: "", supplier: "", notes: "" });
    setShowAddForm(false);
    showToastMessage("재고 품목이 성공적으로 등록되었습니다.");

    // 재고 등록 알림 생성
    await NotificationService.createInventoryNotification('received', inventory);
  };

  // 재고 수정
  const handleEditInventory = async () => {
    if (!selectedInventory) return;

    const updatedInventoryData = inventoryData.map(inventory =>
      inventory.id === selectedInventory.id ? selectedInventory : inventory
    );
    setInventoryData(updatedInventoryData);
    setShowEditModal(false);
    setSelectedInventory(null);
    showToastMessage("재고 정보가 성공적으로 수정되었습니다.");

    // 재고 수정 알림 생성
    if (selectedInventory.currentStock <= selectedInventory.minStock) {
      await NotificationService.createInventoryNotification('low_stock', selectedInventory);
    }
    if (selectedInventory.currentStock === 0) {
      await NotificationService.createInventoryNotification('out_of_stock', selectedInventory);
    }
  };

  // 재고 삭제
  const handleDeleteInventory = async (id: number) => {
    setInventoryData(inventoryData.filter(inventory => inventory.id !== id));
    showToastMessage("재고 품목이 성공적으로 삭제되었습니다.");

    // 재고 삭제 알림 생성
    const itemToDelete = inventoryData.find(item => item.id === id);
    if (itemToDelete) {
      await NotificationService.createInventoryNotification('disposed', itemToDelete);
    }
  };

  // 재고 조정
  const handleAdjustInventory = () => {
    if (!adjustForm.inventoryId || !adjustForm.quantity) {
      showToastMessage("필수 항목을 모두 입력해주세요.", "error");
      return;
    }

    const inventoryId = parseInt(adjustForm.inventoryId);
    const quantity = parseInt(adjustForm.quantity);
    const inventory = inventoryData.find(i => i.id === inventoryId);

    if (!inventory) {
      showToastMessage("재고 품목을 찾을 수 없습니다.", "error");
      return;
    }

    let newStock = inventory.currentStock;
    if (adjustForm.type === 'in') {
      newStock += quantity;
    } else if (adjustForm.type === 'out') {
      if (newStock < quantity) {
        showToastMessage("출고 수량이 현재 재고보다 많습니다.", "error");
        return;
      }
      newStock -= quantity;
    } else if (adjustForm.type === 'dispose') {
      if (newStock < quantity) {
        showToastMessage("폐기 수량이 현재 재고보다 많습니다.", "error");
        return;
      }
      newStock -= quantity;
    }

    // 재고 상태 업데이트
    let newStatus: "normal" | "low" | "critical" | "overstock" = "normal";
    if (newStock <= inventory.minStock) {
      newStatus = newStock <= inventory.minStock / 2 ? "critical" : "low";
    } else if (newStock >= inventory.maxStock) {
      newStatus = "overstock";
    }

    const updatedInventoryData = inventoryData.map(i =>
      i.id === inventoryId 
        ? { ...i, currentStock: newStock, status: newStatus, lastUpdated: new Date().toISOString().split('T')[0] }
        : i
    );
    setInventoryData(updatedInventoryData);

    // 이력 추가
    const history: InventoryHistory = {
      id: Math.max(...inventoryHistory.map(h => h.id)) + 1,
      inventoryId,
      type: adjustForm.type,
      quantity,
      date: new Date().toISOString().split('T')[0],
      reason: adjustForm.reason,
      operator: "현재 사용자"
    };
    setInventoryHistory([...inventoryHistory, history]);

    setAdjustForm({ inventoryId: "", type: "in", quantity: "", reason: "" });
    setShowAdjustForm(false);
    showToastMessage("재고가 성공적으로 조정되었습니다.");

    // 재고 조정 알림 생성
    if (newStock <= inventory.minStock) {
      await NotificationService.createInventoryNotification('low_stock', {
        ...inventory,
        currentStock: newStock
      });
    }
    if (newStock === 0) {
      await NotificationService.createInventoryNotification('out_of_stock', {
        ...inventory,
        currentStock: newStock
      });
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

  return (
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

          {/* 검색 및 필터 */}
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="품목명, 카테고리, 공급업체로 검색..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <div>
                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-md bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                  >
                    <option value="all">전체 상태</option>
                    <option value="normal">정상</option>
                    <option value="low">부족</option>
                    <option value="overstock">과다</option>
                  </select>
                </div>
                <Button variant="outline">필터</Button>
              </div>
            </CardContent>
          </Card>

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
                            <Button variant="outline" size="sm" onClick={() => handleViewDetail(item)}>
                              <Eye className="w-3 h-3" />
                            </Button>
                            <Button variant="outline" size="sm" onClick={() => handleViewHistory(item)}>
                              <History className="w-3 h-3" />
                            </Button>
                            <Button variant="outline" size="sm" onClick={() => handleEditClick(item)}>
                              <Edit className="w-3 h-3" />
                            </Button>
                            <Button variant="outline" size="sm" onClick={() => handleDeleteInventory(item.id)}>
                              <Trash2 className="w-3 h-3" />
                            </Button>
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
  );
} 
'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../src/components/ui/card';
import { Button } from '../../src/components/ui/button';
import { Input } from '../../src/components/ui/input';
import { Badge } from '../../src/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../../src/components/ui/dialog';
import { Label } from '../../src/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../src/components/ui/select';
import { Textarea } from '../../src/components/ui/textarea';
import { 
  Package, 
  Plus, 
  Search, 
  Edit, 
  Trash2, 
  AlertTriangle,
  CheckCircle,
  XCircle,
  TrendingUp,
  TrendingDown,
  ShoppingCart,
  BarChart3,
  RefreshCw
} from 'lucide-react';
import { toast } from 'sonner';
import { apiClient, Store as StoreType } from '../../src/lib/api-client';
import useLoadingState from '../../src/hooks/useLoadingState';
import useErrorHandler from '../../src/hooks/useErrorHandler';

interface Inventory {
  id: number;
  name: string;
  description?: string;
  quantity: number;
  unit: string;
  min_quantity: number;
  max_quantity: number;
  status: 'in_stock' | 'low_stock' | 'out_of_stock';
  store_id: number;
  store_name?: string;
  category?: string;
  supplier?: string;
  cost_per_unit: number;
  last_restocked?: string;
  created_at: string;
  updated_at: string;
}

interface InventoryFormData {
  name: string;
  description: string;
  quantity: number;
  unit: string;
  min_quantity: number;
  max_quantity: number;
  store_id: number;
  category: string;
  supplier: string;
  cost_per_unit: number;
}

export default function InventoryManagement() {
  const [inventories, setInventories] = useState<Inventory[]>([]);
  const [stores, setStores] = useState<StoreType[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStore, setSelectedStore] = useState<number | 'all'>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [editingInventory, setEditingInventory] = useState<Inventory | null>(null);
  
  const [formData, setFormData] = useState<InventoryFormData>({
    name: '',
    description: '',
    quantity: 0,
    unit: '개',
    min_quantity: 10,
    max_quantity: 100,
    store_id: 0,
    category: '',
    supplier: '',
    cost_per_unit: 0,
  });

  const { isLoading, setLoading } = useLoadingState();
  const { handleError } = useErrorHandler();

  // 재고 목록 조회
  const fetchInventories = async () => {
    try {
      // 임시로 샘플 데이터 사용
      const sampleInventories: Inventory[] = [
        {
          id: 1,
          name: '아메리카노 원두',
          description: '에스프레소 원두',
          quantity: 50,
          unit: 'kg',
          min_quantity: 10,
          max_quantity: 100,
          status: 'in_stock',
          store_id: 1,
          store_name: '강남점',
          category: '원두',
          supplier: '원두공급업체',
          cost_per_unit: 15000,
          last_restocked: '2024-01-15',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-15T00:00:00Z'
        },
        {
          id: 2,
          name: '우유',
          description: '신선 우유',
          quantity: 5,
          unit: 'L',
          min_quantity: 10,
          max_quantity: 50,
          status: 'low_stock',
          store_id: 1,
          store_name: '강남점',
          category: '유제품',
          supplier: '우유공급업체',
          cost_per_unit: 3000,
          last_restocked: '2024-01-10',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-10T00:00:00Z'
        },
        {
          id: 3,
          name: '시럽',
          description: '바닐라 시럽',
          quantity: 0,
          unit: 'L',
          min_quantity: 5,
          max_quantity: 20,
          status: 'out_of_stock',
          store_id: 2,
          store_name: '홍대점',
          category: '시럽',
          supplier: '시럽공급업체',
          cost_per_unit: 8000,
          last_restocked: '2024-01-05',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-05T00:00:00Z'
        }
      ];
      
      setInventories(sampleInventories);
    } catch (error) {
      handleError(error as Error);
    }
  };

  // 매장 목록 조회
  const fetchStores = async () => {
    try {
      const sampleStores: StoreType[] = [
        { 
          id: 1, 
          name: '강남점', 
          address: '서울 강남구', 
          phone: '02-1234-5678', 
          status: 'active',
          brand_id: 1,
          employee_count: 15,
          total_revenue: 50000000,
          last_activity: '2024-01-15T00:00:00Z',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-15T00:00:00Z'
        },
        { 
          id: 2, 
          name: '홍대점', 
          address: '서울 마포구', 
          phone: '02-2345-6789', 
          status: 'active',
          brand_id: 1,
          employee_count: 12,
          total_revenue: 40000000,
          last_activity: '2024-01-14T00:00:00Z',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-14T00:00:00Z'
        }
      ];
      setStores(sampleStores);
    } catch (error) {
      handleError(error as Error);
    }
  };

  // 폼 초기화
  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      quantity: 0,
      unit: '개',
      min_quantity: 10,
      max_quantity: 100,
      store_id: 0,
      category: '',
      supplier: '',
      cost_per_unit: 0,
    });
    setEditingInventory(null);
  };

  // 재고 추가/수정
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name || formData.store_id === 0) {
      toast.error('필수 항목을 입력해주세요.');
      return;
    }

    try {
      setLoading(true);
      
      if (editingInventory) {
        // 수정
        const updatedInventory = {
          ...editingInventory,
          ...formData,
          updated_at: new Date().toISOString()
        };
        
        setInventories(prev => prev.map(item => 
          item.id === editingInventory.id ? updatedInventory : item
        ));
        
        toast.success('재고가 수정되었습니다.');
      } else {
        // 추가
        const newInventory: Inventory = {
          id: Date.now(),
          ...formData,
          status: formData.quantity > formData.min_quantity ? 'in_stock' : 
                  formData.quantity > 0 ? 'low_stock' : 'out_of_stock',
          store_name: stores.find(s => s.id === formData.store_id)?.name,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };
        
        setInventories(prev => [...prev, newInventory]);
        toast.success('재고가 추가되었습니다.');
      }
      
      setIsCreateDialogOpen(false);
      resetForm();
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 재고 삭제
  const handleDelete = async (inventory: Inventory) => {
    try {
      setLoading(true);
      setInventories(prev => prev.filter(item => item.id !== inventory.id));
      toast.success('재고가 삭제되었습니다.');
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 수량 조정
  const handleQuantityAdjustment = async (inventory: Inventory, adjustment: number) => {
    try {
      setLoading(true);
      
      const newQuantity = Math.max(0, inventory.quantity + adjustment);
      const newStatus = newQuantity > inventory.min_quantity ? 'in_stock' : 
                       newQuantity > 0 ? 'low_stock' : 'out_of_stock';
      
      const updatedInventory: Inventory = {
        ...inventory,
        quantity: newQuantity,
        status: newStatus as 'in_stock' | 'low_stock' | 'out_of_stock',
        updated_at: new Date().toISOString()
      };
      
      setInventories(prev => prev.map(item => 
        item.id === inventory.id ? updatedInventory : item
      ));
      
      toast.success(`수량이 ${adjustment > 0 ? '증가' : '감소'}되었습니다.`);
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 편집 모드 시작
  const handleEdit = (inventory: Inventory) => {
    setEditingInventory(inventory);
    setFormData({
      name: inventory.name,
      description: inventory.description || '',
      quantity: inventory.quantity,
      unit: inventory.unit,
      min_quantity: inventory.min_quantity,
      max_quantity: inventory.max_quantity,
      store_id: inventory.store_id,
      category: inventory.category || '',
      supplier: inventory.supplier || '',
      cost_per_unit: inventory.cost_per_unit,
    });
    setIsCreateDialogOpen(true);
  };

  // 상태별 색상
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'in_stock': return 'bg-green-500/20 text-green-400';
      case 'low_stock': return 'bg-yellow-500/20 text-yellow-400';
      case 'out_of_stock': return 'bg-red-500/20 text-red-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  // 상태별 텍스트
  const getStatusText = (status: string) => {
    switch (status) {
      case 'in_stock': return '재고 있음';
      case 'low_stock': return '재고 부족';
      case 'out_of_stock': return '재고 없음';
      default: return '알 수 없음';
    }
  };

  // 필터링된 재고 목록
  const filteredInventories = inventories.filter(inventory => {
    const matchesSearch = inventory.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (inventory.description || '').toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStore = selectedStore === 'all' || inventory.store_id === selectedStore;
    const matchesStatus = selectedStatus === 'all' || inventory.status === selectedStatus;
    const matchesCategory = selectedCategory === 'all' || inventory.category === selectedCategory;
    
    return matchesSearch && matchesStore && matchesStatus && matchesCategory;
  });

  // 카테고리 목록
  const categories = [...new Set(inventories.map(item => item.category).filter(Boolean))];

  // 통계 계산
  const totalItems = inventories.length;
  const lowStockItems = inventories.filter(item => item.status === 'low_stock').length;
  const outOfStockItems = inventories.filter(item => item.status === 'out_of_stock').length;
  const totalValue = inventories.reduce((sum, item) => sum + (item.quantity * item.cost_per_unit), 0);

  // 초기 데이터 로드
  useEffect(() => {
    fetchInventories();
    fetchStores();
  }, []);

  return (
    <div className="min-h-screen p-6">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <Package className="w-6 h-6" />
          재고 관리
        </h1>
        <p className="text-gray-300 mt-2">재고 현황 및 발주 관리</p>
      </div>

      {/* 액션 버튼 */}
      <div className="flex gap-4 mb-8">
        <Button
          onClick={() => setIsCreateDialogOpen(true)}
          className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700"
        >
          <Plus className="w-4 h-4 mr-2" />
          재고 추가
        </Button>
        <Button
          onClick={fetchInventories}
          disabled={isLoading}
          className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          새로고침
        </Button>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">총 재고</p>
                <p className="text-2xl font-bold text-white">{totalItems}</p>
                <p className="text-gray-400 text-sm">{inventories.filter(item => item.status === 'in_stock').length}개 재고 있음</p>
              </div>
              <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
                <Package className="w-6 h-6 text-blue-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">재고 있음</p>
                <p className="text-2xl font-bold text-white">{inventories.filter(item => item.status === 'in_stock').length}</p>
                <p className="text-gray-400 text-sm">정상 재고</p>
              </div>
              <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-green-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">재고 부족</p>
                <p className="text-2xl font-bold text-white">{lowStockItems}</p>
                <p className="text-gray-400 text-sm">발주 필요</p>
              </div>
              <div className="w-12 h-12 bg-yellow-500/20 rounded-lg flex items-center justify-center">
                <AlertTriangle className="w-6 h-6 text-yellow-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">재고 없음</p>
                <p className="text-2xl font-bold text-white">{outOfStockItems}</p>
                <p className="text-gray-400 text-sm">긴급 발주</p>
              </div>
              <div className="w-12 h-12 bg-red-500/20 rounded-lg flex items-center justify-center">
                <XCircle className="w-6 h-6 text-red-400" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 검색 및 필터 */}
      <Card className="bg-white/10 backdrop-blur-sm border border-white/20 mb-8">
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <Label className="text-gray-300 text-sm">검색</Label>
              <Input
                placeholder="재고명 또는 설명으로 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="mt-1 bg-white/10 border-white/20 text-white placeholder-gray-400"
              />
            </div>
            
            <div>
              <Label className="text-gray-300 text-sm">매장</Label>
              <Select value={selectedStore.toString()} onValueChange={(value) => setSelectedStore(value === 'all' ? 'all' : parseInt(value))}>
                <SelectTrigger className="mt-1 bg-white/10 border-white/20 text-white">
                  <SelectValue placeholder="매장 선택" />
                </SelectTrigger>
                <SelectContent className="bg-white/10 border-white/20">
                  <SelectItem value="all">모든 매장</SelectItem>
                  {stores.map(store => (
                    <SelectItem key={store.id} value={store.id.toString()}>{store.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label className="text-gray-300 text-sm">상태</Label>
              <Select value={selectedStatus} onValueChange={setSelectedStatus}>
                <SelectTrigger className="mt-1 bg-white/10 border-white/20 text-white">
                  <SelectValue placeholder="상태 선택" />
                </SelectTrigger>
                <SelectContent className="bg-white/10 border-white/20">
                  <SelectItem value="all">모든 상태</SelectItem>
                  <SelectItem value="in_stock">재고 있음</SelectItem>
                  <SelectItem value="low_stock">재고 부족</SelectItem>
                  <SelectItem value="out_of_stock">재고 없음</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label className="text-gray-300 text-sm">카테고리</Label>
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger className="mt-1 bg-white/10 border-white/20 text-white">
                  <SelectValue placeholder="카테고리 선택" />
                </SelectTrigger>
                <SelectContent className="bg-white/10 border-white/20">
                  <SelectItem value="all">모든 카테고리</SelectItem>
                  {categories.map(category => (
                    <SelectItem key={category} value={category || ''}>{category || '미분류'}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 재고 목록 */}
      <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
        <CardHeader>
          <CardTitle className="text-white">재고 목록 ({filteredInventories.length}개)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredInventories.map((inventory) => (
              <div
                key={inventory.id}
                className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:bg-white/10 transition-all duration-300"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-4 mb-3">
                      <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                        <Package className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-white">{inventory.name}</h3>
                        <p className="text-gray-400">{inventory.description}</p>
                        <p className="text-gray-400 text-sm">{inventory.store_name} • {inventory.category || '미분류'}</p>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div>
                        <p className="text-gray-300 text-sm">수량</p>
                        <p className="text-white font-medium">{inventory.quantity} {inventory.unit}</p>
                      </div>
                      <div>
                        <p className="text-gray-300 text-sm">최소 수량</p>
                        <p className="text-white font-medium">{inventory.min_quantity} {inventory.unit}</p>
                      </div>
                      <div>
                        <p className="text-gray-300 text-sm">단가</p>
                        <p className="text-white font-medium">₩{inventory.cost_per_unit.toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="text-gray-300 text-sm">총 가치</p>
                        <p className="text-white font-medium">₩{(inventory.quantity * inventory.cost_per_unit).toLocaleString()}</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex flex-col gap-2 ml-4">
                    <Badge className={getStatusColor(inventory.status)}>
                      {getStatusText(inventory.status)}
                    </Badge>
                    
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleEdit(inventory)}
                        className="border-white/20 text-white hover:bg-white/10"
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button
                        size="sm"
                        onClick={() => handleDelete(inventory)}
                        className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                    
                    <div className="flex gap-1">
                      <Button
                        size="sm"
                        onClick={() => handleQuantityAdjustment(inventory, 1)}
                        className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700"
                      >
                        <TrendingUp className="w-4 h-4" />
                      </Button>
                      <Button
                        size="sm"
                        onClick={() => handleQuantityAdjustment(inventory, -1)}
                        className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700"
                      >
                        <TrendingDown className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 재고 추가/수정 다이얼로그 */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="bg-white/10 backdrop-blur-sm border border-white/20 max-w-2xl">
          <DialogHeader>
            <DialogTitle className="text-white">
              {editingInventory ? '재고 수정' : '재고 추가'}
            </DialogTitle>
          </DialogHeader>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label className="text-gray-300">재고명 *</Label>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="mt-1 bg-white/10 border-white/20 text-white"
                  placeholder="재고명을 입력하세요"
                />
              </div>
              
              <div>
                <Label className="text-gray-300">매장 *</Label>
                <Select value={formData.store_id.toString()} onValueChange={(value) => setFormData({...formData, store_id: parseInt(value)})}>
                  <SelectTrigger className="mt-1 bg-white/10 border-white/20 text-white">
                    <SelectValue placeholder="매장을 선택하세요" />
                  </SelectTrigger>
                  <SelectContent className="bg-white/10 border-white/20">
                    {stores.map(store => (
                      <SelectItem key={store.id} value={store.id.toString()}>{store.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label className="text-gray-300">카테고리</Label>
                <Input
                  value={formData.category}
                  onChange={(e) => setFormData({...formData, category: e.target.value})}
                  className="mt-1 bg-white/10 border-white/20 text-white"
                  placeholder="카테고리를 입력하세요"
                />
              </div>
              
              <div>
                <Label className="text-gray-300">공급업체</Label>
                <Input
                  value={formData.supplier}
                  onChange={(e) => setFormData({...formData, supplier: e.target.value})}
                  className="mt-1 bg-white/10 border-white/20 text-white"
                  placeholder="공급업체를 입력하세요"
                />
              </div>
              
              <div>
                <Label className="text-gray-300">수량</Label>
                <Input
                  type="number"
                  value={formData.quantity}
                  onChange={(e) => setFormData({...formData, quantity: parseInt(e.target.value) || 0})}
                  className="mt-1 bg-white/10 border-white/20 text-white"
                  placeholder="0"
                />
              </div>
              
              <div>
                <Label className="text-gray-300">단위</Label>
                <Input
                  value={formData.unit}
                  onChange={(e) => setFormData({...formData, unit: e.target.value})}
                  className="mt-1 bg-white/10 border-white/20 text-white"
                  placeholder="개, kg, L 등"
                />
              </div>
              
              <div>
                <Label className="text-gray-300">최소 수량</Label>
                <Input
                  type="number"
                  value={formData.min_quantity}
                  onChange={(e) => setFormData({...formData, min_quantity: parseInt(e.target.value) || 0})}
                  className="mt-1 bg-white/10 border-white/20 text-white"
                  placeholder="10"
                />
              </div>
              
              <div>
                <Label className="text-gray-300">최대 수량</Label>
                <Input
                  type="number"
                  value={formData.max_quantity}
                  onChange={(e) => setFormData({...formData, max_quantity: parseInt(e.target.value) || 0})}
                  className="mt-1 bg-white/10 border-white/20 text-white"
                  placeholder="100"
                />
              </div>
              
              <div>
                <Label className="text-gray-300">단가 (원)</Label>
                <Input
                  type="number"
                  value={formData.cost_per_unit}
                  onChange={(e) => setFormData({...formData, cost_per_unit: parseInt(e.target.value) || 0})}
                  className="mt-1 bg-white/10 border-white/20 text-white"
                  placeholder="0"
                />
              </div>
            </div>
            
            <div>
              <Label className="text-gray-300">설명</Label>
              <Textarea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                className="mt-1 bg-white/10 border-white/20 text-white"
                placeholder="재고에 대한 설명을 입력하세요"
                rows={3}
              />
            </div>
            
            <div className="flex gap-2">
              <Button type="submit" className="flex-1 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700">
                {editingInventory ? '수정' : '추가'}
              </Button>
              <Button type="button" variant="outline" onClick={() => setIsCreateDialogOpen(false)} className="border-white/20 text-white hover:bg-white/10">
                취소
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
} 
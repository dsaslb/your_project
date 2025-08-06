'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../src/components/ui/card';
import { Button } from '../../src/components/ui/button';
import { Input } from '../../src/components/ui/input';
import { Badge } from '../../src/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../../src/components/ui/dialog';
import { Label } from '../../src/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../src/components/ui/select';
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
  BarChart3
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

  const { isLoading, setLoading, withLoading } = useLoadingState();
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
          store_name: '스타벅스 강남점',
          category: '원두',
          supplier: '원두공급업체',
          cost_per_unit: 15000,
          last_restocked: '2024-01-15T00:00:00Z',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-15T00:00:00Z'
        },
        {
          id: 2,
          name: '우유',
          description: '신선우유',
          quantity: 5,
          unit: 'L',
          min_quantity: 10,
          max_quantity: 50,
          status: 'low_stock',
          store_id: 1,
          store_name: '스타벅스 강남점',
          category: '유제품',
          supplier: '우유공급업체',
          cost_per_unit: 3000,
          last_restocked: '2024-01-10T00:00:00Z',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-10T00:00:00Z'
        },
        {
          id: 3,
          name: '종이컵',
          description: '일회용 종이컵',
          quantity: 0,
          unit: '개',
          min_quantity: 100,
          max_quantity: 1000,
          status: 'out_of_stock',
          store_id: 2,
          store_name: '스타벅스 홍대점',
          category: '소모품',
          supplier: '소모품공급업체',
          cost_per_unit: 100,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
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
      // 임시로 샘플 데이터 사용
      const sampleStores: StoreType[] = [
        { id: 1, name: '스타벅스 강남점', address: '서울시 강남구' },
        { id: 2, name: '스타벅스 홍대점', address: '서울시 마포구' },
        { id: 3, name: '스타벅스 명동점', address: '서울시 중구' }
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

  // 재고 생성/수정
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name.trim() || formData.store_id === 0) {
      toast.error('필수 항목을 입력해주세요.');
      return;
    }

    try {
      setLoading(true);
      
      // 실제 API 호출 대신 시뮬레이션
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      if (editingInventory) {
        // 수정
        setInventories(prev => prev.map(item => 
          item.id === editingInventory.id 
            ? { ...item, ...formData, updated_at: new Date().toISOString() }
            : item
        ));
        toast.success('재고가 수정되었습니다.');
      } else {
        // 생성
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
        toast.success('재고가 생성되었습니다.');
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
    if (!confirm(`${inventory.name} 재고를 삭제하시겠습니까?`)) return;
    
    try {
      setLoading(true);
      // 실제 API 호출 대신 시뮬레이션
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setInventories(prev => prev.filter(item => item.id !== inventory.id));
      toast.success('재고가 삭제되었습니다.');
      
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 재고 수량 조정
  const handleQuantityAdjustment = async (inventory: Inventory, adjustment: number) => {
    try {
      setLoading(true);
      // 실제 API 호출 대신 시뮬레이션
      await new Promise(resolve => setTimeout(resolve, 500));
      
      const newQuantity = Math.max(0, inventory.quantity + adjustment);
      const newStatus = newQuantity > inventory.min_quantity ? 'in_stock' : 
                       newQuantity > 0 ? 'low_stock' : 'out_of_stock';
      
      setInventories(prev => prev.map(item => 
        item.id === inventory.id 
          ? { ...item, quantity: newQuantity, status: newStatus, updated_at: new Date().toISOString() }
          : item
      ));
      
      toast.success(`수량이 ${adjustment > 0 ? '증가' : '감소'}되었습니다.`);
      
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 재고 수정 모드로 설정
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
      case 'in_stock': return '#10b981';
      case 'low_stock': return '#f59e0b';
      case 'out_of_stock': return '#ef4444';
      default: return '#6b7280';
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
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      zIndex: 9999,
      backgroundColor: '#f3f4f6',
      fontFamily: 'Arial, sans-serif',
      overflow: 'auto'
    }}>
      <div style={{
        maxWidth: '1400px',
        margin: '2rem auto',
        padding: '0 2rem'
      }}>
        {/* 헤더 */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '2rem'
        }}>
          <div>
            <h1 style={{
              fontSize: '2rem',
              fontWeight: 'bold',
              color: '#1f2937',
              marginBottom: '0.5rem'
            }}>
              재고 관리
            </h1>
            <p style={{
              fontSize: '1.125rem',
              color: '#6b7280'
            }}>
              재고 현황 및 발주 관리
            </p>
          </div>
          
          <button
            onClick={() => setIsCreateDialogOpen(true)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.75rem 1rem',
              backgroundColor: '#10b981',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              fontSize: '0.875rem',
              fontWeight: '500',
              cursor: 'pointer'
            }}
          >
            <Plus style={{ width: '16px', height: '16px' }} />
            재고 추가
          </button>
        </div>

        {/* 통계 카드 */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '1.5rem',
          marginBottom: '2rem'
        }}>
          <div style={{
            backgroundColor: '#3b82f6',
            color: 'white',
            padding: '1.5rem',
            borderRadius: '8px'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '1rem'
            }}>
              <h3 style={{ fontSize: '0.875rem', margin: '0' }}>총 재고</h3>
              <Package style={{ width: '20px', height: '20px' }} />
            </div>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0 0 0.5rem 0' }}>
              {inventories.length}
            </p>
            <p style={{ fontSize: '0.875rem', opacity: '0.8', margin: '0' }}>
              {inventories.filter(item => item.status === 'in_stock').length}개 재고 있음
            </p>
          </div>

          <div style={{
            backgroundColor: '#10b981',
            color: 'white',
            padding: '1.5rem',
            borderRadius: '8px'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '1rem'
            }}>
              <h3 style={{ fontSize: '0.875rem', margin: '0' }}>재고 있음</h3>
              <CheckCircle style={{ width: '20px', height: '20px' }} />
            </div>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0 0 0.5rem 0' }}>
              {inventories.filter(item => item.status === 'in_stock').length}
            </p>
            <p style={{ fontSize: '0.875rem', opacity: '0.8', margin: '0' }}>
              정상 재고
            </p>
          </div>

          <div style={{
            backgroundColor: '#f59e0b',
            color: 'white',
            padding: '1.5rem',
            borderRadius: '8px'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '1rem'
            }}>
              <h3 style={{ fontSize: '0.875rem', margin: '0' }}>재고 부족</h3>
              <AlertTriangle style={{ width: '20px', height: '20px' }} />
            </div>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0 0 0.5rem 0' }}>
              {inventories.filter(item => item.status === 'low_stock').length}
            </p>
            <p style={{ fontSize: '0.875rem', opacity: '0.8', margin: '0' }}>
              발주 필요
            </p>
          </div>

          <div style={{
            backgroundColor: '#ef4444',
            color: 'white',
            padding: '1.5rem',
            borderRadius: '8px'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '1rem'
            }}>
              <h3 style={{ fontSize: '0.875rem', margin: '0' }}>재고 없음</h3>
              <XCircle style={{ width: '20px', height: '20px' }} />
            </div>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0 0 0.5rem 0' }}>
              {inventories.filter(item => item.status === 'out_of_stock').length}
            </p>
            <p style={{ fontSize: '0.875rem', opacity: '0.8', margin: '0' }}>
              긴급 발주
            </p>
          </div>
        </div>

        {/* 필터 및 검색 */}
        <div style={{
          backgroundColor: 'white',
          padding: '1.5rem',
          borderRadius: '8px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          marginBottom: '2rem'
        }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '1rem',
            alignItems: 'end'
          }}>
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                검색
              </label>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="재고명 또는 설명으로 검색"
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '0.875rem'
                }}
              />
            </div>
            
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                매장
              </label>
              <select
                value={selectedStore}
                onChange={(e) => setSelectedStore(e.target.value === 'all' ? 'all' : Number(e.target.value))}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '0.875rem',
                  backgroundColor: 'white'
                }}
              >
                <option value="all">전체 매장</option>
                {stores.map(store => (
                  <option key={store.id} value={store.id}>{store.name}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                상태
              </label>
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '0.875rem',
                  backgroundColor: 'white'
                }}
              >
                <option value="all">전체 상태</option>
                <option value="in_stock">재고 있음</option>
                <option value="low_stock">재고 부족</option>
                <option value="out_of_stock">재고 없음</option>
              </select>
            </div>
            
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                카테고리
              </label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '0.875rem',
                  backgroundColor: 'white'
                }}
              >
                <option value="all">전체 카테고리</option>
                <option value="원두">원두</option>
                <option value="유제품">유제품</option>
                <option value="소모품">소모품</option>
              </select>
            </div>
          </div>
        </div>

        {/* 재고 목록 */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          overflow: 'hidden'
        }}>
          <div style={{
            padding: '1.5rem',
            borderBottom: '1px solid #e5e7eb'
          }}>
            <h2 style={{
              fontSize: '1.25rem',
              fontWeight: 'bold',
              color: '#1f2937',
              margin: '0'
            }}>
              재고 목록 ({filteredInventories.length}개)
            </h2>
          </div>
          
          <div style={{ overflowX: 'auto' }}>
            <table style={{
              width: '100%',
              borderCollapse: 'collapse'
            }}>
              <thead style={{
                backgroundColor: '#f9fafb',
                borderBottom: '1px solid #e5e7eb'
              }}>
                <tr>
                  <th style={{
                    padding: '1rem',
                    textAlign: 'left',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    color: '#374151'
                  }}>
                    재고명
                  </th>
                  <th style={{
                    padding: '1rem',
                    textAlign: 'left',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    color: '#374151'
                  }}>
                    수량
                  </th>
                  <th style={{
                    padding: '1rem',
                    textAlign: 'left',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    color: '#374151'
                  }}>
                    상태
                  </th>
                  <th style={{
                    padding: '1rem',
                    textAlign: 'left',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    color: '#374151'
                  }}>
                    매장
                  </th>
                  <th style={{
                    padding: '1rem',
                    textAlign: 'left',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    color: '#374151'
                  }}>
                    카테고리
                  </th>
                  <th style={{
                    padding: '1rem',
                    textAlign: 'left',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    color: '#374151'
                  }}>
                    작업
                  </th>
                </tr>
              </thead>
              <tbody>
                {filteredInventories.map((inventory) => (
                  <tr key={inventory.id} style={{
                    borderBottom: '1px solid #e5e7eb'
                  }}>
                    <td style={{
                      padding: '1rem',
                      fontSize: '0.875rem',
                      color: '#374151'
                    }}>
                      <div>
                        <p style={{ fontWeight: '500', margin: '0 0 0.25rem 0' }}>
                          {inventory.name}
                        </p>
                        {inventory.description && (
                          <p style={{ fontSize: '0.75rem', color: '#6b7280', margin: '0' }}>
                            {inventory.description}
                          </p>
                        )}
                      </div>
                    </td>
                    <td style={{
                      padding: '1rem',
                      fontSize: '0.875rem',
                      color: '#374151'
                    }}>
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem'
                      }}>
                        <span style={{ fontWeight: '500' }}>
                          {inventory.quantity} {inventory.unit}
                        </span>
                        <div style={{
                          display: 'flex',
                          gap: '0.25rem'
                        }}>
                          <button
                            onClick={() => handleQuantityAdjustment(inventory, -1)}
                            style={{
                              padding: '0.25rem',
                              border: '1px solid #d1d5db',
                              borderRadius: '4px',
                              backgroundColor: 'white',
                              color: '#374151',
                              cursor: 'pointer',
                              fontSize: '0.75rem'
                            }}
                          >
                            -
                          </button>
                          <button
                            onClick={() => handleQuantityAdjustment(inventory, 1)}
                            style={{
                              padding: '0.25rem',
                              border: '1px solid #d1d5db',
                              borderRadius: '4px',
                              backgroundColor: 'white',
                              color: '#374151',
                              cursor: 'pointer',
                              fontSize: '0.75rem'
                            }}
                          >
                            +
                          </button>
                        </div>
                      </div>
                    </td>
                    <td style={{
                      padding: '1rem'
                    }}>
                      <span style={{
                        padding: '0.25rem 0.75rem',
                        borderRadius: '9999px',
                        fontSize: '0.75rem',
                        fontWeight: '500',
                        backgroundColor: getStatusColor(inventory.status) + '20',
                        color: getStatusColor(inventory.status)
                      }}>
                        {getStatusText(inventory.status)}
                      </span>
                    </td>
                    <td style={{
                      padding: '1rem',
                      fontSize: '0.875rem',
                      color: '#374151'
                    }}>
                      {inventory.store_name}
                    </td>
                    <td style={{
                      padding: '1rem',
                      fontSize: '0.875rem',
                      color: '#374151'
                    }}>
                      {inventory.category}
                    </td>
                    <td style={{
                      padding: '1rem'
                    }}>
                      <div style={{
                        display: 'flex',
                        gap: '0.5rem'
                      }}>
                        <button
                          onClick={() => handleEdit(inventory)}
                          style={{
                            padding: '0.5rem',
                            border: '1px solid #d1d5db',
                            borderRadius: '4px',
                            backgroundColor: 'white',
                            color: '#374151',
                            cursor: 'pointer'
                          }}
                        >
                          <Edit style={{ width: '16px', height: '16px' }} />
                        </button>
                        <button
                          onClick={() => handleDelete(inventory)}
                          style={{
                            padding: '0.5rem',
                            border: '1px solid #ef4444',
                            borderRadius: '4px',
                            backgroundColor: '#ef4444',
                            color: 'white',
                            cursor: 'pointer'
                          }}
                        >
                          <Trash2 style={{ width: '16px', height: '16px' }} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {filteredInventories.length === 0 && (
            <div style={{
              padding: '3rem',
              textAlign: 'center',
              color: '#6b7280'
            }}>
              <Package style={{ width: '48px', height: '48px', margin: '0 auto 1rem', opacity: '0.5' }} />
              <p>검색 결과가 없습니다.</p>
            </div>
          )}
        </div>
      </div>

      {/* 재고 생성/수정 모달 */}
      {isCreateDialogOpen && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 10000
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '2rem',
            borderRadius: '8px',
            maxWidth: '600px',
            width: '90%',
            maxHeight: '90vh',
            overflow: 'auto'
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '1.5rem'
            }}>
              <h2 style={{
                fontSize: '1.5rem',
                fontWeight: 'bold',
                color: '#1f2937',
                margin: '0'
              }}>
                {editingInventory ? '재고 수정' : '재고 추가'}
              </h2>
              <button
                onClick={() => {
                  setIsCreateDialogOpen(false);
                  resetForm();
                }}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: '1.5rem',
                  cursor: 'pointer',
                  color: '#6b7280'
                }}
              >
                ×
              </button>
            </div>

            <form onSubmit={handleSubmit}>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                gap: '1rem',
                marginBottom: '1.5rem'
              }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                    재고명 *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      fontSize: '0.875rem'
                    }}
                    placeholder="재고명을 입력하세요"
                    required
                  />
                </div>

                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                    매장 *
                  </label>
                  <select
                    value={formData.store_id}
                    onChange={(e) => setFormData(prev => ({ ...prev, store_id: Number(e.target.value) }))}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      fontSize: '0.875rem',
                      backgroundColor: 'white'
                    }}
                    required
                  >
                    <option value={0}>매장을 선택하세요</option>
                    {stores.map(store => (
                      <option key={store.id} value={store.id}>{store.name}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                    수량
                  </label>
                  <input
                    type="number"
                    value={formData.quantity}
                    onChange={(e) => setFormData(prev => ({ ...prev, quantity: Number(e.target.value) }))}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      fontSize: '0.875rem'
                    }}
                    min="0"
                  />
                </div>

                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                    단위
                  </label>
                  <select
                    value={formData.unit}
                    onChange={(e) => setFormData(prev => ({ ...prev, unit: e.target.value }))}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      fontSize: '0.875rem',
                      backgroundColor: 'white'
                    }}
                  >
                    <option value="개">개</option>
                    <option value="kg">kg</option>
                    <option value="L">L</option>
                    <option value="ml">ml</option>
                    <option value="g">g</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                    최소 수량
                  </label>
                  <input
                    type="number"
                    value={formData.min_quantity}
                    onChange={(e) => setFormData(prev => ({ ...prev, min_quantity: Number(e.target.value) }))}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      fontSize: '0.875rem'
                    }}
                    min="0"
                  />
                </div>

                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                    최대 수량
                  </label>
                  <input
                    type="number"
                    value={formData.max_quantity}
                    onChange={(e) => setFormData(prev => ({ ...prev, max_quantity: Number(e.target.value) }))}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      fontSize: '0.875rem'
                    }}
                    min="0"
                  />
                </div>

                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                    카테고리
                  </label>
                  <input
                    type="text"
                    value={formData.category}
                    onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      fontSize: '0.875rem'
                    }}
                    placeholder="예: 원두, 유제품, 소모품"
                  />
                </div>

                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                    공급업체
                  </label>
                  <input
                    type="text"
                    value={formData.supplier}
                    onChange={(e) => setFormData(prev => ({ ...prev, supplier: e.target.value }))}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      fontSize: '0.875rem'
                    }}
                    placeholder="공급업체명"
                  />
                </div>

                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                    단가 (원)
                  </label>
                  <input
                    type="number"
                    value={formData.cost_per_unit}
                    onChange={(e) => setFormData(prev => ({ ...prev, cost_per_unit: Number(e.target.value) }))}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      fontSize: '0.875rem'
                    }}
                    min="0"
                    step="100"
                  />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                  설명
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '0.875rem',
                    minHeight: '100px',
                    resize: 'vertical'
                  }}
                  placeholder="재고에 대한 설명을 입력하세요"
                />
              </div>

              <div style={{
                display: 'flex',
                gap: '1rem',
                justifyContent: 'flex-end',
                marginTop: '1.5rem'
              }}>
                <button
                  type="button"
                  onClick={() => {
                    setIsCreateDialogOpen(false);
                    resetForm();
                  }}
                  style={{
                    padding: '0.75rem 1.5rem',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    backgroundColor: 'white',
                    color: '#374151',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    cursor: 'pointer'
                  }}
                  disabled={isLoading}
                >
                  취소
                </button>
                <button
                  type="submit"
                  disabled={isLoading}
                  style={{
                    padding: '0.75rem 1.5rem',
                    border: 'none',
                    borderRadius: '6px',
                    backgroundColor: isLoading ? '#9ca3af' : '#10b981',
                    color: 'white',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    cursor: isLoading ? 'not-allowed' : 'pointer'
                  }}
                >
                  {isLoading ? '처리 중...' : (editingInventory ? '수정' : '추가')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
} 
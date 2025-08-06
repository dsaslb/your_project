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
  ShoppingCart, 
  Plus, 
  Search, 
  Edit, 
  Trash2, 
  CheckCircle,
  XCircle,
  Clock,
  DollarSign,
  Users,
  TrendingUp,
  BarChart3,
  Package
} from 'lucide-react';
import { toast } from 'sonner';
import { apiClient, Store as StoreType } from '../../src/lib/api-client';
import useLoadingState from '../../src/hooks/useLoadingState';
import useErrorHandler from '../../src/hooks/useErrorHandler';

interface Order {
  id: number;
  order_number: string;
  customer_name: string;
  customer_phone?: string;
  customer_email?: string;
  total_amount: number;
  status: 'pending' | 'confirmed' | 'preparing' | 'ready' | 'completed' | 'cancelled';
  store_id: number;
  store_name?: string;
  items: OrderItem[];
  notes?: string;
  payment_method: 'cash' | 'card' | 'mobile' | 'online';
  created_at: string;
  updated_at: string;
}

interface OrderItem {
  id: number;
  order_id: number;
  product_name: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  notes?: string;
}

interface Product {
  id: number;
  name: string;
  description?: string;
  price: number;
  category: string;
  store_id: number;
  is_available: boolean;
}

interface OrderFormData {
  customer_name: string;
  customer_phone: string;
  customer_email: string;
  store_id: number;
  payment_method: 'cash' | 'card' | 'mobile' | 'online';
  notes: string;
  items: Array<{
    product_name: string;
    quantity: number;
    unit_price: number;
    notes: string;
  }>;
}

export default function OrderManagement() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [stores, setStores] = useState<StoreType[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStore, setSelectedStore] = useState<number | 'all'>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [selectedPaymentMethod, setSelectedPaymentMethod] = useState<string>('all');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [editingOrder, setEditingOrder] = useState<Order | null>(null);
  
  const [formData, setFormData] = useState<OrderFormData>({
    customer_name: '',
    customer_phone: '',
    customer_email: '',
    store_id: 0,
    payment_method: 'cash',
    notes: '',
    items: [{ product_name: '', quantity: 1, unit_price: 0, notes: '' }]
  });

  const { isLoading, setLoading, withLoading } = useLoadingState();
  const { handleError } = useErrorHandler();

  // 주문 목록 조회
  const fetchOrders = async () => {
    try {
      // 임시로 샘플 데이터 사용
      const sampleOrders: Order[] = [
        {
          id: 1,
          order_number: 'ORD-2024-001',
          customer_name: '김철수',
          customer_phone: '010-1234-5678',
          customer_email: 'kim@example.com',
          total_amount: 15000,
          status: 'completed',
          store_id: 1,
          store_name: '스타벅스 강남점',
          items: [
            {
              id: 1,
              order_id: 1,
              product_name: '아메리카노',
              quantity: 2,
              unit_price: 4500,
              total_price: 9000,
              notes: 'ICE'
            },
            {
              id: 2,
              order_id: 1,
              product_name: '카페라떼',
              quantity: 1,
              unit_price: 6000,
              total_price: 6000,
              notes: 'HOT'
            }
          ],
          notes: '테이크아웃',
          payment_method: 'card',
          created_at: '2024-01-15T10:30:00Z',
          updated_at: '2024-01-15T11:00:00Z'
        },
        {
          id: 2,
          order_number: 'ORD-2024-002',
          customer_name: '이영희',
          customer_phone: '010-2345-6789',
          customer_email: 'lee@example.com',
          total_amount: 8000,
          status: 'preparing',
          store_id: 1,
          store_name: '스타벅스 강남점',
          items: [
            {
              id: 3,
              order_id: 2,
              product_name: '카푸치노',
              quantity: 1,
              unit_price: 5000,
              total_price: 5000,
              notes: 'ICE'
            },
            {
              id: 4,
              order_id: 2,
              product_name: '티라떼',
              quantity: 1,
              unit_price: 3000,
              total_price: 3000,
              notes: 'HOT'
            }
          ],
          notes: '',
          payment_method: 'cash',
          created_at: '2024-01-15T11:15:00Z',
          updated_at: '2024-01-15T11:15:00Z'
        },
        {
          id: 3,
          order_number: 'ORD-2024-003',
          customer_name: '박민수',
          customer_phone: '010-3456-7890',
          customer_email: 'park@example.com',
          total_amount: 12000,
          status: 'pending',
          store_id: 2,
          store_name: '스타벅스 홍대점',
          items: [
            {
              id: 5,
              order_id: 3,
              product_name: '모카',
              quantity: 2,
              unit_price: 6000,
              total_price: 12000,
              notes: 'ICE'
            }
          ],
          notes: '매장 내 식사',
          payment_method: 'mobile',
          created_at: '2024-01-15T11:30:00Z',
          updated_at: '2024-01-15T11:30:00Z'
        }
      ];
      
      setOrders(sampleOrders);
    } catch (error) {
      handleError(error as Error);
    }
  };

  // 상품 목록 조회
  const fetchProducts = async () => {
    try {
      // 임시로 샘플 데이터 사용
      const sampleProducts: Product[] = [
        { id: 1, name: '아메리카노', description: '에스프레소 + 물', price: 4500, category: '커피', store_id: 1, is_available: true },
        { id: 2, name: '카페라떼', description: '에스프레소 + 우유', price: 6000, category: '커피', store_id: 1, is_available: true },
        { id: 3, name: '카푸치노', description: '에스프레소 + 우유 + 우유거품', price: 5000, category: '커피', store_id: 1, is_available: true },
        { id: 4, name: '모카', description: '에스프레소 + 우유 + 초콜릿', price: 6000, category: '커피', store_id: 2, is_available: true },
        { id: 5, name: '티라떼', description: '홍차 + 우유', price: 3000, category: '차', store_id: 1, is_available: true }
      ];
      
      setProducts(sampleProducts);
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

  const resetForm = () => {
    setFormData({
      customer_name: '',
      customer_phone: '',
      customer_email: '',
      store_id: 0,
      payment_method: 'cash',
      notes: '',
      items: [{ product_name: '', quantity: 1, unit_price: 0, notes: '' }]
    });
    setEditingOrder(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.customer_name.trim() || formData.store_id === 0) {
      toast.error('필수 항목을 입력해주세요.');
      return;
    }

    try {
      setLoading(true);
      
      // 실제 API 호출 대신 시뮬레이션
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      if (editingOrder) {
        // 수정
        setOrders(prev => prev.map(order => 
          order.id === editingOrder.id 
            ? { ...order, ...formData, updated_at: new Date().toISOString() }
            : order
        ));
        toast.success('주문이 수정되었습니다.');
      } else {
        // 생성
        const newOrder: Order = {
          id: Date.now(),
          order_number: `ORD-2024-${String(Date.now()).slice(-3)}`,
          ...formData,
          store_name: stores.find(s => s.id === formData.store_id)?.name,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };
        
        setOrders(prev => [...prev, newOrder]);
        toast.success('주문이 생성되었습니다.');
      }
      
      setIsCreateDialogOpen(false);
      resetForm();
      
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (order: Order) => {
    if (!confirm(`${order.order_number} 주문을 삭제하시겠습니까?`)) return;
    
    try {
      setLoading(true);
      // 실제 API 호출 대신 시뮬레이션
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setOrders(prev => prev.filter(o => o.id !== order.id));
      toast.success('주문이 삭제되었습니다.');
      
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (order: Order, newStatus: Order['status']) => {
    try {
      setLoading(true);
      // 실제 API 호출 대신 시뮬레이션
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setOrders(prev => prev.map(o => 
        o.id === order.id 
          ? { ...o, status: newStatus, updated_at: new Date().toISOString() }
          : o
      ));
      
      toast.success('주문 상태가 변경되었습니다.');
      
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (order: Order) => {
    setEditingOrder(order);
    setFormData({
      customer_name: order.customer_name,
      customer_phone: order.customer_phone || '',
      customer_email: order.customer_email || '',
      store_id: order.store_id,
      payment_method: order.payment_method,
      notes: order.notes || '',
      items: order.items.map(item => ({
        product_name: item.product_name,
        quantity: item.quantity,
        unit_price: item.unit_price,
        notes: item.notes || ''
      }))
    });
    setIsCreateDialogOpen(true);
  };

  const addOrderItem = () => {
    setFormData(prev => ({
      ...prev,
      items: [...prev.items, { product_name: '', quantity: 1, unit_price: 0, notes: '' }]
    }));
  };

  const removeOrderItem = (index: number) => {
    setFormData(prev => ({
      ...prev,
      items: prev.items.filter((_, i) => i !== index)
    }));
  };

  const updateOrderItem = (index: number, field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      items: prev.items.map((item, i) => 
        i === index ? { ...item, [field]: value } : item
      )
    }));
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return '#f59e0b';
      case 'confirmed': return '#3b82f6';
      case 'preparing': return '#8b5cf6';
      case 'ready': return '#10b981';
      case 'completed': return '#059669';
      case 'cancelled': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending': return '대기중';
      case 'confirmed': return '확인됨';
      case 'preparing': return '준비중';
      case 'ready': return '준비완료';
      case 'completed': return '완료';
      case 'cancelled': return '취소됨';
      default: return '알 수 없음';
    }
  };

  const getPaymentMethodText = (method: string) => {
    switch (method) {
      case 'cash': return '현금';
      case 'card': return '카드';
      case 'mobile': return '모바일';
      case 'online': return '온라인';
      default: return '알 수 없음';
    }
  };

  useEffect(() => {
    fetchOrders();
    fetchProducts();
    fetchStores();
  }, []);

  const filteredOrders = orders.filter(order => {
    const matchesSearch = order.order_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         order.customer_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStore = selectedStore === 'all' || order.store_id === selectedStore;
    const matchesStatus = selectedStatus === 'all' || order.status === selectedStatus;
    const matchesPayment = selectedPaymentMethod === 'all' || order.payment_method === selectedPaymentMethod;
    
    return matchesSearch && matchesStore && matchesStatus && matchesPayment;
  });

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
              주문 관리
            </h1>
            <p style={{
              fontSize: '1.125rem',
              color: '#6b7280'
            }}>
              주문 현황 및 고객 관리
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
            주문 추가
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
              <h3 style={{ fontSize: '0.875rem', margin: '0' }}>총 주문</h3>
              <ShoppingCart style={{ width: '20px', height: '20px' }} />
            </div>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0 0 0.5rem 0' }}>
              {orders.length}
            </p>
            <p style={{ fontSize: '0.875rem', opacity: '0.8', margin: '0' }}>
              오늘: {orders.filter(order => new Date(order.created_at).toDateString() === new Date().toDateString()).length}건
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
              <h3 style={{ fontSize: '0.875rem', margin: '0' }}>완료</h3>
              <CheckCircle style={{ width: '20px', height: '20px' }} />
            </div>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0 0 0.5rem 0' }}>
              {orders.filter(order => order.status === 'completed').length}
            </p>
            <p style={{ fontSize: '0.875rem', opacity: '0.8', margin: '0' }}>
              성공률: {Math.round((orders.filter(order => order.status === 'completed').length / orders.length) * 100)}%
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
              <h3 style={{ fontSize: '0.875rem', margin: '0' }}>진행중</h3>
              <Clock style={{ width: '20px', height: '20px' }} />
            </div>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0 0 0.5rem 0' }}>
              {orders.filter(order => ['pending', 'confirmed', 'preparing', 'ready'].includes(order.status)).length}
            </p>
            <p style={{ fontSize: '0.875rem', opacity: '0.8', margin: '0' }}>
              처리 대기중
            </p>
          </div>

          <div style={{
            backgroundColor: '#8b5cf6',
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
              <h3 style={{ fontSize: '0.875rem', margin: '0' }}>총 매출</h3>
              <DollarSign style={{ width: '20px', height: '20px' }} />
            </div>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0 0 0.5rem 0' }}>
              ₩{orders.reduce((sum, order) => sum + order.total_amount, 0).toLocaleString()}
            </p>
            <p style={{ fontSize: '0.875rem', opacity: '0.8', margin: '0' }}>
              평균: ₩{Math.round(orders.reduce((sum, order) => sum + order.total_amount, 0) / orders.length).toLocaleString()}
            </p>
          </div>
        </div>

        {/* 검색 및 필터 */}
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
                placeholder="주문번호 또는 고객명으로 검색"
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
                <option value="pending">대기중</option>
                <option value="confirmed">확인됨</option>
                <option value="preparing">준비중</option>
                <option value="ready">준비완료</option>
                <option value="completed">완료</option>
                <option value="cancelled">취소됨</option>
              </select>
            </div>
            
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                결제 방법
              </label>
              <select
                value={selectedPaymentMethod}
                onChange={(e) => setSelectedPaymentMethod(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '0.875rem',
                  backgroundColor: 'white'
                }}
              >
                <option value="all">전체 결제</option>
                <option value="cash">현금</option>
                <option value="card">카드</option>
                <option value="mobile">모바일</option>
                <option value="online">온라인</option>
              </select>
            </div>
          </div>
        </div>

        {/* 주문 목록 */}
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
              주문 목록 ({filteredOrders.length}건)
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
                    주문번호
                  </th>
                  <th style={{
                    padding: '1rem',
                    textAlign: 'left',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    color: '#374151'
                  }}>
                    고객명
                  </th>
                  <th style={{
                    padding: '1rem',
                    textAlign: 'left',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    color: '#374151'
                  }}>
                    금액
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
                    결제
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
                {filteredOrders.map((order) => (
                  <tr key={order.id} style={{
                    borderBottom: '1px solid #e5e7eb'
                  }}>
                    <td style={{
                      padding: '1rem',
                      fontSize: '0.875rem',
                      color: '#374151'
                    }}>
                      <p style={{ fontWeight: '500', margin: '0 0 0.25rem 0' }}>
                        {order.order_number}
                      </p>
                      <p style={{ fontSize: '0.75rem', color: '#6b7280', margin: '0' }}>
                        {new Date(order.created_at).toLocaleString('ko-KR')}
                      </p>
                    </td>
                    <td style={{
                      padding: '1rem',
                      fontSize: '0.875rem',
                      color: '#374151'
                    }}>
                      <p style={{ fontWeight: '500', margin: '0 0 0.25rem 0' }}>
                        {order.customer_name}
                      </p>
                      {order.customer_phone && (
                        <p style={{ fontSize: '0.75rem', color: '#6b7280', margin: '0' }}>
                          {order.customer_phone}
                        </p>
                      )}
                    </td>
                    <td style={{
                      padding: '1rem',
                      fontSize: '0.875rem',
                      color: '#374151'
                    }}>
                      <p style={{ fontWeight: '500', margin: '0' }}>
                        ₩{order.total_amount.toLocaleString()}
                      </p>
                    </td>
                    <td style={{
                      padding: '1rem'
                    }}>
                      <span style={{
                        padding: '0.25rem 0.75rem',
                        borderRadius: '9999px',
                        fontSize: '0.75rem',
                        fontWeight: '500',
                        backgroundColor: getStatusColor(order.status) + '20',
                        color: getStatusColor(order.status)
                      }}>
                        {getStatusText(order.status)}
                      </span>
                    </td>
                    <td style={{
                      padding: '1rem',
                      fontSize: '0.875rem',
                      color: '#374151'
                    }}>
                      {order.store_name}
                    </td>
                    <td style={{
                      padding: '1rem',
                      fontSize: '0.875rem',
                      color: '#374151'
                    }}>
                      {getPaymentMethodText(order.payment_method)}
                    </td>
                    <td style={{
                      padding: '1rem'
                    }}>
                      <div style={{
                        display: 'flex',
                        gap: '0.5rem'
                      }}>
                        <button
                          onClick={() => handleEdit(order)}
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
                          onClick={() => handleDelete(order)}
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
          
          {filteredOrders.length === 0 && (
            <div style={{
              padding: '3rem',
              textAlign: 'center',
              color: '#6b7280'
            }}>
              <ShoppingCart style={{ width: '48px', height: '48px', margin: '0 auto 1rem', opacity: '0.5' }} />
              <p>검색 결과가 없습니다.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 
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
  Package,
  RefreshCw
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

  const { isLoading, setLoading } = useLoadingState();
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
          store_name: '강남점',
          items: [
            {
              id: 1,
              order_id: 1,
              product_name: '아메리카노',
              quantity: 2,
              unit_price: 4500,
              total_price: 9000
            },
            {
              id: 2,
              order_id: 1,
              product_name: '카페라떼',
              quantity: 1,
              unit_price: 6000,
              total_price: 6000
            }
          ],
          notes: '따뜻하게 해주세요',
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
          store_name: '강남점',
          items: [
            {
              id: 3,
              order_id: 2,
              product_name: '카푸치노',
              quantity: 1,
              unit_price: 5500,
              total_price: 5500
            },
            {
              id: 4,
              order_id: 2,
              product_name: '티라떼',
              quantity: 1,
              unit_price: 2500,
              total_price: 2500
            }
          ],
          notes: '',
          payment_method: 'cash',
          created_at: '2024-01-15T11:15:00Z',
          updated_at: '2024-01-15T11:20:00Z'
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
          store_name: '홍대점',
          items: [
            {
              id: 5,
              order_id: 3,
              product_name: '모카',
              quantity: 2,
              unit_price: 6000,
              total_price: 12000
            }
          ],
          notes: '샷 추가해주세요',
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
      const sampleProducts: Product[] = [
        { id: 1, name: '아메리카노', description: '에스프레소 + 물', price: 4500, category: '커피', store_id: 1, is_available: true },
        { id: 2, name: '카페라떼', description: '에스프레소 + 우유', price: 6000, category: '커피', store_id: 1, is_available: true },
        { id: 3, name: '카푸치노', description: '에스프레소 + 우유 + 우유거품', price: 5500, category: '커피', store_id: 1, is_available: true },
        { id: 4, name: '모카', description: '에스프레소 + 우유 + 초콜릿', price: 6000, category: '커피', store_id: 2, is_available: true },
        { id: 5, name: '티라떼', description: '홍차 + 우유', price: 2500, category: '차', store_id: 1, is_available: true }
      ];
      setProducts(sampleProducts);
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

  // 주문 추가/수정
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.customer_name || formData.store_id === 0) {
      toast.error('필수 항목을 입력해주세요.');
      return;
    }

    try {
      setLoading(true);
      
      if (editingOrder) {
        // 수정
        const updatedOrder = {
          ...editingOrder,
          customer_name: formData.customer_name,
          customer_phone: formData.customer_phone,
          customer_email: formData.customer_email,
          store_id: formData.store_id,
          store_name: stores.find(s => s.id === formData.store_id)?.name,
          payment_method: formData.payment_method,
          notes: formData.notes,
          items: formData.items.map((item, index) => ({
            id: index + 1,
            order_id: editingOrder.id,
            product_name: item.product_name,
            quantity: item.quantity,
            unit_price: item.unit_price,
            total_price: item.quantity * item.unit_price,
            notes: item.notes
          })),
          total_amount: formData.items.reduce((sum, item) => sum + (item.quantity * item.unit_price), 0),
          updated_at: new Date().toISOString()
        };
        
        setOrders(prev => prev.map(order => 
          order.id === editingOrder.id ? updatedOrder : order
        ));
        
        toast.success('주문이 수정되었습니다.');
      } else {
        // 추가
        const newOrder: Order = {
          id: Date.now(),
          order_number: `ORD-${new Date().getFullYear()}-${String(Date.now()).slice(-3)}`,
          customer_name: formData.customer_name,
          customer_phone: formData.customer_phone,
          customer_email: formData.customer_email,
          store_id: formData.store_id,
          store_name: stores.find(s => s.id === formData.store_id)?.name,
          payment_method: formData.payment_method,
          notes: formData.notes,
          items: formData.items.map((item, index) => ({
            id: index + 1,
            order_id: Date.now(),
            product_name: item.product_name,
            quantity: item.quantity,
            unit_price: item.unit_price,
            total_price: item.quantity * item.unit_price,
            notes: item.notes
          })),
          total_amount: formData.items.reduce((sum, item) => sum + (item.quantity * item.unit_price), 0),
          status: 'pending',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };
        
        setOrders(prev => [...prev, newOrder]);
        toast.success('주문이 추가되었습니다.');
      }
      
      setIsCreateDialogOpen(false);
      resetForm();
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 주문 삭제
  const handleDelete = async (order: Order) => {
    try {
      setLoading(true);
      setOrders(prev => prev.filter(o => o.id !== order.id));
      toast.success('주문이 삭제되었습니다.');
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 주문 상태 변경
  const handleStatusChange = async (order: Order, newStatus: Order['status']) => {
    try {
      setLoading(true);
      
      const updatedOrder = {
        ...order,
        status: newStatus,
        updated_at: new Date().toISOString()
      };
      
      setOrders(prev => prev.map(o => 
        o.id === order.id ? updatedOrder : o
      ));
      
      toast.success(`주문 상태가 ${getStatusText(newStatus)}로 변경되었습니다.`);
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 편집 모드 시작
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

  // 주문 항목 추가
  const addOrderItem = () => {
    setFormData(prev => ({
      ...prev,
      items: [...prev.items, { product_name: '', quantity: 1, unit_price: 0, notes: '' }]
    }));
  };

  // 주문 항목 제거
  const removeOrderItem = (index: number) => {
    setFormData(prev => ({
      ...prev,
      items: prev.items.filter((_, i) => i !== index)
    }));
  };

  // 주문 항목 업데이트
  const updateOrderItem = (index: number, field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      items: prev.items.map((item, i) => 
        i === index ? { ...item, [field]: value } : item
      )
    }));
  };

  // 상태별 색상
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-500/20 text-yellow-400';
      case 'confirmed': return 'bg-blue-500/20 text-blue-400';
      case 'preparing': return 'bg-orange-500/20 text-orange-400';
      case 'ready': return 'bg-green-500/20 text-green-400';
      case 'completed': return 'bg-green-600/20 text-green-500';
      case 'cancelled': return 'bg-red-500/20 text-red-400';
      default: return 'bg-gray-500/20 text-gray-400';
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
    <div className="min-h-screen p-6">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <ShoppingCart className="w-6 h-6" />
          주문 관리
        </h1>
        <p className="text-gray-300 mt-2">주문 현황 및 고객 관리</p>
      </div>

      {/* 액션 버튼 */}
      <div className="flex gap-4 mb-8">
        <Button
          onClick={() => setIsCreateDialogOpen(true)}
          className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700"
        >
          <Plus className="w-4 h-4 mr-2" />
          주문 추가
        </Button>
        <Button
          onClick={fetchOrders}
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
                <p className="text-gray-300 text-sm">총 주문</p>
                <p className="text-2xl font-bold text-white">{orders.length}</p>
                <p className="text-gray-400 text-sm">오늘: {orders.filter(order => new Date(order.created_at).toDateString() === new Date().toDateString()).length}건</p>
              </div>
              <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
                <ShoppingCart className="w-6 h-6 text-blue-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">완료</p>
                <p className="text-2xl font-bold text-white">{orders.filter(order => order.status === 'completed').length}</p>
                <p className="text-gray-400 text-sm">성공률: {Math.round((orders.filter(order => order.status === 'completed').length / orders.length) * 100)}%</p>
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
                <p className="text-gray-300 text-sm">진행중</p>
                <p className="text-2xl font-bold text-white">{orders.filter(order => ['pending', 'confirmed', 'preparing', 'ready'].includes(order.status)).length}</p>
                <p className="text-gray-400 text-sm">처리 대기중</p>
              </div>
              <div className="w-12 h-12 bg-yellow-500/20 rounded-lg flex items-center justify-center">
                <Clock className="w-6 h-6 text-yellow-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">총 매출</p>
                <p className="text-2xl font-bold text-white">₩{orders.reduce((sum, order) => sum + order.total_amount, 0).toLocaleString()}</p>
                <p className="text-gray-400 text-sm">평균: ₩{Math.round(orders.reduce((sum, order) => sum + order.total_amount, 0) / orders.length).toLocaleString()}</p>
              </div>
              <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center">
                <DollarSign className="w-6 h-6 text-purple-400" />
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
                placeholder="주문번호 또는 고객명으로 검색..."
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
                  <SelectItem value="pending">대기중</SelectItem>
                  <SelectItem value="confirmed">확인됨</SelectItem>
                  <SelectItem value="preparing">준비중</SelectItem>
                  <SelectItem value="ready">준비완료</SelectItem>
                  <SelectItem value="completed">완료</SelectItem>
                  <SelectItem value="cancelled">취소됨</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label className="text-gray-300 text-sm">결제 방법</Label>
              <Select value={selectedPaymentMethod} onValueChange={setSelectedPaymentMethod}>
                <SelectTrigger className="mt-1 bg-white/10 border-white/20 text-white">
                  <SelectValue placeholder="결제 방법 선택" />
                </SelectTrigger>
                <SelectContent className="bg-white/10 border-white/20">
                  <SelectItem value="all">모든 방법</SelectItem>
                  <SelectItem value="cash">현금</SelectItem>
                  <SelectItem value="card">카드</SelectItem>
                  <SelectItem value="mobile">모바일</SelectItem>
                  <SelectItem value="online">온라인</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 주문 목록 */}
      <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
        <CardHeader>
          <CardTitle className="text-white">주문 목록 ({filteredOrders.length}건)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredOrders.map((order) => (
              <div
                key={order.id}
                className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:bg-white/10 transition-all duration-300"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-4 mb-3">
                      <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                        <ShoppingCart className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-white">{order.order_number}</h3>
                        <p className="text-gray-400">{order.customer_name}</p>
                        <p className="text-gray-400 text-sm">{order.store_name} • {getPaymentMethodText(order.payment_method)}</p>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                      <div>
                        <p className="text-gray-300 text-sm">총 금액</p>
                        <p className="text-white font-medium">₩{order.total_amount.toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="text-gray-300 text-sm">주문 시간</p>
                        <p className="text-white font-medium">{new Date(order.created_at).toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="text-gray-300 text-sm">상품 수</p>
                        <p className="text-white font-medium">{order.items.length}개</p>
                      </div>
                      <div>
                        <p className="text-gray-300 text-sm">고객 연락처</p>
                        <p className="text-white font-medium">{order.customer_phone || '없음'}</p>
                      </div>
                    </div>
                    
                    {order.items.length > 0 && (
                      <div className="bg-white/5 rounded-lg p-3">
                        <p className="text-gray-300 text-sm mb-2">주문 상품</p>
                        <div className="space-y-1">
                          {order.items.map((item, index) => (
                            <div key={index} className="flex justify-between text-sm">
                              <span className="text-gray-300">{item.product_name} x {item.quantity}</span>
                              <span className="text-white">₩{item.total_price.toLocaleString()}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                  
                  <div className="flex flex-col gap-2 ml-4">
                    <Badge className={getStatusColor(order.status)}>
                      {getStatusText(order.status)}
                    </Badge>
                    
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleEdit(order)}
                        className="border-white/20 text-white hover:bg-white/10"
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button
                        size="sm"
                        onClick={() => handleDelete(order)}
                        className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                    
                    <div className="flex gap-1">
                      {order.status !== 'completed' && order.status !== 'cancelled' && (
                        <Button
                          size="sm"
                          onClick={() => handleStatusChange(order, 'completed')}
                          className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700"
                        >
                          <CheckCircle className="w-4 h-4" />
                        </Button>
                      )}
                      {order.status !== 'cancelled' && (
                        <Button
                          size="sm"
                          onClick={() => handleStatusChange(order, 'cancelled')}
                          className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700"
                        >
                          <XCircle className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 주문 추가/수정 다이얼로그 */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="bg-white/10 backdrop-blur-sm border border-white/20 max-w-4xl">
          <DialogHeader>
            <DialogTitle className="text-white">
              {editingOrder ? '주문 수정' : '주문 추가'}
            </DialogTitle>
          </DialogHeader>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label className="text-gray-300">고객명 *</Label>
                <Input
                  value={formData.customer_name}
                  onChange={(e) => setFormData({...formData, customer_name: e.target.value})}
                  className="mt-1 bg-white/10 border-white/20 text-white"
                  placeholder="고객명을 입력하세요"
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
                <Label className="text-gray-300">연락처</Label>
                <Input
                  value={formData.customer_phone}
                  onChange={(e) => setFormData({...formData, customer_phone: e.target.value})}
                  className="mt-1 bg-white/10 border-white/20 text-white"
                  placeholder="연락처를 입력하세요"
                />
              </div>
              
              <div>
                <Label className="text-gray-300">이메일</Label>
                <Input
                  value={formData.customer_email}
                  onChange={(e) => setFormData({...formData, customer_email: e.target.value})}
                  className="mt-1 bg-white/10 border-white/20 text-white"
                  placeholder="이메일을 입력하세요"
                />
              </div>
              
              <div>
                <Label className="text-gray-300">결제 방법</Label>
                <Select value={formData.payment_method} onValueChange={(value: any) => setFormData({...formData, payment_method: value})}>
                  <SelectTrigger className="mt-1 bg-white/10 border-white/20 text-white">
                    <SelectValue placeholder="결제 방법을 선택하세요" />
                  </SelectTrigger>
                  <SelectContent className="bg-white/10 border-white/20">
                    <SelectItem value="cash">현금</SelectItem>
                    <SelectItem value="card">카드</SelectItem>
                    <SelectItem value="mobile">모바일</SelectItem>
                    <SelectItem value="online">온라인</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div>
              <Label className="text-gray-300">메모</Label>
              <Textarea
                value={formData.notes}
                onChange={(e) => setFormData({...formData, notes: e.target.value})}
                className="mt-1 bg-white/10 border-white/20 text-white"
                placeholder="주문에 대한 메모를 입력하세요"
                rows={2}
              />
            </div>
            
            <div>
              <div className="flex justify-between items-center mb-3">
                <Label className="text-gray-300">주문 상품</Label>
                <Button
                  type="button"
                  onClick={addOrderItem}
                  className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  상품 추가
                </Button>
              </div>
              
              <div className="space-y-3">
                {formData.items.map((item, index) => (
                  <div key={index} className="bg-white/5 rounded-lg p-4">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                      <div>
                        <Label className="text-gray-300 text-sm">상품명</Label>
                        <Input
                          value={item.product_name}
                          onChange={(e) => updateOrderItem(index, 'product_name', e.target.value)}
                          className="mt-1 bg-white/10 border-white/20 text-white"
                          placeholder="상품명을 입력하세요"
                        />
                      </div>
                      
                      <div>
                        <Label className="text-gray-300 text-sm">수량</Label>
                        <Input
                          type="number"
                          value={item.quantity}
                          onChange={(e) => updateOrderItem(index, 'quantity', parseInt(e.target.value) || 1)}
                          className="mt-1 bg-white/10 border-white/20 text-white"
                          placeholder="1"
                        />
                      </div>
                      
                      <div>
                        <Label className="text-gray-300 text-sm">단가</Label>
                        <Input
                          type="number"
                          value={item.unit_price}
                          onChange={(e) => updateOrderItem(index, 'unit_price', parseInt(e.target.value) || 0)}
                          className="mt-1 bg-white/10 border-white/20 text-white"
                          placeholder="0"
                        />
                      </div>
                      
                      <div className="flex items-end gap-2">
                        <div className="flex-1">
                          <Label className="text-gray-300 text-sm">메모</Label>
                          <Input
                            value={item.notes}
                            onChange={(e) => updateOrderItem(index, 'notes', e.target.value)}
                            className="mt-1 bg-white/10 border-white/20 text-white"
                            placeholder="상품 메모"
                          />
                        </div>
                        
                        {formData.items.length > 1 && (
                          <Button
                            type="button"
                            onClick={() => removeOrderItem(index)}
                            className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="flex gap-2">
              <Button type="submit" className="flex-1 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700">
                {editingOrder ? '수정' : '추가'}
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
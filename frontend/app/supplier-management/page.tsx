'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../src/components/ui/card';
import { Button } from '../../src/components/ui/button';
import { Input } from '../../src/components/ui/input';
import { Badge } from '../../src/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '../../src/components/ui/dialog';
import { Label } from '../../src/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../src/components/ui/select';
import { Textarea } from '../../src/components/ui/textarea';
import { apiClient } from '../../src/lib/api-client';
import { useLoadingState } from '../../src/hooks/useLoadingState';
import { useErrorHandler } from '../../src/hooks/useErrorHandler';
import { toast } from 'sonner';
import { 
  Truck, 
  Plus, 
  Search, 
  Filter, 
  Edit, 
  Trash2, 
  Eye, 
  Phone, 
  Mail, 
  MapPin, 
  Calendar, 
  FileText,
  DollarSign,
  Package,
  Clock,
  CheckCircle,
  AlertTriangle,
  Star,
  Building2
} from 'lucide-react';

interface Supplier {
  id: number;
  name: string;
  company_name: string;
  contact_person: string;
  email: string;
  phone: string;
  address: string;
  business_number: string;
  category: string;
  rating: number;
  status: 'active' | 'inactive' | 'suspended';
  contract_start_date: string;
  contract_end_date: string;
  payment_terms: string;
  delivery_terms: string;
  notes?: string;
  total_orders: number;
  total_amount: number;
  average_delivery_time: number;
  quality_rating: number;
  created_at: string;
  updated_at: string;
}

interface SupplierFormData {
  name: string;
  company_name: string;
  contact_person: string;
  email: string;
  phone: string;
  address: string;
  business_number: string;
  category: string;
  contract_start_date: string;
  contract_end_date: string;
  payment_terms: string;
  delivery_terms: string;
  notes: string;
}

interface Contract {
  id: number;
  supplier_id: number;
  supplier_name: string;
  contract_number: string;
  start_date: string;
  end_date: string;
  total_value: number;
  status: 'active' | 'expired' | 'terminated';
  terms: string;
  created_at: string;
}

interface OrderHistory {
  id: number;
  order_number: string;
  supplier_id: number;
  supplier_name: string;
  order_date: string;
  delivery_date?: string;
  total_amount: number;
  status: 'pending' | 'confirmed' | 'shipped' | 'delivered' | 'cancelled';
  items_count: number;
}

export default function SupplierManagement() {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [orderHistory, setOrderHistory] = useState<OrderHistory[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [selectedRating, setSelectedRating] = useState<string>('all');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isContractDialogOpen, setIsContractDialogOpen] = useState(false);
  const [isHistoryDialogOpen, setIsHistoryDialogOpen] = useState(false);
  const [editingSupplier, setEditingSupplier] = useState<Supplier | null>(null);
  const [viewingSupplier, setViewingSupplier] = useState<Supplier | null>(null);
  const [selectedSupplier, setSelectedSupplier] = useState<Supplier | null>(null);
  
  const [formData, setFormData] = useState<SupplierFormData>({
    name: '',
    company_name: '',
    contact_person: '',
    email: '',
    phone: '',
    address: '',
    business_number: '',
    category: '',
    contract_start_date: '',
    contract_end_date: '',
    payment_terms: '',
    delivery_terms: '',
    notes: '',
  });

  const { isLoading, setLoading, withLoading } = useLoadingState();
  const { handleError } = useErrorHandler();

  // 공급업체 목록 조회
  const fetchSuppliers = async () => {
    try {
      const response = await apiClient.get('/api/suppliers');
      if (response.success && response.data) {
        setSuppliers(response.data);
      }
    } catch (error) {
      handleError(error as Error);
    }
  };

  // 계약 목록 조회
  const fetchContracts = async () => {
    try {
      const response = await apiClient.get('/api/contracts');
      if (response.success && response.data) {
        setContracts(response.data);
      }
    } catch (error) {
      handleError(error as Error);
    }
  };

  // 발주 이력 조회
  const fetchOrderHistory = async () => {
    try {
      const response = await apiClient.get('/api/order-history');
      if (response.success && response.data) {
        setOrderHistory(response.data);
      }
    } catch (error) {
      handleError(error as Error);
    }
  };

  // 초기 데이터 로드
  useEffect(() => {
    fetchSuppliers();
    fetchContracts();
    fetchOrderHistory();
  }, []);

  // 폼 초기화
  const resetForm = () => {
    setFormData({
      name: '',
      company_name: '',
      contact_person: '',
      email: '',
      phone: '',
      address: '',
      business_number: '',
      category: '',
      contract_start_date: '',
      contract_end_date: '',
      payment_terms: '',
      delivery_terms: '',
      notes: '',
    });
  };

  // 공급업체 생성/수정 제출
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name || !formData.company_name || !formData.email || !formData.phone) {
      toast.error('필수 정보를 입력해주세요.');
      return;
    }

    try {
      setLoading(true);
      
      if (editingSupplier) {
        // 공급업체 정보 수정
        const response = await apiClient.put(`/api/suppliers/${editingSupplier.id}`, formData);
        if (response.success) {
          toast.success('공급업체 정보가 성공적으로 수정되었습니다.');
          setIsCreateDialogOpen(false);
          setEditingSupplier(null);
          resetForm();
          fetchSuppliers();
        }
      } else {
        // 새 공급업체 생성
        const response = await apiClient.post('/api/suppliers', formData);
        if (response.success) {
          toast.success('공급업체가 성공적으로 등록되었습니다.');
          setIsCreateDialogOpen(false);
          resetForm();
          fetchSuppliers();
        }
      }
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 공급업체 삭제
  const handleDelete = async (supplier: Supplier) => {
    if (!confirm(`정말로 ${supplier.name} 공급업체를 삭제하시겠습니까?`)) {
      return;
    }

    try {
      setLoading(true);
      const response = await apiClient.delete(`/api/suppliers/${supplier.id}`);
      if (response.success) {
        toast.success('공급업체가 성공적으로 삭제되었습니다.');
        fetchSuppliers();
      }
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 공급업체 수정 모드 시작
  const handleEdit = (supplier: Supplier) => {
    setEditingSupplier(supplier);
    setFormData({
      name: supplier.name,
      company_name: supplier.company_name,
      contact_person: supplier.contact_person,
      email: supplier.email,
      phone: supplier.phone,
      address: supplier.address,
      business_number: supplier.business_number,
      category: supplier.category,
      contract_start_date: supplier.contract_start_date,
      contract_end_date: supplier.contract_end_date,
      payment_terms: supplier.payment_terms,
      delivery_terms: supplier.delivery_terms,
      notes: supplier.notes || '',
    });
    setIsCreateDialogOpen(true);
  };

  // 공급업체 상세 보기
  const handleView = (supplier: Supplier) => {
    setViewingSupplier(supplier);
  };

  // 계약 보기
  const handleViewContracts = (supplier: Supplier) => {
    setSelectedSupplier(supplier);
    setIsContractDialogOpen(true);
  };

  // 발주 이력 보기
  const handleViewHistory = (supplier: Supplier) => {
    setSelectedSupplier(supplier);
    setIsHistoryDialogOpen(true);
  };

  // 새 공급업체 생성 모드 시작
  const handleCreate = () => {
    setEditingSupplier(null);
    resetForm();
    setIsCreateDialogOpen(true);
  };

  // 상태별 색상
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500/20 text-green-400 border border-green-500/30';
      case 'inactive': return 'bg-gray-500/20 text-gray-400 border border-gray-500/30';
      case 'suspended': return 'bg-red-500/20 text-red-400 border border-red-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border border-gray-500/30';
    }
  };

  // 등급별 색상
  const getRatingColor = (rating: number) => {
    if (rating >= 4.5) return 'text-yellow-500';
    if (rating >= 4.0) return 'text-green-500';
    if (rating >= 3.0) return 'text-blue-500';
    return 'text-red-500';
  };

  // 필터링된 공급업체 목록
  const filteredSuppliers = suppliers.filter(supplier => {
    const matchesSearch = searchTerm === '' || 
      supplier.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      supplier.company_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      supplier.contact_person.toLowerCase().includes(searchTerm.toLowerCase()) ||
      supplier.email.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesCategory = selectedCategory === 'all' || supplier.category === selectedCategory;
    const matchesStatus = selectedStatus === 'all' || supplier.status === selectedStatus;
    const matchesRating = selectedRating === 'all' || 
      (selectedRating === 'high' && supplier.rating >= 4.5) ||
      (selectedRating === 'medium' && supplier.rating >= 3.5 && supplier.rating < 4.5) ||
      (selectedRating === 'low' && supplier.rating < 3.5);
    
    return matchesSearch && matchesCategory && matchesStatus && matchesRating;
  });

  // 통계 계산
  const totalSuppliers = suppliers.length;
  const activeSuppliers = suppliers.filter(s => s.status === 'active').length;
  const highRatingSuppliers = suppliers.filter(s => s.rating >= 4.5).length;
  const totalContractValue = contracts.reduce((sum, c) => sum + c.total_value, 0);

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Truck className="h-8 w-8 text-blue-600" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">공급업체 관리</h1>
            <p className="text-gray-600">공급업체 정보를 관리하고 계약을 추적하세요</p>
          </div>
        </div>
        <Button onClick={handleCreate} className="bg-blue-600 hover:bg-blue-700">
          <Plus className="h-4 w-4 mr-2" />
          새 공급업체 등록
        </Button>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <Truck className="h-8 w-8 text-blue-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">총 공급업체</p>
                <p className="text-2xl font-bold text-gray-900">{totalSuppliers.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <CheckCircle className="h-8 w-8 text-green-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">활성 공급업체</p>
                <p className="text-2xl font-bold text-gray-900">{activeSuppliers.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <Star className="h-8 w-8 text-yellow-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">고평가 공급업체</p>
                <p className="text-2xl font-bold text-gray-900">{highRatingSuppliers.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <DollarSign className="h-8 w-8 text-green-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">총 계약 금액</p>
                <p className="text-2xl font-bold text-gray-900">₩{totalContractValue.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 필터 및 검색 */}
      <Card>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="공급업체명, 회사명, 담당자 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            
            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger>
                <SelectValue placeholder="카테고리" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">전체 카테고리</SelectItem>
                <SelectItem value="식재료">식재료</SelectItem>
                <SelectItem value="음료">음료</SelectItem>
                <SelectItem value="포장재">포장재</SelectItem>
                <SelectItem value="장비">장비</SelectItem>
                <SelectItem value="서비스">서비스</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={selectedStatus} onValueChange={setSelectedStatus}>
              <SelectTrigger>
                <SelectValue placeholder="상태" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">전체 상태</SelectItem>
                <SelectItem value="active">활성</SelectItem>
                <SelectItem value="inactive">비활성</SelectItem>
                <SelectItem value="suspended">정지</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={selectedRating} onValueChange={setSelectedRating}>
              <SelectTrigger>
                <SelectValue placeholder="평점" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">전체 평점</SelectItem>
                <SelectItem value="high">높음 (4.5+)</SelectItem>
                <SelectItem value="medium">보통 (3.5-4.4)</SelectItem>
                <SelectItem value="low">낮음 (3.5 미만)</SelectItem>
              </SelectContent>
            </Select>
            
            <Button variant="outline" onClick={() => {
              setSearchTerm('');
              setSelectedCategory('all');
              setSelectedStatus('all');
              setSelectedRating('all');
            }}>
              <Filter className="h-4 w-4 mr-2" />
              필터 초기화
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 공급업체 목록 */}
      <Card>
        <CardHeader>
          <CardTitle>공급업체 목록</CardTitle>
          <CardDescription>
            총 {filteredSuppliers.length}개의 공급업체가 있습니다
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredSuppliers.map((supplier) => (
              <div key={supplier.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">{supplier.name}</h3>
                      <Badge className={getStatusColor(supplier.status)}>
                        {supplier.status === 'active' && '활성'}
                        {supplier.status === 'inactive' && '비활성'}
                        {supplier.status === 'suspended' && '정지'}
                      </Badge>
                      <div className={`flex items-center ${getRatingColor(supplier.rating)}`}>
                        <Star className="h-4 w-4 fill-current" />
                        <span className="ml-1 text-sm font-medium">{supplier.rating.toFixed(1)}</span>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                      <div className="flex items-center space-x-2">
                        <Building2 className="h-4 w-4" />
                        <span>{supplier.company_name}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Mail className="h-4 w-4" />
                        <span>{supplier.email}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Phone className="h-4 w-4" />
                        <span>{supplier.phone}</span>
                      </div>
                    </div>
                    
                    <div className="mt-2 text-sm text-gray-500">
                      <span>카테고리: {supplier.category}</span>
                      <span className="mx-2">•</span>
                      <span>총 주문: {supplier.total_orders}회</span>
                      <span className="mx-2">•</span>
                      <span>총 금액: ₩{supplier.total_amount.toLocaleString()}</span>
                      <span className="mx-2">•</span>
                      <span>평균 배송: {supplier.average_delivery_time}일</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleView(supplier)}
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleViewContracts(supplier)}
                    >
                      <FileText className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleViewHistory(supplier)}
                    >
                      <Package className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEdit(supplier)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDelete(supplier)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
            
            {filteredSuppliers.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <Truck className="h-12 w-12 mx-auto mb-2" />
                <p>공급업체가 없습니다.</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* 공급업체 생성/수정 다이얼로그 */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>
              {editingSupplier ? '공급업체 정보 수정' : '새 공급업체 등록'}
            </DialogTitle>
            <DialogDescription>
              {editingSupplier ? '공급업체 정보를 수정하세요.' : '새로운 공급업체를 등록하세요.'}
            </DialogDescription>
          </DialogHeader>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="name">공급업체명 *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </div>
              
              <div>
                <Label htmlFor="company_name">회사명 *</Label>
                <Input
                  id="company_name"
                  value={formData.company_name}
                  onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                  required
                />
              </div>
              
              <div>
                <Label htmlFor="contact_person">담당자 *</Label>
                <Input
                  id="contact_person"
                  value={formData.contact_person}
                  onChange={(e) => setFormData({ ...formData, contact_person: e.target.value })}
                  required
                />
              </div>
              
              <div>
                <Label htmlFor="email">이메일 *</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  required
                />
              </div>
              
              <div>
                <Label htmlFor="phone">전화번호 *</Label>
                <Input
                  id="phone"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  required
                />
              </div>
              
              <div>
                <Label htmlFor="business_number">사업자등록번호</Label>
                <Input
                  id="business_number"
                  value={formData.business_number}
                  onChange={(e) => setFormData({ ...formData, business_number: e.target.value })}
                />
              </div>
              
              <div>
                <Label htmlFor="category">카테고리</Label>
                <Select value={formData.category} onValueChange={(value) => setFormData({ ...formData, category: value })}>
                  <SelectTrigger>
                    <SelectValue placeholder="카테고리 선택" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="식재료">식재료</SelectItem>
                    <SelectItem value="음료">음료</SelectItem>
                    <SelectItem value="포장재">포장재</SelectItem>
                    <SelectItem value="장비">장비</SelectItem>
                    <SelectItem value="서비스">서비스</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label htmlFor="contract_start_date">계약 시작일</Label>
                <Input
                  id="contract_start_date"
                  type="date"
                  value={formData.contract_start_date}
                  onChange={(e) => setFormData({ ...formData, contract_start_date: e.target.value })}
                />
              </div>
              
              <div>
                <Label htmlFor="contract_end_date">계약 종료일</Label>
                <Input
                  id="contract_end_date"
                  type="date"
                  value={formData.contract_end_date}
                  onChange={(e) => setFormData({ ...formData, contract_end_date: e.target.value })}
                />
              </div>
              
              <div>
                <Label htmlFor="payment_terms">결제 조건</Label>
                <Input
                  id="payment_terms"
                  value={formData.payment_terms}
                  onChange={(e) => setFormData({ ...formData, payment_terms: e.target.value })}
                  placeholder="예: 30일 후 결제"
                />
              </div>
              
              <div>
                <Label htmlFor="delivery_terms">배송 조건</Label>
                <Input
                  id="delivery_terms"
                  value={formData.delivery_terms}
                  onChange={(e) => setFormData({ ...formData, delivery_terms: e.target.value })}
                  placeholder="예: 3-5일 배송"
                />
              </div>
            </div>
            
            <div>
              <Label htmlFor="address">주소</Label>
              <Input
                id="address"
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
              />
            </div>
            
            <div>
              <Label htmlFor="notes">메모</Label>
              <Textarea
                id="notes"
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                rows={3}
              />
            </div>
            
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                취소
              </Button>
              <Button type="submit" disabled={isLoading}>
                {isLoading ? '처리 중...' : (editingSupplier ? '수정' : '등록')}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* 공급업체 상세 보기 다이얼로그 */}
      <Dialog open={!!viewingSupplier} onOpenChange={() => setViewingSupplier(null)}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>공급업체 상세 정보</DialogTitle>
            <DialogDescription>
              {viewingSupplier?.name} 공급업체의 상세 정보입니다.
            </DialogDescription>
          </DialogHeader>
          
          {viewingSupplier && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label className="text-sm font-medium text-gray-600">공급업체명</Label>
                  <p className="text-lg font-semibold">{viewingSupplier.name}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">회사명</Label>
                  <p className="text-lg">{viewingSupplier.company_name}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">담당자</Label>
                  <p className="text-lg">{viewingSupplier.contact_person}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">이메일</Label>
                  <p className="text-lg">{viewingSupplier.email}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">전화번호</Label>
                  <p className="text-lg">{viewingSupplier.phone}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">사업자등록번호</Label>
                  <p className="text-lg">{viewingSupplier.business_number || '미입력'}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">카테고리</Label>
                  <Badge variant="secondary">{viewingSupplier.category}</Badge>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">상태</Label>
                  <Badge className={getStatusColor(viewingSupplier.status)}>
                    {viewingSupplier.status === 'active' && '활성'}
                    {viewingSupplier.status === 'inactive' && '비활성'}
                    {viewingSupplier.status === 'suspended' && '정지'}
                  </Badge>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">평점</Label>
                  <div className={`flex items-center ${getRatingColor(viewingSupplier.rating)}`}>
                    <Star className="h-5 w-5 fill-current" />
                    <span className="ml-1 text-lg font-semibold">{viewingSupplier.rating.toFixed(1)}</span>
                  </div>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">품질 평점</Label>
                  <div className={`flex items-center ${getRatingColor(viewingSupplier.quality_rating)}`}>
                    <Star className="h-5 w-5 fill-current" />
                    <span className="ml-1 text-lg font-semibold">{viewingSupplier.quality_rating.toFixed(1)}</span>
                  </div>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">총 주문 수</Label>
                  <p className="text-lg font-semibold text-blue-600">{viewingSupplier.total_orders}회</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">총 거래 금액</Label>
                  <p className="text-lg font-semibold text-green-600">₩{viewingSupplier.total_amount.toLocaleString()}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">평균 배송 시간</Label>
                  <p className="text-lg">{viewingSupplier.average_delivery_time}일</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">계약 시작일</Label>
                  <p className="text-lg">{new Date(viewingSupplier.contract_start_date).toLocaleDateString('ko-KR')}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">계약 종료일</Label>
                  <p className="text-lg">{new Date(viewingSupplier.contract_end_date).toLocaleDateString('ko-KR')}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">결제 조건</Label>
                  <p className="text-lg">{viewingSupplier.payment_terms}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">배송 조건</Label>
                  <p className="text-lg">{viewingSupplier.delivery_terms}</p>
                </div>
              </div>
              
              <div>
                <Label className="text-sm font-medium text-gray-600">주소</Label>
                <p className="text-lg">{viewingSupplier.address}</p>
              </div>
              
              {viewingSupplier.notes && (
                <div>
                  <Label className="text-sm font-medium text-gray-600">메모</Label>
                  <p className="text-lg bg-gray-50 p-3 rounded-lg">{viewingSupplier.notes}</p>
                </div>
              )}
            </div>
          )}
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setViewingSupplier(null)}>
              닫기
            </Button>
            {viewingSupplier && (
              <Button onClick={() => {
                setViewingSupplier(null);
                handleEdit(viewingSupplier);
              }}>
                수정하기
              </Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 계약 목록 다이얼로그 */}
      <Dialog open={isContractDialogOpen} onOpenChange={setIsContractDialogOpen}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>계약 목록</DialogTitle>
            <DialogDescription>
              {selectedSupplier?.name} 공급업체의 계약 정보입니다.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            {contracts.filter(contract => contract.supplier_id === selectedSupplier?.id).map((contract) => (
              <div key={contract.id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-lg font-semibold">{contract.contract_number}</h3>
                  <Badge className={getStatusColor(contract.status)}>
                    {contract.status === 'active' && '활성'}
                    {contract.status === 'expired' && '만료'}
                    {contract.status === 'terminated' && '해지'}
                  </Badge>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="font-medium">계약 기간:</span>
                    <p>{new Date(contract.start_date).toLocaleDateString('ko-KR')} ~ {new Date(contract.end_date).toLocaleDateString('ko-KR')}</p>
                  </div>
                  <div>
                    <span className="font-medium">계약 금액:</span>
                    <p className="text-green-600 font-semibold">₩{contract.total_value.toLocaleString()}</p>
                  </div>
                  <div>
                    <span className="font-medium">계약일:</span>
                    <p>{new Date(contract.created_at).toLocaleDateString('ko-KR')}</p>
                  </div>
                </div>
                {contract.terms && (
                  <div className="mt-2">
                    <span className="font-medium text-sm">계약 조건:</span>
                    <p className="text-sm text-gray-600 mt-1">{contract.terms}</p>
                  </div>
                )}
              </div>
            ))}
            
            {contracts.filter(contract => contract.supplier_id === selectedSupplier?.id).length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <FileText className="h-12 w-12 mx-auto mb-2" />
                <p>계약 정보가 없습니다.</p>
              </div>
            )}
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsContractDialogOpen(false)}>
              닫기
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 발주 이력 다이얼로그 */}
      <Dialog open={isHistoryDialogOpen} onOpenChange={setIsHistoryDialogOpen}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>발주 이력</DialogTitle>
            <DialogDescription>
              {selectedSupplier?.name} 공급업체의 발주 이력입니다.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            {orderHistory.filter(order => order.supplier_id === selectedSupplier?.id).map((order) => (
              <div key={order.id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-lg font-semibold">{order.order_number}</h3>
                  <Badge className={getStatusColor(order.status)}>
                    {order.status === 'pending' && '대기'}
                    {order.status === 'confirmed' && '확정'}
                    {order.status === 'shipped' && '배송중'}
                    {order.status === 'delivered' && '배송완료'}
                    {order.status === 'cancelled' && '취소'}
                  </Badge>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="font-medium">주문일:</span>
                    <p>{new Date(order.order_date).toLocaleDateString('ko-KR')}</p>
                  </div>
                  <div>
                    <span className="font-medium">배송일:</span>
                    <p>{order.delivery_date ? new Date(order.delivery_date).toLocaleDateString('ko-KR') : '미배송'}</p>
                  </div>
                  <div>
                    <span className="font-medium">주문 금액:</span>
                    <p className="text-green-600 font-semibold">₩{order.total_amount.toLocaleString()}</p>
                  </div>
                  <div>
                    <span className="font-medium">주문 항목:</span>
                    <p>{order.items_count}개</p>
                  </div>
                </div>
              </div>
            ))}
            
            {orderHistory.filter(order => order.supplier_id === selectedSupplier?.id).length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <Package className="h-12 w-12 mx-auto mb-2" />
                <p>발주 이력이 없습니다.</p>
              </div>
            )}
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsHistoryDialogOpen(false)}>
              닫기
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
} 
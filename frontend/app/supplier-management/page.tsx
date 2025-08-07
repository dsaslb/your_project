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
  Building2,
  RefreshCw
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
  const [editingSupplier, setEditingSupplier] = useState<Supplier | null>(null);
  const [viewingSupplier, setViewingSupplier] = useState<Supplier | null>(null);
  const [viewingContracts, setViewingContracts] = useState<Supplier | null>(null);
  const [viewingHistory, setViewingHistory] = useState<Supplier | null>(null);
  
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

  const { isLoading, setLoading } = useLoadingState();
  const { handleError } = useErrorHandler();

  // 공급업체 목록 조회
  const fetchSuppliers = async () => {
    try {
      setLoading(true);
      // 임시로 샘플 데이터 사용
      const sampleSuppliers: Supplier[] = [
        {
          id: 1,
          name: '커피원두공급업체',
          company_name: '커피원두주식회사',
          contact_person: '김철수',
          email: 'kim@coffee.com',
          phone: '02-1234-5678',
          address: '서울시 강남구',
          business_number: '123-45-67890',
          category: '음료',
          rating: 4.8,
          status: 'active',
          contract_start_date: '2024-01-01',
          contract_end_date: '2024-12-31',
          payment_terms: '30일 후 지급',
          delivery_terms: '주문 후 3일 이내',
          notes: '고품질 아라비카 원두 전문',
          total_orders: 45,
          total_amount: 12500000,
          average_delivery_time: 2.5,
          quality_rating: 4.9,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-15T00:00:00Z'
        },
        {
          id: 2,
          name: '우유공급업체',
          company_name: '신선우유유한회사',
          contact_person: '이영희',
          email: 'lee@milk.com',
          phone: '02-2345-6789',
          address: '서울시 마포구',
          business_number: '234-56-78901',
          category: '음료',
          rating: 4.5,
          status: 'active',
          contract_start_date: '2024-01-01',
          contract_end_date: '2024-12-31',
          payment_terms: '15일 후 지급',
          delivery_terms: '매일 아침 배송',
          notes: '유기농 우유 전문',
          total_orders: 120,
          total_amount: 8500000,
          average_delivery_time: 1.0,
          quality_rating: 4.7,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-15T00:00:00Z'
        },
        {
          id: 3,
          name: '시럽공급업체',
          company_name: '시럽스페셜리스트',
          contact_person: '박민수',
          email: 'park@syrup.com',
          phone: '02-3456-7890',
          address: '서울시 서초구',
          business_number: '345-67-89012',
          category: '음료',
          rating: 4.2,
          status: 'active',
          contract_start_date: '2024-01-01',
          contract_end_date: '2024-12-31',
          payment_terms: '30일 후 지급',
          delivery_terms: '주문 후 5일 이내',
          notes: '다양한 시럽 제품',
          total_orders: 28,
          total_amount: 3200000,
          average_delivery_time: 4.0,
          quality_rating: 4.3,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-15T00:00:00Z'
        },
        {
          id: 4,
          name: '포장재공급업체',
          company_name: '에코패키징',
          contact_person: '최지영',
          email: 'choi@packaging.com',
          phone: '02-4567-8901',
          address: '서울시 송파구',
          business_number: '456-78-90123',
          category: '포장재',
          rating: 4.0,
          status: 'inactive',
          contract_start_date: '2023-01-01',
          contract_end_date: '2023-12-31',
          payment_terms: '45일 후 지급',
          delivery_terms: '주문 후 7일 이내',
          notes: '친환경 포장재',
          total_orders: 15,
          total_amount: 1800000,
          average_delivery_time: 6.0,
          quality_rating: 4.1,
          created_at: '2023-01-01T00:00:00Z',
          updated_at: '2023-12-31T00:00:00Z'
        }
      ];
      
      setSuppliers(sampleSuppliers);
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 계약 목록 조회
  const fetchContracts = async () => {
    try {
      const sampleContracts: Contract[] = [
        {
          id: 1,
          supplier_id: 1,
          supplier_name: '커피원두공급업체',
          contract_number: 'CON-2024-001',
          start_date: '2024-01-01',
          end_date: '2024-12-31',
          total_value: 12500000,
          status: 'active',
          terms: '월 100kg 원두 공급',
          created_at: '2024-01-01T00:00:00Z'
        },
        {
          id: 2,
          supplier_id: 2,
          supplier_name: '우유공급업체',
          contract_number: 'CON-2024-002',
          start_date: '2024-01-01',
          end_date: '2024-12-31',
          total_value: 8500000,
          status: 'active',
          terms: '일일 우유 공급',
          created_at: '2024-01-01T00:00:00Z'
        }
      ];
      setContracts(sampleContracts);
    } catch (error) {
      handleError(error as Error);
    }
  };

  // 주문 이력 조회
  const fetchOrderHistory = async () => {
    try {
      const sampleOrderHistory: OrderHistory[] = [
        {
          id: 1,
          order_number: 'ORD-2024-001',
          supplier_id: 1,
          supplier_name: '커피원두공급업체',
          order_date: '2024-01-15',
          delivery_date: '2024-01-17',
          total_amount: 500000,
          status: 'delivered',
          items_count: 2
        },
        {
          id: 2,
          order_number: 'ORD-2024-002',
          supplier_id: 2,
          supplier_name: '우유공급업체',
          order_date: '2024-01-14',
          delivery_date: '2024-01-15',
          total_amount: 200000,
          status: 'delivered',
          items_count: 1
        }
      ];
      setOrderHistory(sampleOrderHistory);
    } catch (error) {
      handleError(error as Error);
    }
  };

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
    setEditingSupplier(null);
  };

  // 공급업체 추가/수정
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name || !formData.company_name || !formData.contact_person) {
      toast.error('필수 항목을 입력해주세요.');
      return;
    }

    try {
      setLoading(true);
      
      if (editingSupplier) {
        // 수정
        const updatedSupplier = {
          ...editingSupplier,
          ...formData,
          updated_at: new Date().toISOString()
        };
        
        setSuppliers(prev => prev.map(supplier => 
          supplier.id === editingSupplier.id ? updatedSupplier : supplier
        ));
        
        toast.success('공급업체 정보가 수정되었습니다.');
      } else {
        // 추가
        const newSupplier: Supplier = {
          id: Date.now(),
          ...formData,
          rating: 4.0,
          status: 'active',
          total_orders: 0,
          total_amount: 0,
          average_delivery_time: 0,
          quality_rating: 4.0,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };
        
        setSuppliers(prev => [...prev, newSupplier]);
        toast.success('공급업체가 추가되었습니다.');
      }
      
      setIsCreateDialogOpen(false);
      resetForm();
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 공급업체 삭제
  const handleDelete = async (supplier: Supplier) => {
    try {
      setLoading(true);
      setSuppliers(prev => prev.filter(s => s.id !== supplier.id));
      toast.success('공급업체가 삭제되었습니다.');
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 편집 모드 시작
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

  // 상세 보기
  const handleView = (supplier: Supplier) => {
    setViewingSupplier(supplier);
  };

  // 계약 보기
  const handleViewContracts = (supplier: Supplier) => {
    setViewingContracts(supplier);
  };

  // 이력 보기
  const handleViewHistory = (supplier: Supplier) => {
    setViewingHistory(supplier);
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
      case 'active': return 'bg-green-500/20 text-green-400';
      case 'inactive': return 'bg-gray-500/20 text-gray-400';
      case 'suspended': return 'bg-red-500/20 text-red-400';
      default: return 'bg-gray-500/20 text-gray-400';
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

  useEffect(() => {
    fetchSuppliers();
    fetchContracts();
    fetchOrderHistory();
  }, []);

  return (
    <div className="min-h-screen p-6">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <Truck className="w-6 h-6" />
          공급업체 관리
        </h1>
        <p className="text-gray-300 mt-2">공급업체 정보를 관리하고 계약을 추적하세요</p>
      </div>

      {/* 액션 버튼 */}
      <div className="flex gap-4 mb-8">
        <Button
          onClick={handleCreate}
          className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700"
        >
          <Plus className="w-4 h-4 mr-2" />
          새 공급업체 등록
        </Button>
        <Button
          onClick={fetchSuppliers}
          disabled={isLoading}
          className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700"
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
                <p className="text-gray-300 text-sm">총 공급업체</p>
                <p className="text-2xl font-bold text-white">{totalSuppliers.toLocaleString()}</p>
                <p className="text-gray-400 text-sm">전체 등록 업체</p>
              </div>
              <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
                <Truck className="w-6 h-6 text-blue-400" />
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">활성 공급업체</p>
                <p className="text-2xl font-bold text-white">{activeSuppliers.toLocaleString()}</p>
                <p className="text-gray-400 text-sm">정상 계약 업체</p>
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
                <p className="text-gray-300 text-sm">고평가 공급업체</p>
                <p className="text-2xl font-bold text-white">{highRatingSuppliers.toLocaleString()}</p>
                <p className="text-gray-400 text-sm">4.5점 이상</p>
              </div>
              <div className="w-12 h-12 bg-yellow-500/20 rounded-lg flex items-center justify-center">
                <Star className="w-6 h-6 text-yellow-400" />
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">총 계약 금액</p>
                <p className="text-2xl font-bold text-white">₩{totalContractValue.toLocaleString()}</p>
                <p className="text-gray-400 text-sm">연간 계약 총액</p>
              </div>
              <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
                <DollarSign className="w-6 h-6 text-green-400" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 필터 및 검색 */}
      <Card className="bg-white/10 backdrop-blur-sm border border-white/20 mb-8">
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="공급업체명, 회사명, 담당자 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 bg-white/10 border-white/20 text-white placeholder-gray-400"
              />
            </div>
            
            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger className="bg-white/10 border-white/20 text-white">
                <SelectValue placeholder="카테고리" />
              </SelectTrigger>
              <SelectContent className="bg-white/10 border-white/20">
                <SelectItem value="all">전체 카테고리</SelectItem>
                <SelectItem value="식재료">식재료</SelectItem>
                <SelectItem value="음료">음료</SelectItem>
                <SelectItem value="포장재">포장재</SelectItem>
                <SelectItem value="장비">장비</SelectItem>
                <SelectItem value="서비스">서비스</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={selectedStatus} onValueChange={setSelectedStatus}>
              <SelectTrigger className="bg-white/10 border-white/20 text-white">
                <SelectValue placeholder="상태" />
              </SelectTrigger>
              <SelectContent className="bg-white/10 border-white/20">
                <SelectItem value="all">전체 상태</SelectItem>
                <SelectItem value="active">활성</SelectItem>
                <SelectItem value="inactive">비활성</SelectItem>
                <SelectItem value="suspended">정지</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={selectedRating} onValueChange={setSelectedRating}>
              <SelectTrigger className="bg-white/10 border-white/20 text-white">
                <SelectValue placeholder="평점" />
              </SelectTrigger>
              <SelectContent className="bg-white/10 border-white/20">
                <SelectItem value="all">전체 평점</SelectItem>
                <SelectItem value="high">높음 (4.5+)</SelectItem>
                <SelectItem value="medium">보통 (3.5-4.4)</SelectItem>
                <SelectItem value="low">낮음 (3.5 미만)</SelectItem>
              </SelectContent>
            </Select>
            
            <Button
              variant="outline"
              onClick={() => {
                setSearchTerm('');
                setSelectedCategory('all');
                setSelectedStatus('all');
                setSelectedRating('all');
              }}
              className="border-white/20 text-white hover:bg-white/10"
            >
              <Filter className="w-4 h-4 mr-2" />
              필터 초기화
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 공급업체 목록 */}
      <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
        <CardHeader>
          <CardTitle className="text-white">공급업체 목록</CardTitle>
          <CardDescription className="text-gray-300">
            총 {filteredSuppliers.length}개의 공급업체가 있습니다
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredSuppliers.map((supplier) => (
              <div
                key={supplier.id}
                className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:bg-white/10 transition-all duration-300"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-4 mb-3">
                      <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                        <Building2 className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-white">{supplier.name}</h3>
                        <p className="text-gray-400">{supplier.company_name}</p>
                        <p className="text-gray-400 text-sm">{supplier.contact_person} • {supplier.category}</p>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                      <div>
                        <p className="text-gray-300 text-sm">총 주문</p>
                        <p className="text-white font-medium">{supplier.total_orders}건</p>
                      </div>
                      <div>
                        <p className="text-gray-300 text-sm">총 매출</p>
                        <p className="text-white font-medium">₩{supplier.total_amount.toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="text-gray-300 text-sm">평균 배송</p>
                        <p className="text-white font-medium">{supplier.average_delivery_time}일</p>
                      </div>
                      <div>
                        <p className="text-gray-300 text-sm">계약 기간</p>
                        <p className="text-white font-medium">
                          {new Date(supplier.contract_start_date).toLocaleDateString()} ~ {new Date(supplier.contract_end_date).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    
                    {supplier.notes && (
                      <div className="bg-white/5 rounded-lg p-3">
                        <p className="text-gray-300 text-sm mb-1">메모</p>
                        <p className="text-white text-sm">{supplier.notes}</p>
                      </div>
                    )}
                  </div>
                  
                  <div className="flex flex-col gap-2 ml-4">
                    <Badge className={getStatusColor(supplier.status)}>
                      {supplier.status === 'active' && '활성'}
                      {supplier.status === 'inactive' && '비활성'}
                      {supplier.status === 'suspended' && '정지'}
                    </Badge>
                    
                    <div className={`flex items-center ${getRatingColor(supplier.rating)}`}>
                      <Star className="w-4 h-4 fill-current" />
                      <span className="ml-1">{supplier.rating}</span>
                    </div>
                    
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleView(supplier)}
                        className="border-white/20 text-white hover:bg-white/10"
                      >
                        <Eye className="w-4 h-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleEdit(supplier)}
                        className="border-white/20 text-white hover:bg-white/10"
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button
                        size="sm"
                        onClick={() => handleDelete(supplier)}
                        className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                    
                    <div className="flex gap-1">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleViewContracts(supplier)}
                        className="border-white/20 text-white hover:bg-white/10"
                      >
                        <FileText className="w-4 h-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleViewHistory(supplier)}
                        className="border-white/20 text-white hover:bg-white/10"
                      >
                        <Package className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 공급업체 추가/수정 다이얼로그 */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="bg-white/10 backdrop-blur-sm border border-white/20 max-w-2xl">
          <DialogHeader>
            <DialogTitle className="text-white">
              {editingSupplier ? '공급업체 정보 수정' : '새 공급업체 등록'}
            </DialogTitle>
          </DialogHeader>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label className="text-gray-300">공급업체명 *</Label>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="mt-1 bg-white/10 border-white/20 text-white"
                  placeholder="공급업체명을 입력하세요"
                />
              </div>
              
              <div>
                <Label className="text-gray-300">회사명 *</Label>
                <Input
                  value={formData.company_name}
                  onChange={(e) => setFormData({...formData, company_name: e.target.value})}
                  className="mt-1 bg-white/10 border-white/20 text-white"
                  placeholder="회사명을 입력하세요"
                />
              </div>
              
              <div>
                <Label className="text-gray-300">담당자 *</Label>
                <Input
                  value={formData.contact_person}
                  onChange={(e) => setFormData({...formData, contact_person: e.target.value})}
                  className="mt-1 bg-white/10 border-white/20 text-white"
                  placeholder="담당자명을 입력하세요"
                />
              </div>
              
              <div>
                <Label className="text-gray-300">이메일</Label>
                <Input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  className="mt-1 bg-white/10 border-white/20 text-white"
                  placeholder="이메일을 입력하세요"
                />
              </div>
              
              <div>
                <Label className="text-gray-300">전화번호</Label>
                <Input
                  value={formData.phone}
                  onChange={(e) => setFormData({...formData, phone: e.target.value})}
                  className="mt-1 bg-white/10 border-white/20 text-white"
                  placeholder="전화번호를 입력하세요"
                />
              </div>
              
              <div>
                <Label className="text-gray-300">사업자번호</Label>
                <Input
                  value={formData.business_number}
                  onChange={(e) => setFormData({...formData, business_number: e.target.value})}
                  className="mt-1 bg-white/10 border-white/20 text-white"
                  placeholder="사업자번호를 입력하세요"
                />
              </div>
              
              <div>
                <Label className="text-gray-300">카테고리</Label>
                <Select value={formData.category} onValueChange={(value) => setFormData({...formData, category: value})}>
                  <SelectTrigger className="mt-1 bg-white/10 border-white/20 text-white">
                    <SelectValue placeholder="카테고리를 선택하세요" />
                  </SelectTrigger>
                  <SelectContent className="bg-white/10 border-white/20">
                    <SelectItem value="식재료">식재료</SelectItem>
                    <SelectItem value="음료">음료</SelectItem>
                    <SelectItem value="포장재">포장재</SelectItem>
                    <SelectItem value="장비">장비</SelectItem>
                    <SelectItem value="서비스">서비스</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label className="text-gray-300">계약 시작일</Label>
                <Input
                  type="date"
                  value={formData.contract_start_date}
                  onChange={(e) => setFormData({...formData, contract_start_date: e.target.value})}
                  className="mt-1 bg-white/10 border-white/20 text-white"
                />
              </div>
              
              <div>
                <Label className="text-gray-300">계약 종료일</Label>
                <Input
                  type="date"
                  value={formData.contract_end_date}
                  onChange={(e) => setFormData({...formData, contract_end_date: e.target.value})}
                  className="mt-1 bg-white/10 border-white/20 text-white"
                />
              </div>
              
              <div>
                <Label className="text-gray-300">결제 조건</Label>
                <Input
                  value={formData.payment_terms}
                  onChange={(e) => setFormData({...formData, payment_terms: e.target.value})}
                  className="mt-1 bg-white/10 border-white/20 text-white"
                  placeholder="결제 조건을 입력하세요"
                />
              </div>
              
              <div>
                <Label className="text-gray-300">배송 조건</Label>
                <Input
                  value={formData.delivery_terms}
                  onChange={(e) => setFormData({...formData, delivery_terms: e.target.value})}
                  className="mt-1 bg-white/10 border-white/20 text-white"
                  placeholder="배송 조건을 입력하세요"
                />
              </div>
            </div>
            
            <div>
              <Label className="text-gray-300">주소</Label>
              <Input
                value={formData.address}
                onChange={(e) => setFormData({...formData, address: e.target.value})}
                className="mt-1 bg-white/10 border-white/20 text-white"
                placeholder="주소를 입력하세요"
              />
            </div>
            
            <div>
              <Label className="text-gray-300">메모</Label>
              <Textarea
                value={formData.notes}
                onChange={(e) => setFormData({...formData, notes: e.target.value})}
                className="mt-1 bg-white/10 border-white/20 text-white"
                placeholder="공급업체에 대한 메모를 입력하세요"
                rows={3}
              />
            </div>
            
            <div className="flex gap-2">
              <Button type="submit" className="flex-1 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700">
                {editingSupplier ? '수정' : '등록'}
              </Button>
              <Button type="button" variant="outline" onClick={() => setIsCreateDialogOpen(false)} className="border-white/20 text-white hover:bg-white/10">
                취소
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* 공급업체 상세 보기 다이얼로그 */}
      <Dialog open={!!viewingSupplier} onOpenChange={() => setViewingSupplier(null)}>
        <DialogContent className="bg-white/10 backdrop-blur-sm border border-white/20 max-w-2xl">
          <DialogHeader>
            <DialogTitle className="text-white">공급업체 상세 정보</DialogTitle>
          </DialogHeader>
          
          {viewingSupplier && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label className="text-gray-300 text-sm">공급업체명</Label>
                  <p className="text-white font-medium">{viewingSupplier.name}</p>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">회사명</Label>
                  <p className="text-white font-medium">{viewingSupplier.company_name}</p>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">담당자</Label>
                  <p className="text-white font-medium">{viewingSupplier.contact_person}</p>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">이메일</Label>
                  <p className="text-white font-medium">{viewingSupplier.email}</p>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">전화번호</Label>
                  <p className="text-white font-medium">{viewingSupplier.phone}</p>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">사업자번호</Label>
                  <p className="text-white font-medium">{viewingSupplier.business_number}</p>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">카테고리</Label>
                  <p className="text-white font-medium">{viewingSupplier.category}</p>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">상태</Label>
                  <Badge className={getStatusColor(viewingSupplier.status)}>
                    {viewingSupplier.status === 'active' && '활성'}
                    {viewingSupplier.status === 'inactive' && '비활성'}
                    {viewingSupplier.status === 'suspended' && '정지'}
                  </Badge>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">평점</Label>
                  <div className={`flex items-center ${getRatingColor(viewingSupplier.rating)}`}>
                    <Star className="w-4 h-4 fill-current" />
                    <span className="ml-1">{viewingSupplier.rating}</span>
                  </div>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">총 주문</Label>
                  <p className="text-white font-medium">{viewingSupplier.total_orders}건</p>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">총 매출</Label>
                  <p className="text-white font-medium">₩{viewingSupplier.total_amount.toLocaleString()}</p>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">평균 배송 시간</Label>
                  <p className="text-white font-medium">{viewingSupplier.average_delivery_time}일</p>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">품질 평점</Label>
                  <p className="text-white font-medium">{viewingSupplier.quality_rating}</p>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">계약 시작일</Label>
                  <p className="text-white font-medium">{new Date(viewingSupplier.contract_start_date).toLocaleDateString()}</p>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">계약 종료일</Label>
                  <p className="text-white font-medium">{new Date(viewingSupplier.contract_end_date).toLocaleDateString()}</p>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">결제 조건</Label>
                  <p className="text-white font-medium">{viewingSupplier.payment_terms}</p>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">배송 조건</Label>
                  <p className="text-white font-medium">{viewingSupplier.delivery_terms}</p>
                </div>
              </div>
              
              <div>
                <Label className="text-gray-300 text-sm">주소</Label>
                <p className="text-white">{viewingSupplier.address}</p>
              </div>
              
              {viewingSupplier.notes && (
                <div>
                  <Label className="text-gray-300 text-sm">메모</Label>
                  <p className="text-white">{viewingSupplier.notes}</p>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
} 
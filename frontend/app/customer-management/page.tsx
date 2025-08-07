'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../src/components/ui/card';
import { Button } from '../../src/components/ui/button';
import { Input } from '../../src/components/ui/input';
import { Badge } from '../../src/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '../../src/components/ui/dialog';
import { Label } from '../../src/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../src/components/ui/select';
import { Textarea } from '../../src/components/ui/textarea';
import { apiClient } from '../../src/lib/api-client';
import { useLoadingState } from '../../src/hooks/useLoadingState';
import { useErrorHandler } from '../../src/hooks/useErrorHandler';
import { toast } from 'sonner';
import { Users, Plus, Search, Filter, Edit, Trash2, Eye, Phone, Mail, MapPin, Calendar, Star, TrendingUp, ShoppingBag, RefreshCw } from 'lucide-react';

interface Customer {
  id: number;
  name: string;
  email: string;
  phone: string;
  address: string;
  birth_date?: string;
  gender: 'male' | 'female' | 'other';
  membership_level: 'bronze' | 'silver' | 'gold' | 'platinum';
  total_purchases: number;
  total_spent: number;
  last_visit?: string;
  notes?: string;
  status: 'active' | 'inactive' | 'vip';
  created_at: string;
  updated_at: string;
}

interface CustomerFormData {
  name: string;
  email: string;
  phone: string;
  address: string;
  birth_date: string;
  gender: 'male' | 'female' | 'other';
  membership_level: 'bronze' | 'silver' | 'gold' | 'platinum';
  notes: string;
}

interface StoreType {
  id: number;
  name: string;
  address: string;
}

export default function CustomerManagement() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [stores, setStores] = useState<StoreType[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStore, setSelectedStore] = useState<string>('all');
  const [selectedMembership, setSelectedMembership] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [selectedGender, setSelectedGender] = useState<string>('all');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState<Customer | null>(null);
  const [viewingCustomer, setViewingCustomer] = useState<Customer | null>(null);
  
  const [formData, setFormData] = useState<CustomerFormData>({
    name: '',
    email: '',
    phone: '',
    address: '',
    birth_date: '',
    gender: 'other',
    membership_level: 'bronze',
    notes: '',
  });

  const { isLoading, setLoading } = useLoadingState();
  const { handleError } = useErrorHandler();

  // 고객 목록 조회
  const fetchCustomers = async () => {
    try {
      // 임시로 샘플 데이터 사용
      const sampleCustomers: Customer[] = [
        {
          id: 1,
          name: '김철수',
          email: 'kim@example.com',
          phone: '010-1234-5678',
          address: '서울시 강남구',
          birth_date: '1990-01-15',
          gender: 'male',
          membership_level: 'gold',
          total_purchases: 45,
          total_spent: 1250000,
          last_visit: '2024-01-15T10:30:00Z',
          notes: 'VIP 고객, 커피 애호가',
          status: 'vip',
          created_at: '2023-01-01T00:00:00Z',
          updated_at: '2024-01-15T00:00:00Z'
        },
        {
          id: 2,
          name: '이영희',
          email: 'lee@example.com',
          phone: '010-2345-6789',
          address: '서울시 마포구',
          birth_date: '1992-05-20',
          gender: 'female',
          membership_level: 'silver',
          total_purchases: 23,
          total_spent: 680000,
          last_visit: '2024-01-10T14:20:00Z',
          notes: '티 라떼 선호',
          status: 'active',
          created_at: '2023-03-15T00:00:00Z',
          updated_at: '2024-01-10T00:00:00Z'
        },
        {
          id: 3,
          name: '박민수',
          email: 'park@example.com',
          phone: '010-3456-7890',
          address: '서울시 서초구',
          birth_date: '1988-12-03',
          gender: 'male',
          membership_level: 'bronze',
          total_purchases: 8,
          total_spent: 120000,
          last_visit: '2024-01-05T16:45:00Z',
          notes: '새로운 고객',
          status: 'active',
          created_at: '2023-12-01T00:00:00Z',
          updated_at: '2024-01-05T00:00:00Z'
        },
        {
          id: 4,
          name: '최지영',
          email: 'choi@example.com',
          phone: '010-4567-8901',
          address: '서울시 송파구',
          birth_date: '1995-08-12',
          gender: 'female',
          membership_level: 'platinum',
          total_purchases: 89,
          total_spent: 3200000,
          last_visit: '2024-01-12T11:15:00Z',
          notes: '최고 VIP 고객, 매일 방문',
          status: 'vip',
          created_at: '2022-06-01T00:00:00Z',
          updated_at: '2024-01-12T00:00:00Z'
        }
      ];
      
      setCustomers(sampleCustomers);
    } catch (error) {
      handleError(error as Error);
    }
  };

  // 매장 목록 조회
  const fetchStores = async () => {
    try {
      const sampleStores: StoreType[] = [
        { id: 1, name: '강남점', address: '서울 강남구' },
        { id: 2, name: '홍대점', address: '서울 마포구' },
        { id: 3, name: '명동점', address: '서울 중구' }
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
      email: '',
      phone: '',
      address: '',
      birth_date: '',
      gender: 'other',
      membership_level: 'bronze',
      notes: '',
    });
    setEditingCustomer(null);
  };

  // 고객 추가/수정
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name || !formData.email || !formData.phone) {
      toast.error('필수 항목을 입력해주세요.');
      return;
    }

    try {
      setLoading(true);
      
      if (editingCustomer) {
        // 수정
        const updatedCustomer = {
          ...editingCustomer,
          ...formData,
          updated_at: new Date().toISOString()
        };
        
        setCustomers(prev => prev.map(customer => 
          customer.id === editingCustomer.id ? updatedCustomer : customer
        ));
        
        toast.success('고객 정보가 수정되었습니다.');
      } else {
        // 추가
        const newCustomer: Customer = {
          id: Date.now(),
          ...formData,
          total_purchases: 0,
          total_spent: 0,
          status: 'active',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };
        
        setCustomers(prev => [...prev, newCustomer]);
        toast.success('고객이 추가되었습니다.');
      }
      
      setIsCreateDialogOpen(false);
      resetForm();
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 고객 삭제
  const handleDelete = async (customer: Customer) => {
    try {
      setLoading(true);
      setCustomers(prev => prev.filter(c => c.id !== customer.id));
      toast.success('고객이 삭제되었습니다.');
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 편집 모드 시작
  const handleEdit = (customer: Customer) => {
    setEditingCustomer(customer);
    setFormData({
      name: customer.name,
      email: customer.email,
      phone: customer.phone,
      address: customer.address,
      birth_date: customer.birth_date || '',
      gender: customer.gender,
      membership_level: customer.membership_level,
      notes: customer.notes || '',
    });
    setIsCreateDialogOpen(true);
  };

  // 상세 보기
  const handleView = (customer: Customer) => {
    setViewingCustomer(customer);
  };

  // 새 고객 생성 모드 시작
  const handleCreate = () => {
    setEditingCustomer(null);
    resetForm();
    setIsCreateDialogOpen(true);
  };

  // 멤버십 레벨별 색상
  const getMembershipColor = (level: string) => {
    switch (level) {
      case 'bronze': return 'bg-orange-500/20 text-orange-400';
      case 'silver': return 'bg-gray-500/20 text-gray-400';
      case 'gold': return 'bg-yellow-500/20 text-yellow-400';
      case 'platinum': return 'bg-purple-500/20 text-purple-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  // 상태별 색상
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500/20 text-green-400';
      case 'inactive': return 'bg-red-500/20 text-red-400';
      case 'vip': return 'bg-purple-500/20 text-purple-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  // 필터링된 고객 목록
  const filteredCustomers = customers.filter(customer => {
    const matchesSearch = searchTerm === '' || 
      customer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      customer.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      customer.phone.includes(searchTerm);
    
    const matchesMembership = selectedMembership === 'all' || customer.membership_level === selectedMembership;
    const matchesStatus = selectedStatus === 'all' || customer.status === selectedStatus;
    const matchesGender = selectedGender === 'all' || customer.gender === selectedGender;
    
    return matchesSearch && matchesMembership && matchesStatus && matchesGender;
  });

  // 통계 계산
  const totalCustomers = customers.length;
  const activeCustomers = customers.filter(c => c.status === 'active').length;
  const vipCustomers = customers.filter(c => c.status === 'vip').length;
  const totalRevenue = customers.reduce((sum, c) => sum + c.total_spent, 0);

  useEffect(() => {
    fetchCustomers();
    fetchStores();
  }, []);

  return (
    <div className="min-h-screen p-6">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <Users className="w-6 h-6" />
          고객 관리
        </h1>
        <p className="text-gray-300 mt-2">고객 정보를 관리하고 고객 관계를 개선하세요</p>
      </div>

      {/* 액션 버튼 */}
      <div className="flex gap-4 mb-8">
        <Button
          onClick={handleCreate}
          className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700"
        >
          <Plus className="w-4 h-4 mr-2" />
          새 고객 등록
        </Button>
        <Button
          onClick={fetchCustomers}
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
                <p className="text-gray-300 text-sm">총 고객 수</p>
                <p className="text-2xl font-bold text-white">{totalCustomers.toLocaleString()}</p>
                <p className="text-gray-400 text-sm">전체 등록 고객</p>
              </div>
              <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
                <Users className="w-6 h-6 text-blue-400" />
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">활성 고객</p>
                <p className="text-2xl font-bold text-white">{activeCustomers.toLocaleString()}</p>
                <p className="text-gray-400 text-sm">정상 이용 고객</p>
              </div>
              <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-green-400" />
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">VIP 고객</p>
                <p className="text-2xl font-bold text-white">{vipCustomers.toLocaleString()}</p>
                <p className="text-gray-400 text-sm">프리미엄 고객</p>
              </div>
              <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center">
                <Star className="w-6 h-6 text-purple-400" />
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">총 매출</p>
                <p className="text-2xl font-bold text-white">₩{totalRevenue.toLocaleString()}</p>
                <p className="text-gray-400 text-sm">고객 총 구매액</p>
              </div>
              <div className="w-12 h-12 bg-orange-500/20 rounded-lg flex items-center justify-center">
                <ShoppingBag className="w-6 h-6 text-orange-400" />
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
                placeholder="고객명, 이메일, 전화번호 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 bg-white/10 border-white/20 text-white placeholder-gray-400"
              />
            </div>
            
            <Select value={selectedMembership} onValueChange={setSelectedMembership}>
              <SelectTrigger className="bg-white/10 border-white/20 text-white">
                <SelectValue placeholder="멤버십 레벨" />
              </SelectTrigger>
              <SelectContent className="bg-white/10 border-white/20">
                <SelectItem value="all">전체 레벨</SelectItem>
                <SelectItem value="bronze">브론즈</SelectItem>
                <SelectItem value="silver">실버</SelectItem>
                <SelectItem value="gold">골드</SelectItem>
                <SelectItem value="platinum">플래티넘</SelectItem>
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
                <SelectItem value="vip">VIP</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={selectedGender} onValueChange={setSelectedGender}>
              <SelectTrigger className="bg-white/10 border-white/20 text-white">
                <SelectValue placeholder="성별" />
              </SelectTrigger>
              <SelectContent className="bg-white/10 border-white/20">
                <SelectItem value="all">전체</SelectItem>
                <SelectItem value="male">남성</SelectItem>
                <SelectItem value="female">여성</SelectItem>
                <SelectItem value="other">기타</SelectItem>
              </SelectContent>
            </Select>
            
            <Button 
              variant="outline" 
              onClick={() => {
                setSearchTerm('');
                setSelectedMembership('all');
                setSelectedStatus('all');
                setSelectedGender('all');
              }}
              className="border-white/20 text-white hover:bg-white/10"
            >
              <Filter className="h-4 w-4 mr-2" />
              필터 초기화
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 고객 목록 */}
      <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
        <CardHeader>
          <CardTitle className="text-white">고객 목록</CardTitle>
          <CardDescription className="text-gray-300">
            총 {filteredCustomers.length}명의 고객이 있습니다
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredCustomers.map((customer) => (
              <div
                key={customer.id}
                className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:bg-white/10 transition-all duration-300"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-4 mb-3">
                      <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                        <Users className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-white">{customer.name}</h3>
                        <p className="text-gray-400">{customer.email}</p>
                        <p className="text-gray-400 text-sm">{customer.phone} • {customer.address}</p>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                      <div>
                        <p className="text-gray-300 text-sm">총 구매</p>
                        <p className="text-white font-medium">{customer.total_purchases}회</p>
                      </div>
                      <div>
                        <p className="text-gray-300 text-sm">총 구매액</p>
                        <p className="text-white font-medium">₩{customer.total_spent.toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="text-gray-300 text-sm">마지막 방문</p>
                        <p className="text-white font-medium">
                          {customer.last_visit ? new Date(customer.last_visit).toLocaleDateString() : '없음'}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-300 text-sm">생년월일</p>
                        <p className="text-white font-medium">
                          {customer.birth_date ? new Date(customer.birth_date).toLocaleDateString() : '없음'}
                        </p>
                      </div>
                    </div>
                    
                    {customer.notes && (
                      <div className="bg-white/5 rounded-lg p-3">
                        <p className="text-gray-300 text-sm mb-1">메모</p>
                        <p className="text-white text-sm">{customer.notes}</p>
                      </div>
                    )}
                  </div>
                  
                  <div className="flex flex-col gap-2 ml-4">
                    <Badge className={getMembershipColor(customer.membership_level)}>
                      {customer.membership_level === 'bronze' && '브론즈'}
                      {customer.membership_level === 'silver' && '실버'}
                      {customer.membership_level === 'gold' && '골드'}
                      {customer.membership_level === 'platinum' && '플래티넘'}
                    </Badge>
                    
                    <Badge className={getStatusColor(customer.status)}>
                      {customer.status === 'active' && '활성'}
                      {customer.status === 'inactive' && '비활성'}
                      {customer.status === 'vip' && 'VIP'}
                    </Badge>
                    
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleView(customer)}
                        className="border-white/20 text-white hover:bg-white/10"
                      >
                        <Eye className="w-4 h-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleEdit(customer)}
                        className="border-white/20 text-white hover:bg-white/10"
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button
                        size="sm"
                        onClick={() => handleDelete(customer)}
                        className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 고객 추가/수정 다이얼로그 */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="bg-white/10 backdrop-blur-sm border border-white/20 max-w-2xl">
          <DialogHeader>
            <DialogTitle className="text-white">
              {editingCustomer ? '고객 정보 수정' : '새 고객 등록'}
            </DialogTitle>
          </DialogHeader>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label className="text-gray-300">이름 *</Label>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="mt-1 bg-white/10 border-white/20 text-white"
                  placeholder="고객 이름을 입력하세요"
                />
              </div>
              
              <div>
                <Label className="text-gray-300">이메일 *</Label>
                <Input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  className="mt-1 bg-white/10 border-white/20 text-white"
                  placeholder="이메일을 입력하세요"
                />
              </div>
              
              <div>
                <Label className="text-gray-300">전화번호 *</Label>
                <Input
                  value={formData.phone}
                  onChange={(e) => setFormData({...formData, phone: e.target.value})}
                  className="mt-1 bg-white/10 border-white/20 text-white"
                  placeholder="전화번호를 입력하세요"
                />
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
                <Label className="text-gray-300">생년월일</Label>
                <Input
                  type="date"
                  value={formData.birth_date}
                  onChange={(e) => setFormData({...formData, birth_date: e.target.value})}
                  className="mt-1 bg-white/10 border-white/20 text-white"
                />
              </div>
              
              <div>
                <Label className="text-gray-300">성별</Label>
                <Select value={formData.gender} onValueChange={(value: any) => setFormData({...formData, gender: value})}>
                  <SelectTrigger className="mt-1 bg-white/10 border-white/20 text-white">
                    <SelectValue placeholder="성별을 선택하세요" />
                  </SelectTrigger>
                  <SelectContent className="bg-white/10 border-white/20">
                    <SelectItem value="male">남성</SelectItem>
                    <SelectItem value="female">여성</SelectItem>
                    <SelectItem value="other">기타</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label className="text-gray-300">멤버십 레벨</Label>
                <Select value={formData.membership_level} onValueChange={(value: any) => setFormData({...formData, membership_level: value})}>
                  <SelectTrigger className="mt-1 bg-white/10 border-white/20 text-white">
                    <SelectValue placeholder="멤버십 레벨을 선택하세요" />
                  </SelectTrigger>
                  <SelectContent className="bg-white/10 border-white/20">
                    <SelectItem value="bronze">브론즈</SelectItem>
                    <SelectItem value="silver">실버</SelectItem>
                    <SelectItem value="gold">골드</SelectItem>
                    <SelectItem value="platinum">플래티넘</SelectItem>
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
                placeholder="고객에 대한 메모를 입력하세요"
                rows={3}
              />
            </div>
            
            <div className="flex gap-2">
              <Button type="submit" className="flex-1 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700">
                {editingCustomer ? '수정' : '등록'}
              </Button>
              <Button type="button" variant="outline" onClick={() => setIsCreateDialogOpen(false)} className="border-white/20 text-white hover:bg-white/10">
                취소
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* 고객 상세 보기 다이얼로그 */}
      <Dialog open={!!viewingCustomer} onOpenChange={() => setViewingCustomer(null)}>
        <DialogContent className="bg-white/10 backdrop-blur-sm border border-white/20 max-w-2xl">
          <DialogHeader>
            <DialogTitle className="text-white">고객 상세 정보</DialogTitle>
          </DialogHeader>
          
          {viewingCustomer && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label className="text-gray-300 text-sm">이름</Label>
                  <p className="text-white font-medium">{viewingCustomer.name}</p>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">이메일</Label>
                  <p className="text-white font-medium">{viewingCustomer.email}</p>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">전화번호</Label>
                  <p className="text-white font-medium">{viewingCustomer.phone}</p>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">주소</Label>
                  <p className="text-white font-medium">{viewingCustomer.address}</p>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">생년월일</Label>
                  <p className="text-white font-medium">
                    {viewingCustomer.birth_date ? new Date(viewingCustomer.birth_date).toLocaleDateString() : '없음'}
                  </p>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">성별</Label>
                  <p className="text-white font-medium">
                    {viewingCustomer.gender === 'male' && '남성'}
                    {viewingCustomer.gender === 'female' && '여성'}
                    {viewingCustomer.gender === 'other' && '기타'}
                  </p>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">멤버십 레벨</Label>
                  <Badge className={getMembershipColor(viewingCustomer.membership_level)}>
                    {viewingCustomer.membership_level === 'bronze' && '브론즈'}
                    {viewingCustomer.membership_level === 'silver' && '실버'}
                    {viewingCustomer.membership_level === 'gold' && '골드'}
                    {viewingCustomer.membership_level === 'platinum' && '플래티넘'}
                  </Badge>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">상태</Label>
                  <Badge className={getStatusColor(viewingCustomer.status)}>
                    {viewingCustomer.status === 'active' && '활성'}
                    {viewingCustomer.status === 'inactive' && '비활성'}
                    {viewingCustomer.status === 'vip' && 'VIP'}
                  </Badge>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">총 구매</Label>
                  <p className="text-white font-medium">{viewingCustomer.total_purchases}회</p>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">총 구매액</Label>
                  <p className="text-white font-medium">₩{viewingCustomer.total_spent.toLocaleString()}</p>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">마지막 방문</Label>
                  <p className="text-white font-medium">
                    {viewingCustomer.last_visit ? new Date(viewingCustomer.last_visit).toLocaleString() : '없음'}
                  </p>
                </div>
              </div>
              
              {viewingCustomer.notes && (
                <div>
                  <Label className="text-gray-300 text-sm">메모</Label>
                  <p className="text-white">{viewingCustomer.notes}</p>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
} 
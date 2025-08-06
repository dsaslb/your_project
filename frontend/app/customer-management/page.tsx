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
import { Users, Plus, Search, Filter, Edit, Trash2, Eye, Phone, Mail, MapPin, Calendar, Star, TrendingUp, ShoppingBag } from 'lucide-react';

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

  const { isLoading, setLoading, withLoading } = useLoadingState();
  const { handleError } = useErrorHandler();

  // 고객 목록 조회
  const fetchCustomers = async () => {
    try {
      const response = await apiClient.get('/api/customers');
      if (response.success && response.data) {
        setCustomers(response.data);
      }
    } catch (error) {
      handleError(error as Error);
    }
  };

  // 매장 목록 조회
  const fetchStores = async () => {
    try {
      const response = await apiClient.get('/api/stores');
      if (response.success && response.data) {
        setStores(response.data);
      }
    } catch (error) {
      handleError(error as Error);
    }
  };

  // 초기 데이터 로드
  useEffect(() => {
    fetchCustomers();
    fetchStores();
  }, []);

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
  };

  // 고객 생성/수정 제출
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name || !formData.email || !formData.phone) {
      toast.error('필수 정보를 입력해주세요.');
      return;
    }

    try {
      setLoading(true);
      
      if (editingCustomer) {
        // 고객 정보 수정
        const response = await apiClient.put(`/api/customers/${editingCustomer.id}`, formData);
        if (response.success) {
          toast.success('고객 정보가 성공적으로 수정되었습니다.');
          setIsCreateDialogOpen(false);
          setEditingCustomer(null);
          resetForm();
          fetchCustomers();
        }
      } else {
        // 새 고객 생성
        const response = await apiClient.post('/api/customers', formData);
        if (response.success) {
          toast.success('고객이 성공적으로 등록되었습니다.');
          setIsCreateDialogOpen(false);
          resetForm();
          fetchCustomers();
        }
      }
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 고객 삭제
  const handleDelete = async (customer: Customer) => {
    if (!confirm(`정말로 ${customer.name} 고객을 삭제하시겠습니까?`)) {
      return;
    }

    try {
      setLoading(true);
      const response = await apiClient.delete(`/api/customers/${customer.id}`);
      if (response.success) {
        toast.success('고객이 성공적으로 삭제되었습니다.');
        fetchCustomers();
      }
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 고객 수정 모드 시작
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

  // 고객 상세 보기
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
      case 'bronze': return 'bg-orange-500/20 text-orange-400 border border-orange-500/30';
      case 'silver': return 'bg-gray-500/20 text-gray-400 border border-gray-500/30';
      case 'gold': return 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30';
      case 'platinum': return 'bg-purple-500/20 text-purple-400 border border-purple-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border border-gray-500/30';
    }
  };

  // 상태별 색상
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500/20 text-green-400 border border-green-500/30';
      case 'inactive': return 'bg-red-500/20 text-red-400 border border-red-500/30';
      case 'vip': return 'bg-purple-500/20 text-purple-400 border border-purple-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border border-gray-500/30';
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

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Users className="h-8 w-8 text-blue-600" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">고객 관리</h1>
            <p className="text-gray-600">고객 정보를 관리하고 고객 관계를 개선하세요</p>
          </div>
        </div>
        <Button onClick={handleCreate} className="bg-blue-600 hover:bg-blue-700">
          <Plus className="h-4 w-4 mr-2" />
          새 고객 등록
        </Button>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <Users className="h-8 w-8 text-blue-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">총 고객 수</p>
                <p className="text-2xl font-bold text-gray-900">{totalCustomers.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <TrendingUp className="h-8 w-8 text-green-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">활성 고객</p>
                <p className="text-2xl font-bold text-gray-900">{activeCustomers.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <Star className="h-8 w-8 text-purple-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">VIP 고객</p>
                <p className="text-2xl font-bold text-gray-900">{vipCustomers.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <ShoppingBag className="h-8 w-8 text-orange-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">총 매출</p>
                <p className="text-2xl font-bold text-gray-900">₩{totalRevenue.toLocaleString()}</p>
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
                placeholder="고객명, 이메일, 전화번호 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            
            <Select value={selectedMembership} onValueChange={setSelectedMembership}>
              <SelectTrigger>
                <SelectValue placeholder="멤버십 레벨" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">전체 레벨</SelectItem>
                <SelectItem value="bronze">브론즈</SelectItem>
                <SelectItem value="silver">실버</SelectItem>
                <SelectItem value="gold">골드</SelectItem>
                <SelectItem value="platinum">플래티넘</SelectItem>
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
                <SelectItem value="vip">VIP</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={selectedGender} onValueChange={setSelectedGender}>
              <SelectTrigger>
                <SelectValue placeholder="성별" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">전체</SelectItem>
                <SelectItem value="male">남성</SelectItem>
                <SelectItem value="female">여성</SelectItem>
                <SelectItem value="other">기타</SelectItem>
              </SelectContent>
            </Select>
            
            <Button variant="outline" onClick={() => {
              setSearchTerm('');
              setSelectedMembership('all');
              setSelectedStatus('all');
              setSelectedGender('all');
            }}>
              <Filter className="h-4 w-4 mr-2" />
              필터 초기화
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 고객 목록 */}
      <Card>
        <CardHeader>
          <CardTitle>고객 목록</CardTitle>
          <CardDescription>
            총 {filteredCustomers.length}명의 고객이 있습니다
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredCustomers.map((customer) => (
              <div key={customer.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">{customer.name}</h3>
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
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                      <div className="flex items-center space-x-2">
                        <Mail className="h-4 w-4" />
                        <span>{customer.email}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Phone className="h-4 w-4" />
                        <span>{customer.phone}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <MapPin className="h-4 w-4" />
                        <span>{customer.address}</span>
                      </div>
                    </div>
                    
                    <div className="mt-2 text-sm text-gray-500">
                      <span>총 구매: {customer.total_purchases}회</span>
                      <span className="mx-2">•</span>
                      <span>총 지출: ₩{customer.total_spent.toLocaleString()}</span>
                      {customer.last_visit && (
                        <>
                          <span className="mx-2">•</span>
                          <span>마지막 방문: {new Date(customer.last_visit).toLocaleDateString('ko-KR')}</span>
                        </>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleView(customer)}
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEdit(customer)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDelete(customer)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
            
            {filteredCustomers.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                고객이 없습니다.
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* 고객 생성/수정 다이얼로그 */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              {editingCustomer ? '고객 정보 수정' : '새 고객 등록'}
            </DialogTitle>
            <DialogDescription>
              {editingCustomer ? '고객 정보를 수정하세요.' : '새로운 고객을 등록하세요.'}
            </DialogDescription>
          </DialogHeader>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="name">이름 *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
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
                <Label htmlFor="birth_date">생년월일</Label>
                <Input
                  id="birth_date"
                  type="date"
                  value={formData.birth_date}
                  onChange={(e) => setFormData({ ...formData, birth_date: e.target.value })}
                />
              </div>
              
              <div>
                <Label htmlFor="gender">성별</Label>
                <Select value={formData.gender} onValueChange={(value: 'male' | 'female' | 'other') => setFormData({ ...formData, gender: value })}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="male">남성</SelectItem>
                    <SelectItem value="female">여성</SelectItem>
                    <SelectItem value="other">기타</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label htmlFor="membership_level">멤버십 레벨</Label>
                <Select value={formData.membership_level} onValueChange={(value: 'bronze' | 'silver' | 'gold' | 'platinum') => setFormData({ ...formData, membership_level: value })}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="bronze">브론즈</SelectItem>
                    <SelectItem value="silver">실버</SelectItem>
                    <SelectItem value="gold">골드</SelectItem>
                    <SelectItem value="platinum">플래티넘</SelectItem>
                  </SelectContent>
                </Select>
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
                {isLoading ? '처리 중...' : (editingCustomer ? '수정' : '등록')}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* 고객 상세 보기 다이얼로그 */}
      <Dialog open={!!viewingCustomer} onOpenChange={() => setViewingCustomer(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>고객 상세 정보</DialogTitle>
            <DialogDescription>
              {viewingCustomer?.name} 고객의 상세 정보입니다.
            </DialogDescription>
          </DialogHeader>
          
          {viewingCustomer && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm font-medium text-gray-600">이름</Label>
                  <p className="text-lg font-semibold">{viewingCustomer.name}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">이메일</Label>
                  <p className="text-lg">{viewingCustomer.email}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">전화번호</Label>
                  <p className="text-lg">{viewingCustomer.phone}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">생년월일</Label>
                  <p className="text-lg">{viewingCustomer.birth_date ? new Date(viewingCustomer.birth_date).toLocaleDateString('ko-KR') : '미입력'}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">성별</Label>
                  <p className="text-lg">
                    {viewingCustomer.gender === 'male' && '남성'}
                    {viewingCustomer.gender === 'female' && '여성'}
                    {viewingCustomer.gender === 'other' && '기타'}
                  </p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">멤버십 레벨</Label>
                  <Badge className={getMembershipColor(viewingCustomer.membership_level)}>
                    {viewingCustomer.membership_level === 'bronze' && '브론즈'}
                    {viewingCustomer.membership_level === 'silver' && '실버'}
                    {viewingCustomer.membership_level === 'gold' && '골드'}
                    {viewingCustomer.membership_level === 'platinum' && '플래티넘'}
                  </Badge>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">상태</Label>
                  <Badge className={getStatusColor(viewingCustomer.status)}>
                    {viewingCustomer.status === 'active' && '활성'}
                    {viewingCustomer.status === 'inactive' && '비활성'}
                    {viewingCustomer.status === 'vip' && 'VIP'}
                  </Badge>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">총 구매 횟수</Label>
                  <p className="text-lg font-semibold text-blue-600">{viewingCustomer.total_purchases}회</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">총 지출 금액</Label>
                  <p className="text-lg font-semibold text-green-600">₩{viewingCustomer.total_spent.toLocaleString()}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">마지막 방문</Label>
                  <p className="text-lg">
                    {viewingCustomer.last_visit ? new Date(viewingCustomer.last_visit).toLocaleDateString('ko-KR') : '방문 기록 없음'}
                  </p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">가입일</Label>
                  <p className="text-lg">{new Date(viewingCustomer.created_at).toLocaleDateString('ko-KR')}</p>
                </div>
              </div>
              
              <div>
                <Label className="text-sm font-medium text-gray-600">주소</Label>
                <p className="text-lg">{viewingCustomer.address}</p>
              </div>
              
              {viewingCustomer.notes && (
                <div>
                  <Label className="text-sm font-medium text-gray-600">메모</Label>
                  <p className="text-lg bg-gray-50 p-3 rounded-lg">{viewingCustomer.notes}</p>
                </div>
              )}
            </div>
          )}
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setViewingCustomer(null)}>
              닫기
            </Button>
            {viewingCustomer && (
              <Button onClick={() => {
                setViewingCustomer(null);
                handleEdit(viewingCustomer);
              }}>
                수정하기
              </Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
} 
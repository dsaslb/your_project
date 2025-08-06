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
  Megaphone, 
  Plus, 
  Search, 
  Filter, 
  Edit, 
  Trash2, 
  Eye, 
  Calendar,
  Users,
  DollarSign,
  TrendingUp,
  Target,
  Gift,
  Percent,
  Clock,
  CheckCircle,
  AlertTriangle,
  Star,
  BarChart3,
  Mail,
  Smartphone,
  Globe,
  Tag
} from 'lucide-react';

interface Campaign {
  id: number;
  name: string;
  description: string;
  type: 'promotion' | 'discount' | 'event' | 'loyalty' | 'email' | 'sms' | 'social';
  status: 'draft' | 'active' | 'paused' | 'completed' | 'cancelled';
  start_date: string;
  end_date: string;
  budget: number;
  spent_amount: number;
  target_audience: string;
  target_stores: number[];
  target_categories: string[];
  discount_type: 'percentage' | 'fixed' | 'buy_one_get_one' | 'free_shipping';
  discount_value: number;
  minimum_purchase: number;
  max_uses: number;
  current_uses: number;
  conversion_rate: number;
  revenue_generated: number;
  created_at: string;
  updated_at: string;
}

interface CampaignFormData {
  name: string;
  description: string;
  type: 'promotion' | 'discount' | 'event' | 'loyalty' | 'email' | 'sms' | 'social';
  start_date: string;
  end_date: string;
  budget: number;
  target_audience: string;
  target_stores: number[];
  target_categories: string[];
  discount_type: 'percentage' | 'fixed' | 'buy_one_get_one' | 'free_shipping';
  discount_value: number;
  minimum_purchase: number;
  max_uses: number;
}

interface StoreType {
  id: number;
  name: string;
  address: string;
}

interface CustomerSegment {
  id: number;
  name: string;
  description: string;
  criteria: string;
  customer_count: number;
}

export default function MarketingManagement() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [stores, setStores] = useState<StoreType[]>([]);
  const [customerSegments, setCustomerSegments] = useState<CustomerSegment[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [selectedDateRange, setSelectedDateRange] = useState<string>('all');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isSegmentDialogOpen, setIsSegmentDialogOpen] = useState(false);
  const [editingCampaign, setEditingCampaign] = useState<Campaign | null>(null);
  const [viewingCampaign, setViewingCampaign] = useState<Campaign | null>(null);
  
  const [formData, setFormData] = useState<CampaignFormData>({
    name: '',
    description: '',
    type: 'promotion',
    start_date: '',
    end_date: '',
    budget: 0,
    target_audience: '',
    target_stores: [],
    target_categories: [],
    discount_type: 'percentage',
    discount_value: 0,
    minimum_purchase: 0,
    max_uses: 0,
  });

  const { isLoading, setLoading, withLoading } = useLoadingState();
  const { handleError } = useErrorHandler();

  // 캠페인 목록 조회
  const fetchCampaigns = async () => {
    try {
      const response = await apiClient.get('/api/campaigns');
      if (response.success && response.data) {
        setCampaigns(response.data);
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

  // 고객 세그먼트 조회
  const fetchCustomerSegments = async () => {
    try {
      const response = await apiClient.get('/api/customer-segments');
      if (response.success && response.data) {
        setCustomerSegments(response.data);
      }
    } catch (error) {
      handleError(error as Error);
    }
  };

  // 초기 데이터 로드
  useEffect(() => {
    fetchCampaigns();
    fetchStores();
    fetchCustomerSegments();
  }, []);

  // 폼 초기화
  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      type: 'promotion',
      start_date: '',
      end_date: '',
      budget: 0,
      target_audience: '',
      target_stores: [],
      target_categories: [],
      discount_type: 'percentage',
      discount_value: 0,
      minimum_purchase: 0,
      max_uses: 0,
    });
  };

  // 캠페인 생성/수정 제출
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name || !formData.description || !formData.start_date || !formData.end_date) {
      toast.error('필수 정보를 입력해주세요.');
      return;
    }

    if (new Date(formData.start_date) >= new Date(formData.end_date)) {
      toast.error('종료일은 시작일보다 늦어야 합니다.');
      return;
    }

    try {
      setLoading(true);
      
      if (editingCampaign) {
        // 캠페인 정보 수정
        const response = await apiClient.put(`/api/campaigns/${editingCampaign.id}`, formData);
        if (response.success) {
          toast.success('캠페인이 성공적으로 수정되었습니다.');
          setIsCreateDialogOpen(false);
          setEditingCampaign(null);
          resetForm();
          fetchCampaigns();
        }
      } else {
        // 새 캠페인 생성
        const response = await apiClient.post('/api/campaigns', formData);
        if (response.success) {
          toast.success('캠페인이 성공적으로 생성되었습니다.');
          setIsCreateDialogOpen(false);
          resetForm();
          fetchCampaigns();
        }
      }
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 캠페인 삭제
  const handleDelete = async (campaign: Campaign) => {
    if (!confirm(`정말로 ${campaign.name} 캠페인을 삭제하시겠습니까?`)) {
      return;
    }

    try {
      setLoading(true);
      const response = await apiClient.delete(`/api/campaigns/${campaign.id}`);
      if (response.success) {
        toast.success('캠페인이 성공적으로 삭제되었습니다.');
        fetchCampaigns();
      }
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 캠페인 상태 변경
  const handleStatusChange = async (campaign: Campaign, newStatus: string) => {
    try {
      setLoading(true);
      const response = await apiClient.put(`/api/campaigns/${campaign.id}`, { status: newStatus });
      if (response.success) {
        toast.success(`캠페인 상태가 ${newStatus === 'active' ? '활성화' : '비활성화'}되었습니다.`);
        fetchCampaigns();
      }
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 캠페인 수정 모드 시작
  const handleEdit = (campaign: Campaign) => {
    setEditingCampaign(campaign);
    setFormData({
      name: campaign.name,
      description: campaign.description,
      type: campaign.type,
      start_date: campaign.start_date,
      end_date: campaign.end_date,
      budget: campaign.budget,
      target_audience: campaign.target_audience,
      target_stores: campaign.target_stores,
      target_categories: campaign.target_categories,
      discount_type: campaign.discount_type,
      discount_value: campaign.discount_value,
      minimum_purchase: campaign.minimum_purchase,
      max_uses: campaign.max_uses,
    });
    setIsCreateDialogOpen(true);
  };

  // 캠페인 상세 보기
  const handleView = (campaign: Campaign) => {
    setViewingCampaign(campaign);
  };

  // 새 캠페인 생성 모드 시작
  const handleCreate = () => {
    setEditingCampaign(null);
    resetForm();
    setIsCreateDialogOpen(true);
  };

  // 상태별 색상
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft': return 'bg-gray-500/20 text-gray-400 border border-gray-500/30';
      case 'active': return 'bg-green-500/20 text-green-400 border border-green-500/30';
      case 'paused': return 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30';
      case 'completed': return 'bg-blue-500/20 text-blue-400 border border-blue-500/30';
      case 'cancelled': return 'bg-red-500/20 text-red-400 border border-red-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border border-gray-500/30';
    }
  };

  // 타입별 색상
  const getTypeColor = (type: string) => {
    switch (type) {
      case 'promotion': return 'bg-purple-500/20 text-purple-400 border border-purple-500/30';
      case 'discount': return 'bg-green-500/20 text-green-400 border border-green-500/30';
      case 'event': return 'bg-blue-500/20 text-blue-400 border border-blue-500/30';
      case 'loyalty': return 'bg-orange-500/20 text-orange-400 border border-orange-500/30';
      case 'email': return 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30';
      case 'sms': return 'bg-pink-500/20 text-pink-400 border border-pink-500/30';
      case 'social': return 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border border-gray-500/30';
    }
  };

  // 필터링된 캠페인 목록
  const filteredCampaigns = campaigns.filter(campaign => {
    const matchesSearch = searchTerm === '' || 
      campaign.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      campaign.description.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesType = selectedType === 'all' || campaign.type === selectedType;
    const matchesStatus = selectedStatus === 'all' || campaign.status === selectedStatus;
    
    const now = new Date();
    const startDate = new Date(campaign.start_date);
    const endDate = new Date(campaign.end_date);
    
    let matchesDateRange = true;
    if (selectedDateRange === 'active') {
      matchesDateRange = now >= startDate && now <= endDate;
    } else if (selectedDateRange === 'upcoming') {
      matchesDateRange = now < startDate;
    } else if (selectedDateRange === 'past') {
      matchesDateRange = now > endDate;
    }
    
    return matchesSearch && matchesType && matchesStatus && matchesDateRange;
  });

  // 통계 계산
  const totalCampaigns = campaigns.length;
  const activeCampaigns = campaigns.filter(c => c.status === 'active').length;
  const totalBudget = campaigns.reduce((sum, c) => sum + c.budget, 0);
  const totalSpent = campaigns.reduce((sum, c) => sum + c.spent_amount, 0);
  const totalRevenue = campaigns.reduce((sum, c) => sum + c.revenue_generated, 0);

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Megaphone className="h-8 w-8 text-purple-600" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">마케팅 관리</h1>
            <p className="text-gray-600">프로모션과 캠페인을 관리하여 매출을 증대하세요</p>
          </div>
        </div>
        <Button onClick={handleCreate} className="bg-purple-600 hover:bg-purple-700">
          <Plus className="h-4 w-4 mr-2" />
          새 캠페인 생성
        </Button>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <Megaphone className="h-8 w-8 text-purple-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">총 캠페인</p>
                <p className="text-2xl font-bold text-gray-900">{totalCampaigns.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <TrendingUp className="h-8 w-8 text-green-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">활성 캠페인</p>
                <p className="text-2xl font-bold text-gray-900">{activeCampaigns.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <DollarSign className="h-8 w-8 text-blue-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">총 예산</p>
                <p className="text-2xl font-bold text-gray-900">₩{totalBudget.toLocaleString()}</p>
                <p className="text-sm text-gray-500">사용: ₩{totalSpent.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <BarChart3 className="h-8 w-8 text-orange-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">생성된 매출</p>
                <p className="text-2xl font-bold text-gray-900">₩{totalRevenue.toLocaleString()}</p>
                <p className="text-sm text-gray-500">ROI: {totalBudget > 0 ? ((totalRevenue - totalSpent) / totalSpent * 100).toFixed(1) : 0}%</p>
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
                placeholder="캠페인명, 설명 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            
            <Select value={selectedType} onValueChange={setSelectedType}>
              <SelectTrigger>
                <SelectValue placeholder="캠페인 타입" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">전체 타입</SelectItem>
                <SelectItem value="promotion">프로모션</SelectItem>
                <SelectItem value="discount">할인</SelectItem>
                <SelectItem value="event">이벤트</SelectItem>
                <SelectItem value="loyalty">로열티</SelectItem>
                <SelectItem value="email">이메일</SelectItem>
                <SelectItem value="sms">SMS</SelectItem>
                <SelectItem value="social">소셜미디어</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={selectedStatus} onValueChange={setSelectedStatus}>
              <SelectTrigger>
                <SelectValue placeholder="상태" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">전체 상태</SelectItem>
                <SelectItem value="draft">초안</SelectItem>
                <SelectItem value="active">활성</SelectItem>
                <SelectItem value="paused">일시정지</SelectItem>
                <SelectItem value="completed">완료</SelectItem>
                <SelectItem value="cancelled">취소</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={selectedDateRange} onValueChange={setSelectedDateRange}>
              <SelectTrigger>
                <SelectValue placeholder="기간" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">전체 기간</SelectItem>
                <SelectItem value="active">진행 중</SelectItem>
                <SelectItem value="upcoming">예정</SelectItem>
                <SelectItem value="past">종료</SelectItem>
              </SelectContent>
            </Select>
            
            <Button variant="outline" onClick={() => {
              setSearchTerm('');
              setSelectedType('all');
              setSelectedStatus('all');
              setSelectedDateRange('all');
            }}>
              <Filter className="h-4 w-4 mr-2" />
              필터 초기화
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 캠페인 목록 */}
      <Card>
        <CardHeader>
          <CardTitle>캠페인 목록</CardTitle>
          <CardDescription>
            총 {filteredCampaigns.length}개의 캠페인이 있습니다
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredCampaigns.map((campaign) => (
              <div key={campaign.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">{campaign.name}</h3>
                      <Badge className={getTypeColor(campaign.type)}>
                        {campaign.type === 'promotion' && '프로모션'}
                        {campaign.type === 'discount' && '할인'}
                        {campaign.type === 'event' && '이벤트'}
                        {campaign.type === 'loyalty' && '로열티'}
                        {campaign.type === 'email' && '이메일'}
                        {campaign.type === 'sms' && 'SMS'}
                        {campaign.type === 'social' && '소셜미디어'}
                      </Badge>
                      <Badge className={getStatusColor(campaign.status)}>
                        {campaign.status === 'draft' && '초안'}
                        {campaign.status === 'active' && '활성'}
                        {campaign.status === 'paused' && '일시정지'}
                        {campaign.status === 'completed' && '완료'}
                        {campaign.status === 'cancelled' && '취소'}
                      </Badge>
                    </div>
                    
                    <p className="text-sm text-gray-600 mb-2">{campaign.description}</p>
                    
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm text-gray-500">
                      <div className="flex items-center space-x-2">
                        <Calendar className="h-4 w-4" />
                        <span>{new Date(campaign.start_date).toLocaleDateString('ko-KR')} ~ {new Date(campaign.end_date).toLocaleDateString('ko-KR')}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <DollarSign className="h-4 w-4" />
                        <span>예산: ₩{campaign.budget.toLocaleString()}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Users className="h-4 w-4" />
                        <span>사용: {campaign.current_uses}/{campaign.max_uses}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <TrendingUp className="h-4 w-4" />
                        <span>전환율: {campaign.conversion_rate.toFixed(1)}%</span>
                      </div>
                    </div>
                    
                    <div className="mt-2 text-sm text-gray-500">
                      <span>할인: {campaign.discount_type === 'percentage' ? `${campaign.discount_value}%` : `₩${campaign.discount_value.toLocaleString()}`}</span>
                      {campaign.minimum_purchase > 0 && (
                        <>
                          <span className="mx-2">•</span>
                          <span>최소 구매: ₩{campaign.minimum_purchase.toLocaleString()}</span>
                        </>
                      )}
                      <span className="mx-2">•</span>
                      <span>생성 매출: ₩{campaign.revenue_generated.toLocaleString()}</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleView(campaign)}
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEdit(campaign)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    {campaign.status === 'active' && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleStatusChange(campaign, 'paused')}
                        className="text-yellow-600 hover:text-yellow-700"
                      >
                        <Clock className="h-4 w-4" />
                      </Button>
                    )}
                    {campaign.status === 'paused' && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleStatusChange(campaign, 'active')}
                        className="text-green-600 hover:text-green-700"
                      >
                        <CheckCircle className="h-4 w-4" />
                      </Button>
                    )}
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDelete(campaign)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
            
            {filteredCampaigns.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <Megaphone className="h-12 w-12 mx-auto mb-2" />
                <p>캠페인이 없습니다.</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* 캠페인 생성/수정 다이얼로그 */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {editingCampaign ? '캠페인 수정' : '새 캠페인 생성'}
            </DialogTitle>
            <DialogDescription>
              {editingCampaign ? '캠페인 정보를 수정하세요.' : '새로운 마케팅 캠페인을 생성하세요.'}
            </DialogDescription>
          </DialogHeader>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="name">캠페인명 *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </div>
              
              <div>
                <Label htmlFor="type">캠페인 타입 *</Label>
                <Select value={formData.type} onValueChange={(value: any) => setFormData({ ...formData, type: value })}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="promotion">프로모션</SelectItem>
                    <SelectItem value="discount">할인</SelectItem>
                    <SelectItem value="event">이벤트</SelectItem>
                    <SelectItem value="loyalty">로열티</SelectItem>
                    <SelectItem value="email">이메일</SelectItem>
                    <SelectItem value="sms">SMS</SelectItem>
                    <SelectItem value="social">소셜미디어</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label htmlFor="start_date">시작일 *</Label>
                <Input
                  id="start_date"
                  type="date"
                  value={formData.start_date}
                  onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                  required
                />
              </div>
              
              <div>
                <Label htmlFor="end_date">종료일 *</Label>
                <Input
                  id="end_date"
                  type="date"
                  value={formData.end_date}
                  onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                  required
                />
              </div>
              
              <div>
                <Label htmlFor="budget">예산 (원)</Label>
                <Input
                  id="budget"
                  type="number"
                  value={formData.budget}
                  onChange={(e) => setFormData({ ...formData, budget: Number(e.target.value) })}
                  min="0"
                />
              </div>
              
              <div>
                <Label htmlFor="max_uses">최대 사용 횟수</Label>
                <Input
                  id="max_uses"
                  type="number"
                  value={formData.max_uses}
                  onChange={(e) => setFormData({ ...formData, max_uses: Number(e.target.value) })}
                  min="0"
                />
              </div>
              
              <div>
                <Label htmlFor="discount_type">할인 타입</Label>
                <Select value={formData.discount_type} onValueChange={(value: any) => setFormData({ ...formData, discount_type: value })}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="percentage">퍼센트 할인</SelectItem>
                    <SelectItem value="fixed">고정 금액 할인</SelectItem>
                    <SelectItem value="buy_one_get_one">1+1</SelectItem>
                    <SelectItem value="free_shipping">무료 배송</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label htmlFor="discount_value">할인 값</Label>
                <Input
                  id="discount_value"
                  type="number"
                  value={formData.discount_value}
                  onChange={(e) => setFormData({ ...formData, discount_value: Number(e.target.value) })}
                  min="0"
                  step={formData.discount_type === 'percentage' ? '1' : '1000'}
                />
              </div>
              
              <div>
                <Label htmlFor="minimum_purchase">최소 구매 금액</Label>
                <Input
                  id="minimum_purchase"
                  type="number"
                  value={formData.minimum_purchase}
                  onChange={(e) => setFormData({ ...formData, minimum_purchase: Number(e.target.value) })}
                  min="0"
                  step="1000"
                />
              </div>
            </div>
            
            <div>
              <Label htmlFor="target_audience">타겟 고객</Label>
              <Input
                id="target_audience"
                value={formData.target_audience}
                onChange={(e) => setFormData({ ...formData, target_audience: e.target.value })}
                placeholder="예: VIP 고객, 신규 고객, 20-30대 여성"
              />
            </div>
            
            <div>
              <Label htmlFor="description">캠페인 설명 *</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
                required
              />
            </div>
            
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                취소
              </Button>
              <Button type="submit" disabled={isLoading}>
                {isLoading ? '처리 중...' : (editingCampaign ? '수정' : '생성')}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* 캠페인 상세 보기 다이얼로그 */}
      <Dialog open={!!viewingCampaign} onOpenChange={() => setViewingCampaign(null)}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>캠페인 상세 정보</DialogTitle>
            <DialogDescription>
              {viewingCampaign?.name} 캠페인의 상세 정보입니다.
            </DialogDescription>
          </DialogHeader>
          
          {viewingCampaign && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label className="text-sm font-medium text-gray-600">캠페인명</Label>
                  <p className="text-lg font-semibold">{viewingCampaign.name}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">캠페인 타입</Label>
                  <Badge className={getTypeColor(viewingCampaign.type)}>
                    {viewingCampaign.type === 'promotion' && '프로모션'}
                    {viewingCampaign.type === 'discount' && '할인'}
                    {viewingCampaign.type === 'event' && '이벤트'}
                    {viewingCampaign.type === 'loyalty' && '로열티'}
                    {viewingCampaign.type === 'email' && '이메일'}
                    {viewingCampaign.type === 'sms' && 'SMS'}
                    {viewingCampaign.type === 'social' && '소셜미디어'}
                  </Badge>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">상태</Label>
                  <Badge className={getStatusColor(viewingCampaign.status)}>
                    {viewingCampaign.status === 'draft' && '초안'}
                    {viewingCampaign.status === 'active' && '활성'}
                    {viewingCampaign.status === 'paused' && '일시정지'}
                    {viewingCampaign.status === 'completed' && '완료'}
                    {viewingCampaign.status === 'cancelled' && '취소'}
                  </Badge>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">캠페인 기간</Label>
                  <p className="text-lg">{new Date(viewingCampaign.start_date).toLocaleDateString('ko-KR')} ~ {new Date(viewingCampaign.end_date).toLocaleDateString('ko-KR')}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">예산</Label>
                  <p className="text-lg font-semibold text-blue-600">₩{viewingCampaign.budget.toLocaleString()}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">사용된 금액</Label>
                  <p className="text-lg font-semibold text-green-600">₩{viewingCampaign.spent_amount.toLocaleString()}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">할인 정보</Label>
                  <p className="text-lg">
                    {viewingCampaign.discount_type === 'percentage' && `${viewingCampaign.discount_value}% 할인`}
                    {viewingCampaign.discount_type === 'fixed' && `₩${viewingCampaign.discount_value.toLocaleString()} 할인`}
                    {viewingCampaign.discount_type === 'buy_one_get_one' && '1+1 이벤트'}
                    {viewingCampaign.discount_type === 'free_shipping' && '무료 배송'}
                  </p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">최소 구매 금액</Label>
                  <p className="text-lg">{viewingCampaign.minimum_purchase > 0 ? `₩${viewingCampaign.minimum_purchase.toLocaleString()}` : '없음'}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">사용 횟수</Label>
                  <p className="text-lg font-semibold text-purple-600">{viewingCampaign.current_uses} / {viewingCampaign.max_uses}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">전환율</Label>
                  <p className="text-lg font-semibold text-orange-600">{viewingCampaign.conversion_rate.toFixed(1)}%</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">생성된 매출</Label>
                  <p className="text-lg font-semibold text-green-600">₩{viewingCampaign.revenue_generated.toLocaleString()}</p>
                </div>
              </div>
              
              <div>
                <Label className="text-sm font-medium text-gray-600">타겟 고객</Label>
                <p className="text-lg">{viewingCampaign.target_audience}</p>
              </div>
              
              <div>
                <Label className="text-sm font-medium text-gray-600">캠페인 설명</Label>
                <p className="text-lg bg-gray-50 p-3 rounded-lg">{viewingCampaign.description}</p>
              </div>
            </div>
          )}
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setViewingCampaign(null)}>
              닫기
            </Button>
            {viewingCampaign && (
              <Button onClick={() => {
                setViewingCampaign(null);
                handleEdit(viewingCampaign);
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
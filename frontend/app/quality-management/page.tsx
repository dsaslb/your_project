'use client';

import React, { useState, useEffect } from 'react';
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
  Shield, 
  Plus, 
  Search, 
  Filter, 
  Edit, 
  Trash2, 
  Eye, 
  Star,
  AlertTriangle,
  CheckCircle,
  Clock,
  TrendingUp,
  Users,
  BarChart3,
  FileText,
  Target,
  Award,
  Zap
} from 'lucide-react';

interface QualityIssue {
  id: number;
  title: string;
  description: string;
  category: 'product' | 'service' | 'process' | 'safety' | 'hygiene';
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'open' | 'investigating' | 'resolved' | 'closed';
  reported_by: string;
  assigned_to?: string;
  store_id: number;
  store_name: string;
  reported_date: string;
  resolved_date?: string;
  resolution?: string;
  created_at: string;
  updated_at: string;
}

interface CustomerSatisfaction {
  id: number;
  customer_id: number;
  customer_name: string;
  store_id: number;
  store_name: string;
  rating: number;
  category: 'food_quality' | 'service_quality' | 'cleanliness' | 'value' | 'overall';
  comment?: string;
  survey_date: string;
  created_at: string;
}

interface QualityMetric {
  id: number;
  name: string;
  category: string;
  target_value: number;
  current_value: number;
  unit: string;
  measurement_date: string;
  status: 'excellent' | 'good' | 'fair' | 'poor';
  trend: 'improving' | 'stable' | 'declining';
}

interface QualityFormData {
  title: string;
  description: string;
  category: 'product' | 'service' | 'process' | 'safety' | 'hygiene';
  severity: 'low' | 'medium' | 'high' | 'critical';
  store_id: number;
  assigned_to?: string;
}

export default function QualityManagement() {
  const [qualityIssues, setQualityIssues] = useState<QualityIssue[]>([]);
  const [satisfactionData, setSatisfactionData] = useState<CustomerSatisfaction[]>([]);
  const [qualityMetrics, setQualityMetrics] = useState<QualityMetric[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [editingIssue, setEditingIssue] = useState<QualityIssue | null>(null);
  const [viewingIssue, setViewingIssue] = useState<QualityIssue | null>(null);
  
  const [formData, setFormData] = useState<QualityFormData>({
    title: '',
    description: '',
    category: 'product',
    severity: 'medium',
    store_id: 0,
    assigned_to: '',
  });

  const { isLoading, setLoading } = useLoadingState();
  const { handleError } = useErrorHandler();

  // 품질 이슈 목록 조회
  const fetchQualityIssues = async () => {
    try {
      const response = await apiClient.get('/api/quality-issues');
      if (response.success && response.data) {
        setQualityIssues(response.data);
      }
    } catch (error) {
      handleError(error as Error);
    }
  };

  // 고객 만족도 데이터 조회
  const fetchSatisfactionData = async () => {
    try {
      const response = await apiClient.get('/api/customer-satisfaction');
      if (response.success && response.data) {
        setSatisfactionData(response.data);
      }
    } catch (error) {
      handleError(error as Error);
    }
  };

  // 품질 지표 조회
  const fetchQualityMetrics = async () => {
    try {
      const response = await apiClient.get('/api/quality-metrics');
      if (response.success && response.data) {
        setQualityMetrics(response.data);
      }
    } catch (error) {
      handleError(error as Error);
    }
  };

  // 초기 데이터 로드
  useEffect(() => {
    fetchQualityIssues();
    fetchSatisfactionData();
    fetchQualityMetrics();
  }, []);

  // 폼 초기화
  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      category: 'product',
      severity: 'medium',
      store_id: 0,
      assigned_to: '',
    });
  };

  // 품질 이슈 생성/수정 제출
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.title || !formData.description) {
      toast.error('필수 정보를 입력해주세요.');
      return;
    }

    try {
      setLoading(true);
      
      if (editingIssue) {
        const response = await apiClient.put(`/api/quality-issues/${editingIssue.id}`, formData);
        if (response.success) {
          toast.success('품질 이슈가 성공적으로 수정되었습니다.');
          setIsCreateDialogOpen(false);
          setEditingIssue(null);
          resetForm();
          fetchQualityIssues();
        }
      } else {
        const response = await apiClient.post('/api/quality-issues', formData);
        if (response.success) {
          toast.success('품질 이슈가 성공적으로 등록되었습니다.');
          setIsCreateDialogOpen(false);
          resetForm();
          fetchQualityIssues();
        }
      }
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 품질 이슈 삭제
  const handleDelete = async (issue: QualityIssue) => {
    if (!confirm(`정말로 ${issue.title} 이슈를 삭제하시겠습니까?`)) {
      return;
    }

    try {
      setLoading(true);
      const response = await apiClient.delete(`/api/quality-issues/${issue.id}`);
      if (response.success) {
        toast.success('품질 이슈가 성공적으로 삭제되었습니다.');
        fetchQualityIssues();
      }
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 품질 이슈 수정 모드 시작
  const handleEdit = (issue: QualityIssue) => {
    setEditingIssue(issue);
    setFormData({
      title: issue.title,
      description: issue.description,
      category: issue.category,
      severity: issue.severity,
      store_id: issue.store_id,
      assigned_to: issue.assigned_to || '',
    });
    setIsCreateDialogOpen(true);
  };

  // 품질 이슈 상세 보기
  const handleView = (issue: QualityIssue) => {
    setViewingIssue(issue);
  };

  // 새 품질 이슈 생성 모드 시작
  const handleCreate = () => {
    setEditingIssue(null);
    resetForm();
    setIsCreateDialogOpen(true);
  };

  // 심각도별 색상
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'low': return 'bg-green-500/20 text-green-400 border border-green-500/30';
      case 'medium': return 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30';
      case 'high': return 'bg-orange-500/20 text-orange-400 border border-orange-500/30';
      case 'critical': return 'bg-red-500/20 text-red-400 border border-red-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border border-gray-500/30';
    }
  };

  // 상태별 색상
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open': return 'bg-red-500/20 text-red-400 border border-red-500/30';
      case 'investigating': return 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30';
      case 'resolved': return 'bg-green-500/20 text-green-400 border border-green-500/30';
      case 'closed': return 'bg-gray-500/20 text-gray-400 border border-gray-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border border-gray-500/30';
    }
  };

  // 필터링된 품질 이슈 목록
  const filteredIssues = qualityIssues.filter(issue => {
    const matchesSearch = searchTerm === '' || 
      issue.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      issue.description.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesCategory = selectedCategory === 'all' || issue.category === selectedCategory;
    const matchesSeverity = selectedSeverity === 'all' || issue.severity === selectedSeverity;
    const matchesStatus = selectedStatus === 'all' || issue.status === selectedStatus;
    
    return matchesSearch && matchesCategory && matchesSeverity && matchesStatus;
  });

  // 통계 계산
  const totalIssues = qualityIssues.length;
  const openIssues = qualityIssues.filter(i => i.status === 'open').length;
  const criticalIssues = qualityIssues.filter(i => i.severity === 'critical').length;
  const averageSatisfaction = satisfactionData.length > 0 
    ? satisfactionData.reduce((sum, s) => sum + s.rating, 0) / satisfactionData.length 
    : 0;

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Shield className="h-8 w-8 text-green-600" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">품질 관리</h1>
            <p className="text-gray-600">제품 품질과 고객 만족도를 관리하세요</p>
          </div>
        </div>
        <Button onClick={handleCreate} className="bg-green-600 hover:bg-green-700">
          <Plus className="h-4 w-4 mr-2" />
          새 이슈 등록
        </Button>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <AlertTriangle className="h-8 w-8 text-red-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">총 이슈</p>
                <p className="text-2xl font-bold text-gray-900">{totalIssues.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <Clock className="h-8 w-8 text-orange-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">미해결 이슈</p>
                <p className="text-2xl font-bold text-gray-900">{openIssues.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <Zap className="h-8 w-8 text-red-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">긴급 이슈</p>
                <p className="text-2xl font-bold text-gray-900">{criticalIssues.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <Star className="h-8 w-8 text-yellow-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">평균 만족도</p>
                <p className="text-2xl font-bold text-gray-900">{averageSatisfaction.toFixed(1)}/5.0</p>
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
                placeholder="이슈 제목, 설명 검색..."
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
                <SelectItem value="product">제품</SelectItem>
                <SelectItem value="service">서비스</SelectItem>
                <SelectItem value="process">프로세스</SelectItem>
                <SelectItem value="safety">안전</SelectItem>
                <SelectItem value="hygiene">위생</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={selectedSeverity} onValueChange={setSelectedSeverity}>
              <SelectTrigger>
                <SelectValue placeholder="심각도" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">전체 심각도</SelectItem>
                <SelectItem value="low">낮음</SelectItem>
                <SelectItem value="medium">보통</SelectItem>
                <SelectItem value="high">높음</SelectItem>
                <SelectItem value="critical">긴급</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={selectedStatus} onValueChange={setSelectedStatus}>
              <SelectTrigger>
                <SelectValue placeholder="상태" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">전체 상태</SelectItem>
                <SelectItem value="open">열림</SelectItem>
                <SelectItem value="investigating">조사 중</SelectItem>
                <SelectItem value="resolved">해결됨</SelectItem>
                <SelectItem value="closed">닫힘</SelectItem>
              </SelectContent>
            </Select>
            
            <Button variant="outline" onClick={() => {
              setSearchTerm('');
              setSelectedCategory('all');
              setSelectedSeverity('all');
              setSelectedStatus('all');
            }}>
              <Filter className="h-4 w-4 mr-2" />
              필터 초기화
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 품질 이슈 목록 */}
      <Card>
        <CardHeader>
          <CardTitle>품질 이슈 목록</CardTitle>
          <CardDescription>
            총 {filteredIssues.length}개의 이슈가 있습니다
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredIssues.map((issue) => (
              <div key={issue.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">{issue.title}</h3>
                      <Badge className={getSeverityColor(issue.severity)}>
                        {issue.severity === 'low' && '낮음'}
                        {issue.severity === 'medium' && '보통'}
                        {issue.severity === 'high' && '높음'}
                        {issue.severity === 'critical' && '긴급'}
                      </Badge>
                      <Badge className={getStatusColor(issue.status)}>
                        {issue.status === 'open' && '열림'}
                        {issue.status === 'investigating' && '조사 중'}
                        {issue.status === 'resolved' && '해결됨'}
                        {issue.status === 'closed' && '닫힘'}
                      </Badge>
                    </div>
                    
                    <p className="text-sm text-gray-600 mb-2">{issue.description}</p>
                    
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm text-gray-500">
                      <div>
                        <span className="font-medium">카테고리:</span> {issue.category}
                      </div>
                      <div>
                        <span className="font-medium">매장:</span> {issue.store_name}
                      </div>
                      <div>
                        <span className="font-medium">신고자:</span> {issue.reported_by}
                      </div>
                      <div>
                        <span className="font-medium">신고일:</span> {new Date(issue.reported_date).toLocaleDateString('ko-KR')}
                      </div>
                    </div>
                    
                    {issue.assigned_to && (
                      <div className="mt-2 text-sm text-gray-500">
                        <span className="font-medium">담당자:</span> {issue.assigned_to}
                      </div>
                    )}
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleView(issue)}
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEdit(issue)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDelete(issue)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
            
            {filteredIssues.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <Shield className="h-12 w-12 mx-auto mb-2" />
                <p>품질 이슈가 없습니다.</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* 품질 이슈 생성/수정 다이얼로그 */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              {editingIssue ? '품질 이슈 수정' : '새 품질 이슈 등록'}
            </DialogTitle>
            <DialogDescription>
              {editingIssue ? '품질 이슈 정보를 수정하세요.' : '새로운 품질 이슈를 등록하세요.'}
            </DialogDescription>
          </DialogHeader>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="title">이슈 제목 *</Label>
              <Input
                id="title"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                required
              />
            </div>
            
            <div>
              <Label htmlFor="description">이슈 설명 *</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
                required
              />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="category">카테고리</Label>
                <Select value={formData.category} onValueChange={(value: any) => setFormData({ ...formData, category: value })}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="product">제품</SelectItem>
                    <SelectItem value="service">서비스</SelectItem>
                    <SelectItem value="process">프로세스</SelectItem>
                    <SelectItem value="safety">안전</SelectItem>
                    <SelectItem value="hygiene">위생</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label htmlFor="severity">심각도</Label>
                <Select value={formData.severity} onValueChange={(value: any) => setFormData({ ...formData, severity: value })}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">낮음</SelectItem>
                    <SelectItem value="medium">보통</SelectItem>
                    <SelectItem value="high">높음</SelectItem>
                    <SelectItem value="critical">긴급</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div>
              <Label htmlFor="assigned_to">담당자</Label>
              <Input
                id="assigned_to"
                value={formData.assigned_to}
                onChange={(e) => setFormData({ ...formData, assigned_to: e.target.value })}
                placeholder="담당자 이름"
              />
            </div>
            
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                취소
              </Button>
              <Button type="submit" disabled={isLoading}>
                {isLoading ? '처리 중...' : (editingIssue ? '수정' : '등록')}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* 품질 이슈 상세 보기 다이얼로그 */}
      <Dialog open={!!viewingIssue} onOpenChange={() => setViewingIssue(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>품질 이슈 상세 정보</DialogTitle>
            <DialogDescription>
              {viewingIssue?.title} 이슈의 상세 정보입니다.
            </DialogDescription>
          </DialogHeader>
          
          {viewingIssue && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm font-medium text-gray-600">이슈 제목</Label>
                  <p className="text-lg font-semibold">{viewingIssue.title}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">카테고리</Label>
                  <Badge variant="secondary">{viewingIssue.category}</Badge>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">심각도</Label>
                  <Badge className={getSeverityColor(viewingIssue.severity)}>
                    {viewingIssue.severity === 'low' && '낮음'}
                    {viewingIssue.severity === 'medium' && '보통'}
                    {viewingIssue.severity === 'high' && '높음'}
                    {viewingIssue.severity === 'critical' && '긴급'}
                  </Badge>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">상태</Label>
                  <Badge className={getStatusColor(viewingIssue.status)}>
                    {viewingIssue.status === 'open' && '열림'}
                    {viewingIssue.status === 'investigating' && '조사 중'}
                    {viewingIssue.status === 'resolved' && '해결됨'}
                    {viewingIssue.status === 'closed' && '닫힘'}
                  </Badge>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">매장</Label>
                  <p className="text-lg">{viewingIssue.store_name}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">신고자</Label>
                  <p className="text-lg">{viewingIssue.reported_by}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">신고일</Label>
                  <p className="text-lg">{new Date(viewingIssue.reported_date).toLocaleDateString('ko-KR')}</p>
                </div>
                
                {viewingIssue.assigned_to && (
                  <div>
                    <Label className="text-sm font-medium text-gray-600">담당자</Label>
                    <p className="text-lg">{viewingIssue.assigned_to}</p>
                  </div>
                )}
              </div>
              
              <div>
                <Label className="text-sm font-medium text-gray-600">이슈 설명</Label>
                <p className="text-lg bg-gray-50 p-3 rounded-lg">{viewingIssue.description}</p>
              </div>
              
              {viewingIssue.resolution && (
                <div>
                  <Label className="text-sm font-medium text-gray-600">해결 방법</Label>
                  <p className="text-lg bg-green-50 p-3 rounded-lg">{viewingIssue.resolution}</p>
                </div>
              )}
            </div>
          )}
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setViewingIssue(null)}>
              닫기
            </Button>
            {viewingIssue && (
              <Button onClick={() => {
                setViewingIssue(null);
                handleEdit(viewingIssue);
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
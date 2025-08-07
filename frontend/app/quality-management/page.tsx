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
  Zap,
  RefreshCw
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
    store_id: 1,
    assigned_to: '',
  });

  const { isLoading, setLoading } = useLoadingState();
  const { handleError } = useErrorHandler();

  // 품질 이슈 목록 조회
  const fetchQualityIssues = async () => {
    try {
      setLoading(true);
      // 임시로 샘플 데이터 사용
      const sampleIssues: QualityIssue[] = [
        {
          id: 1,
          title: '음료 온도 불일치',
          description: '고객이 주문한 음료의 온도가 요청과 다르게 나옴',
          category: 'product',
          severity: 'medium',
          status: 'investigating',
          reported_by: '김철수',
          assigned_to: '이영희',
          store_id: 1,
          store_name: '강남점',
          reported_date: '2024-01-15',
          created_at: '2024-01-15T00:00:00Z',
          updated_at: '2024-01-15T00:00:00Z'
        },
        {
          id: 2,
          title: '위생 관리 부족',
          description: '주방 위생 상태가 기준에 미달함',
          category: 'hygiene',
          severity: 'high',
          status: 'open',
          reported_by: '박민수',
          store_id: 2,
          store_name: '홍대점',
          reported_date: '2024-01-14',
          created_at: '2024-01-14T00:00:00Z',
          updated_at: '2024-01-14T00:00:00Z'
        },
        {
          id: 3,
          title: '고객 서비스 응답 지연',
          description: '고객 문의에 대한 응답이 너무 늦음',
          category: 'service',
          severity: 'low',
          status: 'resolved',
          reported_by: '최지영',
          assigned_to: '김철수',
          store_id: 1,
          store_name: '강남점',
          reported_date: '2024-01-13',
          resolved_date: '2024-01-14',
          resolution: '서비스 매뉴얼 업데이트 및 직원 교육 실시',
          created_at: '2024-01-13T00:00:00Z',
          updated_at: '2024-01-14T00:00:00Z'
        },
        {
          id: 4,
          title: '안전 장비 점검 필요',
          description: '주방 안전 장비의 정기 점검이 필요함',
          category: 'safety',
          severity: 'critical',
          status: 'open',
          reported_by: '이영희',
          store_id: 3,
          store_name: '명동점',
          reported_date: '2024-01-12',
          created_at: '2024-01-12T00:00:00Z',
          updated_at: '2024-01-12T00:00:00Z'
        }
      ];
      
      setQualityIssues(sampleIssues);
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 고객 만족도 데이터 조회
  const fetchSatisfactionData = async () => {
    try {
      const sampleSatisfaction: CustomerSatisfaction[] = [
        {
          id: 1,
          customer_id: 1,
          customer_name: '김고객',
          store_id: 1,
          store_name: '강남점',
          rating: 4.5,
          category: 'overall',
          comment: '전반적으로 만족합니다',
          survey_date: '2024-01-15',
          created_at: '2024-01-15T00:00:00Z'
        },
        {
          id: 2,
          customer_id: 2,
          customer_name: '이고객',
          store_id: 2,
          store_name: '홍대점',
          rating: 3.8,
          category: 'overall',
          comment: '음료는 좋지만 서비스가 아쉽습니다',
          survey_date: '2024-01-14',
          created_at: '2024-01-14T00:00:00Z'
        },
        {
          id: 3,
          customer_id: 3,
          customer_name: '박고객',
          store_id: 1,
          store_name: '강남점',
          rating: 5.0,
          category: 'overall',
          comment: '완벽한 서비스였습니다',
          survey_date: '2024-01-13',
          created_at: '2024-01-13T00:00:00Z'
        }
      ];
      setSatisfactionData(sampleSatisfaction);
    } catch (error) {
      handleError(error as Error);
    }
  };

  // 품질 지표 데이터 조회
  const fetchQualityMetrics = async () => {
    try {
      const sampleMetrics: QualityMetric[] = [
        {
          id: 1,
          name: '고객 만족도',
          category: '서비스',
          target_value: 4.5,
          current_value: 4.4,
          unit: '점',
          measurement_date: '2024-01-15',
          status: 'good',
          trend: 'stable'
        },
        {
          id: 2,
          name: '음료 품질 점수',
          category: '제품',
          target_value: 95,
          current_value: 92,
          unit: '%',
          measurement_date: '2024-01-15',
          status: 'good',
          trend: 'improving'
        },
        {
          id: 3,
          name: '위생 점수',
          category: '위생',
          target_value: 98,
          current_value: 96,
          unit: '%',
          measurement_date: '2024-01-15',
          status: 'excellent',
          trend: 'stable'
        }
      ];
      setQualityMetrics(sampleMetrics);
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
      store_id: 1,
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
        // 이슈 정보 수정
        const updatedIssue = {
          ...editingIssue,
          ...formData,
          updated_at: new Date().toISOString()
        };
        
        setQualityIssues(prev => prev.map(issue => 
          issue.id === editingIssue.id ? updatedIssue : issue
        ));
        
        toast.success('품질 이슈가 수정되었습니다.');
      } else {
        // 새 이슈 생성
        const newIssue: QualityIssue = {
          id: Date.now(),
          ...formData,
          status: 'open',
          reported_by: '시스템',
          store_name: '강남점',
          reported_date: new Date().toISOString().split('T')[0],
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };
        
        setQualityIssues(prev => [...prev, newIssue]);
        toast.success('품질 이슈가 등록되었습니다.');
      }
      
      setIsCreateDialogOpen(false);
      resetForm();
      setEditingIssue(null);
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 품질 이슈 삭제
  const handleDelete = async (issue: QualityIssue) => {
    try {
      setLoading(true);
      setQualityIssues(prev => prev.filter(i => i.id !== issue.id));
      toast.success('품질 이슈가 삭제되었습니다.');
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
      case 'low': return 'bg-green-500/20 text-green-400';
      case 'medium': return 'bg-yellow-500/20 text-yellow-400';
      case 'high': return 'bg-orange-500/20 text-orange-400';
      case 'critical': return 'bg-red-500/20 text-red-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  // 상태별 색상
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open': return 'bg-red-500/20 text-red-400';
      case 'investigating': return 'bg-yellow-500/20 text-yellow-400';
      case 'resolved': return 'bg-green-500/20 text-green-400';
      case 'closed': return 'bg-gray-500/20 text-gray-400';
      default: return 'bg-gray-500/20 text-gray-400';
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
    <div className="min-h-screen p-6">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <Shield className="w-6 h-6" />
          품질 관리
        </h1>
        <p className="text-gray-300 mt-2">제품 품질과 고객 만족도를 관리하세요</p>
      </div>

      {/* 액션 버튼 */}
      <div className="flex gap-4 mb-8">
        <Button
          onClick={handleCreate}
          className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700"
        >
          <Plus className="w-4 h-4 mr-2" />
          새 이슈 등록
        </Button>
        <Button
          onClick={fetchQualityIssues}
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
                <p className="text-gray-300 text-sm">총 이슈</p>
                <p className="text-2xl font-bold text-white">{totalIssues.toLocaleString()}</p>
                <p className="text-gray-400 text-sm">전체 등록 이슈</p>
              </div>
              <div className="w-12 h-12 bg-red-500/20 rounded-lg flex items-center justify-center">
                <AlertTriangle className="w-6 h-6 text-red-400" />
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">미해결 이슈</p>
                <p className="text-2xl font-bold text-white">{openIssues.toLocaleString()}</p>
                <p className="text-gray-400 text-sm">처리 대기 중</p>
              </div>
              <div className="w-12 h-12 bg-orange-500/20 rounded-lg flex items-center justify-center">
                <Clock className="w-6 h-6 text-orange-400" />
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">긴급 이슈</p>
                <p className="text-2xl font-bold text-white">{criticalIssues.toLocaleString()}</p>
                <p className="text-gray-400 text-sm">즉시 처리 필요</p>
              </div>
              <div className="w-12 h-12 bg-red-500/20 rounded-lg flex items-center justify-center">
                <Zap className="w-6 h-6 text-red-400" />
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">평균 만족도</p>
                <p className="text-2xl font-bold text-white">{averageSatisfaction.toFixed(1)}/5.0</p>
                <p className="text-gray-400 text-sm">고객 만족도</p>
              </div>
              <div className="w-12 h-12 bg-yellow-500/20 rounded-lg flex items-center justify-center">
                <Star className="w-6 h-6 text-yellow-400" />
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
                placeholder="이슈 제목, 설명 검색..."
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
                <SelectItem value="product">제품</SelectItem>
                <SelectItem value="service">서비스</SelectItem>
                <SelectItem value="process">프로세스</SelectItem>
                <SelectItem value="safety">안전</SelectItem>
                <SelectItem value="hygiene">위생</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={selectedSeverity} onValueChange={setSelectedSeverity}>
              <SelectTrigger className="bg-white/10 border-white/20 text-white">
                <SelectValue placeholder="심각도" />
              </SelectTrigger>
              <SelectContent className="bg-white/10 border-white/20">
                <SelectItem value="all">전체 심각도</SelectItem>
                <SelectItem value="low">낮음</SelectItem>
                <SelectItem value="medium">보통</SelectItem>
                <SelectItem value="high">높음</SelectItem>
                <SelectItem value="critical">긴급</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={selectedStatus} onValueChange={setSelectedStatus}>
              <SelectTrigger className="bg-white/10 border-white/20 text-white">
                <SelectValue placeholder="상태" />
              </SelectTrigger>
              <SelectContent className="bg-white/10 border-white/20">
                <SelectItem value="all">전체 상태</SelectItem>
                <SelectItem value="open">열림</SelectItem>
                <SelectItem value="investigating">조사 중</SelectItem>
                <SelectItem value="resolved">해결됨</SelectItem>
                <SelectItem value="closed">닫힘</SelectItem>
              </SelectContent>
            </Select>
            
            <Button
              variant="outline"
              onClick={() => {
                setSearchTerm('');
                setSelectedCategory('all');
                setSelectedSeverity('all');
                setSelectedStatus('all');
              }}
              className="border-white/20 text-white hover:bg-white/10"
            >
              <Filter className="w-4 h-4 mr-2" />
              필터 초기화
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 품질 이슈 목록 */}
      <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
        <CardHeader>
          <CardTitle className="text-white">품질 이슈 목록</CardTitle>
          <CardDescription className="text-gray-300">
            총 {filteredIssues.length}개의 이슈가 있습니다
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredIssues.map((issue) => (
              <div
                key={issue.id}
                className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:bg-white/10 transition-all duration-300"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-4 mb-3">
                      <div className="w-12 h-12 bg-gradient-to-r from-red-500 to-orange-600 rounded-lg flex items-center justify-center">
                        <AlertTriangle className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-white">{issue.title}</h3>
                        <p className="text-gray-400">{issue.store_name} • {issue.reported_by}</p>
                        <p className="text-gray-400 text-sm">{new Date(issue.reported_date).toLocaleDateString()}</p>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                      <div>
                        <p className="text-gray-300 text-sm">카테고리</p>
                        <p className="text-white font-medium">
                          {issue.category === 'product' && '제품'}
                          {issue.category === 'service' && '서비스'}
                          {issue.category === 'process' && '프로세스'}
                          {issue.category === 'safety' && '안전'}
                          {issue.category === 'hygiene' && '위생'}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-300 text-sm">담당자</p>
                        <p className="text-white font-medium">{issue.assigned_to || '미배정'}</p>
                      </div>
                      <div>
                        <p className="text-gray-300 text-sm">보고일</p>
                        <p className="text-white font-medium">{new Date(issue.reported_date).toLocaleDateString()}</p>
                      </div>
                      <div>
                        <p className="text-gray-300 text-sm">해결일</p>
                        <p className="text-white font-medium">
                          {issue.resolved_date ? new Date(issue.resolved_date).toLocaleDateString() : '미해결'}
                        </p>
                      </div>
                    </div>
                    
                    <div className="bg-white/5 rounded-lg p-3">
                      <p className="text-gray-300 text-sm mb-1">설명</p>
                      <p className="text-white text-sm">{issue.description}</p>
                    </div>
                    
                    {issue.resolution && (
                      <div className="bg-white/5 rounded-lg p-3 mt-3">
                        <p className="text-gray-300 text-sm mb-1">해결 방법</p>
                        <p className="text-white text-sm">{issue.resolution}</p>
                      </div>
                    )}
                  </div>
                  
                  <div className="flex flex-col gap-2 ml-4">
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
                    
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleView(issue)}
                        className="border-white/20 text-white hover:bg-white/10"
                      >
                        <Eye className="w-4 h-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleEdit(issue)}
                        className="border-white/20 text-white hover:bg-white/10"
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button
                        size="sm"
                        onClick={() => handleDelete(issue)}
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

      {/* 품질 이슈 생성/수정 다이얼로그 */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="bg-white/10 backdrop-blur-sm border border-white/20 max-w-2xl">
          <DialogHeader>
            <DialogTitle className="text-white">
              {editingIssue ? '품질 이슈 수정' : '새 품질 이슈 등록'}
            </DialogTitle>
          </DialogHeader>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label className="text-gray-300">이슈 제목 *</Label>
                <Input
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  className="mt-1 bg-white/10 border-white/20 text-white"
                  placeholder="이슈 제목을 입력하세요"
                />
              </div>
              
              <div>
                <Label className="text-gray-300">카테고리 *</Label>
                <Select value={formData.category} onValueChange={(value: any) => setFormData({...formData, category: value})}>
                  <SelectTrigger className="mt-1 bg-white/10 border-white/20 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-white/10 border-white/20">
                    <SelectItem value="product">제품</SelectItem>
                    <SelectItem value="service">서비스</SelectItem>
                    <SelectItem value="process">프로세스</SelectItem>
                    <SelectItem value="safety">안전</SelectItem>
                    <SelectItem value="hygiene">위생</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label className="text-gray-300">심각도 *</Label>
                <Select value={formData.severity} onValueChange={(value: any) => setFormData({...formData, severity: value})}>
                  <SelectTrigger className="mt-1 bg-white/10 border-white/20 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-white/10 border-white/20">
                    <SelectItem value="low">낮음</SelectItem>
                    <SelectItem value="medium">보통</SelectItem>
                    <SelectItem value="high">높음</SelectItem>
                    <SelectItem value="critical">긴급</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label className="text-gray-300">담당자</Label>
                <Input
                  value={formData.assigned_to}
                  onChange={(e) => setFormData({...formData, assigned_to: e.target.value})}
                  className="mt-1 bg-white/10 border-white/20 text-white"
                  placeholder="담당자명을 입력하세요"
                />
              </div>
            </div>
            
            <div>
              <Label className="text-gray-300">이슈 설명 *</Label>
              <Textarea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                className="mt-1 bg-white/10 border-white/20 text-white"
                placeholder="이슈에 대한 상세한 설명을 입력하세요"
                rows={4}
              />
            </div>
            
            <div className="flex gap-2">
              <Button type="submit" className="flex-1 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700">
                {editingIssue ? '수정' : '등록'}
              </Button>
              <Button type="button" variant="outline" onClick={() => setIsCreateDialogOpen(false)} className="border-white/20 text-white hover:bg-white/10">
                취소
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* 품질 이슈 상세 보기 다이얼로그 */}
      <Dialog open={!!viewingIssue} onOpenChange={() => setViewingIssue(null)}>
        <DialogContent className="bg-white/10 backdrop-blur-sm border border-white/20 max-w-2xl">
          <DialogHeader>
            <DialogTitle className="text-white">품질 이슈 상세 정보</DialogTitle>
          </DialogHeader>
          
          {viewingIssue && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label className="text-gray-300 text-sm">이슈 제목</Label>
                  <p className="text-white font-medium">{viewingIssue.title}</p>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">카테고리</Label>
                  <Badge className={getSeverityColor(viewingIssue.category)}>
                    {viewingIssue.category === 'product' && '제품'}
                    {viewingIssue.category === 'service' && '서비스'}
                    {viewingIssue.category === 'process' && '프로세스'}
                    {viewingIssue.category === 'safety' && '안전'}
                    {viewingIssue.category === 'hygiene' && '위생'}
                  </Badge>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">심각도</Label>
                  <Badge className={getSeverityColor(viewingIssue.severity)}>
                    {viewingIssue.severity === 'low' && '낮음'}
                    {viewingIssue.severity === 'medium' && '보통'}
                    {viewingIssue.severity === 'high' && '높음'}
                    {viewingIssue.severity === 'critical' && '긴급'}
                  </Badge>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">상태</Label>
                  <Badge className={getStatusColor(viewingIssue.status)}>
                    {viewingIssue.status === 'open' && '열림'}
                    {viewingIssue.status === 'investigating' && '조사 중'}
                    {viewingIssue.status === 'resolved' && '해결됨'}
                    {viewingIssue.status === 'closed' && '닫힘'}
                  </Badge>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">보고자</Label>
                  <p className="text-white font-medium">{viewingIssue.reported_by}</p>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">담당자</Label>
                  <p className="text-white font-medium">{viewingIssue.assigned_to || '미배정'}</p>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">매장</Label>
                  <p className="text-white font-medium">{viewingIssue.store_name}</p>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">보고일</Label>
                  <p className="text-white font-medium">{new Date(viewingIssue.reported_date).toLocaleDateString()}</p>
                </div>
                {viewingIssue.resolved_date && (
                  <div>
                    <Label className="text-gray-300 text-sm">해결일</Label>
                    <p className="text-white font-medium">{new Date(viewingIssue.resolved_date).toLocaleDateString()}</p>
                  </div>
                )}
              </div>
              
              <div>
                <Label className="text-gray-300 text-sm">이슈 설명</Label>
                <p className="text-white">{viewingIssue.description}</p>
              </div>
              
              {viewingIssue.resolution && (
                <div>
                  <Label className="text-gray-300 text-sm">해결 방법</Label>
                  <p className="text-white">{viewingIssue.resolution}</p>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
} 
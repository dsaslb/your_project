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
  FileText, 
  Plus, 
  Search, 
  Filter, 
  Download, 
  Eye, 
  Edit, 
  Trash2,
  Calendar,
  BarChart3,
  TrendingUp,
  DollarSign,
  Users,
  Store,
  Package,
  Clock,
  Star,
  PieChart,
  LineChart,
  Download as DownloadIcon,
  Share2,
  Printer,
  Mail,
  Settings,
  RefreshCw
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  BarChart as RechartsBarChart,
  Bar,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  AreaChart,
  Area
} from 'recharts';

interface Report {
  id: number;
  title: string;
  description: string;
  type: 'sales' | 'inventory' | 'customer' | 'employee' | 'financial' | 'quality' | 'marketing' | 'comprehensive';
  status: 'draft' | 'published' | 'archived';
  created_by: string;
  created_at: string;
  updated_at: string;
  last_generated?: string;
  schedule?: string;
  recipients?: string[];
  data_source: string[];
  chart_config: ChartConfig[];
}

interface ChartConfig {
  id: string;
  type: 'line' | 'bar' | 'pie' | 'area';
  title: string;
  data_source: string;
  x_axis: string;
  y_axis: string;
  color: string;
}

interface ReportFormData {
  title: string;
  description: string;
  type: 'sales' | 'inventory' | 'customer' | 'employee' | 'financial' | 'quality' | 'marketing' | 'comprehensive';
  data_source: string[];
  schedule?: string;
  recipients?: string[];
}

interface SalesData {
  date: string;
  revenue: number;
  orders: number;
  customers: number;
  average_order: number;
}

interface InventoryData {
  category: string;
  current_stock: number;
  reorder_level: number;
  value: number;
  turnover_rate: number;
}

interface CustomerData {
  segment: string;
  count: number;
  total_spent: number;
  average_order: number;
  satisfaction: number;
}

export default function Reports() {
  const [reports, setReports] = useState<Report[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [editingReport, setEditingReport] = useState<Report | null>(null);
  const [previewingReport, setPreviewingReport] = useState<Report | null>(null);
  
  const [formData, setFormData] = useState<ReportFormData>({
    title: '',
    description: '',
    type: 'sales',
    data_source: [],
    schedule: '',
    recipients: [],
  });

  const { isLoading, setLoading } = useLoadingState();
  const { handleError } = useErrorHandler();

  // 보고서 목록 조회
  const fetchReports = async () => {
    try {
      setLoading(true);
      // 임시로 샘플 데이터 사용
      const sampleReports: Report[] = [
        {
          id: 1,
          title: '월간 매출 보고서',
          description: '월별 매출, 주문, 고객 데이터 분석',
          type: 'sales',
          status: 'published',
          created_by: '김관리자',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-15T00:00:00Z',
          last_generated: '2024-01-15T00:00:00Z',
          schedule: 'monthly',
          recipients: ['management@company.com'],
          data_source: ['sales', 'orders', 'customers'],
          chart_config: [
            {
              id: '1',
              type: 'line',
              title: '매출 트렌드',
              data_source: 'sales',
              x_axis: 'date',
              y_axis: 'revenue',
              color: '#3B82F6'
            }
          ]
        },
        {
          id: 2,
          title: '재고 현황 보고서',
          description: '카테고리별 재고 수준 및 회전율 분석',
          type: 'inventory',
          status: 'published',
          created_by: '이관리자',
          created_at: '2024-01-05T00:00:00Z',
          updated_at: '2024-01-10T00:00:00Z',
          last_generated: '2024-01-10T00:00:00Z',
          schedule: 'weekly',
          recipients: ['inventory@company.com'],
          data_source: ['inventory', 'products'],
          chart_config: [
            {
              id: '2',
              type: 'bar',
              title: '카테고리별 재고',
              data_source: 'inventory',
              x_axis: 'category',
              y_axis: 'current_stock',
              color: '#10B981'
            }
          ]
        },
        {
          id: 3,
          title: '고객 만족도 보고서',
          description: '고객 세그먼트별 만족도 및 구매 패턴 분석',
          type: 'customer',
          status: 'draft',
          created_by: '박관리자',
          created_at: '2024-01-12T00:00:00Z',
          updated_at: '2024-01-12T00:00:00Z',
          data_source: ['customers', 'satisfaction'],
          chart_config: [
            {
              id: '3',
              type: 'pie',
              title: '고객 세그먼트 분포',
              data_source: 'customers',
              x_axis: 'segment',
              y_axis: 'count',
              color: '#8B5CF6'
            }
          ]
        },
        {
          id: 4,
          title: '종합 비즈니스 보고서',
          description: '전체 비즈니스 성과 종합 분석',
          type: 'comprehensive',
          status: 'published',
          created_by: '최관리자',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-15T00:00:00Z',
          last_generated: '2024-01-15T00:00:00Z',
          schedule: 'monthly',
          recipients: ['ceo@company.com', 'management@company.com'],
          data_source: ['sales', 'inventory', 'customers', 'employees'],
          chart_config: [
            {
              id: '4',
              type: 'area',
              title: '종합 성과 지표',
              data_source: 'comprehensive',
              x_axis: 'date',
              y_axis: 'performance',
              color: '#F59E0B'
            }
          ]
        }
      ];
      
      setReports(sampleReports);
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 샘플 데이터 조회
  const fetchSampleData = async () => {
    try {
      // 샘플 데이터는 이미 컴포넌트 내에서 정의됨
      return {
        salesData: [
          { date: '2024-01', revenue: 15000000, orders: 1200, customers: 800, average_order: 12500 },
          { date: '2024-02', revenue: 18000000, orders: 1400, customers: 950, average_order: 12857 },
          { date: '2024-03', revenue: 22000000, orders: 1600, customers: 1100, average_order: 13750 }
        ],
        inventoryData: [
          { category: '음료', current_stock: 500, reorder_level: 100, value: 2500000, turnover_rate: 12 },
          { category: '음식', current_stock: 300, reorder_level: 80, value: 1800000, turnover_rate: 8 },
          { category: '디저트', current_stock: 200, reorder_level: 50, value: 1200000, turnover_rate: 6 }
        ],
        customerData: [
          { segment: 'VIP', count: 150, total_spent: 45000000, average_order: 30000, satisfaction: 4.8 },
          { segment: '일반', count: 800, total_spent: 80000000, average_order: 10000, satisfaction: 4.2 },
          { segment: '신규', count: 200, total_spent: 15000000, average_order: 7500, satisfaction: 4.0 }
        ]
      };
    } catch (error) {
      handleError(error as Error);
    }
  };

  // 초기 데이터 로드
  useEffect(() => {
    fetchReports();
    fetchSampleData();
  }, []);

  // 폼 초기화
  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      type: 'sales',
      data_source: [],
      schedule: '',
      recipients: [],
    });
  };

  // 보고서 생성/수정 제출
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.title || !formData.description) {
      toast.error('필수 정보를 입력해주세요.');
      return;
    }

    try {
      setLoading(true);
      
      if (editingReport) {
        // 보고서 정보 수정
        const updatedReport = {
          ...editingReport,
          ...formData,
          updated_at: new Date().toISOString()
        };
        
        setReports(prev => prev.map(report => 
          report.id === editingReport.id ? updatedReport : report
        ));
        
        toast.success('보고서가 수정되었습니다.');
      } else {
        // 새 보고서 생성
        const newReport: Report = {
          id: Date.now(),
          ...formData,
          status: 'draft',
          created_by: '시스템',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          chart_config: []
        };
        
        setReports(prev => [...prev, newReport]);
        toast.success('보고서가 생성되었습니다.');
      }
      
      setIsCreateDialogOpen(false);
      resetForm();
      setEditingReport(null);
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 보고서 삭제
  const handleDelete = async (report: Report) => {
    try {
      setLoading(true);
      setReports(prev => prev.filter(r => r.id !== report.id));
      toast.success('보고서가 삭제되었습니다.');
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 보고서 미리보기
  const handlePreview = (report: Report) => {
    setPreviewingReport(report);
  };

  // 보고서 수정 모드 시작
  const handleEdit = (report: Report) => {
    setEditingReport(report);
    setFormData({
      title: report.title,
      description: report.description,
      type: report.type,
      data_source: report.data_source,
      schedule: report.schedule || '',
      recipients: report.recipients || [],
    });
    setIsCreateDialogOpen(true);
  };

  // 새 보고서 생성 모드 시작
  const handleCreate = () => {
    setEditingReport(null);
    resetForm();
    setIsCreateDialogOpen(true);
  };

  // 보고서 내보내기
  const handleExport = async (report: Report, format: 'pdf' | 'excel' | 'csv') => {
    try {
      setLoading(true);
      toast.success(`${report.title} 보고서가 ${format.toUpperCase()} 형식으로 내보내기되었습니다.`);
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 상태별 색상
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft': return 'bg-gray-500/20 text-gray-400';
      case 'published': return 'bg-green-500/20 text-green-400';
      case 'archived': return 'bg-blue-500/20 text-blue-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  // 타입별 색상
  const getTypeColor = (type: string) => {
    switch (type) {
      case 'sales': return 'bg-green-500/20 text-green-400';
      case 'inventory': return 'bg-blue-500/20 text-blue-400';
      case 'customer': return 'bg-purple-500/20 text-purple-400';
      case 'employee': return 'bg-orange-500/20 text-orange-400';
      case 'financial': return 'bg-red-500/20 text-red-400';
      case 'quality': return 'bg-cyan-500/20 text-cyan-400';
      case 'marketing': return 'bg-pink-500/20 text-pink-400';
      case 'comprehensive': return 'bg-indigo-500/20 text-indigo-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  // 필터링된 보고서 목록
  const filteredReports = reports.filter(report => {
    const matchesSearch = searchTerm === '' || 
      report.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      report.description.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesType = selectedType === 'all' || report.type === selectedType;
    const matchesStatus = selectedStatus === 'all' || report.status === selectedStatus;
    
    return matchesSearch && matchesType && matchesStatus;
  });

  // 통계 계산
  const totalReports = reports.length;
  const publishedReports = reports.filter(r => r.status === 'published').length;
  const scheduledReports = reports.filter(r => r.schedule).length;
  const recentReports = reports.filter(r => {
    const reportDate = new Date(r.created_at);
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);
    return reportDate >= weekAgo;
  }).length;

  // 샘플 차트 데이터
  const chartColors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4'];

  return (
    <div className="min-h-screen p-6">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <FileText className="w-6 h-6" />
          보고서 시스템
        </h1>
        <p className="text-gray-300 mt-2">종합적인 비즈니스 리포트를 생성하고 관리하세요</p>
      </div>

      {/* 액션 버튼 */}
      <div className="flex gap-4 mb-8">
        <Button
          onClick={handleCreate}
          className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700"
        >
          <Plus className="w-4 h-4 mr-2" />
          새 보고서 생성
        </Button>
        <Button
          onClick={fetchReports}
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
                <p className="text-gray-300 text-sm">총 보고서</p>
                <p className="text-2xl font-bold text-white">{totalReports.toLocaleString()}</p>
                <p className="text-gray-400 text-sm">전체 등록 보고서</p>
              </div>
              <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
                <FileText className="w-6 h-6 text-blue-400" />
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">발행된 보고서</p>
                <p className="text-2xl font-bold text-white">{publishedReports.toLocaleString()}</p>
                <p className="text-gray-400 text-sm">공개된 보고서</p>
              </div>
              <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-green-400" />
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">스케줄된 보고서</p>
                <p className="text-2xl font-bold text-white">{scheduledReports.toLocaleString()}</p>
                <p className="text-gray-400 text-sm">자동 생성 예정</p>
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
                <p className="text-gray-300 text-sm">최근 생성</p>
                <p className="text-2xl font-bold text-white">{recentReports.toLocaleString()}</p>
                <p className="text-gray-400 text-sm">지난 7일</p>
              </div>
              <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center">
                <RefreshCw className="w-6 h-6 text-purple-400" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 필터 및 검색 */}
      <Card className="bg-white/10 backdrop-blur-sm border border-white/20 mb-8">
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="보고서명, 설명 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 bg-white/10 border-white/20 text-white placeholder-gray-400"
              />
            </div>
            
            <Select value={selectedType} onValueChange={setSelectedType}>
              <SelectTrigger className="bg-white/10 border-white/20 text-white">
                <SelectValue placeholder="보고서 타입" />
              </SelectTrigger>
              <SelectContent className="bg-white/10 border-white/20">
                <SelectItem value="all">전체 타입</SelectItem>
                <SelectItem value="sales">매출</SelectItem>
                <SelectItem value="inventory">재고</SelectItem>
                <SelectItem value="customer">고객</SelectItem>
                <SelectItem value="employee">직원</SelectItem>
                <SelectItem value="financial">재무</SelectItem>
                <SelectItem value="quality">품질</SelectItem>
                <SelectItem value="marketing">마케팅</SelectItem>
                <SelectItem value="comprehensive">종합</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={selectedStatus} onValueChange={setSelectedStatus}>
              <SelectTrigger className="bg-white/10 border-white/20 text-white">
                <SelectValue placeholder="상태" />
              </SelectTrigger>
              <SelectContent className="bg-white/10 border-white/20">
                <SelectItem value="all">전체 상태</SelectItem>
                <SelectItem value="draft">초안</SelectItem>
                <SelectItem value="published">발행됨</SelectItem>
                <SelectItem value="archived">보관됨</SelectItem>
              </SelectContent>
            </Select>
            
            <Button
              variant="outline"
              onClick={() => {
                setSearchTerm('');
                setSelectedType('all');
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

      {/* 보고서 목록 */}
      <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
        <CardHeader>
          <CardTitle className="text-white">보고서 목록</CardTitle>
          <CardDescription className="text-gray-300">
            총 {filteredReports.length}개의 보고서가 있습니다
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredReports.map((report) => (
              <div
                key={report.id}
                className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:bg-white/10 transition-all duration-300"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-4 mb-3">
                      <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                        <FileText className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-white">{report.title}</h3>
                        <p className="text-gray-400">{report.created_by} • {new Date(report.created_at).toLocaleDateString()}</p>
                        <p className="text-gray-400 text-sm">{report.description}</p>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                      <div>
                        <p className="text-gray-300 text-sm">타입</p>
                        <p className="text-white font-medium">
                          {report.type === 'sales' && '매출'}
                          {report.type === 'inventory' && '재고'}
                          {report.type === 'customer' && '고객'}
                          {report.type === 'employee' && '직원'}
                          {report.type === 'financial' && '재무'}
                          {report.type === 'quality' && '품질'}
                          {report.type === 'marketing' && '마케팅'}
                          {report.type === 'comprehensive' && '종합'}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-300 text-sm">생성자</p>
                        <p className="text-white font-medium">{report.created_by}</p>
                      </div>
                      <div>
                        <p className="text-gray-300 text-sm">생성일</p>
                        <p className="text-white font-medium">{new Date(report.created_at).toLocaleDateString()}</p>
                      </div>
                      <div>
                        <p className="text-gray-300 text-sm">마지막 생성</p>
                        <p className="text-white font-medium">
                          {report.last_generated ? new Date(report.last_generated).toLocaleDateString() : '없음'}
                        </p>
                      </div>
                    </div>
                    
                    <div className="bg-white/5 rounded-lg p-3">
                      <p className="text-gray-300 text-sm mb-1">데이터 소스</p>
                      <div className="flex flex-wrap gap-2">
                        {report.data_source.map((source, index) => (
                          <Badge key={index} className="bg-white/10 text-white border-white/20">
                            {source}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    
                    {report.schedule && (
                      <div className="bg-white/5 rounded-lg p-3 mt-3">
                        <p className="text-gray-300 text-sm mb-1">스케줄</p>
                        <p className="text-white">{report.schedule}</p>
                      </div>
                    )}
                  </div>
                  
                  <div className="flex flex-col gap-2 ml-4">
                    <Badge className={getTypeColor(report.type)}>
                      {report.type === 'sales' && '매출'}
                      {report.type === 'inventory' && '재고'}
                      {report.type === 'customer' && '고객'}
                      {report.type === 'employee' && '직원'}
                      {report.type === 'financial' && '재무'}
                      {report.type === 'quality' && '품질'}
                      {report.type === 'marketing' && '마케팅'}
                      {report.type === 'comprehensive' && '종합'}
                    </Badge>
                    
                    <Badge className={getStatusColor(report.status)}>
                      {report.status === 'draft' && '초안'}
                      {report.status === 'published' && '발행됨'}
                      {report.status === 'archived' && '보관됨'}
                    </Badge>
                    
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handlePreview(report)}
                        className="border-white/20 text-white hover:bg-white/10"
                      >
                        <Eye className="w-4 h-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleEdit(report)}
                        className="border-white/20 text-white hover:bg-white/10"
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button
                        size="sm"
                        onClick={() => handleExport(report, 'pdf')}
                        className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700"
                      >
                        <Download className="w-4 h-4" />
                      </Button>
                      <Button
                        size="sm"
                        onClick={() => handleDelete(report)}
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

      {/* 보고서 생성/수정 다이얼로그 */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="bg-white/10 backdrop-blur-sm border border-white/20 max-w-2xl">
          <DialogHeader>
            <DialogTitle className="text-white">
              {editingReport ? '보고서 수정' : '새 보고서 생성'}
            </DialogTitle>
          </DialogHeader>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label className="text-gray-300">보고서 제목 *</Label>
                <Input
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  className="mt-1 bg-white/10 border-white/20 text-white"
                  placeholder="보고서 제목을 입력하세요"
                />
              </div>
              
              <div>
                <Label className="text-gray-300">보고서 타입 *</Label>
                <Select value={formData.type} onValueChange={(value: any) => setFormData({...formData, type: value})}>
                  <SelectTrigger className="mt-1 bg-white/10 border-white/20 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-white/10 border-white/20">
                    <SelectItem value="sales">매출</SelectItem>
                    <SelectItem value="inventory">재고</SelectItem>
                    <SelectItem value="customer">고객</SelectItem>
                    <SelectItem value="employee">직원</SelectItem>
                    <SelectItem value="financial">재무</SelectItem>
                    <SelectItem value="quality">품질</SelectItem>
                    <SelectItem value="marketing">마케팅</SelectItem>
                    <SelectItem value="comprehensive">종합</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label className="text-gray-300">스케줄</Label>
                <Select value={formData.schedule} onValueChange={(value: any) => setFormData({...formData, schedule: value})}>
                  <SelectTrigger className="mt-1 bg-white/10 border-white/20 text-white">
                    <SelectValue placeholder="스케줄 선택" />
                  </SelectTrigger>
                  <SelectContent className="bg-white/10 border-white/20">
                    <SelectItem value="daily">일간</SelectItem>
                    <SelectItem value="weekly">주간</SelectItem>
                    <SelectItem value="monthly">월간</SelectItem>
                    <SelectItem value="quarterly">분기</SelectItem>
                    <SelectItem value="yearly">연간</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label className="text-gray-300">수신자</Label>
                <Input
                  value={formData.recipients?.join(', ') || ''}
                  onChange={(e) => setFormData({...formData, recipients: e.target.value.split(',').map(s => s.trim())})}
                  className="mt-1 bg-white/10 border-white/20 text-white"
                  placeholder="이메일 주소 (쉼표로 구분)"
                />
              </div>
            </div>
            
            <div>
              <Label className="text-gray-300">보고서 설명 *</Label>
              <Textarea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                className="mt-1 bg-white/10 border-white/20 text-white"
                placeholder="보고서에 대한 상세한 설명을 입력하세요"
                rows={4}
              />
            </div>
            
            <div className="flex gap-2">
              <Button type="submit" className="flex-1 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700">
                {editingReport ? '수정' : '생성'}
              </Button>
              <Button type="button" variant="outline" onClick={() => setIsCreateDialogOpen(false)} className="border-white/20 text-white hover:bg-white/10">
                취소
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* 보고서 미리보기 다이얼로그 */}
      <Dialog open={!!previewingReport} onOpenChange={() => setPreviewingReport(null)}>
        <DialogContent className="bg-white/10 backdrop-blur-sm border border-white/20 max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-white">보고서 미리보기</DialogTitle>
          </DialogHeader>
          
          {previewingReport && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label className="text-gray-300 text-sm">보고서 제목</Label>
                  <p className="text-white font-medium">{previewingReport.title}</p>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">보고서 타입</Label>
                  <Badge className={getTypeColor(previewingReport.type)}>
                    {previewingReport.type === 'sales' && '매출'}
                    {previewingReport.type === 'inventory' && '재고'}
                    {previewingReport.type === 'customer' && '고객'}
                    {previewingReport.type === 'employee' && '직원'}
                    {previewingReport.type === 'financial' && '재무'}
                    {previewingReport.type === 'quality' && '품질'}
                    {previewingReport.type === 'marketing' && '마케팅'}
                    {previewingReport.type === 'comprehensive' && '종합'}
                  </Badge>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">상태</Label>
                  <Badge className={getStatusColor(previewingReport.status)}>
                    {previewingReport.status === 'draft' && '초안'}
                    {previewingReport.status === 'published' && '발행됨'}
                    {previewingReport.status === 'archived' && '보관됨'}
                  </Badge>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">생성자</Label>
                  <p className="text-white font-medium">{previewingReport.created_by}</p>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">생성일</Label>
                  <p className="text-white font-medium">{new Date(previewingReport.created_at).toLocaleDateString()}</p>
                </div>
                <div>
                  <Label className="text-gray-300 text-sm">마지막 생성</Label>
                  <p className="text-white font-medium">
                    {previewingReport.last_generated ? new Date(previewingReport.last_generated).toLocaleDateString() : '없음'}
                  </p>
                </div>
              </div>
              
              <div>
                <Label className="text-gray-300 text-sm">보고서 설명</Label>
                <p className="text-white">{previewingReport.description}</p>
              </div>
              
              <div>
                <Label className="text-gray-300 text-sm">데이터 소스</Label>
                <div className="flex flex-wrap gap-2 mt-2">
                  {previewingReport.data_source.map((source, index) => (
                    <Badge key={index} className="bg-white/10 text-white border-white/20">
                      {source}
                    </Badge>
                  ))}
                </div>
              </div>
              
              {previewingReport.schedule && (
                <div>
                  <Label className="text-gray-300 text-sm">스케줄</Label>
                  <p className="text-white">{previewingReport.schedule}</p>
                </div>
              )}
              
              {previewingReport.recipients && previewingReport.recipients.length > 0 && (
                <div>
                  <Label className="text-gray-300 text-sm">수신자</Label>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {previewingReport.recipients.map((recipient, index) => (
                      <Badge key={index} className="bg-white/10 text-white border-white/20">
                        {recipient}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
} 
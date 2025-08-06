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
  const [salesData, setSalesData] = useState<SalesData[]>([]);
  const [inventoryData, setInventoryData] = useState<InventoryData[]>([]);
  const [customerData, setCustomerData] = useState<CustomerData[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isPreviewDialogOpen, setIsPreviewDialogOpen] = useState(false);
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
      const response = await apiClient.get('/api/reports');
      if (response.success && response.data) {
        setReports(response.data);
      }
    } catch (error) {
      handleError(error as Error);
    }
  };

  // 샘플 데이터 로드
  const fetchSampleData = async () => {
    try {
      // 매출 데이터
      const salesResponse = await apiClient.get('/api/sales-data');
      if (salesResponse.success && salesResponse.data) {
        setSalesData(salesResponse.data);
      }

      // 재고 데이터
      const inventoryResponse = await apiClient.get('/api/inventory-data');
      if (inventoryResponse.success && inventoryResponse.data) {
        setInventoryData(inventoryResponse.data);
      }

      // 고객 데이터
      const customerResponse = await apiClient.get('/api/customer-data');
      if (customerResponse.success && customerResponse.data) {
        setCustomerData(customerResponse.data);
      }
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
        const response = await apiClient.put(`/api/reports/${editingReport.id}`, formData);
        if (response.success) {
          toast.success('보고서가 성공적으로 수정되었습니다.');
          setIsCreateDialogOpen(false);
          setEditingReport(null);
          resetForm();
          fetchReports();
        }
      } else {
        const response = await apiClient.post('/api/reports', formData);
        if (response.success) {
          toast.success('보고서가 성공적으로 생성되었습니다.');
          setIsCreateDialogOpen(false);
          resetForm();
          fetchReports();
        }
      }
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 보고서 삭제
  const handleDelete = async (report: Report) => {
    if (!confirm(`정말로 ${report.title} 보고서를 삭제하시겠습니까?`)) {
      return;
    }

    try {
      setLoading(true);
      const response = await apiClient.delete(`/api/reports/${report.id}`);
      if (response.success) {
        toast.success('보고서가 성공적으로 삭제되었습니다.');
        fetchReports();
      }
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 보고서 미리보기
  const handlePreview = (report: Report) => {
    setPreviewingReport(report);
    setIsPreviewDialogOpen(true);
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
      const response = await apiClient.post(`/api/reports/${report.id}/export`, { format });
      if (response.success) {
        toast.success(`${format.toUpperCase()} 형식으로 내보내기가 완료되었습니다.`);
        // 실제로는 다운로드 링크를 생성하거나 파일을 다운로드
      }
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 상태별 색상
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft': return 'bg-gray-500/20 text-gray-400 border border-gray-500/30';
      case 'published': return 'bg-green-500/20 text-green-400 border border-green-500/30';
      case 'archived': return 'bg-blue-500/20 text-blue-400 border border-blue-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border border-gray-500/30';
    }
  };

  // 타입별 색상
  const getTypeColor = (type: string) => {
    switch (type) {
      case 'sales': return 'bg-green-500/20 text-green-400 border border-green-500/30';
      case 'inventory': return 'bg-blue-500/20 text-blue-400 border border-blue-500/30';
      case 'customer': return 'bg-purple-500/20 text-purple-400 border border-purple-500/30';
      case 'employee': return 'bg-orange-500/20 text-orange-400 border border-orange-500/30';
      case 'financial': return 'bg-red-500/20 text-red-400 border border-red-500/30';
      case 'quality': return 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30';
      case 'marketing': return 'bg-pink-500/20 text-pink-400 border border-pink-500/30';
      case 'comprehensive': return 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border border-gray-500/30';
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
    <div className="container mx-auto p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <FileText className="h-8 w-8 text-blue-600" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">보고서 시스템</h1>
            <p className="text-gray-600">종합적인 비즈니스 리포트를 생성하고 관리하세요</p>
          </div>
        </div>
        <Button onClick={handleCreate} className="bg-blue-600 hover:bg-blue-700">
          <Plus className="h-4 w-4 mr-2" />
          새 보고서 생성
        </Button>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <FileText className="h-8 w-8 text-blue-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">총 보고서</p>
                <p className="text-2xl font-bold text-gray-900">{totalReports.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <BarChart3 className="h-8 w-8 text-green-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">발행된 보고서</p>
                <p className="text-2xl font-bold text-gray-900">{publishedReports.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <Clock className="h-8 w-8 text-orange-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">스케줄된 보고서</p>
                <p className="text-2xl font-bold text-gray-900">{scheduledReports.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <RefreshCw className="h-8 w-8 text-purple-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">최근 생성</p>
                <p className="text-2xl font-bold text-gray-900">{recentReports.toLocaleString()}</p>
                <p className="text-sm text-gray-500">지난 7일</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 필터 및 검색 */}
      <Card>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="보고서명, 설명 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            
            <Select value={selectedType} onValueChange={setSelectedType}>
              <SelectTrigger>
                <SelectValue placeholder="보고서 타입" />
              </SelectTrigger>
              <SelectContent>
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
              <SelectTrigger>
                <SelectValue placeholder="상태" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">전체 상태</SelectItem>
                <SelectItem value="draft">초안</SelectItem>
                <SelectItem value="published">발행됨</SelectItem>
                <SelectItem value="archived">보관됨</SelectItem>
              </SelectContent>
            </Select>
            
            <Button variant="outline" onClick={() => {
              setSearchTerm('');
              setSelectedType('all');
              setSelectedStatus('all');
            }}>
              <Filter className="h-4 w-4 mr-2" />
              필터 초기화
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 보고서 목록 */}
      <Card>
        <CardHeader>
          <CardTitle>보고서 목록</CardTitle>
          <CardDescription>
            총 {filteredReports.length}개의 보고서가 있습니다
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredReports.map((report) => (
              <div key={report.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">{report.title}</h3>
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
                    </div>
                    
                    <p className="text-sm text-gray-600 mb-2">{report.description}</p>
                    
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm text-gray-500">
                      <div>
                        <span className="font-medium">생성자:</span> {report.created_by}
                      </div>
                      <div>
                        <span className="font-medium">생성일:</span> {new Date(report.created_at).toLocaleDateString('ko-KR')}
                      </div>
                      <div>
                        <span className="font-medium">데이터 소스:</span> {report.data_source.length}개
                      </div>
                      <div>
                        <span className="font-medium">차트:</span> {report.chart_config.length}개
                      </div>
                    </div>
                    
                    {report.schedule && (
                      <div className="mt-2 text-sm text-gray-500">
                        <span className="font-medium">스케줄:</span> {report.schedule}
                      </div>
                    )}
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handlePreview(report)}
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEdit(report)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleExport(report, 'pdf')}
                    >
                      <Download className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDelete(report)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
            
            {filteredReports.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <FileText className="h-12 w-12 mx-auto mb-2" />
                <p>보고서가 없습니다.</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* 보고서 생성/수정 다이얼로그 */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {editingReport ? '보고서 수정' : '새 보고서 생성'}
            </DialogTitle>
            <DialogDescription>
              {editingReport ? '보고서 정보를 수정하세요.' : '새로운 보고서를 생성하세요.'}
            </DialogDescription>
          </DialogHeader>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="title">보고서 제목 *</Label>
                <Input
                  id="title"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  required
                />
              </div>
              
              <div>
                <Label htmlFor="type">보고서 타입 *</Label>
                <Select value={formData.type} onValueChange={(value: any) => setFormData({ ...formData, type: value })}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="sales">매출 보고서</SelectItem>
                    <SelectItem value="inventory">재고 보고서</SelectItem>
                    <SelectItem value="customer">고객 보고서</SelectItem>
                    <SelectItem value="employee">직원 보고서</SelectItem>
                    <SelectItem value="financial">재무 보고서</SelectItem>
                    <SelectItem value="quality">품질 보고서</SelectItem>
                    <SelectItem value="marketing">마케팅 보고서</SelectItem>
                    <SelectItem value="comprehensive">종합 보고서</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div>
              <Label htmlFor="description">보고서 설명 *</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
                required
              />
            </div>
            
            <div>
              <Label htmlFor="schedule">자동 생성 스케줄</Label>
              <Input
                id="schedule"
                value={formData.schedule}
                onChange={(e) => setFormData({ ...formData, schedule: e.target.value })}
                placeholder="예: 매일, 매주 월요일, 매월 1일"
              />
            </div>
            
            <div>
              <Label htmlFor="recipients">수신자 (쉼표로 구분)</Label>
              <Input
                id="recipients"
                value={formData.recipients?.join(', ') || ''}
                onChange={(e) => setFormData({ ...formData, recipients: e.target.value.split(',').map(s => s.trim()) })}
                placeholder="email1@example.com, email2@example.com"
              />
            </div>
            
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                취소
              </Button>
              <Button type="submit" disabled={isLoading}>
                {isLoading ? '처리 중...' : (editingReport ? '수정' : '생성')}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* 보고서 미리보기 다이얼로그 */}
      <Dialog open={isPreviewDialogOpen} onOpenChange={setIsPreviewDialogOpen}>
        <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>보고서 미리보기</DialogTitle>
            <DialogDescription>
              {previewingReport?.title} 보고서의 미리보기입니다.
            </DialogDescription>
          </DialogHeader>
          
          {previewingReport && (
            <div className="space-y-6">
              {/* 보고서 헤더 */}
              <div className="text-center border-b pb-4">
                <h2 className="text-2xl font-bold text-gray-900">{previewingReport.title}</h2>
                <p className="text-gray-600 mt-2">{previewingReport.description}</p>
                <div className="flex justify-center space-x-4 mt-4 text-sm text-gray-500">
                  <span>생성일: {new Date(previewingReport.created_at).toLocaleDateString('ko-KR')}</span>
                  <span>생성자: {previewingReport.created_by}</span>
                  <span>타입: {previewingReport.type}</span>
                </div>
              </div>

              {/* 샘플 차트들 */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* 매출 트렌드 차트 */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">매출 트렌드</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <RechartsLineChart data={salesData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="revenue" stroke="#3B82F6" strokeWidth={2} />
                      </RechartsLineChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                {/* 재고 분포 차트 */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">재고 분포</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <RechartsPieChart>
                        <Pie
                          data={inventoryData}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {inventoryData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={chartColors[index % chartColors.length]} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </RechartsPieChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                {/* 고객 세그먼트 차트 */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">고객 세그먼트</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <RechartsBarChart data={customerData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="segment" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="count" fill="#10B981" />
                      </RechartsBarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                {/* 매출 영역 차트 */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">매출 영역</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <AreaChart data={salesData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Area type="monotone" dataKey="revenue" stackId="1" stroke="#8B5CF6" fill="#8B5CF6" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>

              {/* 액션 버튼들 */}
              <div className="flex justify-center space-x-4 pt-4 border-t">
                <Button onClick={() => handleExport(previewingReport, 'pdf')}>
                  <DownloadIcon className="h-4 w-4 mr-2" />
                  PDF 다운로드
                </Button>
                <Button variant="outline" onClick={() => handleExport(previewingReport, 'excel')}>
                  <DownloadIcon className="h-4 w-4 mr-2" />
                  Excel 다운로드
                </Button>
                <Button variant="outline" onClick={() => handleExport(previewingReport, 'csv')}>
                  <DownloadIcon className="h-4 w-4 mr-2" />
                  CSV 다운로드
                </Button>
                <Button variant="outline">
                  <Share2 className="h-4 w-4 mr-2" />
                  공유
                </Button>
                <Button variant="outline">
                  <Printer className="h-4 w-4 mr-2" />
                  인쇄
                </Button>
              </div>
            </div>
          )}
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsPreviewDialogOpen(false)}>
              닫기
            </Button>
            {previewingReport && (
              <Button onClick={() => {
                setIsPreviewDialogOpen(false);
                handleEdit(previewingReport);
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
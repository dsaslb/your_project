'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { 
  Building2, 
  Plus, 
  Edit, 
  Trash2, 
  Search, 
  RefreshCw,
  Wifi,
  AlertTriangle,
  CheckCircle,
  XCircle
} from 'lucide-react';
import { toast } from 'sonner';
import { apiClient } from '@/lib/api-client';
import { OfflineStorage } from '@/utils/offlineStorage';
import { useLoadingState } from '@/hooks/useLoadingState';
import { useErrorHandler } from '@/hooks/useErrorHandler';

interface Industry {
  id: number;
  name: string;
  code: string;
  description?: string;
  brand_count: number;
  status?: 'active' | 'inactive';
  created_at?: string;
  updated_at?: string;
}

interface Brand {
  id: number;
  name: string;
  code: string;
  description?: string;
  industry_id: number;
  industry_name?: string;
  store_count: number;
  employee_count: number;
  status?: 'active' | 'inactive';
  created_at?: string;
  updated_at?: string;
}

interface IndustryFormData {
  name: string;
  code: string;
  description: string;
}

interface BrandFormData {
  name: string;
  code: string;
  description: string;
  industry_id: number;
}

export default function IndustryManagement() {
  const [industries, setIndustries] = useState<Industry[]>([]);
  const [filteredIndustries, setFilteredIndustries] = useState<Industry[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isOffline, setIsOffline] = useState(false);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isCreateBrandDialogOpen, setIsCreateBrandDialogOpen] = useState(false);
  const [editingIndustry, setEditingIndustry] = useState<Industry | null>(null);
  const [selectedIndustry, setSelectedIndustry] = useState<Industry | null>(null);
  const [formData, setFormData] = useState<IndustryFormData>({
    name: '',
    code: '',
    description: ''
  });
  const [brandFormData, setBrandFormData] = useState<BrandFormData>({
    name: '',
    code: '',
    description: '',
    industry_id: 0
  });

  const { isLoading, setLoading } = useLoadingState();
  const { handleError } = useErrorHandler();

  // 데이터 로드
  const loadIndustries = async () => {
    try {
      setLoading(true);
      
      // 온라인 모드: 백엔드 API 호출
      try {
        const response = await apiClient.getIndustries();
        if (response.success) {
          setIndustries(response.data);
          setIsOffline(false);
          return;
        }
      } catch (apiError: any) {
        console.log('🌐 백엔드 연결 실패, 오프라인 모드로 처리:', apiError);
      }
      
      // 오프라인 모드: 로컬 데이터 로드
      const offlineIndustries = OfflineStorage.loadIndustries();
      setIndustries(offlineIndustries);
      setIsOffline(true);
      
    } catch (error: any) {
      handleError(error);
    } finally {
      setLoading(false);
    }
  };

  // 검색 필터링
  useEffect(() => {
    const filtered = industries.filter(industry =>
      industry.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      industry.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (industry.description && industry.description.toLowerCase().includes(searchTerm.toLowerCase()))
    );
    setFilteredIndustries(filtered);
  }, [industries, searchTerm]);

  // 초기 데이터 로드
  useEffect(() => {
    loadIndustries();
  }, []);

  // 폼 리셋
  const resetForm = () => {
    setFormData({
      name: '',
      code: '',
      description: ''
    });
  };

  const resetBrandForm = () => {
    setBrandFormData({
      name: '',
      code: '',
      description: '',
      industry_id: 0
    });
  };

  // 입력 변경 처리
  const handleInputChange = (field: keyof IndustryFormData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleBrandInputChange = (field: keyof BrandFormData, value: string | number) => {
    setBrandFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // 브랜드 생성 다이얼로그 열기
  const handleCreateBrand = (industry: Industry) => {
    setSelectedIndustry(industry);
    setBrandFormData(prev => ({
      ...prev,
      industry_id: industry.id
    }));
    setIsCreateBrandDialogOpen(true);
  };

  // 브랜드 생성 처리
  const handleCreateBrandSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!brandFormData.name.trim() || !brandFormData.code.trim()) {
      toast.error('브랜드명과 코드는 필수 입력 항목입니다.');
      return;
    }

    try {
      setLoading(true);
      
      // 온라인 모드: 백엔드 API 호출
      try {
        const response = await apiClient.createBrand({
          name: brandFormData.name.trim(),
          code: brandFormData.code.trim().toUpperCase(),
          description: brandFormData.description.trim(),
          industry_id: brandFormData.industry_id
        });
        
        if (response.success) {
          toast.success('브랜드가 성공적으로 생성되었습니다.');
          setIsCreateBrandDialogOpen(false);
          resetBrandForm();
          loadIndustries();
          return;
        }
      } catch (apiError: any) {
        console.log('🌐 백엔드 연결 실패, 오프라인 모드로 처리:', apiError);
        
        // 오프라인 모드: 로컬 데이터 생성
        const newBrand = {
          id: Date.now(),
          name: brandFormData.name.trim(),
          code: brandFormData.code.trim().toUpperCase(),
          description: brandFormData.description.trim(),
          industry_id: brandFormData.industry_id,
          industry_name: selectedIndustry?.name || '',
          store_count: 0,
          employee_count: 0,
          status: 'active' as const,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };
        
        // 로컬 브랜드 데이터 저장 (OfflineStorage에 브랜드 저장 기능 필요)
        toast.success('브랜드가 오프라인 모드에서 생성되었습니다. (네트워크 연결 시 동기화됩니다)');
        setIsCreateBrandDialogOpen(false);
        resetBrandForm();
        loadIndustries();
      }
      
    } catch (error: any) {
      toast.error(error.message || '브랜드 생성 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 업종 생성
  const handleCreateIndustry = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name.trim() || !formData.code.trim()) {
      toast.error('업종명과 코드는 필수 입력 항목입니다.');
      return;
    }

    try {
      setLoading(true);
      
      // 온라인 모드: 백엔드 API 호출
      try {
        const response = await apiClient.createIndustry({
          name: formData.name.trim(),
          code: formData.code.trim().toUpperCase(),
          description: formData.description.trim()
        });
        
        if (response.success) {
          toast.success('업종이 성공적으로 생성되었습니다.');
          setIsCreateDialogOpen(false);
          resetForm();
          loadIndustries();
          return;
        }
      } catch (apiError: any) {
        console.log('🌐 백엔드 연결 실패, 오프라인 모드로 처리:', apiError);
        
        // 오프라인 모드: 로컬 데이터 생성
        const newIndustry = {
          id: Date.now(),
          name: formData.name.trim(),
          code: formData.code.trim().toUpperCase(),
          description: formData.description.trim(),
          brand_count: 0,
          status: 'active' as const,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };
        
        const existingIndustries = OfflineStorage.loadIndustries();
        const updatedIndustries = [...existingIndustries, newIndustry];
        OfflineStorage.saveIndustries(updatedIndustries);
        
        toast.success('업종이 오프라인 모드에서 생성되었습니다. (네트워크 연결 시 동기화됩니다)');
        setIsCreateDialogOpen(false);
        resetForm();
        loadIndustries();
      }
      
    } catch (error: any) {
      toast.error(error.message || '업종 생성 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 업종 수정
  const handleEditIndustry = (industry: Industry) => {
    setEditingIndustry(industry);
    setFormData({
      name: industry.name,
      code: industry.code,
      description: industry.description || ''
    });
    setIsEditDialogOpen(true);
  };

  // 업종 수정 저장
  const handleUpdateIndustry = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!editingIndustry || !formData.name.trim() || !formData.code.trim()) {
      toast.error('업종명과 코드는 필수 입력 항목입니다.');
      return;
    }

    try {
      setLoading(true);
      
      // 온라인 모드: 백엔드 API 호출
      try {
        const response = await apiClient.updateIndustry(editingIndustry.id, {
          name: formData.name.trim(),
          code: formData.code.trim().toUpperCase(),
          description: formData.description.trim()
        });
        
        if (response.success) {
          toast.success('업종이 성공적으로 수정되었습니다.');
          setIsEditDialogOpen(false);
          setEditingIndustry(null);
          resetForm();
          loadIndustries();
          return;
        }
      } catch (apiError: any) {
        console.log('🌐 백엔드 연결 실패, 오프라인 모드로 처리:', apiError);
        
        // 오프라인 모드: 로컬 데이터 수정
        const existingIndustries = OfflineStorage.loadIndustries();
        const updatedIndustries = existingIndustries.map(industry =>
          industry.id === editingIndustry.id
            ? {
                ...industry,
                name: formData.name.trim(),
                code: formData.code.trim().toUpperCase(),
                description: formData.description.trim(),
                updated_at: new Date().toISOString()
              }
            : industry
        );
        OfflineStorage.saveIndustries(updatedIndustries);
        
        toast.success('업종이 오프라인 모드에서 수정되었습니다. (네트워크 연결 시 동기화됩니다)');
        setIsEditDialogOpen(false);
        setEditingIndustry(null);
        resetForm();
        loadIndustries();
      }
      
    } catch (error: any) {
      toast.error(error.message || '업종 수정 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 업종 삭제
  const handleDeleteIndustry = async (industry: Industry) => {
    if (!confirm(`정말로 "${industry.name}" 업종을 삭제하시겠습니까?`)) {
      return;
    }

    try {
      setLoading(true);
      
      // 온라인 모드: 백엔드 API 호출
      try {
        const response = await apiClient.deleteIndustry(industry.id);
        if (response.success) {
          toast.success('업종이 성공적으로 삭제되었습니다.');
          loadIndustries();
          return;
        }
      } catch (apiError: any) {
        console.log('🌐 백엔드 연결 실패, 오프라인 모드로 처리:', apiError);
        
        // 오프라인 모드: 로컬 데이터 삭제
        const existingIndustries = OfflineStorage.loadIndustries();
        const updatedIndustries = existingIndustries.filter(item => item.id !== industry.id);
        OfflineStorage.saveIndustries(updatedIndustries);
        
        toast.success('업종이 오프라인 모드에서 삭제되었습니다. (네트워크 연결 시 동기화됩니다)');
        loadIndustries();
      }
      
    } catch (error: any) {
      toast.error(error.message || '업종 삭제 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* 헤더 */}
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400 bg-clip-text text-transparent quantum-pulse">
                업종 관리
              </h1>
              {isOffline && (
                <Badge variant="secondary" className="bg-yellow-900/50 text-yellow-300 border-yellow-600/30 quantum-glass quantum-neon">
                  <Wifi className="w-3 h-3 mr-1" />
                  오프라인 모드
                </Badge>
              )}
            </div>
            <p className="text-slate-300 text-lg">업종별 브랜드 및 매장 현황 관리</p>
          </div>
          <div className="flex items-center gap-4">
            <Button
              onClick={loadIndustries}
              variant="outline"
              className="border-cyan-600/50 text-cyan-400 hover:bg-cyan-600/20 hover:border-cyan-500 quantum-glass quantum-hover"
              disabled={isLoading}
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              새로고침
            </Button>
            <Button
              onClick={() => {
                resetForm();
                setIsCreateDialogOpen(true);
              }}
              className="bg-gradient-to-r from-purple-600 via-pink-600 to-cyan-600 hover:from-purple-700 hover:via-pink-700 hover:to-cyan-700 text-white font-bold px-6 py-3 rounded-xl shadow-2xl hover:shadow-purple-500/25 transition-all duration-300 quantum-hover quantum-neon"
            >
              <Plus className="w-5 h-5 mr-2" />
              새 업종 생성
            </Button>
          </div>
        </div>

        {/* 검색 및 필터 */}
        <Card className="bg-slate-800/50 border-cyan-500/30 quantum-glass">
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
                <Input
                  placeholder="업종명, 코드, 설명으로 검색..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 text-white bg-slate-700/50 border-cyan-500/50 focus:ring-cyan-500 focus:border-cyan-500 quantum-glass quantum-hover"
                />
              </div>
              <Badge variant="secondary" className="bg-slate-700/50 text-slate-300 border-slate-600/50">
                총 {filteredIndustries.length}개 업종
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* 업종 목록 */}
        <Card className="bg-slate-800/50 border-cyan-500/30 quantum-glass">
          <CardHeader>
            <CardTitle className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400">
              업종 목록
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <RefreshCw className="w-8 h-8 animate-spin text-cyan-400" />
                <span className="ml-3 text-slate-300">데이터를 불러오는 중...</span>
              </div>
            ) : filteredIndustries.length === 0 ? (
              <div className="text-center py-12">
                <Building2 className="w-16 h-16 mx-auto text-slate-600 mb-4" />
                <h3 className="text-xl font-semibold text-slate-300 mb-2">업종이 없습니다</h3>
                <p className="text-slate-400 mb-6">새로운 업종을 생성하여 시작하세요</p>
                <Button
                  onClick={() => setIsCreateDialogOpen(true)}
                  className="bg-gradient-to-r from-purple-600 to-cyan-600 hover:from-purple-700 hover:to-cyan-700 quantum-hover"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  첫 업종 생성
                </Button>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow className="border-slate-700/50">
                      <TableHead className="text-slate-300 font-semibold">업종명</TableHead>
                      <TableHead className="text-slate-300 font-semibold">코드</TableHead>
                      <TableHead className="text-slate-300 font-semibold">설명</TableHead>
                      <TableHead className="text-slate-300 font-semibold">브랜드 수</TableHead>
                      <TableHead className="text-slate-300 font-semibold">상태</TableHead>
                      <TableHead className="text-slate-300 font-semibold">생성일</TableHead>
                      <TableHead className="text-slate-300 font-semibold">작업</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredIndustries.map((industry) => (
                      <TableRow key={industry.id} className="border-slate-700/30 hover:bg-slate-700/30 transition-colors">
                        <TableCell className="text-white font-medium">{industry.name}</TableCell>
                        <TableCell>
                          <Badge variant="outline" className="border-cyan-500/50 text-cyan-400 bg-cyan-500/10">
                            {industry.code}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-slate-300 max-w-xs truncate">
                          {industry.description || '-'}
                        </TableCell>
                        <TableCell>
                          <Badge variant="secondary" className="bg-purple-900/50 text-purple-300 border-purple-600/30">
                            {industry.brand_count}개
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {industry.status === 'active' ? (
                            <Badge className="bg-green-900/50 text-green-300 border-green-600/30">
                              <CheckCircle className="w-3 h-3 mr-1" />
                              활성
                            </Badge>
                          ) : (
                            <Badge className="bg-red-900/50 text-red-300 border-red-600/30">
                              <XCircle className="w-3 h-3 mr-1" />
                              비활성
                            </Badge>
                          )}
                        </TableCell>
                        <TableCell className="text-slate-400 text-sm">
                          {industry.created_at ? new Date(industry.created_at).toLocaleDateString('ko-KR') : '-'}
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Button
                              onClick={() => handleCreateBrand(industry)}
                              variant="outline"
                              size="sm"
                              className="border-green-600/50 text-green-400 hover:bg-green-600/20 hover:border-green-500 quantum-glass quantum-hover"
                            >
                              <Plus className="w-3 h-3" />
                            </Button>
                            <Button
                              onClick={() => handleEditIndustry(industry)}
                              variant="outline"
                              size="sm"
                              className="border-blue-600/50 text-blue-400 hover:bg-blue-600/20 hover:border-blue-500 quantum-glass quantum-hover"
                            >
                              <Edit className="w-3 h-3" />
                            </Button>
                            <Button
                              onClick={() => handleDeleteIndustry(industry)}
                              variant="outline"
                              size="sm"
                              className="border-red-600/50 text-red-400 hover:bg-red-600/20 hover:border-red-500 quantum-glass quantum-hover"
                            >
                              <Trash2 className="w-3 h-3" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* 업종 생성 다이얼로그 */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="bg-slate-800/95 border-purple-500/50 text-white max-w-md mx-auto backdrop-blur-xl quantum-glass quantum-neon">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400 quantum-pulse">
              새 업종 생성
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleCreateIndustry}>
            <div className="grid gap-6 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="name" className="text-right text-slate-300 font-medium">
                  업종명
                </Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  className="col-span-3 text-white bg-slate-700/50 border-purple-500/50 focus:ring-purple-500 focus:border-purple-500 quantum-glass quantum-hover"
                  placeholder="예: 음식점, 카페, 쇼핑몰"
                  required
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="code" className="text-right text-slate-300 font-medium">
                  코드
                </Label>
                <Input
                  id="code"
                  value={formData.code}
                  onChange={(e) => handleInputChange('code', e.target.value)}
                  className="col-span-3 text-white bg-slate-700/50 border-purple-500/50 focus:ring-purple-500 focus:border-purple-500 quantum-glass quantum-hover"
                  placeholder="예: FOOD, SHOPPING, SERVICE"
                  required
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="description" className="text-right text-slate-300 font-medium">
                  설명
                </Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  className="col-span-3 text-white bg-slate-700/50 border-purple-500/50 focus:ring-purple-500 focus:border-purple-500 quantum-glass quantum-hover"
                  placeholder="업종에 대한 간단한 설명"
                />
              </div>
            </div>
            <div className="flex justify-end space-x-3 pt-6">
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsCreateDialogOpen(false)}
                className="border-slate-600/50 text-slate-300 hover:border-slate-500 hover:text-slate-200 quantum-glass quantum-hover"
              >
                취소
              </Button>
              <Button
                type="submit"
                className="bg-gradient-to-r from-purple-600 to-cyan-600 hover:from-purple-700 hover:to-cyan-700 quantum-hover quantum-neon font-bold"
                disabled={isLoading}
              >
                {isLoading ? '생성 중...' : '업종 생성'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* 업종 수정 다이얼로그 */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="bg-slate-800/95 border-blue-500/50 text-white max-w-md mx-auto backdrop-blur-xl quantum-glass quantum-neon">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400 quantum-pulse">
              업종 수정
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleUpdateIndustry}>
            <div className="grid gap-6 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="edit-name" className="text-right text-slate-300 font-medium">
                  업종명
                </Label>
                <Input
                  id="edit-name"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  className="col-span-3 text-white bg-slate-700/50 border-blue-500/50 focus:ring-blue-500 focus:border-blue-500 quantum-glass quantum-hover"
                  placeholder="예: 음식점, 카페, 쇼핑몰"
                  required
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="edit-code" className="text-right text-slate-300 font-medium">
                  코드
                </Label>
                <Input
                  id="edit-code"
                  value={formData.code}
                  onChange={(e) => handleInputChange('code', e.target.value)}
                  className="col-span-3 text-white bg-slate-700/50 border-blue-500/50 focus:ring-blue-500 focus:border-blue-500 quantum-glass quantum-hover"
                  placeholder="예: FOOD, SHOPPING, SERVICE"
                  required
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="edit-description" className="text-right text-slate-300 font-medium">
                  설명
                </Label>
                <Textarea
                  id="edit-description"
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  className="col-span-3 text-white bg-slate-700/50 border-blue-500/50 focus:ring-blue-500 focus:border-blue-500 quantum-glass quantum-hover"
                  placeholder="업종에 대한 간단한 설명"
                />
              </div>
            </div>
            <div className="flex justify-end space-x-3 pt-6">
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsEditDialogOpen(false)}
                className="border-slate-600/50 text-slate-300 hover:border-slate-500 hover:text-slate-200 quantum-glass quantum-hover"
              >
                취소
              </Button>
              <Button
                type="submit"
                className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 quantum-hover quantum-neon font-bold"
                disabled={isLoading}
              >
                {isLoading ? '수정 중...' : '업종 수정'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* 브랜드 생성 다이얼로그 */}
      <Dialog open={isCreateBrandDialogOpen} onOpenChange={setIsCreateBrandDialogOpen}>
        <DialogContent className="bg-slate-800/95 border-green-500/50 text-white max-w-md mx-auto backdrop-blur-xl quantum-glass quantum-neon">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-cyan-400 quantum-pulse">
              새 브랜드 생성
            </DialogTitle>
            <p className="text-slate-400 text-sm">
              업종: {selectedIndustry?.name} ({selectedIndustry?.code})
            </p>
          </DialogHeader>
          <form onSubmit={handleCreateBrandSubmit}>
            <div className="grid gap-6 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="brand-name" className="text-right text-slate-300 font-medium">
                  브랜드명
                </Label>
                <Input
                  id="brand-name"
                  value={brandFormData.name}
                  onChange={(e) => handleBrandInputChange('name', e.target.value)}
                  className="col-span-3 text-white bg-slate-700/50 border-green-500/50 focus:ring-green-500 focus:border-green-500 quantum-glass quantum-hover"
                  placeholder="예: 스타벅스, 맥도날드"
                  required
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="brand-code" className="text-right text-slate-300 font-medium">
                  코드
                </Label>
                <Input
                  id="brand-code"
                  value={brandFormData.code}
                  onChange={(e) => handleBrandInputChange('code', e.target.value)}
                  className="col-span-3 text-white bg-slate-700/50 border-green-500/50 focus:ring-green-500 focus:border-green-500 quantum-glass quantum-hover"
                  placeholder="예: STARBUCKS, MCDONALDS"
                  required
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="brand-description" className="text-right text-slate-300 font-medium">
                  설명
                </Label>
                <Textarea
                  id="brand-description"
                  value={brandFormData.description}
                  onChange={(e) => handleBrandInputChange('description', e.target.value)}
                  className="col-span-3 text-white bg-slate-700/50 border-green-500/50 focus:ring-green-500 focus:border-green-500 quantum-glass quantum-hover"
                  placeholder="브랜드에 대한 간단한 설명"
                />
              </div>
            </div>
            <div className="flex justify-end space-x-3 pt-6">
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsCreateBrandDialogOpen(false)}
                className="border-slate-600/50 text-slate-300 hover:border-slate-500 hover:text-slate-200 quantum-glass quantum-hover"
              >
                취소
              </Button>
              <Button
                type="submit"
                className="bg-gradient-to-r from-green-600 to-cyan-600 hover:from-green-700 hover:to-cyan-700 quantum-hover quantum-neon font-bold"
                disabled={isLoading}
              >
                {isLoading ? '생성 중...' : '브랜드 생성'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
} 
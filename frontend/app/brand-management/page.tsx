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
  Store, 
  Plus, 
  Edit, 
  Trash2, 
  Search, 
  RefreshCw,
  Wifi,
  CheckCircle,
  XCircle,
  MapPin,
  Phone,
  User,
  Building2,
  Settings
} from 'lucide-react';
import { toast } from 'sonner';
import { apiClient } from '@/lib/api-client';
import { OfflineStorage } from '@/utils/offlineStorage';
import { useLoadingState } from '@/hooks/useLoadingState';
import { useErrorHandler } from '@/hooks/useErrorHandler';

interface Brand {
  id: number;
  name: string;
  code: string;
  description?: string;
  industry_id?: number;
  industry_name?: string;
  store_count: number;
  employee_count: number;
  status?: 'active' | 'inactive' | 'pending';
  created_at?: string;
  updated_at?: string;
}

interface Store {
  id: number;
  name: string;
  code: string;
  address?: string;
  phone?: string;
  manager_name?: string;
  brand_id: number;
  brand_name?: string;
  employee_count: number;
  status: 'active' | 'inactive';
  created_at?: string;
  updated_at?: string;
}

interface BrandFormData {
  name: string;
  code: string;
  description: string;
  industry_id: number | undefined;
}

interface StoreFormData {
  name: string;
  code: string;
  address: string;
  phone: string;
  manager_name: string;
  brand_id: number;
}

export default function BrandManagement() {
  const [brands, setBrands] = useState<Brand[]>([]);
  const [filteredBrands, setFilteredBrands] = useState<Brand[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isOffline, setIsOffline] = useState(false);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isCreateStoreDialogOpen, setIsCreateStoreDialogOpen] = useState(false);
  const [isStoreManagementOpen, setIsStoreManagementOpen] = useState(false);
  const [editingBrand, setEditingBrand] = useState<Brand | null>(null);
  const [selectedBrand, setSelectedBrand] = useState<Brand | null>(null);
  const [stores, setStores] = useState<Store[]>([]);
  const [formData, setFormData] = useState<BrandFormData>({
    name: '',
    code: '',
    description: '',
    industry_id: 0
  });
  const [storeFormData, setStoreFormData] = useState<StoreFormData>({
    name: '',
    code: '',
    address: '',
    phone: '',
    manager_name: '',
    brand_id: 0
  });

  const { isLoading, setLoading } = useLoadingState();
  const { handleError } = useErrorHandler();

  // 데이터 로드
  const loadBrands = async () => {
    try {
      setLoading(true);
      
      // 온라인 모드: 백엔드 API 호출
      try {
        const response = await apiClient.getBrands();
        if (response.success) {
          setBrands(response.data);
          setIsOffline(false);
          return;
        }
      } catch (apiError: any) {
        console.log('🌐 백엔드 연결 실패, 오프라인 모드로 처리:', apiError);
      }
      
      // 오프라인 모드: 로컬 데이터 로드
      const offlineBrands = OfflineStorage.loadBrands();
      setBrands(offlineBrands);
      setIsOffline(true);
      
    } catch (error: any) {
      handleError(error);
    } finally {
      setLoading(false);
    }
  };

  // 매장 목록 로드
  const loadStores = async (brandId?: number) => {
    try {
      setLoading(true);
      
      // 온라인 모드: 백엔드 API 호출
      try {
        const url = brandId ? `/api/admin/branches?brand_id=${brandId}` : '/api/admin/branches';
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.success) {
          setStores(data.data || []);
          setIsOffline(false);
          return;
        }
      } catch (apiError: any) {
        console.log('🌐 백엔드 연결 실패, 오프라인 모드로 처리:', apiError);
      }
      
      // 오프라인 모드: 로컬 데이터 로드
      const offlineStores = OfflineStorage.loadStores();
      if (brandId) {
        const filteredStores = offlineStores.filter(store => store.brand_id === brandId);
        setStores(filteredStores);
      } else {
        setStores(offlineStores);
      }
      setIsOffline(true);
      
    } catch (error: any) {
      handleError(error);
    } finally {
      setLoading(false);
    }
  };

  // 검색 필터링
  useEffect(() => {
    const filtered = brands.filter(brand =>
      brand.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      brand.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (brand.description && brand.description.toLowerCase().includes(searchTerm.toLowerCase()))
    );
    setFilteredBrands(filtered);
  }, [brands, searchTerm]);

  // 초기 데이터 로드
  useEffect(() => {
    loadBrands();
  }, []);

  // 폼 리셋
  const resetForm = () => {
    setFormData({
      name: '',
      code: '',
      description: '',
      industry_id: 0
    });
  };

  const resetStoreForm = () => {
    setStoreFormData({
      name: '',
      code: '',
      address: '',
      phone: '',
      manager_name: '',
      brand_id: 0
    });
  };

  // 입력 변경 처리
  const handleInputChange = (field: keyof BrandFormData, value: string | number) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleStoreInputChange = (field: keyof StoreFormData, value: string | number) => {
    setStoreFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // 매장 관리 다이얼로그 열기
  const handleStoreManagement = (brand: Brand) => {
    setSelectedBrand(brand);
    loadStores(brand.id);
    setIsStoreManagementOpen(true);
  };

  // 매장 생성 다이얼로그 열기
  const handleCreateStore = (brand: Brand) => {
    setSelectedBrand(brand);
    setStoreFormData(prev => ({
      ...prev,
      brand_id: brand.id
    }));
    setIsCreateStoreDialogOpen(true);
  };

  // 매장 생성 처리
  const handleCreateStoreSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!storeFormData.name.trim() || !storeFormData.code.trim()) {
      toast.error('매장명과 코드는 필수 입력 항목입니다.');
      return;
    }

    try {
      setLoading(true);
      
      // 온라인 모드: 백엔드 API 호출
      try {
        const response = await fetch('/api/admin/branches', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            name: storeFormData.name.trim(),
            store_code: storeFormData.code.trim().toUpperCase(),
            address: storeFormData.address.trim(),
            phone: storeFormData.phone.trim(),
            brand_id: storeFormData.brand_id
          })
        });
        
        const data = await response.json();
        
        if (data.success) {
          toast.success('매장이 성공적으로 생성되었습니다.');
          setIsCreateStoreDialogOpen(false);
          resetStoreForm();
          loadBrands();
          if (isStoreManagementOpen) {
            loadStores(selectedBrand?.id);
          }
          return;
        } else {
          throw new Error(data.error || '매장 생성에 실패했습니다.');
        }
      } catch (apiError: any) {
        console.log('🌐 백엔드 연결 실패, 오프라인 모드로 처리:', apiError);
        
        // 오프라인 모드: 로컬 데이터 생성
        const newStore = {
          id: Date.now(),
          name: storeFormData.name.trim(),
          code: storeFormData.code.trim().toUpperCase(),
          address: storeFormData.address.trim(),
          phone: storeFormData.phone.trim(),
          manager_name: storeFormData.manager_name.trim(),
          brand_id: storeFormData.brand_id,
          brand_name: selectedBrand?.name || '',
          employee_count: 0,
          status: 'active' as const,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };
        
        // 로컬 매장 데이터 저장
        const existingStores = OfflineStorage.loadStores();
        const updatedStores = [...existingStores, newStore];
        OfflineStorage.saveStores(updatedStores);
        
        toast.success('매장이 오프라인 모드에서 생성되었습니다. (네트워크 연결 시 동기화됩니다)');
        setIsCreateStoreDialogOpen(false);
        resetStoreForm();
        loadBrands();
        if (isStoreManagementOpen) {
          loadStores(selectedBrand?.id);
        }
      }
      
    } catch (error: any) {
      toast.error(error.message || '매장 생성 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 브랜드 편집 다이얼로그 열기
  const handleEditBrand = (brand: Brand) => {
    setEditingBrand(brand);
    setFormData({
      name: brand.name,
      code: brand.code,
      description: brand.description || '',
      industry_id: brand.industry_id
    });
    setIsEditDialogOpen(true);
  };

  // 브랜드 삭제 처리
  const handleDeleteBrand = async (brand: Brand) => {
    if (!confirm(`정말로 "${brand.name}" 브랜드를 삭제하시겠습니까?`)) {
      return;
    }

    try {
      setLoading(true);
      
      // 온라인 모드: 백엔드 API 호출
      try {
        const response = await apiClient.deleteBrand(brand.id);
        if (response.success) {
          toast.success('브랜드가 성공적으로 삭제되었습니다.');
          loadBrands();
          return;
        }
      } catch (apiError: any) {
        console.log('🌐 백엔드 연결 실패, 오프라인 모드로 처리:', apiError);
      }
      
      // 오프라인 모드: 로컬 데이터 삭제
      const updatedBrands = brands.filter(b => b.id !== brand.id);
      setBrands(updatedBrands);
      OfflineStorage.saveBrands(updatedBrands);
      toast.success('브랜드가 오프라인 모드에서 삭제되었습니다.');
      
    } catch (error: any) {
      toast.error(error.message || '브랜드 삭제 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 브랜드 생성/수정 처리
  const handleBrandSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name.trim() || !formData.code.trim()) {
      toast.error('브랜드명과 코드는 필수 입력 항목입니다.');
      return;
    }

    try {
      setLoading(true);
      
      if (editingBrand) {
        // 수정
        try {
          const response = await apiClient.updateBrand(editingBrand.id, {
            name: formData.name.trim(),
            code: formData.code.trim().toUpperCase(),
            description: formData.description.trim()
          });
          
          if (response.success) {
            toast.success('브랜드가 성공적으로 수정되었습니다.');
            setIsEditDialogOpen(false);
            resetForm();
            loadBrands();
            return;
          }
        } catch (apiError: any) {
          console.log('🌐 백엔드 연결 실패, 오프라인 모드로 처리:', apiError);
        }
        
        // 오프라인 모드: 로컬 데이터 수정
        const updatedBrands = brands.map(brand => 
          brand.id === editingBrand.id 
            ? { ...brand, ...formData, updated_at: new Date().toISOString() }
            : brand
        );
        
        setBrands(updatedBrands);
        OfflineStorage.saveBrands(updatedBrands);
        toast.success('브랜드가 오프라인 모드에서 수정되었습니다.');
        setIsEditDialogOpen(false);
        resetForm();
        
      } else {
        // 생성
        try {
          const response = await apiClient.createBrand({
            name: formData.name.trim(),
            code: formData.code.trim().toUpperCase(),
            description: formData.description.trim(),
            industry_id: formData.industry_id
          });
          
          if (response.success) {
            toast.success('브랜드가 성공적으로 생성되었습니다.');
            setIsCreateDialogOpen(false);
            resetForm();
            loadBrands();
            return;
          }
        } catch (apiError: any) {
          console.log('🌐 백엔드 연결 실패, 오프라인 모드로 처리:', apiError);
        }
        
        // 오프라인 모드: 로컬 데이터 생성
        const newBrand = {
          id: Date.now(),
          name: formData.name.trim(),
          code: formData.code.trim().toUpperCase(),
          description: formData.description.trim(),
          industry_id: formData.industry_id,
          store_count: 0,
          employee_count: 0,
          status: 'active' as const,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };
        
        const updatedBrands = [...brands, newBrand];
        setBrands(updatedBrands);
        OfflineStorage.saveBrands(updatedBrands);
        toast.success('브랜드가 오프라인 모드에서 생성되었습니다.');
        setIsCreateDialogOpen(false);
        resetForm();
      }
      
    } catch (error: any) {
      toast.error(error.message || '브랜드 처리 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* 헤더 */}
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 via-cyan-400 to-purple-400 bg-clip-text text-transparent quantum-pulse">
                브랜드 관리
              </h1>
              {isOffline && (
                <Badge variant="secondary" className="bg-yellow-900/50 text-yellow-300 border-yellow-600/30 quantum-glass quantum-neon">
                  <Wifi className="w-3 h-3 mr-1" />
                  오프라인 모드
                </Badge>
              )}
            </div>
            <p className="text-slate-300 text-lg">브랜드별 매장 및 직원 현황 관리</p>
          </div>
          <div className="flex items-center gap-4">
            <Button
              onClick={loadBrands}
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
              className="bg-gradient-to-r from-blue-600 via-cyan-600 to-purple-600 hover:from-blue-700 hover:via-cyan-700 hover:to-purple-700 text-white font-bold px-6 py-3 rounded-xl shadow-2xl hover:shadow-blue-500/25 transition-all duration-300 quantum-hover quantum-neon"
            >
              <Plus className="w-5 h-5 mr-2" />
              새 브랜드 생성
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
                  placeholder="브랜드명, 코드, 설명으로 검색..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 text-white bg-slate-700/50 border-cyan-500/50 focus:ring-cyan-500 focus:border-cyan-500 quantum-glass quantum-hover"
                />
              </div>
              <Badge variant="secondary" className="bg-slate-700/50 text-slate-300 border-slate-600/50">
                총 {filteredBrands.length}개 브랜드
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* 브랜드 목록 */}
        <Card className="bg-slate-800/50 border-cyan-500/30 quantum-glass">
          <CardHeader>
            <CardTitle className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400">
              브랜드 목록
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <RefreshCw className="w-8 h-8 animate-spin text-cyan-400" />
                <span className="ml-3 text-slate-300">데이터를 불러오는 중...</span>
              </div>
            ) : filteredBrands.length === 0 ? (
              <div className="text-center py-12">
                <Store className="w-16 h-16 mx-auto text-slate-600 mb-4" />
                <h3 className="text-xl font-semibold text-slate-300 mb-2">브랜드가 없습니다</h3>
                <p className="text-slate-400 mb-6">새로운 브랜드를 생성하여 시작하세요</p>
                <Button
                  onClick={() => setIsCreateDialogOpen(true)}
                  className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 quantum-hover"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  첫 브랜드 생성
                </Button>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow className="border-slate-700/50">
                      <TableHead className="text-slate-300 font-semibold">브랜드명</TableHead>
                      <TableHead className="text-slate-300 font-semibold">코드</TableHead>
                      <TableHead className="text-slate-300 font-semibold">업종</TableHead>
                      <TableHead className="text-slate-300 font-semibold">매장 수</TableHead>
                      <TableHead className="text-slate-300 font-semibold">직원 수</TableHead>
                      <TableHead className="text-slate-300 font-semibold">상태</TableHead>
                      <TableHead className="text-slate-300 font-semibold">생성일</TableHead>
                      <TableHead className="text-slate-300 font-semibold">작업</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredBrands.map((brand) => (
                      <TableRow key={brand.id} className="border-slate-700/30 hover:bg-slate-700/30 transition-colors">
                        <TableCell className="text-white font-medium">{brand.name}</TableCell>
                        <TableCell>
                          <Badge variant="outline" className="border-blue-500/50 text-blue-400 bg-blue-500/10">
                            {brand.code}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-slate-300">
                          {brand.industry_name || '-'}
                        </TableCell>
                        <TableCell>
                          <Badge variant="secondary" className="bg-green-900/50 text-green-300 border-green-600/30">
                            {brand.store_count}개
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge variant="secondary" className="bg-purple-900/50 text-purple-300 border-purple-600/30">
                            {brand.employee_count}명
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {brand.status === 'active' ? (
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
                          {brand.created_at ? new Date(brand.created_at).toLocaleDateString('ko-KR') : '-'}
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Button
                              onClick={() => handleStoreManagement(brand)}
                              variant="outline"
                              size="sm"
                              className="border-purple-600/50 text-purple-400 hover:bg-purple-600/20 hover:border-purple-500 quantum-glass quantum-hover"
                              title="매장 관리"
                            >
                              <Settings className="w-3 h-3" />
                            </Button>
                            <Button
                              onClick={() => handleCreateStore(brand)}
                              variant="outline"
                              size="sm"
                              className="border-green-600/50 text-green-400 hover:bg-green-600/20 hover:border-green-500 quantum-glass quantum-hover"
                              title="새 매장 생성"
                            >
                              <MapPin className="w-3 h-3" />
                            </Button>
                            <Button
                              onClick={() => handleEditBrand(brand)}
                              variant="outline"
                              size="sm"
                              className="border-blue-600/50 text-blue-400 hover:bg-blue-600/20 hover:border-blue-500 quantum-glass quantum-hover"
                              title="브랜드 수정"
                            >
                              <Edit className="w-3 h-3" />
                            </Button>
                            <Button
                              onClick={() => handleDeleteBrand(brand)}
                              variant="outline"
                              size="sm"
                              className="border-red-600/50 text-red-400 hover:bg-red-600/20 hover:border-red-500 quantum-glass quantum-hover"
                              title="브랜드 삭제"
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

      {/* 매장 관리 다이얼로그 */}
      <Dialog open={isStoreManagementOpen} onOpenChange={setIsStoreManagementOpen}>
        <DialogContent className="bg-slate-800/95 border-purple-500/50 text-white max-w-6xl mx-auto backdrop-blur-xl quantum-glass quantum-neon">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400 quantum-pulse">
              매장 관리
            </DialogTitle>
            <p className="text-slate-400 text-sm">
              브랜드: {selectedBrand?.name} ({selectedBrand?.code})
            </p>
          </DialogHeader>
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-white">매장 목록</h3>
              <Button
                onClick={() => handleCreateStore(selectedBrand!)}
                className="bg-gradient-to-r from-green-600 to-cyan-600 hover:from-green-700 hover:to-cyan-700 quantum-hover quantum-neon"
              >
                <Plus className="w-4 h-4 mr-2" />
                새 매장 생성
              </Button>
            </div>
            
            {isLoading ? (
              <div className="flex items-center justify-center py-8">
                <RefreshCw className="w-6 h-6 animate-spin text-cyan-400" />
                <span className="ml-2 text-slate-300">매장 목록을 불러오는 중...</span>
              </div>
            ) : stores.length === 0 ? (
              <div className="text-center py-8">
                <Store className="w-12 h-12 mx-auto text-slate-600 mb-3" />
                <h4 className="text-lg font-semibold text-slate-300 mb-2">매장이 없습니다</h4>
                <p className="text-slate-400 mb-4">새로운 매장을 생성하여 시작하세요</p>
                <Button
                  onClick={() => handleCreateStore(selectedBrand!)}
                  className="bg-gradient-to-r from-green-600 to-cyan-600 hover:from-green-700 hover:to-cyan-700 quantum-hover"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  첫 매장 생성
                </Button>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow className="border-slate-700/50">
                      <TableHead className="text-slate-300 font-semibold">매장명</TableHead>
                      <TableHead className="text-slate-300 font-semibold">코드</TableHead>
                      <TableHead className="text-slate-300 font-semibold">주소</TableHead>
                      <TableHead className="text-slate-300 font-semibold">전화번호</TableHead>
                      <TableHead className="text-slate-300 font-semibold">직원 수</TableHead>
                      <TableHead className="text-slate-300 font-semibold">상태</TableHead>
                      <TableHead className="text-slate-300 font-semibold">생성일</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {stores.map((store) => (
                      <TableRow key={store.id} className="border-slate-700/30 hover:bg-slate-700/30 transition-colors">
                        <TableCell className="text-white font-medium">{store.name}</TableCell>
                        <TableCell>
                          <Badge variant="outline" className="border-green-500/50 text-green-400 bg-green-500/10">
                            {store.code}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-slate-300">
                          {store.address || '-'}
                        </TableCell>
                        <TableCell className="text-slate-300">
                          {store.phone || '-'}
                        </TableCell>
                        <TableCell>
                          <Badge variant="secondary" className="bg-purple-900/50 text-purple-300 border-purple-600/30">
                            {store.employee_count}명
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {store.status === 'active' ? (
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
                          {store.created_at ? new Date(store.created_at).toLocaleDateString('ko-KR') : '-'}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* 매장 생성 다이얼로그 */}
      <Dialog open={isCreateStoreDialogOpen} onOpenChange={setIsCreateStoreDialogOpen}>
        <DialogContent className="bg-slate-800/95 border-green-500/50 text-white max-w-md mx-auto backdrop-blur-xl quantum-glass quantum-neon">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-cyan-400 quantum-pulse">
              새 매장 생성
            </DialogTitle>
            <p className="text-slate-400 text-sm">
              브랜드: {selectedBrand?.name} ({selectedBrand?.code})
            </p>
          </DialogHeader>
          <form onSubmit={handleCreateStoreSubmit}>
            <div className="grid gap-6 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="store-name" className="text-right text-slate-300 font-medium">
                  매장명
                </Label>
                <Input
                  id="store-name"
                  value={storeFormData.name}
                  onChange={(e) => handleStoreInputChange('name', e.target.value)}
                  className="col-span-3 text-white bg-slate-700/50 border-green-500/50 focus:ring-green-500 focus:border-green-500 quantum-glass quantum-hover"
                  placeholder="예: 강남점, 홍대점"
                  required
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="store-code" className="text-right text-slate-300 font-medium">
                  코드
                </Label>
                <Input
                  id="store-code"
                  value={storeFormData.code}
                  onChange={(e) => handleStoreInputChange('code', e.target.value)}
                  className="col-span-3 text-white bg-slate-700/50 border-green-500/50 focus:ring-green-500 focus:border-green-500 quantum-glass quantum-hover"
                  placeholder="예: GANGNAM, HONGDAE"
                  required
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="store-address" className="text-right text-slate-300 font-medium">
                  주소
                </Label>
                <Input
                  id="store-address"
                  value={storeFormData.address}
                  onChange={(e) => handleStoreInputChange('address', e.target.value)}
                  className="col-span-3 text-white bg-slate-700/50 border-green-500/50 focus:ring-green-500 focus:border-green-500 quantum-glass quantum-hover"
                  placeholder="매장 주소"
                  required
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="store-phone" className="text-right text-slate-300 font-medium">
                  전화번호
                </Label>
                <Input
                  id="store-phone"
                  value={storeFormData.phone}
                  onChange={(e) => handleStoreInputChange('phone', e.target.value)}
                  className="col-span-3 text-white bg-slate-700/50 border-green-500/50 focus:ring-green-500 focus:border-green-500 quantum-glass quantum-hover"
                  placeholder="02-1234-5678"
                  required
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="store-manager" className="text-right text-slate-300 font-medium">
                  매니저
                </Label>
                <Input
                  id="store-manager"
                  value={storeFormData.manager_name}
                  onChange={(e) => handleStoreInputChange('manager_name', e.target.value)}
                  className="col-span-3 text-white bg-slate-700/50 border-green-500/50 focus:ring-green-500 focus:border-green-500 quantum-glass quantum-hover"
                  placeholder="매장 매니저 이름"
                  required
                />
              </div>
            </div>
            <div className="flex justify-end space-x-3 pt-6">
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsCreateStoreDialogOpen(false)}
                className="border-slate-600/50 text-slate-300 hover:border-slate-500 hover:text-slate-200 quantum-glass quantum-hover"
              >
                취소
              </Button>
              <Button
                type="submit"
                className="bg-gradient-to-r from-green-600 to-cyan-600 hover:from-green-700 hover:to-cyan-700 quantum-hover quantum-neon font-bold"
                disabled={isLoading}
              >
                {isLoading ? '생성 중...' : '매장 생성'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
} 
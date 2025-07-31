'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Building2, 
  Plus, 
  Search, 
  Edit, 
  Trash2, 
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Store,
  Users,
  Phone,
  MapPin
} from 'lucide-react';
import { toast } from 'sonner';
import { apiClient, Store as StoreType, Brand } from '../../lib/api-client';
import useLoadingState from '@/hooks/useLoadingState';
import useErrorHandler from '@/hooks/useErrorHandler';

interface StoreFormData {
  name: string;
  code: string;
  address: string;
  phone: string;
  manager_name: string;
  brand_id: number;
}

export default function StoreManagement() {
  const [stores, setStores] = useState<StoreType[]>([]);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedBrand, setSelectedBrand] = useState<number | 'all'>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [editingStore, setEditingStore] = useState<StoreType | null>(null);
  const [formData, setFormData] = useState<StoreFormData>({
    name: '',
    code: '',
    address: '',
    phone: '',
    manager_name: '',
    brand_id: 0,
  });

  const { isLoading, error, withLoading } = useLoadingState();
  const { handleError } = useErrorHandler();

  // 매장 목록 조회
  const fetchStores = async () => {
    const response = await apiClient.getStores();
    if (response.success) {
      setStores(response.data);
    }
  };

  // 브랜드 목록 조회
  const fetchBrands = async () => {
    const response = await apiClient.getBrands();
    if (response.success) {
      setBrands(response.data);
    }
  };

  // 초기 데이터 로드
  useEffect(() => {
    withLoading(async () => {
      await Promise.all([fetchStores(), fetchBrands()]);
    });
  }, []);

  // 검색 및 필터링
  const filteredStores = stores.filter(store => {
    const matchesSearch = 
      store.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      store.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      store.address?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      store.manager_name?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesBrand = selectedBrand === 'all' || store.brand_id === selectedBrand;
    const matchesStatus = selectedStatus === 'all' || store.status === selectedStatus;
    
    return matchesSearch && matchesBrand && matchesStatus;
  });

  // 폼 초기화
  const resetForm = () => {
    setFormData({
      name: '',
      code: '',
      address: '',
      phone: '',
      manager_name: '',
      brand_id: 0,
    });
    setEditingStore(null);
  };

  // 폼 제출 처리
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name.trim() || !formData.code.trim() || formData.brand_id === 0) {
      toast.error('매장명, 코드, 브랜드는 필수 입력 항목입니다.');
      return;
    }

    try {
      if (editingStore) {
        // 수정
        const response = await apiClient.updateStore(editingStore.id, formData);
        if (response.success) {
          toast.success('매장이 성공적으로 수정되었습니다.');
          setIsCreateDialogOpen(false);
          resetForm();
          fetchStores();
        }
      } else {
        // 생성
        const response = await apiClient.createStore(formData);
        if (response.success) {
          toast.success('매장이 성공적으로 생성되었습니다.');
          setIsCreateDialogOpen(false);
          resetForm();
          fetchStores();
        }
      }
    } catch (error) {
      handleError(error as Error);
    }
  };

  // 매장 삭제
  const handleDelete = async (store: StoreType) => {
    if (!confirm(`"${store.name}" 매장을 삭제하시겠습니까?`)) {
      return;
    }

    try {
      const response = await apiClient.deleteStore(store.id);
      if (response.success) {
        toast.success('매장이 성공적으로 삭제되었습니다.');
        fetchStores();
      }
    } catch (error) {
      handleError(error as Error);
    }
  };

  // 수정 모드 시작
  const handleEdit = (store: StoreType) => {
    setEditingStore(store);
    setFormData({
      name: store.name,
      code: store.code,
      address: store.address || '',
      phone: store.phone || '',
      manager_name: store.manager_name || '',
      brand_id: store.brand_id,
    });
    setIsCreateDialogOpen(true);
  };

  // 통계 계산
  const stats = {
    total: stores.length,
    active: stores.filter(store => store.status === 'active').length,
    inactive: stores.filter(store => store.status === 'inactive').length,
    employees: stores.reduce((sum, store) => sum + store.employee_count, 0),
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50';
      case 'inactive': return 'bg-red-500/20 text-red-400 border-red-500/50';
      default: return 'bg-slate-500/20 text-slate-400 border-slate-500/50';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return '활성';
      case 'inactive': return '비활성';
      default: return '알 수 없음';
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <Building2 className="w-8 h-8 text-emerald-400" />
            매장별 관리
          </h1>
          <p className="text-slate-400 mt-2">매장 정보를 관리하고 직원을 조직화합니다.</p>
        </div>
        <Button
          onClick={() => {
            resetForm();
            setIsCreateDialogOpen(true);
          }}
          className="bg-gradient-to-r from-emerald-500/20 to-cyan-500/20 text-emerald-400 border-emerald-500/30 hover:from-emerald-500/30 hover:to-cyan-500/30"
        >
          <Plus className="w-4 h-4 mr-2" />
          매장 추가
        </Button>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="bg-slate-800/50 border-emerald-500/30 backdrop-blur-xl">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">총 매장</p>
                <p className="text-3xl font-bold text-emerald-400">{stats.total}</p>
              </div>
              <Building2 className="w-8 h-8 text-emerald-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 border-cyan-500/30 backdrop-blur-xl">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">활성 매장</p>
                <p className="text-3xl font-bold text-cyan-400">{stats.active}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-cyan-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 border-red-500/30 backdrop-blur-xl">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">비활성 매장</p>
                <p className="text-3xl font-bold text-red-400">{stats.inactive}</p>
              </div>
              <AlertTriangle className="w-8 h-8 text-red-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 border-yellow-500/30 backdrop-blur-xl">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">총 직원</p>
                <p className="text-3xl font-bold text-yellow-400">{stats.employees}</p>
              </div>
              <Users className="w-8 h-8 text-yellow-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 검색 및 필터 */}
      <Card className="bg-slate-800/50 border-slate-600 backdrop-blur-xl">
        <CardContent className="p-6">
          <div className="flex items-center gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input
                type="text"
                placeholder="매장명, 코드, 주소, 매니저로 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 bg-black/50 border-emerald-500/30 text-white placeholder:text-slate-400 focus:border-emerald-500"
              />
            </div>
            <Select value={String(selectedBrand)} onValueChange={(value) => setSelectedBrand(value === 'all' ? 'all' : Number(value))}>
              <SelectTrigger className="w-48 bg-black/50 border-emerald-500/30 text-white focus:border-emerald-500">
                <SelectValue placeholder="브랜드 선택" />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-600">
                <SelectItem value="all">모든 브랜드</SelectItem>
                {brands.map((brand) => (
                  <SelectItem key={brand.id} value={String(brand.id)}>
                    {brand.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={selectedStatus} onValueChange={setSelectedStatus}>
              <SelectTrigger className="w-32 bg-black/50 border-emerald-500/30 text-white focus:border-emerald-500">
                <SelectValue placeholder="상태" />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-600">
                <SelectItem value="all">모든 상태</SelectItem>
                <SelectItem value="active">활성</SelectItem>
                <SelectItem value="inactive">비활성</SelectItem>
              </SelectContent>
            </Select>
            <Button
              onClick={() => withLoading(fetchStores)}
              variant="outline"
              className="border-slate-600 text-slate-300 hover:bg-slate-700"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              새로고침
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 매장 목록 */}
      <Card className="bg-slate-800/50 border-slate-600 backdrop-blur-xl">
        <CardHeader>
          <CardTitle className="text-emerald-400 flex items-center gap-2">
            <Building2 className="w-5 h-5" />
            매장 목록 ({filteredStores.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-12">
              <RefreshCw className="w-8 h-8 text-emerald-400 animate-spin mx-auto mb-4" />
              <p className="text-slate-400">매장 정보를 불러오는 중...</p>
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <AlertTriangle className="w-8 h-8 text-red-400 mx-auto mb-4" />
              <p className="text-red-400 mb-4">{error}</p>
              <Button onClick={() => withLoading(fetchStores)}>
                다시 시도
              </Button>
            </div>
          ) : filteredStores.length === 0 ? (
            <div className="text-center py-12">
              <Building2 className="w-16 h-16 text-slate-600 mx-auto mb-4" />
              <p className="text-slate-400">
                {searchTerm || selectedBrand !== 'all' || selectedStatus !== 'all' ? '검색 결과가 없습니다.' : '등록된 매장이 없습니다.'}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredStores.map((store) => (
                <Card
                  key={store.id}
                  className="bg-slate-700/50 border-slate-600 hover:border-emerald-400/50 transition-all duration-300"
                >
                  <CardHeader className="pb-4">
                    <div className="flex items-center justify-between">
                      <div className="w-12 h-12 bg-gradient-to-r from-emerald-500/20 to-cyan-500/20 rounded-xl flex items-center justify-center">
                        <Building2 className="w-6 h-6 text-emerald-400" />
                      </div>
                      <Badge className={getStatusColor(store.status)}>
                        {getStatusText(store.status)}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div>
                      <h3 className="text-lg font-semibold text-white">
                        {store.name}
                      </h3>
                      <p className="text-sm text-slate-400">코드: {store.code}</p>
                      <p className="text-sm text-slate-400">
                        브랜드: {brands.find(b => b.id === store.brand_id)?.name || '알 수 없음'}
                      </p>
                    </div>

                    {store.address && (
                      <div className="flex items-start gap-2 text-sm">
                        <MapPin className="w-4 h-4 text-slate-400 mt-0.5 flex-shrink-0" />
                        <p className="text-slate-300">{store.address}</p>
                      </div>
                    )}

                    {store.phone && (
                      <div className="flex items-center gap-2 text-sm">
                        <Phone className="w-4 h-4 text-slate-400" />
                        <p className="text-slate-300">{store.phone}</p>
                      </div>
                    )}

                    {store.manager_name && (
                      <div className="flex items-center gap-2 text-sm">
                        <Users className="w-4 h-4 text-slate-400" />
                        <p className="text-slate-300">매니저: {store.manager_name}</p>
                      </div>
                    )}

                    <div className="pt-2">
                      <p className="text-slate-400 text-sm">소속 직원</p>
                      <p className="text-yellow-400 font-semibold">{store.employee_count}명</p>
                    </div>

                    <div className="flex gap-2 pt-2">
                      <Button
                        onClick={() => handleEdit(store)}
                        size="sm"
                        variant="outline"
                        className="flex-1 border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/20"
                      >
                        <Edit className="w-3 h-3 mr-1" />
                        수정
                      </Button>
                      <Button
                        onClick={() => handleDelete(store)}
                        size="sm"
                        variant="outline"
                        className="border-red-500/30 text-red-400 hover:bg-red-500/20"
                      >
                        <Trash2 className="w-3 h-3" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* 매장 생성/수정 다이얼로그 */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="bg-slate-800/90 border-slate-600 backdrop-blur-xl">
          <DialogHeader>
            <DialogTitle className="text-emerald-400">
              {editingStore ? '매장 수정' : '매장 추가'}
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="name" className="text-slate-300">매장명 *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="bg-black/50 border-emerald-500/30 text-white focus:border-emerald-500"
                placeholder="매장명을 입력하세요"
              />
            </div>
            <div>
              <Label htmlFor="code" className="text-slate-300">매장 코드 *</Label>
              <Input
                id="code"
                value={formData.code}
                onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                className="bg-black/50 border-emerald-500/30 text-white focus:border-emerald-500"
                placeholder="매장 코드를 입력하세요"
              />
            </div>
            <div>
              <Label htmlFor="brand" className="text-slate-300">브랜드 *</Label>
              <Select value={String(formData.brand_id)} onValueChange={(value) => setFormData({ ...formData, brand_id: Number(value) })}>
                <SelectTrigger className="bg-black/50 border-emerald-500/30 text-white focus:border-emerald-500">
                  <SelectValue placeholder="브랜드를 선택하세요" />
                </SelectTrigger>
                <SelectContent className="bg-slate-800 border-slate-600">
                  {brands.map((brand) => (
                    <SelectItem key={brand.id} value={String(brand.id)}>
                      {brand.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="address" className="text-slate-300">주소</Label>
              <Input
                id="address"
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                className="bg-black/50 border-emerald-500/30 text-white focus:border-emerald-500"
                placeholder="매장 주소를 입력하세요"
              />
            </div>
            <div>
              <Label htmlFor="phone" className="text-slate-300">전화번호</Label>
              <Input
                id="phone"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="bg-black/50 border-emerald-500/30 text-white focus:border-emerald-500"
                placeholder="매장 전화번호를 입력하세요"
              />
            </div>
            <div>
              <Label htmlFor="manager" className="text-slate-300">매니저명</Label>
              <Input
                id="manager"
                value={formData.manager_name}
                onChange={(e) => setFormData({ ...formData, manager_name: e.target.value })}
                className="bg-black/50 border-emerald-500/30 text-white focus:border-emerald-500"
                placeholder="매니저명을 입력하세요"
              />
            </div>
            <div className="flex gap-3 pt-4">
              <Button
                type="submit"
                className="flex-1 bg-gradient-to-r from-emerald-500/20 to-cyan-500/20 text-emerald-400 border-emerald-500/30 hover:from-emerald-500/30 hover:to-cyan-500/30"
              >
                {editingStore ? '수정' : '추가'}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsCreateDialogOpen(false)}
                className="border-slate-600 text-slate-300 hover:bg-slate-700"
              >
                취소
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
} 
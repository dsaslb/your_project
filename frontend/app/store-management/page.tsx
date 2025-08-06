'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../src/components/ui/card';
import { Button } from '../../src/components/ui/button';
import { Input } from '../../src/components/ui/input';
import { Badge } from '../../src/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../../src/components/ui/dialog';
import { Label } from '../../src/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../src/components/ui/select';
import { 
  Building2, 
  Plus, 
  Search, 
  Edit, 
  Trash2, 
  Users,
  CheckCircle,
  XCircle
} from 'lucide-react';
import { toast } from 'sonner';
import { apiClient, Store as StoreType, Brand } from '../../src/lib/api-client';
import useLoadingState from '../../src/hooks/useLoadingState';
import useErrorHandler from '../../src/hooks/useErrorHandler';

interface StoreFormData {
  name: string;
  code: string;
  address: string;
  phone: string;
  manager_name: string;
  brand_id: number;
}

interface EmployeeFormData {
  name: string;
  email: string;
  phone: string;
  role: string;
  department: string;
  hireDate: string;
  location: string;
  store_id: number;
  permissions: {
    schedule_management: boolean;
    inventory_management: boolean;
    order_management: boolean;
    employee_management: boolean;
    reporting: boolean;
  };
}

export default function StoreManagement() {
  const [stores, setStores] = useState<StoreType[]>([]);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedBrand, setSelectedBrand] = useState<number | 'all'>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isCreateEmployeeDialogOpen, setIsCreateEmployeeDialogOpen] = useState(false);
  const [editingStore, setEditingStore] = useState<StoreType | null>(null);
  const [selectedStore, setSelectedStore] = useState<StoreType | null>(null);
  
  const [formData, setFormData] = useState<StoreFormData>({
    name: '',
    code: '',
    address: '',
    phone: '',
    manager_name: '',
    brand_id: 0,
  });
  
  const [employeeFormData, setEmployeeFormData] = useState<EmployeeFormData>({
    name: '',
    email: '',
    phone: '',
    role: '',
    department: '',
    hireDate: '',
    location: '',
    store_id: 0,
    permissions: {
      schedule_management: false,
      inventory_management: false,
      order_management: false,
      employee_management: false,
      reporting: false,
    },
  });

  const { isLoading, setLoading, withLoading } = useLoadingState();
  const { handleError } = useErrorHandler();

  // 매장 목록 조회
  const fetchStores = async () => {
    try {
      const response = await apiClient.getStores();
      if (response.success && response.data) {
        setStores(response.data);
      }
    } catch (error) {
      handleError(error as Error);
    }
  };

  // 브랜드 목록 조회
  const fetchBrands = async () => {
    try {
      const response = await apiClient.getBrands();
      if (response.success && response.data) {
        setBrands(response.data);
      }
    } catch (error) {
      handleError(error as Error);
    }
  };

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

  // 매장 생성/수정
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name.trim() || !formData.code.trim()) {
      toast.error('매장명과 코드는 필수 입력 항목입니다.');
      return;
    }

    try {
      setLoading(true);
      
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
    } finally {
      setLoading(false);
    }
  };

  // 매장 삭제
  const handleDelete = async (store: StoreType) => {
    if (!confirm('매장을 삭제하시겠습니까?')) {
      return;
    }

    try {
      setLoading(true);
      const response = await apiClient.deleteStore(store.id);
      if (response.success) {
        toast.success('매장이 성공적으로 삭제되었습니다.');
        fetchStores();
      }
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 매장 활성화/비활성화
  const handleActivate = async (store: StoreType) => {
    try {
      setLoading(true);
      const newStatus = store.status === 'active' ? 'inactive' : 'active';
      
      const response = await apiClient.updateStore(store.id, { status: newStatus });
      if (response.success) {
        toast.success(`매장이 ${newStatus === 'active' ? '활성화' : '비활성화'}되었습니다.`);
        fetchStores();
      }
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 매장 수정 모드로 설정
  const handleEdit = (store: StoreType) => {
    setEditingStore(store);
    setFormData({
      name: store.name,
      code: store.name, // Store 타입에 code가 없으므로 name을 사용
      address: store.address || '',
      phone: store.phone || '',
      manager_name: '', // Store 타입에 manager_name이 없으므로 빈 문자열 사용
      brand_id: store.brand_id,
    });
    setIsCreateDialogOpen(true);
  };

  // 상태별 색상
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500/20 text-green-400 border border-green-500/30';
      case 'inactive': return 'bg-red-500/20 text-red-400 border border-red-500/30';
      default: return 'bg-slate-500/20 text-slate-400 border border-slate-500/30';
    }
  };

  // 상태별 텍스트
  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return '활성';
      case 'inactive': return '비활성';
      default: return '알 수 없음';
    }
  };

  // 직원 생성 다이얼로그 열기
  const handleCreateEmployee = (store: StoreType) => {
    setSelectedStore(store);
    setEmployeeFormData({
      name: '',
      email: '',
      phone: '',
      role: '',
      department: '',
      hireDate: '',
      location: store.name,
      store_id: store.id,
      permissions: {
        schedule_management: false,
        inventory_management: false,
        order_management: false,
        employee_management: false,
        reporting: false,
      },
    });
    setIsCreateEmployeeDialogOpen(true);
  };

  // 직원 생성 처리
  const handleCreateEmployeeSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!employeeFormData.name.trim() || !employeeFormData.email.trim()) {
      toast.error('직원명과 이메일은 필수 입력 항목입니다.');
      return;
    }

    try {
      setLoading(true);
      const employeeData = {
        name: employeeFormData.name,
        email: employeeFormData.email,
        phone: employeeFormData.phone,
        role: employeeFormData.role as 'super_admin' | 'brand_manager' | 'store_manager' | 'employee',
        status: 'active' as const,
        store_id: employeeFormData.store_id,
      };
      const response = await apiClient.createEmployee(employeeData);
      if (response.success) {
        toast.success('직원이 성공적으로 생성되었습니다.');
        setIsCreateEmployeeDialogOpen(false);
        resetEmployeeForm();
        fetchStores(); // 매장 목록 새로고침 (직원 수 업데이트)
      }
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 직원 폼 초기화
  const resetEmployeeForm = () => {
    setEmployeeFormData({
      name: '',
      email: '',
      phone: '',
      role: '',
      department: '',
      hireDate: '',
      location: '',
      store_id: 0,
      permissions: {
        schedule_management: false,
        inventory_management: false,
        order_management: false,
        employee_management: false,
        reporting: false,
      },
    });
    setSelectedStore(null);
  };

  // 직원 폼 입력 처리
  const handleEmployeeInputChange = (field: keyof EmployeeFormData, value: string | number | boolean) => {
    if (field === 'permissions') {
      setEmployeeFormData(prev => ({
        ...prev,
        permissions: {
          ...prev.permissions,
          [value as string]: !prev.permissions[value as keyof typeof prev.permissions]
        }
      }));
    } else {
      setEmployeeFormData(prev => ({
        ...prev,
        [field]: value
      }));
    }
  };

  // 필터링된 매장 목록
  const filteredStores = stores.filter(store => {
    const matchesSearch = searchTerm === '' || 
      store.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      store.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      store.address.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesBrand = selectedBrand === 'all' || store.brand_id === selectedBrand;
    const matchesStatus = selectedStatus === 'all' || store.status === selectedStatus;
    
    return matchesSearch && matchesBrand && matchesStatus;
  });

  // 초기 데이터 로드
  useEffect(() => {
    withLoading(async () => {
      await Promise.all([fetchStores(), fetchBrands()]);
    });
  }, []);

  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <Building2 className="w-8 h-8 text-blue-400" />
            매장 관리
          </h1>
          <p className="text-slate-400 mt-2">매장 정보를 관리하고 직원을 등록합니다.</p>
        </div>
        <Button
          onClick={() => {
            resetForm();
            setIsCreateDialogOpen(true);
          }}
          className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700"
        >
          <Plus className="w-4 h-4 mr-2" />
          새 매장 추가
        </Button>
      </div>

      {/* 필터 및 검색 */}
      <Card className="bg-slate-800/50 border-slate-600">
        <CardContent className="p-4">
          <div className="flex items-center gap-4 flex-wrap">
            <div className="flex items-center gap-2">
              <Search className="w-4 h-4 text-slate-400" />
              <Input
                type="text"
                placeholder="매장명, 코드, 매니저명으로 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-64 bg-slate-600/50 border-slate-500"
              />
            </div>
            
            <div className="flex items-center gap-2">
              <Label className="text-slate-300">브랜드:</Label>
              <Select value={selectedBrand.toString()} onValueChange={(value) => setSelectedBrand(value === 'all' ? 'all' : parseInt(value))}>
                <SelectTrigger className="w-40 bg-slate-600/50 border-slate-500">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-slate-700 border-slate-600">
                  <SelectItem value="all">전체 브랜드</SelectItem>
                  {brands.map((brand) => (
                    <SelectItem key={brand.id} value={brand.id.toString()}>
                      {brand.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div className="flex items-center gap-2">
              <Label className="text-slate-300">상태:</Label>
              <Select value={selectedStatus} onValueChange={setSelectedStatus}>
                <SelectTrigger className="w-32 bg-slate-600/50 border-slate-500">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-slate-700 border-slate-600">
                  <SelectItem value="all">전체</SelectItem>
                  <SelectItem value="active">활성</SelectItem>
                  <SelectItem value="inactive">비활성</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <Button
              onClick={() => {
                setSearchTerm('');
                setSelectedBrand('all');
                setSelectedStatus('all');
              }}
              variant="outline"
              className="border-slate-500 text-slate-300 hover:bg-slate-600"
            >
              필터 초기화
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 매장 목록 */}
      <Card className="bg-slate-800/50 border-slate-600">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Building2 className="w-5 h-5 text-blue-400" />
            매장 목록 ({filteredStores.length}개)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredStores.map((store) => (
              <div 
                key={store.id} 
                className="flex justify-between items-center p-4 bg-slate-600/30 rounded-lg hover:bg-slate-600/50 transition-all"
              >
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
                    <Building2 className="w-6 h-6 text-blue-400" />
                  </div>
                  <div>
                    <h3 className="text-white font-semibold">{store.name}</h3>
                    <p className="text-slate-400 text-sm">ID: {store.id}</p>
                    <p className="text-slate-500 text-xs">{store.address}</p>
                    <p className="text-slate-500 text-xs">연락처: {store.phone || '미지정'}</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-3">
                  <Badge className={getStatusColor(store.status)}>
                    {getStatusText(store.status)}
                  </Badge>
                  
                  <div className="flex items-center gap-1 text-slate-400">
                    <Users className="w-4 h-4" />
                    <span className="text-sm">{store.employee_count || 0}명</span>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleCreateEmployee(store)}
                      className="text-blue-400 hover:text-blue-300 hover:bg-blue-500/20"
                    >
                      <Users className="w-4 h-4" />
                    </Button>
                    
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleEdit(store)}
                      className="text-cyan-400 hover:text-cyan-300 hover:bg-cyan-500/20"
                    >
                      <Edit className="w-4 h-4" />
                    </Button>
                    
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleActivate(store)}
                      className={store.status === 'active' 
                        ? "text-red-400 hover:text-red-300 hover:bg-red-500/20" 
                        : "text-green-400 hover:text-green-300 hover:bg-green-500/20"
                      }
                    >
                      {store.status === 'active' ? <XCircle className="w-4 h-4" /> : <CheckCircle className="w-4 h-4" />}
                    </Button>
                    
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(store)}
                      className="text-red-400 hover:text-red-300 hover:bg-red-500/20"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
            
            {filteredStores.length === 0 && (
              <div className="text-center py-8">
                <Building2 className="w-12 h-12 text-slate-500 mx-auto mb-4" />
                <p className="text-slate-400">등록된 매장이 없습니다.</p>
                <p className="text-slate-500 text-sm">새로운 매장을 추가해보세요.</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* 매장 생성/수정 다이얼로그 */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="bg-slate-800/95 border-blue-500/50 text-white max-w-md mx-auto backdrop-blur-xl">
          <DialogHeader>
            <DialogTitle className="text-xl text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400">
              {editingStore ? '매장 수정' : '새 매장 추가'}
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label className="text-gray-300 block mb-2">매장명 *</Label>
              <Input
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                className="bg-slate-700/50 border-blue-500/50 text-white placeholder:text-slate-400 focus:border-blue-400 focus:ring-2 focus:ring-blue-400/20"
                placeholder="매장명을 입력하세요"
                required
              />
            </div>
            
            <div>
              <Label className="text-gray-300 block mb-2">매장 코드 *</Label>
              <Input
                value={formData.code}
                onChange={(e) => setFormData({...formData, code: e.target.value})}
                className="bg-slate-700/50 border-blue-500/50 text-white placeholder:text-slate-400 focus:border-blue-400 focus:ring-2 focus:ring-blue-400/20"
                placeholder="매장 코드를 입력하세요"
                required
              />
            </div>
            
            <div>
              <Label className="text-gray-300 block mb-2">주소</Label>
              <Input
                value={formData.address}
                onChange={(e) => setFormData({...formData, address: e.target.value})}
                className="bg-slate-700/50 border-blue-500/50 text-white placeholder:text-slate-400 focus:border-blue-400 focus:ring-2 focus:ring-blue-400/20"
                placeholder="매장 주소를 입력하세요"
              />
            </div>
            
            <div>
              <Label className="text-gray-300 block mb-2">전화번호</Label>
              <Input
                value={formData.phone}
                onChange={(e) => setFormData({...formData, phone: e.target.value})}
                className="bg-slate-700/50 border-blue-500/50 text-white placeholder:text-slate-400 focus:border-blue-400 focus:ring-2 focus:ring-blue-400/20"
                placeholder="전화번호를 입력하세요"
              />
            </div>
            
            <div>
              <Label className="text-gray-300 block mb-2">매니저명</Label>
              <Input
                value={formData.manager_name}
                onChange={(e) => setFormData({...formData, manager_name: e.target.value})}
                className="bg-slate-700/50 border-blue-500/50 text-white placeholder:text-slate-400 focus:border-blue-400 focus:ring-2 focus:ring-blue-400/20"
                placeholder="매니저명을 입력하세요"
              />
            </div>
            
            <div>
              <Label className="text-gray-300 block mb-2">브랜드 *</Label>
              <Select 
                value={formData.brand_id.toString()} 
                onValueChange={(value) => setFormData({...formData, brand_id: parseInt(value)})}
              >
                <SelectTrigger className="bg-slate-700/50 border-blue-500/50 text-white focus:border-blue-400 focus:ring-2 focus:ring-blue-400/20">
                  <SelectValue placeholder="브랜드를 선택하세요" />
                </SelectTrigger>
                <SelectContent className="bg-slate-800 border-blue-500/50">
                  {brands.map((brand) => (
                    <SelectItem key={brand.id} value={brand.id.toString()}>
                      {brand.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div className="flex justify-end space-x-2 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsCreateDialogOpen(false)}
                className="border-gray-600/50 text-gray-300 hover:border-gray-500 hover:text-gray-200"
              >
                취소
              </Button>
              <Button
                type="submit"
                className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700"
                disabled={isLoading}
              >
                {isLoading ? '처리 중...' : (editingStore ? '수정' : '추가')}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* 직원 생성 다이얼로그 */}
      <Dialog open={isCreateEmployeeDialogOpen} onOpenChange={setIsCreateEmployeeDialogOpen}>
        <DialogContent className="bg-slate-800/95 border-green-500/50 text-white max-w-md mx-auto backdrop-blur-xl">
          <DialogHeader>
            <DialogTitle className="text-xl text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-emerald-400">
              새 직원 추가
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleCreateEmployeeSubmit} className="space-y-4">
            <div>
              <Label className="text-gray-300 block mb-2">직원명 *</Label>
              <Input
                value={employeeFormData.name}
                onChange={(e) => handleEmployeeInputChange('name', e.target.value)}
                className="bg-slate-700/50 border-green-500/50 text-white placeholder:text-slate-400 focus:border-green-400 focus:ring-2 focus:ring-green-400/20"
                placeholder="직원명을 입력하세요"
                required
              />
            </div>
            
            <div>
              <Label className="text-gray-300 block mb-2">이메일 *</Label>
              <Input
                type="email"
                value={employeeFormData.email}
                onChange={(e) => handleEmployeeInputChange('email', e.target.value)}
                className="bg-slate-700/50 border-green-500/50 text-white placeholder:text-slate-400 focus:border-green-400 focus:ring-2 focus:ring-green-400/20"
                placeholder="이메일을 입력하세요"
                required
              />
            </div>
            
            <div>
              <Label className="text-gray-300 block mb-2">전화번호</Label>
              <Input
                value={employeeFormData.phone}
                onChange={(e) => handleEmployeeInputChange('phone', e.target.value)}
                className="bg-slate-700/50 border-green-500/50 text-white placeholder:text-slate-400 focus:border-green-400 focus:ring-2 focus:ring-green-400/20"
                placeholder="전화번호를 입력하세요"
              />
            </div>
            
            <div>
              <Label className="text-gray-300 block mb-2">직책</Label>
              <Input
                value={employeeFormData.role}
                onChange={(e) => handleEmployeeInputChange('role', e.target.value)}
                className="bg-slate-700/50 border-green-500/50 text-white placeholder:text-slate-400 focus:border-green-400 focus:ring-2 focus:ring-green-400/20"
                placeholder="직책을 입력하세요"
              />
            </div>
            
            <div>
              <Label className="text-gray-300 block mb-2">부서</Label>
              <Input
                value={employeeFormData.department}
                onChange={(e) => handleEmployeeInputChange('department', e.target.value)}
                className="bg-slate-700/50 border-green-500/50 text-white placeholder:text-slate-400 focus:border-green-400 focus:ring-2 focus:ring-green-400/20"
                placeholder="부서를 입력하세요"
              />
            </div>
            
            <div>
              <Label className="text-gray-300 block mb-2">입사일</Label>
              <Input
                type="date"
                value={employeeFormData.hireDate}
                onChange={(e) => handleEmployeeInputChange('hireDate', e.target.value)}
                className="bg-slate-700/50 border-green-500/50 text-white focus:border-green-400 focus:ring-2 focus:ring-green-400/20"
              />
            </div>
            
            <div>
              <Label className="text-gray-300 block mb-2">근무지</Label>
              <Input
                value={employeeFormData.location}
                onChange={(e) => handleEmployeeInputChange('location', e.target.value)}
                className="bg-slate-700/50 border-green-500/50 text-white placeholder:text-slate-400 focus:border-green-400 focus:ring-2 focus:ring-green-400/20"
                placeholder="근무지를 입력하세요"
              />
            </div>
            
            <div>
              <Label className="text-gray-300 block mb-2">권한 설정</Label>
              <div className="space-y-2">
                {Object.entries(employeeFormData.permissions).map(([key, value]) => (
                  <div key={key} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id={key}
                      checked={value}
                      onChange={() => handleEmployeeInputChange('permissions', key)}
                      className="rounded border-green-500/50 bg-slate-700/50 text-green-400 focus:ring-green-400/20"
                    />
                    <Label htmlFor={key} className="text-sm text-gray-300">
                      {key === 'schedule_management' && '스케줄 관리'}
                      {key === 'inventory_management' && '재고 관리'}
                      {key === 'order_management' && '발주 관리'}
                      {key === 'employee_management' && '직원 관리'}
                      {key === 'reporting' && '보고서'}
                    </Label>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="flex justify-end space-x-2 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsCreateEmployeeDialogOpen(false)}
                className="border-gray-600/50 text-gray-300 hover:border-gray-500 hover:text-gray-200"
              >
                취소
              </Button>
              <Button
                type="submit"
                className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700"
                disabled={isLoading}
              >
                {isLoading ? '처리 중...' : '추가'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
} 
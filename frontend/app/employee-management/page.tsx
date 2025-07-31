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
  Users, 
  Plus, 
  Search, 
  Edit, 
  Trash2, 
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Building2,
  Mail,
  Phone,
  Calendar,
  User
} from 'lucide-react';
import { toast } from 'sonner';
import { apiClient, Employee, Store as StoreType, Brand } from '../../lib/api-client';
import useLoadingState from '@/hooks/useLoadingState';
import useErrorHandler from '@/hooks/useErrorHandler';

interface EmployeeFormData {
  name: string;
  email: string;
  phone: string;
  position: string;
  store_id: number;
  hire_date: string;
}

export default function EmployeeManagement() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [stores, setStores] = useState<StoreType[]>([]);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStore, setSelectedStore] = useState<number | 'all'>('all');
  const [selectedBrand, setSelectedBrand] = useState<number | 'all'>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState<Employee | null>(null);
  const [formData, setFormData] = useState<EmployeeFormData>({
    name: '',
    email: '',
    phone: '',
    position: '',
    store_id: 0,
    hire_date: '',
  });

  const { isLoading, error, withLoading } = useLoadingState();
  const { handleError } = useErrorHandler();

  // 직원 목록 조회
  const fetchEmployees = async () => {
    const response = await apiClient.getEmployees();
    if (response.success) {
      setEmployees(response.data);
    }
  };

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
      await Promise.all([fetchEmployees(), fetchStores(), fetchBrands()]);
    });
  }, []);

  // 검색 및 필터링
  const filteredEmployees = employees.filter(employee => {
    const matchesSearch = 
      employee.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      employee.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      employee.position?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStore = selectedStore === 'all' || employee.store_id === selectedStore;
    const matchesBrand = selectedBrand === 'all' || 
      stores.find(s => s.id === employee.store_id)?.brand_id === selectedBrand;
    const matchesStatus = selectedStatus === 'all' || employee.status === selectedStatus;
    
    return matchesSearch && matchesStore && matchesBrand && matchesStatus;
  });

  // 폼 초기화
  const resetForm = () => {
    setFormData({
      name: '',
      email: '',
      phone: '',
      position: '',
      store_id: 0,
      hire_date: '',
    });
    setEditingEmployee(null);
  };

  // 폼 제출 처리
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name.trim() || formData.store_id === 0) {
      toast.error('직원명과 소속 매장은 필수 입력 항목입니다.');
      return;
    }

    try {
      if (editingEmployee) {
        // 수정
        const response = await apiClient.updateEmployee(editingEmployee.id, formData);
        if (response.success) {
          toast.success('직원이 성공적으로 수정되었습니다.');
          setIsCreateDialogOpen(false);
          resetForm();
          fetchEmployees();
        }
      } else {
        // 생성
        const response = await apiClient.createEmployee(formData);
        if (response.success) {
          toast.success('직원이 성공적으로 생성되었습니다.');
          setIsCreateDialogOpen(false);
          resetForm();
          fetchEmployees();
        }
      }
    } catch (error) {
      handleError(error as Error);
    }
  };

  // 직원 삭제
  const handleDelete = async (employee: Employee) => {
    if (!confirm(`"${employee.name}" 직원을 삭제하시겠습니까?`)) {
      return;
    }

    try {
      const response = await apiClient.deleteEmployee(employee.id);
      if (response.success) {
        toast.success('직원이 성공적으로 삭제되었습니다.');
        fetchEmployees();
      }
    } catch (error) {
      handleError(error as Error);
    }
  };

  // 수정 모드 시작
  const handleEdit = (employee: Employee) => {
    setEditingEmployee(employee);
    setFormData({
      name: employee.name,
      email: employee.email || '',
      phone: employee.phone || '',
      position: employee.position || '',
      store_id: employee.store_id,
      hire_date: employee.hire_date || '',
    });
    setIsCreateDialogOpen(true);
  };

  // 통계 계산
  const stats = {
    total: employees.length,
    active: employees.filter(employee => employee.status === 'active').length,
    inactive: employees.filter(employee => employee.status === 'inactive').length,
    stores: new Set(employees.map(e => e.store_id)).size,
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
      case 'active': return '재직';
      case 'inactive': return '퇴직';
      default: return '알 수 없음';
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <Users className="w-8 h-8 text-yellow-400" />
            직원별 관리
          </h1>
          <p className="text-slate-400 mt-2">직원 정보를 관리하고 업무를 조직화합니다.</p>
        </div>
        <Button
          onClick={() => {
            resetForm();
            setIsCreateDialogOpen(true);
          }}
          className="bg-gradient-to-r from-yellow-500/20 to-cyan-500/20 text-yellow-400 border-yellow-500/30 hover:from-yellow-500/30 hover:to-cyan-500/30"
        >
          <Plus className="w-4 h-4 mr-2" />
          직원 추가
        </Button>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="bg-slate-800/50 border-yellow-500/30 backdrop-blur-xl">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">총 직원</p>
                <p className="text-3xl font-bold text-yellow-400">{stats.total}</p>
              </div>
              <Users className="w-8 h-8 text-yellow-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 border-emerald-500/30 backdrop-blur-xl">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">재직 직원</p>
                <p className="text-3xl font-bold text-emerald-400">{stats.active}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-emerald-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 border-red-500/30 backdrop-blur-xl">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">퇴직 직원</p>
                <p className="text-3xl font-bold text-red-400">{stats.inactive}</p>
              </div>
              <AlertTriangle className="w-8 h-8 text-red-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 border-cyan-500/30 backdrop-blur-xl">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">소속 매장</p>
                <p className="text-3xl font-bold text-cyan-400">{stats.stores}</p>
              </div>
              <Building2 className="w-8 h-8 text-cyan-400" />
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
                placeholder="직원명, 이메일, 직책으로 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 bg-black/50 border-yellow-500/30 text-white placeholder:text-slate-400 focus:border-yellow-500"
              />
            </div>
            <Select value={String(selectedBrand)} onValueChange={(value) => setSelectedBrand(value === 'all' ? 'all' : Number(value))}>
              <SelectTrigger className="w-40 bg-black/50 border-yellow-500/30 text-white focus:border-yellow-500">
                <SelectValue placeholder="브랜드" />
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
            <Select value={String(selectedStore)} onValueChange={(value) => setSelectedStore(value === 'all' ? 'all' : Number(value))}>
              <SelectTrigger className="w-40 bg-black/50 border-yellow-500/30 text-white focus:border-yellow-500">
                <SelectValue placeholder="매장" />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-600">
                <SelectItem value="all">모든 매장</SelectItem>
                {stores.map((store) => (
                  <SelectItem key={store.id} value={String(store.id)}>
                    {store.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={selectedStatus} onValueChange={setSelectedStatus}>
              <SelectTrigger className="w-32 bg-black/50 border-yellow-500/30 text-white focus:border-yellow-500">
                <SelectValue placeholder="상태" />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-600">
                <SelectItem value="all">모든 상태</SelectItem>
                <SelectItem value="active">재직</SelectItem>
                <SelectItem value="inactive">퇴직</SelectItem>
              </SelectContent>
            </Select>
            <Button
              onClick={() => withLoading(fetchEmployees)}
              variant="outline"
              className="border-slate-600 text-slate-300 hover:bg-slate-700"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              새로고침
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 직원 목록 */}
      <Card className="bg-slate-800/50 border-slate-600 backdrop-blur-xl">
        <CardHeader>
          <CardTitle className="text-yellow-400 flex items-center gap-2">
            <Users className="w-5 h-5" />
            직원 목록 ({filteredEmployees.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-12">
              <RefreshCw className="w-8 h-8 text-yellow-400 animate-spin mx-auto mb-4" />
              <p className="text-slate-400">직원 정보를 불러오는 중...</p>
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <AlertTriangle className="w-8 h-8 text-red-400 mx-auto mb-4" />
              <p className="text-red-400 mb-4">{error}</p>
              <Button onClick={() => withLoading(fetchEmployees)}>
                다시 시도
              </Button>
            </div>
          ) : filteredEmployees.length === 0 ? (
            <div className="text-center py-12">
              <Users className="w-16 h-16 text-slate-600 mx-auto mb-4" />
              <p className="text-slate-400">
                {searchTerm || selectedStore !== 'all' || selectedBrand !== 'all' || selectedStatus !== 'all' ? '검색 결과가 없습니다.' : '등록된 직원이 없습니다.'}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredEmployees.map((employee) => (
                <Card
                  key={employee.id}
                  className="bg-slate-700/50 border-slate-600 hover:border-yellow-400/50 transition-all duration-300"
                >
                  <CardHeader className="pb-4">
                    <div className="flex items-center justify-between">
                      <div className="w-12 h-12 bg-gradient-to-r from-yellow-500/20 to-cyan-500/20 rounded-xl flex items-center justify-center">
                        <User className="w-6 h-6 text-yellow-400" />
                      </div>
                      <Badge className={getStatusColor(employee.status)}>
                        {getStatusText(employee.status)}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div>
                      <h3 className="text-lg font-semibold text-white">
                        {employee.name}
                      </h3>
                      {employee.position && (
                        <p className="text-sm text-slate-400">직책: {employee.position}</p>
                      )}
                      <p className="text-sm text-slate-400">
                        매장: {stores.find(s => s.id === employee.store_id)?.name || '알 수 없음'}
                      </p>
                      <p className="text-sm text-slate-400">
                        브랜드: {brands.find(b => b.id === stores.find(s => s.id === employee.store_id)?.brand_id)?.name || '알 수 없음'}
                      </p>
                    </div>

                    {employee.email && (
                      <div className="flex items-center gap-2 text-sm">
                        <Mail className="w-4 h-4 text-slate-400" />
                        <p className="text-slate-300">{employee.email}</p>
                      </div>
                    )}

                    {employee.phone && (
                      <div className="flex items-center gap-2 text-sm">
                        <Phone className="w-4 h-4 text-slate-400" />
                        <p className="text-slate-300">{employee.phone}</p>
                      </div>
                    )}

                    {employee.hire_date && (
                      <div className="flex items-center gap-2 text-sm">
                        <Calendar className="w-4 h-4 text-slate-400" />
                        <p className="text-slate-300">입사일: {new Date(employee.hire_date).toLocaleDateString()}</p>
                      </div>
                    )}

                    <div className="flex gap-2 pt-2">
                      <Button
                        onClick={() => handleEdit(employee)}
                        size="sm"
                        variant="outline"
                        className="flex-1 border-yellow-500/30 text-yellow-400 hover:bg-yellow-500/20"
                      >
                        <Edit className="w-3 h-3 mr-1" />
                        수정
                      </Button>
                      <Button
                        onClick={() => handleDelete(employee)}
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

      {/* 직원 생성/수정 다이얼로그 */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="bg-slate-800/90 border-slate-600 backdrop-blur-xl">
          <DialogHeader>
            <DialogTitle className="text-yellow-400">
              {editingEmployee ? '직원 수정' : '직원 추가'}
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="name" className="text-slate-300">직원명 *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="bg-black/50 border-yellow-500/30 text-white focus:border-yellow-500"
                placeholder="직원명을 입력하세요"
              />
            </div>
            <div>
              <Label htmlFor="email" className="text-slate-300">이메일</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="bg-black/50 border-yellow-500/30 text-white focus:border-yellow-500"
                placeholder="이메일을 입력하세요"
              />
            </div>
            <div>
              <Label htmlFor="phone" className="text-slate-300">전화번호</Label>
              <Input
                id="phone"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="bg-black/50 border-yellow-500/30 text-white focus:border-yellow-500"
                placeholder="전화번호를 입력하세요"
              />
            </div>
            <div>
              <Label htmlFor="position" className="text-slate-300">직책</Label>
              <Input
                id="position"
                value={formData.position}
                onChange={(e) => setFormData({ ...formData, position: e.target.value })}
                className="bg-black/50 border-yellow-500/30 text-white focus:border-yellow-500"
                placeholder="직책을 입력하세요"
              />
            </div>
            <div>
              <Label htmlFor="store" className="text-slate-300">소속 매장 *</Label>
              <Select value={String(formData.store_id)} onValueChange={(value) => setFormData({ ...formData, store_id: Number(value) })}>
                <SelectTrigger className="bg-black/50 border-yellow-500/30 text-white focus:border-yellow-500">
                  <SelectValue placeholder="매장을 선택하세요" />
                </SelectTrigger>
                <SelectContent className="bg-slate-800 border-slate-600">
                  {stores.map((store) => (
                    <SelectItem key={store.id} value={String(store.id)}>
                      {store.name} ({brands.find(b => b.id === store.brand_id)?.name || '알 수 없음'})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="hire_date" className="text-slate-300">입사일</Label>
              <Input
                id="hire_date"
                type="date"
                value={formData.hire_date}
                onChange={(e) => setFormData({ ...formData, hire_date: e.target.value })}
                className="bg-black/50 border-yellow-500/30 text-white focus:border-yellow-500"
              />
            </div>
            <div className="flex gap-3 pt-4">
              <Button
                type="submit"
                className="flex-1 bg-gradient-to-r from-yellow-500/20 to-cyan-500/20 text-yellow-400 border-yellow-500/30 hover:from-yellow-500/30 hover:to-cyan-500/30"
              >
                {editingEmployee ? '수정' : '추가'}
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
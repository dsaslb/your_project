'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { toast } from 'sonner';
import { 
  Building2, 
  Store, 
  Users, 
  TrendingUp, 
  Activity, 
  AlertTriangle,
  Crown,
  BarChart3,
  Settings,
  Bell,
  Plus,
  UserPlus,
  CheckCircle,
  XCircle,
  MapPin,
  Phone,
  Mail
} from 'lucide-react';

interface BrandStats {
  totalStores: number;
  totalEmployees: number;
  activeStores: number;
  totalRevenue: number;
  growthRate: number;
  pendingApprovals: number;
}

interface Store {
  id: number;
  name: string;
  address: string;
  phone: string;
  email: string;
  manager_name: string;
  employee_count: number;
  status: 'active' | 'inactive' | 'maintenance';
  revenue: number;
  created_at: string;
}

interface StoreFormData {
  name: string;
  address: string;
  phone: string;
  email: string;
  manager_name: string;
  manager_email: string;
  manager_phone: string;
}

export default function BrandDashboard() {
  const [stats, setStats] = useState<BrandStats>({
    totalStores: 0,
    totalEmployees: 0,
    activeStores: 0,
    totalRevenue: 0,
    growthRate: 0,
    pendingApprovals: 0
  });

  const [stores, setStores] = useState<Store[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState<StoreFormData>({
    name: '',
    address: '',
    phone: '',
    email: '',
    manager_name: '',
    manager_email: '',
    manager_phone: ''
  });

  useEffect(() => {
    loadBrandData();
  }, []);

  const loadBrandData = async () => {
    try {
      // 브랜드관리자 대시보드 데이터 로드
      const response = await fetch('/api/brand/dashboard');
      const result = await response.json();

      if (result.success) {
        setStats({
          totalStores: result.stats.total_stores,
          totalEmployees: result.stats.total_employees,
          activeStores: result.stats.total_stores, // 활성 매장 수
          totalRevenue: 0, // 매출 데이터는 별도 API 필요
          growthRate: 0, // 성장률 데이터는 별도 API 필요
          pendingApprovals: result.stats.pending_approvals
        });
      } else {
        console.warn('브랜드 대시보드 API 호출 실패:', result.error);
        // 기본 데이터 사용
        setStats({
          totalStores: 0,
          totalEmployees: 0,
          activeStores: 0,
          totalRevenue: 0,
          growthRate: 0,
          pendingApprovals: 0
        });
      }

      // 매장 목록 데이터 로드
      const storesResponse = await fetch('/api/brand/stores');
      const storesResult = await storesResponse.json();

      if (storesResult.success) {
        const storesData = storesResult.stores.map((store: any) => ({
          id: store.id,
          name: store.name,
          address: store.address,
          phone: store.phone,
          email: store.email,
          manager_name: store.manager_name,
          employee_count: store.employee_count,
          status: store.status,
          revenue: 0, // 매출 데이터는 별도 API 필요
          created_at: store.created_at
        }));
        setStores(storesData);
      } else {
        console.warn('매장 목록 API 호출 실패:', storesResult.error);
        setStores([]);
      }
    } catch (error) {
      console.error('브랜드 데이터 로드 오류:', error);
      toast.error('데이터 로드 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: keyof StoreFormData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const validateForm = (): { isValid: boolean; errors: string[] } => {
    const errors: string[] = [];
    
    if (!formData.name.trim()) errors.push('매장명을 입력해주세요.');
    if (!formData.address.trim()) errors.push('매장 주소를 입력해주세요.');
    if (!formData.phone.trim()) errors.push('매장 연락처를 입력해주세요.');
    if (!formData.manager_name.trim()) errors.push('매장관리자 이름을 입력해주세요.');
    if (!formData.manager_email.trim()) errors.push('매장관리자 이메일을 입력해주세요.');
    if (!formData.manager_phone.trim()) errors.push('매장관리자 연락처를 입력해주세요.');
    
    // 이메일 형식 검증
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (formData.manager_email && !emailRegex.test(formData.manager_email)) {
      errors.push('올바른 이메일 형식을 입력해주세요.');
    }
    
    // 전화번호 형식 검증
    const phoneRegex = /^[0-9-+\s()]{10,15}$/;
    if (formData.manager_phone && !phoneRegex.test(formData.manager_phone)) {
      errors.push('올바른 전화번호 형식을 입력해주세요.');
    }

    return { isValid: errors.length === 0, errors };
  };

  const handleSubmit = async () => {
    const validation = validateForm();
    if (!validation.isValid) {
      validation.errors.forEach(error => toast.error(error));
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await fetch('/api/brand/create_store_with_manager', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      const result = await response.json();

      if (result.success) {
        toast.success('매장과 매장관리자 계정이 성공적으로 생성되었습니다!', {
          description: `임시 비밀번호: ${result.data.temp_password}`,
          duration: 10000,
        });
        
        // 폼 초기화
        setFormData({
          name: '',
          address: '',
          phone: '',
          email: '',
          manager_name: '',
          manager_email: '',
          manager_phone: ''
        });
        
        // 다이얼로그 닫기
        setIsCreateDialogOpen(false);
        
        // 데이터 새로고침
        await loadBrandData();
      } else {
        toast.error(result.error || '매장 생성 중 오류가 발생했습니다.');
      }
    } catch (error) {
      console.error('매장 생성 오류:', error);
      toast.error('네트워크 오류가 발생했습니다.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      address: '',
      phone: '',
      email: '',
      manager_name: '',
      manager_email: '',
      manager_phone: ''
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500/20 text-green-600';
      case 'inactive': return 'bg-gray-500/20 text-gray-600';
      case 'maintenance': return 'bg-yellow-500/20 text-yellow-600';
      default: return 'bg-gray-500/20 text-gray-600';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-blue-900">
      {/* 헤더 */}
      <header className="bg-white/10 backdrop-blur-xl border-b border-white/20">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Building2 className="h-8 w-8 text-blue-400" />
              <div>
                <h1 className="text-2xl font-bold text-white">브랜드 관리자 대시보드</h1>
                <p className="text-slate-300">매장 관리 및 직원 모니터링</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
                <DialogTrigger asChild>
                  <Button className="bg-green-600 hover:bg-green-700 text-white">
                    <Plus className="h-4 w-4 mr-2" />
                    매장 + 관리자 생성
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                  <DialogHeader>
                    <DialogTitle className="flex items-center gap-2">
                      <UserPlus className="h-5 w-5" />
                      매장 및 매장관리자 계정 생성
                    </DialogTitle>
                  </DialogHeader>
                  
                  <div className="space-y-6">
                    {/* 매장 정보 섹션 */}
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold text-gray-900 border-b pb-2">
                        매장 정보
                      </h3>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="name">매장명 *</Label>
                          <Input
                            id="name"
                            value={formData.name}
                            onChange={(e) => handleInputChange('name', e.target.value)}
                            placeholder="매장명을 입력하세요"
                          />
                        </div>
                        
                        <div className="space-y-2">
                          <Label htmlFor="email">매장 이메일</Label>
                          <Input
                            id="email"
                            type="email"
                            value={formData.email}
                            onChange={(e) => handleInputChange('email', e.target.value)}
                            placeholder="매장 연락처 이메일"
                          />
                        </div>
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="address">매장 주소 *</Label>
                        <Input
                          id="address"
                          value={formData.address}
                          onChange={(e) => handleInputChange('address', e.target.value)}
                          placeholder="매장 주소를 입력하세요"
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="phone">매장 연락처 *</Label>
                        <Input
                          id="phone"
                          value={formData.phone}
                          onChange={(e) => handleInputChange('phone', e.target.value)}
                          placeholder="매장 전화번호를 입력하세요"
                        />
                      </div>
                    </div>
                    
                    {/* 매장관리자 정보 섹션 */}
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold text-gray-900 border-b pb-2">
                        매장관리자 정보
                      </h3>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="manager_name">관리자 이름 *</Label>
                          <Input
                            id="manager_name"
                            value={formData.manager_name}
                            onChange={(e) => handleInputChange('manager_name', e.target.value)}
                            placeholder="매장관리자 이름을 입력하세요"
                          />
                        </div>
                        
                        <div className="space-y-2">
                          <Label htmlFor="manager_email">관리자 이메일 *</Label>
                          <Input
                            id="manager_email"
                            type="email"
                            value={formData.manager_email}
                            onChange={(e) => handleInputChange('manager_email', e.target.value)}
                            placeholder="매장관리자 이메일을 입력하세요"
                          />
                        </div>
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="manager_phone">관리자 연락처 *</Label>
                        <Input
                          id="manager_phone"
                          value={formData.manager_phone}
                          onChange={(e) => handleInputChange('manager_phone', e.target.value)}
                          placeholder="매장관리자 전화번호를 입력하세요"
                        />
                      </div>
                    </div>
                    
                    {/* 안내 메시지 */}
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                      <div className="flex items-start gap-2">
                        <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                        <div className="text-sm text-green-800">
                          <p className="font-medium mb-1">생성 완료 후 안내사항:</p>
                          <ul className="list-disc list-inside space-y-1">
                            <li>매장관리자 계정이 자동으로 생성됩니다</li>
                            <li>임시 비밀번호가 발급되어 화면에 표시됩니다</li>
                            <li>매장관리자는 매장 전용 대시보드에 접근할 수 있습니다</li>
                            <li>추후 로그인 기능이 구현되면 정식 로그인이 가능합니다</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex justify-end gap-3 pt-4 border-t">
                    <Button
                      variant="outline"
                      onClick={() => {
                        resetForm();
                        setIsCreateDialogOpen(false);
                      }}
                      disabled={isSubmitting}
                    >
                      <XCircle className="h-4 w-4 mr-2" />
                      취소
                    </Button>
                    <Button
                      onClick={handleSubmit}
                      disabled={isSubmitting}
                      className="bg-green-600 hover:bg-green-700"
                    >
                      {isSubmitting ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                          생성 중...
                        </>
                      ) : (
                        <>
                          <CheckCircle className="h-4 w-4 mr-2" />
                          매장 + 관리자 생성
                        </>
                      )}
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
              
              <Badge variant="outline" className="text-green-400 border-green-400">
                <Activity className="h-4 w-4 mr-1" />
                실시간 모니터링
              </Badge>
              <div className="text-slate-300 text-sm">
                {new Date().toLocaleString()}
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        {/* 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="bg-white/10 backdrop-blur-xl border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">총 매장</CardTitle>
              <Store className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.totalStores}</div>
              <p className="text-xs text-slate-400">운영 중인 매장</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-xl border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">총 직원</CardTitle>
              <Users className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.totalEmployees}</div>
              <p className="text-xs text-slate-400">등록된 직원</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-xl border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">월 매출</CardTitle>
              <TrendingUp className="h-4 w-4 text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {(stats.totalRevenue / 1000000).toFixed(0)}M
              </div>
              <p className="text-xs text-slate-400">월 총 매출</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-xl border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">승인 대기</CardTitle>
              <AlertTriangle className="h-4 w-4 text-yellow-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.pendingApprovals}</div>
              <p className="text-xs text-slate-400">승인 대기 중</p>
            </CardContent>
          </Card>
        </div>

        {/* 매장 목록 */}
        <Card className="bg-white/10 backdrop-blur-xl border-white/20">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Store className="h-5 w-5" />
              매장 목록
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stores.map((store) => (
                <div
                  key={store.id}
                  className="flex items-center justify-between p-4 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="text-2xl">🏪</div>
                    <div>
                      <h3 className="font-semibold text-white">{store.name}</h3>
                      <div className="flex items-center gap-4 text-sm text-slate-400">
                        <span className="flex items-center gap-1">
                          <MapPin className="h-3 w-3" />
                          {store.address}
                        </span>
                        <span className="flex items-center gap-1">
                          <Phone className="h-3 w-3" />
                          {store.phone}
                        </span>
                        <span className="flex items-center gap-1">
                          <Mail className="h-3 w-3" />
                          {store.email}
                        </span>
                      </div>
                      <p className="text-xs text-slate-500 mt-1">
                        매장관리자: {store.manager_name} • 직원 {store.employee_count}명
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-white">
                      {(store.revenue / 1000000).toFixed(1)}M
                    </div>
                    <Badge className={getStatusColor(store.status)}>
                      {store.status === 'active' ? '운영중' : 
                       store.status === 'inactive' ? '비활성' : '점검중'}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 
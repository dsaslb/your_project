'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
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
  XCircle
} from 'lucide-react';

interface IndustryStats {
  totalIndustries: number;
  totalBrands: number;
  totalStores: number;
  totalEmployees: number;
  activeStores: number;
  totalRevenue: number;
  growthRate: number;
}

interface Industry {
  id: number;
  name: string;
  type: 'hospital' | 'fashion' | 'beauty' | 'your_program' | 'retail';
  brandsCount: number;
  storesCount: number;
  employeesCount: number;
  revenue: number;
  status: 'active' | 'inactive' | 'maintenance';
  lastUpdated: string;
}

interface BrandFormData {
  brand_name: string;
  brand_description: string;
  brand_contact_email: string;
  brand_contact_phone: string;
  brand_address: string;
  admin_name: string;
  admin_email: string;
  admin_phone: string;
}

export default function IndustryDashboard() {
  const [stats, setStats] = useState<IndustryStats>({
    totalIndustries: 0,
    totalBrands: 0,
    totalStores: 0,
    totalEmployees: 0,
    activeStores: 0,
    totalRevenue: 0,
    growthRate: 0
  });

  const [industries, setIndustries] = useState<Industry[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState<BrandFormData>({
    brand_name: '',
    brand_description: '',
    brand_contact_email: '',
    brand_contact_phone: '',
    brand_address: '',
    admin_name: '',
    admin_email: '',
    admin_phone: ''
  });

  useEffect(() => {
    loadIndustryData();
  }, []);

  const loadIndustryData = async () => {
    try {
      setLoading(true);
      
      // 더미 데이터로 업종 통계 생성
      const dummyStats: IndustryStats = {
        totalIndustries: 5,
        totalBrands: 25,
        totalStores: 150,
        totalEmployees: 1200,
        activeStores: 145,
        totalRevenue: 85000000,
        growthRate: 12.5
      };
      
      const dummyIndustries: Industry[] = [
        {
          id: 1,
          name: '레스토랑',
          type: 'your_program',
          brandsCount: 8,
          storesCount: 45,
          employeesCount: 320,
          revenue: 25000000,
          status: 'active',
          lastUpdated: new Date().toISOString()
        },
        {
          id: 2,
          name: '카페',
          type: 'your_program',
          brandsCount: 6,
          storesCount: 38,
          employeesCount: 280,
          revenue: 18000000,
          status: 'active',
          lastUpdated: new Date().toISOString()
        },
        {
          id: 3,
          name: '패스트푸드',
          type: 'your_program',
          brandsCount: 4,
          storesCount: 32,
          employeesCount: 240,
          revenue: 22000000,
          status: 'active',
          lastUpdated: new Date().toISOString()
        },
        {
          id: 4,
          name: '베이커리',
          type: 'your_program',
          brandsCount: 3,
          storesCount: 18,
          employeesCount: 140,
          revenue: 12000000,
          status: 'active',
          lastUpdated: new Date().toISOString()
        },
        {
          id: 5,
          name: '주점',
          type: 'your_program',
          brandsCount: 4,
          storesCount: 17,
          employeesCount: 120,
          revenue: 8000000,
          status: 'active',
          lastUpdated: new Date().toISOString()
        }
      ];
      
      setStats(dummyStats);
      setIndustries(dummyIndustries);
    } catch (error) {
      console.error('업종 데이터 로드 오류:', error);
      toast.error('업종 데이터를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: keyof BrandFormData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const validateForm = (): { isValid: boolean; errors: string[] } => {
    const errors: string[] = [];
    
    if (!formData.brand_name.trim()) errors.push('브랜드명을 입력해주세요.');
    if (!formData.brand_description.trim()) errors.push('브랜드 설명을 입력해주세요.');
    if (!formData.admin_name.trim()) errors.push('관리자 이름을 입력해주세요.');
    if (!formData.admin_email.trim()) errors.push('관리자 이메일을 입력해주세요.');
    if (!formData.admin_phone.trim()) errors.push('관리자 연락처를 입력해주세요.');
    
    // 이메일 형식 검증
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (formData.admin_email && !emailRegex.test(formData.admin_email)) {
      errors.push('올바른 이메일 형식을 입력해주세요.');
    }
    
    // 전화번호 형식 검증
    const phoneRegex = /^[0-9-+\s()]{10,15}$/;
    if (formData.admin_phone && !phoneRegex.test(formData.admin_phone)) {
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
      // 실제로는 API 호출
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      toast.success('새 브랜드가 성공적으로 생성되었습니다.');
      setIsCreateDialogOpen(false);
      resetForm();
      loadIndustryData(); // 데이터 새로고침
    } catch (error) {
      console.error('브랜드 생성 오류:', error);
      toast.error('브랜드 생성에 실패했습니다.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setFormData({
      brand_name: '',
      brand_description: '',
      brand_contact_email: '',
      brand_contact_phone: '',
      brand_address: '',
      admin_name: '',
      admin_email: '',
      admin_phone: ''
    });
  };

  const getIndustryIcon = (type: string) => {
    switch (type) {
      case 'your_program':
        return <Building2 className="h-5 w-5" />;
      default:
        return <Store className="h-5 w-5" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-500/20 text-green-400 border-green-500/50';
      case 'inactive':
        return 'bg-red-500/20 text-red-400 border-red-500/50';
      case 'maintenance':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50';
      default:
        return 'bg-slate-500/20 text-slate-400 border-slate-500/50';
    }
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-400"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-purple-600 bg-clip-text text-transparent">
            업종 관리자 대시보드
          </h1>
          <p className="text-slate-400 mt-2">전체 업종 현황 및 관리</p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-cyan-500/20 text-cyan-400 border-cyan-500/50 hover:bg-cyan-500/30">
              <Plus className="h-4 w-4 mr-2" />
              새 브랜드 추가
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-slate-900 border-slate-700">
            <DialogHeader>
              <DialogTitle className="text-white">새 브랜드 추가</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="brand_name" className="text-white">브랜드명</Label>
                <Input
                  id="brand_name"
                  value={formData.brand_name}
                  onChange={(e) => handleInputChange('brand_name', e.target.value)}
                  className="bg-slate-800 border-slate-600 text-white"
                />
              </div>
              <div>
                <Label htmlFor="brand_description" className="text-white">브랜드 설명</Label>
                <Textarea
                  id="brand_description"
                  value={formData.brand_description}
                  onChange={(e) => handleInputChange('brand_description', e.target.value)}
                  className="bg-slate-800 border-slate-600 text-white"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="admin_name" className="text-white">관리자 이름</Label>
                  <Input
                    id="admin_name"
                    value={formData.admin_name}
                    onChange={(e) => handleInputChange('admin_name', e.target.value)}
                    className="bg-slate-800 border-slate-600 text-white"
                  />
                </div>
                <div>
                  <Label htmlFor="admin_email" className="text-white">관리자 이메일</Label>
                  <Input
                    id="admin_email"
                    type="email"
                    value={formData.admin_email}
                    onChange={(e) => handleInputChange('admin_email', e.target.value)}
                    className="bg-slate-800 border-slate-600 text-white"
                  />
                </div>
              </div>
              <div>
                <Label htmlFor="admin_phone" className="text-white">관리자 연락처</Label>
                <Input
                  id="admin_phone"
                  value={formData.admin_phone}
                  onChange={(e) => handleInputChange('admin_phone', e.target.value)}
                  className="bg-slate-800 border-slate-600 text-white"
                />
              </div>
              <div className="flex gap-2 pt-4">
                <Button
                  onClick={handleSubmit}
                  disabled={isSubmitting}
                  className="flex-1 bg-cyan-500/20 text-cyan-400 border-cyan-500/50 hover:bg-cyan-500/30"
                >
                  {isSubmitting ? '생성 중...' : '브랜드 생성'}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setIsCreateDialogOpen(false)}
                  className="border-slate-600 text-slate-400 hover:bg-slate-800"
                >
                  취소
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-black/50 border-cyan-500/20 backdrop-blur-xl">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">총 업종</p>
                <p className="text-2xl font-bold text-white">{stats.totalIndustries}</p>
              </div>
              <div className="w-12 h-12 bg-cyan-500/20 rounded-lg flex items-center justify-center">
                <Building2 className="h-6 w-6 text-cyan-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-black/50 border-emerald-500/20 backdrop-blur-xl">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">총 브랜드</p>
                <p className="text-2xl font-bold text-white">{stats.totalBrands}</p>
              </div>
              <div className="w-12 h-12 bg-emerald-500/20 rounded-lg flex items-center justify-center">
                <Store className="h-6 w-6 text-emerald-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-black/50 border-purple-500/20 backdrop-blur-xl">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">총 매장</p>
                <p className="text-2xl font-bold text-white">{stats.totalStores}</p>
              </div>
              <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center">
                <Users className="h-6 w-6 text-purple-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-black/50 border-yellow-500/20 backdrop-blur-xl">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">총 매출</p>
                <p className="text-2xl font-bold text-white">₩{(stats.totalRevenue / 1000000).toFixed(1)}M</p>
              </div>
              <div className="w-12 h-12 bg-yellow-500/20 rounded-lg flex items-center justify-center">
                <TrendingUp className="h-6 w-6 text-yellow-400" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 업종별 현황 */}
      <Card className="bg-black/50 border-slate-500/20 backdrop-blur-xl">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-cyan-400" />
            업종별 현황
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {industries.map((industry) => (
              <Card key={industry.id} className="bg-slate-800/50 border-slate-600 backdrop-blur-xl">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      {getIndustryIcon(industry.type)}
                      <h3 className="font-semibold text-white">{industry.name}</h3>
                    </div>
                    <Badge className={getStatusColor(industry.status)}>
                      {industry.status === 'active' ? '활성' : 
                       industry.status === 'inactive' ? '비활성' : '점검중'}
                    </Badge>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-400">브랜드:</span>
                      <span className="text-white">{industry.brandsCount}개</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-400">매장:</span>
                      <span className="text-white">{industry.storesCount}개</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-400">직원:</span>
                      <span className="text-white">{industry.employeesCount}명</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-400">매출:</span>
                      <span className="text-white">₩{(industry.revenue / 1000000).toFixed(1)}M</span>
                    </div>
                  </div>
                  
                  <div className="mt-3 pt-3 border-t border-slate-600">
                    <div className="flex justify-between text-xs text-slate-400">
                      <span>성장률</span>
                      <span>+{stats.growthRate}%</span>
                    </div>
                    <Progress value={stats.growthRate} className="mt-1" />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 최근 활동 */}
      <Card className="bg-black/50 border-slate-500/20 backdrop-blur-xl">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Activity className="h-5 w-5 text-cyan-400" />
            최근 활동
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[
              { action: '새 브랜드 등록', target: '스타벅스', time: '2시간 전', status: 'success' },
              { action: '매장 정보 업데이트', target: '카페베네 강남점', time: '4시간 전', status: 'info' },
              { action: '직원 계정 생성', target: '김철수 (매니저)', time: '6시간 전', status: 'success' },
              { action: '시스템 점검', target: '전체 시스템', time: '1일 전', status: 'warning' },
              { action: '매출 리포트 생성', target: '7월 월간 리포트', time: '1일 전', status: 'success' }
            ].map((activity, index) => (
              <div key={index} className="flex items-center gap-3 p-3 bg-slate-800/30 rounded-lg">
                <div className={`w-2 h-2 rounded-full ${
                  activity.status === 'success' ? 'bg-green-400' :
                  activity.status === 'warning' ? 'bg-yellow-400' :
                  'bg-blue-400'
                }`} />
                <div className="flex-1">
                  <p className="text-white text-sm">{activity.action} - {activity.target}</p>
                  <p className="text-slate-400 text-xs">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 
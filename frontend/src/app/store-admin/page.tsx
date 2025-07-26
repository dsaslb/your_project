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
  Mail,
  Clock,
  Calendar
} from 'lucide-react';

interface StoreStats {
  totalEmployees: number;
  activeEmployees: number;
  totalSales: number;
  dailySales: number;
  growthRate: number;
  pendingRequests: number;
}

interface Employee {
  id: number;
  name: string;
  email: string;
  phone: string;
  position: string;
  department: string;
  hire_date: string;
  status: 'active' | 'inactive' | 'pending';
  salary: number;
  performance_rating: number;
}

export default function StoreAdminDashboard() {
  const [stats, setStats] = useState<StoreStats>({
    totalEmployees: 0,
    activeEmployees: 0,
    totalSales: 0,
    dailySales: 0,
    growthRate: 0,
    pendingRequests: 0
  });

  const [employees, setEmployees] = useState<Employee[]>([]);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    position: '',
    department: '',
    salary: '',
    hire_date: ''
  });

  useEffect(() => {
    loadStoreData();
  }, []);

  const loadStoreData = async () => {
    try {
      const response = await fetch('/api/store/dashboard');
      const result = await response.json();

      if (result.success) {
        setStats(result.data.stats);
        setEmployees(result.data.employees);
      } else {
        toast.error('데이터 로드 중 오류가 발생했습니다.');
      }
    } catch (error) {
      console.error('데이터 로드 오류:', error);
      toast.error('네트워크 오류가 발생했습니다.');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const response = await fetch('/api/store/create_employee', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      const result = await response.json();

      if (result.success) {
        toast.success('직원 계정이 성공적으로 생성되었습니다!', {
          description: `임시 비밀번호: ${result.data.temp_password}`,
          duration: 10000,
        });
        
        // 폼 초기화
        setFormData({
          name: '',
          email: '',
          phone: '',
          position: '',
          department: '',
          salary: '',
          hire_date: ''
        });
        
        // 다이얼로그 닫기
        setIsCreateDialogOpen(false);
        
        // 데이터 새로고침
        await loadStoreData();
      } else {
        toast.error(result.error || '직원 생성 중 오류가 발생했습니다.');
      }
    } catch (error) {
      console.error('직원 생성 오류:', error);
      toast.error('네트워크 오류가 발생했습니다.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-400 border-green-400';
      case 'inactive': return 'text-red-400 border-red-400';
      case 'pending': return 'text-yellow-400 border-yellow-400';
      default: return 'text-gray-400 border-gray-400';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return '활성';
      case 'inactive': return '비활성';
      case 'pending': return '대기중';
      default: return '알 수 없음';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* 헤더 */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">
              매장 관리자 대시보드
            </h1>
            <p className="text-slate-300">
              매장 운영 및 직원 관리
            </p>
          </div>
          <div className="flex items-center gap-4">
            <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
              <DialogTrigger asChild>
                <Button className="bg-blue-600 hover:bg-blue-700 text-white">
                  <Plus className="h-4 w-4 mr-2" />
                  직원 계정 생성
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle className="text-xl font-semibold">
                    직원 계정 생성
                  </DialogTitle>
                </DialogHeader>
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="name">직원 이름 *</Label>
                      <Input
                        id="name"
                        value={formData.name}
                        onChange={(e) => setFormData({...formData, name: e.target.value})}
                        placeholder="직원 이름을 입력하세요"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="email">이메일 *</Label>
                      <Input
                        id="email"
                        type="email"
                        value={formData.email}
                        onChange={(e) => setFormData({...formData, email: e.target.value})}
                        placeholder="이메일을 입력하세요"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="phone">연락처 *</Label>
                      <Input
                        id="phone"
                        value={formData.phone}
                        onChange={(e) => setFormData({...formData, phone: e.target.value})}
                        placeholder="연락처를 입력하세요"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="position">직책 *</Label>
                      <Input
                        id="position"
                        value={formData.position}
                        onChange={(e) => setFormData({...formData, position: e.target.value})}
                        placeholder="직책을 입력하세요"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="department">부서</Label>
                      <Input
                        id="department"
                        value={formData.department}
                        onChange={(e) => setFormData({...formData, department: e.target.value})}
                        placeholder="부서를 입력하세요"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="salary">급여</Label>
                      <Input
                        id="salary"
                        type="number"
                        value={formData.salary}
                        onChange={(e) => setFormData({...formData, salary: e.target.value})}
                        placeholder="급여를 입력하세요"
                      />
                    </div>
                    <div className="space-y-2 md:col-span-2">
                      <Label htmlFor="hire_date">입사일 *</Label>
                      <Input
                        id="hire_date"
                        type="date"
                        value={formData.hire_date}
                        onChange={(e) => setFormData({...formData, hire_date: e.target.value})}
                        required
                      />
                    </div>
                  </div>
                  <div className="flex justify-end gap-3">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => setIsCreateDialogOpen(false)}
                    >
                      취소
                    </Button>
                    <Button type="submit" disabled={isSubmitting}>
                      {isSubmitting ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                          생성 중...
                        </>
                      ) : (
                        <>
                          <UserPlus className="h-4 w-4 mr-2" />
                          직원 생성
                        </>
                      )}
                    </Button>
                  </div>
                </form>
              </DialogContent>
            </Dialog>
            <Badge variant="outline" className="text-green-400 border-green-400">
              <Activity className="h-4 w-4 mr-1" />
              실시간 모니터링
            </Badge>
          </div>
        </div>

        {/* 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <Card className="bg-white/10 border-white/20 text-white">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">총 직원 수</CardTitle>
              <Users className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalEmployees}</div>
              <p className="text-xs text-slate-300">
                활성 직원: {stats.activeEmployees}명
              </p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 border-white/20 text-white">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">일일 매출</CardTitle>
              <TrendingUp className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {stats.dailySales.toLocaleString()}원
              </div>
              <p className="text-xs text-slate-300">
                성장률: +{stats.growthRate}%
              </p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 border-white/20 text-white">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">대기 요청</CardTitle>
              <AlertTriangle className="h-4 w-4 text-yellow-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.pendingRequests}</div>
              <p className="text-xs text-slate-300">
                승인 대기 중
              </p>
            </CardContent>
          </Card>
        </div>

        {/* 직원 목록 */}
        <Card className="bg-white/10 border-white/20 text-white">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              직원 관리
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/20">
                    <th className="text-left py-3 px-4">이름</th>
                    <th className="text-left py-3 px-4">직책</th>
                    <th className="text-left py-3 px-4">부서</th>
                    <th className="text-left py-3 px-4">연락처</th>
                    <th className="text-left py-3 px-4">입사일</th>
                    <th className="text-left py-3 px-4">상태</th>
                    <th className="text-left py-3 px-4">성과</th>
                  </tr>
                </thead>
                <tbody>
                  {employees.map((employee) => (
                    <tr key={employee.id} className="border-b border-white/10 hover:bg-white/5">
                      <td className="py-3 px-4">
                        <div>
                          <div className="font-medium">{employee.name}</div>
                          <div className="text-xs text-slate-300">{employee.email}</div>
                        </div>
                      </td>
                      <td className="py-3 px-4">{employee.position}</td>
                      <td className="py-3 px-4">{employee.department}</td>
                      <td className="py-3 px-4">{employee.phone}</td>
                      <td className="py-3 px-4">{employee.hire_date}</td>
                      <td className="py-3 px-4">
                        <Badge 
                          variant="outline" 
                          className={getStatusColor(employee.status)}
                        >
                          {getStatusText(employee.status)}
                        </Badge>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <div className="w-16 bg-slate-700 rounded-full h-2">
                            <div 
                              className="bg-blue-500 h-2 rounded-full" 
                              style={{ width: `${employee.performance_rating}%` }}
                            ></div>
                          </div>
                          <span className="text-xs">{employee.performance_rating}%</span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 
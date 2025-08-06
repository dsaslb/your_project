'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../src/components/ui/card';
import { Button } from '../../src/components/ui/button';
import { Input } from '../../src/components/ui/input';
import { Badge } from '../../src/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '../../src/components/ui/dialog';
import { Label } from '../../src/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../src/components/ui/select';
import { Switch } from '../../src/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../src/components/ui/tabs';
import { apiClient } from '../../src/lib/api-client';
import { useLoadingState } from '../../src/hooks/useLoadingState';
import { useErrorHandler } from '../../src/hooks/useErrorHandler';
import { toast } from 'sonner';
import { 
  Users, 
  Shield, 
  Bell, 
  Plus,
  Edit,
  Trash2,
  Save,
  UserCheck,
  UserX,
  Activity
} from 'lucide-react';

interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: 'admin' | 'manager' | 'employee' | 'viewer';
  status: 'active' | 'inactive' | 'suspended';
  last_login?: string;
  created_at: string;
}

interface UserFormData {
  username: string;
  email: string;
  full_name: string;
  role: 'admin' | 'manager' | 'employee' | 'viewer';
  password?: string;
  confirm_password?: string;
}

export default function Settings() {
  const [users, setUsers] = useState<User[]>([]);
  const [activeTab, setActiveTab] = useState('users');
  const [isUserDialogOpen, setIsUserDialogOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  
  const [userFormData, setUserFormData] = useState<UserFormData>({
    username: '',
    email: '',
    full_name: '',
    role: 'employee',
    password: '',
    confirm_password: '',
  });

  const { isLoading, setLoading } = useLoadingState();
  const { handleError } = useErrorHandler();

  // 사용자 목록 조회
  const fetchUsers = async () => {
    try {
      const response = await apiClient.get('/api/users');
      if (response.success && response.data) {
        setUsers(response.data);
      }
    } catch (error) {
      handleError(error as Error);
    }
  };

  // 초기 데이터 로드
  useEffect(() => {
    fetchUsers();
  }, []);

  // 사용자 폼 초기화
  const resetUserForm = () => {
    setUserFormData({
      username: '',
      email: '',
      full_name: '',
      role: 'employee',
      password: '',
      confirm_password: '',
    });
  };

  // 사용자 생성/수정 제출
  const handleUserSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!userFormData.username || !userFormData.email || !userFormData.full_name) {
      toast.error('필수 정보를 입력해주세요.');
      return;
    }

    if (!editingUser && (!userFormData.password || !userFormData.confirm_password)) {
      toast.error('비밀번호를 입력해주세요.');
      return;
    }

    if (userFormData.password && userFormData.password !== userFormData.confirm_password) {
      toast.error('비밀번호가 일치하지 않습니다.');
      return;
    }

    try {
      setLoading(true);
      
      if (editingUser) {
        const response = await apiClient.put(`/api/users/${editingUser.id}`, userFormData);
        if (response.success) {
          toast.success('사용자가 성공적으로 수정되었습니다.');
          setIsUserDialogOpen(false);
          setEditingUser(null);
          resetUserForm();
          fetchUsers();
        }
      } else {
        const response = await apiClient.post('/api/users', userFormData);
        if (response.success) {
          toast.success('사용자가 성공적으로 생성되었습니다.');
          setIsUserDialogOpen(false);
          resetUserForm();
          fetchUsers();
        }
      }
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 사용자 삭제
  const handleDeleteUser = async (user: User) => {
    if (!confirm(`정말로 ${user.full_name} 사용자를 삭제하시겠습니까?`)) {
      return;
    }

    try {
      setLoading(true);
      const response = await apiClient.delete(`/api/users/${user.id}`);
      if (response.success) {
        toast.success('사용자가 성공적으로 삭제되었습니다.');
        fetchUsers();
      }
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 사용자 상태 변경
  const handleToggleUserStatus = async (user: User) => {
    const newStatus = user.status === 'active' ? 'inactive' : 'active';
    
    try {
      setLoading(true);
      const response = await apiClient.put(`/api/users/${user.id}/status`, { status: newStatus });
      if (response.success) {
        toast.success(`사용자 상태가 ${newStatus === 'active' ? '활성화' : '비활성화'}되었습니다.`);
        fetchUsers();
      }
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 사용자 수정 모드 시작
  const handleEditUser = (user: User) => {
    setEditingUser(user);
    setUserFormData({
      username: user.username,
      email: user.email,
      full_name: user.full_name,
      role: user.role,
      password: '',
      confirm_password: '',
    });
    setIsUserDialogOpen(true);
  };

  // 새 사용자 생성 모드 시작
  const handleCreateUser = () => {
    setEditingUser(null);
    resetUserForm();
    setIsUserDialogOpen(true);
  };

  // 역할별 색상
  const getRoleColor = (role: string) => {
    switch (role) {
      case 'admin': return 'bg-red-500/20 text-red-400 border border-red-500/30';
      case 'manager': return 'bg-blue-500/20 text-blue-400 border border-blue-500/30';
      case 'employee': return 'bg-green-500/20 text-green-400 border border-green-500/30';
      case 'viewer': return 'bg-gray-500/20 text-gray-400 border border-gray-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border border-gray-500/30';
    }
  };

  // 상태별 색상
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500/20 text-green-400 border border-green-500/30';
      case 'inactive': return 'bg-gray-500/20 text-gray-400 border border-gray-500/30';
      case 'suspended': return 'bg-red-500/20 text-red-400 border border-red-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border border-gray-500/30';
    }
  };

  // 통계 계산
  const totalUsers = users.length;
  const activeUsers = users.filter(u => u.status === 'active').length;
  const adminUsers = users.filter(u => u.role === 'admin').length;
  const recentLogins = users.filter(u => u.last_login && new Date(u.last_login) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)).length;

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Settings className="h-8 w-8 text-blue-600" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">시스템 설정</h1>
            <p className="text-gray-600">사용자 관리, 시스템 설정, 보안 설정을 관리하세요</p>
          </div>
        </div>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <Users className="h-8 w-8 text-blue-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">총 사용자</p>
                <p className="text-2xl font-bold text-gray-900">{totalUsers.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <UserCheck className="h-8 w-8 text-green-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">활성 사용자</p>
                <p className="text-2xl font-bold text-gray-900">{activeUsers.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <Shield className="h-8 w-8 text-red-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">관리자</p>
                <p className="text-2xl font-bold text-gray-900">{adminUsers.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <Activity className="h-8 w-8 text-purple-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">최근 로그인</p>
                <p className="text-2xl font-bold text-gray-900">{recentLogins.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 설정 탭 */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="users">사용자 관리</TabsTrigger>
          <TabsTrigger value="system">시스템 설정</TabsTrigger>
          <TabsTrigger value="security">보안 설정</TabsTrigger>
          <TabsTrigger value="notifications">알림 설정</TabsTrigger>
        </TabsList>

        {/* 사용자 관리 탭 */}
        <TabsContent value="users" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>사용자 목록</CardTitle>
                  <CardDescription>시스템 사용자를 관리하세요</CardDescription>
                </div>
                <Button onClick={handleCreateUser} className="bg-blue-600 hover:bg-blue-700">
                  <Plus className="h-4 w-4 mr-2" />
                  새 사용자 추가
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {users.map((user) => (
                  <div key={user.id} className="border rounded-lg p-4 hover:bg-gray-50">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="text-lg font-semibold text-gray-900">{user.full_name}</h3>
                          <Badge className={getRoleColor(user.role)}>
                            {user.role === 'admin' && '관리자'}
                            {user.role === 'manager' && '매니저'}
                            {user.role === 'employee' && '직원'}
                            {user.role === 'viewer' && '조회자'}
                          </Badge>
                          <Badge className={getStatusColor(user.status)}>
                            {user.status === 'active' && '활성'}
                            {user.status === 'inactive' && '비활성'}
                            {user.status === 'suspended' && '정지'}
                          </Badge>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-500">
                          <div>
                            <span className="font-medium">사용자명:</span> {user.username}
                          </div>
                          <div>
                            <span className="font-medium">이메일:</span> {user.email}
                          </div>
                          <div>
                            <span className="font-medium">마지막 로그인:</span> {user.last_login ? new Date(user.last_login).toLocaleString('ko-KR') : '로그인 기록 없음'}
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleToggleUserStatus(user)}
                        >
                          {user.status === 'active' ? <UserX className="h-4 w-4" /> : <UserCheck className="h-4 w-4" />}
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEditUser(user)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDeleteUser(user)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
                
                {users.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    <Users className="h-12 w-12 mx-auto mb-2" />
                    <p>사용자가 없습니다.</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 시스템 설정 탭 */}
        <TabsContent value="system" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>시스템 설정</CardTitle>
              <CardDescription>기본 시스템 설정을 관리하세요</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-500">
                <Settings className="h-12 w-12 mx-auto mb-2" />
                <p>시스템 설정 기능이 준비 중입니다.</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 보안 설정 탭 */}
        <TabsContent value="security" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>보안 설정</CardTitle>
              <CardDescription>보안 관련 설정을 관리하세요</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-500">
                <Shield className="h-12 w-12 mx-auto mb-2" />
                <p>보안 설정 기능이 준비 중입니다.</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 알림 설정 탭 */}
        <TabsContent value="notifications" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>알림 설정</CardTitle>
              <CardDescription>알림 관련 설정을 관리하세요</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-500">
                <Bell className="h-12 w-12 mx-auto mb-2" />
                <p>알림 설정 기능이 준비 중입니다.</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* 사용자 생성/수정 다이얼로그 */}
      <Dialog open={isUserDialogOpen} onOpenChange={setIsUserDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              {editingUser ? '사용자 수정' : '새 사용자 생성'}
            </DialogTitle>
            <DialogDescription>
              {editingUser ? '사용자 정보를 수정하세요.' : '새로운 사용자를 생성하세요.'}
            </DialogDescription>
          </DialogHeader>
          
          <form onSubmit={handleUserSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="username">사용자명 *</Label>
                <Input
                  id="username"
                  value={userFormData.username}
                  onChange={(e) => setUserFormData({ ...userFormData, username: e.target.value })}
                  required
                />
              </div>
              
              <div>
                <Label htmlFor="email">이메일 *</Label>
                <Input
                  id="email"
                  type="email"
                  value={userFormData.email}
                  onChange={(e) => setUserFormData({ ...userFormData, email: e.target.value })}
                  required
                />
              </div>
            </div>
            
            <div>
              <Label htmlFor="full_name">전체 이름 *</Label>
              <Input
                id="full_name"
                value={userFormData.full_name}
                onChange={(e) => setUserFormData({ ...userFormData, full_name: e.target.value })}
                required
              />
            </div>
            
            <div>
              <Label htmlFor="role">역할</Label>
              <Select value={userFormData.role} onValueChange={(value: any) => setUserFormData({ ...userFormData, role: value })}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="admin">관리자</SelectItem>
                  <SelectItem value="manager">매니저</SelectItem>
                  <SelectItem value="employee">직원</SelectItem>
                  <SelectItem value="viewer">조회자</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            {!editingUser && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="password">비밀번호 *</Label>
                  <Input
                    id="password"
                    type="password"
                    value={userFormData.password}
                    onChange={(e) => setUserFormData({ ...userFormData, password: e.target.value })}
                    required
                  />
                </div>
                
                <div>
                  <Label htmlFor="confirm_password">비밀번호 확인 *</Label>
                  <Input
                    id="confirm_password"
                    type="password"
                    value={userFormData.confirm_password}
                    onChange={(e) => setUserFormData({ ...userFormData, confirm_password: e.target.value })}
                    required
                  />
                </div>
              </div>
            )}
            
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setIsUserDialogOpen(false)}>
                취소
              </Button>
              <Button type="submit" disabled={isLoading}>
                {isLoading ? '처리 중...' : (editingUser ? '수정' : '생성')}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
} 
'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Badge } from '../../components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../../components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { Switch } from '../../components/ui/switch';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { 
  Users, 
  Shield, 
  UserPlus, 
  Lock, 
  Unlock, 
  Eye, 
  EyeOff,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  Activity,
  Settings,
  Key,
  UserCheck,
  UserX,
  ShieldCheck,
  AlertCircle,
  Info
} from 'lucide-react';
// import { useLoadingState } from '../../hooks/useLoadingState';
import { useErrorHandler } from '../../hooks/useErrorHandler';
import { apiClient } from '../../lib/api-client';

interface User {
  user_id: string;
  username: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  is_locked: boolean;
  failed_login_attempts: number;
  last_login?: string;
  created_at?: string;
  updated_at?: string;
}

interface Role {
  role_id: string;
  name: string;
  description: string;
  permissions: string[];
  is_active: boolean;
  created_at?: string;
}

interface Permission {
  permission_id: string;
  name: string;
  description: string;
  resource: string;
  action: string;
  is_active: boolean;
}

interface SecurityEvent {
  event_id: string;
  user_id?: string;
  event_type: string;
  ip_address: string;
  user_agent: string;
  details: any;
  timestamp: string;
  severity: string;
}

interface UserFormData {
  username: string;
  email: string;
  password: string;
  full_name: string;
  role: string;
}

export default function AuthPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { handleApiError } = useErrorHandler();
  
  // 성공 메시지 표시 함수
  const showSuccess = (message: string) => {
    if (typeof window !== 'undefined' && (window as any).toast) {
      (window as any).toast.success(message);
    }
  };
  
  const [users, setUsers] = useState<User[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [securityEvents, setSecurityEvents] = useState<SecurityEvent[]>([]);
  const [authStats, setAuthStats] = useState<{
    total_users: number;
    total_roles: number;
    total_permissions: number;
    active_sessions: number;
  } | null>(null);
  
  const [showCreateUserDialog, setShowCreateUserDialog] = useState(false);
  const [showPasswordDialog, setShowPasswordDialog] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  
  const [userForm, setUserForm] = useState<UserFormData>({
    username: '',
    email: '',
    password: '',
    full_name: '',
    role: 'employee'
  });
  
  const [passwordForm, setPasswordForm] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });

  // 데이터 로딩 함수들
  const loadUsers = useCallback(async () => {
    try {
      const response = await apiClient.get('/api/auth/users');
      if (response.success) {
        setUsers(response.data);
      }
    } catch (error) {
      console.error('사용자 로딩 오류:', error);
    }
  }, []);

  const loadRoles = useCallback(async () => {
    try {
      const response = await apiClient.get('/api/auth/roles');
      if (response.success) {
        setRoles(response.data);
      }
    } catch (error) {
      console.error('역할 로딩 오류:', error);
    }
  }, []);

  const loadPermissions = useCallback(async () => {
    try {
      const response = await apiClient.get('/api/auth/permissions');
      if (response.success) {
        setPermissions(response.data);
      }
    } catch (error) {
      console.error('권한 로딩 오류:', error);
    }
  }, []);

  const loadSecurityEvents = useCallback(async () => {
    try {
      const response = await apiClient.get('/api/auth/security-events?limit=50');
      if (response.success) {
        setSecurityEvents(response.data);
      }
    } catch (error) {
      console.error('보안 이벤트 로딩 오류:', error);
    }
  }, []);

  const loadAuthStats = useCallback(async () => {
    try {
      const response = await apiClient.get('/api/auth/health');
      if (response.success) {
        setAuthStats(response.data);
      }
    } catch (error) {
      console.error('인증 통계 로딩 오류:', error);
    }
  }, []);

  // 이벤트 핸들러들
  const handleCreateUser = async () => {
    try {
      setIsLoading(true);
      const response = await apiClient.post('/api/auth/users', userForm);
      if (response.success) {
        showSuccess('사용자가 생성되었습니다');
        setShowCreateUserDialog(false);
        setUserForm({
          username: '',
          email: '',
          password: '',
          full_name: '',
          role: 'employee'
        });
        await loadUsers();
      }
    } catch (err) {
      setError('사용자 생성에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUnlockUser = async (userId: string) => {
    try {
      setIsLoading(true);
      const response = await apiClient.post(`/api/auth/users/${userId}/unlock`);
      if (response.success) {
        showSuccess('계정 잠금이 해제되었습니다');
        await loadUsers();
      }
    } catch (err) {
      setError('계정 잠금 해제에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChangePassword = async () => {
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      handleApiError('새 비밀번호가 일치하지 않습니다');
      return;
    }

    try {
      setIsLoading(true);
      const response = await apiClient.post('/api/auth/change-password', {
        current_password: passwordForm.current_password,
        new_password: passwordForm.new_password
      });
      if (response.success) {
        showSuccess('비밀번호가 변경되었습니다');
        setShowPasswordDialog(false);
        setPasswordForm({
          current_password: '',
          new_password: '',
          confirm_password: ''
        });
      }
    } catch (err) {
      setError('비밀번호 변경에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  const handleValidatePassword = async (password: string) => {
    try {
      const response = await apiClient.post('/api/auth/validate-password', {
        password
      });
      if (response.success) {
        return response.data;
      }
    } catch (error) {
      console.error('비밀번호 검증 오류:', error);
    }
    return null;
  };

  // 유틸리티 함수들
  const getRoleColor = (role: string) => {
    switch (role) {
      case 'admin': return 'bg-red-100 text-red-800';
      case 'manager': return 'bg-blue-100 text-blue-800';
      case 'employee': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (isActive: boolean, isLocked: boolean) => {
    if (isLocked) return 'bg-red-100 text-red-800';
    if (isActive) return 'bg-green-100 text-green-800';
    return 'bg-gray-100 text-gray-800';
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800';
      case 'error': return 'bg-orange-100 text-orange-800';
      case 'warning': return 'bg-yellow-100 text-yellow-800';
      case 'info': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getEventTypeIcon = (eventType: string) => {
    switch (eventType) {
      case 'login_success': return <CheckCircle className="w-4 h-4" />;
      case 'login_failed': return <XCircle className="w-4 h-4" />;
      case 'logout': return <UserX className="w-4 h-4" />;
      case 'password_change_success': return <Key className="w-4 h-4" />;
      case 'password_change_failed': return <AlertTriangle className="w-4 h-4" />;
      case 'account_locked': return <Lock className="w-4 h-4" />;
      default: return <Info className="w-4 h-4" />;
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString('ko-KR');
  };

  const getEventTypeText = (eventType: string) => {
    switch (eventType) {
      case 'login_success': return '로그인 성공';
      case 'login_failed': return '로그인 실패';
      case 'logout': return '로그아웃';
      case 'password_change_success': return '비밀번호 변경 성공';
      case 'password_change_failed': return '비밀번호 변경 실패';
      case 'account_locked': return '계정 잠금';
      default: return eventType;
    }
  };

  // 초기 데이터 로딩
  useEffect(() => {
    const loadAllData = async () => {
      await Promise.all([
        loadUsers(),
        loadRoles(),
        loadPermissions(),
        loadSecurityEvents(),
        loadAuthStats()
      ]);
    };

    loadAllData();
  }, [loadUsers, loadRoles, loadPermissions, loadSecurityEvents, loadAuthStats]);

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">인증 및 권한 관리</h1>
          <p className="text-gray-600">사용자 인증, 역할 관리, 보안 모니터링</p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowPasswordDialog(true)}
          >
            <Key className="w-4 h-4 mr-2" />
            비밀번호 변경
          </Button>
          <Button
            onClick={() => setShowCreateUserDialog(true)}
            disabled={isLoading}
          >
            <UserPlus className="w-4 h-4 mr-2" />
            사용자 생성
          </Button>
        </div>
      </div>

      {/* 인증 통계 */}
      {authStats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">총 사용자</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{authStats.total_users}</div>
              <p className="text-xs text-muted-foreground mt-2">
                등록된 사용자 수
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">역할</CardTitle>
              <Shield className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{authStats.total_roles}</div>
              <p className="text-xs text-muted-foreground mt-2">
                정의된 역할 수
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">권한</CardTitle>
              <ShieldCheck className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{authStats.total_permissions}</div>
              <p className="text-xs text-muted-foreground mt-2">
                시스템 권한 수
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">활성 세션</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{authStats.active_sessions}</div>
              <p className="text-xs text-muted-foreground mt-2">
                현재 로그인 세션
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 메인 탭 */}
      <Tabs defaultValue="users" className="space-y-4">
        <TabsList>
          <TabsTrigger value="users">사용자 관리</TabsTrigger>
          <TabsTrigger value="roles">역할 관리</TabsTrigger>
          <TabsTrigger value="permissions">권한 관리</TabsTrigger>
          <TabsTrigger value="security">보안 이벤트</TabsTrigger>
        </TabsList>

        {/* 사용자 관리 탭 */}
        <TabsContent value="users" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>사용자 목록</CardTitle>
              <CardDescription>
                시스템에 등록된 사용자들을 관리합니다
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {users.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <Users className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                    <p>등록된 사용자가 없습니다</p>
                  </div>
                ) : (
                  users.map((user) => (
                    <div
                      key={user.user_id}
                      className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
                    >
                      <div className="flex items-center gap-4">
                        <div className="flex-shrink-0">
                          <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                            <Users className="w-5 h-5 text-gray-600" />
                          </div>
                        </div>
                        <div>
                          <div className="font-medium">{user.full_name}</div>
                          <div className="text-sm text-gray-500">
                            {user.username} • {user.email}
                          </div>
                          <div className="flex items-center gap-2 mt-1">
                            <Badge className={getRoleColor(user.role)}>
                              {user.role}
                            </Badge>
                            <Badge className={getStatusColor(user.is_active, user.is_locked)}>
                              {user.is_locked ? '잠김' : user.is_active ? '활성' : '비활성'}
                            </Badge>
                            {user.failed_login_attempts > 0 && (
                              <Badge variant="outline" className="text-orange-600">
                                실패 {user.failed_login_attempts}회
                              </Badge>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {user.is_locked && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleUnlockUser(user.user_id)}
                          >
                            <Unlock className="w-4 h-4 mr-1" />
                            잠금 해제
                          </Button>
                        )}
                        <div className="text-sm text-gray-500">
                          마지막 로그인: {formatDate(user.last_login)}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 역할 관리 탭 */}
        <TabsContent value="roles" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>역할 목록</CardTitle>
              <CardDescription>
                시스템에서 사용되는 역할들을 관리합니다
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {roles.map((role) => (
                  <div
                    key={role.role_id}
                    className="flex items-center justify-between p-4 border rounded-lg"
                  >
                    <div>
                      <div className="font-medium">{role.name}</div>
                      <div className="text-sm text-gray-500">{role.description}</div>
                      <div className="flex flex-wrap gap-1 mt-2">
                        {role.permissions.map((permission) => (
                          <Badge key={permission} variant="outline" className="text-xs">
                            {permission}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={role.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                        {role.is_active ? '활성' : '비활성'}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 권한 관리 탭 */}
        <TabsContent value="permissions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>권한 목록</CardTitle>
              <CardDescription>
                시스템에서 사용되는 권한들을 관리합니다
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {permissions.map((permission) => (
                  <div
                    key={permission.permission_id}
                    className="flex items-center justify-between p-4 border rounded-lg"
                  >
                    <div>
                      <div className="font-medium">{permission.name}</div>
                      <div className="text-sm text-gray-500">{permission.description}</div>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge variant="outline" className="text-xs">
                          {permission.resource}
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          {permission.action}
                        </Badge>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={permission.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                        {permission.is_active ? '활성' : '비활성'}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 보안 이벤트 탭 */}
        <TabsContent value="security" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>보안 이벤트</CardTitle>
              <CardDescription>
                시스템 보안 관련 이벤트들을 모니터링합니다
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {securityEvents.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <Shield className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                    <p>보안 이벤트가 없습니다</p>
                  </div>
                ) : (
                  securityEvents.map((event) => (
                    <div
                      key={event.event_id}
                      className="flex items-center justify-between p-4 border rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-full ${getSeverityColor(event.severity)}`}>
                          {getEventTypeIcon(event.event_type)}
                        </div>
                        <div>
                          <div className="font-medium">{getEventTypeText(event.event_type)}</div>
                          <div className="text-sm text-gray-500">
                            {event.user_id ? `사용자 ID: ${event.user_id}` : '익명 사용자'}
                          </div>
                          <div className="text-xs text-gray-400 mt-1">
                            IP: {event.ip_address} • {formatDate(event.timestamp)}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className={getSeverityColor(event.severity)}>
                          {event.severity}
                        </Badge>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* 사용자 생성 다이얼로그 */}
      <Dialog open={showCreateUserDialog} onOpenChange={setShowCreateUserDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>새 사용자 생성</DialogTitle>
            <DialogDescription>
              새로운 사용자 계정을 생성합니다
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">사용자명</label>
              <Input
                value={userForm.username}
                onChange={(e) => setUserForm({...userForm, username: e.target.value})}
                placeholder="사용자명을 입력하세요"
              />
            </div>
            <div>
              <label className="text-sm font-medium">이메일</label>
              <Input
                type="email"
                value={userForm.email}
                onChange={(e) => setUserForm({...userForm, email: e.target.value})}
                placeholder="이메일을 입력하세요"
              />
            </div>
            <div>
              <label className="text-sm font-medium">비밀번호</label>
              <div className="relative">
                <Input
                  type={showPassword ? 'text' : 'password'}
                  value={userForm.password}
                  onChange={(e) => setUserForm({...userForm, password: e.target.value})}
                  placeholder="비밀번호를 입력하세요"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </Button>
              </div>
            </div>
            <div>
              <label className="text-sm font-medium">이름</label>
              <Input
                value={userForm.full_name}
                onChange={(e) => setUserForm({...userForm, full_name: e.target.value})}
                placeholder="전체 이름을 입력하세요"
              />
            </div>
            <div>
              <label className="text-sm font-medium">역할</label>
              <select
                value={userForm.role}
                onChange={(e) => setUserForm({...userForm, role: e.target.value})}
                className="w-full border rounded px-3 py-2"
              >
                <option value="employee">직원</option>
                <option value="manager">매니저</option>
                <option value="admin">관리자</option>
              </select>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setShowCreateUserDialog(false)}>
                취소
              </Button>
              <Button onClick={handleCreateUser}>
                생성
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* 비밀번호 변경 다이얼로그 */}
      <Dialog open={showPasswordDialog} onOpenChange={setShowPasswordDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>비밀번호 변경</DialogTitle>
            <DialogDescription>
              현재 비밀번호를 확인하고 새 비밀번호로 변경합니다
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">현재 비밀번호</label>
              <Input
                type="password"
                value={passwordForm.current_password}
                onChange={(e) => setPasswordForm({...passwordForm, current_password: e.target.value})}
                placeholder="현재 비밀번호를 입력하세요"
              />
            </div>
            <div>
              <label className="text-sm font-medium">새 비밀번호</label>
              <Input
                type="password"
                value={passwordForm.new_password}
                onChange={(e) => setPasswordForm({...passwordForm, new_password: e.target.value})}
                placeholder="새 비밀번호를 입력하세요"
              />
            </div>
            <div>
              <label className="text-sm font-medium">새 비밀번호 확인</label>
              <Input
                type="password"
                value={passwordForm.confirm_password}
                onChange={(e) => setPasswordForm({...passwordForm, confirm_password: e.target.value})}
                placeholder="새 비밀번호를 다시 입력하세요"
              />
            </div>
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                비밀번호는 최소 8자 이상이며, 대문자, 숫자, 특수문자를 포함해야 합니다.
              </AlertDescription>
            </Alert>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setShowPasswordDialog(false)}>
                취소
              </Button>
              <Button onClick={handleChangePassword}>
                변경
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
} 
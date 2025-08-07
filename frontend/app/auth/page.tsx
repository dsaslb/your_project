'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import { Alert, AlertDescription } from '@/components/ui/alert';
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
import { toast } from 'sonner';

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

// 샘플 데이터
const sampleUsers: User[] = [
  {
    user_id: '1',
    username: 'admin',
    email: 'admin@example.com',
    full_name: '관리자',
    role: 'admin',
    is_active: true,
    is_locked: false,
    failed_login_attempts: 0,
    last_login: '2024-01-15T10:30:00Z',
    created_at: '2024-01-01T00:00:00Z'
  },
  {
    user_id: '2',
    username: 'user1',
    email: 'user1@example.com',
    full_name: '사용자1',
    role: 'user',
    is_active: true,
    is_locked: false,
    failed_login_attempts: 0,
    last_login: '2024-01-15T09:15:00Z',
    created_at: '2024-01-01T00:00:00Z'
  },
  {
    user_id: '3',
    username: 'user2',
    email: 'user2@example.com',
    full_name: '사용자2',
    role: 'user',
    is_active: false,
    is_locked: true,
    failed_login_attempts: 5,
    last_login: '2024-01-14T15:20:00Z',
    created_at: '2024-01-01T00:00:00Z'
  }
];

const sampleRoles: Role[] = [
  {
    role_id: '1',
    name: 'admin',
    description: '시스템 관리자',
    permissions: ['read', 'write', 'delete', 'admin'],
    is_active: true,
    created_at: '2024-01-01T00:00:00Z'
  },
  {
    role_id: '2',
    name: 'user',
    description: '일반 사용자',
    permissions: ['read', 'write'],
    is_active: true,
    created_at: '2024-01-01T00:00:00Z'
  },
  {
    role_id: '3',
    name: 'guest',
    description: '게스트 사용자',
    permissions: ['read'],
    is_active: true,
    created_at: '2024-01-01T00:00:00Z'
  }
];

const sampleSecurityEvents: SecurityEvent[] = [
  {
    event_id: '1',
    user_id: '1',
    event_type: 'login_success',
    ip_address: '192.168.1.100',
    user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    details: { browser: 'Chrome', os: 'Windows' },
    timestamp: '2024-01-15T10:30:00Z',
    severity: 'info'
  },
  {
    event_id: '2',
    user_id: '3',
    event_type: 'login_failed',
    ip_address: '192.168.1.101',
    user_agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    details: { reason: 'Invalid password' },
    timestamp: '2024-01-15T10:25:00Z',
    severity: 'warning'
  },
  {
    event_id: '3',
    event_type: 'account_locked',
    ip_address: '192.168.1.101',
    user_agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    details: { reason: 'Too many failed attempts' },
    timestamp: '2024-01-15T10:20:00Z',
    severity: 'critical'
  }
];

export default function AuthPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [users, setUsers] = useState<User[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [securityEvents, setSecurityEvents] = useState<SecurityEvent[]>([]);
  const [showCreateUserDialog, setShowCreateUserDialog] = useState(false);
  const [showChangePasswordDialog, setShowChangePasswordDialog] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [userForm, setUserForm] = useState<UserFormData>({
    username: '',
    email: '',
    password: '',
    full_name: '',
    role: ''
  });
  const [passwordForm, setPasswordForm] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // 데이터 로드 함수들
  const loadUsers = useCallback(async () => {
    try {
      setUsers(sampleUsers);
    } catch (error) {
      toast.error('사용자 목록을 불러오는데 실패했습니다');
    }
  }, []);

  const loadRoles = useCallback(async () => {
    try {
      setRoles(sampleRoles);
    } catch (error) {
      toast.error('역할 목록을 불러오는데 실패했습니다');
    }
  }, []);

  const loadSecurityEvents = useCallback(async () => {
    try {
      setSecurityEvents(sampleSecurityEvents);
    } catch (error) {
      toast.error('보안 이벤트를 불러오는데 실패했습니다');
    }
  }, []);

  // 사용자 관리
  const handleCreateUser = async () => {
    if (!userForm.username || !userForm.email || !userForm.password || !userForm.full_name || !userForm.role) {
      toast.error('모든 필드를 입력해주세요');
      return;
    }

    setIsLoading(true);
    try {
      const newUser: User = {
        user_id: (users.length + 1).toString(),
        username: userForm.username,
        email: userForm.email,
        full_name: userForm.full_name,
        role: userForm.role,
        is_active: true,
        is_locked: false,
        failed_login_attempts: 0,
        created_at: new Date().toISOString()
      };
      
      setUsers(prev => [...prev, newUser]);
      setShowCreateUserDialog(false);
      setUserForm({
        username: '',
        email: '',
        password: '',
        full_name: '',
        role: ''
      });
      toast.success('사용자가 생성되었습니다');
    } catch (error) {
      toast.error('사용자 생성에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleUserStatus = async (userId: string, isActive: boolean) => {
    setIsLoading(true);
    try {
      setUsers(prev => prev.map(user => 
        user.user_id === userId ? { ...user, is_active: isActive } : user
      ));
      toast.success(`사용자가 ${isActive ? '활성화' : '비활성화'}되었습니다`);
    } catch (error) {
      toast.error('사용자 상태 변경에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUnlockUser = async (userId: string) => {
    setIsLoading(true);
    try {
      setUsers(prev => prev.map(user => 
        user.user_id === userId ? { ...user, is_locked: false, failed_login_attempts: 0 } : user
      ));
      toast.success('사용자 계정이 잠금 해제되었습니다');
    } catch (error) {
      toast.error('사용자 잠금 해제에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChangePassword = async () => {
    if (!passwordForm.new_password || passwordForm.new_password !== passwordForm.confirm_password) {
      toast.error('새 비밀번호가 일치하지 않습니다');
      return;
    }

    setIsLoading(true);
    try {
      toast.success('비밀번호가 변경되었습니다');
      setShowChangePasswordDialog(false);
      setPasswordForm({
        current_password: '',
        new_password: '',
        confirm_password: ''
      });
    } catch (error) {
      toast.error('비밀번호 변경에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  const handleValidatePassword = async (password: string) => {
    // 비밀번호 유효성 검사 로직
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumbers = /\d/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
    const isLongEnough = password.length >= 8;

    return {
      isValid: hasUpperCase && hasLowerCase && hasNumbers && hasSpecialChar && isLongEnough,
      checks: {
        hasUpperCase,
        hasLowerCase,
        hasNumbers,
        hasSpecialChar,
        isLongEnough
      }
    };
  };

  // 유틸리티 함수들
  const getRoleColor = (role: string) => {
    switch (role) {
      case 'admin': return 'bg-red-500/20 text-red-400';
      case 'user': return 'bg-blue-500/20 text-blue-400';
      case 'guest': return 'bg-gray-500/20 text-gray-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  const getStatusColor = (isActive: boolean, isLocked: boolean) => {
    if (isLocked) return 'bg-red-500/20 text-red-400';
    if (isActive) return 'bg-green-500/20 text-green-400';
    return 'bg-gray-500/20 text-gray-400';
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-500/20 text-red-400';
      case 'warning': return 'bg-yellow-500/20 text-yellow-400';
      case 'info': return 'bg-blue-500/20 text-blue-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  const getEventTypeIcon = (eventType: string) => {
    switch (eventType) {
      case 'login_success': return <UserCheck className="w-4 h-4" />;
      case 'login_failed': return <UserX className="w-4 h-4" />;
      case 'account_locked': return <Lock className="w-4 h-4" />;
      case 'password_changed': return <Key className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return '없음';
    return new Date(dateString).toLocaleString('ko-KR');
  };

  const getEventTypeText = (eventType: string) => {
    switch (eventType) {
      case 'login_success': return '로그인 성공';
      case 'login_failed': return '로그인 실패';
      case 'account_locked': return '계정 잠금';
      case 'password_changed': return '비밀번호 변경';
      case 'user_created': return '사용자 생성';
      case 'user_deleted': return '사용자 삭제';
      default: return eventType;
    }
  };

  // 초기 데이터 로드
  useEffect(() => {
    const loadAllData = async () => {
      await loadUsers();
      await loadRoles();
      await loadSecurityEvents();
    };
    loadAllData();
  }, [loadUsers, loadRoles, loadSecurityEvents]);

  return (
    <div className="min-h-screen p-6">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <Shield className="w-8 h-8 text-blue-400" />
          인증 및 권한 관리
        </h1>
        <p className="text-gray-300 mt-2">사용자 계정, 역할, 보안 이벤트를 관리합니다</p>
      </div>

      {/* 액션 버튼 */}
      <div className="flex gap-3 mb-6">
        <Button 
          onClick={() => setShowCreateUserDialog(true)}
          className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700"
        >
          <UserPlus className="w-4 h-4 mr-2" />
          사용자 생성
        </Button>
        <Button 
          onClick={() => setShowChangePasswordDialog(true)}
          variant="outline"
          className="border-white/20 text-white hover:bg-white/10"
        >
          <Key className="w-4 h-4 mr-2" />
          비밀번호 변경
        </Button>
      </div>

      {/* 메인 탭 */}
      <Tabs defaultValue="users" className="space-y-4">
        <TabsList className="bg-white/10 border border-white/20">
          <TabsTrigger value="users" className="text-white data-[state=active]:bg-white/20">사용자</TabsTrigger>
          <TabsTrigger value="roles" className="text-white data-[state=active]:bg-white/20">역할</TabsTrigger>
          <TabsTrigger value="events" className="text-white data-[state=active]:bg-white/20">보안 이벤트</TabsTrigger>
        </TabsList>

        {/* 사용자 탭 */}
        <TabsContent value="users" className="space-y-4">
          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader>
              <CardTitle className="text-white">사용자 목록</CardTitle>
              <CardDescription className="text-gray-300">시스템 사용자 계정을 관리합니다</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {users.map((user) => (
                  <div key={user.user_id} className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:bg-white/10">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h3 className="font-medium text-white">{user.full_name}</h3>
                          <Badge className={getRoleColor(user.role)}>
                            {user.role}
                          </Badge>
                          <Badge className={getStatusColor(user.is_active, user.is_locked)}>
                            {user.is_locked ? '잠금' : user.is_active ? '활성' : '비활성'}
                          </Badge>
                        </div>
                        <div className="text-sm text-gray-300 space-y-1">
                          <div>사용자명: {user.username}</div>
                          <div>이메일: {user.email}</div>
                          <div>마지막 로그인: {formatDate(user.last_login)}</div>
                          {user.failed_login_attempts > 0 && (
                            <div className="text-red-400">실패한 로그인: {user.failed_login_attempts}회</div>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Switch
                          checked={user.is_active}
                          onCheckedChange={(isActive) => handleToggleUserStatus(user.user_id, isActive)}
                        />
                        {user.is_locked && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleUnlockUser(user.user_id)}
                            className="border-white/20 text-white hover:bg-white/10"
                          >
                            <Unlock className="w-4 h-4" />
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                
                {users.length === 0 && (
                  <div className="text-center py-8 text-gray-300">
                    사용자가 없습니다.
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 역할 탭 */}
        <TabsContent value="roles" className="space-y-4">
          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader>
              <CardTitle className="text-white">역할 목록</CardTitle>
              <CardDescription className="text-gray-300">시스템 역할과 권한을 관리합니다</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {roles.map((role) => (
                  <div key={role.role_id} className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:bg-white/10">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h3 className="font-medium text-white">{role.name}</h3>
                          <Badge className={role.is_active ? "bg-green-500/20 text-green-400" : "bg-gray-500/20 text-gray-400"}>
                            {role.is_active ? '활성' : '비활성'}
                          </Badge>
                        </div>
                        <div className="text-sm text-gray-300 space-y-1">
                          <div>설명: {role.description}</div>
                          <div>권한: {role.permissions.join(', ')}</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Switch
                          checked={role.is_active}
                          onCheckedChange={(isActive) => {
                            setRoles(prev => prev.map(r => 
                              r.role_id === role.role_id ? { ...r, is_active: isActive } : r
                            ));
                            toast.success(`역할이 ${isActive ? '활성화' : '비활성화'}되었습니다`);
                          }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
                
                {roles.length === 0 && (
                  <div className="text-center py-8 text-gray-300">
                    역할이 없습니다.
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 보안 이벤트 탭 */}
        <TabsContent value="events" className="space-y-4">
          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader>
              <CardTitle className="text-white">보안 이벤트</CardTitle>
              <CardDescription className="text-gray-300">시스템 보안 관련 이벤트를 확인합니다</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {securityEvents.map((event) => (
                  <div key={event.event_id} className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:bg-white/10">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h3 className="font-medium text-white">{getEventTypeText(event.event_type)}</h3>
                          <Badge className={getSeverityColor(event.severity)}>
                            {getEventTypeIcon(event.event_type)}
                            <span className="ml-1">{event.severity}</span>
                          </Badge>
                        </div>
                        <div className="text-sm text-gray-300 space-y-1">
                          <div>IP 주소: {event.ip_address}</div>
                          <div>발생 시간: {formatDate(event.timestamp)}</div>
                          {event.details && (
                            <div>상세: {JSON.stringify(event.details)}</div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                
                {securityEvents.length === 0 && (
                  <div className="text-center py-8 text-gray-300">
                    보안 이벤트가 없습니다.
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* 사용자 생성 다이얼로그 */}
      <Dialog open={showCreateUserDialog} onOpenChange={setShowCreateUserDialog}>
        <DialogContent className="max-w-md bg-white/10 backdrop-blur-sm border border-white/20">
          <DialogHeader>
            <DialogTitle className="text-white">사용자 생성</DialogTitle>
            <DialogDescription className="text-gray-300">새로운 사용자 계정을 생성합니다</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-300">사용자명</label>
              <Input
                value={userForm.username}
                onChange={(e) => setUserForm(prev => ({ ...prev, username: e.target.value }))}
                placeholder="사용자명을 입력하세요"
                className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
              />
            </div>
            
            <div>
              <label className="text-sm font-medium text-gray-300">이메일</label>
              <Input
                type="email"
                value={userForm.email}
                onChange={(e) => setUserForm(prev => ({ ...prev, email: e.target.value }))}
                placeholder="이메일을 입력하세요"
                className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
              />
            </div>
            
            <div>
              <label className="text-sm font-medium text-gray-300">전체 이름</label>
              <Input
                value={userForm.full_name}
                onChange={(e) => setUserForm(prev => ({ ...prev, full_name: e.target.value }))}
                placeholder="전체 이름을 입력하세요"
                className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
              />
            </div>
            
            <div>
              <label className="text-sm font-medium text-gray-300">비밀번호</label>
              <div className="relative">
                <Input
                  type={showPassword ? "text" : "password"}
                  value={userForm.password}
                  onChange={(e) => setUserForm(prev => ({ ...prev, password: e.target.value }))}
                  placeholder="비밀번호를 입력하세요"
                  className="bg-white/10 border-white/20 text-white placeholder:text-gray-400 pr-10"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 text-gray-400 hover:text-white"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </Button>
              </div>
            </div>
            
            <div>
              <label className="text-sm font-medium text-gray-300">역할</label>
              <select
                value={userForm.role}
                onChange={(e) => setUserForm(prev => ({ ...prev, role: e.target.value }))}
                className="w-full bg-white/10 border border-white/20 text-white rounded-md px-3 py-2"
              >
                <option value="">역할을 선택하세요</option>
                {roles.map((role) => (
                  <option key={role.role_id} value={role.name}>
                    {role.name} - {role.description}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="flex gap-2">
              <Button 
                onClick={handleCreateUser}
                disabled={isLoading}
                className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700"
              >
                {isLoading ? "생성 중..." : "사용자 생성"}
              </Button>
              <Button 
                variant="outline" 
                onClick={() => setShowCreateUserDialog(false)}
                className="border-white/20 text-white hover:bg-white/10"
              >
                취소
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* 비밀번호 변경 다이얼로그 */}
      <Dialog open={showChangePasswordDialog} onOpenChange={setShowChangePasswordDialog}>
        <DialogContent className="max-w-md bg-white/10 backdrop-blur-sm border border-white/20">
          <DialogHeader>
            <DialogTitle className="text-white">비밀번호 변경</DialogTitle>
            <DialogDescription className="text-gray-300">현재 비밀번호를 변경합니다</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-300">현재 비밀번호</label>
              <div className="relative">
                <Input
                  type={showPassword ? "text" : "password"}
                  value={passwordForm.current_password}
                  onChange={(e) => setPasswordForm(prev => ({ ...prev, current_password: e.target.value }))}
                  placeholder="현재 비밀번호를 입력하세요"
                  className="bg-white/10 border-white/20 text-white placeholder:text-gray-400 pr-10"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 text-gray-400 hover:text-white"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </Button>
              </div>
            </div>
            
            <div>
              <label className="text-sm font-medium text-gray-300">새 비밀번호</label>
              <div className="relative">
                <Input
                  type={showNewPassword ? "text" : "password"}
                  value={passwordForm.new_password}
                  onChange={(e) => setPasswordForm(prev => ({ ...prev, new_password: e.target.value }))}
                  placeholder="새 비밀번호를 입력하세요"
                  className="bg-white/10 border-white/20 text-white placeholder:text-gray-400 pr-10"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 text-gray-400 hover:text-white"
                  onClick={() => setShowNewPassword(!showNewPassword)}
                >
                  {showNewPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </Button>
              </div>
            </div>
            
            <div>
              <label className="text-sm font-medium text-gray-300">새 비밀번호 확인</label>
              <div className="relative">
                <Input
                  type={showConfirmPassword ? "text" : "password"}
                  value={passwordForm.confirm_password}
                  onChange={(e) => setPasswordForm(prev => ({ ...prev, confirm_password: e.target.value }))}
                  placeholder="새 비밀번호를 다시 입력하세요"
                  className="bg-white/10 border-white/20 text-white placeholder:text-gray-400 pr-10"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 text-gray-400 hover:text-white"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                >
                  {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </Button>
              </div>
            </div>
            
            <div className="flex gap-2">
              <Button 
                onClick={handleChangePassword}
                disabled={isLoading}
                className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700"
              >
                {isLoading ? "변경 중..." : "비밀번호 변경"}
              </Button>
              <Button 
                variant="outline" 
                onClick={() => setShowChangePasswordDialog(false)}
                className="border-white/20 text-white hover:bg-white/10"
              >
                취소
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
} 
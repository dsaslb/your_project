'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Badge } from '../../components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../../components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { Switch } from '../../components/ui/switch';
import { Progress } from '../../components/ui/progress';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { Shield, Lock, Eye, EyeOff, AlertTriangle, CheckCircle, XCircle, Clock, Users, Activity, Settings } from 'lucide-react';
// import { useLoadingState } from '../../hooks/useLoadingState';
import { useErrorHandler } from '../../hooks/useErrorHandler';
import { ApiClient } from '../../lib/api-client';

// 타입 정의
interface SecurityStats {
  active_sessions: number;
  total_events_24h: number;
  failed_logins_24h: number;
  locked_accounts: number;
  security_score: number;
}

interface SecurityEvent {
  event_id: string;
  user_id: string | null;
  event_type: string;
  description: string;
  ip_address: string;
  user_agent: string;
  timestamp: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'pending' | 'reviewed' | 'resolved';
}

interface UserSession {
  session_id: string;
  user_id: string;
  created_at: string;
  last_activity: string;
  ip_address: string;
  user_agent: string;
  is_active: boolean;
}

interface LoginFormData {
  username: string;
  password: string;
}

interface PasswordChangeFormData {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

const SecurityPage: React.FC = () => {
  // 상태 관리
  const [stats, setStats] = useState<SecurityStats | null>(null);
  const [events, setEvents] = useState<SecurityEvent[]>([]);
  const [sessions, setSessions] = useState<UserSession[]>([]);
  const [showLoginDialog, setShowLoginDialog] = useState(false);
  const [showPasswordDialog, setShowPasswordDialog] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState<SecurityEvent | null>(null);
  const [eventFilter, setEventFilter] = useState({
    severity: '',
    status: '',
    event_type: ''
  });

  // 폼 데이터
  const [loginForm, setLoginForm] = useState<LoginFormData>({
    username: '',
    password: ''
  });

  const [passwordForm, setPasswordForm] = useState<PasswordChangeFormData>({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });

  // 훅 사용
  const [isLoading, setIsLoading] = useState(false);
  const { handleError } = useErrorHandler();
    // 데이터 로드 함수들
  const loadSecurityStats = useCallback(async () => {
    try {
      const response = await apiClient.get('/api/security/stats');
      setStats(response.data);
    } catch (error) {
      handleError(error, '보안 통계를 불러오는데 실패했습니다');
    }
  }, [apiClient, handleError]);

  const loadSecurityEvents = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      if (eventFilter.severity) params.append('severity', eventFilter.severity);
      if (eventFilter.status) params.append('status', eventFilter.status);
      if (eventFilter.event_type) params.append('event_type', eventFilter.event_type);
      
      const response = await apiClient.get(`/api/security/events?${params.toString()}`);
      setEvents(response.data.events);
    } catch (error) {
      handleError(error, '보안 이벤트를 불러오는데 실패했습니다');
    }
  }, [apiClient, handleError, eventFilter]);

  const loadSessions = useCallback(async () => {
    try {
      const response = await apiClient.get('/api/security/sessions');
      setSessions(response.data.sessions);
    } catch (error) {
      handleError(error, '세션 정보를 불러오는데 실패했습니다');
    }
  }, [apiClient, handleError]);

  // 로그인 처리
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!loginForm.username || !loginForm.password) {
      showError('사용자명과 비밀번호를 입력해주세요');
      return;
    }

    await withLoading(async () => {
      try {
        const response = await apiClient.post('/api/security/login', loginForm);
        
        // 토큰 저장
        localStorage.setItem('auth_token', response.data.token);
        localStorage.setItem('session_id', response.data.session_id);
        
        setShowLoginDialog(false);
        setLoginForm({ username: '', password: '' });
        
        // 페이지 새로고침하여 인증 상태 업데이트
        window.location.reload();
      } catch (error: any) {
        if (error.response?.status === 423) {
          showError('계정이 잠겼습니다. 잠시 후 다시 시도해주세요');
        } else {
          showError('로그인에 실패했습니다. 사용자명과 비밀번호를 확인해주세요');
        }
      }
    });
  };

  // 비밀번호 변경
  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      showError('새 비밀번호가 일치하지 않습니다');
      return;
    }

    await withLoading(async () => {
      try {
        const response = await apiClient.post('/api/security/change-password', {
          current_password: passwordForm.current_password,
          new_password: passwordForm.new_password
        });
        
        setShowPasswordDialog(false);
        setPasswordForm({
          current_password: '',
          new_password: '',
          confirm_password: ''
        });
        
        showError('비밀번호가 성공적으로 변경되었습니다', 'success');
      } catch (error: any) {
        if (error.response?.data?.errors) {
          const errors = error.response.data.errors.join(', ');
          showError(`비밀번호 변경 실패: ${errors}`);
        } else {
          showError('비밀번호 변경에 실패했습니다');
        }
      }
    });
  };

  // 세션 무효화
  const handleInvalidateSession = async (sessionId: string) => {
    await withLoading(async () => {
      try {
        await apiClient.delete(`/api/security/sessions/${sessionId}`);
        await loadSessions();
        showError('세션이 무효화되었습니다', 'success');
      } catch (error) {
        handleError(error, '세션 무효화에 실패했습니다');
      }
    });
  };

  // 이벤트 상태 업데이트
  const handleUpdateEventStatus = async (eventId: string, status: string) => {
    await withLoading(async () => {
      try {
        await apiClient.put(`/api/security/events/${eventId}/status`, { status });
        await loadSecurityEvents();
        showError('이벤트 상태가 업데이트되었습니다', 'success');
      } catch (error) {
        handleError(error, '이벤트 상태 업데이트에 실패했습니다');
      }
    });
  };

  // 세션 정리
  const handleCleanupSessions = async () => {
    await withLoading(async () => {
      try {
        await apiClient.post('/api/security/cleanup');
        await loadSessions();
        await loadSecurityStats();
        showError('만료된 세션이 정리되었습니다', 'success');
      } catch (error) {
        handleError(error, '세션 정리에 실패했습니다');
      }
    });
  };

  // 초기 데이터 로드
  useEffect(() => {
    loadSecurityStats();
    loadSecurityEvents();
    loadSessions();
  }, [loadSecurityStats, loadSecurityEvents, loadSessions]);

  // 이벤트 필터 변경 시 재로드
  useEffect(() => {
    loadSecurityEvents();
  }, [eventFilter, loadSecurityEvents]);

  // 유틸리티 함수들
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'destructive';
      case 'high': return 'destructive';
      case 'medium': return 'secondary';
      case 'low': return 'default';
      default: return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'resolved': return 'default';
      case 'reviewed': return 'secondary';
      case 'pending': return 'destructive';
      default: return 'default';
    }
  };

  const getEventTypeIcon = (eventType: string) => {
    switch (eventType) {
      case 'login_success':
      case 'login_failed':
        return <Lock className="w-4 h-4" />;
      case 'password_changed':
        return <Shield className="w-4 h-4" />;
      default:
        return <Activity className="w-4 h-4" />;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('ko-KR');
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">보안 관리</h1>
          <p className="text-muted-foreground">시스템 보안 상태를 모니터링하고 관리합니다</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => setShowLoginDialog(true)} variant="outline">
            로그인
          </Button>
          <Button onClick={() => setShowPasswordDialog(true)} variant="outline">
            비밀번호 변경
          </Button>
        </div>
      </div>

      {/* 보안 통계 */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">활성 세션</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.active_sessions}</div>
              <p className="text-xs text-muted-foreground">현재 로그인된 사용자</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">24시간 이벤트</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_events_24h}</div>
              <p className="text-xs text-muted-foreground">보안 이벤트 수</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">실패한 로그인</CardTitle>
              <XCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.failed_logins_24h}</div>
              <p className="text-xs text-muted-foreground">24시간 내 실패</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">보안 점수</CardTitle>
              <Shield className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.security_score}/100</div>
              <Progress value={stats.security_score} className="mt-2" />
            </CardContent>
          </Card>
        </div>
      )}

      {/* 메인 탭 */}
      <Tabs defaultValue="events" className="space-y-4">
        <TabsList>
          <TabsTrigger value="events">보안 이벤트</TabsTrigger>
          <TabsTrigger value="sessions">세션 관리</TabsTrigger>
        </TabsList>

        {/* 보안 이벤트 탭 */}
        <TabsContent value="events" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>보안 이벤트</CardTitle>
              <CardDescription>시스템에서 발생한 보안 관련 이벤트를 모니터링합니다</CardDescription>
            </CardHeader>
            <CardContent>
              {/* 필터 */}
              <div className="flex gap-4 mb-4">
                <Select value={eventFilter.severity} onValueChange={(value) => setEventFilter(prev => ({ ...prev, severity: value }))}>
                  <SelectTrigger className="w-32">
                    <SelectValue placeholder="심각도" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">전체</SelectItem>
                    <SelectItem value="low">낮음</SelectItem>
                    <SelectItem value="medium">보통</SelectItem>
                    <SelectItem value="high">높음</SelectItem>
                    <SelectItem value="critical">치명적</SelectItem>
                  </SelectContent>
                </Select>

                <Select value={eventFilter.status} onValueChange={(value) => setEventFilter(prev => ({ ...prev, status: value }))}>
                  <SelectTrigger className="w-32">
                    <SelectValue placeholder="상태" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">전체</SelectItem>
                    <SelectItem value="pending">대기</SelectItem>
                    <SelectItem value="reviewed">검토</SelectItem>
                    <SelectItem value="resolved">해결</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* 이벤트 목록 */}
              <div className="space-y-2">
                {events.map((event) => (
                  <div key={event.event_id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      {getEventTypeIcon(event.event_type)}
                      <div>
                        <div className="font-medium">{event.description}</div>
                        <div className="text-sm text-muted-foreground">
                          {event.user_id || '알 수 없음'} • {event.ip_address} • {formatDate(event.timestamp)}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant={getSeverityColor(event.severity)}>
                        {event.severity}
                      </Badge>
                      <Badge variant={getStatusColor(event.status)}>
                        {event.status}
                      </Badge>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setSelectedEvent(event)}
                      >
                        상세보기
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 세션 관리 탭 */}
        <TabsContent value="sessions" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>세션 관리</CardTitle>
                  <CardDescription>활성 사용자 세션을 관리합니다</CardDescription>
                </div>
                <Button onClick={handleCleanupSessions} variant="outline">
                  만료 세션 정리
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {sessions.map((session) => (
                  <div key={session.session_id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <div className="font-medium">{session.user_id}</div>
                      <div className="text-sm text-muted-foreground">
                        {session.ip_address} • {formatDate(session.last_activity)}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        생성: {formatDate(session.created_at)}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant={session.is_active ? "default" : "secondary"}>
                        {session.is_active ? "활성" : "비활성"}
                      </Badge>
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => handleInvalidateSession(session.session_id)}
                      >
                        무효화
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* 로그인 다이얼로그 */}
      <Dialog open={showLoginDialog} onOpenChange={setShowLoginDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>로그인</DialogTitle>
            <DialogDescription>시스템에 로그인합니다</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <Label htmlFor="username">사용자명</Label>
              <Input
                id="username"
                value={loginForm.username}
                onChange={(e) => setLoginForm(prev => ({ ...prev, username: e.target.value }))}
                placeholder="사용자명을 입력하세요"
              />
            </div>
            <div>
              <Label htmlFor="password">비밀번호</Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  value={loginForm.password}
                  onChange={(e) => setLoginForm(prev => ({ ...prev, password: e.target.value }))}
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
            <div className="flex gap-2">
              <Button type="submit" disabled={isLoading}>
                {isLoading ? "로그인 중..." : "로그인"}
              </Button>
              <Button type="button" variant="outline" onClick={() => setShowLoginDialog(false)}>
                취소
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* 비밀번호 변경 다이얼로그 */}
      <Dialog open={showPasswordDialog} onOpenChange={setShowPasswordDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>비밀번호 변경</DialogTitle>
            <DialogDescription>새로운 비밀번호로 변경합니다</DialogDescription>
          </DialogHeader>
          <form onSubmit={handlePasswordChange} className="space-y-4">
            <div>
              <Label htmlFor="current-password">현재 비밀번호</Label>
              <div className="relative">
                <Input
                  id="current-password"
                  type={showPassword ? "text" : "password"}
                  value={passwordForm.current_password}
                  onChange={(e) => setPasswordForm(prev => ({ ...prev, current_password: e.target.value }))}
                  placeholder="현재 비밀번호를 입력하세요"
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
              <Label htmlFor="new-password">새 비밀번호</Label>
              <div className="relative">
                <Input
                  id="new-password"
                  type={showNewPassword ? "text" : "password"}
                  value={passwordForm.new_password}
                  onChange={(e) => setPasswordForm(prev => ({ ...prev, new_password: e.target.value }))}
                  placeholder="새 비밀번호를 입력하세요"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                  onClick={() => setShowNewPassword(!showNewPassword)}
                >
                  {showNewPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </Button>
              </div>
            </div>
            <div>
              <Label htmlFor="confirm-password">비밀번호 확인</Label>
              <div className="relative">
                <Input
                  id="confirm-password"
                  type={showConfirmPassword ? "text" : "password"}
                  value={passwordForm.confirm_password}
                  onChange={(e) => setPasswordForm(prev => ({ ...prev, confirm_password: e.target.value }))}
                  placeholder="새 비밀번호를 다시 입력하세요"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                >
                  {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </Button>
              </div>
            </div>
            <div className="flex gap-2">
              <Button type="submit" disabled={isLoading}>
                {isLoading ? "변경 중..." : "비밀번호 변경"}
              </Button>
              <Button type="button" variant="outline" onClick={() => setShowPasswordDialog(false)}>
                취소
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* 이벤트 상세보기 다이얼로그 */}
      <Dialog open={!!selectedEvent} onOpenChange={() => setSelectedEvent(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>이벤트 상세정보</DialogTitle>
          </DialogHeader>
          {selectedEvent && (
            <div className="space-y-4">
              <div>
                <Label>이벤트 ID</Label>
                <p className="text-sm">{selectedEvent.event_id}</p>
              </div>
              <div>
                <Label>사용자</Label>
                <p className="text-sm">{selectedEvent.user_id || '알 수 없음'}</p>
              </div>
              <div>
                <Label>이벤트 유형</Label>
                <p className="text-sm">{selectedEvent.event_type}</p>
              </div>
              <div>
                <Label>설명</Label>
                <p className="text-sm">{selectedEvent.description}</p>
              </div>
              <div>
                <Label>IP 주소</Label>
                <p className="text-sm">{selectedEvent.ip_address}</p>
              </div>
              <div>
                <Label>사용자 에이전트</Label>
                <p className="text-sm">{selectedEvent.user_agent}</p>
              </div>
              <div>
                <Label>발생 시간</Label>
                <p className="text-sm">{formatDate(selectedEvent.timestamp)}</p>
              </div>
              <div className="flex gap-2">
                <Badge variant={getSeverityColor(selectedEvent.severity)}>
                  {selectedEvent.severity}
                </Badge>
                <Badge variant={getStatusColor(selectedEvent.status)}>
                  {selectedEvent.status}
                </Badge>
              </div>
              <div className="flex gap-2">
                <Select
                  value={selectedEvent.status}
                  onValueChange={(value) => handleUpdateEventStatus(selectedEvent.event_id, value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="상태 변경" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="pending">대기</SelectItem>
                    <SelectItem value="reviewed">검토</SelectItem>
                    <SelectItem value="resolved">해결</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default SecurityPage; 
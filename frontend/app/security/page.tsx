'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../src/components/ui/card';
import { Button } from '../../src/components/ui/button';
import { Input } from '../../src/components/ui/input';
import { Label } from '../../src/components/ui/label';
import { Badge } from '../../src/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../../src/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../src/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../src/components/ui/select';
import { Switch } from '../../src/components/ui/switch';
import { Progress } from '../../src/components/ui/progress';
import { Alert, AlertDescription } from '../../src/components/ui/alert';
import { Shield, Lock, Eye, EyeOff, AlertTriangle, CheckCircle, XCircle, Clock, Users, Activity, Settings, RefreshCw } from 'lucide-react';
import { useLoadingState } from '../../src/hooks/useLoadingState';
import { useErrorHandler } from '../../src/hooks/useErrorHandler';
import { apiClient } from '../../src/lib/api-client';
import { toast } from 'sonner';

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
    severity: 'all',
    status: 'all',
    event_type: 'all'
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
  const { isLoading, setLoading } = useLoadingState();
  const { handleError } = useErrorHandler();

  // 데이터 로드 함수들
  const loadSecurityStats = useCallback(async () => {
    try {
      setLoading(true);
      // 임시로 샘플 데이터 사용
      const sampleStats: SecurityStats = {
        active_sessions: 12,
        total_events_24h: 156,
        failed_logins_24h: 8,
        locked_accounts: 2,
        security_score: 85
      };
      setStats(sampleStats);
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  }, [setLoading, handleError]);

  const loadSecurityEvents = useCallback(async () => {
    try {
      setLoading(true);
      // 임시로 샘플 데이터 사용
      const sampleEvents: SecurityEvent[] = [
        {
          event_id: '1',
          user_id: 'user123',
          event_type: 'login_failed',
          description: '로그인 실패 - 잘못된 비밀번호',
          ip_address: '192.168.1.100',
          user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
          timestamp: '2024-01-15T10:30:00Z',
          severity: 'medium',
          status: 'pending'
        },
        {
          event_id: '2',
          user_id: null,
          event_type: 'suspicious_activity',
          description: '의심스러운 IP에서 접근 시도',
          ip_address: '203.0.113.45',
          user_agent: 'Unknown',
          timestamp: '2024-01-15T09:15:00Z',
          severity: 'high',
          status: 'reviewed'
        },
        {
          event_id: '3',
          user_id: 'user456',
          event_type: 'password_changed',
          description: '비밀번호 변경 완료',
          ip_address: '192.168.1.101',
          user_agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
          timestamp: '2024-01-15T08:45:00Z',
          severity: 'low',
          status: 'resolved'
        },
        {
          event_id: '4',
          user_id: 'user789',
          event_type: 'account_locked',
          description: '계정 잠금 - 5회 연속 로그인 실패',
          ip_address: '192.168.1.102',
          user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
          timestamp: '2024-01-15T07:20:00Z',
          severity: 'critical',
          status: 'pending'
        }
      ];
      setEvents(sampleEvents);
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  }, [setLoading, handleError]);

  const loadUserSessions = useCallback(async () => {
    try {
      setLoading(true);
      // 임시로 샘플 데이터 사용
      const sampleSessions: UserSession[] = [
        {
          session_id: 'session1',
          user_id: 'user123',
          created_at: '2024-01-15T08:00:00Z',
          last_activity: '2024-01-15T10:30:00Z',
          ip_address: '192.168.1.100',
          user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
          is_active: true
        },
        {
          session_id: 'session2',
          user_id: 'user456',
          created_at: '2024-01-15T09:15:00Z',
          last_activity: '2024-01-15T10:25:00Z',
          ip_address: '192.168.1.101',
          user_agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
          is_active: true
        },
        {
          session_id: 'session3',
          user_id: 'user789',
          created_at: '2024-01-15T07:30:00Z',
          last_activity: '2024-01-15T09:45:00Z',
          ip_address: '192.168.1.102',
          user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
          is_active: false
        }
      ];
      setSessions(sampleSessions);
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  }, [setLoading, handleError]);

  // 초기 데이터 로드
  useEffect(() => {
    loadSecurityStats();
    loadSecurityEvents();
    loadUserSessions();
  }, [loadSecurityStats, loadSecurityEvents, loadUserSessions]);

  // 이벤트 핸들러들
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      // 임시 로그인 처리
      toast.success('로그인이 성공했습니다.');
      setShowLoginDialog(false);
      setLoginForm({ username: '', password: '' });
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      toast.error('새 비밀번호가 일치하지 않습니다.');
      return;
    }
    try {
      setLoading(true);
      // 임시 비밀번호 변경 처리
      toast.success('비밀번호가 성공적으로 변경되었습니다.');
      setShowPasswordDialog(false);
      setPasswordForm({
        current_password: '',
        new_password: '',
        confirm_password: ''
      });
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  const handleInvalidateSession = async (sessionId: string) => {
    try {
      setLoading(true);
      setSessions(prev => prev.filter(session => session.session_id !== sessionId));
      toast.success('세션이 무효화되었습니다.');
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateEventStatus = async (eventId: string, status: string) => {
    try {
      setLoading(true);
      setEvents(prev => prev.map(event => 
        event.event_id === eventId 
          ? { ...event, status: status as 'pending' | 'reviewed' | 'resolved' }
          : event
      ));
      toast.success('이벤트 상태가 업데이트되었습니다.');
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  const handleCleanupSessions = async () => {
    try {
      setLoading(true);
      setSessions(prev => prev.filter(session => session.is_active));
      toast.success('비활성 세션이 정리되었습니다.');
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 유틸리티 함수들
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'low': return 'bg-green-500/20 text-green-400';
      case 'medium': return 'bg-yellow-500/20 text-yellow-400';
      case 'high': return 'bg-orange-500/20 text-orange-400';
      case 'critical': return 'bg-red-500/20 text-red-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-500/20 text-yellow-400';
      case 'reviewed': return 'bg-blue-500/20 text-blue-400';
      case 'resolved': return 'bg-green-500/20 text-green-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  const getEventTypeIcon = (eventType: string) => {
    switch (eventType) {
      case 'login_failed':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'suspicious_activity':
        return <AlertTriangle className="h-5 w-5 text-orange-500" />;
      case 'password_changed':
        return <Lock className="h-5 w-5 text-blue-500" />;
      case 'account_locked':
        return <Shield className="h-5 w-5 text-red-600" />;
      default:
        return <Activity className="h-5 w-5 text-gray-500" />;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('ko-KR');
  };

  // 필터링된 이벤트
  const filteredEvents = events.filter(event => {
    const matchesSeverity = eventFilter.severity === 'all' || event.severity === eventFilter.severity;
    const matchesStatus = eventFilter.status === 'all' || event.status === eventFilter.status;
    return matchesSeverity && matchesStatus;
  });

  return (
    <div className="min-h-screen p-6">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <Shield className="w-6 h-6" />
          보안 관리
        </h1>
        <p className="text-gray-300 mt-2">시스템 보안 상태를 모니터링하고 관리합니다</p>
      </div>

      {/* 액션 버튼 */}
      <div className="flex gap-4 mb-8">
        <Button
          onClick={() => setShowLoginDialog(true)}
          className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700"
        >
          <Lock className="w-4 h-4 mr-2" />
          로그인
        </Button>
        <Button
          onClick={() => setShowPasswordDialog(true)}
          className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700"
        >
          <Settings className="w-4 h-4 mr-2" />
          비밀번호 변경
        </Button>
        <Button
          onClick={() => {
            loadSecurityStats();
            loadSecurityEvents();
            loadUserSessions();
          }}
          disabled={isLoading}
          className="bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          새로고침
        </Button>
      </div>

      {/* 보안 통계 */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-300">활성 세션</CardTitle>
              <div className="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center">
                <Users className="h-4 w-4 text-blue-400" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.active_sessions}</div>
              <p className="text-xs text-gray-400">현재 로그인된 사용자</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-300">24시간 이벤트</CardTitle>
              <div className="w-8 h-8 bg-orange-500/20 rounded-lg flex items-center justify-center">
                <Activity className="h-4 w-4 text-orange-400" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.total_events_24h}</div>
              <p className="text-xs text-gray-400">보안 이벤트 수</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-300">실패한 로그인</CardTitle>
              <div className="w-8 h-8 bg-red-500/20 rounded-lg flex items-center justify-center">
                <XCircle className="h-4 w-4 text-red-400" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.failed_logins_24h}</div>
              <p className="text-xs text-gray-400">24시간 내 실패</p>
            </CardContent>
          </Card>

          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-300">보안 점수</CardTitle>
              <div className="w-8 h-8 bg-green-500/20 rounded-lg flex items-center justify-center">
                <Shield className="h-4 w-4 text-green-400" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats.security_score}/100</div>
              <Progress value={stats.security_score} className="mt-2" />
            </CardContent>
          </Card>
        </div>
      )}

      {/* 메인 탭 */}
      <Tabs defaultValue="events" className="space-y-4">
        <TabsList className="bg-white/10 border border-white/20">
          <TabsTrigger value="events" className="text-white data-[state=active]:bg-white/20">보안 이벤트</TabsTrigger>
          <TabsTrigger value="sessions" className="text-white data-[state=active]:bg-white/20">세션 관리</TabsTrigger>
        </TabsList>

        {/* 보안 이벤트 탭 */}
        <TabsContent value="events" className="space-y-4">
          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader>
              <CardTitle className="text-white">보안 이벤트</CardTitle>
              <CardDescription className="text-gray-300">시스템에서 발생한 보안 관련 이벤트를 모니터링합니다</CardDescription>
            </CardHeader>
            <CardContent>
              {/* 필터 */}
              <div className="flex gap-4 mb-4">
                <Select value={eventFilter.severity} onValueChange={(value) => setEventFilter(prev => ({ ...prev, severity: value }))}>
                  <SelectTrigger className="w-32 bg-white/10 border-white/20 text-white">
                    <SelectValue placeholder="심각도" />
                  </SelectTrigger>
                  <SelectContent className="bg-white/10 border-white/20">
                    <SelectItem value="all">전체</SelectItem>
                    <SelectItem value="low">낮음</SelectItem>
                    <SelectItem value="medium">보통</SelectItem>
                    <SelectItem value="high">높음</SelectItem>
                    <SelectItem value="critical">치명적</SelectItem>
                  </SelectContent>
                </Select>

                <Select value={eventFilter.status} onValueChange={(value) => setEventFilter(prev => ({ ...prev, status: value }))}>
                  <SelectTrigger className="w-32 bg-white/10 border-white/20 text-white">
                    <SelectValue placeholder="상태" />
                  </SelectTrigger>
                  <SelectContent className="bg-white/10 border-white/20">
                    <SelectItem value="all">전체</SelectItem>
                    <SelectItem value="pending">대기</SelectItem>
                    <SelectItem value="reviewed">검토</SelectItem>
                    <SelectItem value="resolved">해결</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* 이벤트 목록 */}
              <div className="space-y-2">
                {filteredEvents.map((event) => (
                  <div key={event.event_id} className="flex items-center justify-between p-4 bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg hover:bg-white/10 transition-all duration-300">
                    <div className="flex items-center gap-3">
                      {getEventTypeIcon(event.event_type)}
                      <div>
                        <div className="font-medium text-white">{event.description}</div>
                        <div className="text-sm text-gray-400">
                          {event.user_id || '알 수 없음'} • {event.ip_address} • {formatDate(event.timestamp)}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={getSeverityColor(event.severity)}>
                        {event.severity === 'low' && '낮음'}
                        {event.severity === 'medium' && '보통'}
                        {event.severity === 'high' && '높음'}
                        {event.severity === 'critical' && '치명적'}
                      </Badge>
                      <Badge className={getStatusColor(event.status)}>
                        {event.status === 'pending' && '대기'}
                        {event.status === 'reviewed' && '검토'}
                        {event.status === 'resolved' && '해결'}
                      </Badge>
                      <Select value={event.status} onValueChange={(value) => handleUpdateEventStatus(event.event_id, value)}>
                        <SelectTrigger className="w-24 bg-white/10 border-white/20 text-white">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-white/10 border-white/20">
                          <SelectItem value="pending">대기</SelectItem>
                          <SelectItem value="reviewed">검토</SelectItem>
                          <SelectItem value="resolved">해결</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 세션 관리 탭 */}
        <TabsContent value="sessions" className="space-y-4">
          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader>
              <CardTitle className="text-white">세션 관리</CardTitle>
              <CardDescription className="text-gray-300">활성 사용자 세션을 모니터링하고 관리합니다</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex justify-between items-center mb-4">
                <div className="text-sm text-gray-300">
                  총 {sessions.length}개 세션 (활성: {sessions.filter(s => s.is_active).length}개)
                </div>
                <Button
                  onClick={handleCleanupSessions}
                  className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700"
                >
                  비활성 세션 정리
                </Button>
              </div>

              <div className="space-y-2">
                {sessions.map((session) => (
                  <div key={session.session_id} className="flex items-center justify-between p-4 bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg hover:bg-white/10 transition-all duration-300">
                    <div className="flex items-center gap-3">
                      <div className={`w-3 h-3 rounded-full ${session.is_active ? 'bg-green-500' : 'bg-gray-500'}`} />
                      <div>
                        <div className="font-medium text-white">사용자: {session.user_id}</div>
                        <div className="text-sm text-gray-400">
                          {session.ip_address} • {formatDate(session.last_activity)}
                        </div>
                        <div className="text-xs text-gray-500">{session.user_agent}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={session.is_active ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}>
                        {session.is_active ? '활성' : '비활성'}
                      </Badge>
                      <Button
                        size="sm"
                        onClick={() => handleInvalidateSession(session.session_id)}
                        className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700"
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
        <DialogContent className="bg-white/10 backdrop-blur-sm border border-white/20">
          <DialogHeader>
            <DialogTitle className="text-white">로그인</DialogTitle>
            <DialogDescription className="text-gray-300">관리자 계정으로 로그인합니다</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <Label className="text-gray-300">사용자명</Label>
              <Input
                value={loginForm.username}
                onChange={(e) => setLoginForm({ ...loginForm, username: e.target.value })}
                className="mt-1 bg-white/10 border-white/20 text-white"
                placeholder="사용자명을 입력하세요"
              />
            </div>
            <div>
              <Label className="text-gray-300">비밀번호</Label>
              <div className="relative">
                <Input
                  type={showPassword ? 'text' : 'password'}
                  value={loginForm.password}
                  onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                  className="mt-1 bg-white/10 border-white/20 text-white pr-10"
                  placeholder="비밀번호를 입력하세요"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-white/10"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff className="h-4 w-4 text-gray-400" /> : <Eye className="h-4 w-4 text-gray-400" />}
                </Button>
              </div>
            </div>
            <div className="flex gap-2">
              <Button type="submit" className="flex-1 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700">
                로그인
              </Button>
              <Button type="button" variant="outline" onClick={() => setShowLoginDialog(false)} className="border-white/20 text-white hover:bg-white/10">
                취소
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* 비밀번호 변경 다이얼로그 */}
      <Dialog open={showPasswordDialog} onOpenChange={setShowPasswordDialog}>
        <DialogContent className="bg-white/10 backdrop-blur-sm border border-white/20">
          <DialogHeader>
            <DialogTitle className="text-white">비밀번호 변경</DialogTitle>
            <DialogDescription className="text-gray-300">새로운 비밀번호로 변경합니다</DialogDescription>
          </DialogHeader>
          <form onSubmit={handlePasswordChange} className="space-y-4">
            <div>
              <Label className="text-gray-300">현재 비밀번호</Label>
              <div className="relative">
                <Input
                  type={showPassword ? 'text' : 'password'}
                  value={passwordForm.current_password}
                  onChange={(e) => setPasswordForm({ ...passwordForm, current_password: e.target.value })}
                  className="mt-1 bg-white/10 border-white/20 text-white pr-10"
                  placeholder="현재 비밀번호를 입력하세요"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-white/10"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff className="h-4 w-4 text-gray-400" /> : <Eye className="h-4 w-4 text-gray-400" />}
                </Button>
              </div>
            </div>
            <div>
              <Label className="text-gray-300">새 비밀번호</Label>
              <div className="relative">
                <Input
                  type={showNewPassword ? 'text' : 'password'}
                  value={passwordForm.new_password}
                  onChange={(e) => setPasswordForm({ ...passwordForm, new_password: e.target.value })}
                  className="mt-1 bg-white/10 border-white/20 text-white pr-10"
                  placeholder="새 비밀번호를 입력하세요"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-white/10"
                  onClick={() => setShowNewPassword(!showNewPassword)}
                >
                  {showNewPassword ? <EyeOff className="h-4 w-4 text-gray-400" /> : <Eye className="h-4 w-4 text-gray-400" />}
                </Button>
              </div>
            </div>
            <div>
              <Label className="text-gray-300">새 비밀번호 확인</Label>
              <div className="relative">
                <Input
                  type={showConfirmPassword ? 'text' : 'password'}
                  value={passwordForm.confirm_password}
                  onChange={(e) => setPasswordForm({ ...passwordForm, confirm_password: e.target.value })}
                  className="mt-1 bg-white/10 border-white/20 text-white pr-10"
                  placeholder="새 비밀번호를 다시 입력하세요"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-white/10"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                >
                  {showConfirmPassword ? <EyeOff className="h-4 w-4 text-gray-400" /> : <Eye className="h-4 w-4 text-gray-400" />}
                </Button>
              </div>
            </div>
            <div className="flex gap-2">
              <Button type="submit" className="flex-1 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700">
                변경
              </Button>
              <Button type="button" variant="outline" onClick={() => setShowPasswordDialog(false)} className="border-white/20 text-white hover:bg-white/10">
                취소
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default SecurityPage; 
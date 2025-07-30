"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Alert, AlertDescription, AlertTitle } from './ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { 
  Shield, 
  Lock, 
  Eye, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  Fingerprint,
  Smartphone,
  Mail,
  Key,
  Activity,
  BarChart3,
  Clock,
  Users,
  Globe
} from 'lucide-react';

interface SecurityEvent {
  event_id: string;
  event_type: string;
  user_id?: string;
  ip_address: string;
  timestamp: string;
  security_level: string;
  description: string;
  success: boolean;
}

interface SecurityAlert {
  alert_id: string;
  alert_type: string;
  severity: string;
  title: string;
  description: string;
  timestamp: string;
  user_id?: string;
  ip_address: string;
  resolved: boolean;
}

interface SecurityReport {
  period: string;
  total_events: number;
  total_alerts: number;
  event_stats: Record<string, number>;
  security_stats: Record<string, number>;
  alert_stats: Record<string, number>;
  unresolved_alerts: number;
  threat_indicators: number;
}

const SecurityDashboard: React.FC = () => {
  const [events, setEvents] = useState<SecurityEvent[]>([]);
  const [alerts, setAlerts] = useState<SecurityAlert[]>([]);
  const [report, setReport] = useState<SecurityReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  // MFA 설정 상태
  const [mfaSetup, setMfaSetup] = useState({
    totp: false,
    email: false,
    biometric: false
  });

  // 암호화 상태
  const [encryptionStatus, setEncryptionStatus] = useState({
    keys_generated: 0,
    data_encrypted: 0,
    active_sessions: 0
  });

  useEffect(() => {
    fetchSecurityData();
  }, []);

  const fetchSecurityData = async () => {
    try {
      setLoading(true);
      
      // 병렬로 데이터 가져오기
      const [eventsRes, alertsRes, reportRes] = await Promise.all([
        fetch('/api/security/audit/events?hours=24'),
        fetch('/api/security/audit/alerts?hours=24'),
        fetch('/api/security/audit/report?hours=24')
      ]);

      if (eventsRes.ok) {
        const eventsData = await eventsRes.json();
        setEvents(eventsData.data.events);
      }

      if (alertsRes.ok) {
        const alertsData = await alertsRes.json();
        setAlerts(alertsData.data.alerts);
      }

      if (reportRes.ok) {
        const reportData = await reportRes.json();
        setReport(reportData.data);
      }

    } catch (error) {
      console.error('보안 데이터 가져오기 오류:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'bg-red-500';
      case 'high':
        return 'bg-orange-500';
      case 'medium':
        return 'bg-yellow-500';
      case 'low':
        return 'bg-blue-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getEventIcon = (eventType: string) => {
    switch (eventType) {
      case 'login':
        return <Key className="h-4 w-4" />;
      case 'mfa_enabled':
        return <Shield className="h-4 w-4" />;
      case 'data_export':
        return <Globe className="h-4 w-4" />;
      case 'suspicious_activity':
        return <AlertTriangle className="h-4 w-4" />;
      default:
        return <Activity className="h-4 w-4" />;
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('ko-KR');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">보안 대시보드</h1>
          <p className="text-muted-foreground">
            시스템 보안 상태 및 이벤트 모니터링
          </p>
        </div>
        <Button onClick={fetchSecurityData} variant="outline">
          새로고침
        </Button>
      </div>

      {/* 보안 상태 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 이벤트</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{report?.total_events || 0}</div>
            <p className="text-xs text-muted-foreground">
              지난 24시간
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">보안 알림</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{report?.total_alerts || 0}</div>
            <p className="text-xs text-muted-foreground">
              미해결: {report?.unresolved_alerts || 0}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">위협 지표</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{report?.threat_indicators || 0}</div>
            <p className="text-xs text-muted-foreground">
              활성 위협
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">시스템 상태</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">정상</div>
            <p className="text-xs text-muted-foreground">
              모든 시스템 운영 중
            </p>
          </CardContent>
        </Card>
      </div>

      {/* 탭 네비게이션 */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">개요</TabsTrigger>
          <TabsTrigger value="events">이벤트</TabsTrigger>
          <TabsTrigger value="alerts">알림</TabsTrigger>
          <TabsTrigger value="mfa">MFA 관리</TabsTrigger>
        </TabsList>

        {/* 개요 탭 */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* 이벤트 통계 */}
            <Card>
              <CardHeader>
                <CardTitle>이벤트 통계</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {report?.event_stats && Object.entries(report.event_stats).map(([type, count]) => (
                    <div key={type} className="flex items-center justify-between">
                      <span className="text-sm capitalize">{type.replace('_', ' ')}</span>
                      <Badge variant="secondary">{count}</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* 보안 수준별 통계 */}
            <Card>
              <CardHeader>
                <CardTitle>보안 수준별 통계</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {report?.security_stats && Object.entries(report.security_stats).map(([level, count]) => (
                    <div key={level} className="flex items-center justify-between">
                      <span className="text-sm capitalize">{level}</span>
                      <Badge className={getSeverityColor(level)}>{count}</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 최근 활동 */}
          <Card>
            <CardHeader>
              <CardTitle>최근 보안 활동</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {events.slice(0, 5).map((event) => (
                  <div key={event.event_id} className="flex items-center space-x-3 p-3 border rounded-lg">
                    <div className={`p-2 rounded-full ${event.success ? 'bg-green-100' : 'bg-red-100'}`}>
                      {getEventIcon(event.event_type)}
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">{event.description}</p>
                      <p className="text-xs text-muted-foreground">
                        {event.user_id} • {event.ip_address} • {formatTimestamp(event.timestamp)}
                      </p>
                    </div>
                    <Badge variant={event.success ? "default" : "destructive"}>
                      {event.success ? '성공' : '실패'}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 이벤트 탭 */}
        <TabsContent value="events" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>보안 이벤트 로그</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {events.map((event) => (
                  <div key={event.event_id} className="flex items-center space-x-3 p-3 border rounded-lg">
                    <div className={`p-2 rounded-full ${event.success ? 'bg-green-100' : 'bg-red-100'}`}>
                      {getEventIcon(event.event_type)}
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">{event.description}</p>
                      <p className="text-xs text-muted-foreground">
                        {event.user_id} • {event.ip_address} • {formatTimestamp(event.timestamp)}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge className={getSeverityColor(event.security_level)}>
                        {event.security_level}
                      </Badge>
                      <Badge variant={event.success ? "default" : "destructive"}>
                        {event.success ? '성공' : '실패'}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 알림 탭 */}
        <TabsContent value="alerts" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>보안 알림</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {alerts.map((alert) => (
                  <Alert key={alert.alert_id} className={alert.resolved ? 'opacity-60' : ''}>
                    <AlertTriangle className="h-4 w-4" />
                    <AlertTitle className="flex items-center justify-between">
                      {alert.title}
                      <div className="flex items-center space-x-2">
                        <Badge className={getSeverityColor(alert.severity)}>
                          {alert.severity}
                        </Badge>
                        {alert.resolved && (
                          <Badge variant="secondary">해결됨</Badge>
                        )}
                      </div>
                    </AlertTitle>
                    <AlertDescription>
                      <p className="mb-2">{alert.description}</p>
                      <p className="text-xs text-muted-foreground">
                        {alert.user_id} • {alert.ip_address} • {formatTimestamp(alert.timestamp)}
                      </p>
                    </AlertDescription>
                  </Alert>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* MFA 관리 탭 */}
        <TabsContent value="mfa" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* TOTP 설정 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Smartphone className="h-5 w-5" />
                  <span>TOTP 설정</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <Badge variant={mfaSetup.totp ? "default" : "secondary"}>
                      {mfaSetup.totp ? '활성화' : '비활성화'}
                    </Badge>
                  </div>
                  <Button variant="outline" className="w-full">
                    {mfaSetup.totp ? 'TOTP 비활성화' : 'TOTP 설정'}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* 이메일 MFA */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Mail className="h-5 w-5" />
                  <span>이메일 MFA</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <Badge variant={mfaSetup.email ? "default" : "secondary"}>
                      {mfaSetup.email ? '활성화' : '비활성화'}
                    </Badge>
                  </div>
                  <Button variant="outline" className="w-full">
                    {mfaSetup.email ? '이메일 MFA 비활성화' : '이메일 MFA 설정'}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* 생체 인증 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Fingerprint className="h-5 w-5" />
                  <span>생체 인증</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <Badge variant={mfaSetup.biometric ? "default" : "secondary"}>
                      {mfaSetup.biometric ? '활성화' : '비활성화'}
                    </Badge>
                  </div>
                  <Button variant="outline" className="w-full">
                    {mfaSetup.biometric ? '생체 인증 비활성화' : '생체 인증 설정'}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* 백업 코드 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Key className="h-5 w-5" />
                  <span>백업 코드</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <p className="text-sm text-muted-foreground">
                    MFA 장치를 잃어버렸을 때 사용할 백업 코드를 생성합니다.
                  </p>
                  <Button variant="outline" className="w-full">
                    백업 코드 생성
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default SecurityDashboard; 
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { 
  Shield, 
  AlertTriangle, 
  Eye, 
  Play, 
  Square, 
  RefreshCw,
  Search,
  Filter,
  Download,
  Upload,
  Lock,
  Unlock,
  CheckCircle,
  XCircle,
  Clock,
  TrendingUp,
  TrendingDown,
  Activity,
  Zap,
  AlertCircle,
  Info,
  FileText,
  Code,
  Globe,
  Database,
  Server
} from 'lucide-react';

interface SecuritySummary {
  open_vulnerabilities: number;
  active_malware: number;
  unresolved_events: number;
  critical_plugins: number;
  high_risk_plugins: number;
  recent_events: Array<[string, string, string, string, string]>;
}

interface Vulnerability {
  id: string;
  plugin_id: string;
  severity: string;
  title: string;
  description: string;
  cve_id?: string;
  cvss_score?: number;
  affected_component: string;
  remediation: string;
  discovered_at: string;
  status: string;
  false_positive_reason: string;
}

interface MalwareDetection {
  id: string;
  plugin_id: string;
  file_path: string;
  malware_type: string;
  signature: string;
  confidence: number;
  description: string;
  detected_at: string;
  status: string;
}

interface SecurityEvent {
  id: string;
  plugin_id: string;
  event_type: string;
  severity: string;
  description: string;
  source_ip?: string;
  user_id?: string;
  timestamp: string;
  resolved: boolean;
  resolution_notes: string;
}

interface SecurityProfile {
  plugin_id: string;
  risk_level: string;
  last_scan: string;
  vulnerabilities_count: number;
  malware_count: number;
  security_events_count: number;
  permissions?: string;
  network_access?: string;
  file_access?: string;
  api_calls?: string;
  security_score: number;
  compliance_status: string;
}

interface ScanHistory {
  id: string;
  plugin_id: string;
  scan_type: string;
  started_at: string;
  completed_at?: string;
  status: string;
  findings_count: number;
  scan_duration?: number;
}

const EnhancedSecurityDashboard: React.FC = () => {
  const [summary, setSummary] = useState<SecuritySummary | null>(null);
  const [vulnerabilities, setVulnerabilities] = useState<Vulnerability[]>([]);
  const [malwareDetections, setMalwareDetections] = useState<MalwareDetection[]>([]);
  const [securityEvents, setSecurityEvents] = useState<SecurityEvent[]>([]);
  const [securityProfiles, setSecurityProfiles] = useState<SecurityProfile[]>([]);
  const [scanHistory, setScanHistory] = useState<ScanHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [monitoringActive, setMonitoringActive] = useState(false);
  const [selectedVulnerability, setSelectedVulnerability] = useState<Vulnerability | null>(null);
  const [selectedMalware, setSelectedMalware] = useState<MalwareDetection | null>(null);
  const [selectedEvent, setSelectedEvent] = useState<SecurityEvent | null>(null);
  const [showVulnDialog, setShowVulnDialog] = useState(false);
  const [showMalwareDialog, setShowMalwareDialog] = useState(false);
  const [showEventDialog, setShowEventDialog] = useState(false);
  const [resolutionNotes, setResolutionNotes] = useState('');

  // 데이터 로드
  useEffect(() => {
    loadSecurityData();
  }, []);

  const loadSecurityData = async () => {
    try {
      setLoading(true);
      
      // 보안 요약 로드
      const summaryResponse = await fetch('/api/enhanced-security/summary');
      if (summaryResponse.ok) {
        const summaryData = await summaryResponse.json();
        setSummary(summaryData.data);
      }
      
      // 취약점 목록 로드
      const vulnResponse = await fetch('/api/enhanced-security/vulnerabilities?limit=20');
      if (vulnResponse.ok) {
        const vulnData = await vulnResponse.json();
        setVulnerabilities(vulnData.data);
      }
      
      // 악성코드 감지 목록 로드
      const malwareResponse = await fetch('/api/enhanced-security/malware?limit=20');
      if (malwareResponse.ok) {
        const malwareData = await malwareResponse.json();
        setMalwareDetections(malwareData.data);
      }
      
      // 보안 이벤트 목록 로드
      const eventsResponse = await fetch('/api/enhanced-security/events?limit=20');
      if (eventsResponse.ok) {
        const eventsData = await eventsResponse.json();
        setSecurityEvents(eventsData.data);
      }
      
      // 보안 프로필 목록 로드
      const profilesResponse = await fetch('/api/enhanced-security/profiles?limit=20');
      if (profilesResponse.ok) {
        const profilesData = await profilesResponse.json();
        setSecurityProfiles(profilesData.data);
      }
      
      // 스캔 이력 로드
      const scansResponse = await fetch('/api/enhanced-security/scans?limit=20');
      if (scansResponse.ok) {
        const scansData = await scansResponse.json();
        setScanHistory(scansData.data);
      }
      
    } catch (error) {
      console.error('보안 데이터 로드 오류:', error);
    } finally {
      setLoading(false);
    }
  };

  const startMonitoring = async () => {
    try {
      const response = await fetch('/api/enhanced-security/monitoring/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        setMonitoringActive(true);
        alert('보안 모니터링이 시작되었습니다.');
      } else {
        alert('보안 모니터링 시작에 실패했습니다.');
      }
    } catch (error) {
      console.error('보안 모니터링 시작 오류:', error);
      alert('보안 모니터링 시작 중 오류가 발생했습니다.');
    }
  };

  const stopMonitoring = async () => {
    try {
      const response = await fetch('/api/enhanced-security/monitoring/stop', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        setMonitoringActive(false);
        alert('보안 모니터링이 중지되었습니다.');
      } else {
        alert('보안 모니터링 중지에 실패했습니다.');
      }
    } catch (error) {
      console.error('보안 모니터링 중지 오류:', error);
      alert('보안 모니터링 중지 중 오류가 발생했습니다.');
    }
  };

  const startSecurityScan = async (pluginId?: string) => {
    try {
      const response = await fetch('/api/enhanced-security/scan/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ plugin_id: pluginId })
      });
      
      if (response.ok) {
        alert(pluginId ? `플러그인 ${pluginId} 보안 스캔이 시작되었습니다.` : '전체 플러그인 보안 스캔이 시작되었습니다.');
        setTimeout(loadSecurityData, 5000); // 5초 후 데이터 새로고침
      } else {
        alert('보안 스캔 시작에 실패했습니다.');
      }
    } catch (error) {
      console.error('보안 스캔 시작 오류:', error);
      alert('보안 스캔 시작 중 오류가 발생했습니다.');
    }
  };

  const updateVulnerabilityStatus = async (vulnId: string, status: string, falsePositiveReason?: string) => {
    try {
      const response = await fetch(`/api/enhanced-security/vulnerabilities/${vulnId}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          status, 
          false_positive_reason: falsePositiveReason || '' 
        })
      });
      
      if (response.ok) {
        alert('취약점 상태가 업데이트되었습니다.');
        loadSecurityData();
        setShowVulnDialog(false);
      } else {
        alert('취약점 상태 업데이트에 실패했습니다.');
      }
    } catch (error) {
      console.error('취약점 상태 업데이트 오류:', error);
      alert('취약점 상태 업데이트 중 오류가 발생했습니다.');
    }
  };

  const quarantineMalware = async (detectionId: string) => {
    try {
      const response = await fetch(`/api/enhanced-security/malware/${detectionId}/quarantine`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        alert('악성코드가 격리되었습니다.');
        loadSecurityData();
        setShowMalwareDialog(false);
      } else {
        alert('악성코드 격리에 실패했습니다.');
      }
    } catch (error) {
      console.error('악성코드 격리 오류:', error);
      alert('악성코드 격리 중 오류가 발생했습니다.');
    }
  };

  const resolveSecurityEvent = async (eventId: string) => {
    try {
      const response = await fetch(`/api/enhanced-security/events/${eventId}/resolve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ resolution_notes: resolutionNotes })
      });
      
      if (response.ok) {
        alert('보안 이벤트가 해결되었습니다.');
        loadSecurityData();
        setShowEventDialog(false);
        setResolutionNotes('');
      } else {
        alert('보안 이벤트 해결에 실패했습니다.');
      }
    } catch (error) {
      console.error('보안 이벤트 해결 오류:', error);
      alert('보안 이벤트 해결 중 오류가 발생했습니다.');
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical': return 'bg-red-500';
      case 'high': return 'bg-orange-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  };

  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel.toLowerCase()) {
      case 'critical': return 'bg-red-500';
      case 'high': return 'bg-orange-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('ko-KR');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">보안 대시보드를 로드하는 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">플러그인 보안 모니터링</h1>
          <p className="text-gray-600 mt-2">플러그인 보안 상태를 실시간으로 모니터링하고 관리하세요</p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant={monitoringActive ? "destructive" : "default"}
            onClick={monitoringActive ? stopMonitoring : startMonitoring}
          >
            {monitoringActive ? <Square className="w-4 h-4 mr-2" /> : <Play className="w-4 h-4 mr-2" />}
            {monitoringActive ? '모니터링 중지' : '모니터링 시작'}
          </Button>
          <Button onClick={() => startSecurityScan()}>
            <RefreshCw className="w-4 h-4 mr-2" />
            전체 스캔
          </Button>
        </div>
      </div>

      {/* 보안 요약 카드 */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="w-5 h-5 text-red-600" />
                <div>
                  <p className="text-sm text-gray-600">미해결 취약점</p>
                  <p className="text-2xl font-bold text-red-600">{summary.open_vulnerabilities}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="w-5 h-5 text-purple-600" />
                <div>
                  <p className="text-sm text-gray-600">활성 악성코드</p>
                  <p className="text-2xl font-bold text-purple-600">{summary.active_malware}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <AlertCircle className="w-5 h-5 text-orange-600" />
                <div>
                  <p className="text-sm text-gray-600">미해결 이벤트</p>
                  <p className="text-2xl font-bold text-orange-600">{summary.unresolved_events}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Shield className="w-5 h-5 text-red-600" />
                <div>
                  <p className="text-sm text-gray-600">위험 플러그인</p>
                  <p className="text-2xl font-bold text-red-600">{summary.critical_plugins}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="w-5 h-5 text-orange-600" />
                <div>
                  <p className="text-sm text-gray-600">높은 위험</p>
                  <p className="text-2xl font-bold text-orange-600">{summary.high_risk_plugins}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Activity className="w-5 h-5 text-blue-600" />
                <div>
                  <p className="text-sm text-gray-600">최근 이벤트</p>
                  <p className="text-2xl font-bold text-blue-600">{summary.recent_events.length}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 메인 콘텐츠 */}
      <Tabs defaultValue="vulnerabilities" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="vulnerabilities">취약점</TabsTrigger>
          <TabsTrigger value="malware">악성코드</TabsTrigger>
          <TabsTrigger value="events">보안 이벤트</TabsTrigger>
          <TabsTrigger value="profiles">보안 프로필</TabsTrigger>
          <TabsTrigger value="scans">스캔 이력</TabsTrigger>
        </TabsList>

        {/* 취약점 탭 */}
        <TabsContent value="vulnerabilities" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <AlertTriangle className="w-5 h-5 text-red-600" />
                <span>보안 취약점</span>
                <Badge variant="outline">{vulnerabilities.length}</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {vulnerabilities.map((vuln) => (
                  <div key={vuln.id} className="border rounded-lg p-4 hover:bg-gray-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <Badge className={getSeverityColor(vuln.severity)}>
                            {vuln.severity.toUpperCase()}
                          </Badge>
                          <span className="font-medium">{vuln.title}</span>
                          {vuln.cve_id && (
                            <Badge variant="outline">{vuln.cve_id}</Badge>
                          )}
                        </div>
                        <p className="text-gray-700 mb-2">{vuln.description}</p>
                        <div className="text-sm text-gray-500 space-y-1">
                          <p>플러그인: {vuln.plugin_id}</p>
                          <p>영향받는 컴포넌트: {vuln.affected_component}</p>
                          <p>발견일: {formatDate(vuln.discovered_at)}</p>
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setSelectedVulnerability(vuln);
                            setShowVulnDialog(true);
                          }}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => updateVulnerabilityStatus(vuln.id, 'fixed')}
                        >
                          <CheckCircle className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
                
                {vulnerabilities.length === 0 && (
                  <p className="text-center text-gray-500 py-8">
                    발견된 취약점이 없습니다.
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 악성코드 탭 */}
        <TabsContent value="malware" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <AlertTriangle className="w-5 h-5 text-purple-600" />
                <span>악성코드 감지</span>
                <Badge variant="outline">{malwareDetections.length}</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {malwareDetections.map((malware) => (
                  <div key={malware.id} className="border rounded-lg p-4 hover:bg-gray-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <Badge className="bg-purple-500">
                            {malware.malware_type.toUpperCase()}
                          </Badge>
                          <span className="font-medium">악성코드 감지</span>
                          <Badge variant="outline">
                            {(malware.confidence * 100).toFixed(0)}% 신뢰도
                          </Badge>
                        </div>
                        <p className="text-gray-700 mb-2">{malware.description}</p>
                        <div className="text-sm text-gray-500 space-y-1">
                          <p>플러그인: {malware.plugin_id}</p>
                          <p>파일 경로: {malware.file_path}</p>
                          <p>감지일: {formatDate(malware.detected_at)}</p>
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setSelectedMalware(malware);
                            setShowMalwareDialog(true);
                          }}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        {malware.status === 'detected' && (
                          <Button
                            variant="destructive"
                            size="sm"
                            onClick={() => quarantineMalware(malware.id)}
                          >
                            <Lock className="w-4 h-4" />
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                
                {malwareDetections.length === 0 && (
                  <p className="text-center text-gray-500 py-8">
                    감지된 악성코드가 없습니다.
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 보안 이벤트 탭 */}
        <TabsContent value="events" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <AlertCircle className="w-5 h-5 text-orange-600" />
                <span>보안 이벤트</span>
                <Badge variant="outline">{securityEvents.length}</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {securityEvents.map((event) => (
                  <div key={event.id} className="border rounded-lg p-4 hover:bg-gray-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <Badge className={getSeverityColor(event.severity)}>
                            {event.severity.toUpperCase()}
                          </Badge>
                          <Badge variant="outline">{event.event_type}</Badge>
                          {event.resolved && (
                            <Badge className="bg-green-500">
                              <CheckCircle className="w-3 h-3 mr-1" />
                              해결됨
                            </Badge>
                          )}
                        </div>
                        <p className="text-gray-700 mb-2">{event.description}</p>
                        <div className="text-sm text-gray-500 space-y-1">
                          <p>플러그인: {event.plugin_id}</p>
                          {event.source_ip && <p>소스 IP: {event.source_ip}</p>}
                          {event.user_id && <p>사용자: {event.user_id}</p>}
                          <p>발생일: {formatDate(event.timestamp)}</p>
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setSelectedEvent(event);
                            setShowEventDialog(true);
                          }}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        {!event.resolved && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setSelectedEvent(event);
                              setShowEventDialog(true);
                            }}
                          >
                            <CheckCircle className="w-4 h-4" />
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                
                {securityEvents.length === 0 && (
                  <p className="text-center text-gray-500 py-8">
                    발생한 보안 이벤트가 없습니다.
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 보안 프로필 탭 */}
        <TabsContent value="profiles" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Shield className="w-5 h-5 text-blue-600" />
                <span>플러그인 보안 프로필</span>
                <Badge variant="outline">{securityProfiles.length}</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {securityProfiles.map((profile) => (
                  <div key={profile.plugin_id} className="border rounded-lg p-4 hover:bg-gray-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <Badge className={getRiskLevelColor(profile.risk_level)}>
                            {profile.risk_level.toUpperCase()}
                          </Badge>
                          <span className="font-medium">{profile.plugin_id}</span>
                          <Badge variant="outline">
                            {profile.compliance_status}
                          </Badge>
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-2">
                          <div>
                            <p className="text-sm text-gray-500">보안 점수</p>
                            <div className="flex items-center space-x-2">
                              <Progress value={profile.security_score} className="w-20" />
                              <span className="text-sm font-medium">{profile.security_score.toFixed(1)}</span>
                            </div>
                          </div>
                          <div>
                            <p className="text-sm text-gray-500">취약점</p>
                            <p className="text-sm font-medium">{profile.vulnerabilities_count}</p>
                          </div>
                          <div>
                            <p className="text-sm text-gray-500">악성코드</p>
                            <p className="text-sm font-medium">{profile.malware_count}</p>
                          </div>
                          <div>
                            <p className="text-sm text-gray-500">보안 이벤트</p>
                            <p className="text-sm font-medium">{profile.security_events_count}</p>
                          </div>
                        </div>
                        <div className="text-sm text-gray-500">
                          <p>마지막 스캔: {formatDate(profile.last_scan)}</p>
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => startSecurityScan(profile.plugin_id)}
                        >
                          <RefreshCw className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
                
                {securityProfiles.length === 0 && (
                  <p className="text-center text-gray-500 py-8">
                    보안 프로필이 없습니다.
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 스캔 이력 탭 */}
        <TabsContent value="scans" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Activity className="w-5 h-5 text-green-600" />
                <span>보안 스캔 이력</span>
                <Badge variant="outline">{scanHistory.length}</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {scanHistory.map((scan) => (
                  <div key={scan.id} className="border rounded-lg p-4 hover:bg-gray-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <Badge variant="outline">{scan.scan_type}</Badge>
                          <span className="font-medium">{scan.plugin_id}</span>
                          <Badge className={scan.status === 'completed' ? 'bg-green-500' : 'bg-yellow-500'}>
                            {scan.status}
                          </Badge>
                        </div>
                        <div className="text-sm text-gray-500 space-y-1">
                          <p>시작: {formatDate(scan.started_at)}</p>
                          {scan.completed_at && <p>완료: {formatDate(scan.completed_at)}</p>}
                          <p>발견 항목: {scan.findings_count}</p>
                          {scan.scan_duration && <p>소요 시간: {scan.scan_duration.toFixed(2)}초</p>}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                
                {scanHistory.length === 0 && (
                  <p className="text-center text-gray-500 py-8">
                    스캔 이력이 없습니다.
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* 취약점 상세 다이얼로그 */}
      <Dialog open={showVulnDialog} onOpenChange={setShowVulnDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>취약점 상세 정보</DialogTitle>
          </DialogHeader>
          
          {selectedVulnerability && (
            <div className="space-y-4">
              <div>
                <Label>제목</Label>
                <p className="text-sm text-gray-700">{selectedVulnerability.title}</p>
              </div>
              
              <div>
                <Label>설명</Label>
                <p className="text-sm text-gray-700">{selectedVulnerability.description}</p>
              </div>
              
              <div>
                <Label>해결 방법</Label>
                <p className="text-sm text-gray-700">{selectedVulnerability.remediation}</p>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>심각도</Label>
                  <Badge className={getSeverityColor(selectedVulnerability.severity)}>
                    {selectedVulnerability.severity.toUpperCase()}
                  </Badge>
                </div>
                <div>
                  <Label>상태</Label>
                  <Badge variant="outline">{selectedVulnerability.status}</Badge>
                </div>
              </div>
              
              <div className="flex justify-end space-x-2">
                <Button
                  variant="outline"
                  onClick={() => updateVulnerabilityStatus(selectedVulnerability.id, 'fixed')}
                >
                  해결됨으로 표시
                </Button>
                <Button
                  variant="outline"
                  onClick={() => updateVulnerabilityStatus(selectedVulnerability.id, 'false_positive')}
                >
                  오탐으로 표시
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* 악성코드 상세 다이얼로그 */}
      <Dialog open={showMalwareDialog} onOpenChange={setShowMalwareDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>악성코드 상세 정보</DialogTitle>
          </DialogHeader>
          
          {selectedMalware && (
            <div className="space-y-4">
              <div>
                <Label>파일 경로</Label>
                <p className="text-sm text-gray-700">{selectedMalware.file_path}</p>
              </div>
              
              <div>
                <Label>악성코드 유형</Label>
                <Badge className="bg-purple-500">{selectedMalware.malware_type}</Badge>
              </div>
              
              <div>
                <Label>설명</Label>
                <p className="text-sm text-gray-700">{selectedMalware.description}</p>
              </div>
              
              <div>
                <Label>신뢰도</Label>
                <div className="flex items-center space-x-2">
                  <Progress value={selectedMalware.confidence * 100} className="w-32" />
                  <span className="text-sm">{(selectedMalware.confidence * 100).toFixed(0)}%</span>
                </div>
              </div>
              
              <div className="flex justify-end space-x-2">
                {selectedMalware.status === 'detected' && (
                  <Button
                    variant="destructive"
                    onClick={() => quarantineMalware(selectedMalware.id)}
                  >
                    격리
                  </Button>
                )}
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* 보안 이벤트 상세 다이얼로그 */}
      <Dialog open={showEventDialog} onOpenChange={setShowEventDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>보안 이벤트 상세 정보</DialogTitle>
          </DialogHeader>
          
          {selectedEvent && (
            <div className="space-y-4">
              <div>
                <Label>이벤트 유형</Label>
                <Badge variant="outline">{selectedEvent.event_type}</Badge>
              </div>
              
              <div>
                <Label>설명</Label>
                <p className="text-sm text-gray-700">{selectedEvent.description}</p>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>심각도</Label>
                  <Badge className={getSeverityColor(selectedEvent.severity)}>
                    {selectedEvent.severity.toUpperCase()}
                  </Badge>
                </div>
                <div>
                  <Label>상태</Label>
                  <Badge className={selectedEvent.resolved ? 'bg-green-500' : 'bg-yellow-500'}>
                    {selectedEvent.resolved ? '해결됨' : '미해결'}
                  </Badge>
                </div>
              </div>
              
              {!selectedEvent.resolved && (
                <div>
                  <Label>해결 노트</Label>
                  <Textarea
                    value={resolutionNotes}
                    onChange={(e) => setResolutionNotes(e.target.value)}
                    placeholder="이벤트 해결에 대한 노트를 입력하세요..."
                    rows={3}
                  />
                </div>
              )}
              
              <div className="flex justify-end space-x-2">
                {!selectedEvent.resolved && (
                  <Button
                    onClick={() => resolveSecurityEvent(selectedEvent.id)}
                  >
                    해결됨으로 표시
                  </Button>
                )}
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default EnhancedSecurityDashboard; 
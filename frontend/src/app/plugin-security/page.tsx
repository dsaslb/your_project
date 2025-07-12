'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Separator } from '@/components/ui/separator';
import { Shield, Key, Eye, AlertTriangle, CheckCircle, XCircle, Clock, Users } from 'lucide-react';

interface SecurityPolicy {
  plugin_id: string;
  security_level: string;
  allowed_ips: string[];
  allowed_domains: string[];
  max_requests_per_minute: number;
  require_authentication: boolean;
  require_authorization: boolean;
  allowed_permissions: string[];
  created_at: string;
  updated_at: string;
}

interface ApiKey {
  key_id: string;
  plugin_id: string;
  name: string;
  permissions: string[];
  expires_at?: string;
  last_used?: string;
  created_at: string;
  is_active: boolean;
}

interface AuditLog {
  log_id: string;
  plugin_id: string;
  user_id?: string;
  action: string;
  resource: string;
  ip_address: string;
  user_agent: string;
  success: boolean;
  details: any;
  timestamp: string;
}

interface Vulnerability {
  report_id: string;
  plugin_id: string;
  severity: string;
  title: string;
  description: string;
  cve_id?: string;
  affected_versions: string[];
  fixed_versions: string[];
  remediation: string;
  discovered_at: string;
  status: string;
}

export default function PluginSecurityPage() {
  const [activeTab, setActiveTab] = useState('policies');
  const [policies, setPolicies] = useState<SecurityPolicy[]>([]);
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [vulnerabilities, setVulnerabilities] = useState<Vulnerability[]>([]);
  const [securityLevels, setSecurityLevels] = useState<string[]>([]);
  const [permissionTypes, setPermissionTypes] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // 다이얼로그 상태
  const [showCreatePolicy, setShowCreatePolicy] = useState(false);
  const [showCreateApiKey, setShowCreateApiKey] = useState(false);
  const [showVulnerabilityScan, setShowVulnerabilityScan] = useState(false);

  // 폼 데이터
  const [policyForm, setPolicyForm] = useState({
    plugin_id: '',
    security_level: 'medium',
    allowed_ips: '',
    allowed_domains: '',
    max_requests_per_minute: 100,
    require_authentication: true,
    require_authorization: true,
    allowed_permissions: ['read']
  });

  const [apiKeyForm, setApiKeyForm] = useState({
    plugin_id: '',
    name: '',
    permissions: ['read'],
    expires_in_days: 30
  });

  const [scanForm, setScanForm] = useState({
    plugin_id: ''
  });

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        loadSecurityLevels(),
        loadPermissionTypes(),
        loadPolicies(),
        loadApiKeys(),
        loadAuditLogs(),
        loadVulnerabilities()
      ]);
    } catch (error) {
      setError('데이터 로드 중 오류가 발생했습니다');
    } finally {
      setLoading(false);
    }
  };

  const loadSecurityLevels = async () => {
    try {
      const response = await fetch('/api/plugin-security/security-levels');
      const data = await response.json();
      if (data.success) {
        setSecurityLevels(data.data);
      }
    } catch (error) {
      console.error('보안 레벨 로드 실패:', error);
    }
  };

  const loadPermissionTypes = async () => {
    try {
      const response = await fetch('/api/plugin-security/permission-types');
      const data = await response.json();
      if (data.success) {
        setPermissionTypes(data.data);
      }
    } catch (error) {
      console.error('권한 유형 로드 실패:', error);
    }
  };

  const loadPolicies = async () => {
    try {
      const response = await fetch('/api/plugin-security/policies');
      const data = await response.json();
      if (data.success) {
        setPolicies(data.data);
      }
    } catch (error) {
      console.error('보안 정책 로드 실패:', error);
    }
  };

  const loadApiKeys = async () => {
    try {
      const response = await fetch('/api/plugin-security/api-keys');
      const data = await response.json();
      if (data.success) {
        setApiKeys(data.data);
      }
    } catch (error) {
      console.error('API 키 로드 실패:', error);
    }
  };

  const loadAuditLogs = async () => {
    try {
      const response = await fetch('/api/plugin-security/audit-logs?limit=50');
      const data = await response.json();
      if (data.success) {
        setAuditLogs(data.data);
      }
    } catch (error) {
      console.error('감사 로그 로드 실패:', error);
    }
  };

  const loadVulnerabilities = async () => {
    try {
      const response = await fetch('/api/plugin-security/vulnerabilities');
      const data = await response.json();
      if (data.success) {
        setVulnerabilities(data.data);
      }
    } catch (error) {
      console.error('취약점 보고서 로드 실패:', error);
    }
  };

  const createSecurityPolicy = async () => {
    try {
      const response = await fetch('/api/plugin-security/policies', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...policyForm,
          allowed_ips: policyForm.allowed_ips.split(',').map(ip => ip.trim()).filter(ip => ip),
          allowed_domains: policyForm.allowed_domains.split(',').map(domain => domain.trim()).filter(domain => domain)
        })
      });

      const data = await response.json();
      if (data.success) {
        setSuccess('보안 정책이 생성되었습니다');
        setShowCreatePolicy(false);
        loadPolicies();
      } else {
        setError(data.message);
      }
    } catch (error) {
      setError('보안 정책 생성 중 오류가 발생했습니다');
    }
  };

  const generateApiKey = async () => {
    try {
      const response = await fetch('/api/plugin-security/api-keys', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(apiKeyForm)
      });

      const data = await response.json();
      if (data.success) {
        setSuccess(`API 키가 생성되었습니다: ${data.data.api_key}`);
        setShowCreateApiKey(false);
        loadApiKeys();
      } else {
        setError(data.message);
      }
    } catch (error) {
      setError('API 키 생성 중 오류가 발생했습니다');
    }
  };

  const revokeApiKey = async (keyId: string) => {
    try {
      const response = await fetch(`/api/plugin-security/api-keys/${keyId}/revoke`, {
        method: 'POST'
      });

      const data = await response.json();
      if (data.success) {
        setSuccess('API 키가 폐기되었습니다');
        loadApiKeys();
      } else {
        setError(data.message);
      }
    } catch (error) {
      setError('API 키 폐기 중 오류가 발생했습니다');
    }
  };

  const scanVulnerabilities = async () => {
    try {
      const response = await fetch(`/api/plugin-security/vulnerabilities/scan/${scanForm.plugin_id}`, {
        method: 'POST'
      });

      const data = await response.json();
      if (data.success) {
        setSuccess(`${data.data.total_count}개의 취약점이 발견되었습니다`);
        setShowVulnerabilityScan(false);
        loadVulnerabilities();
      } else {
        setError(data.message);
      }
    } catch (error) {
      setError('취약점 스캔 중 오류가 발생했습니다');
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-500';
      case 'high': return 'bg-orange-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open': return 'bg-red-100 text-red-800';
      case 'fixed': return 'bg-green-100 text-green-800';
      case 'ignored': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">로딩 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Shield className="h-8 w-8 text-blue-600" />
            플러그인 보안 관리
          </h1>
          <p className="text-gray-600 mt-2">플러그인 보안 정책, API 키, 감사 로그, 취약점 관리</p>
        </div>
      </div>

      {error && (
        <Alert className="border-red-200 bg-red-50">
          <XCircle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert className="border-green-200 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">{success}</AlertDescription>
        </Alert>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="policies" className="flex items-center gap-2">
            <Shield className="h-4 w-4" />
            보안 정책
          </TabsTrigger>
          <TabsTrigger value="api-keys" className="flex items-center gap-2">
            <Key className="h-4 w-4" />
            API 키
          </TabsTrigger>
          <TabsTrigger value="audit-logs" className="flex items-center gap-2">
            <Eye className="h-4 w-4" />
            감사 로그
          </TabsTrigger>
          <TabsTrigger value="vulnerabilities" className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4" />
            취약점
          </TabsTrigger>
        </TabsList>

        <TabsContent value="policies" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>보안 정책 관리</CardTitle>
                  <CardDescription>플러그인별 보안 정책을 설정하고 관리합니다</CardDescription>
                </div>
                <Dialog open={showCreatePolicy} onOpenChange={setShowCreatePolicy}>
                  <DialogTrigger asChild>
                    <Button>새 정책 생성</Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-2xl">
                    <DialogHeader>
                      <DialogTitle>보안 정책 생성</DialogTitle>
                      <DialogDescription>새로운 플러그인 보안 정책을 생성합니다</DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div>
                        <Label htmlFor="plugin_id">플러그인 ID</Label>
                        <Input
                          id="plugin_id"
                          value={policyForm.plugin_id}
                          onChange={(e) => setPolicyForm({...policyForm, plugin_id: e.target.value})}
                          placeholder="plugin_id"
                        />
                      </div>
                      <div>
                        <Label htmlFor="security_level">보안 레벨</Label>
                        <Select value={policyForm.security_level} onValueChange={(value) => setPolicyForm({...policyForm, security_level: value})}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {securityLevels.map(level => (
                              <SelectItem key={level} value={level}>{level}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <Label htmlFor="allowed_ips">허용 IP 주소 (쉼표로 구분)</Label>
                        <Input
                          id="allowed_ips"
                          value={policyForm.allowed_ips}
                          onChange={(e) => setPolicyForm({...policyForm, allowed_ips: e.target.value})}
                          placeholder="192.168.1.1, 10.0.0.1"
                        />
                      </div>
                      <div>
                        <Label htmlFor="allowed_domains">허용 도메인 (쉼표로 구분)</Label>
                        <Input
                          id="allowed_domains"
                          value={policyForm.allowed_domains}
                          onChange={(e) => setPolicyForm({...policyForm, allowed_domains: e.target.value})}
                          placeholder="example.com, api.example.com"
                        />
                      </div>
                      <div>
                        <Label htmlFor="max_requests">분당 최대 요청 수</Label>
                        <Input
                          id="max_requests"
                          type="number"
                          value={policyForm.max_requests_per_minute}
                          onChange={(e) => setPolicyForm({...policyForm, max_requests_per_minute: parseInt(e.target.value)})}
                        />
                      </div>
                      <div className="flex items-center space-x-2">
                        <Switch
                          id="require_auth"
                          checked={policyForm.require_authentication}
                          onCheckedChange={(checked) => setPolicyForm({...policyForm, require_authentication: checked})}
                        />
                        <Label htmlFor="require_auth">인증 필요</Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Switch
                          id="require_authz"
                          checked={policyForm.require_authorization}
                          onCheckedChange={(checked) => setPolicyForm({...policyForm, require_authorization: checked})}
                        />
                        <Label htmlFor="require_authz">권한 확인 필요</Label>
                      </div>
                    </div>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setShowCreatePolicy(false)}>취소</Button>
                      <Button onClick={createSecurityPolicy}>생성</Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>플러그인 ID</TableHead>
                    <TableHead>보안 레벨</TableHead>
                    <TableHead>허용 IP</TableHead>
                    <TableHead>인증</TableHead>
                    <TableHead>권한 확인</TableHead>
                    <TableHead>작업</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {policies.map((policy) => (
                    <TableRow key={policy.plugin_id}>
                      <TableCell>{policy.plugin_id}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{policy.security_level}</Badge>
                      </TableCell>
                      <TableCell>{policy.allowed_ips.length}개</TableCell>
                      <TableCell>
                        {policy.require_authentication ? (
                          <CheckCircle className="h-4 w-4 text-green-600" />
                        ) : (
                          <XCircle className="h-4 w-4 text-red-600" />
                        )}
                      </TableCell>
                      <TableCell>
                        {policy.require_authorization ? (
                          <CheckCircle className="h-4 w-4 text-green-600" />
                        ) : (
                          <XCircle className="h-4 w-4 text-red-600" />
                        )}
                      </TableCell>
                      <TableCell>
                        <Button variant="outline" size="sm">편집</Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="api-keys" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>API 키 관리</CardTitle>
                  <CardDescription>플러그인 API 키를 생성하고 관리합니다</CardDescription>
                </div>
                <Dialog open={showCreateApiKey} onOpenChange={setShowCreateApiKey}>
                  <DialogTrigger asChild>
                    <Button>새 API 키 생성</Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>API 키 생성</DialogTitle>
                      <DialogDescription>새로운 플러그인 API 키를 생성합니다</DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div>
                        <Label htmlFor="api_plugin_id">플러그인 ID</Label>
                        <Input
                          id="api_plugin_id"
                          value={apiKeyForm.plugin_id}
                          onChange={(e) => setApiKeyForm({...apiKeyForm, plugin_id: e.target.value})}
                          placeholder="plugin_id"
                        />
                      </div>
                      <div>
                        <Label htmlFor="api_key_name">키 이름</Label>
                        <Input
                          id="api_key_name"
                          value={apiKeyForm.name}
                          onChange={(e) => setApiKeyForm({...apiKeyForm, name: e.target.value})}
                          placeholder="API 키 이름"
                        />
                      </div>
                      <div>
                        <Label htmlFor="api_key_permissions">권한</Label>
                        <Select value={apiKeyForm.permissions[0]} onValueChange={(value) => setApiKeyForm({...apiKeyForm, permissions: [value]})}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {permissionTypes.map(perm => (
                              <SelectItem key={perm} value={perm}>{perm}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <Label htmlFor="expires_in_days">만료일 (일)</Label>
                        <Input
                          id="expires_in_days"
                          type="number"
                          value={apiKeyForm.expires_in_days}
                          onChange={(e) => setApiKeyForm({...apiKeyForm, expires_in_days: parseInt(e.target.value)})}
                        />
                      </div>
                    </div>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setShowCreateApiKey(false)}>취소</Button>
                      <Button onClick={generateApiKey}>생성</Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>이름</TableHead>
                    <TableHead>플러그인 ID</TableHead>
                    <TableHead>권한</TableHead>
                    <TableHead>상태</TableHead>
                    <TableHead>만료일</TableHead>
                    <TableHead>마지막 사용</TableHead>
                    <TableHead>작업</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {apiKeys.map((apiKey) => (
                    <TableRow key={apiKey.key_id}>
                      <TableCell>{apiKey.name}</TableCell>
                      <TableCell>{apiKey.plugin_id}</TableCell>
                      <TableCell>
                        {apiKey.permissions.map(perm => (
                          <Badge key={perm} variant="outline" className="mr-1">{perm}</Badge>
                        ))}
                      </TableCell>
                      <TableCell>
                        {apiKey.is_active ? (
                          <Badge className="bg-green-100 text-green-800">활성</Badge>
                        ) : (
                          <Badge className="bg-red-100 text-red-800">비활성</Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        {apiKey.expires_at ? new Date(apiKey.expires_at).toLocaleDateString() : '무제한'}
                      </TableCell>
                      <TableCell>
                        {apiKey.last_used ? new Date(apiKey.last_used).toLocaleString() : '사용 안함'}
                      </TableCell>
                      <TableCell>
                        <Button 
                          variant="outline" 
                          size="sm" 
                          onClick={() => revokeApiKey(apiKey.key_id)}
                          disabled={!apiKey.is_active}
                        >
                          폐기
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="audit-logs" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>감사 로그</CardTitle>
              <CardDescription>플러그인 보안 이벤트 로그를 확인합니다</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>시간</TableHead>
                    <TableHead>플러그인 ID</TableHead>
                    <TableHead>사용자</TableHead>
                    <TableHead>액션</TableHead>
                    <TableHead>리소스</TableHead>
                    <TableHead>IP 주소</TableHead>
                    <TableHead>결과</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {auditLogs.map((log) => (
                    <TableRow key={log.log_id}>
                      <TableCell>{new Date(log.timestamp).toLocaleString()}</TableCell>
                      <TableCell>{log.plugin_id}</TableCell>
                      <TableCell>{log.user_id || 'N/A'}</TableCell>
                      <TableCell>{log.action}</TableCell>
                      <TableCell>{log.resource}</TableCell>
                      <TableCell>{log.ip_address}</TableCell>
                      <TableCell>
                        {log.success ? (
                          <CheckCircle className="h-4 w-4 text-green-600" />
                        ) : (
                          <XCircle className="h-4 w-4 text-red-600" />
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="vulnerabilities" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>취약점 관리</CardTitle>
                  <CardDescription>플러그인 보안 취약점을 스캔하고 관리합니다</CardDescription>
                </div>
                <Dialog open={showVulnerabilityScan} onOpenChange={setShowVulnerabilityScan}>
                  <DialogTrigger asChild>
                    <Button>취약점 스캔</Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>취약점 스캔</DialogTitle>
                      <DialogDescription>플러그인에서 보안 취약점을 스캔합니다</DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div>
                        <Label htmlFor="scan_plugin_id">플러그인 ID</Label>
                        <Input
                          id="scan_plugin_id"
                          value={scanForm.plugin_id}
                          onChange={(e) => setScanForm({...scanForm, plugin_id: e.target.value})}
                          placeholder="plugin_id"
                        />
                      </div>
                    </div>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setShowVulnerabilityScan(false)}>취소</Button>
                      <Button onClick={scanVulnerabilities}>스캔 시작</Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>플러그인 ID</TableHead>
                    <TableHead>심각도</TableHead>
                    <TableHead>제목</TableHead>
                    <TableHead>상태</TableHead>
                    <TableHead>발견일</TableHead>
                    <TableHead>작업</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {vulnerabilities.map((vuln) => (
                    <TableRow key={vuln.report_id}>
                      <TableCell>{vuln.plugin_id}</TableCell>
                      <TableCell>
                        <Badge className={getSeverityColor(vuln.severity)}>
                          {vuln.severity}
                        </Badge>
                      </TableCell>
                      <TableCell>{vuln.title}</TableCell>
                      <TableCell>
                        <Badge className={getStatusColor(vuln.status)}>
                          {vuln.status}
                        </Badge>
                      </TableCell>
                      <TableCell>{new Date(vuln.discovered_at).toLocaleDateString()}</TableCell>
                      <TableCell>
                        <Button variant="outline" size="sm">상세보기</Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
} 
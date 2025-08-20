'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { FileText, Download, RefreshCw, Settings, ExternalLink, AlertTriangle, CheckCircle, FileJson, FileCode, FileType } from 'lucide-react';
import { ApiClient } from '@/lib/api-client';
import { useLoadingState } from '@/hooks/useLoadingState';
import { useErrorHandler } from '@/hooks/useErrorHandler';

const apiClient = new ApiClient();

interface DocsFile {
  name: string;
  size: number;
  modified: string;
  type: string;
}

interface DocsStats {
  endpoint_count: number;
  tag_stats: Record<string, number>;
  file_count: number;
  total_size: number;
  config: {
    title: string;
    version: string;
    output_dir: string;
  };
}

interface DocsConfig {
  title: string;
  version: string;
  description: string;
  contact_name: string;
  contact_email: string;
  server_url: string;
  output_dir: string;
  enable_swagger_ui: boolean;
  enable_redoc: boolean;
  enable_postman: boolean;
  enable_insomnia: boolean;
}

export default function ApiDocsPage() {
  const [files, setFiles] = useState<DocsFile[]>([]);
  const [stats, setStats] = useState<DocsStats | null>(null);
  const [config, setConfig] = useState<DocsConfig | null>(null);
  const [isConfigOpen, setIsConfigOpen] = useState(false);
  const [configForm, setConfigForm] = useState({
    title: '',
    version: '',
    description: '',
    contact_name: '',
    contact_email: '',
    server_url: '',
    enable_swagger_ui: true,
    enable_redoc: true,
    enable_postman: true,
    enable_insomnia: true
  });
  const { isLoading, setLoading } = useLoadingState();
  const { handleError } = useErrorHandler();
  const [error, setError] = useState<string | null>(null);
    useEffect(() => {
    loadFiles();
    loadStats();
    loadConfig();
  }, []);

  const loadFiles = async () => {
    try {
      setError(null);
      const res = await apiClient.get('/api/docs/files') as any;
      setFiles(res.data.files || []);
    } catch (err) {
      handleError(err as Error);
      setError('파일 목록을 불러오는데 실패했습니다.');
    }
  };

  const loadStats = async () => {
    try {
      setError(null);
      const res = await apiClient.get('/api/docs/stats') as any;
      setStats(res.data);
    } catch (err) {
      handleError(err as Error);
      setError('통계를 불러오는데 실패했습니다.');
    }
  };

  const loadConfig = async () => {
    try {
      setError(null);
      const res = await apiClient.get('/api/docs/config') as any;
      setConfig(res.data);
      setConfigForm({
        title: res.data.title,
        version: res.data.version,
        description: res.data.description,
        contact_name: res.data.contact_name,
        contact_email: res.data.contact_email,
        server_url: res.data.server_url,
        enable_swagger_ui: res.data.enable_swagger_ui,
        enable_redoc: res.data.enable_redoc,
        enable_postman: res.data.enable_postman,
        enable_insomnia: res.data.enable_insomnia
      });
    } catch (err) {
      handleError(err as Error);
      setError('설정을 불러오는데 실패했습니다.');
    }
  };

  const generateDocs = async () => {
    try {
      setLoading(true);
      setError(null);
      await apiClient.post('/api/docs/generate');
      await loadFiles();
      await loadStats();
    } catch (err) {
      handleError(err as Error);
      setError('문서 생성에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const downloadFile = async (filename: string) => {
    try {
      const response = await fetch(`/api/docs/files/${filename}`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      handleError(err as Error);
    }
  };

  const updateConfig = async () => {
    try {
      setLoading(true);
      await apiClient.put('/api/docs/config', configForm);
      setIsConfigOpen(false);
      await loadConfig();
    } catch (err) {
      handleError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  const openSwaggerUI = () => {
    window.open('/api/docs/swagger', '_blank');
  };

  const openReDocUI = () => {
    window.open('/api/docs/redoc', '_blank');
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'JSON':
        return <FileJson className="h-4 w-4" />;
      case 'YAML':
        return <FileCode className="h-4 w-4" />;
      case 'Markdown':
        return <FileText className="h-4 w-4" />;
      default:
        return <FileType className="h-4 w-4" />;
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">API 문서 관리</h1>
          <p className="text-gray-600 mt-2">OpenAPI 스펙 생성 및 문서 관리</p>
        </div>
        <div className="flex space-x-2">
          <Button onClick={() => { loadFiles(); loadStats(); loadConfig(); }} disabled={isLoading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            새로고침
          </Button>
          <Button onClick={generateDocs} disabled={isLoading}>
            <FileText className="w-4 h-4 mr-2" />
            문서 생성
          </Button>
        </div>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 엔드포인트</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.endpoint_count || 0}</div>
            <p className="text-xs text-muted-foreground">
              태그: {Object.keys(stats?.tag_stats || {}).length}개
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">생성된 파일</CardTitle>
            <FileCode className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.file_count || 0}</div>
            <p className="text-xs text-muted-foreground">
              크기: {stats ? formatBytes(stats.total_size) : '0 Bytes'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">API 버전</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{config?.version || 'N/A'}</div>
            <p className="text-xs text-muted-foreground">
              {config?.title || 'API 문서'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">문서 UI</CardTitle>
            <ExternalLink className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex space-x-2">
              <Button size="sm" variant="outline" onClick={openSwaggerUI}>
                Swagger
              </Button>
              <Button size="sm" variant="outline" onClick={openReDocUI}>
                ReDoc
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="files" className="space-y-6">
        <TabsList>
          <TabsTrigger value="files">문서 파일</TabsTrigger>
          <TabsTrigger value="stats">통계</TabsTrigger>
          <TabsTrigger value="settings">설정</TabsTrigger>
        </TabsList>

        <TabsContent value="files" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>생성된 문서 파일</CardTitle>
              <CardDescription>OpenAPI 스펙, 마크다운, Postman 컬렉션 등</CardDescription>
            </CardHeader>
            <CardContent>
              {files.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>파일명</TableHead>
                      <TableHead>타입</TableHead>
                      <TableHead>크기</TableHead>
                      <TableHead>수정일</TableHead>
                      <TableHead>작업</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {files.map((file) => (
                      <TableRow key={file.name}>
                        <TableCell className="font-mono">{file.name}</TableCell>
                        <TableCell>
                          <div className="flex items-center space-x-2">
                            {getFileIcon(file.type)}
                            <Badge variant="outline">{file.type}</Badge>
                          </div>
                        </TableCell>
                        <TableCell>{formatBytes(file.size)}</TableCell>
                        <TableCell>
                          {new Date(file.modified).toLocaleString()}
                        </TableCell>
                        <TableCell>
                          <Button size="sm" variant="outline" onClick={() => downloadFile(file.name)}>
                            <Download className="h-4 w-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-8">
                  <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">생성된 문서 파일이 없습니다</p>
                  <Button onClick={generateDocs} className="mt-4">
                    문서 생성하기
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="stats" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>태그별 엔드포인트</CardTitle>
                <CardDescription>API 태그별 엔드포인트 분포</CardDescription>
              </CardHeader>
              <CardContent>
                {stats?.tag_stats ? (
                  <div className="space-y-3">
                    {Object.entries(stats.tag_stats).map(([tag, count]) => (
                      <div key={tag} className="flex items-center justify-between">
                        <span className="font-medium">{tag}</span>
                        <Badge variant="secondary">{count}개</Badge>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground">태그 통계가 없습니다</p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>시스템 정보</CardTitle>
                <CardDescription>API 문서 시스템 정보</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div>
                    <Label className="text-sm font-medium">제목</Label>
                    <p className="text-sm text-muted-foreground">{config?.title}</p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium">버전</Label>
                    <p className="text-sm text-muted-foreground">{config?.version}</p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium">출력 디렉토리</Label>
                    <p className="text-sm text-muted-foreground">{config?.output_dir}</p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium">서버 URL</Label>
                    <p className="text-sm text-muted-foreground">{config?.server_url}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>문서 설정</CardTitle>
                  <CardDescription>API 문서 생성 설정을 관리합니다</CardDescription>
                </div>
                <Dialog open={isConfigOpen} onOpenChange={setIsConfigOpen}>
                  <DialogTrigger asChild>
                    <Button>
                      <Settings className="w-4 h-4 mr-2" />
                      설정 편집
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-[600px]">
                    <DialogHeader>
                      <DialogTitle>API 문서 설정</DialogTitle>
                      <DialogDescription>문서 생성 설정을 수정합니다</DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="title">제목</Label>
                          <Input
                            id="title"
                            value={configForm.title}
                            onChange={(e) => setConfigForm({ ...configForm, title: e.target.value })}
                          />
                        </div>
                        <div>
                          <Label htmlFor="version">버전</Label>
                          <Input
                            id="version"
                            value={configForm.version}
                            onChange={(e) => setConfigForm({ ...configForm, version: e.target.value })}
                          />
                        </div>
                      </div>
                      <div>
                        <Label htmlFor="description">설명</Label>
                        <Textarea
                          id="description"
                          value={configForm.description}
                          onChange={(e) => setConfigForm({ ...configForm, description: e.target.value })}
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="contact_name">연락처 이름</Label>
                          <Input
                            id="contact_name"
                            value={configForm.contact_name}
                            onChange={(e) => setConfigForm({ ...configForm, contact_name: e.target.value })}
                          />
                        </div>
                        <div>
                          <Label htmlFor="contact_email">연락처 이메일</Label>
                          <Input
                            id="contact_email"
                            value={configForm.contact_email}
                            onChange={(e) => setConfigForm({ ...configForm, contact_email: e.target.value })}
                          />
                        </div>
                      </div>
                      <div>
                        <Label htmlFor="server_url">서버 URL</Label>
                        <Input
                          id="server_url"
                          value={configForm.server_url}
                          onChange={(e) => setConfigForm({ ...configForm, server_url: e.target.value })}
                        />
                      </div>
                      <div>
                        <Label>문서 타입 활성화</Label>
                        <div className="grid grid-cols-2 gap-4 mt-2">
                          <div className="flex items-center space-x-2">
                            <input
                              type="checkbox"
                              id="swagger_ui"
                              checked={configForm.enable_swagger_ui}
                              onChange={(e) => setConfigForm({ ...configForm, enable_swagger_ui: e.target.checked })}
                            />
                            <Label htmlFor="swagger_ui">Swagger UI</Label>
                          </div>
                          <div className="flex items-center space-x-2">
                            <input
                              type="checkbox"
                              id="redoc"
                              checked={configForm.enable_redoc}
                              onChange={(e) => setConfigForm({ ...configForm, enable_redoc: e.target.checked })}
                            />
                            <Label htmlFor="redoc">ReDoc</Label>
                          </div>
                          <div className="flex items-center space-x-2">
                            <input
                              type="checkbox"
                              id="postman"
                              checked={configForm.enable_postman}
                              onChange={(e) => setConfigForm({ ...configForm, enable_postman: e.target.checked })}
                            />
                            <Label htmlFor="postman">Postman</Label>
                          </div>
                          <div className="flex items-center space-x-2">
                            <input
                              type="checkbox"
                              id="insomnia"
                              checked={configForm.enable_insomnia}
                              onChange={(e) => setConfigForm({ ...configForm, enable_insomnia: e.target.checked })}
                            />
                            <Label htmlFor="insomnia">Insomnia</Label>
                          </div>
                        </div>
                      </div>
                    </div>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setIsConfigOpen(false)}>
                        취소
                      </Button>
                      <Button onClick={updateConfig} disabled={isLoading}>
                        저장
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <Label className="text-sm font-medium">제목</Label>
                    <p className="text-sm text-muted-foreground">{config?.title}</p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium">버전</Label>
                    <p className="text-sm text-muted-foreground">{config?.version}</p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium">설명</Label>
                    <p className="text-sm text-muted-foreground">{config?.description}</p>
                  </div>
                </div>
                <div className="space-y-4">
                  <div>
                    <Label className="text-sm font-medium">연락처</Label>
                    <p className="text-sm text-muted-foreground">
                      {config?.contact_name} ({config?.contact_email})
                    </p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium">서버 URL</Label>
                    <p className="text-sm text-muted-foreground">{config?.server_url}</p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium">활성화된 문서 타입</Label>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {config?.enable_swagger_ui && <Badge variant="secondary">Swagger UI</Badge>}
                      {config?.enable_redoc && <Badge variant="secondary">ReDoc</Badge>}
                      {config?.enable_postman && <Badge variant="secondary">Postman</Badge>}
                      {config?.enable_insomnia && <Badge variant="secondary">Insomnia</Badge>}
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
} 
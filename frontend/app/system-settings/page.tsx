'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { 
  Settings, 
  Save, 
  Download, 
  History, 
  Database, 
  Shield, 
  FileText, 
  Mail, 
  Activity,
  CheckCircle,
  Edit,
  Plus,
  RefreshCw,
  Copy,
  FileDown
} from 'lucide-react';
// import { useLoadingState } from '@/hooks/useLoadingState';
import { useErrorHandler } from '@/hooks/useErrorHandler';
import { apiClient } from '@/lib/api-client';

interface SettingItem {
  key: string;
  value: any;
  category: string;
  description: string;
  data_type: string;
  is_sensitive: boolean;
  is_required: boolean;
  default_value: any;
  created_at?: string;
  updated_at?: string;
}

interface SettingsStats {
  total_settings: number;
  sensitive_settings: number;
  required_settings: number;
  categories: number;
  backups: number;
  changes_today: number;
  category_stats: Record<string, number>;
}

interface SettingsChange {
  change_id: string;
  setting_key: string;
  old_value: any;
  new_value: any;
  changed_by: string;
  change_reason: string;
  timestamp: string;
  category: string;
}

export default function SystemSettingsPage() {
  const [isLoading, setIsLoading] = useState(false);
  const { handleError } = useErrorHandler();
  
  // 상태 관리
  const [stats, setStats] = useState<SettingsStats | null>(null);
  const [settings, setSettings] = useState<SettingItem[]>([]);
  const [changes, setChanges] = useState<SettingsChange[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showSensitive, setShowSensitive] = useState(false);
  
  // 다이얼로그 상태
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [editForm, setEditForm] = useState<{ key: string; value: any; reason: string }>({
    key: '',
    value: '',
    reason: ''
  });

  // 데이터 로드 함수들
  const loadStats = useCallback(async () => {
    try {
      const response = await apiClient.get('/api/settings/stats');
      setStats(response.data);
    } catch (error) {
      handleError(error, '설정 통계 로드 실패');
    }
  }, [handleError]);

  const loadSettings = useCallback(async () => {
    try {
      const response = await apiClient.get('/api/settings/settings');
      setSettings(response.data);
    } catch (error) {
      handleError(error, '설정 목록 로드 실패');
    }
  }, [handleError]);

  const loadChanges = useCallback(async () => {
    try {
      const response = await apiClient.get('/api/settings/changes?limit=50');
      setChanges(response.data);
    } catch (error) {
      handleError(error, '변경 이력 로드 실패');
    }
  }, [handleError]);

  // 초기 데이터 로드
  useEffect(() => {
    const loadAllData = async () => {
      setIsLoading(true);
      try {
        await Promise.all([
          loadStats(),
          loadSettings(),
          loadChanges()
        ]);
      } catch (error) {
        handleError(error, '데이터 로드 실패');
      } finally {
        setIsLoading(false);
      }
    };
    
    loadAllData();
  }, [loadStats, loadSettings, loadChanges, handleError]);

  // 필터링된 설정
  const filteredSettings = settings.filter(setting => {
    const matchesCategory = selectedCategory === 'all' || setting.category === selectedCategory;
    const matchesSearch = setting.key.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         setting.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesSensitive = showSensitive || !setting.is_sensitive;
    
    return matchesCategory && matchesSearch && matchesSensitive;
  });

  // 이벤트 핸들러들
  const handleEditSetting = (setting: SettingItem) => {
    setEditForm({
      key: setting.key,
      value: setting.value,
      reason: ''
    });
    setShowEditDialog(true);
  };

  const handleSaveSetting = async () => {
    try {
      await apiClient.put(`/api/settings/settings/${editForm.key}`, {
        value: editForm.value,
        changed_by: 'admin',
        change_reason: editForm.reason
      });
      
      setShowEditDialog(false);
      await loadSettings();
      await loadChanges();
      await loadStats();
    } catch (error) {
      handleError(error, '설정 저장 실패');
    }
  };

  const handleExportSettings = async (format: 'json' | 'yaml') => {
    try {
      const response = await apiClient.get(`/api/settings/export?format=${format}`);
      const content = response.data.content;
      
      // 파일 다운로드
      const blob = new Blob([content], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `settings.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      handleError(error, '설정 내보내기 실패');
    }
  };

  // 유틸리티 함수들
  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'system': return <Settings className="w-4 h-4" />;
      case 'database': return <Database className="w-4 h-4" />;
      case 'api': return <Activity className="w-4 h-4" />;
      case 'security': return <Shield className="w-4 h-4" />;
      case 'logging': return <FileText className="w-4 h-4" />;
      case 'email': return <Mail className="w-4 h-4" />;
      default: return <Settings className="w-4 h-4" />;
    }
  };

  const formatValue = (value: any, isSensitive: boolean) => {
    if (isSensitive && !showSensitive) {
      return '***';
    }
    
    if (typeof value === 'boolean') {
      return value ? '활성' : '비활성';
    }
    
    if (Array.isArray(value)) {
      return JSON.stringify(value);
    }
    
    if (typeof value === 'object') {
      return JSON.stringify(value);
    }
    
    return String(value);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">시스템 설정 관리</h1>
          <p className="text-gray-600 mt-2">애플리케이션 설정을 중앙에서 관리하고 모니터링합니다</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => handleExportSettings('json')}>
            <Download className="w-4 h-4 mr-2" />
            내보내기
          </Button>
        </div>
      </div>

      {/* 통계 카드 */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">총 설정</CardTitle>
              <Settings className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_settings}</div>
              <p className="text-xs text-muted-foreground">
                {stats.categories}개 카테고리
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">민감한 설정</CardTitle>
              <Shield className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.sensitive_settings}</div>
              <p className="text-xs text-muted-foreground">
                암호화된 정보
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">필수 설정</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.required_settings}</div>
              <p className="text-xs text-muted-foreground">
                시스템 필수 항목
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">오늘 변경</CardTitle>
              <History className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.changes_today}</div>
              <p className="text-xs text-muted-foreground">
                설정 변경 횟수
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 메인 콘텐츠 */}
      <Tabs defaultValue="settings" className="space-y-4">
        <TabsList>
          <TabsTrigger value="settings">설정 관리</TabsTrigger>
          <TabsTrigger value="changes">변경 이력</TabsTrigger>
        </TabsList>

        {/* 설정 관리 탭 */}
        <TabsContent value="settings" className="space-y-4">
          {/* 필터 및 검색 */}
          <Card>
            <CardHeader>
              <CardTitle>설정 필터</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                  <Label htmlFor="search">검색</Label>
                  <Input
                    id="search"
                    placeholder="설정 키 또는 설명으로 검색..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>
                <div className="w-full sm:w-48">
                  <Label htmlFor="category">카테고리</Label>
                  <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">모든 카테고리</SelectItem>
                      <SelectItem value="system">시스템</SelectItem>
                      <SelectItem value="database">데이터베이스</SelectItem>
                      <SelectItem value="api">API</SelectItem>
                      <SelectItem value="security">보안</SelectItem>
                      <SelectItem value="logging">로깅</SelectItem>
                      <SelectItem value="email">이메일</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="show-sensitive"
                    checked={showSensitive}
                    onCheckedChange={setShowSensitive}
                  />
                  <Label htmlFor="show-sensitive">민감한 정보 표시</Label>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 설정 목록 */}
          <Card>
            <CardHeader>
              <CardTitle>설정 목록</CardTitle>
              <CardDescription>
                총 {filteredSettings.length}개의 설정 항목
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {filteredSettings.map((setting) => (
                  <div key={setting.key} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        {getCategoryIcon(setting.category)}
                        <span className="font-medium">{setting.key}</span>
                        {setting.is_sensitive && (
                          <Badge variant="secondary">
                            <Shield className="w-3 h-3 mr-1" />
                            민감
                          </Badge>
                        )}
                        {setting.is_required && (
                          <Badge variant="destructive">
                            <CheckCircle className="w-3 h-3 mr-1" />
                            필수
                          </Badge>
                        )}
                        <Badge variant="outline">{setting.category}</Badge>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{setting.description}</p>
                      <div className="flex items-center gap-4 text-sm text-gray-500">
                        <span>타입: {setting.data_type}</span>
                        {setting.updated_at && (
                          <span>수정: {new Date(setting.updated_at).toLocaleString()}</span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="text-right">
                        <div className="font-medium">
                          {formatValue(setting.value, setting.is_sensitive)}
                        </div>
                        {setting.default_value !== null && (
                          <div className="text-sm text-gray-500">
                            기본값: {formatValue(setting.default_value, false)}
                          </div>
                        )}
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleEditSetting(setting)}
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 변경 이력 탭 */}
        <TabsContent value="changes" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>설정 변경 이력</CardTitle>
              <CardDescription>
                최근 50개의 설정 변경 내역
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {changes.map((change) => (
                  <div key={change.change_id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="font-medium">{change.setting_key}</span>
                        <Badge variant="outline">{change.category}</Badge>
                      </div>
                      <div className="text-sm text-gray-600 mb-2">
                        <div>이전 값: {formatValue(change.old_value, false)}</div>
                        <div>새 값: {formatValue(change.new_value, false)}</div>
                      </div>
                      <div className="flex items-center gap-4 text-sm text-gray-500">
                        <span>변경자: {change.changed_by}</span>
                        <span>시간: {new Date(change.timestamp).toLocaleString()}</span>
                      </div>
                      {change.change_reason && (
                        <div className="text-sm text-gray-500 mt-1">
                          사유: {change.change_reason}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* 설정 편집 다이얼로그 */}
      <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>설정 편집</DialogTitle>
            <DialogDescription>
              설정 값을 변경합니다
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>설정 키</Label>
              <Input value={editForm.key} disabled />
            </div>
            <div>
              <Label>값</Label>
              <Input
                value={editForm.value}
                onChange={(e) => setEditForm({ ...editForm, value: e.target.value })}
              />
            </div>
            <div>
              <Label>변경 사유 (선택사항)</Label>
              <Textarea
                value={editForm.reason}
                onChange={(e) => setEditForm({ ...editForm, reason: e.target.value })}
                placeholder="변경 사유를 입력하세요..."
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowEditDialog(false)}>
              취소
            </Button>
            <Button onClick={handleSaveSetting}>
              저장
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
} 
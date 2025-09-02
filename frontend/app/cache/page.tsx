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
import { Database, RefreshCw, Trash2, Plus, Search, Settings, AlertTriangle, CheckCircle, Clock, Zap } from 'lucide-react';
import { ApiClient } from '@/lib/api-client';
import { useLoadingState } from '@/hooks/useLoadingState';
import { useErrorHandler } from '@/hooks/useErrorHandler';

const apiClient = new ApiClient();

interface CacheItem {
  key: string;
  value: any;
  ttl: number;
  created_at: string;
  accessed_at: string;
  access_count: number;
  size: number;
}

interface CacheStats {
  total_items: number;
  total_size: number;
  hit_rate: number;
  miss_rate: number;
  evicted_items: number;
  memory_usage: number;
  max_memory: number;
  cache_types: {
    redis: number;
    memory: number;
    file: number;
  };
}

interface CacheConfig {
  max_size: number;
  default_ttl: number;
  enable_compression: boolean;
  enable_persistence: boolean;
  cache_strategy: string;
}

export default function CachePage() {
  const [cacheItems, setCacheItems] = useState<CacheItem[]>([]);
  const [stats, setStats] = useState<CacheStats | null>(null);
  const [config, setConfig] = useState<CacheConfig | null>(null);
  const [searchKey, setSearchKey] = useState('');
  const [isAddItemOpen, setIsAddItemOpen] = useState(false);
  const [isConfigOpen, setIsConfigOpen] = useState(false);
  const [newItem, setNewItem] = useState({ key: '', value: '', ttl: 3600 });
  const [configForm, setConfigForm] = useState({
    max_size: 1000,
    default_ttl: 3600,
    enable_compression: true,
    enable_persistence: true,
    cache_strategy: 'lru'
  });
  const { isLoading, setLoading } = useLoadingState();
  const { handleError } = useErrorHandler();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadCacheItems();
    loadStats();
    loadConfig();
  }, []);

  const loadCacheItems = async () => {
    try {
      setError(null);
      const res = await apiClient.get('/api/cache/items') as any;
      setCacheItems(res.data.items || []);
    } catch (err) {
      handleError(err as Error);
      setError('캐시 항목을 불러오는데 실패했습니다.');
    }
  };

  const loadStats = async () => {
    try {
      setError(null);
      const res = await apiClient.get('/api/cache/stats') as any;
      setStats(res.data);
    } catch (err) {
      handleError(err as Error);
      setError('통계를 불러오는데 실패했습니다.');
    }
  };

  const loadConfig = async () => {
    try {
      setError(null);
      const res = await apiClient.get('/api/cache/config') as any;
      setConfig(res.data);
      setConfigForm({
        max_size: res.data.max_size,
        default_ttl: res.data.default_ttl,
        enable_compression: res.data.enable_compression,
        enable_persistence: res.data.enable_persistence,
        cache_strategy: res.data.cache_strategy
      });
    } catch (err) {
      handleError(err as Error);
      setError('설정을 불러오는데 실패했습니다.');
    }
  };

  const addCacheItem = async () => {
    try {
      setLoading(true);
      setError(null);
      await apiClient.post('/api/cache/items', {
        key: newItem.key,
        value: newItem.value,
        ttl: newItem.ttl
      });
      setIsAddItemOpen(false);
      setNewItem({ key: '', value: '', ttl: 3600 });
      await loadCacheItems();
      await loadStats();
    } catch (err) {
      handleError(err as Error);
      setError('캐시 항목 추가에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const deleteCacheItem = async (key: string) => {
    if (!confirm('정말로 이 캐시 항목을 삭제하시겠습니까?')) return;
    try {
      setLoading(true);
      setError(null);
      await apiClient.delete(`/api/cache/items/${encodeURIComponent(key)}`);
      await loadCacheItems();
      await loadStats();
    } catch (err) {
      handleError(err as Error);
      setError('캐시 항목 삭제에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const clearCache = async () => {
    if (!confirm('정말로 모든 캐시를 삭제하시겠습니까?')) return;
    try {
      setLoading(true);
      setError(null);
      await apiClient.delete('/api/cache/clear');
      await loadCacheItems();
      await loadStats();
    } catch (err) {
      handleError(err as Error);
      setError('캐시 삭제에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const updateConfig = async () => {
    try {
      setLoading(true);
      setError(null);
      await apiClient.put('/api/cache/config', configForm);
      setIsConfigOpen(false);
      await loadConfig();
    } catch (err) {
      handleError(err as Error);
      setError('설정 업데이트에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const searchCache = async () => {
    if (!searchKey.trim()) {
      await loadCacheItems();
      return;
    }
    try {
      setError(null);
      const res = await apiClient.get(`/api/cache/search?q=${encodeURIComponent(searchKey)}`) as any;
      setCacheItems(res.data.items || []);
    } catch (err) {
      handleError(err as Error);
      setError('캐시 검색에 실패했습니다.');
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatTTL = (ttl: number) => {
    if (ttl === -1) return '무제한';
    const hours = Math.floor(ttl / 3600);
    const minutes = Math.floor((ttl % 3600) / 60);
    const seconds = ttl % 60;
    return `${hours}h ${minutes}m ${seconds}s`;
  };

  const filteredItems = cacheItems.filter(item => 
    searchKey === '' || item.key.toLowerCase().includes(searchKey.toLowerCase())
  );

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">캐시 관리</h1>
          <p className="text-gray-600 mt-2">Redis, 메모리, 파일 캐시를 관리합니다</p>
        </div>
        <div className="flex space-x-2">
          <Button onClick={() => { loadCacheItems(); loadStats(); loadConfig(); }} disabled={isLoading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            새로고침
          </Button>
          <Button variant="outline" onClick={clearCache} disabled={isLoading}>
            <Trash2 className="w-4 h-4 mr-2" />
            전체 삭제
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
            <CardTitle className="text-sm font-medium">총 항목</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_items || 0}</div>
            <p className="text-xs text-muted-foreground">
              크기: {stats ? formatBytes(stats.total_size) : '0 Bytes'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">히트율</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.hit_rate?.toFixed(1) || 0}%</div>
            <p className="text-xs text-muted-foreground">
              미스율: {stats?.miss_rate?.toFixed(1) || 0}%
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">메모리 사용량</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats ? formatBytes(stats.memory_usage) : '0 Bytes'}
            </div>
            <p className="text-xs text-muted-foreground">
              최대: {stats ? formatBytes(stats.max_memory) : '0 Bytes'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">제거된 항목</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.evicted_items || 0}</div>
            <p className="text-xs text-muted-foreground">TTL 만료</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="items" className="space-y-6">
        <TabsList>
          <TabsTrigger value="items">캐시 항목</TabsTrigger>
          <TabsTrigger value="stats">통계</TabsTrigger>
          <TabsTrigger value="settings">설정</TabsTrigger>
        </TabsList>

        <TabsContent value="items" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>캐시 항목</CardTitle>
                  <CardDescription>캐시된 데이터를 관리합니다</CardDescription>
                </div>
                <Dialog open={isAddItemOpen} onOpenChange={setIsAddItemOpen}>
                  <DialogTrigger asChild>
                    <Button>
                      <Plus className="w-4 h-4 mr-2" />
                      항목 추가
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-[500px]">
                    <DialogHeader>
                      <DialogTitle>캐시 항목 추가</DialogTitle>
                      <DialogDescription>새로운 캐시 항목을 추가합니다</DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                      <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="key" className="text-right">키</Label>
                        <Input
                          id="key"
                          value={newItem.key}
                          onChange={(e) => setNewItem({ ...newItem, key: e.target.value })}
                          className="col-span-3"
                        />
                      </div>
                      <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="value" className="text-right">값</Label>
                        <Textarea
                          id="value"
                          value={newItem.value}
                          onChange={(e) => setNewItem({ ...newItem, value: e.target.value })}
                          className="col-span-3"
                        />
                      </div>
                      <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="ttl" className="text-right">TTL (초)</Label>
                        <Input
                          id="ttl"
                          type="number"
                          value={newItem.ttl}
                          onChange={(e) => setNewItem({ ...newItem, ttl: parseInt(e.target.value) })}
                          className="col-span-3"
                        />
                      </div>
                    </div>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setIsAddItemOpen(false)}>
                        취소
                      </Button>
                      <Button onClick={addCacheItem} disabled={isLoading}>
                        추가
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex space-x-2 mb-4">
                <Input
                  placeholder="키로 검색..."
                  value={searchKey}
                  onChange={(e) => setSearchKey(e.target.value)}
                  className="flex-1"
                />
                <Button onClick={searchCache} disabled={isLoading}>
                  <Search className="w-4 h-4" />
                </Button>
              </div>
              
              {filteredItems.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>키</TableHead>
                      <TableHead>값</TableHead>
                      <TableHead>TTL</TableHead>
                      <TableHead>크기</TableHead>
                      <TableHead>접근 횟수</TableHead>
                      <TableHead>생성일</TableHead>
                      <TableHead>작업</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredItems.map((item) => (
                      <TableRow key={item.key}>
                        <TableCell className="font-mono">{item.key}</TableCell>
                        <TableCell className="max-w-xs truncate">
                          {typeof item.value === 'string' ? item.value : JSON.stringify(item.value)}
                        </TableCell>
                        <TableCell>{formatTTL(item.ttl)}</TableCell>
                        <TableCell>{formatBytes(item.size)}</TableCell>
                        <TableCell>{item.access_count}</TableCell>
                        <TableCell>
                          {new Date(item.created_at).toLocaleString()}
                        </TableCell>
                        <TableCell>
                          <Button 
                            size="sm" 
                            variant="outline" 
                            onClick={() => deleteCacheItem(item.key)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-8">
                  <Database className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">
                    {searchKey ? '검색 결과가 없습니다' : '캐시 항목이 없습니다'}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="stats" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>캐시 타입별 통계</CardTitle>
                <CardDescription>각 캐시 타입의 사용 현황</CardDescription>
              </CardHeader>
              <CardContent>
                {stats?.cache_types ? (
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">Redis</span>
                      <Badge variant="secondary">{stats.cache_types.redis}개</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="font-medium">메모리</span>
                      <Badge variant="secondary">{stats.cache_types.memory}개</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="font-medium">파일</span>
                      <Badge variant="secondary">{stats.cache_types.file}개</Badge>
                    </div>
                  </div>
                ) : (
                  <p className="text-muted-foreground">캐시 타입 통계가 없습니다</p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>성능 지표</CardTitle>
                <CardDescription>캐시 성능 통계</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div>
                    <Label className="text-sm font-medium">히트율</Label>
                    <p className="text-sm text-muted-foreground">{stats?.hit_rate?.toFixed(1) || 0}%</p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium">미스율</Label>
                    <p className="text-sm text-muted-foreground">{stats?.miss_rate?.toFixed(1) || 0}%</p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium">제거된 항목</Label>
                    <p className="text-sm text-muted-foreground">{stats?.evicted_items || 0}개</p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium">메모리 사용률</Label>
                    <p className="text-sm text-muted-foreground">
                      {stats ? ((stats.memory_usage / stats.max_memory) * 100).toFixed(1) : 0}%
                    </p>
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
                  <CardTitle>캐시 설정</CardTitle>
                  <CardDescription>캐시 시스템 설정을 관리합니다</CardDescription>
                </div>
                <Dialog open={isConfigOpen} onOpenChange={setIsConfigOpen}>
                  <DialogTrigger asChild>
                    <Button>
                      <Settings className="w-4 h-4 mr-2" />
                      설정 편집
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-[500px]">
                    <DialogHeader>
                      <DialogTitle>캐시 설정</DialogTitle>
                      <DialogDescription>캐시 시스템 설정을 수정합니다</DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                      <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="max_size" className="text-right">최대 크기</Label>
                        <Input
                          id="max_size"
                          type="number"
                          value={configForm.max_size}
                          onChange={(e) => setConfigForm({ ...configForm, max_size: parseInt(e.target.value) })}
                          className="col-span-3"
                        />
                      </div>
                      <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="default_ttl" className="text-right">기본 TTL (초)</Label>
                        <Input
                          id="default_ttl"
                          type="number"
                          value={configForm.default_ttl}
                          onChange={(e) => setConfigForm({ ...configForm, default_ttl: parseInt(e.target.value) })}
                          className="col-span-3"
                        />
                      </div>
                      <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="cache_strategy" className="text-right">캐시 전략</Label>
                        <Select
                          value={configForm.cache_strategy}
                          onValueChange={(value) => setConfigForm({ ...configForm, cache_strategy: value })}
                        >
                          <SelectTrigger className="col-span-3">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="lru">LRU (Least Recently Used)</SelectItem>
                            <SelectItem value="lfu">LFU (Least Frequently Used)</SelectItem>
                            <SelectItem value="fifo">FIFO (First In First Out)</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="grid grid-cols-4 items-center gap-4">
                        <Label className="text-right">옵션</Label>
                        <div className="col-span-3 space-y-2">
                          <div className="flex items-center space-x-2">
                            <input
                              type="checkbox"
                              id="compression"
                              checked={configForm.enable_compression}
                              onChange={(e) => setConfigForm({ ...configForm, enable_compression: e.target.checked })}
                            />
                            <Label htmlFor="compression">압축 활성화</Label>
                          </div>
                          <div className="flex items-center space-x-2">
                            <input
                              type="checkbox"
                              id="persistence"
                              checked={configForm.enable_persistence}
                              onChange={(e) => setConfigForm({ ...configForm, enable_persistence: e.target.checked })}
                            />
                            <Label htmlFor="persistence">영속성 활성화</Label>
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
                    <Label className="text-sm font-medium">최대 크기</Label>
                    <p className="text-sm text-muted-foreground">{config?.max_size}개</p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium">기본 TTL</Label>
                    <p className="text-sm text-muted-foreground">{config?.default_ttl}초</p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium">캐시 전략</Label>
                    <p className="text-sm text-muted-foreground">{config?.cache_strategy?.toUpperCase()}</p>
                  </div>
                </div>
                <div className="space-y-4">
                  <div>
                    <Label className="text-sm font-medium">압축</Label>
                    <p className="text-sm text-muted-foreground">
                      {config?.enable_compression ? '활성화' : '비활성화'}
                    </p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium">영속성</Label>
                    <p className="text-sm text-muted-foreground">
                      {config?.enable_persistence ? '활성화' : '비활성화'}
                    </p>
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
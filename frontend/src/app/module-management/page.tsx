'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Settings, 
  Power, 
  PowerOff, 
  Trash2, 
  Download, 
  Star, 
  Activity,
  BarChart3,
  Clock,
  AlertCircle
} from 'lucide-react';
import { toast } from 'sonner';

interface InstalledModule {
  id: string;
  name: string;
  description: string;
  category: string;
  version: string;
  author: string;
  price: number;
  rating: number;
  downloads: number;
  tags: string[];
  features: string[];
  installed_at: string;
  is_active: boolean;
  settings: any;
}

interface ModuleStatistics {
  total_installed: number;
  active_modules: number;
  inactive_modules: number;
  total_downloads: number;
  average_rating: number;
}

export default function ModuleManagementPage() {
  const [installedModules, setInstalledModules] = useState<InstalledModule[]>([]);
  const [statistics, setStatistics] = useState<ModuleStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedModule, setSelectedModule] = useState<string | null>(null);

  // 설치된 모듈 목록 조회
  const fetchInstalledModules = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/module-marketplace/modules/installed');
      const data = await response.json();

      if (data.success) {
        setInstalledModules(data.modules);
      } else {
        toast.error('설치된 모듈 목록을 불러오는데 실패했습니다.');
      }
    } catch (error) {
      console.error('설치된 모듈 목록 조회 실패:', error);
      toast.error('설치된 모듈 목록을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 모듈 통계 조회
  const fetchModuleStatistics = async () => {
    try {
      const response = await fetch('/api/module-marketplace/modules/statistics');
      const data = await response.json();

      if (data.success) {
        setStatistics(data.data);
      } else {
        console.error('모듈 통계 조회 실패:', data.error);
      }
    } catch (error) {
      console.error('모듈 통계 조회 실패:', error);
    }
  };

  // 모듈 활성화/비활성화
  const toggleModuleStatus = async (moduleId: string, isActive: boolean) => {
    try {
      const endpoint = isActive ? 'deactivate' : 'activate';
      const response = await fetch(`/api/module-marketplace/modules/${moduleId}/${endpoint}`, {
        method: 'POST',
      });
      const data = await response.json();

      if (data.success) {
        toast.success(data.message);
        fetchInstalledModules(); // 목록 새로고침
        fetchModuleStatistics(); // 통계 새로고침
      } else {
        toast.error(data.error || '모듈 상태 변경에 실패했습니다.');
      }
    } catch (error) {
      console.error('모듈 상태 변경 실패:', error);
      toast.error('모듈 상태 변경에 실패했습니다.');
    }
  };

  // 모듈 제거
  const uninstallModule = async (moduleId: string, moduleName: string) => {
    if (!confirm(`정말로 "${moduleName}" 모듈을 제거하시겠습니까?`)) {
      return;
    }

    try {
      const response = await fetch(`/api/module-marketplace/modules/${moduleId}/uninstall`, {
        method: 'POST',
      });
      const data = await response.json();

      if (data.success) {
        toast.success(data.message);
        fetchInstalledModules(); // 목록 새로고침
        fetchModuleStatistics(); // 통계 새로고침
      } else {
        toast.error(data.error || '모듈 제거에 실패했습니다.');
      }
    } catch (error) {
      console.error('모듈 제거 실패:', error);
      toast.error('모듈 제거에 실패했습니다.');
    }
  };

  // 모듈 업데이트
  const updateModule = async (moduleId: string, moduleName: string) => {
    try {
      const response = await fetch(`/api/module-marketplace/modules/${moduleId}/update`, {
        method: 'POST',
      });
      const data = await response.json();

      if (data.success) {
        toast.success(data.message);
        fetchInstalledModules(); // 목록 새로고침
      } else {
        toast.error(data.error || '모듈 업데이트에 실패했습니다.');
      }
    } catch (error) {
      console.error('모듈 업데이트 실패:', error);
      toast.error('모듈 업데이트에 실패했습니다.');
    }
  };

  useEffect(() => {
    fetchInstalledModules();
    fetchModuleStatistics();
  }, []);

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`w-4 h-4 ${
          i < Math.floor(rating) ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
        }`}
      />
    ));
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const activeModules = installedModules.filter(module => module.is_active);
  const inactiveModules = installedModules.filter(module => !module.is_active);

  return (
    <div className="container mx-auto px-4 py-8">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">모듈 관리</h1>
        <p className="text-gray-600">
          설치된 모듈을 관리하고 설정을 변경하세요
        </p>
      </div>

      {/* 통계 카드 */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">총 설치</p>
                  <p className="text-2xl font-bold">{statistics.total_installed}</p>
                </div>
                <Download className="w-8 h-8 text-blue-500" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">활성화</p>
                  <p className="text-2xl font-bold text-green-600">{statistics.active_modules}</p>
                </div>
                <Power className="w-8 h-8 text-green-500" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">비활성화</p>
                  <p className="text-2xl font-bold text-gray-600">{statistics.inactive_modules}</p>
                </div>
                <PowerOff className="w-8 h-8 text-gray-500" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">총 다운로드</p>
                  <p className="text-2xl font-bold">{statistics.total_downloads.toLocaleString()}</p>
                </div>
                <BarChart3 className="w-8 h-8 text-purple-500" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">평균 평점</p>
                  <p className="text-2xl font-bold">{statistics.average_rating.toFixed(1)}</p>
                </div>
                <Star className="w-8 h-8 text-yellow-500" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      <Tabs defaultValue="all" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="all">전체 모듈</TabsTrigger>
          <TabsTrigger value="active">활성화된 모듈</TabsTrigger>
          <TabsTrigger value="inactive">비활성화된 모듈</TabsTrigger>
        </TabsList>

        {/* 전체 모듈 탭 */}
        <TabsContent value="all" className="space-y-6">
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {Array.from({ length: 6 }).map((_, i) => (
                <Card key={i} className="animate-pulse">
                  <CardHeader>
                    <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                  </CardHeader>
                  <CardContent>
                    <div className="h-20 bg-gray-200 rounded mb-4"></div>
                    <div className="space-y-2">
                      <div className="h-3 bg-gray-200 rounded"></div>
                      <div className="h-3 bg-gray-200 rounded w-2/3"></div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : installedModules.length === 0 ? (
            <div className="text-center py-12">
              <Settings className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-medium text-gray-900 mb-2">
                설치된 모듈이 없습니다
              </h3>
              <p className="text-gray-600 mb-6">
                마켓플레이스에서 원하는 모듈을 설치해보세요
              </p>
              <Button onClick={() => window.location.href = '/marketplace'}>
                마켓플레이스로 이동
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {installedModules.map((module) => (
                <Card key={module.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex justify-between items-start mb-2">
                      <CardTitle className="text-lg">{module.name}</CardTitle>
                      <Badge variant={module.is_active ? 'default' : 'secondary'}>
                        {module.is_active ? '활성' : '비활성'}
                      </Badge>
                    </div>
                    <CardDescription className="line-clamp-2">
                      {module.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {/* 모듈 정보 */}
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-600">버전:</span>
                          <span className="font-medium">{module.version}</span>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-600">설치일:</span>
                          <span className="font-medium">{formatDate(module.installed_at)}</span>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-600">평점:</span>
                          <div className="flex items-center">
                            {renderStars(module.rating)}
                            <span className="ml-1">{module.rating.toFixed(1)}</span>
                          </div>
                        </div>
                      </div>

                      {/* 태그 */}
                      <div className="flex flex-wrap gap-1">
                        {module.tags.slice(0, 3).map((tag) => (
                          <Badge key={tag} variant="outline" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                      </div>

                      {/* 액션 버튼 */}
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-600">활성화</span>
                          <Switch
                            checked={module.is_active}
                            onCheckedChange={(checked) => toggleModuleStatus(module.id, !checked)}
                          />
                        </div>
                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setSelectedModule(module.id)}
                            className="flex-1"
                          >
                            <Settings className="w-4 h-4 mr-1" />
                            설정
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => updateModule(module.id, module.name)}
                          >
                            <Activity className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => uninstallModule(module.id, module.name)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        {/* 활성화된 모듈 탭 */}
        <TabsContent value="active" className="space-y-6">
          {activeModules.length === 0 ? (
            <div className="text-center py-12">
              <Power className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-medium text-gray-900 mb-2">
                활성화된 모듈이 없습니다
              </h3>
              <p className="text-gray-600">
                모듈을 활성화하여 사용을 시작하세요
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {activeModules.map((module) => (
                <Card key={module.id} className="border-green-200 bg-green-50/30">
                  <CardHeader>
                    <div className="flex justify-between items-start mb-2">
                      <CardTitle className="text-lg">{module.name}</CardTitle>
                      <Badge variant="default" className="bg-green-600">
                        활성
                      </Badge>
                    </div>
                    <CardDescription className="line-clamp-2">
                      {module.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-600">버전:</span>
                          <span className="font-medium">{module.version}</span>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-600">설치일:</span>
                          <span className="font-medium">{formatDate(module.installed_at)}</span>
                        </div>
                      </div>

                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setSelectedModule(module.id)}
                          className="flex-1"
                        >
                          <Settings className="w-4 h-4 mr-1" />
                          설정
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => toggleModuleStatus(module.id, true)}
                        >
                          <PowerOff className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        {/* 비활성화된 모듈 탭 */}
        <TabsContent value="inactive" className="space-y-6">
          {inactiveModules.length === 0 ? (
            <div className="text-center py-12">
              <PowerOff className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-medium text-gray-900 mb-2">
                비활성화된 모듈이 없습니다
              </h3>
              <p className="text-gray-600">
                모든 모듈이 활성화되어 있습니다
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {inactiveModules.map((module) => (
                <Card key={module.id} className="border-gray-200 bg-gray-50/30">
                  <CardHeader>
                    <div className="flex justify-between items-start mb-2">
                      <CardTitle className="text-lg text-gray-600">{module.name}</CardTitle>
                      <Badge variant="secondary">
                        비활성
                      </Badge>
                    </div>
                    <CardDescription className="line-clamp-2 text-gray-500">
                      {module.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-600">버전:</span>
                          <span className="font-medium text-gray-600">{module.version}</span>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-600">설치일:</span>
                          <span className="font-medium text-gray-600">{formatDate(module.installed_at)}</span>
                        </div>
                      </div>

                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => toggleModuleStatus(module.id, false)}
                          className="flex-1"
                        >
                          <Power className="w-4 h-4 mr-1" />
                          활성화
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => uninstallModule(module.id, module.name)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
} 
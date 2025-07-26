'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Settings, Download, Star, Eye, RefreshCw } from 'lucide-react';
import { toast } from 'sonner';
// import PluginRenderer from '../../../components/PluginRenderer';

interface Plugin {
  id: number;
  name: string;
  display_name: string;
  description: string;
  version: string;
  author: string;
  category: string;
  tags: string[];
  icon: string;
  ui_schema: any;
  download_count: number;
  rating: number;
  review_count: number;
}

export default function PluginDashboard() {
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [installedPlugins, setInstalledPlugins] = useState<Plugin[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');

  // 플러그인 데이터 로드
  useEffect(() => {
    loadPlugins();
  }, []);

  const loadPlugins = async () => {
    try {
      const response = await fetch('/api/plugin/test');
      const data = await response.json();
      if (data.success) {
        setPlugins(data.data.plugins);
        // 설치된 플러그인 필터링 (더미 데이터)
        setInstalledPlugins(data.data.plugins.slice(0, 2)); // 처음 2개를 설치된 것으로 가정
      }
    } catch (error) {
      console.error('플러그인 로드 오류:', error);
      toast.error('플러그인 목록을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const refreshData = async () => {
    setLoading(true);
    await loadPlugins();
    toast.success('데이터가 새로고침되었습니다.');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* 헤더 */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">플러그인 대시보드</h1>
            <p className="text-gray-600">설치된 플러그인들의 실시간 데이터와 분석 결과를 확인하세요</p>
          </div>
          <Button onClick={refreshData} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            새로고침
          </Button>
        </div>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Settings className="h-4 w-4 text-blue-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm text-gray-600">설치된 플러그인</p>
                <p className="text-lg font-semibold">{installedPlugins.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <Download className="h-4 w-4 text-green-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm text-gray-600">활성 플러그인</p>
                <p className="text-lg font-semibold">{installedPlugins.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <Star className="h-4 w-4 text-yellow-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm text-gray-600">평균 평점</p>
                <p className="text-lg font-semibold">
                  {installedPlugins.length > 0 
                    ? (installedPlugins.reduce((sum, plugin) => sum + plugin.rating, 0) / installedPlugins.length).toFixed(1)
                    : '0.0'
                  }
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Eye className="h-4 w-4 text-purple-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm text-gray-600">총 사용량</p>
                <p className="text-lg font-semibold">
                  {installedPlugins.reduce((sum, plugin) => sum + plugin.download_count, 0)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 탭 네비게이션 */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="dashboard">대시보드</TabsTrigger>
          <TabsTrigger value="plugins">설치된 플러그인</TabsTrigger>
          <TabsTrigger value="marketplace">마켓플레이스</TabsTrigger>
        </TabsList>

        {/* 대시보드 탭 */}
        <TabsContent value="dashboard" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {installedPlugins.map((plugin) => (
              <Card key={plugin.id} className="col-span-1">
                <CardHeader>
                  <CardTitle>{plugin.display_name}</CardTitle>
                  <CardDescription>{plugin.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center p-6">
                    <div className="text-4xl font-bold text-blue-600 mb-2">85%</div>
                    <p className="text-gray-600">최적화 완료율</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
          
          {installedPlugins.length === 0 && (
            <Card>
              <CardContent className="p-12 text-center">
                <div className="text-gray-400 mb-4">
                  <Settings className="h-16 w-16 mx-auto" />
                </div>
                <h3 className="text-lg font-semibold mb-2">설치된 플러그인이 없습니다</h3>
                <p className="text-gray-600 mb-4">마켓플레이스에서 유용한 플러그인을 설치해보세요</p>
                <Button onClick={() => setActiveTab('marketplace')}>
                  마켓플레이스로 이동
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* 설치된 플러그인 탭 */}
        <TabsContent value="plugins" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {installedPlugins.map((plugin) => (
              <Card key={plugin.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-2">
                      <div className="p-2 bg-gray-100 rounded-lg">
                        <i className={`${plugin.icon} text-lg`}></i>
                      </div>
                      <div>
                        <CardTitle className="text-lg">{plugin.display_name}</CardTitle>
                        <CardDescription className="text-sm">
                          v{plugin.version} • {plugin.author}
                        </CardDescription>
                      </div>
                    </div>
                    <Badge variant="secondary" className="text-xs">
                      설치됨
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600 mb-4 line-clamp-3">
                    {plugin.description}
                  </p>
                  
                  {/* 태그 */}
                  <div className="flex flex-wrap gap-1 mb-4">
                    {plugin.tags.slice(0, 3).map((tag) => (
                      <Badge key={tag} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>

                  {/* 통계 */}
                  <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                    <div className="flex items-center space-x-4">
                      <span className="flex items-center">
                        <Download className="h-3 w-3 mr-1" />
                        {plugin.download_count}
                      </span>
                      <span className="flex items-center">
                        <Star className="h-3 w-3 mr-1" />
                        {plugin.rating}
                      </span>
                    </div>
                  </div>

                  {/* 액션 버튼 */}
                  <div className="flex space-x-2">
                    <Button variant="outline" size="sm" className="flex-1">
                      <Settings className="h-4 w-4 mr-1" />
                      설정
                    </Button>
                    <Button variant="outline" size="sm">
                      <Eye className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* 마켓플레이스 탭 */}
        <TabsContent value="marketplace" className="space-y-6">
          <Card>
            <CardContent className="p-12 text-center">
              <div className="text-gray-400 mb-4">
                <Download className="h-16 w-16 mx-auto" />
              </div>
              <h3 className="text-lg font-semibold mb-2">플러그인 마켓플레이스</h3>
              <p className="text-gray-600 mb-4">더 많은 플러그인을 찾아보세요</p>
              <Button onClick={() => window.location.href = '/plugin-marketplace'}>
                마켓플레이스로 이동
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
} 
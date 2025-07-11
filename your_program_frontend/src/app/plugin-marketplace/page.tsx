'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Progress } from '@/components/ui/progress';
import { Star, Download, Eye, Settings, Upload, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

interface Plugin {
  plugin_id: string;
  name: string;
  description: string;
  author: string;
  version: string;
  category: string;
  status: string;
  downloads: number;
  rating: number;
  rating_count: number;
  deployment_status?: any;
}

interface MarketplaceStats {
  total_plugins: number;
  total_downloads: number;
  total_ratings: number;
  category_statistics: Record<string, any>;
  recent_plugins: any[];
}

interface Category {
  id: string;
  name: string;
  description: string;
}

export default function PluginMarketplacePage() {
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [filteredPlugins, setFilteredPlugins] = useState<Plugin[]>([]);
  const [stats, setStats] = useState<MarketplaceStats | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('published');
  const [selectedPlugin, setSelectedPlugin] = useState<Plugin | null>(null);
  const [rating, setRating] = useState(0);
  const [deploymentStatus, setDeploymentStatus] = useState<any>({});

  // 데이터 로드
  useEffect(() => {
    loadMarketplaceData();
  }, []);

  // 필터링 적용
  useEffect(() => {
    let filtered = plugins;

    // 검색어 필터
    if (searchQuery) {
      filtered = filtered.filter(plugin =>
        plugin.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        plugin.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        plugin.author.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // 카테고리 필터
    if (selectedCategory) {
      filtered = filtered.filter(plugin => plugin.category === selectedCategory);
    }

    // 상태 필터
    if (selectedStatus) {
      filtered = filtered.filter(plugin => plugin.status === selectedStatus);
    }

    setFilteredPlugins(filtered);
  }, [plugins, searchQuery, selectedCategory, selectedStatus]);

  const loadMarketplaceData = async () => {
    try {
      setLoading(true);

      // 플러그인 목록 로드
      const pluginsResponse = await fetch('/api/marketplace/plugins?limit=100');
      const pluginsData = await pluginsResponse.json();
      
      if (pluginsData.success) {
        setPlugins(pluginsData.data.plugins);
      }

      // 통계 로드
      const statsResponse = await fetch('/api/marketplace/statistics');
      const statsData = await statsResponse.json();
      
      if (statsData.success) {
        setStats(statsData.data);
      }

      // 카테고리 로드
      const categoriesResponse = await fetch('/api/marketplace/categories');
      const categoriesData = await categoriesResponse.json();
      
      if (categoriesData.success) {
        setCategories(categoriesData.data);
      }

      // 배포 상태 로드
      const deploymentResponse = await fetch('/api/marketplace/deployments');
      const deploymentData = await deploymentResponse.json();
      
      if (deploymentData.success) {
        setDeploymentStatus(deploymentData.data);
      }

    } catch (error) {
      console.error('마켓플레이스 데이터 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (pluginId: string) => {
    try {
      const response = await fetch(`/api/marketplace/plugins/${pluginId}/download`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          target_dir: 'plugins/downloaded'
        })
      });

      const data = await response.json();
      
      if (data.success) {
        alert('플러그인이 성공적으로 다운로드되었습니다.');
        loadMarketplaceData(); // 데이터 새로고침
      } else {
        alert('다운로드 실패: ' + data.error);
      }
    } catch (error) {
      console.error('다운로드 실패:', error);
      alert('다운로드 중 오류가 발생했습니다.');
    }
  };

  const handleRate = async (pluginId: string, rating: number) => {
    try {
      const response = await fetch(`/api/marketplace/plugins/${pluginId}/rate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ rating })
      });

      const data = await response.json();
      
      if (data.success) {
        alert('평점이 성공적으로 등록되었습니다.');
        loadMarketplaceData(); // 데이터 새로고침
      } else {
        alert('평점 등록 실패: ' + data.error);
      }
    } catch (error) {
      console.error('평점 등록 실패:', error);
      alert('평점 등록 중 오류가 발생했습니다.');
    }
  };

  const handleDeploy = async (pluginId: string, environment: string = 'production') => {
    try {
      const response = await fetch(`/api/marketplace/deployments/${pluginId}/deploy`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          environment,
          plugin_path: `plugins/downloaded/${pluginId}`
        })
      });

      const data = await response.json();
      
      if (data.success) {
        alert('플러그인이 성공적으로 배포되었습니다.');
        loadMarketplaceData(); // 데이터 새로고침
      } else {
        alert('배포 실패: ' + data.error);
      }
    } catch (error) {
      console.error('배포 실패:', error);
      alert('배포 중 오류가 발생했습니다.');
    }
  };

  const handleUndeploy = async (pluginId: string, environment: string = 'production') => {
    try {
      const response = await fetch(`/api/marketplace/deployments/${pluginId}/undeploy`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ environment })
      });

      const data = await response.json();
      
      if (data.success) {
        alert('플러그인 배포가 해제되었습니다.');
        loadMarketplaceData(); // 데이터 새로고침
      } else {
        alert('배포 해제 실패: ' + data.error);
      }
    } catch (error) {
      console.error('배포 해제 실패:', error);
      alert('배포 해제 중 오류가 발생했습니다.');
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'published':
        return <Badge variant="default" className="bg-green-100 text-green-800">게시됨</Badge>;
      case 'pending':
        return <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">대기중</Badge>;
      case 'rejected':
        return <Badge variant="destructive">거부됨</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const getCategoryName = (categoryId: string) => {
    const category = categories.find(c => c.id === categoryId);
    return category ? category.name : categoryId;
  };

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`w-4 h-4 ${i < rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}`}
      />
    ));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">마켓플레이스 로딩 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">플러그인 마켓플레이스</h1>
          <p className="text-gray-600 mt-2">다양한 플러그인을 검색하고 설치하세요</p>
        </div>
        <Button>
          <Upload className="w-4 h-4 mr-2" />
          플러그인 등록
        </Button>
      </div>

      {/* 통계 카드 */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Settings className="w-6 h-6 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm text-gray-600">총 플러그인</p>
                  <p className="text-2xl font-bold">{stats.total_plugins}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center">
                <div className="p-2 bg-green-100 rounded-lg">
                  <Download className="w-6 h-6 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm text-gray-600">총 다운로드</p>
                  <p className="text-2xl font-bold">{stats.total_downloads}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center">
                <div className="p-2 bg-yellow-100 rounded-lg">
                  <Star className="w-6 h-6 text-yellow-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm text-gray-600">총 평점</p>
                  <p className="text-2xl font-bold">{stats.total_ratings}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <Eye className="w-6 h-6 text-purple-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm text-gray-600">활성 플러그인</p>
                  <p className="text-2xl font-bold">{filteredPlugins.length}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 필터 및 검색 */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <Input
                placeholder="플러그인 검색..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger className="w-full md:w-48">
                <SelectValue placeholder="카테고리 선택" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">모든 카테고리</SelectItem>
                {categories.map(category => (
                  <SelectItem key={category.id} value={category.id}>
                    {category.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={selectedStatus} onValueChange={setSelectedStatus}>
              <SelectTrigger className="w-full md:w-48">
                <SelectValue placeholder="상태 선택" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="published">게시됨</SelectItem>
                <SelectItem value="pending">대기중</SelectItem>
                <SelectItem value="rejected">거부됨</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* 플러그인 목록 */}
      <Tabs defaultValue="all" className="space-y-4">
        <TabsList>
          <TabsTrigger value="all">모든 플러그인 ({filteredPlugins.length})</TabsTrigger>
          <TabsTrigger value="installed">설치된 플러그인</TabsTrigger>
          <TabsTrigger value="favorites">즐겨찾기</TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredPlugins.map(plugin => (
              <Card key={plugin.plugin_id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-lg">{plugin.name}</CardTitle>
                      <CardDescription className="mt-1">
                        {plugin.description}
                      </CardDescription>
                    </div>
                    {getStatusBadge(plugin.status)}
                  </div>
                </CardHeader>
                
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between text-sm text-gray-600">
                    <span>작성자: {plugin.author}</span>
                    <span>v{plugin.version}</span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">
                      {getCategoryName(plugin.category)}
                    </span>
                    <div className="flex items-center space-x-1">
                      {renderStars(plugin.rating)}
                      <span className="text-sm text-gray-600 ml-1">
                        ({plugin.rating_count})
                      </span>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between text-sm text-gray-600">
                    <span>다운로드: {plugin.downloads}</span>
                    <span>평점: {plugin.rating.toFixed(1)}</span>
                  </div>
                  
                  <div className="flex space-x-2">
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button variant="outline" size="sm" className="flex-1">
                          <Eye className="w-4 h-4 mr-1" />
                          상세보기
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="max-w-2xl">
                        <DialogHeader>
                          <DialogTitle>{plugin.name}</DialogTitle>
                          <DialogDescription>
                            플러그인 상세 정보 및 관리
                          </DialogDescription>
                        </DialogHeader>
                        <div className="space-y-4">
                          <div>
                            <h4 className="font-semibold mb-2">설명</h4>
                            <p className="text-gray-600">{plugin.description}</p>
                          </div>
                          
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <h4 className="font-semibold mb-2">기본 정보</h4>
                              <div className="space-y-1 text-sm">
                                <p><span className="font-medium">작성자:</span> {plugin.author}</p>
                                <p><span className="font-medium">버전:</span> {plugin.version}</p>
                                <p><span className="font-medium">카테고리:</span> {getCategoryName(plugin.category)}</p>
                                <p><span className="font-medium">상태:</span> {plugin.status}</p>
                              </div>
                            </div>
                            
                            <div>
                              <h4 className="font-semibold mb-2">통계</h4>
                              <div className="space-y-1 text-sm">
                                <p><span className="font-medium">다운로드:</span> {plugin.downloads}</p>
                                <p><span className="font-medium">평점:</span> {plugin.rating.toFixed(1)} ({plugin.rating_count}개)</p>
                                <div className="flex items-center mt-2">
                                  {renderStars(plugin.rating)}
                                </div>
                              </div>
                            </div>
                          </div>
                          
                          {plugin.deployment_status && (
                            <div>
                              <h4 className="font-semibold mb-2">배포 상태</h4>
                              <div className="flex items-center space-x-2">
                                {plugin.deployment_status.status === 'deployed' ? (
                                  <CheckCircle className="w-5 h-5 text-green-600" />
                                ) : (
                                  <XCircle className="w-5 h-5 text-red-600" />
                                )}
                                <span className="text-sm">
                                  {plugin.deployment_status.status === 'deployed' ? '배포됨' : '배포되지 않음'}
                                </span>
                              </div>
                            </div>
                          )}
                          
                          <div className="flex space-x-2 pt-4">
                            <Button
                              onClick={() => handleDownload(plugin.plugin_id)}
                              className="flex-1"
                            >
                              <Download className="w-4 h-4 mr-2" />
                              다운로드
                            </Button>
                            
                            {plugin.deployment_status?.status === 'deployed' ? (
                              <Button
                                variant="destructive"
                                onClick={() => handleUndeploy(plugin.plugin_id)}
                                className="flex-1"
                              >
                                배포 해제
                              </Button>
                            ) : (
                              <Button
                                variant="secondary"
                                onClick={() => handleDeploy(plugin.plugin_id)}
                                className="flex-1"
                              >
                                배포
                              </Button>
                            )}
                          </div>
                        </div>
                      </DialogContent>
                    </Dialog>
                    
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setSelectedPlugin(plugin);
                        setRating(0);
                      }}
                    >
                      <Star className="w-4 h-4 mr-1" />
                      평점
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
          
          {filteredPlugins.length === 0 && (
            <div className="text-center py-12">
              <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">플러그인을 찾을 수 없습니다</h3>
              <p className="text-gray-600">검색 조건을 변경해보세요.</p>
            </div>
          )}
        </TabsContent>

        <TabsContent value="installed" className="text-center py-12">
          <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">설치된 플러그인이 없습니다</h3>
          <p className="text-gray-600">플러그인을 다운로드하고 설치해보세요.</p>
        </TabsContent>

        <TabsContent value="favorites" className="text-center py-12">
          <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">즐겨찾기한 플러그인이 없습니다</h3>
          <p className="text-gray-600">플러그인을 즐겨찾기에 추가해보세요.</p>
        </TabsContent>
      </Tabs>

      {/* 평점 모달 */}
      {selectedPlugin && (
        <Dialog open={!!selectedPlugin} onOpenChange={() => setSelectedPlugin(null)}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{selectedPlugin.name} 평점</DialogTitle>
              <DialogDescription>
                이 플러그인에 대한 평점을 남겨주세요.
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4">
              <div className="flex justify-center space-x-2">
                {Array.from({ length: 5 }, (_, i) => (
                  <button
                    key={i}
                    onClick={() => setRating(i + 1)}
                    className="p-2 hover:bg-gray-100 rounded"
                  >
                    <Star
                      className={`w-8 h-8 ${
                        i < rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
                      }`}
                    />
                  </button>
                ))}
              </div>
              
              <div className="text-center">
                <p className="text-sm text-gray-600">
                  선택된 평점: {rating} / 5
                </p>
              </div>
              
              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  onClick={() => setSelectedPlugin(null)}
                  className="flex-1"
                >
                  취소
                </Button>
                <Button
                  onClick={() => {
                    if (rating > 0) {
                      handleRate(selectedPlugin.plugin_id, rating);
                      setSelectedPlugin(null);
                    }
                  }}
                  disabled={rating === 0}
                  className="flex-1"
                >
                  평점 등록
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
} 
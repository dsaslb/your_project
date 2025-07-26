'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Star, Download, Eye, Settings, Trash2, RefreshCw } from 'lucide-react';
import { toast } from 'sonner';

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

interface Category {
  id: string;
  name: string;
  description: string;
  icon: string;
  plugin_count: number;
}

export default function PluginMarketplace() {
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [sortBy, setSortBy] = useState('download_count');
  const [sortOrder, setSortOrder] = useState('desc');
  const [installedPlugins, setInstalledPlugins] = useState<Set<number>>(new Set());

  // 플러그인 데이터 로드
  useEffect(() => {
    loadPlugins();
    loadCategories();
  }, []);

  const loadPlugins = async () => {
    try {
      const response = await fetch('/api/plugin/test');
      const data = await response.json();
      if (data.success) {
        setPlugins(data.data.plugins);
      }
    } catch (error) {
      console.error('플러그인 로드 오류:', error);
      toast.error('플러그인 목록을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const loadCategories = async () => {
    try {
      const response = await fetch('/api/plugin/categories');
      const data = await response.json();
      if (data.success) {
        setCategories(data.categories);
      }
    } catch (error) {
      console.error('카테고리 로드 오류:', error);
    }
  };

  // 플러그인 설치
  const installPlugin = async (pluginId: number) => {
    try {
      const response = await fetch('/api/plugin/install', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ plugin_id: pluginId }),
      });
      
      const data = await response.json();
      if (data.success) {
        setInstalledPlugins(prev => new Set(prev).add(pluginId));
        toast.success(data.message);
      } else {
        toast.error(data.error || '설치에 실패했습니다.');
      }
    } catch (error) {
      console.error('플러그인 설치 오류:', error);
      toast.error('플러그인 설치에 실패했습니다.');
    }
  };

  // 플러그인 제거
  const uninstallPlugin = async (installationId: string) => {
    try {
      const response = await fetch('/api/plugin/uninstall', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ installation_id: installationId }),
      });
      
      const data = await response.json();
      if (data.success) {
        setInstalledPlugins(prev => {
          const newSet = new Set(prev);
          // installationId에서 plugin_id 추출 (install_1_12345 -> 1)
          const pluginId = parseInt(installationId.split('_')[1]);
          newSet.delete(pluginId);
          return newSet;
        });
        toast.success(data.message);
      } else {
        toast.error(data.error || '제거에 실패했습니다.');
      }
    } catch (error) {
      console.error('플러그인 제거 오류:', error);
      toast.error('플러그인 제거에 실패했습니다.');
    }
  };

  // 필터링된 플러그인 목록
  const filteredPlugins = plugins.filter(plugin => {
    const matchesSearch = plugin.display_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         plugin.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         plugin.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesCategory = selectedCategory === 'all' || plugin.category === selectedCategory;
    
    return matchesSearch && matchesCategory;
  });

  // 정렬된 플러그인 목록
  const sortedPlugins = [...filteredPlugins].sort((a, b) => {
    let aValue = a[sortBy as keyof Plugin];
    let bValue = b[sortBy as keyof Plugin];
    
    if (typeof aValue === 'string') {
      aValue = aValue.toLowerCase();
      bValue = bValue.toLowerCase();
    }
    
    if (sortOrder === 'asc') {
      return aValue > bValue ? 1 : -1;
    } else {
      return aValue < bValue ? 1 : -1;
    }
  });

  const getCategoryIcon = (categoryId: string) => {
    const category = categories.find(cat => cat.id === categoryId);
    return category?.icon || 'fas fa-puzzle-piece';
  };

  const getCategoryName = (categoryId: string) => {
    const category = categories.find(cat => cat.id === categoryId);
    return category?.name || categoryId;
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
        <h1 className="text-3xl font-bold mb-2">플러그인 마켓플레이스</h1>
        <p className="text-gray-600">매장 운영을 더욱 효율적으로 만들어주는 플러그인들을 찾아보세요</p>
      </div>

      {/* 필터 및 검색 */}
      <div className="mb-6 space-y-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <Input
              placeholder="플러그인 검색..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full"
            />
          </div>
          <Select value={selectedCategory} onValueChange={setSelectedCategory}>
            <SelectTrigger className="w-full sm:w-48">
              <SelectValue placeholder="카테고리 선택" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">모든 카테고리</SelectItem>
              {categories.map((category) => (
                <SelectItem key={category.id} value={category.id}>
                  {category.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={sortBy} onValueChange={setSortBy}>
            <SelectTrigger className="w-full sm:w-48">
              <SelectValue placeholder="정렬 기준" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="download_count">다운로드 수</SelectItem>
              <SelectItem value="rating">평점</SelectItem>
              <SelectItem value="display_name">이름</SelectItem>
            </SelectContent>
          </Select>
          <Button
            variant="outline"
            onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
            className="w-full sm:w-auto"
          >
            {sortOrder === 'asc' ? '오름차순' : '내림차순'}
          </Button>
        </div>
      </div>

      {/* 통계 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Download className="h-4 w-4 text-blue-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm text-gray-600">총 플러그인</p>
                <p className="text-lg font-semibold">{plugins.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <Settings className="h-4 w-4 text-green-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm text-gray-600">설치된 플러그인</p>
                <p className="text-lg font-semibold">{installedPlugins.size}</p>
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
                  {(plugins.reduce((sum, plugin) => sum + plugin.rating, 0) / plugins.length).toFixed(1)}
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
                <p className="text-sm text-gray-600">총 다운로드</p>
                <p className="text-lg font-semibold">
                  {plugins.reduce((sum, plugin) => sum + plugin.download_count, 0)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 플러그인 목록 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {sortedPlugins.map((plugin) => (
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
                  {getCategoryName(plugin.category)}
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
                {plugin.tags.length > 3 && (
                  <Badge variant="outline" className="text-xs">
                    +{plugin.tags.length - 3}
                  </Badge>
                )}
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
                  <span>({plugin.review_count})</span>
                </div>
              </div>

              {/* 액션 버튼 */}
              <div className="flex space-x-2">
                {installedPlugins.has(plugin.id) ? (
                  <Button
                    variant="destructive"
                    size="sm"
                    className="flex-1"
                    onClick={() => uninstallPlugin(`install_${plugin.id}_12345`)}
                  >
                    <Trash2 className="h-4 w-4 mr-1" />
                    제거
                  </Button>
                ) : (
                  <Button
                    size="sm"
                    className="flex-1"
                    onClick={() => installPlugin(plugin.id)}
                  >
                    <Download className="h-4 w-4 mr-1" />
                    설치
                  </Button>
                )}
                <Button variant="outline" size="sm">
                  <Eye className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* 결과 없음 */}
      {sortedPlugins.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <i className="fas fa-search text-6xl"></i>
          </div>
          <h3 className="text-lg font-semibold mb-2">플러그인을 찾을 수 없습니다</h3>
          <p className="text-gray-600">검색 조건을 변경해보세요</p>
        </div>
      )}
    </div>
  );
} 
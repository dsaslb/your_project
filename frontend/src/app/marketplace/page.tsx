'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Star, Download, Eye, Settings, Search, Filter, TrendingUp } from 'lucide-react';
import { toast } from 'sonner';

interface Module {
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
  requirements: {
    python_version: string;
    dependencies: string[];
    permissions: string[];
  };
  screenshots: string[];
  status: string;
  created_at: string;
  updated_at: string;
}

interface MarketplaceResponse {
  success: boolean;
  modules: Module[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
  };
  categories: string[];
  total_modules: number;
}

export default function MarketplacePage() {
  const [modules, setModules] = useState<Module[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [sortBy, setSortBy] = useState('downloads');
  const [order, setOrder] = useState('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [categories, setCategories] = useState<string[]>([]);
  const [trendingModules, setTrendingModules] = useState<Module[]>([]);

  // 모듈 목록 조회
  const fetchModules = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: currentPage.toString(),
        per_page: '12',
        sort_by: sortBy,
        order: order,
      });

      if (searchTerm) params.append('search', searchTerm);
      if (selectedCategory) params.append('category', selectedCategory);

      const response = await fetch(`/api/marketplace/modules?${params}`);
      const data: MarketplaceResponse = await response.json();

      if (data.success) {
        setModules(data.modules);
        setTotalPages(data.pagination.pages);
        setCategories(data.categories);
      } else {
        toast.error('모듈 목록을 불러오는데 실패했습니다.');
      }
    } catch (error) {
      console.error('모듈 목록 조회 실패:', error);
      toast.error('모듈 목록을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 인기 모듈 조회
  const fetchTrendingModules = async () => {
    try {
      const response = await fetch('/api/marketplace/trending');
      const data = await response.json();

      if (data.success) {
        setTrendingModules(data.modules);
      }
    } catch (error) {
      console.error('인기 모듈 조회 실패:', error);
    }
  };

  // 모듈 설치
  const installModule = async (moduleId: string, moduleName: string) => {
    try {
      const response = await fetch(`/api/marketplace/modules/${moduleId}/install`, {
        method: 'POST',
      });
      const data = await response.json();

      if (data.success) {
        toast.success(data.message);
        fetchModules(); // 목록 새로고침
      } else {
        toast.error(data.error || '모듈 설치에 실패했습니다.');
      }
    } catch (error) {
      console.error('모듈 설치 실패:', error);
      toast.error('모듈 설치에 실패했습니다.');
    }
  };

  // 모듈 상세 보기
  const viewModuleDetail = (moduleId: string) => {
    // 모듈 상세 페이지로 이동
    window.open(`/marketplace/modules/${moduleId}`, '_blank');
  };

  useEffect(() => {
    fetchModules();
    fetchTrendingModules();
  }, [currentPage, sortBy, order, searchTerm, selectedCategory]);

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

  const formatNumber = (num: number) => {
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">모듈 마켓플레이스</h1>
        <p className="text-gray-600">
          업무 효율성을 높이는 다양한 모듈을 찾아보세요
        </p>
      </div>

      <Tabs defaultValue="all" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="all">전체 모듈</TabsTrigger>
          <TabsTrigger value="trending">인기 모듈</TabsTrigger>
          <TabsTrigger value="installed">설치된 모듈</TabsTrigger>
        </TabsList>

        {/* 검색 및 필터 */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <Input
              placeholder="모듈 검색..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          <Select value={selectedCategory} onValueChange={setSelectedCategory}>
            <SelectTrigger className="w-full sm:w-48">
              <SelectValue placeholder="카테고리 선택" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">전체 카테고리</SelectItem>
              {categories.map((category) => (
                <SelectItem key={category} value={category}>
                  {category}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={sortBy} onValueChange={setSortBy}>
            <SelectTrigger className="w-full sm:w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="downloads">다운로드</SelectItem>
              <SelectItem value="rating">평점</SelectItem>
              <SelectItem value="name">이름</SelectItem>
              <SelectItem value="price">가격</SelectItem>
            </SelectContent>
          </Select>
          <Button
            variant="outline"
            onClick={() => setOrder(order === 'desc' ? 'asc' : 'desc')}
          >
            {order === 'desc' ? '내림차순' : '오름차순'}
          </Button>
        </div>

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
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {modules.map((module) => (
                  <Card key={module.id} className="hover:shadow-lg transition-shadow">
                    <CardHeader>
                      <div className="flex justify-between items-start mb-2">
                        <CardTitle className="text-lg">{module.name}</CardTitle>
                        <Badge variant={module.price === 0 ? 'default' : 'secondary'}>
                          {module.price === 0 ? '무료' : `${module.price}원`}
                        </Badge>
                      </div>
                      <CardDescription className="line-clamp-2">
                        {module.description}
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {/* 평점 및 다운로드 */}
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-1">
                            {renderStars(module.rating)}
                            <span className="text-sm text-gray-600 ml-1">
                              {module.rating.toFixed(1)}
                            </span>
                          </div>
                          <div className="flex items-center text-sm text-gray-600">
                            <Download className="w-4 h-4 mr-1" />
                            {formatNumber(module.downloads)}
                          </div>
                        </div>

                        {/* 태그 */}
                        <div className="flex flex-wrap gap-1">
                          {module.tags.slice(0, 3).map((tag) => (
                            <Badge key={tag} variant="outline" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                          {module.tags.length > 3 && (
                            <Badge variant="outline" className="text-xs">
                              +{module.tags.length - 3}
                            </Badge>
                          )}
                        </div>

                        {/* 기능 목록 */}
                        <div className="space-y-1">
                          {module.features.slice(0, 2).map((feature, index) => (
                            <div key={index} className="text-sm text-gray-600 flex items-center">
                              <div className="w-1 h-1 bg-blue-500 rounded-full mr-2"></div>
                              {feature}
                            </div>
                          ))}
                          {module.features.length > 2 && (
                            <div className="text-sm text-gray-500">
                              +{module.features.length - 2}개 더보기
                            </div>
                          )}
                        </div>

                        {/* 액션 버튼 */}
                        <div className="flex gap-2 pt-2">
                          <Button
                            onClick={() => installModule(module.id, module.name)}
                            className="flex-1"
                          >
                            설치
                          </Button>
                          <Button
                            variant="outline"
                            onClick={() => viewModuleDetail(module.id)}
                          >
                            <Eye className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {/* 페이지네이션 */}
              {totalPages > 1 && (
                <div className="flex justify-center mt-8">
                  <div className="flex space-x-2">
                    <Button
                      variant="outline"
                      onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                      disabled={currentPage === 1}
                    >
                      이전
                    </Button>
                    {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                      const page = i + 1;
                      return (
                        <Button
                          key={page}
                          variant={currentPage === page ? 'default' : 'outline'}
                          onClick={() => setCurrentPage(page)}
                        >
                          {page}
                        </Button>
                      );
                    })}
                    <Button
                      variant="outline"
                      onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                      disabled={currentPage === totalPages}
                    >
                      다음
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </TabsContent>

        {/* 인기 모듈 탭 */}
        <TabsContent value="trending" className="space-y-6">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-orange-500" />
            <h2 className="text-xl font-semibold">인기 모듈</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {trendingModules.map((module, index) => (
              <Card key={module.id} className="hover:shadow-lg transition-shadow">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <Badge variant="destructive" className="text-xs">
                      #{index + 1}
                    </Badge>
                    <Badge variant={module.price === 0 ? 'default' : 'secondary'}>
                      {module.price === 0 ? '무료' : `${module.price}원`}
                    </Badge>
                  </div>
                  <CardTitle className="text-sm">{module.name}</CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-xs">
                      <div className="flex items-center">
                        {renderStars(module.rating)}
                        <span className="ml-1">{module.rating.toFixed(1)}</span>
                      </div>
                      <div className="flex items-center">
                        <Download className="w-3 h-3 mr-1" />
                        {formatNumber(module.downloads)}
                      </div>
                    </div>
                    <Button
                      size="sm"
                      onClick={() => installModule(module.id, module.name)}
                      className="w-full"
                    >
                      설치
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* 설치된 모듈 탭 */}
        <TabsContent value="installed" className="space-y-6">
          <div className="text-center py-8">
            <Settings className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              설치된 모듈이 없습니다
            </h3>
            <p className="text-gray-600 mb-4">
              마켓플레이스에서 원하는 모듈을 설치해보세요
            </p>
            <Button onClick={() => {
              const element = document.querySelector('[data-value="all"]') as HTMLElement;
              element?.click();
            }}>
              모듈 둘러보기
            </Button>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
} 
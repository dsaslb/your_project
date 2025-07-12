import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { 
  Search, 
  Filter, 
  Download, 
  Star, 
  Eye, 
  MessageSquare, 
  Package, 
  Users, 
  TrendingUp,
  Heart,
  Share2,
  Bookmark,
  Calendar,
  Tag,
  Globe,
  Code,
  Shield,
  Zap
} from 'lucide-react';

interface Plugin {
  id: string;
  name: string;
  description: string;
  version: string;
  author: string;
  category: string;
  tags: string[];
  price: number;
  download_count: number;
  rating: number;
  review_count: number;
  size: number;
  dependencies: string[];
  compatibility: string[];
  created_at: string;
  updated_at: string;
  status: string;
  license: string;
  homepage: string;
  repository: string;
  download_stats?: {
    total_downloads: number;
    daily_downloads: number;
    weekly_downloads: number;
    monthly_downloads: number;
    last_download: string;
  };
}

interface Review {
  id: number;
  plugin_id: string;
  user_id: string;
  rating: number;
  title: string;
  content: string;
  created_at: string;
  helpful_count: number;
  reported: boolean;
}

interface MarketplaceStats {
  total_plugins: number;
  total_downloads: number;
  average_rating: number;
  free_plugins: number;
  paid_plugins: number;
  categories: Record<string, number>;
}

const EnhancedMarketplace: React.FC = () => {
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [selectedPlugin, setSelectedPlugin] = useState<Plugin | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [stats, setStats] = useState<MarketplaceStats | null>(null);
  const [categories, setCategories] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [sortBy, setSortBy] = useState<string>('name');
  const [sortOrder, setSortOrder] = useState<string>('asc');
  const [showReviewDialog, setShowReviewDialog] = useState(false);
  const [newReview, setNewReview] = useState({
    rating: 5,
    title: '',
    content: ''
  });

  // 데이터 로드
  useEffect(() => {
    loadMarketplaceData();
  }, []);

  useEffect(() => {
    loadPlugins();
  }, [searchTerm, selectedCategory, sortBy, sortOrder]);

  const loadMarketplaceData = async () => {
    try {
      setLoading(true);
      
      // 통계 로드
      const statsResponse = await fetch('/api/enhanced-marketplace/stats');
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStats(statsData.data);
      }
      
      // 카테고리 로드
      const categoriesResponse = await fetch('/api/enhanced-marketplace/categories');
      if (categoriesResponse.ok) {
        const categoriesData = await categoriesResponse.json();
        setCategories(categoriesData.data);
      }
      
    } catch (error) {
      console.error('마켓플레이스 데이터 로드 오류:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadPlugins = async () => {
    try {
      const params = new URLSearchParams({
        sort_by: sortBy,
        sort_order: sortOrder,
        limit: '50'
      });
      
      if (searchTerm) params.append('search', searchTerm);
      if (selectedCategory) params.append('category', selectedCategory);
      
      const response = await fetch(`/api/enhanced-marketplace/plugins?${params}`);
      if (response.ok) {
        const data = await response.json();
        setPlugins(data.data);
      }
    } catch (error) {
      console.error('플러그인 목록 로드 오류:', error);
    }
  };

  const loadPluginDetails = async (pluginId: string) => {
    try {
      const response = await fetch(`/api/enhanced-marketplace/plugins/${pluginId}`);
      if (response.ok) {
        const data = await response.json();
        setSelectedPlugin(data.data);
        
        // 리뷰 로드
        const reviewsResponse = await fetch(`/api/enhanced-marketplace/plugins/${pluginId}/reviews`);
        if (reviewsResponse.ok) {
          const reviewsData = await reviewsResponse.json();
          setReviews(reviewsData.data);
        }
      }
    } catch (error) {
      console.error('플러그인 상세 정보 로드 오류:', error);
    }
  };

  const downloadPlugin = async (pluginId: string) => {
    try {
      const response = await fetch(`/api/enhanced-marketplace/plugins/${pluginId}/download`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        alert('플러그인이 다운로드되었습니다.');
        loadPlugins(); // 목록 새로고침
      } else {
        alert('다운로드에 실패했습니다.');
      }
    } catch (error) {
      console.error('플러그인 다운로드 오류:', error);
      alert('다운로드 중 오류가 발생했습니다.');
    }
  };

  const submitReview = async () => {
    if (!selectedPlugin) return;
    
    try {
      const response = await fetch(`/api/enhanced-marketplace/plugins/${selectedPlugin.id}/reviews`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newReview)
      });
      
      if (response.ok) {
        alert('리뷰가 등록되었습니다.');
        setShowReviewDialog(false);
        setNewReview({ rating: 5, title: '', content: '' });
        loadPluginDetails(selectedPlugin.id); // 리뷰 목록 새로고침
      } else {
        alert('리뷰 등록에 실패했습니다.');
      }
    } catch (error) {
      console.error('리뷰 등록 오류:', error);
      alert('리뷰 등록 중 오류가 발생했습니다.');
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
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
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">마켓플레이스를 로드하는 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">플러그인 마켓플레이스</h1>
          <p className="text-gray-600 mt-2">다양한 플러그인을 탐색하고 설치하세요</p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm">
            <Bookmark className="w-4 h-4 mr-2" />
            즐겨찾기
          </Button>
          <Button variant="outline" size="sm">
            <Share2 className="w-4 h-4 mr-2" />
            공유
          </Button>
        </div>
      </div>

      {/* 통계 카드 */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Package className="w-5 h-5 text-blue-600" />
                <div>
                  <p className="text-sm text-gray-600">전체 플러그인</p>
                  <p className="text-2xl font-bold">{stats.total_plugins}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Download className="w-5 h-5 text-green-600" />
                <div>
                  <p className="text-sm text-gray-600">총 다운로드</p>
                  <p className="text-2xl font-bold">{stats.total_downloads.toLocaleString()}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Star className="w-5 h-5 text-yellow-600" />
                <div>
                  <p className="text-sm text-gray-600">평균 평점</p>
                  <p className="text-2xl font-bold">{stats.average_rating}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Zap className="w-5 h-5 text-purple-600" />
                <div>
                  <p className="text-sm text-gray-600">무료 플러그인</p>
                  <p className="text-2xl font-bold">{stats.free_plugins}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Shield className="w-5 h-5 text-red-600" />
                <div>
                  <p className="text-sm text-gray-600">유료 플러그인</p>
                  <p className="text-2xl font-bold">{stats.paid_plugins}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 검색 및 필터 */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  placeholder="플러그인 검색..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger className="w-full lg:w-48">
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
              <SelectTrigger className="w-full lg:w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="name">이름순</SelectItem>
                <SelectItem value="rating">평점순</SelectItem>
                <SelectItem value="download_count">다운로드순</SelectItem>
                <SelectItem value="created_at">최신순</SelectItem>
                <SelectItem value="price">가격순</SelectItem>
              </SelectContent>
            </Select>
            <Button
              variant="outline"
              onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
            >
              {sortOrder === 'asc' ? '오름차순' : '내림차순'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 플러그인 목록 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {plugins.map((plugin) => (
          <Card key={plugin.id} className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="text-lg font-semibold line-clamp-1">{plugin.name}</CardTitle>
                  <p className="text-sm text-gray-600 mt-1">v{plugin.version}</p>
                </div>
                <Badge variant={plugin.price === 0 ? 'default' : 'secondary'}>
                  {plugin.price === 0 ? '무료' : `$${plugin.price}`}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-gray-700 line-clamp-2">{plugin.description}</p>
              
              <div className="flex items-center space-x-4 text-sm text-gray-600">
                <div className="flex items-center space-x-1">
                  <Star className="w-4 h-4" />
                  <span>{plugin.rating}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Download className="w-4 h-4" />
                  <span>{plugin.download_count.toLocaleString()}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <MessageSquare className="w-4 h-4" />
                  <span>{plugin.review_count}</span>
                </div>
              </div>
              
              <div className="flex flex-wrap gap-1">
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
              
              <div className="flex items-center justify-between pt-2">
                <div className="text-xs text-gray-500">
                  <p>크기: {formatFileSize(plugin.size)}</p>
                  <p>라이선스: {plugin.license}</p>
                </div>
                <div className="flex space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => loadPluginDetails(plugin.id)}
                  >
                    <Eye className="w-4 h-4" />
                  </Button>
                  <Button
                    size="sm"
                    onClick={() => downloadPlugin(plugin.id)}
                  >
                    <Download className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* 플러그인 상세 다이얼로그 */}
      {selectedPlugin && (
        <Dialog open={!!selectedPlugin} onOpenChange={() => setSelectedPlugin(null)}>
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="flex items-center space-x-2">
                <Package className="w-6 h-6" />
                <span>{selectedPlugin.name}</span>
                <Badge variant={selectedPlugin.price === 0 ? 'default' : 'secondary'}>
                  {selectedPlugin.price === 0 ? '무료' : `$${selectedPlugin.price}`}
                </Badge>
              </DialogTitle>
            </DialogHeader>
            
            <div className="space-y-6">
              {/* 기본 정보 */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="font-semibold mb-2">설명</h3>
                  <p className="text-gray-700">{selectedPlugin.description}</p>
                </div>
                <div>
                  <h3 className="font-semibold mb-2">통계</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>평점:</span>
                      <div className="flex items-center space-x-1">
                        {renderStars(selectedPlugin.rating)}
                        <span className="ml-1">({selectedPlugin.rating})</span>
                      </div>
                    </div>
                    <div className="flex justify-between">
                      <span>다운로드:</span>
                      <span>{selectedPlugin.download_count.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>리뷰:</span>
                      <span>{selectedPlugin.review_count}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>크기:</span>
                      <span>{formatFileSize(selectedPlugin.size)}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* 상세 정보 */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <h4 className="font-medium mb-2">개발자</h4>
                  <p className="text-sm text-gray-600">{selectedPlugin.author}</p>
                </div>
                <div>
                  <h4 className="font-medium mb-2">카테고리</h4>
                  <Badge variant="outline">{selectedPlugin.category}</Badge>
                </div>
                <div>
                  <h4 className="font-medium mb-2">라이선스</h4>
                  <p className="text-sm text-gray-600">{selectedPlugin.license}</p>
                </div>
              </div>

              {/* 태그 */}
              <div>
                <h4 className="font-medium mb-2">태그</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedPlugin.tags.map((tag) => (
                    <Badge key={tag} variant="outline">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* 의존성 및 호환성 */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium mb-2">의존성</h4>
                  {selectedPlugin.dependencies.length > 0 ? (
                    <div className="space-y-1">
                      {selectedPlugin.dependencies.map((dep) => (
                        <Badge key={dep} variant="outline" className="text-xs">
                          {dep}
                        </Badge>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500">의존성 없음</p>
                  )}
                </div>
                <div>
                  <h4 className="font-medium mb-2">호환성</h4>
                  <div className="space-y-1">
                    {selectedPlugin.compatibility.map((comp) => (
                      <Badge key={comp} variant="outline" className="text-xs">
                        {comp}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>

              {/* 링크 */}
              {(selectedPlugin.homepage || selectedPlugin.repository) && (
                <div className="flex space-x-4">
                  {selectedPlugin.homepage && (
                    <Button variant="outline" size="sm" asChild>
                      <a href={selectedPlugin.homepage} target="_blank" rel="noopener noreferrer">
                        <Globe className="w-4 h-4 mr-2" />
                        홈페이지
                      </a>
                    </Button>
                  )}
                  {selectedPlugin.repository && (
                    <Button variant="outline" size="sm" asChild>
                      <a href={selectedPlugin.repository} target="_blank" rel="noopener noreferrer">
                        <Code className="w-4 h-4 mr-2" />
                        저장소
                      </a>
                    </Button>
                  )}
                </div>
              )}

              <Separator />

              {/* 리뷰 섹션 */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold">리뷰 ({reviews.length})</h3>
                  <Button onClick={() => setShowReviewDialog(true)}>
                    리뷰 작성
                  </Button>
                </div>
                
                <div className="space-y-4">
                  {reviews.map((review) => (
                    <Card key={review.id}>
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex items-center space-x-2">
                            <div className="flex items-center space-x-1">
                              {renderStars(review.rating)}
                            </div>
                            <span className="font-medium">{review.title}</span>
                          </div>
                          <span className="text-sm text-gray-500">
                            {new Date(review.created_at).toLocaleDateString()}
                          </span>
                        </div>
                        <p className="text-gray-700 mt-2">{review.content}</p>
                        <div className="flex items-center justify-between mt-3">
                          <span className="text-sm text-gray-500">by {review.user_id}</span>
                          <div className="flex items-center space-x-2">
                            <Button variant="ghost" size="sm">
                              <Heart className="w-4 h-4 mr-1" />
                              {review.helpful_count}
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                  
                  {reviews.length === 0 && (
                    <p className="text-center text-gray-500 py-8">
                      아직 리뷰가 없습니다. 첫 번째 리뷰를 작성해보세요!
                    </p>
                  )}
                </div>
              </div>

              {/* 액션 버튼 */}
              <div className="flex justify-end space-x-4 pt-4">
                <Button variant="outline" onClick={() => setSelectedPlugin(null)}>
                  닫기
                </Button>
                <Button onClick={() => downloadPlugin(selectedPlugin.id)}>
                  <Download className="w-4 h-4 mr-2" />
                  다운로드
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}

      {/* 리뷰 작성 다이얼로그 */}
      <Dialog open={showReviewDialog} onOpenChange={setShowReviewDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>리뷰 작성</DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4">
            <div>
              <Label htmlFor="rating">평점</Label>
              <Select value={newReview.rating.toString()} onValueChange={(value) => setNewReview({...newReview, rating: parseInt(value)})}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {[5, 4, 3, 2, 1].map((rating) => (
                    <SelectItem key={rating} value={rating.toString()}>
                      {rating}점
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label htmlFor="title">제목</Label>
              <Input
                id="title"
                value={newReview.title}
                onChange={(e) => setNewReview({...newReview, title: e.target.value})}
                placeholder="리뷰 제목을 입력하세요"
              />
            </div>
            
            <div>
              <Label htmlFor="content">내용</Label>
              <Textarea
                id="content"
                value={newReview.content}
                onChange={(e) => setNewReview({...newReview, content: e.target.value})}
                placeholder="플러그인에 대한 리뷰를 작성해주세요"
                rows={4}
              />
            </div>
            
            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setShowReviewDialog(false)}>
                취소
              </Button>
              <Button onClick={submitReview}>
                리뷰 등록
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default EnhancedMarketplace; 
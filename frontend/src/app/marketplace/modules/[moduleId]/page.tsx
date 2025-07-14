'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Star, Download, Calendar, User, Settings, MessageSquare, ThumbsUp, ThumbsDown } from 'lucide-react';
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
  is_installed?: boolean;
  is_activated?: boolean;
}

interface Review {
  id: string;
  user_name: string;
  rating: number;
  comment: string;
  created_at: string;
  helpful_count: number;
}

interface ModuleConfig {
  [key: string]: any;
}

export default function ModuleDetailPage() {
  const params = useParams();
  const moduleId = params.moduleId as string;
  
  const [module, setModule] = useState<Module | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [config, setConfig] = useState<ModuleConfig>({});
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  
  // 리뷰 작성 상태
  const [newReview, setNewReview] = useState({
    rating: 5,
    comment: ''
  });
  const [showReviewForm, setShowReviewForm] = useState(false);

  // 모듈 상세 정보 로드
  const loadModuleDetails = async () => {
    try {
      setLoading(true);
      
      // 모듈 상세 정보
      const moduleResponse = await fetch(`/api/module-marketplace/modules/${moduleId}`);
      if (moduleResponse.ok) {
        const moduleData = await moduleResponse.json();
        if (moduleData.success) {
          setModule(moduleData.module);
        }
      }
      
      // 모듈 리뷰 로드
      await loadModuleReviews();
      
      // 모듈 설정 로드
      await loadModuleSettings();
      
    } catch (error) {
      console.error('모듈 상세 정보 로드 오류:', error);
      toast.error('모듈 정보를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 모듈 리뷰 로드
  const loadModuleReviews = async () => {
    try {
      const response = await fetch(`/api/module-marketplace/modules/${moduleId}/reviews`);
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setReviews(data.reviews || []);
        }
      }
    } catch (error) {
      console.error('모듈 리뷰 로드 오류:', error);
    }
  };

  // 모듈 설정 로드
  const loadModuleSettings = async () => {
    try {
      const response = await fetch(`/api/module-marketplace/modules/${moduleId}/config`);
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setConfig(data.config || {});
        }
      }
    } catch (error) {
      console.error('모듈 설정 로드 오류:', error);
    }
  };

  // 모듈 설치
  const installModule = async () => {
    try {
      const response = await fetch(`/api/module-marketplace/modules/${moduleId}/install`, {
        method: 'POST',
      });
      const data = await response.json();

      if (data.success) {
        toast.success(data.message);
        await loadModuleDetails(); // 상세 정보 새로고침
      } else {
        toast.error(data.error || '모듈 설치에 실패했습니다.');
      }
    } catch (error) {
      console.error('모듈 설치 실패:', error);
      toast.error('모듈 설치에 실패했습니다.');
    }
  };

  // 모듈 활성화/비활성화
  const toggleModuleStatus = async () => {
    if (!module) return;
    
    try {
      const endpoint = module.is_activated ? 'deactivate' : 'activate';
      const response = await fetch(`/api/module-marketplace/modules/${moduleId}/${endpoint}`, {
        method: 'POST',
      });
      const data = await response.json();

      if (data.success) {
        toast.success(data.message);
        await loadModuleDetails(); // 상세 정보 새로고침
      } else {
        toast.error(data.error || '모듈 상태 변경에 실패했습니다.');
      }
    } catch (error) {
      console.error('모듈 상태 변경 실패:', error);
      toast.error('모듈 상태 변경에 실패했습니다.');
    }
  };

  // 리뷰 제출
  const submitReview = async () => {
    if (!newReview.comment.trim()) {
      toast.error('리뷰 내용을 입력해주세요.');
      return;
    }

    try {
      const response = await fetch(`/api/module-marketplace/modules/${moduleId}/reviews`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newReview),
      });
      const data = await response.json();

      if (data.success) {
        toast.success('리뷰가 성공적으로 등록되었습니다.');
        setNewReview({ rating: 5, comment: '' });
        setShowReviewForm(false);
        await loadModuleReviews(); // 리뷰 목록 새로고침
      } else {
        toast.error(data.error || '리뷰 등록에 실패했습니다.');
      }
    } catch (error) {
      console.error('리뷰 등록 실패:', error);
      toast.error('리뷰 등록에 실패했습니다.');
    }
  };

  useEffect(() => {
    if (moduleId) {
      loadModuleDetails();
    }
  }, [moduleId]);

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

  const formatNumber = (num: number) => {
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2 mb-8"></div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <div className="h-64 bg-gray-200 rounded mb-6"></div>
              <div className="h-32 bg-gray-200 rounded"></div>
            </div>
            <div>
              <div className="h-48 bg-gray-200 rounded"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!module) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">모듈을 찾을 수 없습니다</h1>
          <p className="text-gray-600 mb-4">요청하신 모듈이 존재하지 않거나 삭제되었습니다.</p>
          <Button onClick={() => window.history.back()}>뒤로 가기</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* 헤더 */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold mb-2">{module.name}</h1>
            <p className="text-gray-600">{module.description}</p>
          </div>
          <div className="flex gap-2">
            {!module.is_installed ? (
              <Button onClick={installModule} className="bg-blue-600 hover:bg-blue-700">
                설치하기
              </Button>
            ) : (
              <Button 
                onClick={toggleModuleStatus}
                variant={module.is_activated ? 'destructive' : 'default'}
              >
                {module.is_activated ? '비활성화' : '활성화'}
              </Button>
            )}
          </div>
        </div>
        
        {/* 모듈 메타데이터 */}
        <div className="flex flex-wrap gap-4 text-sm text-gray-600">
          <div className="flex items-center gap-1">
            <User className="w-4 h-4" />
            {module.author}
          </div>
          <div className="flex items-center gap-1">
            <Calendar className="w-4 h-4" />
            {formatDate(module.created_at)}
          </div>
          <div className="flex items-center gap-1">
            <Download className="w-4 h-4" />
            {formatNumber(module.downloads)} 다운로드
          </div>
          <div className="flex items-center gap-1">
            {renderStars(module.rating)}
            <span>{module.rating.toFixed(1)}</span>
          </div>
          <Badge variant={module.price === 0 ? 'default' : 'secondary'}>
            {module.price === 0 ? '무료' : `${module.price}원`}
          </Badge>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">개요</TabsTrigger>
          <TabsTrigger value="reviews">리뷰 ({reviews.length})</TabsTrigger>
          <TabsTrigger value="settings">설정</TabsTrigger>
          <TabsTrigger value="requirements">요구사항</TabsTrigger>
        </TabsList>

        {/* 개요 탭 */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
              {/* 기능 목록 */}
              <Card>
                <CardHeader>
                  <CardTitle>주요 기능</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {module.features.map((feature, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                        <span>{feature}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* 스크린샷 */}
              {module.screenshots && module.screenshots.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>스크린샷</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {module.screenshots.map((screenshot, index) => (
                        <img
                          key={index}
                          src={screenshot}
                          alt={`스크린샷 ${index + 1}`}
                          className="rounded-lg border"
                        />
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>

            <div className="space-y-6">
              {/* 태그 */}
              <Card>
                <CardHeader>
                  <CardTitle>태그</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {module.tags.map((tag) => (
                      <Badge key={tag} variant="outline">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* 버전 정보 */}
              <Card>
                <CardHeader>
                  <CardTitle>버전 정보</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>버전:</span>
                      <span className="font-medium">{module.version}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>카테고리:</span>
                      <span className="font-medium">{module.category}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>상태:</span>
                      <Badge variant={module.status === 'active' ? 'default' : 'secondary'}>
                        {module.status}
                      </Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* 리뷰 탭 */}
        <TabsContent value="reviews" className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold">사용자 리뷰</h2>
            <Button onClick={() => setShowReviewForm(!showReviewForm)}>
              <MessageSquare className="w-4 h-4 mr-2" />
              리뷰 작성
            </Button>
          </div>

          {/* 리뷰 작성 폼 */}
          {showReviewForm && (
            <Card>
              <CardHeader>
                <CardTitle>리뷰 작성</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">평점</label>
                  <div className="flex gap-1">
                    {Array.from({ length: 5 }, (_, i) => (
                      <button
                        key={i}
                        onClick={() => setNewReview(prev => ({ ...prev, rating: i + 1 }))}
                        className="p-1"
                      >
                        <Star
                          className={`w-6 h-6 ${
                            i < newReview.rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
                          }`}
                        />
                      </button>
                    ))}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">리뷰 내용</label>
                  <Textarea
                    value={newReview.comment}
                    onChange={(e) => setNewReview(prev => ({ ...prev, comment: e.target.value }))}
                    placeholder="이 모듈에 대한 리뷰를 작성해주세요..."
                    rows={4}
                  />
                </div>
                <div className="flex gap-2">
                  <Button onClick={submitReview}>리뷰 등록</Button>
                  <Button variant="outline" onClick={() => setShowReviewForm(false)}>
                    취소
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* 리뷰 목록 */}
          <div className="space-y-4">
            {reviews.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                아직 리뷰가 없습니다. 첫 번째 리뷰를 작성해보세요!
              </div>
            ) : (
              reviews.map((review) => (
                <Card key={review.id}>
                  <CardContent className="pt-6">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <div className="flex items-center gap-2 mb-2">
                          <span className="font-medium">{review.user_name}</span>
                          <div className="flex items-center gap-1">
                            {renderStars(review.rating)}
                          </div>
                        </div>
                        <p className="text-sm text-gray-500">
                          {formatDate(review.created_at)}
                        </p>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-500">
                        <button className="flex items-center gap-1 hover:text-blue-600">
                          <ThumbsUp className="w-4 h-4" />
                          {review.helpful_count}
                        </button>
                      </div>
                    </div>
                    <p className="text-gray-700">{review.comment}</p>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </TabsContent>

        {/* 설정 탭 */}
        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="w-5 h-5" />
                모듈 설정
              </CardTitle>
              <CardDescription>
                모듈의 동작을 커스터마이징할 수 있습니다.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {Object.keys(config).length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  설정 가능한 옵션이 없습니다.
                </div>
              ) : (
                <div className="space-y-4">
                  {Object.entries(config).map(([key, value]) => (
                    <div key={key} className="space-y-2">
                      <label className="block text-sm font-medium">{key}</label>
                      {typeof value === 'boolean' ? (
                        <input
                          type="checkbox"
                          checked={value as boolean}
                          onChange={(e) => setConfig(prev => ({ ...prev, [key]: e.target.checked }))}
                          className="rounded"
                        />
                      ) : typeof value === 'number' ? (
                        <Input
                          type="number"
                          value={value as number}
                          onChange={(e) => setConfig(prev => ({ ...prev, [key]: Number(e.target.value) }))}
                        />
                      ) : (
                        <Input
                          value={value as string}
                          onChange={(e) => setConfig(prev => ({ ...prev, [key]: e.target.value }))}
                        />
                      )}
                    </div>
                  ))}
                  <Button className="mt-4">설정 저장</Button>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* 요구사항 탭 */}
        <TabsContent value="requirements" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>시스템 요구사항</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Python 버전 */}
              <div>
                <h3 className="font-medium mb-2">Python 버전</h3>
                <Badge variant="outline">{module.requirements.python_version}</Badge>
              </div>

              {/* 의존성 */}
              <div>
                <h3 className="font-medium mb-2">필요한 패키지</h3>
                <div className="space-y-1">
                  {module.requirements.dependencies.map((dep, index) => (
                    <Badge key={index} variant="secondary" className="mr-2">
                      {dep}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* 권한 */}
              <div>
                <h3 className="font-medium mb-2">필요한 권한</h3>
                <div className="space-y-1">
                  {module.requirements.permissions.map((permission, index) => (
                    <Badge key={index} variant="outline" className="mr-2">
                      {permission}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
} 
'use client';

import React, { useState } from 'react';
import { useBrands } from '@/hooks/useDashboard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Building, Users, TrendingUp, Plus } from 'lucide-react';
import { toast } from 'sonner';

export default function BrandsPage() {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [newBrand, setNewBrand] = useState({
    name: '',
    description: '',
    industry: ''
  });

  // API 훅 사용
  const { brands, loading, error, refetch } = useBrands(1, 100);

  const handleCreateBrand = async () => {
    if (!newBrand.name || !newBrand.description) {
      toast.error('필수 정보를 모두 입력해주세요.');
      return;
    }

    try {
      // TODO: 실제 API 호출 구현
      toast.success('브랜드가 생성되었습니다.');
      setNewBrand({ name: '', description: '', industry: '' });
      setIsCreateDialogOpen(false);
      refetch();
    } catch (error) {
      console.error('브랜드 생성 실패:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">브랜드 정보를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-red-500">브랜드 정보를 불러오는데 실패했습니다.</p>
          <Button onClick={() => refetch()} className="mt-4">
            다시 시도
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* 헤더 */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">브랜드 관리</h1>
            <p className="text-gray-600 mt-1">등록된 브랜드 목록을 확인하고 관리하세요.</p>
          </div>
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button className="flex items-center gap-2">
                <Plus className="h-4 w-4" />
                새 브랜드 추가
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>새 브랜드 추가</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="name">브랜드명 *</Label>
                  <Input
                    id="name"
                    value={newBrand.name}
                    onChange={(e) => setNewBrand({ ...newBrand, name: e.target.value })}
                    placeholder="브랜드명을 입력하세요"
                  />
                </div>
                <div>
                  <Label htmlFor="description">설명 *</Label>
                  <Input
                    id="description"
                    value={newBrand.description}
                    onChange={(e) => setNewBrand({ ...newBrand, description: e.target.value })}
                    placeholder="브랜드 설명을 입력하세요"
                  />
                </div>
                <div>
                  <Label htmlFor="industry">업종</Label>
                  <Input
                    id="industry"
                    value={newBrand.industry}
                    onChange={(e) => setNewBrand({ ...newBrand, industry: e.target.value })}
                    placeholder="업종을 입력하세요"
                  />
                </div>
                <div className="flex gap-2 justify-end">
                  <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                    취소
                  </Button>
                  <Button onClick={handleCreateBrand}>
                    생성
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {/* 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">총 브랜드</CardTitle>
              <Building className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{brands.length}</div>
              <p className="text-xs text-muted-foreground">
                활성 브랜드 수
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">총 매장</CardTitle>
              <Building className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {brands.reduce((total: number, brand: any) => total + (brand.store_count || 0), 0)}
              </div>
              <p className="text-xs text-muted-foreground">
                전체 매장 수
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">총 직원</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {brands.reduce((total: number, brand: any) => total + (brand.employee_count || 0), 0)}
              </div>
              <p className="text-xs text-muted-foreground">
                전체 직원 수
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">총 매출</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                ₩{brands.reduce((total: number, brand: any) => total + (brand.total_revenue || 0), 0).toLocaleString()}
              </div>
              <p className="text-xs text-muted-foreground">
                전체 브랜드 합계
              </p>
            </CardContent>
          </Card>
        </div>

        {/* 브랜드 목록 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {brands.map((brand: any) => (
            <Card key={brand.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-lg">{brand.name}</CardTitle>
                    <p className="text-sm text-gray-600">{brand.description}</p>
                  </div>
                  <Badge variant={brand.status === 'active' ? 'default' : 'secondary'}>
                    {brand.status === 'active' ? '활성' : '비활성'}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">매장 수:</span>
                    <span className="font-medium">{brand.store_count || 0}개</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">직원 수:</span>
                    <span className="font-medium">{brand.employee_count || 0}명</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">총 매출:</span>
                    <span className="font-medium">₩{(brand.total_revenue || 0).toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">등록일:</span>
                    <span className="font-medium">
                      {new Date(brand.created_at).toLocaleDateString('ko-KR')}
                    </span>
                  </div>
                </div>
                <div className="mt-4 flex gap-2">
                  <Button variant="outline" size="sm" className="flex-1">
                    상세보기
                  </Button>
                  <Button variant="outline" size="sm" className="flex-1">
                    매장 관리
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {brands.length === 0 && (
          <Card>
            <CardContent className="p-12 text-center">
              <Building className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">등록된 브랜드가 없습니다</h3>
              <p className="text-gray-600 mb-4">
                첫 번째 브랜드를 등록해보세요.
              </p>
              <Button onClick={() => setIsCreateDialogOpen(true)}>
                <Plus className="h-4 w-4 mr-2" />
                새 브랜드 추가
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
} 
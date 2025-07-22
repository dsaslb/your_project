'use client';

import React, { useState } from 'react';
import { useBranches, useBrands } from '../../../src/hooks/useApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Building, Users, Phone, MapPin, Calendar, TrendingUp } from 'lucide-react';
import { toast } from 'sonner';

export default function BranchesPage() {
  const [selectedBrandId, setSelectedBrandId] = useState<string>('');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [newBranch, setNewBranch] = useState({
    name: '',
    address: '',
    phone: '',
    manager: '',
    brand_id: ''
  });

  // API 훅 사용
  const { data: brandsData } = useBrands();
  const { data: branchesData, isLoading, error, refetch } = useBranches(selectedBrandId);

  const brands = brandsData?.data || [];
  const branches = branchesData?.data || [];

  const handleCreateBranch = async () => {
    if (!newBranch.name || !newBranch.address || !newBranch.brand_id) {
      toast.error('필수 정보를 모두 입력해주세요.');
      return;
    }

    try {
      // TODO: 실제 API 호출 구현
      toast.success('매장이 생성되었습니다.');
      setNewBranch({ name: '', address: '', phone: '', manager: '', brand_id: '' });
      setIsCreateDialogOpen(false);
    } catch (error) {
      console.error('매장 생성 실패:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">매장 정보를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-red-500">매장 정보를 불러오는데 실패했습니다.</p>
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
            <h1 className="text-3xl font-bold text-gray-900">매장 관리</h1>
            <p className="text-gray-600 mt-1">등록된 매장 목록을 확인하고 관리하세요.</p>
          </div>
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button className="flex items-center gap-2">
                <Building className="h-4 w-4" />
                새 매장 추가
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>새 매장 추가</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="brand">브랜드 *</Label>
                  <Select value={newBranch.brand_id} onValueChange={(value) => setNewBranch({ ...newBranch, brand_id: value })}>
                    <SelectTrigger>
                      <SelectValue placeholder="브랜드를 선택하세요" />
                    </SelectTrigger>
                    <SelectContent>
                      {brands.map((brand: any) => (
                        <SelectItem key={brand.id} value={brand.id}>
                          {brand.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="name">매장명 *</Label>
                  <Input
                    id="name"
                    value={newBranch.name}
                    onChange={(e) => setNewBranch({ ...newBranch, name: e.target.value })}
                    placeholder="매장명을 입력하세요"
                  />
                </div>
                <div>
                  <Label htmlFor="address">주소 *</Label>
                  <Input
                    id="address"
                    value={newBranch.address}
                    onChange={(e) => setNewBranch({ ...newBranch, address: e.target.value })}
                    placeholder="매장 주소를 입력하세요"
                  />
                </div>
                <div>
                  <Label htmlFor="phone">전화번호</Label>
                  <Input
                    id="phone"
                    value={newBranch.phone}
                    onChange={(e) => setNewBranch({ ...newBranch, phone: e.target.value })}
                    placeholder="전화번호를 입력하세요"
                  />
                </div>
                <div>
                  <Label htmlFor="manager">매니저</Label>
                  <Input
                    id="manager"
                    value={newBranch.manager}
                    onChange={(e) => setNewBranch({ ...newBranch, manager: e.target.value })}
                    placeholder="매니저 이름을 입력하세요"
                  />
                </div>
                <div className="flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                    취소
                  </Button>
                  <Button onClick={handleCreateBranch}>
                    생성
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {/* 필터 */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex gap-4">
              <div className="flex-1">
                <Label htmlFor="brand-filter">브랜드 필터</Label>
                <Select value={selectedBrandId} onValueChange={setSelectedBrandId}>
                  <SelectTrigger>
                    <SelectValue placeholder="모든 브랜드" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">모든 브랜드</SelectItem>
                    {brands.map((brand: any) => (
                      <SelectItem key={brand.id} value={brand.id}>
                        {brand.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">총 매장</CardTitle>
              <Building className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{branches.length}</div>
              <p className="text-xs text-muted-foreground">
                활성 매장 수
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
                {branches.reduce((total: number, branch: any) => total + (branch.employee_count || 0), 0)}
              </div>
              <p className="text-xs text-muted-foreground">
                전체 직원 수
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">평균 매출</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {branches.length > 0 
                  ? (branches.reduce((total: number, branch: any) => total + (branch.monthly_sales || 0), 0) / branches.length).toLocaleString()
                  : 0
                }원
              </div>
              <p className="text-xs text-muted-foreground">
                매장당 평균
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">신규 매장</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {branches.filter((branch: any) => {
                  const createdDate = new Date(branch.created_at);
                  const thirtyDaysAgo = new Date();
                  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
                  return createdDate > thirtyDaysAgo;
                }).length}
              </div>
              <p className="text-xs text-muted-foreground">
                최근 30일
              </p>
            </CardContent>
          </Card>
        </div>

        {/* 매장 목록 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {branches.map((branch: any) => (
            <Card key={branch.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-lg">{branch.name}</CardTitle>
                    <p className="text-sm text-gray-600">
                      {brands.find((brand: any) => brand.id === branch.brand_id)?.name || '알 수 없는 브랜드'}
                    </p>
                  </div>
                  <Badge variant={branch.status === 'active' ? 'default' : 'secondary'}>
                    {branch.status === 'active' ? '활성' : '비활성'}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <MapPin className="h-4 w-4" />
                    <span className="truncate">{branch.address}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Phone className="h-4 w-4" />
                    <span>{branch.phone || '전화번호 없음'}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Users className="h-4 w-4" />
                    <span>매니저: {branch.manager || '미지정'}</span>
                  </div>
                </div>
                <div className="mt-4 space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">직원 수:</span>
                    <span className="font-medium">{branch.employee_count || 0}명</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">이번 달 매출:</span>
                    <span className="font-medium">
                      {(branch.monthly_sales || 0).toLocaleString()}원
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">등록일:</span>
                    <span className="font-medium">
                      {new Date(branch.created_at).toLocaleDateString('ko-KR')}
                    </span>
                  </div>
                </div>
                <div className="mt-4 flex gap-2">
                  <Button variant="outline" size="sm" className="flex-1">
                    상세보기
                  </Button>
                  <Button variant="outline" size="sm" className="flex-1">
                    직원 관리
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* 빈 상태 */}
        {branches.length === 0 && (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Building className="h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">등록된 매장이 없습니다</h3>
              <p className="text-gray-600 mb-4">
                {selectedBrandId 
                  ? '선택한 브랜드에 등록된 매장이 없습니다.' 
                  : '새 매장을 추가하여 시작하세요.'
                }
              </p>
              <Button onClick={() => setIsCreateDialogOpen(true)}>
                <Building className="h-4 w-4 mr-2" />
                첫 번째 매장 추가
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
} 
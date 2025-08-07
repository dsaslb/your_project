'use client';

import React, { useState } from 'react';
import { useBrands, useStores } from '@/hooks/useDashboard';
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
  const [selectedBrandId, setSelectedBrandId] = useState<string>('all');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [newBranch, setNewBranch] = useState({
    name: '',
    address: '',
    phone: '',
    manager: '',
    brand_id: ''
  });

  // API 훅 사용
  const { brands } = useBrands(1, 100);
  const { stores: branches, loading: isLoading, error, refetch } = useStores(1, 100, '', '', selectedBrandId && selectedBrandId !== 'all' ? parseInt(selectedBrandId) : undefined);

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
                        <SelectItem key={brand.id} value={brand.id.toString()}>
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
                  <Label htmlFor="manager">매장장</Label>
                  <Input
                    id="manager"
                    value={newBranch.manager}
                    onChange={(e) => setNewBranch({ ...newBranch, manager: e.target.value })}
                    placeholder="매장장 이름을 입력하세요"
                  />
                </div>
                <div className="flex gap-2 justify-end">
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

        {/* 브랜드 필터 */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <Label htmlFor="brand-filter">브랜드 필터:</Label>
              <Select value={selectedBrandId} onValueChange={setSelectedBrandId}>
                <SelectTrigger className="w-64">
                  <SelectValue placeholder="전체 브랜드" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">전체 브랜드</SelectItem>
                  {brands.map((brand: any) => (
                    <SelectItem key={brand.id} value={brand.id.toString()}>
                      {brand.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* 매장 목록 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {branches.map((branch: any) => (
            <Card key={branch.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-lg">{branch.name}</CardTitle>
                    <p className="text-sm text-gray-600">{branch.description}</p>
                  </div>
                  <Badge variant={branch.status === 'active' ? 'default' : 'secondary'}>
                    {branch.status === 'active' ? '운영중' : '비활성'}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center gap-2 text-sm">
                  <MapPin className="h-4 w-4 text-gray-500" />
                  <span>{branch.address}</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Phone className="h-4 w-4 text-gray-500" />
                  <span>{branch.phone}</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Users className="h-4 w-4 text-gray-500" />
                  <span>{branch.employee_count}명</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <TrendingUp className="h-4 w-4 text-gray-500" />
                  <span>₩{branch.total_revenue?.toLocaleString() || '0'}</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Calendar className="h-4 w-4 text-gray-500" />
                  <span>{new Date(branch.created_at).toLocaleDateString()}</span>
                </div>
                <div className="flex gap-2 pt-2">
                  <Button variant="outline" size="sm" className="flex-1">
                    수정
                  </Button>
                  <Button variant="outline" size="sm" className="flex-1">
                    삭제
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {branches.length === 0 && (
          <Card>
            <CardContent className="p-12 text-center">
              <Building className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">등록된 매장이 없습니다</h3>
              <p className="text-gray-600 mb-4">
                첫 번째 매장을 등록해보세요.
              </p>
              <Button onClick={() => setIsCreateDialogOpen(true)}>
                <Building className="h-4 w-4 mr-2" />
                새 매장 추가
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
} 
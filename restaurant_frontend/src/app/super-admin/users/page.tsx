'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/apiClient';
import { SuperAdminOnly } from '@/components/auth/PermissionGuard';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table';
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogFooter, 
  DialogHeader, 
  DialogTitle, 
  DialogTrigger 
} from '@/components/ui/dialog';
import { 
  Users, 
  Search, 
  Filter, 
  MoreHorizontal, 
  CheckCircle, 
  XCircle,
  Edit,
  Trash2,
  Eye
} from 'lucide-react';
import { toast } from 'sonner';

// 사용자 데이터 타입
interface User {
  id: number;
  username: string;
  name: string;
  email: string;
  role: string;
  branch_id?: number;
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

interface UsersResponse {
  users: User[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
  };
}

// 사용자 목록 조회 훅
const useUsers = (params: Record<string, any> = {}) => {
  return useQuery({
    queryKey: ['super-admin', 'users', params],
    queryFn: async () => {
      const response = await apiClient.get<UsersResponse>('/api/super-admin/users', params);
      if (!response.success) {
        throw new Error(response.error || '사용자 목록을 불러올 수 없습니다.');
      }
      return response.data;
    },
    staleTime: 30 * 1000,
  });
};

// 사용자 상태 변경 훅
const useUpdateUserStatus = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ userId, action }: { userId: number; action: 'approve' | 'block' }) => {
      const response = await apiClient.put(`/api/super-admin/users/${userId}/status`, { action });
      if (!response.success) {
        throw new Error(response.error || '사용자 상태 변경에 실패했습니다.');
      }
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['super-admin', 'users'] });
      toast.success('사용자 상태가 변경되었습니다.');
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });
};

// 역할별 배지 색상
const getRoleBadgeVariant = (role: string) => {
  switch (role) {
    case 'super_admin':
      return 'default';
    case 'brand_manager':
      return 'secondary';
    case 'store_manager':
      return 'outline';
    case 'employee':
      return 'destructive';
    default:
      return 'outline';
  }
};

// 상태별 배지 색상
const getStatusBadgeVariant = (isActive: boolean) => {
  return isActive ? 'default' : 'destructive';
};

// 사용자 관리 페이지 메인 컴포넌트
const UsersManagement = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [isUserDetailOpen, setIsUserDetailOpen] = useState(false);

  const updateUserStatus = useUpdateUserStatus();

  // 필터링된 파라미터
  const queryParams = {
    page: currentPage,
    per_page: 20,
    search: searchTerm || undefined,
    role: roleFilter || undefined,
    status: statusFilter || undefined,
  };

  const { data, isLoading, error } = useUsers(queryParams);

  // 사용자 상태 변경 핸들러
  const handleStatusChange = (userId: number, action: 'approve' | 'block') => {
    updateUserStatus.mutate({ userId, action });
  };

  // 사용자 상세 정보 모달
  const openUserDetail = (user: User) => {
    setSelectedUser(user);
    setIsUserDetailOpen(true);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">사용자 목록을 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <XCircle className="h-8 w-8 text-red-500 mx-auto mb-4" />
          <p className="text-red-500 mb-4">사용자 목록을 불러올 수 없습니다.</p>
          <Button onClick={() => window.location.reload()}>다시 시도</Button>
        </div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <SuperAdminOnly>
      <div className="space-y-6">
        {/* 헤더 */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">사용자 관리</h1>
            <p className="text-muted-foreground">
              전체 사용자 승인, 차단, 권한 관리
            </p>
          </div>
          <Button>
            <Users className="h-4 w-4 mr-2" />
            새 사용자 등록
          </Button>
        </div>

        {/* 필터 및 검색 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Filter className="h-5 w-5" />
              필터 및 검색
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="사용자명, 이메일 검색..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Select value={roleFilter} onValueChange={setRoleFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="역할 선택" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">모든 역할</SelectItem>
                  <SelectItem value="super_admin">슈퍼 관리자</SelectItem>
                  <SelectItem value="brand_manager">브랜드 관리자</SelectItem>
                  <SelectItem value="store_manager">매장 관리자</SelectItem>
                  <SelectItem value="employee">직원</SelectItem>
                </SelectContent>
              </Select>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="상태 선택" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">모든 상태</SelectItem>
                  <SelectItem value="active">활성</SelectItem>
                  <SelectItem value="inactive">비활성</SelectItem>
                </SelectContent>
              </Select>
              <Button 
                variant="outline" 
                onClick={() => {
                  setSearchTerm('');
                  setRoleFilter('');
                  setStatusFilter('');
                  setCurrentPage(1);
                }}
              >
                필터 초기화
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* 사용자 목록 */}
        <Card>
          <CardHeader>
            <CardTitle>사용자 목록</CardTitle>
            <CardDescription>
              총 {data.pagination.total}명의 사용자 (페이지 {data.pagination.page}/{data.pagination.pages})
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>사용자</TableHead>
                  <TableHead>역할</TableHead>
                  <TableHead>상태</TableHead>
                  <TableHead>가입일</TableHead>
                  <TableHead>최근 로그인</TableHead>
                  <TableHead>작업</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.users.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>
                      <div>
                        <div className="font-medium">{user.name}</div>
                        <div className="text-sm text-muted-foreground">
                          @{user.username} • {user.email}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant={getRoleBadgeVariant(user.role)}>
                        {user.role === 'super_admin' && '슈퍼 관리자'}
                        {user.role === 'brand_manager' && '브랜드 관리자'}
                        {user.role === 'store_manager' && '매장 관리자'}
                        {user.role === 'employee' && '직원'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={getStatusBadgeVariant(user.is_active)}>
                        {user.is_active ? '활성' : '비활성'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {new Date(user.created_at).toLocaleDateString('ko-KR')}
                    </TableCell>
                    <TableCell>
                      {user.last_login 
                        ? new Date(user.last_login).toLocaleDateString('ko-KR')
                        : '로그인 기록 없음'
                      }
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => openUserDetail(user)}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {/* 편집 기능 */}}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        {user.is_active ? (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleStatusChange(user.id, 'block')}
                            disabled={updateUserStatus.isPending}
                          >
                            <XCircle className="h-4 w-4 text-red-500" />
                          </Button>
                        ) : (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleStatusChange(user.id, 'approve')}
                            disabled={updateUserStatus.isPending}
                          >
                            <CheckCircle className="h-4 w-4 text-green-500" />
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>

            {/* 페이지네이션 */}
            {data.pagination.pages > 1 && (
              <div className="flex items-center justify-between mt-4">
                <div className="text-sm text-muted-foreground">
                  {data.pagination.total}개 중 {(data.pagination.page - 1) * data.pagination.per_page + 1}-
                  {Math.min(data.pagination.page * data.pagination.per_page, data.pagination.total)}개 표시
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(currentPage - 1)}
                    disabled={currentPage === 1}
                  >
                    이전
                  </Button>
                  <span className="text-sm">
                    {data.pagination.page} / {data.pagination.pages}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(currentPage + 1)}
                    disabled={currentPage === data.pagination.pages}
                  >
                    다음
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* 사용자 상세 정보 모달 */}
        <Dialog open={isUserDetailOpen} onOpenChange={setIsUserDetailOpen}>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>사용자 상세 정보</DialogTitle>
              <DialogDescription>
                선택한 사용자의 상세 정보를 확인합니다.
              </DialogDescription>
            </DialogHeader>
            {selectedUser && (
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium">이름</label>
                  <p className="text-sm text-muted-foreground">{selectedUser.name}</p>
                </div>
                <div>
                  <label className="text-sm font-medium">사용자명</label>
                  <p className="text-sm text-muted-foreground">@{selectedUser.username}</p>
                </div>
                <div>
                  <label className="text-sm font-medium">이메일</label>
                  <p className="text-sm text-muted-foreground">{selectedUser.email}</p>
                </div>
                <div>
                  <label className="text-sm font-medium">역할</label>
                  <Badge variant={getRoleBadgeVariant(selectedUser.role)} className="mt-1">
                    {selectedUser.role === 'super_admin' && '슈퍼 관리자'}
                    {selectedUser.role === 'brand_manager' && '브랜드 관리자'}
                    {selectedUser.role === 'store_manager' && '매장 관리자'}
                    {selectedUser.role === 'employee' && '직원'}
                  </Badge>
                </div>
                <div>
                  <label className="text-sm font-medium">상태</label>
                  <Badge variant={getStatusBadgeVariant(selectedUser.is_active)} className="mt-1">
                    {selectedUser.is_active ? '활성' : '비활성'}
                  </Badge>
                </div>
                <div>
                  <label className="text-sm font-medium">가입일</label>
                  <p className="text-sm text-muted-foreground">
                    {new Date(selectedUser.created_at).toLocaleString('ko-KR')}
                  </p>
                </div>
                {selectedUser.last_login && (
                  <div>
                    <label className="text-sm font-medium">최근 로그인</label>
                    <p className="text-sm text-muted-foreground">
                      {new Date(selectedUser.last_login).toLocaleString('ko-KR')}
                    </p>
                  </div>
                )}
              </div>
            )}
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsUserDetailOpen(false)}>
                닫기
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </SuperAdminOnly>
  );
};

export default UsersManagement; 
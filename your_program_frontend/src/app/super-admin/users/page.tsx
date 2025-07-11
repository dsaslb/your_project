'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
// Toast 기능은 나중에 구현
const useToast = () => ({
  toast: (props: any) => {
    if (props.variant === 'destructive') {
      alert(`❌ ${props.title}: ${props.description}`);
    } else {
      alert(`✅ ${props.title}: ${props.description}`);
    }
  }
});

interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  status: string;
  branch_id?: number;
  created_at: string;
  last_login?: string;
}

export default function SuperAdminUsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      // TODO: 실제 API 호출로 변경
      const mockUsers: User[] = [
        {
          id: 1,
          username: 'admin',
          email: 'admin@restaurant.com',
          role: 'super_admin',
          status: 'approved',
          created_at: '2024-01-01T00:00:00Z',
          last_login: '2024-07-11T10:30:00Z'
        },
        {
          id: 2,
          username: 'manager1',
          email: 'manager1@restaurant.com',
          role: 'manager',
          status: 'approved',
          branch_id: 1,
          created_at: '2024-01-15T00:00:00Z',
          last_login: '2024-07-11T09:15:00Z'
        },
        {
          id: 3,
          username: 'employee1',
          email: 'employee1@restaurant.com',
          role: 'employee',
          status: 'pending',
          branch_id: 1,
          created_at: '2024-07-10T00:00:00Z'
        },
        {
          id: 4,
          username: 'teamlead1',
          email: 'teamlead1@restaurant.com',
          role: 'teamlead',
          status: 'approved',
          branch_id: 1,
          created_at: '2024-02-01T00:00:00Z',
          last_login: '2024-07-10T18:45:00Z'
        }
      ];
      setUsers(mockUsers);
    } catch (error) {
      toast({
        title: "오류",
        description: "사용자 목록을 불러오는데 실패했습니다.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = roleFilter === 'all' || user.role === roleFilter;
    const matchesStatus = statusFilter === 'all' || user.status === statusFilter;
    
    return matchesSearch && matchesRole && matchesStatus;
  });

  const handleStatusChange = async (userId: number, newStatus: string) => {
    try {
      // TODO: 실제 API 호출로 변경
      setUsers(prev => prev.map(user => 
        user.id === userId ? { ...user, status: newStatus } : user
      ));
      
      toast({
        title: "성공",
        description: "사용자 상태가 변경되었습니다.",
      });
    } catch (error) {
      toast({
        title: "오류",
        description: "상태 변경에 실패했습니다.",
        variant: "destructive",
      });
    }
  };

  const handleRoleChange = async (userId: number, newRole: string) => {
    try {
      // TODO: 실제 API 호출로 변경
      setUsers(prev => prev.map(user => 
        user.id === userId ? { ...user, role: newRole } : user
      ));
      
      toast({
        title: "성공",
        description: "사용자 역할이 변경되었습니다.",
      });
    } catch (error) {
      toast({
        title: "오류",
        description: "역할 변경에 실패했습니다.",
        variant: "destructive",
      });
    }
  };

  const getRoleLabel = (role: string) => {
    const roleLabels: { [key: string]: string } = {
      'super_admin': '최고관리자',
      'admin': '관리자',
      'manager': '매니저',
      'teamlead': '팀리드',
      'employee': '직원'
    };
    return roleLabels[role] || role;
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      'approved': { label: '승인됨', variant: 'default' as const },
      'pending': { label: '대기중', variant: 'secondary' as const },
      'blocked': { label: '차단됨', variant: 'destructive' as const }
    };
    
    const config = statusConfig[status as keyof typeof statusConfig] || { label: status, variant: 'outline' as const };
    
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  const getRoleBadge = (role: string) => {
    const roleConfig = {
      'super_admin': { variant: 'default' as const },
      'admin': { variant: 'secondary' as const },
      'manager': { variant: 'outline' as const },
      'teamlead': { variant: 'outline' as const },
      'employee': { variant: 'outline' as const }
    };
    
    const config = roleConfig[role as keyof typeof roleConfig] || { variant: 'outline' as const };
    
    return <Badge variant={config.variant}>{getRoleLabel(role)}</Badge>;
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          <div className="space-y-2">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-16 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">사용자 관리</h1>
          <p className="text-gray-600">시스템의 모든 사용자를 관리하고 권한을 설정할 수 있습니다.</p>
        </div>

        {/* 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">전체 사용자</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{users.length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">승인된 사용자</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{users.filter(u => u.status === 'approved').length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">대기중</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{users.filter(u => u.status === 'pending').length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">차단된 사용자</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{users.filter(u => u.status === 'blocked').length}</div>
            </CardContent>
          </Card>
        </div>

        {/* 필터 */}
        <Card className="mb-6">
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="text-sm font-medium mb-2 block">검색</label>
                <Input
                  placeholder="사용자명 또는 이메일로 검색..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">역할</label>
                <Select value={roleFilter} onValueChange={setRoleFilter}>
                  <SelectTrigger>
                    <SelectValue placeholder="모든 역할" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">모든 역할</SelectItem>
                    <SelectItem value="super_admin">최고관리자</SelectItem>
                    <SelectItem value="admin">관리자</SelectItem>
                    <SelectItem value="manager">매니저</SelectItem>
                    <SelectItem value="teamlead">팀리드</SelectItem>
                    <SelectItem value="employee">직원</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">상태</label>
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger>
                    <SelectValue placeholder="모든 상태" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">모든 상태</SelectItem>
                    <SelectItem value="approved">승인됨</SelectItem>
                    <SelectItem value="pending">대기중</SelectItem>
                    <SelectItem value="blocked">차단됨</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 사용자 테이블 */}
        <Card>
          <CardHeader>
            <CardTitle>사용자 목록</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>사용자명</TableHead>
                  <TableHead>이메일</TableHead>
                  <TableHead>역할</TableHead>
                  <TableHead>상태</TableHead>
                  <TableHead>가입일</TableHead>
                  <TableHead>마지막 로그인</TableHead>
                  <TableHead>작업</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredUsers.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell className="font-medium">{user.username}</TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>{getRoleBadge(user.role)}</TableCell>
                    <TableCell>{getStatusBadge(user.status)}</TableCell>
                    <TableCell>{new Date(user.created_at).toLocaleDateString('ko-KR')}</TableCell>
                    <TableCell>
                      {user.last_login 
                        ? new Date(user.last_login).toLocaleString('ko-KR')
                        : '로그인 기록 없음'
                      }
                    </TableCell>
                    <TableCell>
                      <div className="flex space-x-2">
                        <Dialog>
                          <DialogTrigger asChild>
                            <Button 
                              variant="outline" 
                              size="sm"
                              onClick={() => setSelectedUser(user)}
                            >
                              편집
                            </Button>
                          </DialogTrigger>
                          <DialogContent>
                            <DialogHeader>
                              <DialogTitle>사용자 편집</DialogTitle>
                            </DialogHeader>
                            <div className="space-y-4">
                              <div>
                                <label className="text-sm font-medium">역할</label>
                                <Select 
                                  value={user.role} 
                                  onValueChange={(value) => handleRoleChange(user.id, value)}
                                >
                                  <SelectTrigger>
                                    <SelectValue />
                                  </SelectTrigger>
                                  <SelectContent>
                                    <SelectItem value="super_admin">최고관리자</SelectItem>
                                    <SelectItem value="admin">관리자</SelectItem>
                                    <SelectItem value="manager">매니저</SelectItem>
                                    <SelectItem value="teamlead">팀리드</SelectItem>
                                    <SelectItem value="employee">직원</SelectItem>
                                  </SelectContent>
                                </Select>
                              </div>
                              <div>
                                <label className="text-sm font-medium">상태</label>
                                <Select 
                                  value={user.status} 
                                  onValueChange={(value) => handleStatusChange(user.id, value)}
                                >
                                  <SelectTrigger>
                                    <SelectValue />
                                  </SelectTrigger>
                                  <SelectContent>
                                    <SelectItem value="approved">승인됨</SelectItem>
                                    <SelectItem value="pending">대기중</SelectItem>
                                    <SelectItem value="blocked">차단됨</SelectItem>
                                  </SelectContent>
                                </Select>
                              </div>
                            </div>
                          </DialogContent>
                        </Dialog>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            
            {filteredUsers.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                검색 조건에 맞는 사용자가 없습니다.
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 
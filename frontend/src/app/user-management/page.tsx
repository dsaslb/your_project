"use client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { 
  Users, 
  UserPlus, 
  Search, 
  Filter,
  MoreHorizontal,
  Edit,
  Trash2,
  Shield,
  CheckCircle,
  XCircle
} from "lucide-react";

export default function UserManagement() {
  // 더미 데이터
  const users = [
    {
      id: 1,
      name: "김철수",
      email: "kim@example.com",
      role: "store_manager",
      store: "강남점",
      status: "active",
      lastLogin: "2024-01-15 14:30",
      createdAt: "2024-01-01"
    },
    {
      id: 2,
      name: "이영희",
      email: "lee@example.com",
      role: "employee",
      store: "홍대점",
      status: "pending",
      lastLogin: "2024-01-14 09:15",
      createdAt: "2024-01-05"
    },
    {
      id: 3,
      name: "박민수",
      email: "park@example.com",
      role: "brand_admin",
      store: "전체",
      status: "active",
      lastLogin: "2024-01-15 16:45",
      createdAt: "2023-12-15"
    },
    {
      id: 4,
      name: "정수진",
      email: "jung@example.com",
      role: "employee",
      store: "부산점",
      status: "inactive",
      lastLogin: "2024-01-10 11:20",
      createdAt: "2024-01-08"
    },
    {
      id: 5,
      name: "최동현",
      email: "choi@example.com",
      role: "store_manager",
      store: "대구점",
      status: "active",
      lastLogin: "2024-01-15 13:10",
      createdAt: "2023-11-20"
    }
  ];

  const getRoleLabel = (role: string) => {
    switch (role) {
      case "super_admin": return "슈퍼 관리자";
      case "brand_admin": return "브랜드 관리자";
      case "store_manager": return "매장 관리자";
      case "employee": return "직원";
      default: return role;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "active":
        return <Badge variant="default" className="bg-green-600"><CheckCircle className="w-3 h-3 mr-1" />활성</Badge>;
      case "pending":
        return <Badge variant="secondary">승인 대기</Badge>;
      case "inactive":
        return <Badge variant="destructive"><XCircle className="w-3 h-3 mr-1" />비활성</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const stats = {
    totalUsers: users.length,
    activeUsers: users.filter(u => u.status === "active").length,
    pendingUsers: users.filter(u => u.status === "pending").length,
    inactiveUsers: users.filter(u => u.status === "inactive").length,
  };

  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            사용자 관리
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            시스템 사용자 계정 관리 및 권한 설정
          </p>
        </div>
        <Button className="flex items-center space-x-2">
          <UserPlus className="h-4 w-4" />
          <span>새 사용자 추가</span>
        </Button>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">전체 사용자</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalUsers}</div>
            <p className="text-xs text-muted-foreground">
              등록된 사용자 수
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">활성 사용자</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.activeUsers}</div>
            <p className="text-xs text-muted-foreground">
              정상 사용 중
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">승인 대기</CardTitle>
            <Shield className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{stats.pendingUsers}</div>
            <p className="text-xs text-muted-foreground">
              승인 필요
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">비활성 사용자</CardTitle>
            <XCircle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats.inactiveUsers}</div>
            <p className="text-xs text-muted-foreground">
              접근 제한
            </p>
          </CardContent>
        </Card>
      </div>

      {/* 검색 및 필터 */}
      <Card>
        <CardHeader>
          <CardTitle>사용자 검색</CardTitle>
          <CardDescription>
            이름, 이메일, 역할로 사용자를 검색하세요
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex space-x-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="사용자 검색..."
                  className="pl-10"
                />
              </div>
            </div>
            <Button variant="outline" className="flex items-center space-x-2">
              <Filter className="h-4 w-4" />
              <span>필터</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 사용자 목록 */}
      <Card>
        <CardHeader>
          <CardTitle>사용자 목록</CardTitle>
          <CardDescription>
            등록된 모든 사용자 정보
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {users.map((user) => (
              <div key={user.id} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                    <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
                      {user.name.charAt(0)}
                    </span>
                  </div>
                  <div>
                    <h3 className="font-medium">{user.name}</h3>
                    <p className="text-sm text-muted-foreground">{user.email}</p>
                    <div className="flex items-center space-x-2 mt-1">
                      <Badge variant="outline">{getRoleLabel(user.role)}</Badge>
                      <span className="text-xs text-muted-foreground">•</span>
                      <span className="text-xs text-muted-foreground">{user.store}</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <p className="text-sm font-medium">마지막 로그인</p>
                    <p className="text-xs text-muted-foreground">{user.lastLogin}</p>
                  </div>
                  {getStatusBadge(user.status)}
                  <div className="flex items-center space-x-2">
                    <Button variant="outline" size="sm">
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button variant="outline" size="sm">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 역할별 통계 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>역할별 사용자 분포</CardTitle>
            <CardDescription>
              각 역할별 사용자 수
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm">슈퍼 관리자</span>
                <Badge variant="outline">1명</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">브랜드 관리자</span>
                <Badge variant="outline">1명</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">매장 관리자</span>
                <Badge variant="outline">2명</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">일반 직원</span>
                <Badge variant="outline">2명</Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>최근 활동</CardTitle>
            <CardDescription>
              사용자 관련 최근 활동
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <div>
                  <p className="text-sm font-medium">새 사용자 등록</p>
                  <p className="text-xs text-muted-foreground">이영희 - 2시간 전</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <div>
                  <p className="text-sm font-medium">권한 변경</p>
                  <p className="text-xs text-muted-foreground">박민수 - 1일 전</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                <div>
                  <p className="text-sm font-medium">계정 비활성화</p>
                  <p className="text-xs text-muted-foreground">정수진 - 3일 전</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 
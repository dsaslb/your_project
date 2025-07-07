"use client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { 
  Building2, 
  MapPin, 
  Phone, 
  Mail,
  Users,
  DollarSign,
  Plus,
  Edit,
  Trash2,
  Search,
  Filter
} from "lucide-react";

export default function BranchManagement() {
  // 더미 데이터
  const branches = [
    {
      id: 1,
      name: "강남점",
      address: "서울시 강남구 테헤란로 123",
      phone: "02-1234-5678",
      email: "gangnam@restaurant.com",
      manager: "김철수",
      employees: 28,
      status: "active",
      revenue: "₩350,000,000",
      openDate: "2023-01-15"
    },
    {
      id: 2,
      name: "홍대점",
      address: "서울시 마포구 홍대로 456",
      phone: "02-2345-6789",
      email: "hongdae@restaurant.com",
      manager: "이영희",
      employees: 25,
      status: "active",
      revenue: "₩280,000,000",
      openDate: "2023-03-20"
    },
    {
      id: 3,
      name: "부산점",
      address: "부산시 해운대구 해운대로 789",
      phone: "051-3456-7890",
      email: "busan@restaurant.com",
      manager: "박민수",
      employees: 22,
      status: "active",
      revenue: "₩220,000,000",
      openDate: "2023-06-10"
    },
    {
      id: 4,
      name: "대구점",
      address: "대구시 중구 동성로 321",
      phone: "053-4567-8901",
      email: "daegu@restaurant.com",
      manager: "정수진",
      employees: 20,
      status: "maintenance",
      revenue: "₩200,000,000",
      openDate: "2023-08-05"
    },
    {
      id: 5,
      name: "인천점",
      address: "인천시 연수구 송도대로 654",
      phone: "032-5678-9012",
      email: "incheon@restaurant.com",
      manager: "최동현",
      employees: 18,
      status: "active",
      revenue: "₩180,000,000",
      openDate: "2023-10-12"
    }
  ];

  const stats = {
    totalBranches: branches.length,
    activeBranches: branches.filter(b => b.status === "active").length,
    totalEmployees: branches.reduce((sum, b) => sum + b.employees, 0),
    totalRevenue: branches.reduce((sum, b) => sum + parseInt(b.revenue.replace(/[₩,]/g, '')), 0)
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "active":
        return <Badge variant="default" className="bg-green-600">운영 중</Badge>;
      case "maintenance":
        return <Badge variant="secondary">점검 중</Badge>;
      case "closed":
        return <Badge variant="destructive">폐점</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            브랜치 관리
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            매장 정보 및 운영 현황 관리
          </p>
        </div>
        <Button className="flex items-center space-x-2">
          <Plus className="h-4 w-4" />
          <span>새 매장 추가</span>
        </Button>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">전체 매장</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalBranches}</div>
            <p className="text-xs text-muted-foreground">
              등록된 매장 수
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">운영 중</CardTitle>
            <Building2 className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.activeBranches}</div>
            <p className="text-xs text-muted-foreground">
              정상 운영 매장
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">전체 직원</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalEmployees}</div>
            <p className="text-xs text-muted-foreground">
              총 직원 수
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 매출</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">₩{stats.totalRevenue.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              전체 매장 매출
            </p>
          </CardContent>
        </Card>
      </div>

      {/* 검색 및 필터 */}
      <Card>
        <CardHeader>
          <CardTitle>매장 검색</CardTitle>
          <CardDescription>
            매장명, 주소, 매니저로 검색하세요
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex space-x-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="매장 검색..."
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

      {/* 매장 목록 */}
      <Card>
        <CardHeader>
          <CardTitle>매장 목록</CardTitle>
          <CardDescription>
            등록된 모든 매장 정보
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {branches.map((branch) => (
              <div key={branch.id} className="flex items-center justify-between p-6 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                    <Building2 className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                  </div>
                  <div>
                    <h3 className="font-medium text-lg">{branch.name}</h3>
                    <div className="flex items-center space-x-4 text-sm text-muted-foreground mt-1">
                      <div className="flex items-center space-x-1">
                        <MapPin className="h-3 w-3" />
                        <span>{branch.address}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Phone className="h-3 w-3" />
                        <span>{branch.phone}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Mail className="h-3 w-3" />
                        <span>{branch.email}</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-6">
                  <div className="text-right">
                    <p className="text-sm font-medium">매니저: {branch.manager}</p>
                    <p className="text-sm text-muted-foreground">{branch.employees}명 직원</p>
                    <p className="text-sm text-muted-foreground">개점일: {branch.openDate}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">{branch.revenue}</p>
                    <p className="text-sm text-muted-foreground">월 매출</p>
                  </div>
                  {getStatusBadge(branch.status)}
                  <div className="flex items-center space-x-2">
                    <Button variant="outline" size="sm">
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button variant="outline" size="sm">
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 매장별 상세 통계 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>매장별 매출 현황</CardTitle>
            <CardDescription>
              각 매장의 월별 매출 비교
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {branches.map((branch) => (
                <div key={branch.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div>
                    <h3 className="font-medium">{branch.name}</h3>
                    <p className="text-sm text-muted-foreground">{branch.manager} 매니저</p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">{branch.revenue}</p>
                    <div className="w-32 bg-gray-200 rounded-full h-2 mt-1">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{width: `${(parseInt(branch.revenue.replace(/[₩,]/g, '')) / 350000000) * 100}%`}}
                      ></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>매장별 직원 현황</CardTitle>
            <CardDescription>
              각 매장의 직원 수 및 구성
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {branches.map((branch) => (
                <div key={branch.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div>
                    <h3 className="font-medium">{branch.name}</h3>
                    <p className="text-sm text-muted-foreground">총 {branch.employees}명</p>
                  </div>
                  <div className="text-right">
                    <Badge variant="outline">{branch.employees}명</Badge>
                    <div className="w-32 bg-gray-200 rounded-full h-2 mt-1">
                      <div 
                        className="bg-green-600 h-2 rounded-full" 
                        style={{width: `${(branch.employees / 28) * 100}%`}}
                      ></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Building2, 
  Store, 
  Users, 
  TrendingUp, 
  DollarSign, 
  ShoppingCart,
  Clock,
  Star,
  ArrowRight,
  ChevronRight
} from 'lucide-react';

interface Brand {
  id: number;
  name: string;
  today_revenue: number;
  branch_count: number;
  staff_count: number;
  avg_revenue_per_branch: number;
}

interface Branch {
  id: number;
  name: string;
  brand_name: string;
  location: string;
  today_revenue: number;
  staff_count: number;
  today_orders: number;
  avg_order_value: number;
}

interface Staff {
  id: number;
  name: string;
  position: string;
  branch_name: string;
  brand_name: string;
  today_orders: number;
  today_revenue: number;
  avg_order_value: number;
}

interface RestaurantHierarchyProps {
  currentLevel: 'brand' | 'branch' | 'staff';
  selectedId?: number;
}

export const RestaurantHierarchy: React.FC<RestaurantHierarchyProps> = ({
  currentLevel,
  selectedId
}) => {
  const [brands, setBrands] = useState<Brand[]>([]);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [staff, setStaff] = useState<Staff[]>([]);
  const [selectedBrand, setSelectedBrand] = useState<Brand | null>(null);
  const [selectedBranch, setSelectedBranch] = useState<Branch | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // 예시 데이터 사용 (API 호출 대신)
      const mockBrands = [
        {
          id: 1,
          name: '스타벅스',
          today_revenue: 15000000,
          branch_count: 5,
          staff_count: 45,
          avg_revenue_per_branch: 3000000
        },
        {
          id: 2,
          name: '맥도날드',
          today_revenue: 12000000,
          branch_count: 4,
          staff_count: 38,
          avg_revenue_per_branch: 3000000
        },
        {
          id: 3,
          name: '버거킹',
          today_revenue: 8000000,
          branch_count: 3,
          staff_count: 25,
          avg_revenue_per_branch: 2666667
        }
      ];
      setBrands(mockBrands);

      const mockBranches = [
        {
          id: 1,
          name: '강남점',
          brand_name: '스타벅스',
          location: '서울시 강남구',
          today_revenue: 3500000,
          staff_count: 12,
          today_orders: 150,
          avg_order_value: 23333
        },
        {
          id: 2,
          name: '홍대점',
          brand_name: '스타벅스',
          location: '서울시 마포구',
          today_revenue: 2800000,
          staff_count: 10,
          today_orders: 120,
          avg_order_value: 23333
        },
        {
          id: 3,
          name: '강남점',
          brand_name: '맥도날드',
          location: '서울시 강남구',
          today_revenue: 3200000,
          staff_count: 15,
          today_orders: 200,
          avg_order_value: 16000
        }
      ];
      setBranches(mockBranches);

      const mockStaff = [
        {
          id: 1,
          name: '김철수',
          position: '매니저',
          branch_name: '강남점',
          brand_name: '스타벅스',
          today_orders: 25,
          today_revenue: 600000,
          avg_order_value: 24000
        },
        {
          id: 2,
          name: '이영희',
          position: '바리스타',
          branch_name: '강남점',
          brand_name: '스타벅스',
          today_orders: 30,
          today_revenue: 720000,
          avg_order_value: 24000
        },
        {
          id: 3,
          name: '박민수',
          position: '매니저',
          branch_name: '홍대점',
          brand_name: '스타벅스',
          today_orders: 20,
          today_revenue: 480000,
          avg_order_value: 24000
        }
      ];
      setStaff(mockStaff);

    } catch (error) {
      console.error('데이터 로드 오류:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW'
    }).format(amount);
  };

  const getBranchesByBrand = (brandId: number) => {
    return branches.filter(branch => 
      branch.brand_name === brands.find(b => b.id === brandId)?.name
    );
  };

  const getStaffByBranch = (branchId: number) => {
    return staff.filter(s => 
      s.branch_name === branches.find(b => b.id === branchId)?.name
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 브랜드 레벨 */}
      <Tabs defaultValue="brands" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="brands" className="flex items-center gap-2">
            <Store className="h-4 w-4" />
            브랜드 관리
          </TabsTrigger>
          <TabsTrigger value="branches" className="flex items-center gap-2">
            <Building2 className="h-4 w-4" />
            매장 관리
          </TabsTrigger>
          <TabsTrigger value="staff" className="flex items-center gap-2">
            <Users className="h-4 w-4" />
            직원 관리
          </TabsTrigger>
        </TabsList>

        {/* 브랜드 탭 */}
        <TabsContent value="brands" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {brands.map((brand) => (
              <Card key={brand.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span className="text-lg font-semibold">{brand.name}</span>
                    <Badge variant="secondary">{brand.branch_count}개 매장</Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div className="flex items-center gap-1">
                      <DollarSign className="h-4 w-4 text-green-600" />
                      <span className="text-gray-600">오늘 매출:</span>
                    </div>
                    <div className="font-semibold">{formatCurrency(brand.today_revenue)}</div>
                    
                    <div className="flex items-center gap-1">
                      <Users className="h-4 w-4 text-blue-600" />
                      <span className="text-gray-600">직원 수:</span>
                    </div>
                    <div className="font-semibold">{brand.staff_count}명</div>
                    
                    <div className="flex items-center gap-1">
                      <TrendingUp className="h-4 w-4 text-purple-600" />
                      <span className="text-gray-600">매장당 평균:</span>
                    </div>
                    <div className="font-semibold">{formatCurrency(brand.avg_revenue_per_branch)}</div>
                  </div>
                  
                  <Button 
                    className="w-full" 
                    variant="outline"
                    onClick={() => setSelectedBrand(brand)}
                  >
                    매장 보기
                    <ChevronRight className="h-4 w-4 ml-2" />
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* 매장 탭 */}
        <TabsContent value="branches" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {branches.map((branch) => (
              <Card key={branch.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span className="text-lg font-semibold">{branch.name}</span>
                    <Badge variant="outline">{branch.brand_name}</Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="text-sm text-gray-600">{branch.location}</div>
                  
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div className="flex items-center gap-1">
                      <DollarSign className="h-4 w-4 text-green-600" />
                      <span className="text-gray-600">오늘 매출:</span>
                    </div>
                    <div className="font-semibold">{formatCurrency(branch.today_revenue)}</div>
                    
                    <div className="flex items-center gap-1">
                      <ShoppingCart className="h-4 w-4 text-blue-600" />
                      <span className="text-gray-600">주문 수:</span>
                    </div>
                    <div className="font-semibold">{branch.today_orders}건</div>
                    
                    <div className="flex items-center gap-1">
                      <Users className="h-4 w-4 text-purple-600" />
                      <span className="text-gray-600">직원 수:</span>
                    </div>
                    <div className="font-semibold">{branch.staff_count}명</div>
                    
                    <div className="flex items-center gap-1">
                      <TrendingUp className="h-4 w-4 text-orange-600" />
                      <span className="text-gray-600">평균 주문:</span>
                    </div>
                    <div className="font-semibold">{formatCurrency(branch.avg_order_value)}</div>
                  </div>
                  
                  <Button 
                    className="w-full" 
                    variant="outline"
                    onClick={() => setSelectedBranch(branch)}
                  >
                    직원 보기
                    <ChevronRight className="h-4 w-4 ml-2" />
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* 직원 탭 */}
        <TabsContent value="staff" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {staff.map((staffMember) => (
              <Card key={staffMember.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span className="text-lg font-semibold">{staffMember.name}</span>
                    <Badge variant="secondary">{staffMember.position}</Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="text-sm text-gray-600">
                    {staffMember.branch_name} - {staffMember.brand_name}
                  </div>
                  
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div className="flex items-center gap-1">
                      <ShoppingCart className="h-4 w-4 text-blue-600" />
                      <span className="text-gray-600">오늘 주문:</span>
                    </div>
                    <div className="font-semibold">{staffMember.today_orders}건</div>
                    
                    <div className="flex items-center gap-1">
                      <DollarSign className="h-4 w-4 text-green-600" />
                      <span className="text-gray-600">매출 기여:</span>
                    </div>
                    <div className="font-semibold">{formatCurrency(staffMember.today_revenue)}</div>
                    
                    <div className="flex items-center gap-1">
                      <TrendingUp className="h-4 w-4 text-purple-600" />
                      <span className="text-gray-600">평균 주문:</span>
                    </div>
                    <div className="font-semibold">{formatCurrency(staffMember.avg_order_value)}</div>
                  </div>
                  
                  <Button className="w-full" variant="outline">
                    상세 보기
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>

      {/* 선택된 브랜드의 매장들 */}
      {selectedBrand && (
        <div className="mt-8">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold">
              {selectedBrand.name} - 소속 매장
            </h3>
            <Button variant="ghost" onClick={() => setSelectedBrand(null)}>
              닫기
            </Button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {getBranchesByBrand(selectedBrand.id).map((branch) => (
              <Card key={branch.id} className="border-l-4 border-l-blue-500">
                <CardContent className="pt-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold">{branch.name}</h4>
                    <Badge variant="outline">{branch.brand_name}</Badge>
                  </div>
                  <div className="text-sm text-gray-600 mb-3">{branch.location}</div>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>매출: {formatCurrency(branch.today_revenue)}</div>
                    <div>주문: {branch.today_orders}건</div>
                    <div>직원: {branch.staff_count}명</div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* 선택된 매장의 직원들 */}
      {selectedBranch && (
        <div className="mt-8">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold">
              {selectedBranch.name} - 소속 직원
            </h3>
            <Button variant="ghost" onClick={() => setSelectedBranch(null)}>
              닫기
            </Button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {getStaffByBranch(selectedBranch.id).map((staffMember) => (
              <Card key={staffMember.id} className="border-l-4 border-l-green-500">
                <CardContent className="pt-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold">{staffMember.name}</h4>
                    <Badge variant="secondary">{staffMember.position}</Badge>
                  </div>
                  <div className="text-sm text-gray-600 mb-3">{staffMember.branch_name}</div>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>주문: {staffMember.today_orders}건</div>
                    <div>매출: {formatCurrency(staffMember.today_revenue)}</div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}; 
'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { 
  Building2, 
  Store, 
  Users, 
  TrendingUp, 
  Search,
  Plus,
  ArrowRight,
  Activity,
  BarChart3,
  Zap,
  Sparkles,
  Globe,
  Cpu,
  Brain
} from 'lucide-react';
import { toast } from 'sonner';

// 퀀텀 스타일 CSS
const quantumStyles = `
  @keyframes quantum-glow {
    0%, 100% { box-shadow: 0 0 20px rgba(34, 211, 238, 0.3); }
    50% { box-shadow: 0 0 40px rgba(34, 211, 238, 0.6); }
  }
  
  @keyframes quantum-pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.8; transform: scale(1.05); }
  }
  
  @keyframes quantum-float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
  }
  
  @keyframes quantum-sparkle {
    0%, 100% { opacity: 0; transform: scale(0) rotate(0deg); }
    50% { opacity: 1; transform: scale(1) rotate(180deg); }
  }
  
  .quantum-glow {
    animation: quantum-glow 3s ease-in-out infinite;
  }
  
  .quantum-pulse {
    animation: quantum-pulse 2s ease-in-out infinite;
  }
  
  .quantum-float {
    animation: quantum-float 4s ease-in-out infinite;
  }
  
  .quantum-sparkle {
    animation: quantum-sparkle 2s ease-in-out infinite;
  }
  
  .quantum-gradient {
    background: linear-gradient(135deg, 
      rgba(34, 211, 238, 0.1) 0%, 
      rgba(147, 51, 234, 0.1) 25%, 
      rgba(16, 185, 129, 0.1) 50%, 
      rgba(251, 191, 36, 0.1) 75%, 
      rgba(34, 211, 238, 0.1) 100%);
  }
  
  .quantum-border {
    border: 1px solid transparent;
    background: linear-gradient(135deg, 
      rgba(34, 211, 238, 0.3), 
      rgba(147, 51, 234, 0.3), 
      rgba(16, 185, 129, 0.3)) border-box;
    -webkit-mask: 
      linear-gradient(#fff 0 0) padding-box, 
      linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
  }
`;

interface Brand {
  id: number;
  name: string;
  description?: string;
  store_count: number;
  employee_count: number;
  revenue: number;
  status: 'active' | 'inactive' | 'pending';
  created_at: string;
}

export default function BrandDashboardMain() {
  const router = useRouter();
  const [brands, setBrands] = useState<Brand[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [hoveredCard, setHoveredCard] = useState<number | null>(null);

  useEffect(() => {
    loadBrands();
  }, []);

  const loadBrands = async () => {
    try {
      setLoading(true);
      
      // 더미 데이터로 브랜드 목록 생성
      const dummyBrands: Brand[] = [
        {
          id: 1,
          name: '스타벅스',
          description: '글로벌 커피 체인점',
          store_count: 15,
          employee_count: 120,
          revenue: 85000000,
          status: 'active',
          created_at: '2024-01-15'
        },
        {
          id: 2,
          name: '카페베네',
          description: '국내 커피 전문점',
          store_count: 8,
          employee_count: 65,
          revenue: 42000000,
          status: 'active',
          created_at: '2024-02-20'
        },
        {
          id: 3,
          name: '빽다방',
          description: '저가 커피 체인점',
          store_count: 12,
          employee_count: 85,
          revenue: 38000000,
          status: 'active',
          created_at: '2024-03-10'
        },
        {
          id: 4,
          name: '이디야',
          description: '국내 커피 브랜드',
          store_count: 6,
          employee_count: 45,
          revenue: 28000000,
          status: 'active',
          created_at: '2024-04-05'
        },
        {
          id: 5,
          name: '투썸플레이스',
          description: '프리미엄 커피 체인',
          store_count: 10,
          employee_count: 75,
          revenue: 52000000,
          status: 'active',
          created_at: '2024-05-12'
        }
      ];
      
      setBrands(dummyBrands);
    } catch (error) {
      console.error('브랜드 데이터 로드 오류:', error);
      toast.error('브랜드 데이터를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleBrandSelect = (brandId: number) => {
    router.push(`/brand-dashboard/${brandId}`);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50 shadow-emerald-500/25';
      case 'inactive':
        return 'bg-red-500/20 text-red-400 border-red-500/50 shadow-red-500/25';
      case 'pending':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50 shadow-yellow-500/25';
      default:
        return 'bg-slate-500/20 text-slate-400 border-slate-500/50';
    }
  };

  const filteredBrands = brands.filter(brand =>
    brand.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    brand.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="relative">
          <div className="w-16 h-16 border-4 border-cyan-400/30 border-t-cyan-400 rounded-full animate-spin"></div>
          <div className="absolute inset-0 w-16 h-16 border-4 border-purple-400/30 border-t-purple-400 rounded-full animate-spin" style={{ animationDelay: '-0.5s' }}></div>
          <div className="absolute inset-0 w-16 h-16 border-4 border-emerald-400/30 border-t-emerald-400 rounded-full animate-spin" style={{ animationDelay: '-1s' }}></div>
        </div>
      </div>
    );
  }

  return (
    <>
      <style jsx global>{quantumStyles}</style>
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6 space-y-8">
        {/* 헤더 */}
        <div className="relative">
          <div className="absolute inset-0 bg-gradient-to-r from-cyan-400/10 via-purple-400/10 to-emerald-400/10 rounded-2xl blur-3xl"></div>
          <div className="relative bg-black/20 backdrop-blur-xl border border-white/10 rounded-2xl p-8 quantum-glow">
            <div className="flex items-center justify-between">
              <div className="space-y-2">
                <div className="flex items-center gap-3">
                  <div className="relative">
                    <div className="w-12 h-12 bg-gradient-to-r from-cyan-400 to-purple-600 rounded-xl flex items-center justify-center quantum-pulse">
                      <Building2 className="w-6 h-6 text-white" />
                    </div>
                    <div className="absolute -top-1 -right-1 w-4 h-4 bg-emerald-400 rounded-full quantum-sparkle"></div>
                  </div>
                  <div>
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-emerald-400 bg-clip-text text-transparent">
                      브랜드 대시보드
                    </h1>
                    <p className="text-slate-300 mt-1 flex items-center gap-2">
                      <Sparkles className="w-4 h-4 text-cyan-400 quantum-sparkle" />
                      퀀텀 브랜드 관리 시스템
                    </p>
                  </div>
                </div>
              </div>
              <Button className="bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700 text-white border-0 shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 transition-all duration-300 quantum-glow">
                <Plus className="h-4 w-4 mr-2" />
                새 브랜드 추가
              </Button>
            </div>
          </div>
        </div>

        {/* 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="group relative bg-gradient-to-br from-cyan-500/10 to-cyan-600/5 border border-cyan-500/20 backdrop-blur-xl hover:border-cyan-400/40 transition-all duration-500 hover:scale-105 quantum-float">
            <div className="absolute inset-0 bg-gradient-to-r from-cyan-400/5 to-transparent rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            <CardContent className="relative p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-300 mb-1">총 브랜드</p>
                  <p className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-cyan-300 bg-clip-text text-transparent">
                    {brands.length}
                  </p>
                  <p className="text-xs text-slate-400 mt-1">활성 브랜드</p>
                </div>
                <div className="w-14 h-14 bg-gradient-to-br from-cyan-500/20 to-cyan-600/20 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                  <Building2 className="h-7 w-7 text-cyan-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="group relative bg-gradient-to-br from-emerald-500/10 to-emerald-600/5 border border-emerald-500/20 backdrop-blur-xl hover:border-emerald-400/40 transition-all duration-500 hover:scale-105 quantum-float" style={{ animationDelay: '0.5s' }}>
            <div className="absolute inset-0 bg-gradient-to-r from-emerald-400/5 to-transparent rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            <CardContent className="relative p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-300 mb-1">총 매장</p>
                  <p className="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-emerald-300 bg-clip-text text-transparent">
                    {brands.reduce((sum, brand) => sum + brand.store_count, 0)}
                  </p>
                  <p className="text-xs text-slate-400 mt-1">운영 중</p>
                </div>
                <div className="w-14 h-14 bg-gradient-to-br from-emerald-500/20 to-emerald-600/20 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                  <Store className="h-7 w-7 text-emerald-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="group relative bg-gradient-to-br from-purple-500/10 to-purple-600/5 border border-purple-500/20 backdrop-blur-xl hover:border-purple-400/40 transition-all duration-500 hover:scale-105 quantum-float" style={{ animationDelay: '1s' }}>
            <div className="absolute inset-0 bg-gradient-to-r from-purple-400/5 to-transparent rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            <CardContent className="relative p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-300 mb-1">총 직원</p>
                  <p className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-purple-300 bg-clip-text text-transparent">
                    {brands.reduce((sum, brand) => sum + brand.employee_count, 0)}
                  </p>
                  <p className="text-xs text-slate-400 mt-1">근무 중</p>
                </div>
                <div className="w-14 h-14 bg-gradient-to-br from-purple-500/20 to-purple-600/20 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                  <Users className="h-7 w-7 text-purple-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="group relative bg-gradient-to-br from-yellow-500/10 to-yellow-600/5 border border-yellow-500/20 backdrop-blur-xl hover:border-yellow-400/40 transition-all duration-500 hover:scale-105 quantum-float" style={{ animationDelay: '1.5s' }}>
            <div className="absolute inset-0 bg-gradient-to-r from-yellow-400/5 to-transparent rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            <CardContent className="relative p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-300 mb-1">총 매출</p>
                  <p className="text-3xl font-bold bg-gradient-to-r from-yellow-400 to-yellow-300 bg-clip-text text-transparent">
                    ₩{(brands.reduce((sum, brand) => sum + brand.revenue, 0) / 1000000).toFixed(1)}M
                  </p>
                  <p className="text-xs text-slate-400 mt-1">이번 달</p>
                </div>
                <div className="w-14 h-14 bg-gradient-to-br from-yellow-500/20 to-yellow-600/20 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                  <TrendingUp className="h-7 w-7 text-yellow-400" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 검색 및 필터 */}
        <Card className="relative bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-600/30 backdrop-blur-xl quantum-glow">
          <div className="absolute inset-0 bg-gradient-to-r from-cyan-400/5 via-purple-400/5 to-emerald-400/5 rounded-lg"></div>
          <CardContent className="relative p-6">
            <div className="flex items-center gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
                <Input
                  placeholder="브랜드명 또는 설명으로 검색..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-12 bg-slate-800/50 border-slate-600/50 text-white placeholder:text-slate-400 focus:border-cyan-400/50 focus:ring-cyan-400/20"
                />
              </div>
              <Badge className="bg-gradient-to-r from-cyan-500/20 to-purple-500/20 text-cyan-300 border border-cyan-500/30 px-4 py-2 quantum-pulse">
                <Zap className="w-4 h-4 mr-2" />
                {filteredBrands.length}개 브랜드
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* 브랜드 목록 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredBrands.map((brand, index) => (
            <Card 
              key={brand.id} 
              className={`group relative bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-600/30 backdrop-blur-xl hover:border-cyan-400/50 transition-all duration-500 cursor-pointer transform hover:scale-105 hover:shadow-2xl hover:shadow-cyan-500/20 quantum-float ${
                hoveredCard === brand.id ? 'ring-2 ring-cyan-400/30' : ''
              }`}
              style={{ animationDelay: `${index * 200}ms` }}
              onClick={() => handleBrandSelect(brand.id)}
              onMouseEnter={() => setHoveredCard(brand.id)}
              onMouseLeave={() => setHoveredCard(null)}
            >
              <div className="absolute inset-0 bg-gradient-to-r from-cyan-400/5 via-purple-400/5 to-emerald-400/5 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              <CardHeader className="relative pb-4">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-white group-hover:text-cyan-400 transition-colors duration-300 text-xl">
                    {brand.name}
                  </CardTitle>
                  <Badge className={`${getStatusColor(brand.status)} shadow-lg`}>
                    {brand.status === 'active' ? '활성' : 
                     brand.status === 'inactive' ? '비활성' : '대기중'}
                  </Badge>
                </div>
                {brand.description && (
                  <p className="text-sm text-slate-400 group-hover:text-slate-300 transition-colors duration-300">
                    {brand.description}
                  </p>
                )}
              </CardHeader>
              <CardContent className="relative space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-4 bg-gradient-to-br from-emerald-500/10 to-emerald-600/5 border border-emerald-500/20 rounded-xl group-hover:border-emerald-400/40 transition-all duration-300">
                    <div className="flex items-center justify-center gap-2 mb-2">
                      <Store className="w-5 h-5 text-emerald-400" />
                      <span className="text-sm text-slate-300">매장</span>
                    </div>
                    <p className="text-xl font-bold text-white">{brand.store_count}개</p>
                  </div>
                  <div className="text-center p-4 bg-gradient-to-br from-purple-500/10 to-purple-600/5 border border-purple-500/20 rounded-xl group-hover:border-purple-400/40 transition-all duration-300">
                    <div className="flex items-center justify-center gap-2 mb-2">
                      <Users className="w-5 h-5 text-purple-400" />
                      <span className="text-sm text-slate-300">직원</span>
                    </div>
                    <p className="text-xl font-bold text-white">{brand.employee_count}명</p>
                  </div>
                </div>
                
                <div className="p-4 bg-gradient-to-br from-yellow-500/10 to-yellow-600/5 border border-yellow-500/20 rounded-xl group-hover:border-yellow-400/40 transition-all duration-300">
                  <div className="flex items-center justify-center gap-2 mb-2">
                    <TrendingUp className="w-5 h-5 text-yellow-400" />
                    <span className="text-sm text-slate-300">월 매출</span>
                  </div>
                  <p className="text-xl font-bold text-white text-center">
                    ₩{(brand.revenue / 1000000).toFixed(1)}M
                  </p>
                </div>
                
                <Button 
                  className="w-full bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700 text-white border-0 shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 transition-all duration-300 group-hover:scale-105"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleBrandSelect(brand.id);
                  }}
                >
                  <ArrowRight className="w-4 h-4 mr-2 group-hover:translate-x-1 transition-transform duration-300" />
                  대시보드 보기
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* 빈 상태 */}
        {filteredBrands.length === 0 && (
          <Card className="relative bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-600/30 backdrop-blur-xl quantum-glow">
            <div className="absolute inset-0 bg-gradient-to-r from-cyan-400/5 via-purple-400/5 to-emerald-400/5 rounded-lg"></div>
            <CardContent className="relative p-12 text-center">
              <div className="relative w-20 h-20 mx-auto mb-6">
                <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 to-purple-600 rounded-full quantum-pulse"></div>
                <Building2 className="w-12 h-12 text-white relative z-10 mx-auto mt-4" />
              </div>
              <h3 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent mb-3">
                브랜드를 찾을 수 없습니다
              </h3>
              <p className="text-slate-400 mb-6 max-w-md mx-auto">
                검색어를 변경하거나 새 브랜드를 추가하여 퀀텀 브랜드 관리 시스템을 시작해보세요.
              </p>
              <Button className="bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700 text-white border-0 shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 transition-all duration-300">
                <Plus className="h-4 w-4 mr-2" />
                새 브랜드 추가
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </>
  );
} 
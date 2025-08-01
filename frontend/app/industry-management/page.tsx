'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { 
  Building2, 
  Plus, 
  Search, 
  Edit, 
  Trash2, 
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Wifi,
  TrendingUp,
  Users,
  Calendar,
  Activity
} from 'lucide-react';
import { toast } from 'sonner';
import { Industry } from '../../lib/api-client';
import ProtectedRoute from '@/components/ProtectedRoute';
import { OfflineStorage } from '@/utils/offlineStorage';

interface IndustryFormData {
  name: string;
  code: string;
  description: string;
}

export default function IndustryManagement() {
  const [industries, setIndustries] = useState<Industry[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [editingIndustry, setEditingIndustry] = useState<Industry | null>(null);
  const [formData, setFormData] = useState<IndustryFormData>({
    name: '',
    code: '',
    description: '',
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isOffline, setIsOffline] = useState(false);

  // 업종 목록 조회
  const fetchIndustries = async () => {
    try {
      setIsLoading(true);
      setError(null);
      console.log('🔍 업종 목록 조회 시작...');
      
      // 백엔드 API 직접 호출 시도
      try {
        const response = await fetch('http://192.168.45.44:5000/api/admin/industries', {
          signal: AbortSignal.timeout(5000) // 5초 타임아웃
        });
        console.log('📊 API 응답 상태:', response.status);
        
        if (response.ok) {
          const data = await response.json();
          console.log('📋 업종 데이터:', data);
          
          if (data.success && data.data) {
            setIndustries(data.data);
            // 온라인 모드: 데이터를 로컬에 저장
            OfflineStorage.saveIndustries(data.data);
            OfflineStorage.saveLastSync();
            OfflineStorage.setOfflineMode(false);
            setIsOffline(false);
            console.log('✅ 온라인 모드: 업종 목록 설정 완료:', data.data.length, '개');
          } else {
            throw new Error('API 응답에 데이터가 없음');
          }
        } else {
          throw new Error(`API 호출 실패: ${response.status}`);
        }
      } catch (apiError) {
        console.log('🌐 백엔드 연결 실패, 오프라인 모드로 전환:', apiError);
        
        // 오프라인 모드: 로컬 데이터 사용
        let offlineData = OfflineStorage.loadIndustries();
        
        // 로컬 데이터가 없으면 기본 데이터 생성
        if (offlineData.length === 0) {
          console.log('📦 기본 오프라인 데이터 생성');
          const defaultData = OfflineStorage.createDefaultData();
          offlineData = defaultData.industries;
        }
        
        setIndustries(offlineData);
        OfflineStorage.setOfflineMode(true);
        setIsOffline(true);
        console.log('✅ 오프라인 모드: 업종 목록 설정 완료:', offlineData.length, '개');
      }
    } catch (error) {
      console.error('❌ 업종 목록 조회 오류:', error);
      setError('업종 목록 조회 중 오류가 발생했습니다.');
      setIndustries([]);
    } finally {
      setIsLoading(false);
    }
  };

  // 초기 데이터 로드
  useEffect(() => {
    console.log('🚀 초기 데이터 로드 시작');
    fetchIndustries();
  }, []);

  // 검색 필터링
  const filteredIndustries = industries.filter(industry =>
    industry.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    industry.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
    industry.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // 통계 계산
  const totalIndustries = industries.length;
  const totalBrands = industries.reduce((sum, industry) => sum + (industry.brand_count || 0), 0);
  const activeIndustries = industries.filter(industry => (industry as any).status === 'active').length;

  // 폼 초기화
  const resetForm = () => {
    setFormData({
      name: '',
      code: '',
      description: '',
    });
    setEditingIndustry(null);
  };

  // 입력 필드 변경 핸들러
  const handleInputChange = (field: keyof IndustryFormData, value: string) => {
    console.log(`입력 필드 변경: ${field} = ${value}`);
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // 폼 제출 처리
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    console.log('폼 제출 시도:', formData);
    
    if (!formData.name.trim() || !formData.code.trim()) {
      toast.error('업종명과 코드는 필수 입력 항목입니다.');
      return;
    }

    try {
      if (editingIndustry) {
        // 수정
        try {
          const response = await fetch(`http://192.168.45.44:5000/api/admin/industries/${editingIndustry.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData),
            signal: AbortSignal.timeout(5000)
          });
          
          if (response.ok) {
            toast.success('업종이 성공적으로 수정되었습니다.');
            setIsCreateDialogOpen(false);
            resetForm();
            fetchIndustries();
            return;
          }
        } catch (apiError) {
          console.log('🌐 백엔드 연결 실패, 오프라인 모드로 처리:', apiError);
        }
        
        // 오프라인 모드: 로컬 데이터 수정
        const updatedIndustries = industries.map(industry => 
          industry.id === editingIndustry.id 
            ? { ...industry, ...formData, updated_at: new Date().toISOString() }
            : industry
        );
        
        setIndustries(updatedIndustries);
        OfflineStorage.saveIndustries(updatedIndustries);
        OfflineStorage.setOfflineMode(true);
        toast.success('업종이 오프라인 모드에서 수정되었습니다.');
        setIsCreateDialogOpen(false);
        resetForm();
        
      } else {
        // 생성
        try {
          const response = await fetch('http://192.168.45.44:5000/api/admin/industries', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData),
            signal: AbortSignal.timeout(5000)
          });
          
          if (response.ok) {
            toast.success('업종이 성공적으로 생성되었습니다.');
            setIsCreateDialogOpen(false);
            resetForm();
            fetchIndustries();
            return;
          }
        } catch (apiError) {
          console.log('🌐 백엔드 연결 실패, 오프라인 모드로 처리:', apiError);
        }
        
        // 오프라인 모드: 로컬 데이터 생성
        const newIndustry = {
          id: Date.now(),
          ...formData,
          brand_count: 0,
          status: 'active',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };
        
        const updatedIndustries = [...industries, newIndustry];
        setIndustries(updatedIndustries);
        OfflineStorage.saveIndustries(updatedIndustries);
        OfflineStorage.setOfflineMode(true);
        toast.success('업종이 오프라인 모드에서 생성되었습니다.');
        setIsCreateDialogOpen(false);
        resetForm();
      }
    } catch (error) {
      console.error('업종 처리 오류:', error);
      toast.error('업종 처리 중 오류가 발생했습니다.');
    }
  };

  // 삭제 처리
  const handleDelete = async (industry: Industry) => {
    if (!confirm(`정말로 "${industry.name}" 업종을 비활성화하시겠습니까?\n\n⚠️ 관련 브랜드가 있으면 비활성화할 수 없습니다.`)) {
      return;
    }

    try {
      // 온라인 모드: 백엔드 API 호출
      try {
        const response = await fetch(`http://192.168.45.44:5000/api/admin/industries/${industry.id}`, {
          method: 'DELETE',
          headers: { 'Content-Type': 'application/json' },
          signal: AbortSignal.timeout(5000)
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
          toast.success(result.message || '업종이 성공적으로 비활성화되었습니다.');
          fetchIndustries(); // 목록 새로고침
          return;
        } else {
          // 백엔드에서 오류 응답
          const errorMessage = result.error || '업종 비활성화에 실패했습니다.';
          toast.error(errorMessage);
          
          // 관련 데이터가 있는 경우 오프라인 모드로 처리하지 않음
          if (errorMessage.includes('브랜드가 있어') || errorMessage.includes('사용자가 있어')) {
            return;
          }
        }
      } catch (apiError) {
        console.log('🌐 백엔드 연결 실패, 오프라인 모드로 처리:', apiError);
      }
      
      // 오프라인 모드: 로컬 데이터 비활성화
      const updatedIndustries = industries.map(item => 
        item.id === industry.id 
          ? { ...item, is_active: false, status: 'inactive' }
          : item
      );
      setIndustries(updatedIndustries);
      OfflineStorage.saveIndustries(updatedIndustries);
      OfflineStorage.setOfflineMode(true);
      toast.success('업종이 오프라인 모드에서 비활성화되었습니다.');
      
    } catch (error) {
      console.error('업종 비활성화 오류:', error);
      toast.error('업종 비활성화 중 오류가 발생했습니다.');
    }
  };

  // 활성화 처리
  const handleActivate = async (industry: Industry) => {
    if (!confirm(`"${industry.name}" 업종을 활성화하시겠습니까?`)) {
      return;
    }

    try {
      // 온라인 모드: 백엔드 API 호출
      try {
        const response = await fetch(`http://192.168.45.44:5000/api/admin/industries/${industry.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ is_active: true }),
          signal: AbortSignal.timeout(5000)
        });
        
        if (response.ok) {
          toast.success('업종이 성공적으로 활성화되었습니다.');
          fetchIndustries();
          return;
        }
      } catch (apiError) {
        console.log('🌐 백엔드 연결 실패, 오프라인 모드로 처리:', apiError);
      }
      
      // 오프라인 모드: 로컬 데이터 활성화
      const updatedIndustries = industries.map(item => 
        item.id === industry.id 
          ? { ...item, is_active: true, status: 'active' }
          : item
      );
      setIndustries(updatedIndustries);
      OfflineStorage.saveIndustries(updatedIndustries);
      OfflineStorage.setOfflineMode(true);
      toast.success('업종이 오프라인 모드에서 활성화되었습니다.');
      
    } catch (error) {
      console.error('업종 활성화 오류:', error);
      toast.error('업종 활성화 중 오류가 발생했습니다.');
    }
  };

  // 수정 모드 시작
  const handleEdit = (industry: Industry) => {
    setEditingIndustry(industry);
    setFormData({
      name: industry.name,
      code: industry.code,
      description: industry.description || '',
    });
    setIsCreateDialogOpen(true);
  };

  return (
    <ProtectedRoute requiredRole="admin" requiredPermission={{ module: 'industry_management', action: 'view' }}>
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 text-white p-4 sm:p-6 lg:p-8">
        <div className="max-w-7xl mx-auto">
          {/* 헤더 */}
          <div className="mb-8">
            <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <h1 className="text-2xl sm:text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400 quantum-pulse">
                    업종 관리
                  </h1>
                  {isOffline && (
                    <Badge variant="secondary" className="bg-yellow-900/50 text-yellow-300 border-yellow-600/30 quantum-glass">
                      <Wifi className="w-3 h-3 mr-1" />
                      오프라인 모드
                    </Badge>
                  )}
                </div>
                <p className="text-gray-300 text-sm sm:text-base">업종 정보를 관리하고 브랜드를 구성하세요</p>
              </div>
              
              {/* 생성 버튼 */}
              <div className="flex items-center gap-3">
                <Button
                  onClick={() => {
                    // 브랜드 관리 페이지로 이동
                    window.location.href = '/brand-management';
                  }}
                  className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold px-6 py-2 rounded-lg shadow-lg hover:shadow-xl transition-all duration-300"
                >
                  <Plus className="w-5 h-5 mr-2" />
                  브랜드 생성
                </Button>
              </div>
            </div>
          </div>

          {/* 통계 카드 */}
          {!isLoading && !error && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
              <Card className="quantum-glass quantum-hover border-cyan-500/30">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-400">총 업종</p>
                      <p className="text-2xl font-bold text-cyan-400">{totalIndustries}</p>
                    </div>
                    <Building2 className="w-8 h-8 text-cyan-400/60" />
                  </div>
                </CardContent>
              </Card>
              
              <Card className="quantum-glass quantum-hover border-purple-500/30">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-400">총 브랜드</p>
                      <p className="text-2xl font-bold text-purple-400">{totalBrands}</p>
                    </div>
                    <TrendingUp className="w-8 h-8 text-purple-400/60" />
                  </div>
                </CardContent>
              </Card>
              
              <Card className="quantum-glass quantum-hover border-green-500/30">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-400">활성 업종</p>
                      <p className="text-2xl font-bold text-green-400">{activeIndustries}</p>
                    </div>
                    <Activity className="w-8 h-8 text-green-400/60" />
                  </div>
                </CardContent>
              </Card>
              
              <Card className="quantum-glass quantum-hover border-orange-500/30">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-400">평균 브랜드</p>
                      <p className="text-2xl font-bold text-orange-400">
                        {totalIndustries > 0 ? Math.round(totalBrands / totalIndustries) : 0}
                      </p>
                    </div>
                    <Users className="w-8 h-8 text-orange-400/60" />
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* 검색 및 필터 */}
          <div className="mb-6">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <Input
                type="text"
                placeholder="업종명, 코드, 설명으로 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 quantum-glass border-cyan-500/30 text-white placeholder:text-slate-400 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20"
              />
            </div>
          </div>

          {/* 업종 목록 */}
          {!isLoading && !error && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
                {filteredIndustries.map((industry, index) => (
                  <Card 
                    key={industry.id} 
                    className="quantum-glass quantum-hover border-cyan-500/30 transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:shadow-cyan-500/20"
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    <CardHeader className="pb-3">
                      <div className="flex justify-between items-start">
                        <div className="flex items-center space-x-2">
                          <div className="p-2 rounded-lg bg-gradient-to-br from-cyan-500/20 to-blue-500/20">
                            <Building2 className="w-5 h-5 text-cyan-400" />
                          </div>
                          <CardTitle className="text-lg text-white font-semibold">{industry.name}</CardTitle>
                        </div>
                        <Badge variant="secondary" className="quantum-neon bg-cyan-900/50 text-cyan-300 border-cyan-500/30">
                          {industry.code}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-gray-300 text-sm mb-4 line-clamp-2 leading-relaxed">
                        {industry.description || '설명이 없습니다.'}
                      </p>
                      
                      <div className="space-y-3">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-400 flex items-center">
                            <TrendingUp className="w-4 h-4 mr-1" />
                            브랜드 수
                          </span>
                          <span className="text-cyan-400 font-semibold">{industry.brand_count || 0}개</span>
                        </div>
                        
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-400 flex items-center">
                            <Activity className="w-4 h-4 mr-1" />
                            상태
                          </span>
                                                     <Badge 
                             variant="secondary" 
                             className={`${
                               (industry as any).status === 'active' 
                                 ? 'bg-green-900/50 text-green-300 border-green-500/30' 
                                 : 'bg-red-900/50 text-red-300 border-red-500/30'
                             }`}
                           >
                             {(industry as any).status === 'active' ? '활성' : '비활성'}
                          </Badge>
                        </div>
                      </div>
                      
                      <div className="flex space-x-2 mt-4 pt-4 border-t border-gray-700/50">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleEdit(industry)}
                          className="flex-1 border-cyan-600/50 text-cyan-400 hover:border-cyan-500 hover:text-cyan-300 quantum-hover"
                        >
                          <Edit className="w-3 h-3 mr-1" />
                          수정
                        </Button>
                        {(industry as any).status === 'active' ? (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleDelete(industry)}
                            className="flex-1 border-red-600/50 text-red-400 hover:border-red-500 hover:text-red-300 quantum-hover"
                          >
                            <Trash2 className="w-3 h-3 mr-1" />
                            비활성화
                          </Button>
                        ) : (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleActivate(industry)}
                            className="flex-1 border-green-600/50 text-green-400 hover:border-green-500 hover:text-green-300 quantum-hover"
                          >
                            <CheckCircle className="w-3 h-3 mr-1" />
                            활성화
                          </Button>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {/* 데이터가 없을 때 */}
              {filteredIndustries.length === 0 && (
                <div className="text-center py-16">
                  <div className="quantum-glass rounded-full p-8 w-32 h-32 mx-auto mb-6 flex items-center justify-center">
                    <Building2 className="w-16 h-16 text-gray-400" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-300 mb-2">업종이 없습니다</h3>
                  <p className="text-gray-400 mb-6 max-w-md mx-auto">새로운 업종을 추가하여 브랜드 관리를 시작하세요</p>
                  <Button
                    onClick={() => {
                      resetForm();
                      setIsCreateDialogOpen(true);
                    }}
                    className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 quantum-hover"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    첫 업종 추가
                  </Button>
                </div>
              )}
            </>
          )}

          {/* 에러 상태 */}
          {error && (
            <div className="text-center py-16">
              <div className="quantum-glass rounded-full p-8 w-32 h-32 mx-auto mb-6 flex items-center justify-center">
                <AlertTriangle className="w-16 h-16 text-red-400" />
              </div>
              <h3 className="text-xl font-semibold text-red-400 mb-2">오류가 발생했습니다</h3>
              <p className="text-gray-300 mb-6 max-w-md mx-auto">{error}</p>
              <Button
                onClick={fetchIndustries}
                className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 quantum-hover"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                다시 시도
              </Button>
            </div>
          )}

          {/* 로딩 상태 */}
          {isLoading && (
            <div className="text-center py-16">
              <div className="quantum-glass rounded-full p-8 w-32 h-32 mx-auto mb-6 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400"></div>
              </div>
              <p className="text-gray-300 text-lg">업종 정보를 불러오는 중...</p>
              <p className="text-gray-400 text-sm mt-2">잠시만 기다려주세요</p>
            </div>
          )}

          {/* 생성/수정 다이얼로그 */}
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogContent className="bg-slate-800/95 border-cyan-500/50 text-white max-w-md mx-auto backdrop-blur-xl">
              <DialogHeader>
                <DialogTitle className="text-xl text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400">
                  {editingIndustry ? '업종 수정' : '새 업종 추가'}
                </DialogTitle>
              </DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <Label htmlFor="name" className="text-gray-300 block mb-2">업종명 *</Label>
                  <Input
                    id="name"
                    type="text"
                    value={formData.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    className="bg-slate-700/50 border-cyan-500/50 text-white placeholder:text-slate-400 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20"
                    placeholder="업종명을 입력하세요"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="code" className="text-gray-300 block mb-2">업종 코드 *</Label>
                  <Input
                    id="code"
                    type="text"
                    value={formData.code}
                    onChange={(e) => handleInputChange('code', e.target.value)}
                    className="bg-slate-700/50 border-cyan-500/50 text-white placeholder:text-slate-400 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20"
                    placeholder="업종 코드를 입력하세요"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="description" className="text-gray-300 block mb-2">설명</Label>
                  <Textarea
                    id="description"
                    value={formData.description}
                    onChange={(e) => handleInputChange('description', e.target.value)}
                    className="bg-slate-700/50 border-cyan-500/50 text-white placeholder:text-slate-400 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20"
                    placeholder="업종에 대한 설명을 입력하세요"
                    rows={3}
                    style={{ resize: 'vertical' }}
                  />
                </div>
                <div className="flex justify-end space-x-2 pt-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setIsCreateDialogOpen(false)}
                    className="border-gray-600/50 text-gray-300 hover:border-gray-500 hover:text-gray-200"
                  >
                    취소
                  </Button>
                  <Button 
                    type="submit" 
                    className="bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-700 hover:to-blue-700"
                  >
                    {editingIndustry ? '수정' : '추가'}
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>
    </ProtectedRoute>
  );
} 
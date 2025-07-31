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
  XCircle
} from 'lucide-react';
import { toast } from 'sonner';
import { apiClient, Industry } from '../../lib/api-client';
import useLoadingState from '@/hooks/useLoadingState';
import useErrorHandler from '@/hooks/useErrorHandler';

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

  const { isLoading, error, withLoading } = useLoadingState();
  const { handleError } = useErrorHandler();

  // 업종 목록 조회
  const fetchIndustries = async () => {
    const response = await apiClient.getIndustries();
    if (response.success) {
      setIndustries(response.data);
    }
  };

  // 초기 데이터 로드
  useEffect(() => {
    withLoading(fetchIndustries);
  }, []);

  // 검색 필터링
  const filteredIndustries = industries.filter(industry =>
    industry.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    industry.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
    industry.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // 폼 초기화
  const resetForm = () => {
    setFormData({
      name: '',
      code: '',
      description: '',
    });
    setEditingIndustry(null);
  };

  // 폼 제출 처리
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name.trim() || !formData.code.trim()) {
      toast.error('업종명과 코드는 필수 입력 항목입니다.');
      return;
    }

    try {
      if (editingIndustry) {
        // 수정
        const response = await apiClient.updateIndustry(editingIndustry.id, formData);
        if (response.success) {
          toast.success('업종이 성공적으로 수정되었습니다.');
          setIsCreateDialogOpen(false);
          resetForm();
          fetchIndustries();
        }
      } else {
        // 생성
        const response = await apiClient.createIndustry(formData);
        if (response.success) {
          toast.success('업종이 성공적으로 생성되었습니다.');
          setIsCreateDialogOpen(false);
          resetForm();
          fetchIndustries();
        }
      }
    } catch (error) {
      handleError(error as Error);
    }
  };

  // 업종 삭제
  const handleDelete = async (industry: Industry) => {
    if (!confirm(`"${industry.name}" 업종을 삭제하시겠습니까?`)) {
      return;
    }

    try {
      const response = await apiClient.deleteIndustry(industry.id);
      if (response.success) {
        toast.success('업종이 성공적으로 삭제되었습니다.');
        fetchIndustries();
      }
    } catch (error) {
      handleError(error as Error);
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

  // 통계 계산
  const stats = {
    total: industries.length,
    active: industries.length, // 모든 업종이 활성 상태로 가정
    brands: industries.reduce((sum, industry) => sum + industry.brand_count, 0),
  };

  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <Building2 className="w-8 h-8 text-cyan-400" />
            업종별 관리
          </h1>
          <p className="text-slate-400 mt-2">업종 정보를 관리하고 브랜드를 조직화합니다.</p>
        </div>
        <Button
          onClick={() => {
            resetForm();
            setIsCreateDialogOpen(true);
          }}
          className="bg-gradient-to-r from-cyan-500/20 to-purple-500/20 text-cyan-400 border-cyan-500/30 hover:from-cyan-500/30 hover:to-purple-500/30"
        >
          <Plus className="w-4 h-4 mr-2" />
          업종 추가
        </Button>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="bg-slate-800/50 border-cyan-500/30 backdrop-blur-xl">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">총 업종</p>
                <p className="text-3xl font-bold text-cyan-400">{stats.total}</p>
              </div>
              <Building2 className="w-8 h-8 text-cyan-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 border-purple-500/30 backdrop-blur-xl">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">활성 업종</p>
                <p className="text-3xl font-bold text-purple-400">{stats.active}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-purple-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 border-emerald-500/30 backdrop-blur-xl">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">총 브랜드</p>
                <p className="text-3xl font-bold text-emerald-400">{stats.brands}</p>
              </div>
              <Building2 className="w-8 h-8 text-emerald-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 검색 및 필터 */}
      <Card className="bg-slate-800/50 border-slate-600 backdrop-blur-xl">
        <CardContent className="p-6">
          <div className="flex items-center gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input
                type="text"
                placeholder="업종명, 코드, 설명으로 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 bg-black/50 border-cyan-500/30 text-white placeholder:text-slate-400 focus:border-cyan-500"
              />
            </div>
            <Button
              onClick={() => withLoading(fetchIndustries)}
              variant="outline"
              className="border-slate-600 text-slate-300 hover:bg-slate-700"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              새로고침
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 업종 목록 */}
      <Card className="bg-slate-800/50 border-slate-600 backdrop-blur-xl">
        <CardHeader>
          <CardTitle className="text-cyan-400 flex items-center gap-2">
            <Building2 className="w-5 h-5" />
            업종 목록 ({filteredIndustries.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-12">
              <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin mx-auto mb-4" />
              <p className="text-slate-400">업종 정보를 불러오는 중...</p>
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <AlertTriangle className="w-8 h-8 text-red-400 mx-auto mb-4" />
              <p className="text-red-400 mb-4">{error}</p>
              <Button onClick={() => withLoading(fetchIndustries)}>
                다시 시도
              </Button>
            </div>
          ) : filteredIndustries.length === 0 ? (
            <div className="text-center py-12">
              <Building2 className="w-16 h-16 text-slate-600 mx-auto mb-4" />
              <p className="text-slate-400">
                {searchTerm ? '검색 결과가 없습니다.' : '등록된 업종이 없습니다.'}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredIndustries.map((industry) => (
                <Card
                  key={industry.id}
                  className="bg-slate-700/50 border-slate-600 hover:border-cyan-400/50 transition-all duration-300"
                >
                  <CardHeader className="pb-4">
                    <div className="flex items-center justify-between">
                      <div className="w-12 h-12 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 rounded-xl flex items-center justify-center">
                        <Building2 className="w-6 h-6 text-cyan-400" />
                      </div>
                      <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/50">
                        활성
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div>
                      <h3 className="text-lg font-semibold text-white">
                        {industry.name}
                      </h3>
                      <p className="text-sm text-slate-400">코드: {industry.code}</p>
                    </div>

                    {industry.description && (
                      <p className="text-sm text-slate-300">{industry.description}</p>
                    )}

                    <div className="pt-2">
                      <p className="text-slate-400 text-sm">소속 브랜드</p>
                      <p className="text-emerald-400 font-semibold">{industry.brand_count}개</p>
                    </div>

                    <div className="flex gap-2 pt-2">
                      <Button
                        onClick={() => handleEdit(industry)}
                        size="sm"
                        variant="outline"
                        className="flex-1 border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/20"
                      >
                        <Edit className="w-3 h-3 mr-1" />
                        수정
                      </Button>
                      <Button
                        onClick={() => handleDelete(industry)}
                        size="sm"
                        variant="outline"
                        className="border-red-500/30 text-red-400 hover:bg-red-500/20"
                      >
                        <Trash2 className="w-3 h-3" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* 업종 생성/수정 다이얼로그 */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="bg-slate-800/90 border-slate-600 backdrop-blur-xl">
          <DialogHeader>
            <DialogTitle className="text-cyan-400">
              {editingIndustry ? '업종 수정' : '업종 추가'}
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="name" className="text-slate-300">업종명 *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="bg-black/50 border-cyan-500/30 text-white focus:border-cyan-500"
                placeholder="업종명을 입력하세요"
              />
            </div>
            <div>
              <Label htmlFor="code" className="text-slate-300">업종 코드 *</Label>
              <Input
                id="code"
                value={formData.code}
                onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                className="bg-black/50 border-cyan-500/30 text-white focus:border-cyan-500"
                placeholder="업종 코드를 입력하세요"
              />
            </div>
            <div>
              <Label htmlFor="description" className="text-slate-300">설명</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="bg-black/50 border-cyan-500/30 text-white focus:border-cyan-500"
                placeholder="업종에 대한 설명을 입력하세요"
                rows={3}
              />
            </div>
            <div className="flex gap-3 pt-4">
              <Button
                type="submit"
                className="flex-1 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 text-cyan-400 border-cyan-500/30 hover:from-cyan-500/30 hover:to-purple-500/30"
              >
                {editingIndustry ? '수정' : '추가'}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsCreateDialogOpen(false)}
                className="border-slate-600 text-slate-300 hover:bg-slate-700"
              >
                취소
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
} 
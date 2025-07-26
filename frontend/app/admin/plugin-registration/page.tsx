'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { X, Plus, Upload, Save, ArrowLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';

interface PluginFormData {
  name: string;
  display_name: string;
  description: string;
  version: string;
  author: string;
  category: string;
  tags: string[];
  icon: string;
  file_path: string;
  ui_schema: {
    menu: {
      title: string;
      icon: string;
      position: number;
    };
    dashboard: {
      type: string;
      size: string;
      component: string;
    };
  };
}

export default function PluginRegistrationPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [newTag, setNewTag] = useState('');
  const [formData, setFormData] = useState<PluginFormData>({
    name: '',
    display_name: '',
    description: '',
    version: '1.0.0',
    author: '',
    category: '',
    tags: [],
    icon: '',
    file_path: '',
    ui_schema: {
      menu: {
        title: '',
        icon: '',
        position: 1
      },
      dashboard: {
        type: 'card',
        size: 'medium',
        component: ''
      }
    }
  });

  const categories = [
    { id: 'scheduling', name: '스케줄링' },
    { id: 'customer_management', name: '고객 관리' },
    { id: 'quality_management', name: '품질 관리' },
    { id: 'contract_management', name: '계약 관리' },
    { id: 'inventory_management', name: '재고 관리' }
  ];

  const dashboardTypes = [
    { id: 'card', name: '카드' },
    { id: 'chart', name: '차트' },
    { id: 'list', name: '리스트' },
    { id: 'gauge', name: '게이지' },
    { id: 'table', name: '테이블' }
  ];

  const dashboardSizes = [
    { id: 'small', name: '작음' },
    { id: 'medium', name: '보통' },
    { id: 'large', name: '큼' }
  ];

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleUISchemaChange = (section: string, field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      ui_schema: {
        ...prev.ui_schema,
        [section]: {
          ...prev.ui_schema[section as keyof typeof prev.ui_schema],
          [field]: value
        }
      }
    }));
  };

  const addTag = () => {
    if (newTag.trim() && !formData.tags.includes(newTag.trim())) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, newTag.trim()]
      }));
      setNewTag('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await fetch('/api/admin/plugin/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        toast.success('플러그인이 성공적으로 등록되었습니다!');
        router.push('/admin/plugin-management');
      } else {
        const error = await response.json();
        toast.error(error.message || '플러그인 등록에 실패했습니다.');
      }
    } catch (error) {
      toast.error('플러그인 등록 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.back()}
            className="flex items-center space-x-2"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>뒤로가기</span>
          </Button>
          <div>
            <h1 className="text-3xl font-bold">플러그인 등록</h1>
            <p className="text-muted-foreground">새로운 플러그인을 시스템에 등록합니다.</p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* 기본 정보 */}
        <Card>
          <CardHeader>
            <CardTitle>기본 정보</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="name">플러그인 ID *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  placeholder="예: ai_schedule_optimizer"
                  required
                />
                <p className="text-sm text-muted-foreground">
                  영문 소문자, 언더스코어만 사용 가능
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="display_name">표시 이름 *</Label>
                <Input
                  id="display_name"
                  value={formData.display_name}
                  onChange={(e) => handleInputChange('display_name', e.target.value)}
                  placeholder="예: AI 스케줄 최적화"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="version">버전 *</Label>
                <Input
                  id="version"
                  value={formData.version}
                  onChange={(e) => handleInputChange('version', e.target.value)}
                  placeholder="예: 1.0.0"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="author">개발자 *</Label>
                <Input
                  id="author"
                  value={formData.author}
                  onChange={(e) => handleInputChange('author', e.target.value)}
                  placeholder="예: AI Team"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="category">카테고리 *</Label>
                <Select
                  value={formData.category}
                  onValueChange={(value) => handleInputChange('category', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="카테고리를 선택하세요" />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map((category) => (
                      <SelectItem key={category.id} value={category.id}>
                        {category.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="icon">아이콘</Label>
                <Input
                  id="icon"
                  value={formData.icon}
                  onChange={(e) => handleInputChange('icon', e.target.value)}
                  placeholder="예: calendar, robot, chart"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">설명 *</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                placeholder="플러그인의 기능과 특징을 설명하세요."
                rows={3}
                required
              />
            </div>

            <div className="space-y-2">
              <Label>태그</Label>
              <div className="flex items-center space-x-2">
                <Input
                  value={newTag}
                  onChange={(e) => setNewTag(e.target.value)}
                  placeholder="태그를 입력하세요"
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                />
                <Button type="button" onClick={addTag} size="sm">
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex flex-wrap gap-2 mt-2">
                {formData.tags.map((tag) => (
                  <Badge key={tag} variant="secondary" className="flex items-center space-x-1">
                    <span>{tag}</span>
                    <X
                      className="h-3 w-3 cursor-pointer"
                      onClick={() => removeTag(tag)}
                    />
                  </Badge>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 파일 정보 */}
        <Card>
          <CardHeader>
            <CardTitle>파일 정보</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="file_path">파일 경로 *</Label>
              <Input
                id="file_path"
                value={formData.file_path}
                onChange={(e) => handleInputChange('file_path', e.target.value)}
                placeholder="예: /plugins/ai_schedule_optimizer.py"
                required
              />
            </div>
          </CardContent>
        </Card>

        {/* UI 스키마 */}
        <Card>
          <CardHeader>
            <CardTitle>UI 스키마</CardTitle>
            <p className="text-sm text-muted-foreground">
              플러그인이 메뉴와 대시보드에서 어떻게 표시될지 설정합니다.
            </p>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* 메뉴 설정 */}
            <div className="space-y-4">
              <h4 className="font-medium">메뉴 설정</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>메뉴 제목</Label>
                  <Input
                    value={formData.ui_schema.menu.title}
                    onChange={(e) => handleUISchemaChange('menu', 'title', e.target.value)}
                    placeholder="메뉴에 표시될 제목"
                  />
                </div>
                <div className="space-y-2">
                  <Label>메뉴 아이콘</Label>
                  <Input
                    value={formData.ui_schema.menu.icon}
                    onChange={(e) => handleUISchemaChange('menu', 'icon', e.target.value)}
                    placeholder="메뉴 아이콘"
                  />
                </div>
                <div className="space-y-2">
                  <Label>메뉴 순서</Label>
                  <Input
                    type="number"
                    value={formData.ui_schema.menu.position}
                    onChange={(e) => handleUISchemaChange('menu', 'position', parseInt(e.target.value))}
                    placeholder="1"
                  />
                </div>
              </div>
            </div>

            {/* 대시보드 설정 */}
            <div className="space-y-4">
              <h4 className="font-medium">대시보드 설정</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>컴포넌트 타입</Label>
                  <Select
                    value={formData.ui_schema.dashboard.type}
                    onValueChange={(value) => handleUISchemaChange('dashboard', 'type', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {dashboardTypes.map((type) => (
                        <SelectItem key={type.id} value={type.id}>
                          {type.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>크기</Label>
                  <Select
                    value={formData.ui_schema.dashboard.size}
                    onValueChange={(value) => handleUISchemaChange('dashboard', 'size', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {dashboardSizes.map((size) => (
                        <SelectItem key={size.id} value={size.id}>
                          {size.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>컴포넌트명</Label>
                  <Input
                    value={formData.ui_schema.dashboard.component}
                    onChange={(e) => handleUISchemaChange('dashboard', 'component', e.target.value)}
                    placeholder="예: ScheduleOptimizationChart"
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 제출 버튼 */}
        <div className="flex justify-end space-x-4">
          <Button
            type="button"
            variant="outline"
            onClick={() => router.back()}
          >
            취소
          </Button>
          <Button
            type="submit"
            disabled={isLoading}
            className="flex items-center space-x-2"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>등록 중...</span>
              </>
            ) : (
              <>
                <Save className="h-4 w-4" />
                <span>플러그인 등록</span>
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  );
} 
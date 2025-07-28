'use client';
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Building2, Save, Trash2, X, Plus } from 'lucide-react';
import { toast } from 'sonner';
import { Badge } from '@/components/ui/badge';

interface Industry {
  id?: number;
  name: string;
  code: string;
  description: string;
  icon: string;
  color: string;
  status: 'active' | 'inactive';
}

interface IndustryModalProps {
  industry?: Industry | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (industry: Industry) => void;
  onDelete?: (id: number) => void;
  mode: 'create' | 'edit';
}

const defaultIndustry: Industry = {
  name: '',
  code: '',
  description: '',
  icon: '🏢',
  color: '#3B82F6',
  status: 'active'
};

const industryIcons = [
  '🏢', '💐', '🏥', '✂️', '🍽️', '☕', '💊', '👕', '🛒', '🏦',
  '🎓', '🚗', '🏠', '💻', '🎨', '⚽', '🏪', '🏭', '🏨', '🎭'
];

export default function IndustryModal({ industry, isOpen, onClose, onSave, onDelete, mode }: IndustryModalProps) {
  const [formData, setFormData] = useState<Industry>(defaultIndustry);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      if (industry && mode === 'edit') {
        setFormData(industry);
      } else {
        setFormData(defaultIndustry);
      }
    }
  }, [industry, isOpen, mode]);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const generateCode = () => {
    const code = formData.name
      .replace(/[^a-zA-Z0-9가-힣]/g, '')
      .toUpperCase()
      .substring(0, 10);
    handleInputChange('code', code);
  };

  const validateForm = () => {
    if (!formData.name.trim()) {
      toast.error('업종명을 입력해주세요.');
      return false;
    }
    if (!formData.code.trim()) {
      toast.error('업종 코드를 입력해주세요.');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    setLoading(true);
    try {
      await onSave(formData);
      toast.success(mode === 'create' ? '업종이 생성되었습니다!' : '업종이 수정되었습니다!');
      onClose();
    } catch (error) {
      toast.error('저장 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!industry?.id || !onDelete) return;
    
    if (!confirm('정말로 이 업종을 삭제하시겠습니까?')) return;

    setLoading(true);
    try {
      await onDelete(industry.id);
      toast.success('업종이 삭제되었습니다!');
      onClose();
    } catch (error) {
      toast.error('삭제 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-slate-800 rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* 헤더 */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <Building2 className="w-6 h-6 text-blue-600" />
              <h2 className="text-xl font-bold">
                {mode === 'create' ? '새 업종 생성' : '업종 수정'}
              </h2>
            </div>
            <Button variant="outline" size="sm" onClick={onClose}>
              <X className="w-4 h-4" />
            </Button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* 업종 정보 */}
            <Card>
              <CardHeader>
                <CardTitle>업종 정보</CardTitle>
                <CardDescription>업종의 기본 정보를 입력해주세요.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="name">업종명 *</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => handleInputChange('name', e.target.value)}
                      placeholder="예: 꽃집, 병원, 미용실"
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="code">업종 코드 *</Label>
                    <div className="flex gap-2">
                      <Input
                        id="code"
                        value={formData.code}
                        onChange={(e) => handleInputChange('code', e.target.value.toUpperCase())}
                        placeholder="예: FLOWER_SHOP"
                        required
                      />
                      <Button type="button" variant="outline" onClick={generateCode}>
                        자동생성
                      </Button>
                    </div>
                  </div>
                </div>

                <div>
                  <Label htmlFor="description">설명</Label>
                  <Textarea
                    id="description"
                    value={formData.description}
                    onChange={(e) => handleInputChange('description', e.target.value)}
                    placeholder="업종에 대한 설명을 입력해주세요."
                    rows={3}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>아이콘</Label>
                    <div className="grid grid-cols-10 gap-2 mt-2">
                      {industryIcons.map((icon, index) => (
                        <button
                          key={index}
                          type="button"
                          className={`w-8 h-8 text-lg rounded border-2 ${
                            formData.icon === icon
                              ? 'border-blue-500 bg-blue-50'
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                          onClick={() => handleInputChange('icon', icon)}
                        >
                          {icon}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <Label>색상</Label>
                    <div className="grid grid-cols-6 gap-2 mt-2">
                      {['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899'].map((color) => (
                        <button
                          key={color}
                          type="button"
                          className={`w-8 h-8 rounded border-2 ${
                            formData.color === color
                              ? 'border-gray-800'
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                          style={{ backgroundColor: color }}
                          onClick={() => handleInputChange('color', color)}
                        />
                      ))}
                    </div>
                    <Input
                      value={formData.color}
                      onChange={(e) => handleInputChange('color', e.target.value)}
                      className="mt-2"
                      placeholder="#3B82F6"
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="status">상태</Label>
                  <Select value={formData.status} onValueChange={(value) => handleInputChange('status', value)}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="active">활성</SelectItem>
                      <SelectItem value="inactive">비활성</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* 미리보기 */}
            <Card>
              <CardHeader>
                <CardTitle>미리보기</CardTitle>
                <CardDescription>업종이 어떻게 표시될지 미리 확인해보세요.</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-3 p-4 border rounded-lg">
                  <div 
                    className="w-12 h-12 rounded-lg flex items-center justify-center text-2xl"
                    style={{ backgroundColor: formData.color + '20' }}
                  >
                    {formData.icon}
                  </div>
                  <div>
                    <h3 className="font-semibold">{formData.name || '업종명'}</h3>
                    <p className="text-sm text-gray-500">{formData.code || '업종코드'}</p>
                    {formData.description && (
                      <p className="text-sm text-gray-600 mt-1">{formData.description}</p>
                    )}
                  </div>
                  <Badge className={formData.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                    {formData.status === 'active' ? '활성' : '비활성'}
                  </Badge>
                </div>
              </CardContent>
            </Card>

            {/* 액션 버튼 */}
            <div className="flex justify-end gap-3">
              {mode === 'edit' && onDelete && (
                <Button
                  type="button"
                  variant="destructive"
                  onClick={handleDelete}
                  disabled={loading}
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  삭제
                </Button>
              )}
              <Button type="button" variant="outline" onClick={onClose} disabled={loading}>
                취소
              </Button>
              <Button type="submit" disabled={loading}>
                {loading ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                ) : (
                  <Save className="w-4 h-4 mr-2" />
                )}
                {mode === 'create' ? '업종 생성' : '업종 수정'}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
} 
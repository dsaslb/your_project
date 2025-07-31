'use client';

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { AlertTriangle, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'email' | 'number' | 'textarea' | 'select' | 'date' | 'tel';
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  options?: Array<{ value: string | number; label: string }>;
  validation?: (value: any) => string | undefined;
}

export interface CrudDialogProps<T> {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  mode: 'create' | 'edit' | 'delete' | 'view';
  title: string;
  data?: T;
  fields?: FormField[];
  onSubmit: (data: T) => Promise<void>;
  isLoading?: boolean;
  className?: string;
}

export function CrudDialog<T extends Record<string, any>>({
  open,
  onOpenChange,
  mode,
  title,
  data,
  fields = [],
  onSubmit,
  isLoading = false,
  className,
}: CrudDialogProps<T>) {
  const [formData, setFormData] = useState<Record<string, any>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // 초기 데이터 설정
  useEffect(() => {
    if (data && (mode === 'edit' || mode === 'view')) {
      setFormData(data);
    } else if (mode === 'create') {
      const initialData: Record<string, any> = {};
      fields.forEach(field => {
        initialData[field.name] = '';
      });
      setFormData(initialData);
    }
  }, [data, mode, fields]);

  // 폼 유효성 검사
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    fields.forEach(field => {
      const value = formData[field.name];
      
      // 필수 필드 검사
      if (field.required && !value) {
        newErrors[field.name] = `${field.label}은(는) 필수 항목입니다.`;
      }
      
      // 커스텀 유효성 검사
      if (field.validation && value) {
        const error = field.validation(value);
        if (error) {
          newErrors[field.name] = error;
        }
      }
    });
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // 폼 제출 처리
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (mode === 'view') return;
    
    if (mode !== 'delete' && !validateForm()) {
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      await onSubmit(formData as T);
      onOpenChange(false);
      setFormData({});
      setErrors({});
    } catch (error) {
      console.error('Submit error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  // 입력 필드 변경 처리
  const handleFieldChange = (name: string, value: any) => {
    setFormData(prev => ({ ...prev, [name]: value }));
    // 에러 제거
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  // 입력 필드 렌더링
  const renderField = (field: FormField) => {
    const value = formData[field.name] || '';
    const error = errors[field.name];
    const isDisabled = field.disabled || mode === 'view';

    switch (field.type) {
      case 'textarea':
        return (
          <div key={field.name} className="space-y-2">
            <Label htmlFor={field.name} className="text-slate-300">
              {field.label}
              {field.required && <span className="text-red-400 ml-1">*</span>}
            </Label>
            <Textarea
              id={field.name}
              value={value}
              onChange={(e) => handleFieldChange(field.name, e.target.value)}
              placeholder={field.placeholder}
              disabled={isDisabled}
              className={cn(
                "bg-slate-800/50 border-slate-700 text-white placeholder:text-slate-400",
                error && "border-red-500"
              )}
              rows={4}
            />
            {error && <p className="text-sm text-red-400">{error}</p>}
          </div>
        );

      case 'select':
        return (
          <div key={field.name} className="space-y-2">
            <Label htmlFor={field.name} className="text-slate-300">
              {field.label}
              {field.required && <span className="text-red-400 ml-1">*</span>}
            </Label>
            <Select
              value={value}
              onValueChange={(val) => handleFieldChange(field.name, val)}
              disabled={isDisabled}
            >
              <SelectTrigger
                className={cn(
                  "bg-slate-800/50 border-slate-700 text-white",
                  error && "border-red-500"
                )}
              >
                <SelectValue placeholder={field.placeholder || `${field.label} 선택`} />
              </SelectTrigger>
              <SelectContent>
                {field.options?.map(option => (
                  <SelectItem key={option.value} value={String(option.value)}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {error && <p className="text-sm text-red-400">{error}</p>}
          </div>
        );

      default:
        return (
          <div key={field.name} className="space-y-2">
            <Label htmlFor={field.name} className="text-slate-300">
              {field.label}
              {field.required && <span className="text-red-400 ml-1">*</span>}
            </Label>
            <Input
              id={field.name}
              type={field.type}
              value={value}
              onChange={(e) => handleFieldChange(field.name, e.target.value)}
              placeholder={field.placeholder}
              disabled={isDisabled}
              className={cn(
                "bg-slate-800/50 border-slate-700 text-white placeholder:text-slate-400",
                error && "border-red-500"
              )}
            />
            {error && <p className="text-sm text-red-400">{error}</p>}
          </div>
        );
    }
  };

  // 삭제 확인 다이얼로그
  if (mode === 'delete') {
    return (
      <AlertDialog open={open} onOpenChange={onOpenChange}>
        <AlertDialogContent className="bg-slate-800 border-red-500/30">
          <AlertDialogHeader>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-red-500/20 rounded-full flex items-center justify-center">
                <AlertTriangle className="w-5 h-5 text-red-400" />
              </div>
              <AlertDialogTitle className="text-red-400">{title}</AlertDialogTitle>
            </div>
            <AlertDialogDescription className="text-slate-300">
              이 작업은 되돌릴 수 없습니다. 정말로 삭제하시겠습니까?
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="bg-slate-700 text-white hover:bg-slate-600">
              취소
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="bg-red-600 text-white hover:bg-red-700"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  삭제 중...
                </>
              ) : (
                '삭제'
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    );
  }

  // 생성/수정/조회 다이얼로그
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className={cn("bg-slate-800 border-slate-700 max-w-2xl", className)}>
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle className="text-white">{title}</DialogTitle>
            {mode !== 'view' && (
              <DialogDescription className="text-slate-400">
                {mode === 'create' ? '새로운 항목을 추가합니다.' : '항목 정보를 수정합니다.'}
              </DialogDescription>
            )}
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            {fields.map(renderField)}
          </div>
          
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              className="border-slate-700 text-slate-300 hover:bg-slate-700"
            >
              {mode === 'view' ? '닫기' : '취소'}
            </Button>
            {mode !== 'view' && (
              <Button
                type="submit"
                disabled={isSubmitting || isLoading}
                className="bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-600 hover:to-purple-600"
              >
                {isSubmitting || isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    {mode === 'create' ? '생성 중...' : '수정 중...'}
                  </>
                ) : (
                  mode === 'create' ? '생성' : '수정'
                )}
              </Button>
            )}
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export default CrudDialog;
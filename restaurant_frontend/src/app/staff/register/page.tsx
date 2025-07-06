"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Save, User, Mail, Phone, Building, Calendar, DollarSign, FileText } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { AlertCircle, Check } from 'lucide-react';

interface StaffForm {
  name: string;
  position: string;
  department: string;
  email: string;
  phone: string;
  username: string;
  password: string;
  confirmPassword: string;
  joinDate: string;
  salary: number;
  contractType: string;
}

export default function StaffRegisterPage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedbackMessage, setFeedbackMessage] = useState('');
  const [feedbackType, setFeedbackType] = useState<'success' | 'error'>('success');
  const [errorMessage, setErrorMessage] = useState('');
  const [showError, setShowError] = useState(false);

  const [formData, setFormData] = useState<StaffForm>({
    name: '',
    position: '',
    department: '',
    email: '',
    phone: '',
    username: '',
    password: '',
    confirmPassword: '',
    joinDate: new Date().toISOString().split('T')[0],
    salary: 2500000,
    contractType: '정규직'
  });

  // 직책 및 부서 자동완성 데이터
  const positions = ['주방장', '부주방장', '요리사', '보조요리사', '서버', '홀매니저', '카운터', '청소원', '매니저', '사장'];
  const departments = ['주방', '홀', '카운터', '관리', '청소', '매니저'];

  // 피드백 메시지 표시 함수
  const showFeedbackMessage = (message: string, type: 'success' | 'error' = 'success') => {
    setFeedbackMessage(message);
    setFeedbackType(type);
    setShowFeedback(true);
    setTimeout(() => setShowFeedback(false), 3000);
  };

  // 에러 메시지 표시 함수
  const showErrorMessage = (message: string) => {
    setErrorMessage(message);
    setShowError(true);
    setTimeout(() => setShowError(false), 5000);
  };

  // 폼 검증
  const validateForm = () => {
    if (!formData.name.trim()) {
      showErrorMessage('직원명을 입력해주세요.');
      return false;
    }
    if (!formData.position.trim()) {
      showErrorMessage('직책을 선택해주세요.');
      return false;
    }
    if (!formData.department.trim()) {
      showErrorMessage('부서를 선택해주세요.');
      return false;
    }
    if (!formData.email.trim()) {
      showErrorMessage('이메일을 입력해주세요.');
      return false;
    }
    if (!formData.phone.trim()) {
      showErrorMessage('전화번호를 입력해주세요.');
      return false;
    }
    if (!formData.username.trim()) {
      showErrorMessage('아이디를 입력해주세요.');
      return false;
    }
    if (!formData.password.trim()) {
      showErrorMessage('비밀번호를 입력해주세요.');
      return false;
    }
    if (formData.password !== formData.confirmPassword) {
      showErrorMessage('비밀번호가 일치하지 않습니다.');
      return false;
    }
    return true;
  };

  // 직원 등록
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    
    try {
      const employeeData = {
        name: formData.name,
        position: formData.position,
        department: formData.department,
        email: formData.email,
        phone: formData.phone,
        username: formData.username,
        password: formData.password,
        join_date: formData.joinDate,
        salary: formData.salary.toString(),
        status: 'pending',
        contract_type: formData.contractType,
        contract_start_date: formData.joinDate,
        contract_expiry_date: new Date(new Date(formData.joinDate).getTime() + 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        permissions: {
          dashboard: { view: true, edit: false, admin_only: false },
          employee_management: { view: false, create: false, edit: false, delete: false, approve: false, assign_roles: false },
          schedule_management: { view: true, create: false, edit: false, delete: false, approve: false },
          order_management: { view: true, create: false, edit: false, delete: false, approve: false },
          inventory_management: { view: true, create: false, edit: false, delete: false },
          notification_management: { view: true, send: false, delete: false },
          system_management: { view: false, backup: false, restore: false, settings: false, monitoring: false },
          reports: { view: false, export: false, admin_only: false },
        }
      };

      const response = await fetch('http://localhost:5000/api/staff', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(employeeData)
      });

      const responseData = await response.json();
      
      if (response.ok && responseData.success) {
        showFeedbackMessage('직원이 성공적으로 등록되었습니다!');
        
        // 직원 목록/스케줄 새로고침 이벤트 발생
        window.dispatchEvent(new CustomEvent('staffDataUpdated'));
        
        // 2초 후 직원 목록으로 이동
        setTimeout(() => {
          router.push('/staff');
        }, 2000);
      } else {
        throw new Error(responseData.error || '등록에 실패했습니다.');
      }
      
    } catch (error) {
      console.error('직원 등록 실패:', error);
      showErrorMessage(error instanceof Error ? error.message : '등록에 실패했습니다.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* 피드백 메시지 */}
      {showFeedback && (
        <div className={`fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg ${
          feedbackType === 'success' 
            ? 'bg-green-500 text-white' 
            : 'bg-red-500 text-white'
        }`}>
          <div className="flex items-center gap-2">
            {feedbackType === 'success' ? (
              <Check className="h-4 w-4" />
            ) : (
              <AlertCircle className="h-4 w-4" />
            )}
            <span>{feedbackMessage}</span>
          </div>
        </div>
      )}

      {/* 에러 메시지 */}
      {showError && (
        <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 p-4 rounded-lg shadow-lg bg-red-500 text-white">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4" />
            <span>{errorMessage}</span>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                onClick={() => router.back()}
                className="flex items-center gap-2"
              >
                <ArrowLeft className="h-4 w-4" />
                뒤로가기
              </Button>
              <div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">새직원 등록</h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">새로운 직원을 등록하세요</p>
              </div>
            </div>
            <Button
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="flex items-center gap-2"
            >
              <Save className="h-4 w-4" />
              {isSubmitting ? '등록 중...' : '등록'}
            </Button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* 기본 정보 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5" />
                기본 정보
              </CardTitle>
              <CardDescription>직원의 기본 정보를 입력하세요</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="name">직원명 *</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    placeholder="직원명을 입력하세요"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="position">직책 *</Label>
                  <Select value={formData.position} onValueChange={(value) => setFormData({...formData, position: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="직책을 선택하세요" />
                    </SelectTrigger>
                    <SelectContent>
                      {positions.map((position) => (
                        <SelectItem key={position} value={position}>
                          {position}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="department">부서 *</Label>
                  <Select value={formData.department} onValueChange={(value) => setFormData({...formData, department: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="부서를 선택하세요" />
                    </SelectTrigger>
                    <SelectContent>
                      {departments.map((dept) => (
                        <SelectItem key={dept} value={dept}>
                          {dept}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="joinDate">입사일 *</Label>
                  <Input
                    id="joinDate"
                    type="date"
                    value={formData.joinDate}
                    onChange={(e) => setFormData({...formData, joinDate: e.target.value})}
                    required
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 연락처 정보 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Mail className="h-5 w-5" />
                연락처 정보
              </CardTitle>
              <CardDescription>직원의 연락처 정보를 입력하세요</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="email">이메일 *</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    placeholder="이메일을 입력하세요"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="phone">전화번호 *</Label>
                  <Input
                    id="phone"
                    value={formData.phone}
                    onChange={(e) => setFormData({...formData, phone: e.target.value})}
                    placeholder="전화번호를 입력하세요"
                    required
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 계정 정보 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5" />
                계정 정보
              </CardTitle>
              <CardDescription>로그인에 사용할 계정 정보를 입력하세요</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="username">아이디 *</Label>
                  <Input
                    id="username"
                    value={formData.username}
                    onChange={(e) => setFormData({...formData, username: e.target.value})}
                    placeholder="아이디를 입력하세요"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="password">비밀번호 *</Label>
                  <Input
                    id="password"
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({...formData, password: e.target.value})}
                    placeholder="비밀번호를 입력하세요"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="confirmPassword">비밀번호 확인 *</Label>
                  <Input
                    id="confirmPassword"
                    type="password"
                    value={formData.confirmPassword}
                    onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
                    placeholder="비밀번호를 다시 입력하세요"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="contractType">계약 유형</Label>
                  <Select value={formData.contractType} onValueChange={(value) => setFormData({...formData, contractType: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="정규직">정규직</SelectItem>
                      <SelectItem value="계약직">계약직</SelectItem>
                      <SelectItem value="파트타임">파트타임</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 급여 정보 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <DollarSign className="h-5 w-5" />
                급여 정보
              </CardTitle>
              <CardDescription>기본 급여를 설정하세요</CardDescription>
            </CardHeader>
            <CardContent>
              <div>
                <Label htmlFor="salary">기본 급여 (원)</Label>
                <Input
                  id="salary"
                  type="number"
                  value={formData.salary}
                  onChange={(e) => setFormData({...formData, salary: parseInt(e.target.value) || 0})}
                  placeholder="기본 급여를 입력하세요"
                />
              </div>
            </CardContent>
          </Card>
        </form>
      </div>
    </div>
  );
} 
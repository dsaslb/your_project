"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Save, User, Phone, Mail, Calendar, MapPin, FileText, Shield } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';

interface StaffFormData {
  name: string;
  position: string;
  department: string;
  email: string;
  phone: string;
  join_date: string;
  salary: string;
  status: 'active' | 'inactive' | 'pending';
  contract_type: string;
  contract_start_date: string;
  contract_expiry_date: string;
  health_certificate_type: string;
  health_certificate_issue_date: string;
  health_certificate_expiry_date: string;
  issuing_authority: string;
}

export default function AddStaffPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<StaffFormData>({
    name: '',
    position: '',
    department: '',
    email: '',
    phone: '',
    join_date: '',
    salary: '',
    status: 'active',
    contract_type: '정규직',
    contract_start_date: '',
    contract_expiry_date: '',
    health_certificate_type: '식품위생교육',
    health_certificate_issue_date: '',
    health_certificate_expiry_date: '',
    issuing_authority: '서울시보건소'
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch('http://localhost:5000/api/staff', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        alert('직원이 성공적으로 추가되었습니다!');
        router.push('/staff');
      } else {
        const errorData = await response.json();
        alert(`직원 추가 실패: ${errorData.error || '알 수 없는 오류'}`);
      }
    } catch (error) {
      console.error('직원 추가 오류:', error);
      alert('직원 추가 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const departments = ['주방', '홀', '매니저', '청소', '배송', '기타'];
  const positions = ['주방장', '주방직원', '서버', '매니저', '청소직원', '배송원', '기타'];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-4">
            <Button
              variant="outline"
              onClick={() => router.back()}
              className="flex items-center gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              뒤로가기
            </Button>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">새 직원 추가</h1>
          </div>
          <p className="text-gray-600 dark:text-gray-400">
            새로운 직원의 정보를 입력하고 등록하세요.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* 기본 정보 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5" />
                기본 정보
              </CardTitle>
              <CardDescription>
                직원의 기본적인 개인 정보를 입력하세요.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    이름 *
                  </label>
                  <Input
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    placeholder="직원 이름"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    이메일 *
                  </label>
                  <Input
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    placeholder="email@restaurant.com"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    전화번호 *
                  </label>
                  <Input
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                    placeholder="010-1234-5678"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    입사일 *
                  </label>
                  <Input
                    name="join_date"
                    type="date"
                    value={formData.join_date}
                    onChange={handleInputChange}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    부서 *
                  </label>
                  <select
                    name="department"
                    value={formData.department}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    <option value="">부서 선택</option>
                    {departments.map(dept => (
                      <option key={dept} value={dept}>{dept}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    직책 *
                  </label>
                  <select
                    name="position"
                    value={formData.position}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    <option value="">직책 선택</option>
                    {positions.map(pos => (
                      <option key={pos} value={pos}>{pos}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    급여
                  </label>
                  <Input
                    name="salary"
                    type="number"
                    value={formData.salary}
                    onChange={handleInputChange}
                    placeholder="3000000"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    상태
                  </label>
                  <select
                    name="status"
                    value={formData.status}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="active">재직중</option>
                    <option value="inactive">퇴사</option>
                    <option value="pending">대기중</option>
                  </select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 계약서 정보 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                계약서 정보
              </CardTitle>
              <CardDescription>
                직원의 계약서 정보를 입력하세요.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    계약 유형
                  </label>
                  <select
                    name="contract_type"
                    value={formData.contract_type}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="정규직">정규직</option>
                    <option value="계약직">계약직</option>
                    <option value="파트타임">파트타임</option>
                    <option value="인턴">인턴</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    계약 시작일
                  </label>
                  <Input
                    name="contract_start_date"
                    type="date"
                    value={formData.contract_start_date}
                    onChange={handleInputChange}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    계약 만료일
                  </label>
                  <Input
                    name="contract_expiry_date"
                    type="date"
                    value={formData.contract_expiry_date}
                    onChange={handleInputChange}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 보건증 정보 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                보건증 정보
              </CardTitle>
              <CardDescription>
                직원의 보건증 정보를 입력하세요.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    보건증 유형
                  </label>
                  <select
                    name="health_certificate_type"
                    value={formData.health_certificate_type}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="식품위생교육">식품위생교육</option>
                    <option value="위생교육">위생교육</option>
                    <option value="기타">기타</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    발급기관
                  </label>
                  <Input
                    name="issuing_authority"
                    value={formData.issuing_authority}
                    onChange={handleInputChange}
                    placeholder="서울시보건소"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    발급일
                  </label>
                  <Input
                    name="health_certificate_issue_date"
                    type="date"
                    value={formData.health_certificate_issue_date}
                    onChange={handleInputChange}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    만료일
                  </label>
                  <Input
                    name="health_certificate_expiry_date"
                    type="date"
                    value={formData.health_certificate_expiry_date}
                    onChange={handleInputChange}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 제출 버튼 */}
          <div className="flex justify-end gap-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => router.back()}
              disabled={loading}
            >
              취소
            </Button>
            <Button
              type="submit"
              disabled={loading}
              className="flex items-center gap-2"
            >
              <Save className="h-4 w-4" />
              {loading ? '저장 중...' : '직원 추가'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
} 
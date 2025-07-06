"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Save, Download, FileText, Calendar, Clock, User, Building, DollarSign, CheckCircle } from "lucide-react";
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface ContractForm {
  employeeName: string;
  employeeId: string;
  position: string;
  department: string;
  startDate: string;
  endDate: string;
  workDays: string[];
  workHours: {
    start: string;
    end: string;
  };
  salary: {
    base: number;
    allowance: number;
    bonus: number;
  };
  probationPeriod: number;
  noticePeriod: number;
  benefits: string[];
  responsibilities: string;
  terms: string;
}

export default function ContractPage() {
  const router = useRouter();
  const [isGenerating, setIsGenerating] = useState(false);
  const [contractForm, setContractForm] = useState<ContractForm>({
    employeeName: "",
    employeeId: "",
    position: "",
    department: "",
    startDate: "",
    endDate: "",
    workDays: ["월", "화", "수", "목", "금"],
    workHours: {
      start: "09:00",
      end: "18:00"
    },
    salary: {
      base: 0,
      allowance: 0,
      bonus: 0
    },
    probationPeriod: 3,
    noticePeriod: 30,
    benefits: ["4대보험", "연차휴가", "식대지원"],
    responsibilities: "",
    terms: ""
  });

  const workDayOptions = ["월", "화", "수", "목", "금", "토", "일"];
  const benefitOptions = ["4대보험", "연차휴가", "식대지원", "교통비지원", "야근수당", "휴일수당", "상여금"];

  const handleWorkDayToggle = (day: string) => {
    setContractForm(prev => ({
      ...prev,
      workDays: prev.workDays.includes(day)
        ? prev.workDays.filter(d => d !== day)
        : [...prev.workDays, day]
    }));
  };

  const handleBenefitToggle = (benefit: string) => {
    setContractForm(prev => ({
      ...prev,
      benefits: prev.benefits.includes(benefit)
        ? prev.benefits.filter(b => b !== benefit)
        : [...prev.benefits, benefit]
    }));
  };

  const generateContract = async () => {
    setIsGenerating(true);
    try {
      // 계약서 생성 로직
      await new Promise(resolve => setTimeout(resolve, 2000)); // 시뮬레이션
      
      // PDF 생성 및 다운로드
      const contractData = {
        ...contractForm,
        totalSalary: contractForm.salary.base + contractForm.salary.allowance + contractForm.salary.bonus,
        generatedDate: new Date().toISOString()
      };
      
      console.log("계약서 생성:", contractData);
      
      // 실제로는 PDF 생성 API 호출
      // const response = await fetch('/api/contracts/generate', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(contractData)
      // });
      
    } catch (error) {
      console.error("계약서 생성 실패:", error);
    } finally {
      setIsGenerating(false);
    }
  };

  const totalSalary = contractForm.salary.base + contractForm.salary.allowance + contractForm.salary.bonus;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => router.back()}
                className="p-2"
              >
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">근로계약서 작성</h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">직원과의 근로계약서를 작성하세요</p>
              </div>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={generateContract}
                disabled={isGenerating}
                className="flex items-center gap-2"
              >
                <FileText className="h-4 w-4" />
                {isGenerating ? "생성중..." : "계약서 생성"}
              </Button>
              <Button
                size="sm"
                onClick={generateContract}
                disabled={isGenerating}
                className="flex items-center gap-2"
              >
                <Save className="h-4 w-4" />
                저장
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 계약서 작성 폼 */}
          <div className="lg:col-span-2 space-y-6">
            {/* 기본 정보 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="h-5 w-5" />
                  기본 정보
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      직원명 *
                    </label>
                    <Input
                      value={contractForm.employeeName}
                      onChange={(e) => setContractForm(prev => ({ ...prev, employeeName: e.target.value }))}
                      placeholder="직원명을 입력하세요"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      사원번호
                    </label>
                    <Input
                      value={contractForm.employeeId}
                      onChange={(e) => setContractForm(prev => ({ ...prev, employeeId: e.target.value }))}
                      placeholder="사원번호"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      직책 *
                    </label>
                    <Input
                      value={contractForm.position}
                      onChange={(e) => setContractForm(prev => ({ ...prev, position: e.target.value }))}
                      placeholder="직책을 입력하세요"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      부서 *
                    </label>
                    <Input
                      value={contractForm.department}
                      onChange={(e) => setContractForm(prev => ({ ...prev, department: e.target.value }))}
                      placeholder="부서를 입력하세요"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* 계약 기간 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="h-5 w-5" />
                  계약 기간
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      계약 시작일 *
                    </label>
                    <Input
                      type="date"
                      value={contractForm.startDate}
                      onChange={(e) => setContractForm(prev => ({ ...prev, startDate: e.target.value }))}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      계약 종료일
                    </label>
                    <Input
                      type="date"
                      value={contractForm.endDate}
                      onChange={(e) => setContractForm(prev => ({ ...prev, endDate: e.target.value }))}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* 근무 조건 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5" />
                  근무 조건
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    근무일
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {workDayOptions.map(day => (
                      <Button
                        key={day}
                        variant={contractForm.workDays.includes(day) ? "default" : "outline"}
                        size="sm"
                        onClick={() => handleWorkDayToggle(day)}
                        className="w-12 h-10"
                      >
                        {day}
                      </Button>
                    ))}
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      출근 시간
                    </label>
                    <Input
                      type="time"
                      value={contractForm.workHours.start}
                      onChange={(e) => setContractForm(prev => ({ 
                        ...prev, 
                        workHours: { ...prev.workHours, start: e.target.value }
                      }))}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      퇴근 시간
                    </label>
                    <Input
                      type="time"
                      value={contractForm.workHours.end}
                      onChange={(e) => setContractForm(prev => ({ 
                        ...prev, 
                        workHours: { ...prev.workHours, end: e.target.value }
                      }))}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* 급여 조건 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <DollarSign className="h-5 w-5" />
                  급여 조건
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      기본급
                    </label>
                    <Input
                      type="number"
                      value={contractForm.salary.base}
                      onChange={(e) => setContractForm(prev => ({ 
                        ...prev, 
                        salary: { ...prev.salary, base: Number(e.target.value) }
                      }))}
                      placeholder="0"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      수당
                    </label>
                    <Input
                      type="number"
                      value={contractForm.salary.allowance}
                      onChange={(e) => setContractForm(prev => ({ 
                        ...prev, 
                        salary: { ...prev.salary, allowance: Number(e.target.value) }
                      }))}
                      placeholder="0"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      상여금
                    </label>
                    <Input
                      type="number"
                      value={contractForm.salary.bonus}
                      onChange={(e) => setContractForm(prev => ({ 
                        ...prev, 
                        salary: { ...prev.salary, bonus: Number(e.target.value) }
                      }))}
                      placeholder="0"
                    />
                  </div>
                </div>
                <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-blue-900 dark:text-blue-100">총 급여</span>
                    <span className="text-lg font-bold text-blue-900 dark:text-blue-100">
                      ₩{totalSalary.toLocaleString()}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* 복리후생 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5" />
                  복리후생
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {benefitOptions.map(benefit => (
                    <Button
                      key={benefit}
                      variant={contractForm.benefits.includes(benefit) ? "default" : "outline"}
                      size="sm"
                      onClick={() => handleBenefitToggle(benefit)}
                    >
                      {benefit}
                    </Button>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* 기타 조건 */}
            <Card>
              <CardHeader>
                <CardTitle>기타 조건</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    주요 업무
                  </label>
                  <Textarea
                    value={contractForm.responsibilities}
                    onChange={(e) => setContractForm(prev => ({ ...prev, responsibilities: e.target.value }))}
                    placeholder="주요 업무 내용을 입력하세요"
                    rows={3}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    특별 조건
                  </label>
                  <Textarea
                    value={contractForm.terms}
                    onChange={(e) => setContractForm(prev => ({ ...prev, terms: e.target.value }))}
                    placeholder="특별한 계약 조건이 있다면 입력하세요"
                    rows={3}
                  />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 미리보기 */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>계약서 미리보기</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4 text-sm">
                  <div className="border-b pb-2">
                    <h3 className="font-semibold text-lg mb-2">근로계약서</h3>
                    <p className="text-gray-600 dark:text-gray-400">
                      계약일: {new Date().toLocaleDateString()}
                    </p>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">직원명:</span>
                      <span className="font-medium">{contractForm.employeeName || "미입력"}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">직책:</span>
                      <span className="font-medium">{contractForm.position || "미입력"}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">부서:</span>
                      <span className="font-medium">{contractForm.department || "미입력"}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">계약기간:</span>
                      <span className="font-medium">
                        {contractForm.startDate ? new Date(contractForm.startDate).toLocaleDateString() : "미입력"}
                        {contractForm.endDate && ` ~ ${new Date(contractForm.endDate).toLocaleDateString()}`}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">근무시간:</span>
                      <span className="font-medium">
                        {contractForm.workHours.start} ~ {contractForm.workHours.end}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">총 급여:</span>
                      <span className="font-medium">₩{totalSalary.toLocaleString()}</span>
                    </div>
                  </div>

                  <div className="pt-2">
                    <h4 className="font-medium mb-2">복리후생</h4>
                    <div className="flex flex-wrap gap-1">
                      {contractForm.benefits.map(benefit => (
                        <Badge key={benefit} variant="secondary" className="text-xs">
                          {benefit}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* 빠른 설정 */}
            <Card>
              <CardHeader>
                <CardTitle>빠른 설정</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full"
                  onClick={() => {
                    setContractForm(prev => ({
                      ...prev,
                      workDays: ["월", "화", "수", "목", "금"],
                      workHours: { start: "09:00", end: "18:00" },
                      salary: { base: 2500000, allowance: 200000, bonus: 0 },
                      benefits: ["4대보험", "연차휴가", "식대지원"]
                    }));
                  }}
                >
                  정규직 기본 설정
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full"
                  onClick={() => {
                    setContractForm(prev => ({
                      ...prev,
                      workDays: ["월", "화", "수", "목", "금", "토"],
                      workHours: { start: "10:00", end: "19:00" },
                      salary: { base: 2000000, allowance: 150000, bonus: 0 },
                      benefits: ["4대보험", "연차휴가"]
                    }));
                  }}
                >
                  주방직 기본 설정
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full"
                  onClick={() => {
                    setContractForm(prev => ({
                      ...prev,
                      workDays: ["월", "화", "수", "목", "금", "토", "일"],
                      workHours: { start: "11:00", end: "20:00" },
                      salary: { base: 1800000, allowance: 100000, bonus: 0 },
                      benefits: ["4대보험"]
                    }));
                  }}
                >
                  파트타임 기본 설정
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
} 
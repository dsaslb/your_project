"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Save, Settings, User, Clock, DollarSign, CheckCircle, Plus, Trash2, RotateCcw } from "lucide-react";
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface ContractTemplate {
  id: string;
  name: string;
  type: 'regular' | 'kitchen' | 'parttime';
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
  isDefault: boolean;
}

const workDayOptions = ["월", "화", "수", "목", "금", "토", "일"];
const benefitOptions = ["4대보험", "연차휴가", "식대지원", "교통비지원", "야근수당", "휴일수당", "상여금"];

export default function ContractSettingsPage() {
  const router = useRouter();
  const [templates, setTemplates] = useState<ContractTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<ContractTemplate | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [activeTab, setActiveTab] = useState<'templates' | 'positions'>('templates');
  const [positions, setPositions] = useState<string[]>([]);
  const [newPosition, setNewPosition] = useState("");

  // 기본 템플릿 초기화
  useEffect(() => {
    // 로컬 스토리지에서 저장된 템플릿 불러오기
    const savedTemplates = localStorage.getItem('contractTemplates');
    
    if (savedTemplates) {
      setTemplates(JSON.parse(savedTemplates));
    } else {
      const defaultTemplates: ContractTemplate[] = [
        {
          id: "regular-1",
          name: "정규직 기본 설정",
          type: "regular",
          workDays: ["월", "화", "수", "목", "금"],
          workHours: { start: "09:00", end: "18:00" },
          salary: { base: 2500000, allowance: 200000, bonus: 0 },
          probationPeriod: 3,
          noticePeriod: 30,
          benefits: ["4대보험", "연차휴가", "식대지원"],
          responsibilities: "매장 운영 및 고객 서비스",
          terms: "근로기준법에 따른 근무 조건 적용",
          isDefault: true
        },
        {
          id: "kitchen-1",
          name: "주방직 기본 설정",
          type: "kitchen",
          workDays: ["월", "화", "수", "목", "금", "토"],
          workHours: { start: "10:00", end: "19:00" },
          salary: { base: 2000000, allowance: 150000, bonus: 0 },
          probationPeriod: 3,
          noticePeriod: 30,
          benefits: ["4대보험", "연차휴가"],
          responsibilities: "음식 조리 및 주방 관리",
          terms: "위생관리법 준수 및 안전수칙 준수",
          isDefault: true
        },
        {
          id: "parttime-1",
          name: "파트타임 기본 설정",
          type: "parttime",
          workDays: ["월", "화", "수", "목", "금", "토", "일"],
          workHours: { start: "11:00", end: "20:00" },
          salary: { base: 1800000, allowance: 100000, bonus: 0 },
          probationPeriod: 1,
          noticePeriod: 14,
          benefits: ["4대보험"],
          responsibilities: "고객 응대 및 서빙 업무",
          terms: "시급 기준 적용 및 근무 시간 유연성 보장",
          isDefault: true
        }
      ];

      setTemplates(defaultTemplates);
      localStorage.setItem('contractTemplates', JSON.stringify(defaultTemplates));
    }

    // 직책 목록 불러오기
    const savedPositions = localStorage.getItem('restaurantPositions');
    if (savedPositions) {
      setPositions(JSON.parse(savedPositions));
    } else {
      const defaultPositions = [
        "매니저", "주방장", "서버", "주방보조", "홀보조", "캐셔", "배달원", "청소원"
      ];
      setPositions(defaultPositions);
      localStorage.setItem('restaurantPositions', JSON.stringify(defaultPositions));
    }
  }, []);

  // 템플릿 변경 시 로컬 스토리지 업데이트
  useEffect(() => {
    if (templates.length > 0) {
      localStorage.setItem('contractTemplates', JSON.stringify(templates));
    }
  }, [templates]);

  // 직책 추가
  const addPosition = () => {
    const position = newPosition.trim();
    if (position && !positions.includes(position)) {
      const updatedPositions = [...positions, position];
      setPositions(updatedPositions);
      localStorage.setItem('restaurantPositions', JSON.stringify(updatedPositions));
      setNewPosition("");
    }
  };

  // 직책 삭제
  const removePosition = (positionToRemove: string) => {
    if (confirm(`"${positionToRemove}" 직책을 삭제하시겠습니까?`)) {
      const updatedPositions = positions.filter(pos => pos !== positionToRemove);
      setPositions(updatedPositions);
      localStorage.setItem('restaurantPositions', JSON.stringify(updatedPositions));
    }
  };

  // 직책 초기화
  const resetPositions = () => {
    if (confirm("직책 목록을 기본값으로 초기화하시겠습니까?")) {
      const defaultPositions = [
        "매니저", "주방장", "서버", "주방보조", "홀보조", "캐셔", "배달원", "청소원"
      ];
      setPositions(defaultPositions);
      localStorage.setItem('restaurantPositions', JSON.stringify(defaultPositions));
      alert("직책 목록이 기본값으로 초기화되었습니다.");
    }
  };

  const handleWorkDayToggle = (day: string) => {
    if (!selectedTemplate) return;

    setSelectedTemplate(prev => {
      if (!prev) return null;
      return {
        ...prev,
        workDays: prev.workDays.includes(day)
          ? prev.workDays.filter(d => d !== day)
          : [...prev.workDays, day]
      };
    });
  };

  const handleBenefitToggle = (benefit: string) => {
    if (!selectedTemplate) return;

    setSelectedTemplate(prev => {
      if (!prev) return null;
      return {
        ...prev,
        benefits: prev.benefits.includes(benefit)
          ? prev.benefits.filter(b => b !== benefit)
          : [...prev.benefits, benefit]
      };
    });
  };

  const saveTemplate = async () => {
    if (!selectedTemplate) return;

    setIsSaving(true);
    try {
      // 실제로는 API 호출로 저장
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setTemplates(prev => 
        prev.map(template => 
          template.id === selectedTemplate.id ? selectedTemplate : template
        )
      );
      
      setIsEditing(false);
      alert("설정이 저장되었습니다.");
    } catch (error) {
      console.error("저장 실패:", error);
      alert("저장에 실패했습니다.");
    } finally {
      setIsSaving(false);
    }
  };

  const resetToDefault = () => {
    if (!selectedTemplate) return;
    
    if (confirm("기본값으로 초기화하시겠습니까?")) {
      const defaultTemplates: ContractTemplate[] = [
        {
          id: "regular-1",
          name: "정규직 기본 설정",
          type: "regular",
          workDays: ["월", "화", "수", "목", "금"],
          workHours: { start: "09:00", end: "18:00" },
          salary: { base: 2500000, allowance: 200000, bonus: 0 },
          probationPeriod: 3,
          noticePeriod: 30,
          benefits: ["4대보험", "연차휴가", "식대지원"],
          responsibilities: "매장 운영 및 고객 서비스",
          terms: "근로기준법에 따른 근무 조건 적용",
          isDefault: true
        },
        {
          id: "kitchen-1",
          name: "주방직 기본 설정",
          type: "kitchen",
          workDays: ["월", "화", "수", "목", "금", "토"],
          workHours: { start: "10:00", end: "19:00" },
          salary: { base: 2000000, allowance: 150000, bonus: 0 },
          probationPeriod: 3,
          noticePeriod: 30,
          benefits: ["4대보험", "연차휴가"],
          responsibilities: "음식 조리 및 주방 관리",
          terms: "위생관리법 준수 및 안전수칙 준수",
          isDefault: true
        },
        {
          id: "parttime-1",
          name: "파트타임 기본 설정",
          type: "parttime",
          workDays: ["월", "화", "수", "목", "금", "토", "일"],
          workHours: { start: "11:00", end: "20:00" },
          salary: { base: 1800000, allowance: 100000, bonus: 0 },
          probationPeriod: 1,
          noticePeriod: 14,
          benefits: ["4대보험"],
          responsibilities: "고객 응대 및 서빙 업무",
          terms: "시급 기준 적용 및 근무 시간 유연성 보장",
          isDefault: true
        }
      ];

      setTemplates(defaultTemplates);
      localStorage.setItem('contractTemplates', JSON.stringify(defaultTemplates));
      alert("기본값으로 초기화되었습니다.");
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'regular': return 'bg-blue-100 text-blue-800';
      case 'kitchen': return 'bg-orange-100 text-orange-800';
      case 'parttime': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeText = (type: string) => {
    switch (type) {
      case 'regular': return '정규직';
      case 'kitchen': return '주방직';
      case 'parttime': return '파트타임';
      default: return '기타';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 sticky top-0 z-10">
        <div className="px-4 py-4">
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
                <h1 className="text-lg font-bold text-gray-900 dark:text-white">계약서 기본 설정</h1>
                <p className="text-xs text-gray-500 dark:text-gray-400">근무 유형별 기본 설정 관리</p>
              </div>
            </div>
            <div className="flex gap-2">
              {selectedTemplate && isEditing && (
                <Button
                  size="sm"
                  onClick={saveTemplate}
                  disabled={isSaving}
                  className="flex items-center gap-2"
                >
                  <Save className="h-4 w-4" />
                  {isSaving ? "저장중..." : "저장"}
                </Button>
              )}
              <Button
                variant="outline"
                size="sm"
                onClick={resetToDefault}
                className="flex items-center gap-2"
              >
                <RotateCcw className="h-4 w-4" />
                기본값 초기화
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* 탭 네비게이션 */}
      <div className="px-4 pb-4">
        <div className="flex space-x-1 bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
          <button
            onClick={() => setActiveTab('templates')}
            className={`flex-1 px-3 py-2 text-sm font-medium rounded-md transition-colors ${
              activeTab === 'templates'
                ? 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            근무 설정
          </button>
          <button
            onClick={() => setActiveTab('positions')}
            className={`flex-1 px-3 py-2 text-sm font-medium rounded-md transition-colors ${
              activeTab === 'positions'
                ? 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            직책 관리
          </button>
        </div>
      </div>

      <div className="px-4 py-6">
        {activeTab === 'templates' ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* 템플릿 목록 */}
            <div className="lg:col-span-1">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Settings className="h-5 w-5" />
                    근무 유형
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {templates.map((template) => (
                    <div
                      key={template.id}
                      className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                        selectedTemplate?.id === template.id
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                          : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                      }`}
                      onClick={() => {
                        setSelectedTemplate(template);
                        setIsEditing(false);
                      }}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-medium text-gray-900 dark:text-white">
                          {template.name}
                        </h3>
                        <Badge className={getTypeColor(template.type)}>
                          {getTypeText(template.type)}
                        </Badge>
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        <div>근무일: {template.workDays.join(", ")}</div>
                        <div>시간: {template.workHours.start}~{template.workHours.end}</div>
                        <div>기본급: ₩{template.salary.base.toLocaleString()}</div>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>

            {/* 설정 편집 */}
            <div className="lg:col-span-2">
              {selectedTemplate ? (
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="flex items-center gap-2">
                        <User className="h-5 w-5" />
                        {selectedTemplate.name}
                      </CardTitle>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setIsEditing(!isEditing)}
                      >
                        {isEditing ? "취소" : "편집"}
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {/* 기본 정보 */}
                    <div>
                      <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                        기본 정보
                      </h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">
                            템플릿명
                          </label>
                          <Input
                            value={selectedTemplate.name}
                            onChange={(e) => setSelectedTemplate(prev => 
                              prev ? { ...prev, name: e.target.value } : null
                            )}
                            disabled={!isEditing}
                          />
                        </div>
                        <div>
                          <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">
                            유형
                          </label>
                          <Badge className={getTypeColor(selectedTemplate.type)}>
                            {getTypeText(selectedTemplate.type)}
                          </Badge>
                        </div>
                      </div>
                    </div>

                    {/* 근무 조건 */}
                    <div>
                      <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                        근무 조건
                      </h3>
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm text-gray-600 dark:text-gray-400 mb-2">
                            근무일
                          </label>
                          <div className="grid grid-cols-7 gap-2">
                            {workDayOptions.map(day => (
                              <Button
                                key={day}
                                variant={selectedTemplate.workDays.includes(day) ? "default" : "outline"}
                                size="sm"
                                onClick={() => isEditing && handleWorkDayToggle(day)}
                                disabled={!isEditing}
                                className="w-full h-10 text-xs"
                              >
                                {day}
                              </Button>
                            ))}
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">
                              출근 시간
                            </label>
                            <Input
                              type="time"
                              value={selectedTemplate.workHours.start}
                              onChange={(e) => setSelectedTemplate(prev => 
                                prev ? {
                                  ...prev,
                                  workHours: { ...prev.workHours, start: e.target.value }
                                } : null
                              )}
                              disabled={!isEditing}
                            />
                          </div>
                          <div>
                            <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">
                              퇴근 시간
                            </label>
                            <Input
                              type="time"
                              value={selectedTemplate.workHours.end}
                              onChange={(e) => setSelectedTemplate(prev => 
                                prev ? {
                                  ...prev,
                                  workHours: { ...prev.workHours, end: e.target.value }
                                } : null
                              )}
                              disabled={!isEditing}
                            />
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* 급여 조건 */}
                    <div>
                      <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                        급여 조건
                      </h3>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                          <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">
                            기본급
                          </label>
                          <Input
                            type="number"
                            value={selectedTemplate.salary.base}
                            onChange={(e) => setSelectedTemplate(prev => 
                              prev ? {
                                ...prev,
                                salary: { ...prev.salary, base: Number(e.target.value) }
                              } : null
                            )}
                            disabled={!isEditing}
                          />
                        </div>
                        <div>
                          <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">
                            수당
                          </label>
                          <Input
                            type="number"
                            value={selectedTemplate.salary.allowance}
                            onChange={(e) => setSelectedTemplate(prev => 
                              prev ? {
                                ...prev,
                                salary: { ...prev.salary, allowance: Number(e.target.value) }
                              } : null
                            )}
                            disabled={!isEditing}
                          />
                        </div>
                        <div>
                          <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">
                            상여금
                          </label>
                          <Input
                            type="number"
                            value={selectedTemplate.salary.bonus}
                            onChange={(e) => setSelectedTemplate(prev => 
                              prev ? {
                                ...prev,
                                salary: { ...prev.salary, bonus: Number(e.target.value) }
                              } : null
                            )}
                            disabled={!isEditing}
                          />
                        </div>
                      </div>
                    </div>

                    {/* 복리후생 */}
                    <div>
                      <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                        복리후생
                      </h3>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                        {benefitOptions.map(benefit => (
                          <Button
                            key={benefit}
                            variant={selectedTemplate.benefits.includes(benefit) ? "default" : "outline"}
                            size="sm"
                            onClick={() => isEditing && handleBenefitToggle(benefit)}
                            disabled={!isEditing}
                            className="text-sm"
                          >
                            {benefit}
                          </Button>
                        ))}
                      </div>
                    </div>

                    {/* 기타 조건 */}
                    <div>
                      <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                        기타 조건
                      </h3>
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">
                            주요 업무
                          </label>
                          <Textarea
                            value={selectedTemplate.responsibilities}
                            onChange={(e) => setSelectedTemplate(prev => 
                              prev ? { ...prev, responsibilities: e.target.value } : null
                            )}
                            disabled={!isEditing}
                            rows={2}
                          />
                        </div>
                        <div>
                          <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">
                            특별 조건
                          </label>
                          <Textarea
                            value={selectedTemplate.terms}
                            onChange={(e) => setSelectedTemplate(prev => 
                              prev ? { ...prev, terms: e.target.value } : null
                            )}
                            disabled={!isEditing}
                            rows={2}
                          />
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ) : (
                <Card>
                  <CardContent className="py-12">
                    <div className="text-center text-gray-500 dark:text-gray-400">
                      <Settings className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>왼쪽에서 편집할 템플릿을 선택해주세요.</p>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        ) : (
          /* 직책 관리 탭 */
          <div className="max-w-2xl mx-auto">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="h-5 w-5" />
                  직책 관리
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* 새로운 직책 추가 */}
                <div>
                  <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    새로운 직책 추가
                  </h3>
                  <div className="flex gap-2">
                    <Input
                      value={newPosition}
                      onChange={(e) => setNewPosition(e.target.value)}
                      placeholder="새로운 직책을 입력하세요"
                      onKeyPress={(e) => e.key === 'Enter' && addPosition()}
                    />
                    <Button
                      onClick={addPosition}
                      disabled={!newPosition.trim()}
                      className="flex items-center gap-2"
                    >
                      <Plus className="h-4 w-4" />
                      추가
                    </Button>
                  </div>
                </div>

                {/* 직책 목록 */}
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      등록된 직책 목록 ({positions.length}개)
                    </h3>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={resetPositions}
                      className="flex items-center gap-2"
                    >
                      <RotateCcw className="h-4 w-4" />
                      기본값 초기화
                    </Button>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {positions.map((position, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
                      >
                        <span className="font-medium text-gray-900 dark:text-white">
                          {position}
                        </span>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removePosition(position)}
                          className="text-red-600 hover:text-red-700 hover:bg-red-50 dark:text-red-400 dark:hover:text-red-300"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                  {positions.length === 0 && (
                    <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                      등록된 직책이 없습니다.
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
} 
"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Save, FileText, Calendar, Clock, User, DollarSign, CheckCircle, ChevronRight, PenTool, Settings, Plus, Check, AlertCircle, Mail, Phone } from "lucide-react";
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import SignaturePad from '@/components/ui/signature-pad';

interface ContractForm {
  employeeName: string;
  employeeId: string;
  position: string;
  department: string;
  email: string;
  phone: string;
  username: string;
  password: string;
  confirmPassword: string;
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
  employeeSignature: string | null;
  managerSignature: string | null;
}

export default function MobileContractPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isRegistering, setIsRegistering] = useState(false);
  const [contractForm, setContractForm] = useState<ContractForm>({
    employeeName: "",
    employeeId: "",
    position: "",
    department: "",
    email: "",
    phone: "",
    username: "",
    password: "",
    confirmPassword: "",
    startDate: "",
    endDate: "",
    workDays: ["월", "화", "수", "목", "금"],
    workHours: {
      start: "09:00",
      end: "18:00"
    },
    salary: {
      base: 2500000,
      allowance: 200000,
      bonus: 0
    },
    probationPeriod: 3,
    noticePeriod: 1,
    benefits: ["4대보험", "연차휴가"],
    responsibilities: "매장 운영 및 고객 서비스",
    terms: "근로기준법에 따른 근무 조건 적용",
    employeeSignature: null,
    managerSignature: null
  });

  // 직책 관련 상태
  const [positions, setPositions] = useState<string[]>([]);
  const [showPositionDropdown, setShowPositionDropdown] = useState(false);
  const [positionInput, setPositionInput] = useState("");
  const [filteredPositions, setFilteredPositions] = useState<string[]>([]);
  
  // 부서 관련 상태
  const [departments, setDepartments] = useState<string[]>([]);
  const [showDepartmentDropdown, setShowDepartmentDropdown] = useState(false);
  const [departmentInput, setDepartmentInput] = useState("");
  const [filteredDepartments, setFilteredDepartments] = useState<string[]>([]);
  
  const [appliedTemplate, setAppliedTemplate] = useState<string | null>(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedbackMessage, setFeedbackMessage] = useState('');
  const [feedbackType, setFeedbackType] = useState<'success' | 'error'>('success');

  // 설정 직접 작성 모달 상태
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [showSettingsListModal, setShowSettingsListModal] = useState(false);
  const [customSettings, setCustomSettings] = useState({
    name: '',
    workDays: ["월", "화", "수", "목", "금"],
    workHours: { start: "09:00", end: "18:00" },
    salary: { base: 2500000, allowance: 200000, bonus: 0 },
    benefits: ["4대보험", "연차휴가"]
  });
  const [savedSettings, setSavedSettings] = useState<any[]>([]);
  const [isEditMode, setIsEditMode] = useState(false);

  const workDayOptions = ["월", "화", "수", "목", "금", "토", "일"];
  const benefitOptions = ["4대보험", "연차휴가", "식대지원", "교통비지원", "야근수당", "성과급", "교육지원"];

  const steps = [
    { id: 1, title: "기본 정보", icon: User },
    { id: 2, title: "계약 기간", icon: Calendar },
    { id: 3, title: "근무 조건", icon: Clock },
    { id: 4, title: "급여 조건", icon: DollarSign },
    { id: 5, title: "복리후생", icon: CheckCircle },
    { id: 6, title: "기타 조건", icon: FileText },
    { id: 7, title: "사인", icon: PenTool },
  ];

  // 직책 목록 불러오기
  useEffect(() => {
    const savedPositions = localStorage.getItem('positions');
    if (savedPositions) {
      setPositions(JSON.parse(savedPositions));
    } else {
      // 기본 직책 목록
      const defaultPositions = [
        "매니저", "주방장", "서버", "주방보조", "홀보조", "캐셔", "배달원", "청소원"
      ];
      setPositions(defaultPositions);
      localStorage.setItem('positions', JSON.stringify(defaultPositions));
    }
  }, []);

  // 부서 목록 불러오기
  useEffect(() => {
    const savedDepartments = localStorage.getItem('departments');
    if (savedDepartments) {
      setDepartments(JSON.parse(savedDepartments));
    } else {
      // 기본 부서 목록
      const defaultDepartments = [
        "주방", "홀서비스", "매니지먼트", "배달", "청소", "캐셔"
      ];
      setDepartments(defaultDepartments);
      localStorage.setItem('departments', JSON.stringify(defaultDepartments));
    }
  }, []);

  // 저장된 설정 불러오기 (컴퓨터와 연동)
  useEffect(() => {
    const savedSettings = localStorage.getItem('contractSettings');
    if (savedSettings) {
      const settings = JSON.parse(savedSettings);
      if (settings.positions) {
        setPositions(settings.positions);
        localStorage.setItem('positions', JSON.stringify(settings.positions));
      }
      if (settings.departments) {
        setDepartments(settings.departments);
        localStorage.setItem('departments', JSON.stringify(settings.departments));
      }
    }
  }, []);

  // 사용자 정의 설정 목록 불러오기
  useEffect(() => {
    const settings = JSON.parse(localStorage.getItem('customSettings') || '[]');
    setSavedSettings(settings);
  }, []);

  // 직책 필터링
  useEffect(() => {
    if (positionInput.trim() === '') {
      setFilteredPositions(positions);
    } else {
      const filtered = positions.filter(pos => 
        pos.toLowerCase().includes(positionInput.toLowerCase())
      );
      setFilteredPositions(filtered);
    }
  }, [positionInput, positions]);

  // 부서 필터링
  useEffect(() => {
    if (departmentInput.trim() === '') {
      setFilteredDepartments(departments);
    } else {
      const filtered = departments.filter(dept => 
        dept.toLowerCase().includes(departmentInput.toLowerCase())
      );
      setFilteredDepartments(filtered);
    }
  }, [departmentInput, departments]);

  // 새로운 직책 추가
  const addNewPosition = () => {
    const newPosition = positionInput.trim();
    if (newPosition && !positions.includes(newPosition)) {
      const updatedPositions = [...positions, newPosition];
      setPositions(updatedPositions);
      setContractForm(prev => ({ ...prev, position: newPosition }));
      localStorage.setItem('positions', JSON.stringify(updatedPositions));
      setPositionInput("");
      setShowPositionDropdown(false);
    }
  };

  // 새로운 부서 추가
  const addNewDepartment = () => {
    const newDepartment = departmentInput.trim();
    if (newDepartment && !departments.includes(newDepartment)) {
      const updatedDepartments = [...departments, newDepartment];
      setDepartments(updatedDepartments);
      setContractForm(prev => ({ ...prev, department: newDepartment }));
      localStorage.setItem('departments', JSON.stringify(updatedDepartments));
      setDepartmentInput("");
      setShowDepartmentDropdown(false);
    }
  };

  // 직책 선택
  const selectPosition = (position: string) => {
    setContractForm(prev => ({ ...prev, position }));
    setPositionInput(position);
    setShowPositionDropdown(false);
  };

  // 부서 선택
  const selectDepartment = (department: string) => {
    setContractForm(prev => ({ ...prev, department }));
    setDepartmentInput(department);
    setShowDepartmentDropdown(false);
  };

  // 직책 입력 처리
  const handlePositionInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setPositionInput(value);
    setContractForm(prev => ({ ...prev, position: value }));
    setShowPositionDropdown(true);
  };

  // 부서 입력 처리
  const handleDepartmentInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setDepartmentInput(value);
    setContractForm(prev => ({ ...prev, department: value }));
    setShowDepartmentDropdown(true);
  };

  // 직책 입력 포커스
  const handlePositionFocus = () => {
    setFilteredPositions(positions);
    setShowPositionDropdown(true);
  };

  // 부서 입력 포커스
  const handleDepartmentFocus = () => {
    setFilteredDepartments(departments);
    setShowDepartmentDropdown(true);
  };

  // 직책 입력 블러
  const handlePositionBlur = () => {
    setTimeout(() => {
      setShowPositionDropdown(false);
    }, 200);
  };

  // 부서 입력 블러
  const handleDepartmentBlur = () => {
    setTimeout(() => {
      setShowDepartmentDropdown(false);
    }, 200);
  };

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

  // 계약 기간 빠른 설정 함수들
  const setContractPeriod = (period: '1week' | '1month' | '3months' | '6months' | '1year' | '2years') => {
    if (!contractForm.startDate) {
      showFeedbackMessage('시작일을 먼저 설정해주세요.', 'error');
      return;
    }

    const startDate = new Date(contractForm.startDate);
    let endDate = new Date(startDate);

    switch (period) {
      case '1week':
        endDate.setDate(startDate.getDate() + 7);
        break;
      case '1month':
        endDate.setMonth(startDate.getMonth() + 1);
        break;
      case '3months':
        endDate.setMonth(startDate.getMonth() + 3);
        break;
      case '6months':
        endDate.setMonth(startDate.getMonth() + 6);
        break;
      case '1year':
        endDate.setFullYear(startDate.getFullYear() + 1);
        break;
      case '2years':
        endDate.setFullYear(startDate.getFullYear() + 2);
        break;
    }

    // 종료일을 YYYY-MM-DD 형식으로 변환
    const endDateString = endDate.toISOString().split('T')[0];
    
    setContractForm(prev => ({
      ...prev,
      endDate: endDateString
    }));

    showFeedbackMessage('계약 기간이 설정되었습니다!');
  };

  const clearEndDate = () => {
    setContractForm(prev => ({
      ...prev,
      endDate: ""
    }));
  };

  // 설정 직접 작성 함수들
  const applyCustomSettings = () => {
    setContractForm(prev => ({
      ...prev,
      workDays: customSettings.workDays,
      workHours: customSettings.workHours,
      salary: customSettings.salary,
      benefits: customSettings.benefits
    }));
    setShowSettingsModal(false);
    showFeedbackMessage('사용자 정의 설정이 적용되었습니다.', 'success');
  };

  const saveCustomSettings = () => {
    if (!customSettings.name.trim()) {
      showFeedbackMessage('설정 이름을 입력해주세요.', 'error');
      return;
    }

    // 중복 이름 확인
    const existingSettings = JSON.parse(localStorage.getItem('customSettings') || '[]');
    const isDuplicate = existingSettings.some((setting: any) => setting.name === customSettings.name.trim());
    
    if (isDuplicate) {
      showFeedbackMessage('이미 존재하는 설정 이름입니다.', 'error');
      return;
    }

    const newSetting = {
      id: Date.now(),
      ...customSettings,
      createdAt: new Date().toISOString()
    };
    
    existingSettings.push(newSetting);
    localStorage.setItem('customSettings', JSON.stringify(existingSettings));
    setSavedSettings(existingSettings);
    showFeedbackMessage(`"${customSettings.name}" 설정이 저장되었습니다.`, 'success');
    
    // 설정 이름 초기화
    setCustomSettings(prev => ({ ...prev, name: '' }));
  };

  const loadCustomSettings = (setting: any) => {
    setContractForm(prev => ({
      ...prev,
      workDays: setting.workDays,
      workHours: setting.workHours,
      salary: setting.salary,
      benefits: setting.benefits
    }));
    showFeedbackMessage(`"${setting.name}" 설정이 적용되었습니다.`, 'success');
  };

  const deleteCustomSettings = (settingId: number) => {
    const settingToDelete = savedSettings.find(s => s.id === settingId);
    const filteredSettings = savedSettings.filter((s: any) => s.id !== settingId);
    localStorage.setItem('customSettings', JSON.stringify(filteredSettings));
    setSavedSettings(filteredSettings);
    showFeedbackMessage(`"${settingToDelete?.name}" 설정이 삭제되었습니다.`, 'success');
  };

  const editCustomSettings = (setting: any) => {
    setCustomSettings({
      name: setting.name,
      workDays: setting.workDays,
      workHours: setting.workHours,
      salary: setting.salary,
      benefits: setting.benefits
    });
    setIsEditMode(true);
    setShowSettingsModal(true);
  };

  const updateCustomSettings = () => {
    if (!customSettings.name.trim()) {
      showFeedbackMessage('설정 이름을 입력해주세요.', 'error');
      return;
    }

    const updatedSettings = savedSettings.map(setting => {
      if (setting.name === customSettings.name) {
        return {
          ...setting,
          workDays: customSettings.workDays,
          workHours: customSettings.workHours,
          salary: customSettings.salary,
          benefits: customSettings.benefits,
          updatedAt: new Date().toISOString()
        };
      }
      return setting;
    });

    localStorage.setItem('customSettings', JSON.stringify(updatedSettings));
    setSavedSettings(updatedSettings);
    showFeedbackMessage(`"${customSettings.name}" 설정이 수정되었습니다.`, 'success');
    setShowSettingsModal(false);
  };

  const nextStep = () => {
    if (currentStep < steps.length) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  // 직원 등록 및 계약서 생성
  const generateContract = async () => {
    // 필수 필드 검증
    if (!contractForm.employeeName.trim()) {
      showErrorMessage('직원명을 입력해주세요.');
      return;
    }
    if (!contractForm.position.trim()) {
      showErrorMessage('직책을 입력해주세요.');
      return;
    }
    if (!contractForm.department.trim()) {
      showErrorMessage('부서를 입력해주세요.');
      return;
    }
    if (!contractForm.email.trim()) {
      showErrorMessage('이메일을 입력해주세요.');
      return;
    }
    if (!contractForm.phone.trim()) {
      showErrorMessage('전화번호를 입력해주세요.');
      return;
    }
    if (!contractForm.username.trim()) {
      showErrorMessage('아이디를 입력해주세요.');
      return;
    }
    if (!contractForm.password.trim()) {
      showErrorMessage('비밀번호를 입력해주세요.');
      return;
    }
    if (contractForm.password !== contractForm.confirmPassword) {
      showErrorMessage('비밀번호가 일치하지 않습니다.');
      return;
    }

    setIsGenerating(true);
    setIsRegistering(true);
    
    try {
      // 1. 직원 등록
      const employeeData = {
        name: contractForm.employeeName,
        position: contractForm.position,
        department: contractForm.department,
        email: contractForm.email,
        phone: contractForm.phone,
        username: contractForm.username,
        password: contractForm.password,
        join_date: contractForm.startDate,
        salary: contractForm.salary.base.toString(),
        status: 'pending', // 승인 대기 상태로 변경
        contract_type: '정규직',
        contract_start_date: contractForm.startDate,
        contract_expiry_date: contractForm.endDate,
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

      console.log("직원 데이터 전송:", employeeData);
      
      const employeeResponse = await fetch('http://localhost:5000/api/staff', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(employeeData)
      });

      let responseData;
      try {
        responseData = await employeeResponse.json();
      } catch (error) {
        throw new Error('서버 응답을 파싱할 수 없습니다.');
      }
      
      console.log("서버 응답:", responseData);
      
      if (!employeeResponse.ok) {
        throw new Error(`직원 등록 실패: ${responseData.error || '알 수 없는 오류'}`);
      }

      if (!responseData.success) {
        throw new Error(`직원 등록 실패: ${responseData.error || '서버 오류'}`);
      }

      // 2. 계약서 생성
      await new Promise(resolve => setTimeout(resolve, 1000));
      const contractData = {
        ...contractForm,
        totalSalary: contractForm.salary.base + contractForm.salary.allowance + contractForm.salary.bonus,
        generatedDate: new Date().toISOString(),
        signatures: {
          employee: contractForm.employeeSignature,
          manager: contractForm.managerSignature,
          signedAt: new Date().toISOString()
        }
      };
      
      console.log("계약서 생성:", contractData);
      
      showFeedbackMessage("직원 등록 및 계약서가 성공적으로 생성되었습니다!");
      
      // 직원 목록/스케줄 새로고침 이벤트 발생
      window.dispatchEvent(new CustomEvent('staffDataUpdated'));
      
      // 3. 승인 관리 페이지로 이동
      setTimeout(() => {
        router.push("/staff/approval");
      }, 2000);
      
    } catch (error) {
      console.error("계약서 생성 실패:", error);
      showErrorMessage(`오류가 발생했습니다: ${error instanceof Error ? error.message : '알 수 없는 오류'}`);
    } finally {
      setIsGenerating(false);
      setIsRegistering(false);
    }
  };

  const totalSalary = contractForm.salary.base + contractForm.salary.allowance + contractForm.salary.bonus;

  // 저장된 기본 설정 불러오기
  const getSavedTemplates = () => {
    try {
      const savedTemplates = localStorage.getItem('contractTemplates');
      return savedTemplates ? JSON.parse(savedTemplates) : null;
    } catch (error) {
      console.error('설정 불러오기 실패:', error);
      return null;
    }
  };

  // 피드백 메시지 표시 함수
  const showFeedbackMessage = (message: string, type: 'success' | 'error' = 'success') => {
    setFeedbackMessage(message);
    setFeedbackType(type);
    setShowFeedback(true);
    setTimeout(() => setShowFeedback(false), 3000);
  };

  // 에러 메시지 상태
  const [errorMessage, setErrorMessage] = useState('');
  const [showError, setShowError] = useState(false);

  // 에러 메시지 표시 함수
  const showErrorMessage = (message: string) => {
    setErrorMessage(message);
    setShowError(true);
    setTimeout(() => setShowError(false), 5000);
  };

  // 기본 설정 적용 함수 개선
  const applyTemplate = (type: 'regular' | 'kitchen' | 'parttime') => {
    const templates = getSavedTemplates();
    let appliedSettings: any = null;

    if (!templates) {
      // 기본값 사용
      const defaultSettings = {
        regular: {
          workDays: ["월", "화", "수", "목", "금"],
          workHours: { start: "09:00", end: "18:00" },
          salary: { base: 2500000, allowance: 200000, bonus: 0 },
          benefits: ["4대보험", "연차휴가", "식대지원"],
          responsibilities: "매장 운영 및 고객 서비스",
          terms: "근로기준법에 따른 근무 조건 적용"
        },
        kitchen: {
          workDays: ["월", "화", "수", "목", "금", "토"],
          workHours: { start: "10:00", end: "19:00" },
          salary: { base: 2000000, allowance: 150000, bonus: 0 },
          benefits: ["4대보험", "연차휴가"],
          responsibilities: "음식 조리 및 주방 관리",
          terms: "위생관리법 준수 및 안전수칙 준수"
        },
        parttime: {
          workDays: ["월", "화", "수", "목", "금", "토", "일"],
          workHours: { start: "11:00", end: "20:00" },
          salary: { base: 1800000, allowance: 100000, bonus: 0 },
          benefits: ["4대보험"],
          responsibilities: "고객 응대 및 서빙 업무",
          terms: "시급 기준 적용 및 근무 시간 유연성 보장"
        }
      };

      appliedSettings = defaultSettings[type];
      setContractForm(prev => ({
        ...prev,
        ...appliedSettings
      }));
      
      const templateNames = {
        regular: '정규직',
        kitchen: '주방직',
        parttime: '파트타임'
      };
      
      setAppliedTemplate(templateNames[type]);
      showFeedbackMessage(`${templateNames[type]} 기본 설정이 적용되었습니다!`);
      return;
    }

    const template = templates.find((t: any) => t.type === type);
    if (template) {
      appliedSettings = {
        workDays: template.workDays,
        workHours: template.workHours,
        salary: template.salary,
        benefits: template.benefits,
        responsibilities: template.responsibilities,
        terms: template.terms
      };
      
      setContractForm(prev => ({
        ...prev,
        ...appliedSettings
      }));
      
      const templateNames = {
        regular: '정규직',
        kitchen: '주방직',
        parttime: '파트타임'
      };
      
      setAppliedTemplate(templateNames[type]);
      showFeedbackMessage(`${templateNames[type]} 설정이 적용되었습니다!`);
    } else {
      showFeedbackMessage('저장된 설정을 찾을 수 없습니다. 기본값을 사용합니다.', 'error');
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5" />
                기본 정보
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
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
                  이메일 *
                </label>
                <Input
                  type="email"
                  value={contractForm.email}
                  onChange={(e) => setContractForm(prev => ({ ...prev, email: e.target.value }))}
                  placeholder="email@restaurant.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  전화번호 *
                </label>
                <Input
                  value={contractForm.phone}
                  onChange={(e) => setContractForm(prev => ({ ...prev, phone: e.target.value }))}
                  placeholder="010-1234-5678"
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
                  부서 *
                </label>
                <div className="relative">
                  <Input
                    value={departmentInput}
                    onChange={handleDepartmentInputChange}
                    onFocus={handleDepartmentFocus}
                    onBlur={handleDepartmentBlur}
                    placeholder="부서를 입력하거나 선택하세요"
                  />
                  {showDepartmentDropdown && (
                    <div className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                      {filteredDepartments.length > 0 ? (
                        <>
                          {filteredDepartments.map((department, index) => (
                            <div
                              key={index}
                              className="px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer border-b border-gray-100 dark:border-gray-700 last:border-b-0"
                              onClick={() => selectDepartment(department)}
                            >
                              {department}
                            </div>
                          ))}
                          {!filteredDepartments.includes(departmentInput.trim()) && departmentInput.trim() && (
                            <div
                              className="px-4 py-2 hover:bg-blue-50 dark:hover:bg-blue-900/20 cursor-pointer border-t border-gray-200 dark:border-gray-600 text-blue-600 dark:text-blue-400 font-medium"
                              onClick={addNewDepartment}
                            >
                              <Plus className="h-4 w-4 inline mr-2" />
                              "{departmentInput.trim()}" 추가하기
                            </div>
                          )}
                        </>
                      ) : (
                        <div className="px-4 py-2 text-gray-500 dark:text-gray-400">
                          새로운 부서를 추가하세요
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  직책 *
                </label>
                <div className="relative">
                  <Input
                    value={positionInput}
                    onChange={handlePositionInputChange}
                    onFocus={handlePositionFocus}
                    onBlur={handlePositionBlur}
                    placeholder="직책을 입력하거나 선택하세요"
                  />
                  {showPositionDropdown && (
                    <div className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                      {filteredPositions.length > 0 ? (
                        <>
                          {filteredPositions.map((position, index) => (
                            <div
                              key={index}
                              className="px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer border-b border-gray-100 dark:border-gray-700 last:border-b-0"
                              onClick={() => selectPosition(position)}
                            >
                              {position}
                            </div>
                          ))}
                          {!filteredPositions.includes(positionInput.trim()) && positionInput.trim() && (
                            <div
                              className="px-4 py-2 hover:bg-blue-50 dark:hover:bg-blue-900/20 cursor-pointer border-t border-gray-200 dark:border-gray-600 text-blue-600 dark:text-blue-400 font-medium"
                              onClick={addNewPosition}
                            >
                              <Plus className="h-4 w-4 inline mr-2" />
                              "{positionInput.trim()}" 추가하기
                            </div>
                          )}
                        </>
                      ) : (
                        <div className="px-4 py-2 text-gray-500 dark:text-gray-400">
                          새로운 직책을 추가하세요
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* 계정 정보 섹션 */}
              <div className="border-t pt-4 mt-4">
                <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  계정 정보 (직원이 직접 생성)
                </h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      아이디 *
                    </label>
                    <Input
                      value={contractForm.username}
                      onChange={(e) => setContractForm(prev => ({ ...prev, username: e.target.value }))}
                      placeholder="로그인용 아이디를 입력하세요"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      비밀번호 *
                    </label>
                    <Input
                      type="password"
                      value={contractForm.password}
                      onChange={(e) => setContractForm(prev => ({ ...prev, password: e.target.value }))}
                      placeholder="비밀번호를 입력하세요"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      비밀번호 확인 *
                    </label>
                    <Input
                      type="password"
                      value={contractForm.confirmPassword}
                      onChange={(e) => setContractForm(prev => ({ ...prev, confirmPassword: e.target.value }))}
                      placeholder="비밀번호를 다시 입력하세요"
                    />
                    {contractForm.password && contractForm.confirmPassword && contractForm.password !== contractForm.confirmPassword && (
                      <p className="text-red-500 text-xs mt-1">비밀번호가 일치하지 않습니다.</p>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        );

      case 2:
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                계약 기간
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
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

              {/* 빠른 설정 버튼들 */}
              <div className="space-y-3">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  빠른 설정
                </label>
                <div className="grid grid-cols-3 gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => setContractPeriod('1week')}
                    className="text-xs"
                  >
                    1주일
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => setContractPeriod('1month')}
                    className="text-xs"
                  >
                    1개월
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => setContractPeriod('1year')}
                    className="text-xs"
                  >
                    1년
                  </Button>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => setContractPeriod('3months')}
                    className="text-xs"
                  >
                    3개월
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => setContractPeriod('6months')}
                    className="text-xs"
                  >
                    6개월
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => setContractPeriod('2years')}
                    className="text-xs"
                  >
                    2년
                  </Button>
                </div>
                
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={clearEndDate}
                  className="w-full text-xs text-gray-500"
                >
                  종료일 초기화
                </Button>
              </div>

              {/* 계약 기간 표시 */}
              {contractForm.startDate && contractForm.endDate && (
                <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
                  <div className="text-sm text-blue-900 dark:text-blue-100">
                    <div className="font-medium">계약 기간</div>
                    <div className="text-xs mt-1">
                      {new Date(contractForm.startDate).toLocaleDateString('ko-KR')} ~ {new Date(contractForm.endDate).toLocaleDateString('ko-KR')}
                    </div>
                    <div className="text-xs mt-1 text-blue-700 dark:text-blue-200">
                      총 {Math.ceil((new Date(contractForm.endDate).getTime() - new Date(contractForm.startDate).getTime()) / (1000 * 60 * 60 * 24))}일
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        );

      case 3:
        return (
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
                <div className="grid grid-cols-7 gap-2">
                  {workDayOptions.map(day => (
                    <Button
                      key={day}
                      variant={contractForm.workDays.includes(day) ? "default" : "outline"}
                      size="sm"
                      onClick={() => handleWorkDayToggle(day)}
                      className="w-full h-12 text-xs"
                    >
                      {day}
                    </Button>
                  ))}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
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
        );

      case 4:
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <DollarSign className="h-5 w-5" />
                급여 조건
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
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
        );

      case 5:
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5" />
                복리후생
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-2">
                {benefitOptions.map(benefit => (
                  <Button
                    key={benefit}
                    variant={contractForm.benefits.includes(benefit) ? "default" : "outline"}
                    size="sm"
                    onClick={() => handleBenefitToggle(benefit)}
                    className="text-sm"
                  >
                    {benefit}
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>
        );

      case 6:
        return (
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
        );

      case 7:
        return (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PenTool className="h-5 w-5" />
                  계약서 사인
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 mb-4">
                  계약서에 동의하시면 아래에 사인을 해주세요.
                </p>
              </CardContent>
            </Card>

            {/* 직원 사인 */}
            <SignaturePad
              title="직원 사인"
              width={320}
              height={150}
              onSignatureChange={(signature) => 
                setContractForm(prev => ({ ...prev, employeeSignature: signature }))
              }
            />

            {/* 관리자 사인 */}
            <SignaturePad
              title="관리자 사인"
              width={320}
              height={150}
              onSignatureChange={(signature) => 
                setContractForm(prev => ({ ...prev, managerSignature: signature }))
              }
            />

            {/* 계약 동의 체크박스 */}
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-start space-x-3">
                  <input
                    type="checkbox"
                    id="contract-agreement"
                    className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="contract-agreement" className="text-sm text-gray-700">
                    위 계약 조건을 모두 읽고 이해했으며, 이에 동의합니다.
                  </label>
                </div>
              </CardContent>
            </Card>
          </div>
        );

      case 4:
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <DollarSign className="h-5 w-5" />
                급여 조건
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
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
        );

      case 5:
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5" />
                복리후생
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-2">
                {benefitOptions.map(benefit => (
                  <Button
                    key={benefit}
                    variant={contractForm.benefits.includes(benefit) ? "default" : "outline"}
                    size="sm"
                    onClick={() => handleBenefitToggle(benefit)}
                    className="text-sm"
                  >
                    {benefit}
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>
        );

      case 6:
        return (
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
        );

      case 7:
        return (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PenTool className="h-5 w-5" />
                  계약서 사인
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 mb-4">
                  계약서에 동의하시면 아래에 사인을 해주세요.
                </p>
              </CardContent>
            </Card>

            {/* 직원 사인 */}
            <SignaturePad
              title="직원 사인"
              width={320}
              height={150}
              onSignatureChange={(signature) => 
                setContractForm(prev => ({ ...prev, employeeSignature: signature }))
              }
            />

            {/* 관리자 사인 */}
            <SignaturePad
              title="관리자 사인"
              width={320}
              height={150}
              onSignatureChange={(signature) => 
                setContractForm(prev => ({ ...prev, managerSignature: signature }))
              }
            />

            {/* 계약 동의 체크박스 */}
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-start space-x-3">
                  <input
                    type="checkbox"
                    id="contract-agreement"
                    className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="contract-agreement" className="text-sm text-gray-700">
                    위 계약 조건을 모두 읽고 이해했으며, 이에 동의합니다.
                  </label>
                </div>
              </CardContent>
            </Card>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* 피드백 메시지 */}
      {showFeedback && (
        <div className={`fixed top-4 left-1/2 transform -translate-x-1/2 z-50 px-4 py-2 rounded-lg shadow-lg flex items-center gap-2 ${
          feedbackType === 'success' 
            ? 'bg-green-500 text-white' 
            : 'bg-red-500 text-white'
        }`}>
          {feedbackType === 'success' ? (
            <Check className="h-4 w-4" />
          ) : (
            <AlertCircle className="h-4 w-4" />
          )}
          <span className="text-sm font-medium">{feedbackMessage}</span>
        </div>
      )}

      {/* 에러 메시지 */}
      {showError && (
        <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 px-4 py-2 rounded-lg shadow-lg bg-red-500 text-white flex items-center gap-2">
          <AlertCircle className="h-4 w-4" />
          <span className="text-sm font-medium">{errorMessage}</span>
        </div>
      )}

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
                <h1 className="text-lg font-bold text-gray-900 dark:text-white">근로계약서</h1>
                <p className="text-xs text-gray-500 dark:text-gray-400">단계 {currentStep} / {steps.length}</p>
              </div>
            </div>
            <Button
              size="sm"
              onClick={generateContract}
              disabled={isGenerating}
              className="flex items-center gap-2"
            >
              <Save className="h-4 w-4" />
              {isGenerating ? (isRegistering ? "등록중..." : "생성중...") : "저장"}
            </Button>
          </div>
        </div>

        {/* Progress Steps */}
        <div className="px-4 pb-4">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center">
                <div className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${
                  step.id <= currentStep 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-500'
                }`}>
                  {step.id < currentStep ? '✓' : step.id}
                </div>
                {index < steps.length - 1 && (
                  <div className={`w-8 h-0.5 mx-2 ${
                    step.id < currentStep ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'
                  }`} />
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="px-4 py-6">
        {renderStepContent()}

        {/* Navigation */}
        <div className="flex gap-3 mt-6">
          {currentStep > 1 && (
            <Button
              variant="outline"
              onClick={prevStep}
              className="flex-1"
            >
              이전
            </Button>
          )}
          {currentStep < steps.length ? (
            <Button
              onClick={nextStep}
              className="flex-1"
              disabled={
                (currentStep === 1 && (!contractForm.employeeName || !contractForm.position || !contractForm.department || !contractForm.email || !contractForm.phone || !contractForm.username || !contractForm.password || !contractForm.confirmPassword || contractForm.password !== contractForm.confirmPassword)) ||
                (currentStep === 2 && (!contractForm.startDate || !contractForm.endDate)) ||
                (currentStep === 7 && (!contractForm.employeeSignature || !contractForm.managerSignature))
              }
            >
              다음
            </Button>
          ) : (
            <Button
              onClick={generateContract}
              disabled={isGenerating || !contractForm.employeeSignature || !contractForm.managerSignature}
              className="flex-1"
            >
              {isGenerating ? (isRegistering ? "등록중..." : "생성중...") : "계약서 생성"}
            </Button>
          )}
        </div>

        {/* Quick Actions */}
        {currentStep === 1 && (
          <Card className="mt-6">
            <CardHeader>
              <CardTitle className="text-sm flex items-center justify-between">
                <span>빠른 설정</span>
                {appliedTemplate && (
                  <span className="text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 px-2 py-1 rounded">
                    {appliedTemplate} 적용됨
                  </span>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button
                variant="outline"
                size="sm"
                className="w-full"
                onClick={() => applyTemplate('regular')}
              >
                정규직 기본 설정
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="w-full"
                onClick={() => applyTemplate('kitchen')}
              >
                주방직 기본 설정
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="w-full"
                onClick={() => applyTemplate('parttime')}
              >
                파트타임 기본 설정
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="w-full"
                onClick={() => {
                  const settings = {
                    positions,
                    departments,
                    contractForm
                  };
                  localStorage.setItem('contractSettings', JSON.stringify(settings));
                  showFeedbackMessage('설정이 저장되었습니다. (컴퓨터와 연동)', 'success');
                }}
              >
                <Settings className="h-4 w-4 mr-2" />
                현재 설정 저장
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="w-full"
                onClick={() => {
                  const savedSettings = localStorage.getItem('contractSettings');
                  if (savedSettings) {
                    const settings = JSON.parse(savedSettings);
                    setPositions(settings.positions || []);
                    setDepartments(settings.departments || []);
                    setContractForm(settings.contractForm || contractForm);
                    showFeedbackMessage('저장된 설정을 불러왔습니다.', 'success');
                  } else {
                    showFeedbackMessage('저장된 설정이 없습니다.', 'error');
                  }
                }}
              >
                <Settings className="h-4 w-4 mr-2" />
                저장된 설정 불러오기
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="w-full"
                onClick={() => setShowSettingsModal(true)}
              >
                <Settings className="h-4 w-4 mr-2" />
                설정 직접 작성
              </Button>
            </CardContent>
          </Card>
        )}
      </div>

      {/* 설정 직접 작성 모달 */}
      {showSettingsModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 w-full max-w-md max-h-[90vh] overflow-y-auto mx-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">설정 직접 작성</h2>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowSettingsModal(false)}
                className="p-2"
              >
                ✕
              </Button>
            </div>

            <div className="space-y-4">
              {/* 설정 이름 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  설정 이름 *
                </label>
                <Input
                  value={customSettings.name}
                  onChange={(e) => setCustomSettings(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="설정 이름을 입력하세요"
                />
              </div>

              {/* 근무일 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  근무일
                </label>
                <div className="grid grid-cols-7 gap-2">
                  {workDayOptions.map(day => (
                    <Button
                      key={day}
                      variant={customSettings.workDays.includes(day) ? "default" : "outline"}
                      size="sm"
                      onClick={() => {
                        setCustomSettings(prev => ({
                          ...prev,
                          workDays: prev.workDays.includes(day)
                            ? prev.workDays.filter(d => d !== day)
                            : [...prev.workDays, day]
                        }));
                      }}
                      className="w-full h-12 text-xs"
                    >
                      {day}
                    </Button>
                  ))}
                </div>
              </div>

              {/* 근무 시간 */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    출근 시간
                  </label>
                  <Input
                    type="time"
                    value={customSettings.workHours.start}
                    onChange={(e) => setCustomSettings(prev => ({
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
                    value={customSettings.workHours.end}
                    onChange={(e) => setCustomSettings(prev => ({
                      ...prev,
                      workHours: { ...prev.workHours, end: e.target.value }
                    }))}
                  />
                </div>
              </div>

              {/* 급여 */}
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    기본급
                  </label>
                  <Input
                    type="number"
                    value={customSettings.salary.base}
                    onChange={(e) => setCustomSettings(prev => ({
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
                    value={customSettings.salary.allowance}
                    onChange={(e) => setCustomSettings(prev => ({
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
                    value={customSettings.salary.bonus}
                    onChange={(e) => setCustomSettings(prev => ({
                      ...prev,
                      salary: { ...prev.salary, bonus: Number(e.target.value) }
                    }))}
                    placeholder="0"
                  />
                </div>
              </div>

              {/* 복리후생 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  복리후생
                </label>
                <div className="flex flex-wrap gap-2">
                  {benefitOptions.map(benefit => (
                    <Button
                      key={benefit}
                      variant={customSettings.benefits.includes(benefit) ? "default" : "outline"}
                      size="sm"
                      onClick={() => {
                        setCustomSettings(prev => ({
                          ...prev,
                          benefits: prev.benefits.includes(benefit)
                            ? prev.benefits.filter(b => b !== benefit)
                            : [...prev.benefits, benefit]
                        }));
                      }}
                    >
                      {benefit}
                    </Button>
                  ))}
                </div>
              </div>

              {/* 저장된 설정 목록 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  저장된 설정
                </label>
                <div className="space-y-2 max-h-32 overflow-y-auto">
                  {(() => {
                    const savedSettings = JSON.parse(localStorage.getItem('customSettings') || '[]');
                    return savedSettings.length > 0 ? (
                      savedSettings.map((setting: any) => (
                        <div key={setting.id} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded">
                          <span className="text-sm">{setting.name}</span>
                          <div className="flex gap-1">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => loadCustomSettings(setting)}
                            >
                              적용
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => deleteCustomSettings(setting.id)}
                            >
                              삭제
                            </Button>
                          </div>
                        </div>
                      ))
                    ) : (
                      <p className="text-sm text-gray-500 dark:text-gray-400">저장된 설정이 없습니다.</p>
                    );
                  })()}
                </div>
              </div>
            </div>

            <div className="flex gap-2 mt-6">
              <Button
                onClick={applyCustomSettings}
                disabled={!customSettings.name.trim()}
                className="flex-1"
              >
                설정 적용
              </Button>
              <Button
                variant="outline"
                onClick={saveCustomSettings}
                disabled={!customSettings.name.trim()}
                className="flex-1"
              >
                설정 저장
              </Button>
              <Button
                variant="ghost"
                onClick={() => setShowSettingsModal(false)}
              >
                취소
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 
"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Save, Download, FileText, Calendar, Clock, User, Building, DollarSign, CheckCircle, Settings, Plus, Check, AlertCircle, Edit, Trash2 } from "lucide-react";
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
}

export default function ContractPage() {
  const router = useRouter();
  const [isGenerating, setIsGenerating] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [editStaffId, setEditStaffId] = useState<number | null>(null);
  
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
  
  // 피드백 상태
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedbackMessage, setFeedbackMessage] = useState('');
  const [feedbackType, setFeedbackType] = useState<'success' | 'error'>('success');
  const [errorMessage, setErrorMessage] = useState('');
  const [showError, setShowError] = useState(false);

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
    terms: "근로기준법에 따른 근무 조건 적용"
  });

  const workDayOptions = ["월", "화", "수", "목", "금", "토", "일"];
  const benefitOptions = ["4대보험", "연차휴가", "식대지원", "교통비지원", "야근수당", "휴일수당", "상여금"];

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

  // 저장된 설정 불러오기 (모바일과 연동)
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

  // URL 파라미터 확인하여 수정 모드 설정
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const staffId = urlParams.get('staffId');
    const mode = urlParams.get('mode');
    
    if (staffId && mode === 'edit') {
      setIsEditMode(true);
      setEditStaffId(Number(staffId));
      loadStaffData(Number(staffId));
    }
  }, []);

  // 직원 데이터 불러오기 (수정 모드)
  const loadStaffData = async (staffId: number) => {
    try {
      const response = await fetch(`http://localhost:5000/api/staff/${staffId}`, {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          const staff = data.staff;
          setContractForm({
            employeeName: staff.name || '',
            employeeId: staff.id?.toString() || '',
            position: staff.position || '',
            department: staff.department || '',
            email: staff.email || '',
            phone: staff.phone || '',
            username: staff.username || '',
            password: '',
            confirmPassword: '',
            startDate: staff.contracts?.[0]?.start_date || '',
            endDate: staff.contracts?.[0]?.expiry_date || '',
            workDays: ["월", "화", "수", "목", "금"],
            workHours: {
              start: "09:00",
              end: "18:00"
            },
            salary: {
              base: staff.contracts?.[0]?.salary_amount || 2500000,
              allowance: 200000,
              bonus: 0
            },
            probationPeriod: 3,
            noticePeriod: 1,
            benefits: ["4대보험", "연차휴가"],
            responsibilities: "매장 운영 및 고객 서비스",
            terms: "근로기준법에 따른 근무 조건 적용"
          });
        }
      }
    } catch (error) {
      console.error('직원 데이터 로드 실패:', error);
    }
  };

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
      showFeedbackMessage('새 직책이 추가되었습니다.', 'success');
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
      showFeedbackMessage('새 부서가 추가되었습니다.', 'success');
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

  // 피드백 메시지 표시
  const showFeedbackMessage = (message: string, type: 'success' | 'error' = 'success') => {
    setFeedbackMessage(message);
    setFeedbackType(type);
    setShowFeedback(true);
    setTimeout(() => {
      setShowFeedback(false);
    }, 3000);
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

    setContractForm(prev => ({
      ...prev,
      endDate: endDate.toISOString().split('T')[0]
    }));

    showFeedbackMessage(`${period === '1week' ? '1주일' : period === '1month' ? '1개월' : period === '3months' ? '3개월' : period === '6months' ? '6개월' : period === '1year' ? '1년' : '2년'} 계약 기간이 설정되었습니다.`, 'success');
  };

  const clearEndDate = () => {
    setContractForm(prev => ({ ...prev, endDate: "" }));
    showFeedbackMessage('종료일이 초기화되었습니다.', 'success');
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
    // 필수 필드 검증
    if (!contractForm.employeeName.trim()) {
      setErrorMessage('직원명을 입력해주세요.');
      setShowError(true);
      setTimeout(() => setShowError(false), 3000);
      return;
    }
    if (!contractForm.position.trim()) {
      setErrorMessage('직책을 입력해주세요.');
      setShowError(true);
      setTimeout(() => setShowError(false), 3000);
      return;
    }
    if (!contractForm.department.trim()) {
      setErrorMessage('부서를 입력해주세요.');
      setShowError(true);
      setTimeout(() => setShowError(false), 3000);
      return;
    }
    if (!contractForm.email.trim()) {
      setErrorMessage('이메일을 입력해주세요.');
      setShowError(true);
      setTimeout(() => setShowError(false), 3000);
      return;
    }
    if (!contractForm.phone.trim()) {
      setErrorMessage('전화번호를 입력해주세요.');
      setShowError(true);
      setTimeout(() => setShowError(false), 3000);
      return;
    }
    if (!isEditMode && !contractForm.username.trim()) {
      setErrorMessage('아이디를 입력해주세요.');
      setShowError(true);
      setTimeout(() => setShowError(false), 3000);
      return;
    }
    if (!isEditMode && !contractForm.password.trim()) {
      setErrorMessage('비밀번호를 입력해주세요.');
      setShowError(true);
      setTimeout(() => setShowError(false), 3000);
      return;
    }
    if (!isEditMode && contractForm.password !== contractForm.confirmPassword) {
      setErrorMessage('비밀번호가 일치하지 않습니다.');
      setShowError(true);
      setTimeout(() => setShowError(false), 3000);
      return;
    }

    setIsGenerating(true);
    try {
      // 직원 등록/수정 API 호출
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
        status: 'pending',
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

      const url = isEditMode && editStaffId 
        ? `http://localhost:5000/api/staff/${editStaffId}`
        : 'http://localhost:5000/api/staff';
      
      const method = isEditMode ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(employeeData)
      });

      const responseData = await response.json();
      
      if (response.ok && responseData.success) {
        showFeedbackMessage(
          isEditMode ? '직원 정보가 성공적으로 수정되었습니다.' : '직원이 성공적으로 등록되었습니다.',
          'success'
        );
        
        // 직원 목록/스케줄 새로고침 이벤트 발생
        window.dispatchEvent(new CustomEvent('staffDataUpdated'));
        
        // 수정 모드가 아닌 경우 승인 페이지로 이동
        if (!isEditMode) {
          setTimeout(() => {
            router.push("/staff/approval");
          }, 2000);
        }
      } else {
        throw new Error(responseData.error || '등록/수정에 실패했습니다.');
      }
      
    } catch (error) {
      console.error("직원 등록/수정 실패:", error);
      setErrorMessage(error instanceof Error ? error.message : '등록/수정에 실패했습니다.');
      setShowError(true);
      setTimeout(() => setShowError(false), 5000);
    } finally {
      setIsGenerating(false);
    }
  };

  const totalSalary = contractForm.salary.base + contractForm.salary.allowance + contractForm.salary.bonus;

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
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                  {isEditMode ? '근로계약서 수정' : '근로계약서 작성'}
                </h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {isEditMode ? '기존 계약서 내용을 수정하세요' : '직원과의 근로계약서를 작성하세요'}
                </p>
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
                {isEditMode ? '수정 저장' : '저장'}
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
                  <div className="relative">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      직책 *
                    </label>
                    <Input
                      value={positionInput}
                      onChange={handlePositionInputChange}
                      onFocus={handlePositionFocus}
                      onBlur={handlePositionBlur}
                      placeholder="직책을 입력하거나 선택하세요"
                    />
                    {showPositionDropdown && (
                      <div className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md shadow-lg max-h-60 overflow-auto">
                        {filteredPositions.map((position) => (
                          <div
                            key={position}
                            className="px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer"
                            onClick={() => selectPosition(position)}
                          >
                            {position}
                          </div>
                        ))}
                        {positionInput.trim() && !positions.includes(positionInput.trim()) && (
                          <div
                            className="px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer border-t border-gray-200 dark:border-gray-700"
                            onClick={addNewPosition}
                          >
                            <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400">
                              <Plus className="h-4 w-4" />
                              "{positionInput.trim()}" 추가
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  <div className="relative">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      부서 *
                    </label>
                    <Input
                      value={departmentInput}
                      onChange={handleDepartmentInputChange}
                      onFocus={handleDepartmentFocus}
                      onBlur={handleDepartmentBlur}
                      placeholder="부서를 입력하거나 선택하세요"
                    />
                    {showDepartmentDropdown && (
                      <div className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md shadow-lg max-h-60 overflow-auto">
                        {filteredDepartments.map((department) => (
                          <div
                            key={department}
                            className="px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer"
                            onClick={() => selectDepartment(department)}
                          >
                            {department}
                          </div>
                        ))}
                        {departmentInput.trim() && !departments.includes(departmentInput.trim()) && (
                          <div
                            className="px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer border-t border-gray-200 dark:border-gray-700"
                            onClick={addNewDepartment}
                          >
                            <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400">
                              <Plus className="h-4 w-4" />
                              "{departmentInput.trim()}" 추가
                            </div>
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
                        이메일 *
                      </label>
                      <Input
                        type="email"
                        value={contractForm.email}
                        onChange={(e) => setContractForm(prev => ({ ...prev, email: e.target.value }))}
                        placeholder="이메일을 입력하세요"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        전화번호 *
                      </label>
                      <Input
                        type="tel"
                        value={contractForm.phone}
                        onChange={(e) => setContractForm(prev => ({ ...prev, phone: e.target.value }))}
                        placeholder="전화번호를 입력하세요"
                      />
                    </div>
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

            {/* 설정 관리 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="h-5 w-5" />
                  설정 관리
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* 직책 관리 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    직책 관리
                  </label>
                  <div className="space-y-2">
                    <div className="flex gap-2">
                      <Input
                        placeholder="새 직책 추가"
                        value={positionInput}
                        onChange={handlePositionInputChange}
                        className="flex-1"
                      />
                      <Button
                        size="sm"
                        onClick={addNewPosition}
                        disabled={!positionInput.trim() || positions.includes(positionInput.trim())}
                      >
                        추가
                      </Button>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {positions.map((position) => (
                        <Badge key={position} variant="secondary" className="text-xs">
                          {position}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>

                {/* 부서 관리 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    부서 관리
                  </label>
                  <div className="space-y-2">
                    <div className="flex gap-2">
                      <Input
                        placeholder="새 부서 추가"
                        value={departmentInput}
                        onChange={handleDepartmentInputChange}
                        className="flex-1"
                      />
                      <Button
                        size="sm"
                        onClick={addNewDepartment}
                        disabled={!departmentInput.trim() || departments.includes(departmentInput.trim())}
                      >
                        추가
                      </Button>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {departments.map((department) => (
                        <Badge key={department} variant="secondary" className="text-xs">
                          {department}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>

                {/* 빠른 설정 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    빠른 설정
                  </label>
                  <div className="space-y-2">
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
                        showFeedbackMessage('정규직 기본 설정이 적용되었습니다.', 'success');
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
                        showFeedbackMessage('주방직 기본 설정이 적용되었습니다.', 'success');
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
                        showFeedbackMessage('파트타임 기본 설정이 적용되었습니다.', 'success');
                      }}
                    >
                      파트타임 기본 설정
                    </Button>
                  </div>
                </div>

                {/* 설정 직접 작성 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    설정 직접 작성
                  </label>
                  <div className="space-y-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full"
                      onClick={() => setShowSettingsModal(true)}
                    >
                      설정 직접 작성
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full"
                      onClick={() => setShowSettingsListModal(true)}
                    >
                      저장된 설정 관리
                    </Button>
                  </div>
                </div>

                {/* 설정 저장/불러오기 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    설정 저장/불러오기
                  </label>
                  <div className="space-y-2">
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
                        showFeedbackMessage('설정이 저장되었습니다. (모바일과 연동)', 'success');
                      }}
                    >
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
                      저장된 설정 불러오기
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* 설정 목록 관리 모달 */}
      {showSettingsListModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">저장된 설정 관리</h2>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowSettingsListModal(false)}
                className="p-2"
              >
                ✕
              </Button>
            </div>

            {savedSettings.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-gray-500 dark:text-gray-400 mb-4">
                  <Settings className="h-12 w-12 mx-auto mb-2" />
                  <p>저장된 설정이 없습니다.</p>
                </div>
                <Button
                  onClick={() => {
                    setShowSettingsListModal(false);
                    setIsEditMode(false);
                    setCustomSettings({
                      name: '',
                      workDays: ["월", "화", "수", "목", "금"],
                      workHours: { start: "09:00", end: "18:00" },
                      salary: { base: 2500000, allowance: 200000, bonus: 0 },
                      benefits: ["4대보험", "연차휴가"]
                    });
                    setShowSettingsModal(true);
                  }}
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                >
                  첫 번째 설정 만들기
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {savedSettings.map((setting) => (
                    <div
                      key={setting.id}
                      className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow"
                    >
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="font-medium text-gray-900 dark:text-white">{setting.name}</h3>
                        <div className="flex gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => editCustomSettings(setting)}
                            className="p-1 h-8 w-8"
                            title="수정"
                          >
                            <Edit className="h-3 w-3" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => deleteCustomSettings(setting.id)}
                            className="p-1 h-8 w-8 text-red-600 hover:text-red-700"
                            title="삭제"
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                      
                      <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                        <div>
                          <span className="font-medium">근무일:</span> {setting.workDays.join(', ')}
                        </div>
                        <div>
                          <span className="font-medium">근무시간:</span> {setting.workHours.start} ~ {setting.workHours.end}
                        </div>
                        <div>
                          <span className="font-medium">급여:</span> {setting.salary.base.toLocaleString()}원
                          {setting.salary.allowance > 0 && ` + ${setting.salary.allowance.toLocaleString()}원 수당`}
                          {setting.salary.bonus > 0 && ` + ${setting.salary.bonus.toLocaleString()}원 보너스`}
                        </div>
                        <div>
                          <span className="font-medium">복리후생:</span> {setting.benefits.join(', ')}
                        </div>
                      </div>

                      <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                        <Button
                          onClick={() => {
                            loadCustomSettings(setting);
                            setShowSettingsListModal(false);
                          }}
                          className="w-full bg-blue-600 hover:bg-blue-700 text-white text-sm"
                        >
                          이 설정 적용
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="flex justify-center pt-4 border-t border-gray-200 dark:border-gray-700">
                  <Button
                    onClick={() => {
                      setShowSettingsListModal(false);
                      setIsEditMode(false);
                      setCustomSettings({
                        name: '',
                        workDays: ["월", "화", "수", "목", "금"],
                        workHours: { start: "09:00", end: "18:00" },
                        salary: { base: 2500000, allowance: 200000, bonus: 0 },
                        benefits: ["4대보험", "연차휴가"]
                      });
                      setShowSettingsModal(true);
                    }}
                    className="bg-green-600 hover:bg-green-700 text-white"
                  >
                    새 설정 만들기
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 설정 직접 작성 모달 */}
      {showSettingsModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                {isEditMode ? '설정 수정' : '설정 직접 작성'}
              </h2>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setShowSettingsModal(false);
                  setIsEditMode(false);
                }}
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
                  placeholder="설정 이름을 입력하세요 (예: 고급 정규직)"
                  disabled={isEditMode}
                />
                {isEditMode && (
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    설정 이름은 수정할 수 없습니다.
                  </p>
                )}
              </div>

              {/* 근무일 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  근무일
                </label>
                <div className="flex flex-wrap gap-2">
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
                      className="w-12 h-10"
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
              <div className="grid grid-cols-3 gap-4">
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
              {isEditMode ? (
                <Button
                  variant="outline"
                  onClick={updateCustomSettings}
                  disabled={!customSettings.name.trim()}
                  className="flex-1"
                >
                  설정 수정
                </Button>
              ) : (
                <Button
                  variant="outline"
                  onClick={saveCustomSettings}
                  disabled={!customSettings.name.trim()}
                  className="flex-1"
                >
                  설정 저장
                </Button>
              )}
              <Button
                variant="ghost"
                onClick={() => {
                  setShowSettingsModal(false);
                  setIsEditMode(false);
                }}
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
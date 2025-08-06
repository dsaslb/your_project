"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Clock, DollarSign, Calendar, TrendingUp, Users, Building } from 'lucide-react';
import { toast } from 'sonner';

interface Employee {
  id: number;
  username: string;
  name?: string;
  email?: string;
  role: string;
  position?: string;
  department?: string;
  status: string;
  branch_id?: number;
  created_at: string;
}

interface Branch {
  id: number;
  name: string;
  brand_id: number;
  address: string;
  phone: string;
  status: string;
  created_at: string;
}

interface StaffStats {
  totalWorkHours: number;
  targetWorkHours: number;
  monthlySalary: number;
  remainingVacation: number;
  performanceIndex: number;
  totalEmployees: number;
  activeEmployees: number;
}

export default function StaffPage() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [stats, setStats] = useState<StaffStats>({
    totalWorkHours: 0,
    targetWorkHours: 40,
    monthlySalary: 0,
    remainingVacation: 0,
    performanceIndex: 0,
    totalEmployees: 0,
    activeEmployees: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStaffData();
  }, []);

  const fetchStaffData = async () => {
    try {
      setLoading(true);
      
      // 모든 API 호출을 병렬로 실행
      const [employeesRes, branchesRes] = await Promise.all([
        fetch('/api/admin/employees'),
        fetch('/api/admin/branches')
      ]);

      let employeesList: Employee[] = [];
      let branchesList: Branch[] = [];

      // 직원 데이터
      if (employeesRes.ok) {
        const employeesData = await employeesRes.json();
        employeesList = employeesData.data || employeesData.employees || [];
        setEmployees(employeesList);
      }

      // 매장 데이터
      if (branchesRes.ok) {
        const branchesData = await branchesRes.json();
        branchesList = branchesData.data || branchesData.branches || [];
        setBranches(branchesList);
      }

      // 통계 계산 (샘플 데이터)
      const activeEmployees = employeesList.filter(emp => emp.status === 'active').length;
      const totalWorkHours = 32; // 샘플 데이터
      const monthlySalary = 2500000; // 샘플 데이터
      const remainingVacation = 15; // 샘플 데이터
      const performanceIndex = 95; // 샘플 데이터

      setStats({
        totalWorkHours,
        targetWorkHours: 40,
        monthlySalary,
        remainingVacation,
        performanceIndex,
        totalEmployees: employeesList.length,
        activeEmployees
      });

    } catch (error) {
      console.error('직원 데이터 로딩 오류:', error);
      toast.error('데이터를 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 매장 ID로 매장 정보 찾기
  const getBranchName = (branchId?: number) => {
    if (!branchId) return '미지정';
    const branch = branches.find(b => b.id === branchId);
    return branch?.name || '알 수 없음';
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="text-lg mb-2">로딩 중...</div>
            <div className="text-sm text-gray-500">직원 데이터를 가져오는 중입니다</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">직원 대시보드</h1>
        <p className="text-gray-600">개인 업무 및 성과 관리</p>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">이번 주 근무시간</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalWorkHours}시간</div>
            <p className="text-xs text-muted-foreground">목표: {stats.targetWorkHours}시간</p>
          </CardContent>
        </Card>

        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">이번 달 급여</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">₩{stats.monthlySalary.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">예상 급여</p>
          </CardContent>
        </Card>

        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">남은 휴가</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.remainingVacation}일</div>
            <p className="text-xs text-muted-foreground">연차 잔여</p>
          </CardContent>
        </Card>

        <Card className="border border-gray-100">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">성과 지수</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.performanceIndex}%</div>
            <p className="text-xs text-muted-foreground">목표 달성률</p>
          </CardContent>
        </Card>
      </div>

      {/* 직원 현황 */}
      <Card className="border border-gray-100 mb-8">
        <CardHeader>
          <CardTitle>직원 현황</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {employees.slice(0, 6).map((employee) => (
              <div key={employee.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold">{employee.name || employee.username}</h4>
                  <span className={`text-xs px-2 py-1 rounded ${
                    employee.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {employee.status === 'active' ? '정상 근무' : '비활성'}
                  </span>
                </div>
                <div className="space-y-1 text-sm text-gray-600">
                  <p>직책: {employee.position || employee.role}</p>
                  <p>부서: {employee.department || '미지정'}</p>
                  <p>매장: {getBranchName(employee.branch_id)}</p>
                  {employee.email && (
                    <p className="text-xs text-gray-500">{employee.email}</p>
                  )}
                </div>
              </div>
            ))}
            {employees.length === 0 && (
              <div className="col-span-full text-center py-8 text-gray-500">
                등록된 직원이 없습니다.
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* 개인 정보 */}
      <Card className="border border-gray-100">
        <CardHeader>
          <CardTitle>개인 정보</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="border rounded-lg p-4">
              <h4 className="font-semibold">김직원</h4>
              <p className="text-sm text-gray-600">서버</p>
              <p className="text-sm text-gray-600">근무 시작: 2023년 3월</p>
              <p className="text-sm text-green-600">정상 근무</p>
            </div>
            <div className="border rounded-lg p-4">
              <h4 className="font-semibold">근무 스케줄</h4>
              <p className="text-sm text-gray-600">월-금: 09:00-18:00</p>
              <p className="text-sm text-gray-600">토: 10:00-16:00</p>
              <p className="text-sm text-gray-600">일: 휴무</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 

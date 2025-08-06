'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Users, 
  User, 
  Search, 
  Edit, 
  Trash2, 
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Clock,
  Calendar,
  FileText,
  BarChart3,
  Settings,
  Bell,
  TrendingUp,
  Activity,
  Target,
  Award,
  Wifi
} from 'lucide-react';
import { toast } from 'sonner';
import { apiClient, Employee as EmployeeType } from '../../lib/api-client';
import useLoadingState from '@/hooks/useLoadingState';
import useErrorHandler from '@/hooks/useErrorHandler';
import { OfflineStorage } from '@/utils/offlineStorage';

interface EmployeeStats {
  total: number;
  active: number;
  onDuty: number;
  offDuty: number;
  newThisMonth: number;
}

interface WorkSchedule {
  id: string;
  employeeId: string;
  employeeName: string;
  date: string;
  startTime: string;
  endTime: string;
  role: string;
  status: 'scheduled' | 'working' | 'completed' | 'absent' | 'late';
  hours: number;
}

interface PerformanceData {
  id: string;
  employeeId: string;
  employeeName: string;
  period: string;
  salesTarget: number;
  actualSales: number;
  customerSatisfaction: number;
  efficiency: number;
  attendance: number;
  rating: number;
}

interface TrainingData {
  id: string;
  employeeId: string;
  employeeName: string;
  courseName: string;
  completionDate: string;
  score: number;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  certificate: string;
}

interface PayrollData {
  id: string;
  employeeId: string;
  employeeName: string;
  period: string;
  baseSalary: number;
  overtime: number;
  bonuses: number;
  deductions: number;
  netSalary: number;
  status: 'pending' | 'processed' | 'paid';
}

export default function StaffManagement() {
  const [employees, setEmployees] = useState<EmployeeType[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRole, setSelectedRole] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [isOffline, setIsOffline] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  
  const [stats, setStats] = useState<EmployeeStats>({
    total: 0,
    active: 0,
    onDuty: 0,
    offDuty: 0,
    newThisMonth: 0
  });

  const [schedules, setSchedules] = useState<WorkSchedule[]>([]);
  const [performance, setPerformance] = useState<PerformanceData[]>([]);
  const [training, setTraining] = useState<TrainingData[]>([]);
  const [payroll, setPayroll] = useState<PayrollData[]>([]);

  const { isLoading, setLoading, withLoading } = useLoadingState();
  const { handleError } = useErrorHandler();

  // 직원 데이터 로드
  const fetchData = async () => {
    try {
      setLoading(true);
      
      // 실제 API 호출 대신 샘플 데이터 사용
      const sampleEmployees: EmployeeType[] = [
        {
          id: 1,
          name: '김철수',
          email: 'kim@example.com',
          phone: '010-1234-5678',
          position: '매니저',
          store_id: 1,
          status: 'active',
          created_at: '2024-01-15T00:00:00Z',
          updated_at: '2024-01-15T00:00:00Z'
        },
        {
          id: 2,
          name: '이영희',
          email: 'lee@example.com',
          phone: '010-2345-6789',
          position: '바리스타',
          store_id: 1,
          status: 'active',
          created_at: '2024-01-20T00:00:00Z',
          updated_at: '2024-01-20T00:00:00Z'
        },
        {
          id: 3,
          name: '박민수',
          email: 'park@example.com',
          phone: '010-3456-7890',
          position: '캐셔',
          store_id: 2,
          status: 'active',
          created_at: '2024-02-01T00:00:00Z',
          updated_at: '2024-02-01T00:00:00Z'
        }
      ];
      
      setEmployees(sampleEmployees);
      
      // 통계 계산
      const employeeStats: EmployeeStats = {
        total: sampleEmployees.length,
        active: sampleEmployees.filter(emp => emp.status === 'active').length,
        onDuty: Math.floor(sampleEmployees.length * 0.7),
        offDuty: Math.floor(sampleEmployees.length * 0.3),
        newThisMonth: 1
      };
      
      setStats(employeeStats);
      
    } catch (error) {
      handleError(error as Error);
      setIsOffline(true);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (employee: EmployeeType) => {
    if (!confirm(`${employee.name} 직원을 삭제하시겠습니까?`)) return;
    
    try {
      setLoading(true);
      // 실제 API 호출 대신 시뮬레이션
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setEmployees(prev => prev.filter(emp => emp.id !== employee.id));
      toast.success('직원이 삭제되었습니다.');
      
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  const handleActivate = async (employee: EmployeeType) => {
    try {
      setLoading(true);
      // 실제 API 호출 대신 시뮬레이션
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setEmployees(prev => prev.map(emp => 
        emp.id === employee.id 
          ? { ...emp, status: 'active' }
          : emp
      ));
      
      toast.success('직원이 활성화되었습니다.');
      
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (employee: EmployeeType) => {
    // 편집 기능 구현
    toast.info('편집 기능은 추후 구현 예정입니다.');
  };

  useEffect(() => {
    fetchData();
  }, []);

  const filteredEmployees = employees.filter(employee => {
    const matchesSearch = employee.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         employee.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = selectedRole === 'all' || employee.position === selectedRole;
    const matchesStatus = selectedStatus === 'all' || employee.status === selectedStatus;
    
    return matchesSearch && matchesRole && matchesStatus;
  });

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      zIndex: 9999,
      backgroundColor: '#f3f4f6',
      fontFamily: 'Arial, sans-serif',
      overflow: 'auto'
    }}>
      <div style={{
        maxWidth: '1400px',
        margin: '2rem auto',
        padding: '0 2rem'
      }}>
        {/* 헤더 */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '2rem'
        }}>
          <div>
            <h1 style={{
              fontSize: '2rem',
              fontWeight: 'bold',
              color: '#1f2937',
              marginBottom: '0.5rem'
            }}>
              직원 대시보드
            </h1>
            <p style={{
              fontSize: '1.125rem',
              color: '#6b7280'
            }}>
              직원 관리 및 모니터링
            </p>
          </div>
          
          <div style={{
            display: 'flex',
            gap: '1rem',
            alignItems: 'center'
          }}>
            {isOffline && (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.5rem 1rem',
                backgroundColor: '#fef3c7',
                color: '#92400e',
                borderRadius: '6px',
                fontSize: '0.875rem'
              }}>
                <Wifi style={{ width: '16px', height: '16px' }} />
                오프라인 모드
              </div>
            )}
            
            <button
              onClick={fetchData}
              disabled={isLoading}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.75rem 1rem',
                backgroundColor: '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '0.875rem',
                fontWeight: '500',
                cursor: isLoading ? 'not-allowed' : 'pointer',
                opacity: isLoading ? 0.6 : 1
              }}
            >
              <RefreshCw style={{ width: '16px', height: '16px' }} />
              새로고침
            </button>
          </div>
        </div>

        {/* 통계 카드 */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '1.5rem',
          marginBottom: '2rem'
        }}>
          <div style={{
            backgroundColor: '#3b82f6',
            color: 'white',
            padding: '1.5rem',
            borderRadius: '8px'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '1rem'
            }}>
              <h3 style={{ fontSize: '0.875rem', margin: '0' }}>총 직원</h3>
              <Users style={{ width: '20px', height: '20px' }} />
            </div>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0 0 0.5rem 0' }}>
              {stats.total}
            </p>
            <p style={{ fontSize: '0.875rem', opacity: '0.8', margin: '0' }}>
              {stats.active}명 활성
            </p>
          </div>

          <div style={{
            backgroundColor: '#10b981',
            color: 'white',
            padding: '1.5rem',
            borderRadius: '8px'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '1rem'
            }}>
              <h3 style={{ fontSize: '0.875rem', margin: '0' }}>근무중</h3>
              <Clock style={{ width: '20px', height: '20px' }} />
            </div>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0 0 0.5rem 0' }}>
              {stats.onDuty}
            </p>
            <p style={{ fontSize: '0.875rem', opacity: '0.8', margin: '0' }}>
              {stats.offDuty}명 휴무
            </p>
          </div>

          <div style={{
            backgroundColor: '#8b5cf6',
            color: 'white',
            padding: '1.5rem',
            borderRadius: '8px'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '1rem'
            }}>
              <h3 style={{ fontSize: '0.875rem', margin: '0' }}>신규</h3>
              <User style={{ width: '20px', height: '20px' }} />
            </div>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0 0 0.5rem 0' }}>
              {stats.newThisMonth}
            </p>
            <p style={{ fontSize: '0.875rem', opacity: '0.8', margin: '0' }}>
              이번 달 신규
            </p>
          </div>

          <div style={{
            backgroundColor: '#f59e0b',
            color: 'white',
            padding: '1.5rem',
            borderRadius: '8px'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '1rem'
            }}>
              <h3 style={{ fontSize: '0.875rem', margin: '0' }}>평균 성과</h3>
              <BarChart3 style={{ width: '20px', height: '20px' }} />
            </div>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0 0 0.5rem 0' }}>
              85%
            </p>
            <p style={{ fontSize: '0.875rem', opacity: '0.8', margin: '0' }}>
              목표 대비 달성률
            </p>
          </div>
        </div>

        {/* 검색 및 필터 */}
        <div style={{
          backgroundColor: 'white',
          padding: '1.5rem',
          borderRadius: '8px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          marginBottom: '2rem'
        }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '1rem',
            alignItems: 'end'
          }}>
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                검색
              </label>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="이름 또는 이메일로 검색"
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '0.875rem'
                }}
              />
            </div>
            
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                직책
              </label>
              <select
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '0.875rem',
                  backgroundColor: 'white'
                }}
              >
                <option value="all">전체</option>
                <option value="매니저">매니저</option>
                <option value="바리스타">바리스타</option>
                <option value="캐셔">캐셔</option>
              </select>
            </div>
            
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                상태
              </label>
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '0.875rem',
                  backgroundColor: 'white'
                }}
              >
                <option value="all">전체</option>
                <option value="active">활성</option>
                <option value="inactive">비활성</option>
              </select>
            </div>
          </div>
        </div>

        {/* 직원 목록 */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          overflow: 'hidden'
        }}>
          <div style={{
            padding: '1.5rem',
            borderBottom: '1px solid #e5e7eb'
          }}>
            <h2 style={{
              fontSize: '1.25rem',
              fontWeight: 'bold',
              color: '#1f2937',
              margin: '0'
            }}>
              직원 목록 ({filteredEmployees.length}명)
            </h2>
          </div>
          
          <div style={{ overflowX: 'auto' }}>
            <table style={{
              width: '100%',
              borderCollapse: 'collapse'
            }}>
              <thead style={{
                backgroundColor: '#f9fafb',
                borderBottom: '1px solid #e5e7eb'
              }}>
                <tr>
                  <th style={{
                    padding: '1rem',
                    textAlign: 'left',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    color: '#374151'
                  }}>
                    직원명
                  </th>
                  <th style={{
                    padding: '1rem',
                    textAlign: 'left',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    color: '#374151'
                  }}>
                    이메일
                  </th>
                  <th style={{
                    padding: '1rem',
                    textAlign: 'left',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    color: '#374151'
                  }}>
                    전화번호
                  </th>
                  <th style={{
                    padding: '1rem',
                    textAlign: 'left',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    color: '#374151'
                  }}>
                    직책
                  </th>
                  <th style={{
                    padding: '1rem',
                    textAlign: 'left',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    color: '#374151'
                  }}>
                    상태
                  </th>
                  <th style={{
                    padding: '1rem',
                    textAlign: 'left',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    color: '#374151'
                  }}>
                    작업
                  </th>
                </tr>
              </thead>
              <tbody>
                {filteredEmployees.map((employee) => (
                  <tr key={employee.id} style={{
                    borderBottom: '1px solid #e5e7eb'
                  }}>
                    <td style={{
                      padding: '1rem',
                      fontSize: '0.875rem',
                      color: '#374151'
                    }}>
                      {employee.name}
                    </td>
                    <td style={{
                      padding: '1rem',
                      fontSize: '0.875rem',
                      color: '#374151'
                    }}>
                      {employee.email}
                    </td>
                    <td style={{
                      padding: '1rem',
                      fontSize: '0.875rem',
                      color: '#374151'
                    }}>
                      {employee.phone}
                    </td>
                    <td style={{
                      padding: '1rem',
                      fontSize: '0.875rem',
                      color: '#374151'
                    }}>
                      {employee.position}
                    </td>
                    <td style={{
                      padding: '1rem'
                    }}>
                      <span style={{
                        padding: '0.25rem 0.75rem',
                        borderRadius: '9999px',
                        fontSize: '0.75rem',
                        fontWeight: '500',
                        backgroundColor: employee.status === 'active' ? '#dcfce7' : '#fee2e2',
                        color: employee.status === 'active' ? '#166534' : '#991b1b'
                      }}>
                        {employee.status === 'active' ? '활성' : '비활성'}
                      </span>
                    </td>
                    <td style={{
                      padding: '1rem'
                    }}>
                      <div style={{
                        display: 'flex',
                        gap: '0.5rem'
                      }}>
                        <button
                          onClick={() => handleEdit(employee)}
                          style={{
                            padding: '0.5rem',
                            border: '1px solid #d1d5db',
                            borderRadius: '4px',
                            backgroundColor: 'white',
                            color: '#374151',
                            cursor: 'pointer'
                          }}
                        >
                          <Edit style={{ width: '16px', height: '16px' }} />
                        </button>
                        {employee.status === 'inactive' ? (
                          <button
                            onClick={() => handleActivate(employee)}
                            style={{
                              padding: '0.5rem',
                              border: '1px solid #10b981',
                              borderRadius: '4px',
                              backgroundColor: '#10b981',
                              color: 'white',
                              cursor: 'pointer'
                            }}
                          >
                            <CheckCircle style={{ width: '16px', height: '16px' }} />
                          </button>
                        ) : (
                          <button
                            onClick={() => handleDelete(employee)}
                            style={{
                              padding: '0.5rem',
                              border: '1px solid #ef4444',
                              borderRadius: '4px',
                              backgroundColor: '#ef4444',
                              color: 'white',
                              cursor: 'pointer'
                            }}
                          >
                            <Trash2 style={{ width: '16px', height: '16px' }} />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {filteredEmployees.length === 0 && (
            <div style={{
              padding: '3rem',
              textAlign: 'center',
              color: '#6b7280'
            }}>
              <Users style={{ width: '48px', height: '48px', margin: '0 auto 1rem', opacity: '0.5' }} />
              <p>검색 결과가 없습니다.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 
"use client";

import React, { useState, useEffect } from 'react';

interface Store {
  id: number;
  name: string;
  location: string;
  manager: string;
  status: 'operating' | 'maintenance' | 'closed';
  dailySales: number;
  employeeCount: number;
  rating: number;
}

interface EmployeeCreationData {
  employeeName: string;
  employeeEmail: string;
  employeePhone: string;
  position: string;
  department: string;
  hireDate: string;
  salary: string;
}

export default function BranchAdminPage() {
  const [stores, setStores] = useState<Store[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState<EmployeeCreationData>({
    employeeName: '',
    employeeEmail: '',
    employeePhone: '',
    position: '',
    department: '',
    hireDate: '',
    salary: ''
  });
  const [errors, setErrors] = useState<Partial<EmployeeCreationData>>({});

  useEffect(() => {
    // 샘플 데이터 로드
    const sampleStores: Store[] = [
      {
        id: 1,
        name: '강남점',
        location: '서울시 강남구 역삼동',
        manager: '김철수',
        status: 'operating',
        dailySales: 3500000,
        employeeCount: 15,
        rating: 4.8
      },
      {
        id: 2,
        name: '홍대점',
        location: '서울시 마포구 홍대입구',
        manager: '이영희',
        status: 'operating',
        dailySales: 2800000,
        employeeCount: 12,
        rating: 4.6
      },
      {
        id: 3,
        name: '신촌점',
        location: '서울시 서대문구 신촌동',
        manager: '박민수',
        status: 'maintenance',
        dailySales: 0,
        employeeCount: 8,
        rating: 4.7
      },
      {
        id: 4,
        name: '잠실점',
        location: '서울시 송파구 잠실동',
        manager: '최지영',
        status: 'operating',
        dailySales: 4200000,
        employeeCount: 18,
        rating: 4.9
      }
    ];

    setStores(sampleStores);
    setLoading(false);
  }, []);

  const handleInputChange = (field: keyof EmployeeCreationData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // 에러 메시지 초기화
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  const validateForm = () => {
    const newErrors: Partial<EmployeeCreationData> = {};

    if (!formData.employeeName.trim()) {
      newErrors.employeeName = '직원 이름을 입력해주세요';
    }

    if (!formData.employeeEmail.trim()) {
      newErrors.employeeEmail = '직원 이메일을 입력해주세요';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.employeeEmail)) {
      newErrors.employeeEmail = '올바른 이메일 형식을 입력해주세요';
    }

    if (!formData.employeePhone.trim()) {
      newErrors.employeePhone = '직원 전화번호를 입력해주세요';
    } else if (!/^[0-9-]+$/.test(formData.employeePhone)) {
      newErrors.employeePhone = '올바른 전화번호 형식을 입력해주세요';
    }

    if (!formData.position.trim()) {
      newErrors.position = '직책을 입력해주세요';
    }

    if (!formData.department.trim()) {
      newErrors.department = '부서를 입력해주세요';
    }

    if (!formData.hireDate.trim()) {
      newErrors.hireDate = '입사일을 입력해주세요';
    }

    if (!formData.salary.trim()) {
      newErrors.salary = '급여를 입력해주세요';
    } else if (!/^[0-9,]+$/.test(formData.salary.replace(/,/g, ''))) {
      newErrors.salary = '올바른 급여 형식을 입력해주세요';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const generateTempPassword = () => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < 8; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
  };

  const handleCreateEmployeeAndAccount = async () => {
    if (!validateForm()) return;

    setLoading(true);
    
    try {
      // 실제 API 호출 대신 시뮬레이션
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const tempPassword = generateTempPassword();
      
      // 성공 메시지 표시
      alert(`직원 및 직원 계정 생성 완료!\n\n직원: ${formData.employeeName}\n직책: ${formData.position}\n부서: ${formData.department}\n임시 비밀번호: ${tempPassword}\n\n직원은 이메일로 임시 비밀번호를 받게 됩니다.`);
      
      // 폼 초기화
      setFormData({
        employeeName: '',
        employeeEmail: '',
        employeePhone: '',
        position: '',
        department: '',
        hireDate: '',
        salary: ''
      });
      setShowCreateForm(false);
      
    } catch (error) {
      alert('직원 생성 중 오류가 발생했습니다. 다시 시도해주세요.');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'operating': return '#10b981';
      case 'maintenance': return '#f59e0b';
      case 'closed': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'operating': return '운영중';
      case 'maintenance': return '점검중';
      case 'closed': return '폐점';
      default: return '알 수 없음';
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW'
    }).format(amount);
  };

  if (loading) {
    return (
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        zIndex: 9999,
        backgroundColor: '#f3f4f6',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: 'Arial, sans-serif'
      }}>
        <div style={{ fontSize: '1.5rem', color: '#6b7280' }}>로딩 중...</div>
      </div>
    );
  }

  const operatingStores = stores.filter(store => store.status === 'operating');
  const totalSales = operatingStores.reduce((sum, store) => sum + store.dailySales, 0);
  const totalEmployees = stores.reduce((sum, store) => sum + store.employeeCount, 0);
  const averageRating = stores.reduce((sum, store) => sum + store.rating, 0) / stores.length;

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
              매장 관리자 대시보드
            </h1>
            <p style={{
              fontSize: '1.125rem',
              color: '#6b7280'
            }}>
              전체 매장 현황 및 관리
            </p>
          </div>
          <button
            onClick={() => setShowCreateForm(true)}
            style={{
              backgroundColor: '#10b981',
              color: 'white',
              border: 'none',
              padding: '0.75rem 1.5rem',
              borderRadius: '6px',
              fontSize: '0.875rem',
              fontWeight: '500',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
          >
            <span>+</span>
            직원 + 직원 계정 생성
          </button>
        </div>

        {/* 통계 카드 */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '1.5rem',
          marginBottom: '2rem'
        }}>
          <div style={{
            backgroundColor: '#3b82f6',
            color: 'white',
            padding: '1.5rem',
            borderRadius: '8px'
          }}>
            <h3 style={{ fontSize: '0.875rem', marginBottom: '0.5rem' }}>전체 매장</h3>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0' }}>{stores.length}개</p>
            <p style={{ fontSize: '0.875rem', opacity: '0.8', margin: '0.25rem 0 0 0' }}>
              {operatingStores.length}개 운영중
            </p>
          </div>

          <div style={{
            backgroundColor: '#10b981',
            color: 'white',
            padding: '1.5rem',
            borderRadius: '8px'
          }}>
            <h3 style={{ fontSize: '0.875rem', marginBottom: '0.5rem' }}>전체 직원</h3>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0' }}>{totalEmployees}명</p>
            <p style={{ fontSize: '0.875rem', opacity: '0.8', margin: '0.25rem 0 0 0' }}>근무 중인 직원</p>
          </div>

          <div style={{
            backgroundColor: '#8b5cf6',
            color: 'white',
            padding: '1.5rem',
            borderRadius: '8px'
          }}>
            <h3 style={{ fontSize: '0.875rem', marginBottom: '0.5rem' }}>오늘 매출</h3>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0' }}>
              {formatCurrency(totalSales)}
            </p>
            <p style={{ fontSize: '0.875rem', opacity: '0.8', margin: '0.25rem 0 0 0' }}>전체 매장 매출</p>
          </div>

          <div style={{
            backgroundColor: '#f59e0b',
            color: 'white',
            padding: '1.5rem',
            borderRadius: '8px'
          }}>
            <h3 style={{ fontSize: '0.875rem', marginBottom: '0.5rem' }}>평균 평점</h3>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0' }}>
              {averageRating.toFixed(1)}
            </p>
            <p style={{ fontSize: '0.875rem', opacity: '0.8', margin: '0.25rem 0 0 0' }}>고객 만족도</p>
          </div>
        </div>

        {/* 매장 목록 */}
        <div style={{
          backgroundColor: 'white',
          padding: '2rem',
          borderRadius: '8px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
        }}>
          <h2 style={{
            fontSize: '1.5rem',
            fontWeight: 'bold',
            color: '#1f2937',
            marginBottom: '1.5rem'
          }}>
            매장 목록
          </h2>

          <div style={{
            display: 'grid',
            gap: '1rem'
          }}>
            {stores.map((store) => (
              <div key={store.id} style={{
                display: 'flex',
                alignItems: 'center',
                padding: '1.5rem',
                backgroundColor: '#f9fafb',
                borderRadius: '8px',
                border: '1px solid #e5e7eb'
              }}>
                <div style={{ flex: '1' }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    marginBottom: '0.5rem'
                  }}>
                    <h3 style={{
                      fontSize: '1.125rem',
                      fontWeight: 'bold',
                      color: '#1f2937',
                      margin: '0 0.5rem 0 0'
                    }}>
                      {store.name}
                    </h3>
                    <span style={{
                      backgroundColor: getStatusColor(store.status),
                      color: 'white',
                      padding: '0.25rem 0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.75rem',
                      fontWeight: '500'
                    }}>
                      {getStatusText(store.status)}
                    </span>
                  </div>
                  <p style={{
                    fontSize: '0.875rem',
                    color: '#6b7280',
                    margin: '0 0 0.5rem 0'
                  }}>
                    {store.location}
                  </p>
                  <p style={{
                    fontSize: '0.875rem',
                    color: '#6b7280',
                    margin: '0'
                  }}>
                    매니저: {store.manager} | 직원: {store.employeeCount}명
                  </p>
                </div>

                <div style={{
                  textAlign: 'right',
                  marginLeft: '1rem'
                }}>
                  <div style={{
                    fontSize: '1.25rem',
                    fontWeight: 'bold',
                    color: '#1f2937',
                    marginBottom: '0.25rem'
                  }}>
                    {store.status === 'operating' ? formatCurrency(store.dailySales) : '-'}
                  </div>
                  <div style={{
                    fontSize: '0.875rem',
                    color: '#6b7280'
                  }}>
                    평점: {store.rating}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 직원 + 직원 계정 생성 모달 */}
      {showCreateForm && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 10000
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '2rem',
            borderRadius: '8px',
            maxWidth: '600px',
            width: '90%',
            maxHeight: '90vh',
            overflow: 'auto'
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '1.5rem'
            }}>
              <h2 style={{
                fontSize: '1.5rem',
                fontWeight: 'bold',
                color: '#1f2937',
                margin: '0'
              }}>
                직원 + 직원 계정 생성
              </h2>
              <button
                onClick={() => setShowCreateForm(false)}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: '1.5rem',
                  cursor: 'pointer',
                  color: '#6b7280'
                }}
              >
                ×
              </button>
            </div>

            <div style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: '600', color: '#374151', marginBottom: '1rem' }}>
                직원 정보
              </h3>
              
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                  직원 이름 *
                </label>
                <input
                  type="text"
                  value={formData.employeeName}
                  onChange={(e) => handleInputChange('employeeName', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: errors.employeeName ? '1px solid #ef4444' : '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '0.875rem'
                  }}
                  placeholder="예: 김영희"
                />
                {errors.employeeName && (
                  <p style={{ color: '#ef4444', fontSize: '0.75rem', marginTop: '0.25rem' }}>
                    {errors.employeeName}
                  </p>
                )}
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                  직원 이메일 *
                </label>
                <input
                  type="email"
                  value={formData.employeeEmail}
                  onChange={(e) => handleInputChange('employeeEmail', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: errors.employeeEmail ? '1px solid #ef4444' : '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '0.875rem'
                  }}
                  placeholder="예: employee@store.com"
                />
                {errors.employeeEmail && (
                  <p style={{ color: '#ef4444', fontSize: '0.75rem', marginTop: '0.25rem' }}>
                    {errors.employeeEmail}
                  </p>
                )}
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                  직원 전화번호 *
                </label>
                <input
                  type="text"
                  value={formData.employeePhone}
                  onChange={(e) => handleInputChange('employeePhone', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: errors.employeePhone ? '1px solid #ef4444' : '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '0.875rem'
                  }}
                  placeholder="예: 010-1234-5678"
                />
                {errors.employeePhone && (
                  <p style={{ color: '#ef4444', fontSize: '0.75rem', marginTop: '0.25rem' }}>
                    {errors.employeePhone}
                  </p>
                )}
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                  직책 *
                </label>
                <input
                  type="text"
                  value={formData.position}
                  onChange={(e) => handleInputChange('position', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: errors.position ? '1px solid #ef4444' : '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '0.875rem'
                  }}
                  placeholder="예: 바리스타"
                />
                {errors.position && (
                  <p style={{ color: '#ef4444', fontSize: '0.75rem', marginTop: '0.25rem' }}>
                    {errors.position}
                  </p>
                )}
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                  부서 *
                </label>
                <input
                  type="text"
                  value={formData.department}
                  onChange={(e) => handleInputChange('department', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: errors.department ? '1px solid #ef4444' : '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '0.875rem'
                  }}
                  placeholder="예: 커피팀"
                />
                {errors.department && (
                  <p style={{ color: '#ef4444', fontSize: '0.75rem', marginTop: '0.25rem' }}>
                    {errors.department}
                  </p>
                )}
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                  입사일 *
                </label>
                <input
                  type="date"
                  value={formData.hireDate}
                  onChange={(e) => handleInputChange('hireDate', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: errors.hireDate ? '1px solid #ef4444' : '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '0.875rem'
                  }}
                />
                {errors.hireDate && (
                  <p style={{ color: '#ef4444', fontSize: '0.75rem', marginTop: '0.25rem' }}>
                    {errors.hireDate}
                  </p>
                )}
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                  급여 *
                </label>
                <input
                  type="text"
                  value={formData.salary}
                  onChange={(e) => handleInputChange('salary', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: errors.salary ? '1px solid #ef4444' : '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '0.875rem'
                  }}
                  placeholder="예: 2,500,000"
                />
                {errors.salary && (
                  <p style={{ color: '#ef4444', fontSize: '0.75rem', marginTop: '0.25rem' }}>
                    {errors.salary}
                  </p>
                )}
              </div>
            </div>

            <div style={{
              display: 'flex',
              gap: '1rem',
              justifyContent: 'flex-end'
            }}>
              <button
                onClick={() => setShowCreateForm(false)}
                style={{
                  padding: '0.75rem 1.5rem',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  backgroundColor: 'white',
                  color: '#374151',
                  fontSize: '0.875rem',
                  fontWeight: '500',
                  cursor: 'pointer'
                }}
                disabled={loading}
              >
                취소
              </button>
              <button
                onClick={handleCreateEmployeeAndAccount}
                disabled={loading}
                style={{
                  padding: '0.75rem 1.5rem',
                  border: 'none',
                  borderRadius: '6px',
                  backgroundColor: loading ? '#9ca3af' : '#10b981',
                  color: 'white',
                  fontSize: '0.875rem',
                  fontWeight: '500',
                  cursor: loading ? 'not-allowed' : 'pointer'
                }}
              >
                {loading ? '생성 중...' : '직원 + 직원 계정 생성'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 
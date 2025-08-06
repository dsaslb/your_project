"use client";

import React, { useState } from 'react';

interface StoreCreationData {
  storeName: string;
  location: string;
  phone: string;
  managerName: string;
  managerEmail: string;
  managerPhone: string;
}

export default function BrandAdminPage() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState<StoreCreationData>({
    storeName: '',
    location: '',
    phone: '',
    managerName: '',
    managerEmail: '',
    managerPhone: ''
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Partial<StoreCreationData>>({});

  const handleInputChange = (field: keyof StoreCreationData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // 에러 메시지 초기화
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  const validateForm = () => {
    const newErrors: Partial<StoreCreationData> = {};

    if (!formData.storeName.trim()) {
      newErrors.storeName = '매장명을 입력해주세요';
    }

    if (!formData.location.trim()) {
      newErrors.location = '매장 위치를 입력해주세요';
    }

    if (!formData.phone.trim()) {
      newErrors.phone = '매장 전화번호를 입력해주세요';
    } else if (!/^[0-9-]+$/.test(formData.phone)) {
      newErrors.phone = '올바른 전화번호 형식을 입력해주세요';
    }

    if (!formData.managerName.trim()) {
      newErrors.managerName = '매장 관리자 이름을 입력해주세요';
    }

    if (!formData.managerEmail.trim()) {
      newErrors.managerEmail = '매장 관리자 이메일을 입력해주세요';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.managerEmail)) {
      newErrors.managerEmail = '올바른 이메일 형식을 입력해주세요';
    }

    if (!formData.managerPhone.trim()) {
      newErrors.managerPhone = '매장 관리자 전화번호를 입력해주세요';
    } else if (!/^[0-9-]+$/.test(formData.managerPhone)) {
      newErrors.managerPhone = '올바른 전화번호 형식을 입력해주세요';
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

  const handleCreateStoreAndManager = async () => {
    if (!validateForm()) return;

    setLoading(true);
    
    try {
      // 실제 API 호출 대신 시뮬레이션
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const tempPassword = generateTempPassword();
      
      // 성공 메시지 표시 (실제로는 toast 사용)
      alert(`매장 및 매장 관리자 생성 완료!\n\n매장: ${formData.storeName}\n매장 관리자: ${formData.managerName}\n임시 비밀번호: ${tempPassword}\n\n매장 관리자는 이메일로 임시 비밀번호를 받게 됩니다.`);
      
      // 폼 초기화
      setFormData({
        storeName: '',
        location: '',
        phone: '',
        managerName: '',
        managerEmail: '',
        managerPhone: ''
      });
      setShowCreateForm(false);
      
    } catch (error) {
      alert('매장 생성 중 오류가 발생했습니다. 다시 시도해주세요.');
    } finally {
      setLoading(false);
    }
  };

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
        maxWidth: '1200px',
        margin: '2rem auto',
        backgroundColor: 'white',
        padding: '2rem',
        borderRadius: '8px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
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
              브랜드 관리자 대시보드
            </h1>
            <p style={{
              fontSize: '1.125rem',
              color: '#6b7280'
            }}>
              스타벅스 브랜드 전체 관리 및 모니터링
            </p>
          </div>
          <button
            onClick={() => setShowCreateForm(true)}
            style={{
              backgroundColor: '#3b82f6',
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
            매장 + 매장 관리자 생성
          </button>
        </div>

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
            <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0' }}>12개</p>
            <p style={{ fontSize: '0.875rem', opacity: '0.8', margin: '0.25rem 0 0 0' }}>10개 운영중</p>
          </div>

          <div style={{
            backgroundColor: '#10b981',
            color: 'white',
            padding: '1.5rem',
            borderRadius: '8px'
          }}>
            <h3 style={{ fontSize: '0.875rem', marginBottom: '0.5rem' }}>전체 직원</h3>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0' }}>156명</p>
            <p style={{ fontSize: '0.875rem', opacity: '0.8', margin: '0.25rem 0 0 0' }}>근무 중인 직원</p>
          </div>

          <div style={{
            backgroundColor: '#8b5cf6',
            color: 'white',
            padding: '1.5rem',
            borderRadius: '8px'
          }}>
            <h3 style={{ fontSize: '0.875rem', marginBottom: '0.5rem' }}>오늘 매출</h3>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0' }}>₩15.2M</p>
            <p style={{ fontSize: '0.875rem', opacity: '0.8', margin: '0.25rem 0 0 0' }}>브랜드 전체 매출</p>
          </div>

          <div style={{
            backgroundColor: '#f59e0b',
            color: 'white',
            padding: '1.5rem',
            borderRadius: '8px'
          }}>
            <h3 style={{ fontSize: '0.875rem', marginBottom: '0.5rem' }}>평균 평점</h3>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0' }}>4.8</p>
            <p style={{ fontSize: '0.875rem', opacity: '0.8', margin: '0.25rem 0 0 0' }}>고객 만족도</p>
          </div>
        </div>

        <div style={{
          backgroundColor: '#f9fafb',
          padding: '1.5rem',
          borderRadius: '8px',
          border: '1px solid #e5e7eb'
        }}>
          <h2 style={{
            fontSize: '1.5rem',
            fontWeight: 'bold',
            color: '#1f2937',
            marginBottom: '1rem'
          }}>
            최근 활동
          </h2>

          <div style={{ display: 'flex', alignItems: 'center', padding: '1rem', backgroundColor: 'white', borderRadius: '4px', marginBottom: '0.5rem' }}>
            <div style={{ width: '12px', height: '12px', backgroundColor: '#10b981', borderRadius: '50%', marginRight: '1rem' }}></div>
            <div style={{ flex: '1' }}>
              <p style={{ fontWeight: '500', color: '#1f2937', margin: '0' }}>강남점 매출 업데이트</p>
              <p style={{ fontSize: '0.875rem', color: '#6b7280', margin: '0' }}>일일 매출: ₩3,500,000</p>
            </div>
            <span style={{ fontSize: '0.875rem', color: '#9ca3af' }}>2분 전</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', padding: '1rem', backgroundColor: 'white', borderRadius: '4px', marginBottom: '0.5rem' }}>
            <div style={{ width: '12px', height: '12px', backgroundColor: '#3b82f6', borderRadius: '50%', marginRight: '1rem' }}></div>
            <div style={{ flex: '1' }}>
              <p style={{ fontWeight: '500', color: '#1f2937', margin: '0' }}>홍대점 직원 추가</p>
              <p style={{ fontSize: '0.875rem', color: '#6b7280', margin: '0' }}>새 직원: 김영희 (바리스타)</p>
            </div>
            <span style={{ fontSize: '0.875rem', color: '#9ca3af' }}>15분 전</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', padding: '1rem', backgroundColor: 'white', borderRadius: '4px' }}>
            <div style={{ width: '12px', height: '12px', backgroundColor: '#8b5cf6', borderRadius: '50%', marginRight: '1rem' }}></div>
            <div style={{ flex: '1' }}>
              <p style={{ fontWeight: '500', color: '#1f2937', margin: '0' }}>신촌점 점검 완료</p>
              <p style={{ fontSize: '0.875rem', color: '#6b7280', margin: '0' }}>정기 점검 및 유지보수 완료</p>
            </div>
            <span style={{ fontSize: '0.875rem', color: '#9ca3af' }}>1시간 전</span>
          </div>
        </div>
      </div>

      {/* 매장 + 매장 관리자 생성 모달 */}
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
                매장 + 매장 관리자 생성
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
                매장 정보
              </h3>
              
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                  매장명 *
                </label>
                <input
                  type="text"
                  value={formData.storeName}
                  onChange={(e) => handleInputChange('storeName', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: errors.storeName ? '1px solid #ef4444' : '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '0.875rem'
                  }}
                  placeholder="예: 강남점"
                />
                {errors.storeName && (
                  <p style={{ color: '#ef4444', fontSize: '0.75rem', marginTop: '0.25rem' }}>
                    {errors.storeName}
                  </p>
                )}
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                  매장 위치 *
                </label>
                <input
                  type="text"
                  value={formData.location}
                  onChange={(e) => handleInputChange('location', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: errors.location ? '1px solid #ef4444' : '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '0.875rem'
                  }}
                  placeholder="예: 서울시 강남구 역삼동 123-45"
                />
                {errors.location && (
                  <p style={{ color: '#ef4444', fontSize: '0.75rem', marginTop: '0.25rem' }}>
                    {errors.location}
                  </p>
                )}
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                  매장 전화번호 *
                </label>
                <input
                  type="text"
                  value={formData.phone}
                  onChange={(e) => handleInputChange('phone', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: errors.phone ? '1px solid #ef4444' : '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '0.875rem'
                  }}
                  placeholder="예: 02-1234-5678"
                />
                {errors.phone && (
                  <p style={{ color: '#ef4444', fontSize: '0.75rem', marginTop: '0.25rem' }}>
                    {errors.phone}
                  </p>
                )}
              </div>
            </div>

            <div style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: '600', color: '#374151', marginBottom: '1rem' }}>
                매장 관리자 정보
              </h3>
              
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                  관리자 이름 *
                </label>
                <input
                  type="text"
                  value={formData.managerName}
                  onChange={(e) => handleInputChange('managerName', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: errors.managerName ? '1px solid #ef4444' : '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '0.875rem'
                  }}
                  placeholder="예: 김철수"
                />
                {errors.managerName && (
                  <p style={{ color: '#ef4444', fontSize: '0.75rem', marginTop: '0.25rem' }}>
                    {errors.managerName}
                  </p>
                )}
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                  관리자 이메일 *
                </label>
                <input
                  type="email"
                  value={formData.managerEmail}
                  onChange={(e) => handleInputChange('managerEmail', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: errors.managerEmail ? '1px solid #ef4444' : '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '0.875rem'
                  }}
                  placeholder="예: manager@store.com"
                />
                {errors.managerEmail && (
                  <p style={{ color: '#ef4444', fontSize: '0.75rem', marginTop: '0.25rem' }}>
                    {errors.managerEmail}
                  </p>
                )}
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                  관리자 전화번호 *
                </label>
                <input
                  type="text"
                  value={formData.managerPhone}
                  onChange={(e) => handleInputChange('managerPhone', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: errors.managerPhone ? '1px solid #ef4444' : '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '0.875rem'
                  }}
                  placeholder="예: 010-1234-5678"
                />
                {errors.managerPhone && (
                  <p style={{ color: '#ef4444', fontSize: '0.75rem', marginTop: '0.25rem' }}>
                    {errors.managerPhone}
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
                onClick={handleCreateStoreAndManager}
                disabled={loading}
                style={{
                  padding: '0.75rem 1.5rem',
                  border: 'none',
                  borderRadius: '6px',
                  backgroundColor: loading ? '#9ca3af' : '#3b82f6',
                  color: 'white',
                  fontSize: '0.875rem',
                  fontWeight: '500',
                  cursor: loading ? 'not-allowed' : 'pointer'
                }}
              >
                {loading ? '생성 중...' : '매장 + 매장 관리자 생성'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 
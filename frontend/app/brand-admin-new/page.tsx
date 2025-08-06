"use client";

import React from 'react';

export default function BrandAdminNewPage() {
  return (
    <div style={{ 
      minHeight: '100vh', 
      backgroundColor: '#f3f4f6', 
      padding: '2rem',
      fontFamily: 'Arial, sans-serif'
    }}>
      <div style={{ 
        maxWidth: '1200px', 
        margin: '0 auto',
        backgroundColor: 'white',
        padding: '2rem',
        borderRadius: '8px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
      }}>
        <h1 style={{ 
          fontSize: '2rem', 
          fontWeight: 'bold', 
          color: '#1f2937',
          marginBottom: '1rem',
          textAlign: 'center'
        }}>
          브랜드 관리자 대시보드 (새 버전)
        </h1>
        
        <p style={{ 
          fontSize: '1.125rem', 
          color: '#6b7280',
          textAlign: 'center',
          marginBottom: '2rem'
        }}>
          스타벅스 브랜드 전체 관리 및 모니터링
        </p>
        
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
    </div>
  );
} 
import React from 'react';
import Link from 'next/link';

const HomePage = () => {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">멀티테넌시 관리 시스템</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Link href="/admin/industry" className="block">
          <div className="border rounded-lg p-6 hover:shadow-lg transition-shadow">
            <h2 className="text-xl font-semibold mb-2">업종(레스토랑) 관리자</h2>
            <p className="text-gray-600">전체 브랜드/매장 현황 및 플러그인 관리</p>
          </div>
        </Link>
        
        <Link href="/admin/brand" className="block">
          <div className="border rounded-lg p-6 hover:shadow-lg transition-shadow">
            <h2 className="text-xl font-semibold mb-2">브랜드 관리자</h2>
            <p className="text-gray-600">매장/직원/매출 관리 및 AI 분석 리포트</p>
          </div>
        </Link>
        
        <Link href="/admin/branch" className="block">
          <div className="border rounded-lg p-6 hover:shadow-lg transition-shadow">
            <h2 className="text-xl font-semibold mb-2">매장 관리자</h2>
            <p className="text-gray-600">직원/매출/발주/재고 및 플러그인 권한 관리</p>
          </div>
        </Link>
        
        <Link href="/user" className="block">
          <div className="border rounded-lg p-6 hover:shadow-lg transition-shadow">
            <h2 className="text-xl font-semibold mb-2">직원(사용자)</h2>
            <p className="text-gray-600">근무/급여 및 본인 권한 플러그인 사용</p>
          </div>
        </Link>
      </div>
      
      <div className="mt-8 p-6 bg-blue-50 rounded-lg">
        <h3 className="text-lg font-semibold mb-2">시스템 특징</h3>
        <ul className="list-disc list-inside space-y-1 text-gray-700">
          <li>업종 → 브랜드 → 매장 → 직원 계층별 관리</li>
          <li>플러그인 ON/OFF 및 권한 분배 시스템</li>
          <li>출근, 재고, 구매, 스케줄, AI 분석 플러그인</li>
          <li>실시간 데이터 연동 및 샘플 데이터 지원</li>
        </ul>
      </div>
    </div>
  );
};

export default HomePage; 
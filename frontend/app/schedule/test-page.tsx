'use client';

import React from 'react';

const TestPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          스케줄 관리 시스템 테스트
        </h1>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 mb-4">
            이 페이지가 정상적으로 표시된다면 React와 Tailwind CSS가 작동하고 있습니다.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-100 p-4 rounded-lg">
              <h3 className="font-semibold text-blue-800">인력 배치</h3>
              <p className="text-blue-600">최적화된 인력 배치 관리</p>
            </div>
            <div className="bg-green-100 p-4 rounded-lg">
              <h3 className="font-semibold text-green-800">출퇴근 관리</h3>
              <p className="text-green-600">실시간 출퇴근 체크</p>
            </div>
            <div className="bg-purple-100 p-4 rounded-lg">
              <h3 className="font-semibold text-purple-800">AI 분석</h3>
              <p className="text-purple-600">스케줄 효율성 분석</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TestPage;

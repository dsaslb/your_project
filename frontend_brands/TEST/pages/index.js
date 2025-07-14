import React from 'react';

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-center text-gray-800 mb-8">
          테스트브랜드 관리 시스템
        </h1>
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-semibold mb-4">환영합니다!</h2>
          <p className="text-gray-600">
            테스트브랜드의 관리 시스템에 오신 것을 환영합니다.
          </p>
        </div>
      </div>
    </div>
  );
}

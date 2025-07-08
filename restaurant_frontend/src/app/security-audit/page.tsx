import React from 'react';

export default function SecurityAuditPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center py-12">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">보안 감사</h1>
          <p className="text-gray-600 mb-8">보안 감사 기능이 임시로 비활성화되었습니다.</p>
          <div className="bg-white rounded-lg shadow-sm border p-8">
            <p className="text-gray-500">빌드 오류 수정 후 다시 활성화됩니다.</p>
            <p className="text-sm text-gray-400 mt-2">현재 기본 기능만 사용 가능합니다.</p>
          </div>
        </div>
      </div>
    </div>
  );
} 
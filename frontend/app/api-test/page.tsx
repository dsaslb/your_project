'use client';

import { useState, useEffect } from 'react';
import { ApiClient } from '@/lib/api-client';

const apiClient = new ApiClient();

export default function ApiTestPage() {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const testEndpoints = [
    { name: '업종 목록', endpoint: '/api/admin/industries' },
    { name: '브랜드 목록', endpoint: '/api/admin/brands' },
    { name: '매장 목록', endpoint: '/api/admin/branches' },
    { name: '직원 목록', endpoint: '/api/admin/employees' },
    { name: '계층 트리', endpoint: '/api/admin/hierarchy/tree' },
    { name: '대시보드 통계', endpoint: '/api/admin/dashboard-stats' },
  ];

  const testEndpoint = async (endpoint: string) => {
    setLoading(true);
    setError(null);
    setData(null);

    try {
      const response = await apiClient.get(endpoint);
      setData(response);
    } catch (err: any) {
      setError(err.message || 'API 호출 실패');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-blue-400">
          백엔드 API 연동 테스트
        </h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {testEndpoints.map((test) => (
            <button
              key={test.endpoint}
              onClick={() => testEndpoint(test.endpoint)}
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 p-4 rounded-lg transition-colors"
            >
              {test.name} 테스트
            </button>
          ))}
        </div>

        {loading && (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400 mx-auto"></div>
            <p className="mt-4">API 호출 중...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-900 border border-red-600 rounded-lg p-6 mb-6">
            <h3 className="text-xl font-semibold mb-2">오류 발생</h3>
            <p className="text-red-300">{error}</p>
          </div>
        )}

        {data && (
          <div className="bg-gray-800 border border-gray-600 rounded-lg p-6">
            <h3 className="text-xl font-semibold mb-4">응답 데이터</h3>
            <pre className="bg-gray-900 p-4 rounded overflow-auto text-sm">
              {JSON.stringify(data, null, 2)}
            </pre>
          </div>
        )}

        <div className="mt-8 bg-gray-800 border border-gray-600 rounded-lg p-6">
          <h3 className="text-xl font-semibold mb-4">API 클라이언트 정보</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p><strong>기본 URL:</strong> http://192.168.45.44:5000</p>
              <p><strong>프론트엔드 URL:</strong> http://192.168.45.44:3001</p>
            </div>
            <div>
              <p><strong>상태:</strong> {loading ? '로딩 중' : '대기 중'}</p>
              <p><strong>연결:</strong> {error ? '오류' : '정상'}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 
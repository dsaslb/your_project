'use client';

import React, { useState, useEffect } from 'react';
import { useBadges } from '@/store/useBadges';

export default function TestRealtimePage() {
  const [branchId, setBranchId] = useState<number>(1);
  const [brandId, setBrandId] = useState<number>(1);
  const [testResults, setTestResults] = useState<string[]>([]);
  
  // 배지 훅 사용
  const { badges, isConnected, refreshBadgeCounts } = useBadges(branchId, brandId);

  // 테스트 결과 추가
  const addTestResult = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setTestResults(prev => [`[${timestamp}] ${message}`, ...prev.slice(0, 9)]);
  };

  // API 테스트
  const testCreatePurchaseOrder = async () => {
    try {
      addTestResult('🔍 발주 생성 API 테스트 시작...');
      
      const response = await fetch('/api/mobile/purchase_orders', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Idempotency-Key': crypto.randomUUID(),
        },
        body: JSON.stringify({
          branch_id: branchId,
          items: [
            { barcode: 'TEST001', name: '테스트 상품', qty: 1 }
          ],
          notes: '테스트 발주입니다.'
        })
      });

      if (response.ok) {
        const data = await response.json();
        addTestResult(`✅ 발주 생성 성공! ID: ${data.id}`);
      } else {
        const error = await response.text();
        addTestResult(`❌ 발주 생성 실패: ${error}`);
      }
    } catch (error) {
      addTestResult(`❌ API 호출 오류: ${error}`);
    }
  };

  // 배지 새로고침 테스트
  const testRefreshBadges = async () => {
    try {
      addTestResult('🔄 배지 새로고침 테스트...');
      await refreshBadgeCounts();
      addTestResult('✅ 배지 새로고침 완료');
    } catch (error) {
      addTestResult(`❌ 배지 새로고침 실패: ${error}`);
    }
  };

  // 웹소켓 연결 상태 확인
  useEffect(() => {
    if (isConnected) {
      addTestResult('🔌 웹소켓 연결됨');
    } else {
      addTestResult('🔌 웹소켓 연결 끊김');
    }
  }, [isConnected]);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          🔄 실시간 시스템 테스트 페이지
        </h1>

        {/* 설정 섹션 */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">⚙️ 테스트 설정</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                지점 ID
              </label>
              <input
                type="number"
                value={branchId}
                onChange={(e) => setBranchId(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                브랜드 ID
              </label>
              <input
                type="number"
                value={brandId}
                onChange={(e) => setBrandId(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* 연결 상태 섹션 */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">🔌 연결 상태</h2>
          <div className="flex items-center space-x-4">
            <div className={`w-4 h-4 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className="text-sm font-medium">
              {isConnected ? '웹소켓 연결됨' : '웹소켓 연결 끊김'}
            </span>
          </div>
        </div>

        {/* 실시간 배지 섹션 */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">📊 실시간 배지</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">{badges.poRequested}</div>
              <div className="text-sm text-orange-600">대기중</div>
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{badges.poProcessing}</div>
              <div className="text-sm text-blue-600">처리중</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{badges.poCompleted}</div>
              <div className="text-sm text-green-600">완료</div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">{badges.attendanceUpdates}</div>
              <div className="text-sm text-purple-600">출퇴근</div>
            </div>
          </div>
        </div>

        {/* 테스트 버튼 섹션 */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">🧪 테스트 실행</h2>
          <div className="flex flex-wrap gap-4">
            <button
              onClick={testCreatePurchaseOrder}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              📋 발주 생성 테스트
            </button>
            <button
              onClick={testRefreshBadges}
              className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              🔄 배지 새로고침 테스트
            </button>
          </div>
        </div>

        {/* 테스트 결과 섹션 */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">📋 테스트 결과</h2>
          <div className="bg-gray-50 rounded-lg p-4 h-64 overflow-y-auto">
            {testResults.length === 0 ? (
              <p className="text-gray-500 text-center">테스트를 실행하면 결과가 여기에 표시됩니다.</p>
            ) : (
              <div className="space-y-2">
                {testResults.map((result, index) => (
                  <div key={index} className="text-sm font-mono bg-white p-2 rounded border">
                    {result}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* 사용법 안내 */}
        <div className="bg-blue-50 rounded-lg p-6 mt-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">💡 사용법</h3>
          <div className="text-blue-800 space-y-2">
            <p>1. <strong>지점 ID</strong>와 <strong>브랜드 ID</strong>를 설정하세요</p>
            <p>2. <strong>발주 생성 테스트</strong>를 실행하여 실시간 이벤트를 확인하세요</p>
            <p>3. <strong>배지 새로고침</strong>을 통해 백그라운드 데이터 동기화를 테스트하세요</p>
            <p>4. 다른 브라우저나 모바일 앱에서 발주를 생성하면 실시간으로 배지가 업데이트됩니다</p>
          </div>
        </div>
      </div>
    </div>
  );
}

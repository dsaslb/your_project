'use client';

import React, { useState, useEffect } from 'react';
import { useBadges } from '@/store/useBadges';

export default function TestRealtimePage() {
  const [testBranchId] = useState('test_branch_001');
  const { badges, isConnected, socket } = useBadges(testBranchId);
  const [eventLog, setEventLog] = useState<string[]>([]);
  const [testData, setTestData] = useState({
    barcode: 'TEST001',
    name: '테스트 상품',
    qty: 1
  });

  // 이벤트 로그 추가
  const addEventLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setEventLog(prev => [`[${timestamp}] ${message}`, ...prev.slice(0, 19)]);
  };

  // 테스트 발주 생성
  const testCreatePurchaseOrder = async () => {
    try {
      addEventLog('🧪 테스트 발주 생성 시작');
      
      const response = await fetch('/api/mobile/purchase_orders', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Idempotency-Key': `test-${Date.now()}`,
          'Authorization': 'Bearer test_token'
        },
        body: JSON.stringify({
          branch_id: testBranchId,
          items: [testData]
        })
      });

      if (response.ok) {
        const data = await response.json();
        addEventLog(`✅ 발주 생성 성공: ${data.po_id}`);
      } else {
        addEventLog(`❌ 발주 생성 실패: ${response.status}`);
      }
    } catch (error) {
      addEventLog(`❌ 발주 생성 오류: ${error}`);
    }
  };

  // 테스트 이벤트 수동 발생
  const testManualEvent = (eventType: string) => {
    if (socket) {
      const testEvent = {
        type: eventType,
        industry_id: 'test_industry',
        brand_id: 'test_brand',
        branch_id: testBranchId,
        data: { test: true, timestamp: Date.now() }
      };
      
      socket.emit(eventType, testEvent);
      addEventLog(`📡 수동 이벤트 발생: ${eventType}`);
    } else {
      addEventLog('❌ 소켓 연결이 없습니다');
    }
  };

  // 소켓 이벤트 리스너
  useEffect(() => {
    if (socket) {
      const eventTypes = ['po:created', 'po:status', 'attendance:update', 'inventory:update', 'schedule:update', 'order:update'];
      
      eventTypes.forEach(eventType => {
        socket.on(eventType, (data) => {
          addEventLog(`📨 이벤트 수신: ${eventType} - ${JSON.stringify(data).slice(0, 100)}...`);
        });
      });

      return () => {
        eventTypes.forEach(eventType => {
          socket.off(eventType);
        });
      };
    }
  }, [socket]);

  // 연결 상태 변경 로그
  useEffect(() => {
    addEventLog(isConnected ? '✅ Socket.IO 연결됨' : '❌ Socket.IO 연결 끊김');
  }, [isConnected]);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* 헤더 */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            🧪 실시간 이벤트 시스템 테스트
          </h1>
          <p className="text-lg text-gray-600">
            웹에서 실시간 이벤트 시스템을 테스트할 수 있습니다
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 연결 상태 및 배지 */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              🔌 연결 상태 및 배지
            </h2>
            
            {/* 연결 상태 */}
            <div className="mb-4 p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-sm text-gray-600">
                  {isConnected ? '실시간 연결됨' : '연결 끊김'}
                </span>
              </div>
            </div>

            {/* 배지 상태 */}
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-gray-700">📋 발주:</span>
                <span className="font-semibold text-blue-600">{badges.purchaseOrders}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-700">👥 출퇴근:</span>
                <span className="font-semibold text-purple-600">{badges.attendance}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-700">📦 재고:</span>
                <span className="font-semibold text-yellow-600">{badges.inventory}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-700">📅 일정:</span>
                <span className="font-semibold text-indigo-600">{badges.schedule}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-700">🛒 주문:</span>
                <span className="font-semibold text-green-600">{badges.orders}</span>
              </div>
            </div>
          </div>

          {/* 테스트 기능 */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              🧪 테스트 기능
            </h2>
            
            {/* 발주 생성 테스트 */}
            <div className="mb-4">
              <h3 className="text-lg font-medium text-gray-800 mb-2">📋 발주 생성 테스트</h3>
              <div className="space-y-2 mb-3">
                <input
                  type="text"
                  placeholder="바코드"
                  value={testData.barcode}
                  onChange={(e) => setTestData(prev => ({ ...prev, barcode: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                />
                <input
                  type="text"
                  placeholder="상품명"
                  value={testData.name}
                  onChange={(e) => setTestData(prev => ({ ...prev, name: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                />
                <input
                  type="number"
                  placeholder="수량"
                  value={testData.qty}
                  onChange={(e) => setTestData(prev => ({ ...prev, qty: parseInt(e.target.value) || 0 }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
              <button
                onClick={testCreatePurchaseOrder}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
              >
                🧪 테스트 발주 생성
              </button>
            </div>

            {/* 수동 이벤트 테스트 */}
            <div>
              <h3 className="text-lg font-medium text-gray-800 mb-2">📡 수동 이벤트 테스트</h3>
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => testManualEvent('po:created')}
                  className="bg-green-600 text-white py-2 px-3 rounded-md hover:bg-green-700 transition-colors text-sm"
                >
                  po:created
                </button>
                <button
                  onClick={() => testManualEvent('po:status')}
                  className="bg-blue-600 text-white py-2 px-3 rounded-md hover:bg-blue-700 transition-colors text-sm"
                >
                  po:status
                </button>
                <button
                  onClick={() => testManualEvent('attendance:update')}
                  className="bg-purple-600 text-white py-2 px-3 rounded-md hover:bg-purple-700 transition-colors text-sm"
                >
                  attendance:update
                </button>
                <button
                  onClick={() => testManualEvent('inventory:update')}
                  className="bg-yellow-600 text-white py-2 px-3 rounded-md hover:bg-yellow-700 transition-colors text-sm"
                >
                  inventory:update
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* 이벤트 로그 */}
        <div className="mt-6 bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            📋 이벤트 로그
          </h2>
          <div className="bg-gray-900 text-green-400 p-4 rounded-lg h-64 overflow-y-auto font-mono text-sm">
            {eventLog.length === 0 ? (
              <div className="text-gray-500">이벤트 로그가 여기에 표시됩니다...</div>
            ) : (
              eventLog.map((log, index) => (
                <div key={index} className="mb-1">
                  {log}
                </div>
              ))
            )}
          </div>
        </div>

        {/* 사용법 안내 */}
        <div className="mt-6 bg-blue-50 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-blue-900 mb-4">
            📖 사용법
          </h2>
          <div className="text-blue-800 space-y-2">
            <p>1. <strong>테스트 발주 생성</strong>: 실제 API를 호출하여 발주를 생성하고 실시간 이벤트를 확인합니다</p>
            <p>2. <strong>수동 이벤트 테스트</strong>: 소켓을 통해 직접 이벤트를 발생시켜 실시간 반응을 확인합니다</p>
            <p>3. <strong>배지 업데이트</strong>: 이벤트 발생 시 사이드바 배지가 즉시 업데이트되는지 확인합니다</p>
            <p>4. <strong>백그라운드 재조회</strong>: 2초 후 실제 데이터로 배지 값이 보정되는지 확인합니다</p>
          </div>
        </div>
      </div>
    </div>
  );
}

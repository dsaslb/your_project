"use client";

/**
 * 🔄 실시간 업데이트 위젯
 * 
 * Socket.IO를 통해 실시간으로 업데이트되는 정보를 표시
 */

import React, { useState, useEffect } from 'react';
import { useBadges } from '@/store/useBadges';

interface RealtimeData {
  attendance: any[];
  inventory: any[];
  purchaseOrders: any[];
  orders: any[];
}

export default function RealtimeWidget() {
  // 테스트용 branchId (실제로는 props나 context에서 받아야 함)
  const testBranchId = 'test-branch-001';
  const { badges, isConnected } = useBadges(testBranchId);

  const [data, setData] = useState<RealtimeData>({
    attendance: [],
    inventory: [],
    purchaseOrders: [],
    orders: []
  });

  const formatTime = (timeString: string) => {
    try {
      return new Date(timeString).toLocaleString('ko-KR', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return '시간 정보 없음';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-gray-900">🔄 실시간 업데이트</h2>
        <div className="flex items-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <span className={`text-sm ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
            {isConnected ? '연결됨' : '연결 안됨'}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* 출퇴근 업데이트 */}
        <div className="bg-blue-50 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">🕐 출퇴근</h3>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {data.attendance.length > 0 ? (
              data.attendance.map((item, index) => (
                <div key={index} className="bg-white rounded p-2 text-sm">
                  <div className="flex justify-between items-center">
                    <span className={`font-medium ${
                      item.type === 'in' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {item.type === 'in' ? '출근' : '퇴근'}
                    </span>
                    <span className="text-gray-500 text-xs">
                      {formatTime(item.at)}
                    </span>
                  </div>
                  {item.lat && item.lng && (
                    <div className="text-xs text-gray-400 mt-1">
                      위치: {item.lat.toFixed(4)}, {item.lng.toFixed(4)}
                    </div>
                  )}
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-sm">출퇴근 기록이 없습니다.</p>
            )}
          </div>
        </div>

        {/* 재고 업데이트 */}
        <div className="bg-green-50 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-green-900 mb-3">📦 재고</h3>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {data.inventory.length > 0 ? (
              data.inventory.map((item, index) => (
                <div key={index} className="bg-white rounded p-2 text-sm">
                  <div className="flex justify-between items-center">
                    <span className="font-medium text-gray-900">
                      {item.barcode}
                    </span>
                    <span className="text-green-600 font-bold">
                      {item.qty}개
                    </span>
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {formatTime(item.created_at)}
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-sm">재고 업데이트가 없습니다.</p>
            )}
          </div>
        </div>

        {/* 발주 업데이트 */}
        <div className="bg-yellow-50 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-yellow-900 mb-3">📋 발주</h3>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {data.purchaseOrders.length > 0 ? (
              data.purchaseOrders.map((item, index) => (
                <div key={index} className="bg-white rounded p-2 text-sm">
                  <div className="flex justify-between items-center">
                    <span className="font-medium text-gray-900">
                      발주 #{item.id}
                    </span>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      item.status === 'requested' ? 'bg-blue-100 text-blue-800' :
                      item.status === 'approved' ? 'bg-green-100 text-green-800' :
                      item.status === 'ordered' ? 'bg-purple-100 text-purple-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {item.status === 'requested' ? '요청됨' :
                       item.status === 'approved' ? '승인됨' :
                       item.status === 'ordered' ? '발주됨' :
                       item.status}
                    </span>
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {formatTime(item.created_at)}
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-sm">발주 업데이트가 없습니다.</p>
            )}
          </div>
        </div>

        {/* 주문 업데이트 */}
        <div className="bg-purple-50 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-purple-900 mb-3">🛒 주문</h3>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {data.orders.length > 0 ? (
              data.orders.map((item, index) => (
                <div key={index} className="bg-white rounded p-2 text-sm">
                  <div className="flex justify-between items-center">
                    <span className="font-medium text-gray-900">
                      주문 #{item.id}
                    </span>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      item.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                      item.status === 'confirmed' ? 'bg-blue-100 text-blue-800' :
                      item.status === 'preparing' ? 'bg-orange-100 text-orange-800' :
                      item.status === 'ready' ? 'bg-green-100 text-green-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {item.status === 'pending' ? '대기중' :
                       item.status === 'confirmed' ? '확인됨' :
                       item.status === 'preparing' ? '준비중' :
                       item.status === 'ready' ? '준비완료' :
                       item.status}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-sm">주문 업데이트가 없습니다.</p>
            )}
          </div>
        </div>
      </div>

      {/* 통계 요약 */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="grid grid-cols-4 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-blue-600">{data.attendance.length}</div>
            <div className="text-sm text-gray-600">출퇴근</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-green-600">{data.inventory.length}</div>
            <div className="text-sm text-gray-600">재고</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-yellow-600">{data.purchaseOrders.length}</div>
            <div className="text-sm text-gray-600">발주</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-purple-600">{data.orders.length}</div>
            <div className="text-sm text-gray-600">주문</div>
          </div>
        </div>
      </div>
    </div>
  );
}

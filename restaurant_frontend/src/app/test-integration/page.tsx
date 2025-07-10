'use client';

import React from 'react';
import { useStaffStore } from '../../store/useStaffStore';
import { useOrderStore } from '../../store/useOrderStore';
import { useInventoryStore } from '../../store/useInventoryStore';
import { useScheduleStore } from '../../store/useScheduleStore';
import { useNotificationStore } from '../../store/useNotificationStore';

export default function TestIntegrationPage() {
  const staffStore = useStaffStore();
  const orderStore = useOrderStore();
  const inventoryStore = useInventoryStore();
  const scheduleStore = useScheduleStore();
  const notificationStore = useNotificationStore();

  const addSampleData = () => {
    // 샘플 직원 데이터
    staffStore.addStaff({
      name: '테스트 직원',
      email: 'test@example.com',
      phone: '010-1234-5678',
      position: '서버',
      branchId: 1,
      role: 'employee',
    });

    // 샘플 주문 데이터
    orderStore.addOrder({
      orderNumber: 'ORD-TEST-001',
      customerName: '테스트 고객',
      items: [{ id: 1, productName: '불고기', quantity: 2, price: 15000 }],
      totalAmount: 30000,
      status: 'pending',
      branchId: 1,
    });

    // 샘플 재고 데이터
    inventoryStore.addItem({
      name: '테스트 재고',
      category: '식재료',
      currentStock: 50,
      minStock: 10,
      maxStock: 100,
      unit: 'kg',
      price: 5000,
      supplier: '테스트 공급업체',
      branchId: 1,
    });

    // 샘플 스케줄 데이터
    scheduleStore.addSchedule({
      staffId: 1,
      staffName: '테스트 직원',
      date: new Date().toISOString().split('T')[0],
      startTime: '09:00',
      endTime: '17:00',
      position: '서버',
      status: 'scheduled',
      branchId: 1,
    });

    // 알림 생성
    notificationStore.addNotification({
      title: '샘플 데이터 추가',
      message: '모든 스토어에 샘플 데이터가 추가되었습니다.',
      type: 'success',
      category: 'test',
    });
  };

  const syncAllData = async () => {
    await Promise.all([
      staffStore.manualSync(),
      orderStore.manualSync(),
      inventoryStore.manualSync(),
      scheduleStore.manualSync(),
    ]);

    notificationStore.addNotification({
      title: '동기화 완료',
      message: '모든 데이터가 서버와 동기화되었습니다.',
      type: 'info',
      category: 'sync',
    });
  };

  const clearAllData = () => {
    staffStore.clearAll();
    orderStore.clearAll();
    inventoryStore.clearAll();
    scheduleStore.clearAll();
    notificationStore.clearAll();

    notificationStore.addNotification({
      title: '데이터 초기화',
      message: '모든 데이터가 초기화되었습니다.',
      type: 'warning',
      category: 'system',
    });
  };

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">통합 테스트 페이지</h1>
      
      {/* 제어 패널 */}
      <div className="bg-white p-6 rounded-lg shadow mb-6">
        <h2 className="text-xl font-semibold mb-4">제어 패널</h2>
        <div className="flex flex-wrap gap-4">
          <button
            onClick={addSampleData}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            샘플 데이터 추가
          </button>
          <button
            onClick={syncAllData}
            className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
          >
            모든 데이터 동기화
          </button>
          <button
            onClick={clearAllData}
            className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
          >
            모든 데이터 초기화
          </button>
        </div>
      </div>

      {/* 스토어 상태 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="font-semibold mb-2">직원 스토어</h3>
          <div className="text-sm space-y-1">
            <div>데이터: {staffStore.staff.length}개</div>
            <div>상태: <span className={`px-2 py-1 rounded text-xs ${
              staffStore.syncStatus === 'synced' ? 'bg-green-100 text-green-800' :
              staffStore.syncStatus === 'pending' ? 'bg-yellow-100 text-yellow-800' :
              'bg-red-100 text-red-800'
            }`}>{staffStore.syncStatus}</span></div>
            <div>마지막 동기화: {staffStore.lastSync ? new Date(staffStore.lastSync).toLocaleTimeString() : '없음'}</div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="font-semibold mb-2">주문 스토어</h3>
          <div className="text-sm space-y-1">
            <div>데이터: {orderStore.orders.length}개</div>
            <div>상태: <span className={`px-2 py-1 rounded text-xs ${
              orderStore.syncStatus === 'synced' ? 'bg-green-100 text-green-800' :
              orderStore.syncStatus === 'pending' ? 'bg-yellow-100 text-yellow-800' :
              'bg-red-100 text-red-800'
            }`}>{orderStore.syncStatus}</span></div>
            <div>마지막 동기화: {orderStore.lastSync ? new Date(orderStore.lastSync).toLocaleTimeString() : '없음'}</div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="font-semibold mb-2">재고 스토어</h3>
          <div className="text-sm space-y-1">
            <div>데이터: {inventoryStore.items.length}개</div>
            <div>상태: <span className={`px-2 py-1 rounded text-xs ${
              inventoryStore.syncStatus === 'synced' ? 'bg-green-100 text-green-800' :
              inventoryStore.syncStatus === 'pending' ? 'bg-yellow-100 text-yellow-800' :
              'bg-red-100 text-red-800'
            }`}>{inventoryStore.syncStatus}</span></div>
            <div>마지막 동기화: {inventoryStore.lastSync ? new Date(inventoryStore.lastSync).toLocaleTimeString() : '없음'}</div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="font-semibold mb-2">스케줄 스토어</h3>
          <div className="text-sm space-y-1">
            <div>데이터: {scheduleStore.schedules.length}개</div>
            <div>상태: <span className={`px-2 py-1 rounded text-xs ${
              scheduleStore.syncStatus === 'synced' ? 'bg-green-100 text-green-800' :
              scheduleStore.syncStatus === 'pending' ? 'bg-yellow-100 text-yellow-800' :
              'bg-red-100 text-red-800'
            }`}>{scheduleStore.syncStatus}</span></div>
            <div>마지막 동기화: {scheduleStore.lastSync ? new Date(scheduleStore.lastSync).toLocaleTimeString() : '없음'}</div>
          </div>
        </div>
      </div>

      {/* 데이터 목록 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 직원 목록 */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">직원 목록</h3>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {staffStore.staff.length === 0 ? (
              <p className="text-gray-500">직원 데이터가 없습니다</p>
            ) : (
              staffStore.staff.map((staff) => (
                <div key={staff.id} className="p-3 border rounded">
                  <div className="font-medium">{staff.name}</div>
                  <div className="text-sm text-gray-600">{staff.position}</div>
                  <div className="text-xs text-gray-400">{staff.email}</div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* 주문 목록 */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">주문 목록</h3>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {orderStore.orders.length === 0 ? (
              <p className="text-gray-500">주문 데이터가 없습니다</p>
            ) : (
              orderStore.orders.map((order) => (
                <div key={order.id} className="p-3 border rounded">
                  <div className="font-medium">{order.orderNumber}</div>
                  <div className="text-sm text-gray-600">{order.customerName}</div>
                  <div className="text-xs text-gray-400">
                    {order.items.length}개 상품 | {order.totalAmount.toLocaleString()}원
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* 재고 목록 */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">재고 목록</h3>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {inventoryStore.items.length === 0 ? (
              <p className="text-gray-500">재고 데이터가 없습니다</p>
            ) : (
              inventoryStore.items.map((item) => (
                <div key={item.id} className="p-3 border rounded">
                  <div className="font-medium">{item.name}</div>
                  <div className="text-sm text-gray-600">
                    {item.currentStock}{item.unit} / {item.category}
                  </div>
                  <div className={`text-xs px-2 py-1 rounded inline-block ${
                    item.status === 'normal' ? 'bg-green-100 text-green-800' :
                    item.status === 'low' ? 'bg-yellow-100 text-yellow-800' :
                    item.status === 'out' ? 'bg-red-100 text-red-800' :
                    'bg-blue-100 text-blue-800'
                  }`}>
                    {item.status}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* 스케줄 목록 */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">스케줄 목록</h3>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {scheduleStore.schedules.length === 0 ? (
              <p className="text-gray-500">스케줄 데이터가 없습니다</p>
            ) : (
              scheduleStore.schedules.map((schedule) => (
                <div key={schedule.id} className="p-3 border rounded">
                  <div className="font-medium">{schedule.staffName}</div>
                  <div className="text-sm text-gray-600">
                    {schedule.date} {schedule.startTime}-{schedule.endTime}
                  </div>
                  <div className="text-xs text-gray-400">{schedule.position}</div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* 사용법 안내 */}
      <div className="mt-6 bg-blue-50 p-4 rounded-lg">
        <h3 className="font-semibold text-blue-800 mb-2">테스트 방법</h3>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• "샘플 데이터 추가" 버튼으로 각 스토어에 테스트 데이터를 생성합니다</li>
          <li>• "모든 데이터 동기화" 버튼으로 서버와 동기화를 시도합니다</li>
          <li>• 네트워크를 끊고 데이터를 수정한 후 온라인으로 복구하여 오프라인 기능을 테스트합니다</li>
          <li>• 각 스토어의 상태와 데이터 개수를 확인할 수 있습니다</li>
          <li>• 오른쪽 상단의 알림 센터에서 실시간 알림을 확인합니다</li>
        </ul>
      </div>
    </div>
  );
} 
import React from 'react';
import { useStaffStore } from '../store/useStaffStore';

const StaffList: React.FC = () => {
  const { staffList, syncStatus, lastSync, fetchStaff, manualSync } = useStaffStore();

  React.useEffect(() => {
    if (staffList.length === 0) {
      fetchStaff();
    }
    // eslint-disable-next-line
  }, []);

  return (
    <div className="p-4 max-w-xl mx-auto">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-lg font-bold">직원 목록</h2>
        <button
          className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
          onClick={manualSync}
          disabled={syncStatus === 'pending'}
        >
          {syncStatus === 'pending' ? '동기화 중...' : '수동 동기화'}
        </button>
      </div>
      <div className="mb-2 text-sm">
        동기화 상태: <span className={
          syncStatus === 'synced' ? 'text-green-600' :
          syncStatus === 'offline' ? 'text-red-600' :
          syncStatus === 'pending' ? 'text-blue-600' : 'text-gray-600'
        }>{syncStatus}</span>
        {lastSync && (
          <span className="ml-2 text-gray-500">(마지막 동기화: {new Date(lastSync).toLocaleString()})</span>
        )}
      </div>
      {syncStatus === 'offline' && (
        <div className="mb-2 p-2 bg-yellow-100 text-yellow-800 rounded">
          오프라인 상태입니다. 데이터가 최신이 아닐 수 있습니다.
        </div>
      )}
      <ul className="divide-y divide-gray-200">
        {staffList.length === 0 ? (
          <li className="py-4 text-gray-400">직원 데이터가 없습니다.</li>
        ) : (
          staffList.map((staff) => (
            <li key={staff.id} className="py-2 flex flex-col">
              <span className="font-medium">{staff.name}</span>
              <span className="text-xs text-gray-500">{staff.role} / 지점ID: {staff.branchId}</span>
              <span className="text-xs text-gray-400">업데이트: {new Date(staff.updatedAt).toLocaleString()}</span>
            </li>
          ))
        )}
      </ul>
    </div>
  );
};

export default StaffList; 
'use client';

import { useState } from 'react';
import { 
  MobileBottomNavigation, 
  MobileDataTable, 
  TouchButton, 
  MobileChart,
  SwipeableCard 
} from '@/components/MobileOptimized';
import { DataCard } from '@/components/DataTable';
import { Users, ShoppingCart, DollarSign, Activity, Bell, Settings } from 'lucide-react';

export default function MobilePage() {
  const [activeTab, setActiveTab] = useState('dashboard');

  // 샘플 데이터
  const userData = [
    { id: 1, name: '김철수', role: '매니저', status: '활성', lastLogin: '2분 전' },
    { id: 2, name: '이영희', role: '직원', status: '활성', lastLogin: '5분 전' },
    { id: 3, name: '박민수', role: '매니저', status: '비활성', lastLogin: '1시간 전' },
    { id: 4, name: '최지영', role: '직원', status: '활성', lastLogin: '10분 전' },
  ];

  const chartData = [
    { value: 45, label: 'CPU' },
    { value: 67, label: '메모리' },
    { value: 23, label: '디스크' },
    { value: 12, label: '네트워크' },
  ];

  const userColumns = [
    { key: 'name', title: '이름' },
    { key: 'role', title: '역할' },
    { key: 'status', title: '상태' },
    { key: 'lastLogin', title: '마지막 로그인' },
  ];

  const renderDashboard = () => (
    <div className="space-y-4">
      {/* 통계 카드 */}
      <div className="grid grid-cols-2 gap-3 px-4">
        <DataCard
          title="총 사용자"
          value="1,234"
          change={5.2}
          icon={Users}
          color="cyan"
        />
        <DataCard
          title="총 주문"
          value="567"
          change={-2.1}
          icon={ShoppingCart}
          color="green"
        />
        <DataCard
          title="총 매출"
          value="₩12M"
          change={8.7}
          icon={DollarSign}
          color="yellow"
        />
        <DataCard
          title="시스템 부하"
          value="67%"
          change={1.5}
          icon={Activity}
          color="red"
        />
      </div>

      {/* 시스템 성능 차트 */}
      <MobileChart
        title="시스템 성능"
        data={chartData}
        color="#06b6d4"
      />

      {/* 스와이프 가능한 알림 카드 */}
      <SwipeableCard
        onSwipeLeft={() => console.log('알림 삭제')}
        onSwipeRight={() => console.log('알림 보관')}
        className="mx-4"
      >
        <div className="p-4 bg-black/30 backdrop-blur-sm border border-cyan-500/20 rounded-lg">
          <div className="flex items-center space-x-3">
            <Bell className="w-5 h-5 text-cyan-400" />
            <div className="flex-1">
              <h3 className="font-semibold text-white">새로운 알림</h3>
              <p className="text-sm text-slate-400">시스템 업데이트가 완료되었습니다.</p>
            </div>
          </div>
        </div>
      </SwipeableCard>
    </div>
  );

  const renderUsers = () => (
    <div className="space-y-4">
      <div className="px-4">
        <h2 className="text-lg font-semibold text-white mb-4">사용자 관리</h2>
        <TouchButton
          onClick={() => console.log('새 사용자 추가')}
          className="w-full mb-4"
        >
          새 사용자 추가
        </TouchButton>
      </div>
      
      <MobileDataTable
        data={userData}
        columns={userColumns}
        title="사용자 목록"
      />
    </div>
  );

  const renderSettings = () => (
    <div className="space-y-4 px-4">
      <h2 className="text-lg font-semibold text-white mb-4">설정</h2>
      
      <div className="space-y-3">
        <TouchButton
          onClick={() => console.log('알림 설정')}
          variant="outline"
          className="w-full justify-start"
        >
          <Bell className="w-4 h-4 mr-2" />
          알림 설정
        </TouchButton>
        
        <TouchButton
          onClick={() => console.log('계정 설정')}
          variant="outline"
          className="w-full justify-start"
        >
          <Settings className="w-4 h-4 mr-2" />
          계정 설정
        </TouchButton>
        
        <TouchButton
          onClick={() => console.log('테마 설정')}
          variant="outline"
          className="w-full justify-start"
        >
          <Settings className="w-4 h-4 mr-2" />
          테마 설정
        </TouchButton>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return renderDashboard();
      case 'users':
        return renderUsers();
      case 'settings':
        return renderSettings();
      default:
        return renderDashboard();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 pb-20">
      {/* 헤더 */}
      <div className="p-4 border-b border-cyan-500/20">
        <h1 className="text-xl font-bold text-white">모바일 대시보드</h1>
        <p className="text-sm text-slate-400">모바일에 최적화된 인터페이스</p>
      </div>

      {/* 메인 콘텐츠 */}
      <div className="py-4">
        {renderContent()}
      </div>

      {/* 하단 네비게이션 */}
      <MobileBottomNavigation />
    </div>
  );
} 
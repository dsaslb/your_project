import KPIWidget from './KPIWidget';
import AIManagerWidget from './AIManagerWidget';
import { RealTimeStats, SystemPerformanceCard } from '@/components/RealTimeStats';
import { SystemPerformanceChart, UserActivityChart } from '@/components/RealTimeCharts';
import { DataCard } from '@/components/DataTable';
import { 
  LiveCounter, 
  SystemStatusWidget, 
  AlertSummaryWidget, 
  QuickActionsWidget, 
  ActivityFeedWidget 
} from '@/components/DashboardWidgets';
import { Users, ShoppingCart, DollarSign, Activity } from 'lucide-react';

export default function DashboardPage() {
  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* AI 경영 어시스턴트 위젯 (초보자용 설명) */}
      <AIManagerWidget />
      
      {/* 실시간 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
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
          value="₩12,345,678"
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

      {/* 실시간 카운터 위젯 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <LiveCounter
          title="활성 사용자"
          value={156}
          change={12.5}
          icon={Users}
          color="cyan"
          refreshInterval={3000}
        />
        <LiveCounter
          title="대기 주문"
          value={23}
          change={-8.2}
          icon={ShoppingCart}
          color="green"
          refreshInterval={5000}
        />
        <LiveCounter
          title="시간당 매출"
          value={1250000}
          change={15.3}
          icon={DollarSign}
          color="yellow"
          refreshInterval={10000}
        />
        <LiveCounter
          title="서버 부하"
          value={67}
          change={2.1}
          icon={Activity}
          color="red"
          refreshInterval={8000}
        />
      </div>

      {/* 실시간 KPI 차트 위젯 */}
      <KPIWidget />
      
      {/* 시스템 성능 차트 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SystemPerformanceChart />
        <UserActivityChart />
      </div>
      
      {/* 시스템 성능 카드 */}
      <SystemPerformanceCard />
      
      {/* 시스템 상태 및 알림 위젯 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <SystemStatusWidget />
        <AlertSummaryWidget />
        <QuickActionsWidget />
        <ActivityFeedWidget />
      </div>
      
      {/* 기존 대시보드 내용 ... */}
    </div>
  );
} 
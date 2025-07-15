import KPIWidget from './KPIWidget';
import AIManagerWidget from './AIManagerWidget';

export default function DashboardPage() {
  return (
    <div className="container mx-auto p-6">
      {/* AI 경영 어시스턴트 위젯 (초보자용 설명) */}
      <AIManagerWidget />
      {/* 실시간 KPI 차트 위젯 */}
      <KPIWidget />
      {/* 기존 대시보드 내용 ... */}
    </div>
  );
} 
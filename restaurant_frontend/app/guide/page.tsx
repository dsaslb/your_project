import React from 'react';

export default function GuidePage() {
  return (
    <main className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">온보딩 & 가이드 / Onboarding & Guide</h1>
      <section className="mb-6">
        <h2 className="text-xl font-semibold mb-2">주요 기능 안내 / Key Features</h2>
        <ul className="list-disc pl-6">
          <li>실시간 알림/공지, 통계/차트, 검색/필터/정렬 / Real-time notifications, stats/charts, search/filter/sort</li>
          <li>권한별 메뉴/액션 분기, 접근성/다크모드 지원 / Role-based menu/action, accessibility/dark mode</li>
          <li>모든 주요 기능에 툴팁/설명/온보딩 안내 적용 / Tooltips, explanations, onboarding for all features</li>
        </ul>
      </section>
      <section className="mb-6">
        <h2 className="text-xl font-semibold mb-2">실시간 현황판/차트 / Live Dashboard & Charts</h2>
        <ul className="list-disc pl-6">
          <li>실시간 트래픽/알림/에러 차트(react-chartjs-2) / Live traffic/notification/error charts (react-chartjs-2)</li>
          <li>운영 데이터 기반 실시간 통계/이벤트 로그 / Real-time stats/event logs from live data</li>
          <li>차트 색상/옵션 커스터마이징 가능 / Customizable chart colors/options</li>
        </ul>
      </section>
      <section className="mb-6">
        <h2 className="text-xl font-semibold mb-2">운영자/관리자 안내 / Operator/Admin Guide</h2>
        <ul className="list-disc pl-6">
          <li>실시간 현황판(/admin/dashboard/monitor)에서 트래픽, 알림, 에러, 통계 확인 / Check traffic, notifications, errors, stats in live dashboard</li>
          <li>FAQ, 매뉴얼, 장애 대응, 데이터 백업/복구 메뉴 활용 / Use FAQ, manual, error handling, data backup/restore</li>
          <li>자세한 운영 안내는 <a href="/OPERATOR_MANUAL.md" className="text-blue-600 underline">운영자 매뉴얼</a> 참고 / See <a href="/OPERATOR_MANUAL.md" className="text-blue-600 underline">Operator Manual</a> for details</li>
        </ul>
      </section>
      <section>
        <h2 className="text-xl font-semibold mb-2">FAQ/도움말 / FAQ/Help</h2>
        <p>문제가 있으면 <a href="/faq" className="text-blue-600 underline">/faq</a> 페이지를 참고하거나 관리자에게 문의하세요.<br/>If you have issues, see <a href="/faq" className="text-blue-600 underline">/faq</a> or contact admin.</p>
      </section>
    </main>
  );
} 
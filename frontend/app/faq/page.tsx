import React from 'react';

export default function FAQPage() {
  return (
    <main className="max-w-2xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-4">자주 묻는 질문(FAQ)</h1>
      <section className="mb-6">
        <h2 className="text-xl font-semibold mb-2">브랜드 생성/초기화</h2>
        <p className="mb-2">Q. 신규 브랜드 생성 시 자동으로 페이지/샘플 데이터가 생성되나요?</p>
        <p className="mb-4 text-gray-700">A. 네, 자동 생성됩니다. 별도 수작업 없이 바로 사용 가능합니다.</p>
        <p className="mb-2">Q. 샘플 데이터가 보이지 않아요.</p>
        <p className="mb-4 text-gray-700">A. 최초 생성 시 자동으로 샘플 데이터가 노출됩니다. 문제가 있으면 운영자 가이드의 체크리스트를 참고하세요.</p>
      </section>
      <section className="mb-6">
        <h2 className="text-xl font-semibold mb-2">권한/메뉴/자동 이동</h2>
        <p className="mb-2">Q. 권한별로 메뉴/페이지가 다르게 보이나요?</p>
        <p className="mb-4 text-gray-700">A. 네, 권한(운영자/브랜드관리자/매장/직원)에 따라 맞춤 메뉴/자동 이동이 적용됩니다.</p>
      </section>
      <section className="mb-6">
        <h2 className="text-xl font-semibold mb-2">장애/이상 대응</h2>
        <p className="mb-2">Q. 장애/이상 감지 시 어떻게 대응하나요?</p>
        <p className="mb-4 text-gray-700">A. 대시보드 실시간 알림/로그/상세 모달/검색/필터를 활용하고, 운영자 가이드의 장애 대응 프로세스를 참고하세요.</p>
      </section>
      <section className="mb-6">
        <h2 className="text-xl font-semibold mb-2">접근성/초보자 안내</h2>
        <p className="mb-2">Q. 접근성은 어떻게 보장되나요?</p>
        <p className="mb-4 text-gray-700">A. 모든 주요 버튼/링크에 aria-label, role 등 접근성 속성이 적용되어 있습니다. 키보드 내비게이션, 명확한 안내 메시지, 색상 대비도 준수합니다.</p>
      </section>
      <footer className="mt-8 text-sm text-gray-500">최종 업데이트: 2024-06-01</footer>
    </main>
  );
} 
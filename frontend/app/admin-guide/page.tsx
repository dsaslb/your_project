import React from 'react';

export default function AdminGuidePage() {
  return (
    <main className="max-w-2xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-4">운영자 가이드</h1>
      <section className="mb-6">
        <h2 className="text-xl font-semibold mb-2">실전 운영 대응 시나리오</h2>
        <ul className="list-disc ml-6 text-gray-700">
          <li>신규 브랜드 생성~초기화~샘플 데이터~권한~페이지 자동화</li>
          <li>장애/이상 감지 시 실시간 알림 및 상세 로그 확인</li>
          <li>권한별 맞춤 메뉴/자동 이동/초기화/온보딩 안내</li>
          <li>운영 자동화 이력/검색/필터/상세 보기</li>
        </ul>
      </section>
      <section className="mb-6">
        <h2 className="text-xl font-semibold mb-2">운영 체크리스트</h2>
        <ul className="list-disc ml-6 text-gray-700">
          <li>브랜드별 샘플 데이터/권한/설정/초기화 정상 노출 확인</li>
          <li>대시보드 실시간 알림/통계/피드백/접근성 정상 작동</li>
          <li>외부 연동(슬랙/이메일/웹훅) 및 보안 정책 점검</li>
        </ul>
      </section>
      <section className="mb-6">
        <h2 className="text-xl font-semibold mb-2">장애/이상 대응 프로세스</h2>
        <ol className="list-decimal ml-6 text-gray-700">
          <li>실시간 알림/로그 확인 → 상세 모달/검색/필터 활용</li>
          <li>문제 발생 시 FAQ/접근성 안내/운영자 가이드 참고</li>
          <li>필요시 문의/지원 채널로 즉시 문의</li>
        </ol>
      </section>
      <section className="mb-6">
        <h2 className="text-xl font-semibold mb-2">문의/지원</h2>
        <p>운영 중 문의/지원이 필요하면 <a href="mailto:support@your_program.com" className="text-blue-600 underline" target="_blank" rel="noopener noreferrer">support@your_program.com</a> 으로 연락하세요.</p>
      </section>
      <section className="mb-6">
        <h2 className="text-xl font-semibold mb-2">접근성/초보자 안내</h2>
        <ul className="list-disc ml-6 text-gray-700">
          <li>모든 주요 버튼/링크에 aria-label, role 등 접근성 속성 적용</li>
          <li>키보드 내비게이션, 명확한 안내 메시지, 색상 대비 준수</li>
        </ul>
      </section>
      <footer className="mt-8 text-sm text-gray-500">최종 업데이트: 2024-06-01</footer>
    </main>
  );
} 
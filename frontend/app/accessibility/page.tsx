import React from 'react';

export default function AccessibilityPage() {
  return (
    <main className="max-w-2xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-4">접근성 안내</h1>
      <section className="mb-6">
        <h2 className="text-xl font-semibold mb-2">주요 접근성 정책</h2>
        <ul className="list-disc ml-6 text-gray-700">
          <li>모든 주요 버튼/링크에 aria-label, role 등 접근성 속성 적용</li>
          <li>키보드 내비게이션 완비, 명확한 안내 메시지 제공</li>
          <li>충분한 색상 대비, 시각적 구분 강화</li>
          <li>스크린리더 호환, 시맨틱 마크업 준수</li>
        </ul>
      </section>
      <section className="mb-6">
        <h2 className="text-xl font-semibold mb-2">실전 운영 시나리오</h2>
        <ul className="list-disc ml-6 text-gray-700">
          <li>접근성 이슈 발생 시 FAQ/운영자 가이드 참고</li>
          <li>문제가 지속될 경우 문의/지원 채널로 연락</li>
        </ul>
      </section>
      <section className="mb-6">
        <h2 className="text-xl font-semibold mb-2">초보자 안내</h2>
        <ul className="list-disc ml-6 text-gray-700">
          <li>모든 안내/버튼/링크에 명확한 설명 제공</li>
          <li>운영자/초보자도 쉽게 이해할 수 있는 UI/UX</li>
        </ul>
      </section>
      <footer className="mt-8 text-sm text-gray-500">최종 업데이트: 2024-06-01</footer>
    </main>
  );
} 
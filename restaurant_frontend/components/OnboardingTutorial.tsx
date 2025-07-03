import React, { useState } from 'react';

const steps_ko = [
  { title: '대시보드 소개', content: '실시간 통계, 알림, 주요 현황을 한눈에 확인할 수 있습니다.', link: '/admin/monitor', linkLabel: '실시간 현황판 바로가기' },
  { title: '공지/알림', content: '상단 알림 아이콘에서 실시간 공지/알림을 확인하세요.', link: '/notice', linkLabel: '공지/알림 바로가기' },
  { title: '발주/재고/직원/스케줄', content: '좌측 메뉴에서 각 업무별 페이지로 이동해 관리할 수 있습니다.', link: '/orders', linkLabel: '발주/재고/직원/스케줄 바로가기' },
  { title: '검색/필터/정렬', content: '상단/좌측 필터바와 정렬 옵션을 활용해 데이터를 빠르게 찾으세요.', link: '/guide', linkLabel: '가이드/도움말' },
  { title: '접근성/다크모드', content: '우측 상단 토글로 다크모드 전환, 모든 UI에 접근성 속성이 적용되어 있습니다.', link: '/guide', linkLabel: '접근성 안내' },
  { title: '도움말/FAQ', content: '문제가 있으면 /faq, /guide, /help 페이지를 참고하세요.', link: '/faq', linkLabel: 'FAQ 바로가기' },
  { title: '운영자 매뉴얼', content: '운영/배포/보안/모니터링 등은 운영자 매뉴얼을 참고하세요.', link: '/OPERATOR_MANUAL.md', linkLabel: '운영자 매뉴얼 보기' },
];
const steps_en = [
  { title: 'Dashboard Overview', content: 'Check real-time stats, notifications, and key status at a glance.', link: '/admin/monitor', linkLabel: 'Go to Live Dashboard' },
  { title: 'Notices/Notifications', content: 'Check real-time notices/notifications via the top icon.', link: '/notice', linkLabel: 'Go to Notices/Notifications' },
  { title: 'Orders/Inventory/Staff/Schedule', content: 'Manage each task via the left menu.', link: '/orders', linkLabel: 'Go to Orders/Inventory/Staff/Schedule' },
  { title: 'Search/Filter/Sort', content: 'Use filter bars and sort options to quickly find data.', link: '/guide', linkLabel: 'Guide/Help' },
  { title: 'Accessibility/Dark Mode', content: 'Switch dark mode via the top-right toggle. All UI is accessibility-ready.', link: '/guide', linkLabel: 'Accessibility Info' },
  { title: 'Help/FAQ', content: 'If you have issues, check /faq, /guide, or /help.', link: '/faq', linkLabel: 'Go to FAQ' },
  { title: 'Operator Manual', content: 'For operation/deployment/security/monitoring, see the Operator Manual.', link: '/OPERATOR_MANUAL.md', linkLabel: 'View Operator Manual' },
];

export default function OnboardingTutorial({ steps, theme = 'light', lang = 'ko' }: {
  steps?: typeof steps_ko,
  theme?: 'light' | 'dark',
  lang?: string
}) {
  const stepList = steps || (lang === 'en' ? steps_en : steps_ko);
  const [step, setStep] = useState(0);
  const [show, setShow] = useState(true);
  if (!show) return null;
  return (
    <div className={`fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40 ${theme === 'dark' ? 'dark' : ''}`} role="dialog" aria-modal="true">
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow-lg p-6 max-w-md w-full">
        <h2 className="text-xl font-bold mb-2">{stepList[step].title}</h2>
        <p className="mb-4">{stepList[step].content}</p>
        {stepList[step].link && (
          <a href={stepList[step].link} className="btn mb-2" target="_blank" rel="noopener noreferrer">{stepList[step].linkLabel || (lang === 'en' ? 'Learn more' : '더 알아보기')}</a>
        )}
        <div className="flex justify-between">
          <button className="btn" onClick={() => setShow(false)} aria-label={lang === 'en' ? 'Close tutorial' : '튜토리얼 종료'}>{lang === 'en' ? 'Close' : '종료'}</button>
          <div>
            {step > 0 && <button className="btn mr-2" onClick={() => setStep(step-1)} aria-label={lang === 'en' ? 'Previous step' : '이전 단계'}>{lang === 'en' ? 'Previous' : '이전'}</button>}
            {step < stepList.length-1 ? (
              <button className="btn" onClick={() => setStep(step+1)} aria-label={lang === 'en' ? 'Next step' : '다음 단계'}>{lang === 'en' ? 'Next' : '다음'}</button>
            ) : (
              <button className="btn" onClick={() => setShow(false)} aria-label={lang === 'en' ? 'Finish tutorial' : '튜토리얼 완료'}>{lang === 'en' ? 'Finish' : '완료'}</button>
            )}
          </div>
        </div>
        <div className="mt-2 text-xs text-gray-500">{step+1} / {stepList.length}</div>
      </div>
    </div>
  );
} 
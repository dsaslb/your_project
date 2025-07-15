import React, { useState, useEffect } from 'react';
// AI 경영 어시스턴트 위젯 (실시간 진단/예측/개선점/경보/리포트)
// 글로벌 다국어(i18n), 접근성, 초보자용 설명 포함

const messages = {
  title: { ko: 'AI 경영 도우미', en: 'AI Business Assistant' },
  diagnosis: { ko: '운영 진단', en: 'Diagnosis' },
  prediction: { ko: '다음달 예측', en: 'Prediction' },
  improvement: { ko: '개선점 추천', en: 'Improvement' },
  report: { ko: '자동 리포트', en: 'Auto Report' },
  alerts: { ko: '실시간 경보', en: 'Real-time Alerts' },
  loading: { ko: 'AI 분석 중...', en: 'Analyzing...' }
};
function getLang() {
  if (typeof window !== 'undefined') {
    return (navigator.language || 'ko').startsWith('en') ? 'en' : 'ko';
  }
  return 'ko';
}

const AIManagerWidget: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const lang = getLang();

  // 정책 데이터 상태 추가
  const [policyData, setPolicyData] = useState<any>(null);
  // 정책 목록 fetch 예시(초보자용 주석)
  useEffect(() => {
    fetch('/api/policy/list')
      .then(res => res.json())
      .then(setPolicyData)
      .catch(() => setPolicyData(null));
  }, []);

  useEffect(() => {
    fetch('/api/ai/assistant/report', { method: 'POST' })
      .then(res => res.json())
      .then(setData);
    fetch('/api/ai/assistant/alerts')
      .then(res => res.json())
      .then(res => setAlerts(res.alerts || []));
    setLoading(false);
  }, []);

  // 도움말 모달 상태
  const [helpOpen, setHelpOpen] = useState(false);

  if (loading || !data) return <div aria-label={messages.loading[lang]}>{messages.loading[lang]}</div>;

  return (
    <div>
      {/* 초보자용 도움말 버튼 */}
      <button
        className="mb-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        onClick={() => setHelpOpen(true)}
      >
        초보자용 도움말
      </button>
      {/* 도움말 모달 */}
      {helpOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg p-8 max-w-lg w-full relative">
            <button className="absolute top-2 right-2 text-gray-500" onClick={() => setHelpOpen(false)}>X</button>
            <h2 className="text-xl font-bold mb-2">초보자용 통합 가이드</h2>
            <ul className="list-disc list-inside text-sm mb-4">
              <li><b>AI 리포트:</b> 매출, 재방문율, 리뷰 평점 등 주요 지표를 한눈에!</li>
              <li><b>외부 리뷰 연동/감성분석:</b> 네이버/구글 리뷰 자동 분석, 긍/부정/중립 비율 제공</li>
              <li><b>운영 정책 자동화:</b> 매출 급감/리뷰 하락 등 조건별 자동 알림/조치</li>
            </ul>
            <div className="mb-2 text-xs text-gray-600">자주 묻는 질문(FAQ) 및 그림 예시는 <b>docs/BEGINNER_GUIDE.md</b> 파일 참고</div>
            <img src="/static/img/dashboard_example.png" alt="대시보드 예시" className="w-full rounded border mb-2" />
            <div className="text-xs text-gray-500">더 궁금한 점은 관리자 또는 개발팀에 문의하세요.</div>
          </div>
        </div>
      )}
      <div className="bg-white dark:bg-gray-900 rounded-lg p-4 shadow my-4" aria-label={messages.title[lang]}>
        <h2 className="text-xl font-bold mb-2">{messages.title[lang]}</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <div className="mb-2 font-semibold">{messages.diagnosis[lang]}</div>
            <div className="mb-2">{data.diagnosis}</div>
            <div className="mb-2 font-semibold">{messages.improvement[lang]}</div>
            <div className="mb-2">{data.improvement}</div>
            <div className="mb-2 font-semibold">{messages.prediction[lang]}</div>
            <div className="mb-2">{data.prediction}</div>
          </div>
          <div>
            <div className="mb-2 font-semibold">{messages.report[lang]}</div>
            <div className="mb-2">{data.llm_report}</div>
            <div className="mb-2 font-semibold">{messages.alerts[lang]}</div>
            {alerts.length === 0 ? (
              <div className="text-gray-400">-</div>
            ) : (
              alerts.map((a, i) => (
                <div key={i} className="text-red-500">{a.message}</div>
              ))
            )}
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
          {/* 기존 지표/카드들 ... */}
          {/* 운영 정책 자동화 카드 */}
          <div className="bg-white rounded-lg shadow p-4 flex flex-col items-center">
            <span className="text-sm text-gray-500 mb-1">운영 정책 자동화
              <span title="매출 급감, 리뷰 평점 하락 등 조건에 따라 자동으로 알림/조치가 실행되는 정책 목록입니다." className="ml-1 text-xs text-blue-400 cursor-help">?</span>
            </span>
            <ul className="text-xs text-gray-700 mt-1 list-disc list-inside">
              {policyData?.policies?.map((p: any) => (
                <li key={p.id}>{p.name} ({p.condition}) - {p.enabled ? 'ON' : 'OFF'}</li>
              )) || <li>정책 없음</li>}
            </ul>
          </div>
          {/* 재방문율 카드 */}
          <div className="bg-white rounded-lg shadow p-4 flex flex-col items-center">
            <span className="text-sm text-gray-500 mb-1">재방문율
              <span title="일정 기간 내 재구매한 고객 비율입니다." className="ml-1 text-xs text-blue-400 cursor-help">?</span>
            </span>
            <span className="text-2xl font-bold">{data?.revisit_rate !== undefined ? `${(data.revisit_rate * 100).toFixed(1)}%` : '-'}</span>
          </div>
          {/* 리뷰 평점 카드 */}
          <div className="bg-white rounded-lg shadow p-4 flex flex-col items-center">
            <span className="text-sm text-gray-500 mb-1">리뷰 평점
              <span title="외부 리뷰 플랫폼의 평균 평점입니다." className="ml-1 text-xs text-blue-400 cursor-help">?</span>
            </span>
            <span className="text-2xl font-bold">{data?.review_score !== undefined ? data.review_score.toFixed(2) : '-'}</span>
          </div>
          {/* 리뷰 감성분석 카드 */}
          <div className="bg-white rounded-lg shadow p-4 flex flex-col items-center">
            <span className="text-sm text-gray-500 mb-1">리뷰 감성분석
              <span title="최근 외부 리뷰의 긍정/부정/중립 비율과 평균 평점입니다." className="ml-1 text-xs text-blue-400 cursor-help">?</span>
            </span>
            <span className="text-lg font-bold">긍정: {data?.review_sentiment?.positive_ratio !== undefined ? `${(data.review_sentiment.positive_ratio*100).toFixed(0)}%` : '-'} / 부정: {data?.review_sentiment?.negative_ratio !== undefined ? `${(data.review_sentiment.negative_ratio*100).toFixed(0)}%` : '-'} / 중립: {data?.review_sentiment?.neutral_ratio !== undefined ? `${(data.review_sentiment.neutral_ratio*100).toFixed(0)}%` : '-'}</span>
            <span className="text-sm text-gray-500 mt-1">평균 평점: {data?.review_sentiment?.avg_score !== undefined ? data.review_sentiment.avg_score.toFixed(2) : '-'}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIManagerWidget; 
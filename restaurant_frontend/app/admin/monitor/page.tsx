"use client";

import React, { useEffect, useState } from 'react';
import { Line, Bar, Pie, Doughnut, Radar, PolarArea, Bubble, Scatter } from 'react-chartjs-2';

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  BarElement,
  ArcElement,
  RadialLinearScale,
  Filler,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  BarElement,
  ArcElement,
  RadialLinearScale,
  Filler
);

// 다국어 지원
const LANGS = {
  ko: {
    dashboard: '시스템 모니터링',
    stats: '알림',
    error: '오류',
    logs: '로그',
    loading: '로딩 중...',
    retry: '재시도',
    noData: '데이터가 없습니다',
    refresh: '새로고침',
    search: '검색',
    filter: '필터',
    all: '전체',
    important: '중요',
    warning: '경고',
    info: '정보',
    logNone: '로그가 없습니다',
    chartTitle: '시스템 트래픽',
    barTitle: '이벤트 분포',
    pieTitle: '사용자 분포',
    doughnutTitle: '시스템 상태',
    radarTitle: '사용자 활동',
    polarTitle: '알림 분류',
    lastUpdate: '마지막 업데이트',
    chartCustom: '차트 커스터마이징:',
    seeGuide: '가이드 보기',
    guide: '가이드',
    seeManual: '매뉴얼 보기',
    manual: '매뉴얼',
    seeEnd: '참고하세요',
    admin: '관리자',
    manager: '매니저'
  },
  zh: {
    dashboard: '系统监控',
    stats: '通知',
    error: '错误',
    logs: '日志',
    loading: '加载中...',
    retry: '重试',
    noData: '无数据',
    refresh: '刷新',
    search: '搜索',
    filter: '过滤',
    all: '全部',
    important: '重要',
    warning: '警告',
    info: '信息',
    logNone: '无日志',
    chartTitle: '系统流量',
    barTitle: '事件分布',
    pieTitle: '用户分布',
    doughnutTitle: '系统状态',
    radarTitle: '用户活动',
    polarTitle: '通知分类',
    lastUpdate: '最后更新',
    chartCustom: '图表自定义:',
    seeGuide: '查看指南',
    guide: '指南',
    seeManual: '查看手册',
    manual: '手册',
    seeEnd: '请参考',
    admin: '管理员',
    manager: '经理'
  },
  en: {
    dashboard: 'System Monitoring',
    stats: 'Notifications',
    error: 'Errors',
    logs: 'Logs',
    loading: 'Loading...',
    retry: 'Retry',
    noData: 'No data',
    refresh: 'Refresh',
    search: 'Search',
    filter: 'Filter',
    all: 'All',
    important: 'Important',
    warning: 'Warning',
    info: 'Info',
    logNone: 'No logs',
    chartTitle: 'System Traffic',
    barTitle: 'Event Distribution',
    pieTitle: 'User Distribution',
    doughnutTitle: 'System Status',
    radarTitle: 'User Activity',
    polarTitle: 'Notification Categories',
    lastUpdate: 'Last Update',
    chartCustom: 'Chart Customization:',
    seeGuide: 'See Guide',
    guide: 'Guide',
    seeManual: 'See Manual',
    manual: 'Manual',
    seeEnd: 'for reference',
    admin: 'Admin',
    manager: 'Manager'
  },
  ja: {
    dashboard: 'システム監視',
    stats: '通知',
    error: 'エラー',
    logs: 'ログ',
    loading: '読み込み中...',
    retry: '再試行',
    noData: 'データなし',
    refresh: '更新',
    search: '検索',
    filter: 'フィルター',
    all: 'すべて',
    important: '重要',
    warning: '警告',
    info: '情報',
    logNone: 'ログなし',
    chartTitle: 'システムトラフィック',
    barTitle: 'イベント分布',
    pieTitle: 'ユーザー分布',
    doughnutTitle: 'システム状態',
    radarTitle: 'ユーザー活動',
    polarTitle: '通知分類',
    lastUpdate: '最終更新',
    chartCustom: 'チャートカスタマイズ:',
    seeGuide: 'ガイドを見る',
    guide: 'ガイド',
    seeManual: 'マニュアルを見る',
    manual: 'マニュアル',
    seeEnd: 'を参照してください',
    admin: '管理者',
    manager: 'マネージャー'
  },
  fr: {
    dashboard: 'Surveillance Système',
    stats: 'Notifications',
    error: 'Erreurs',
    logs: 'Journaux',
    loading: 'Chargement...',
    retry: 'Réessayer',
    noData: 'Aucune donnée',
    refresh: 'Actualiser',
    search: 'Rechercher',
    filter: 'Filtrer',
    all: 'Tout',
    important: 'Important',
    warning: 'Avertissement',
    info: 'Info',
    logNone: 'Aucun journal',
    chartTitle: 'Trafic Système',
    barTitle: 'Distribution Événements',
    pieTitle: 'Distribution Utilisateurs',
    doughnutTitle: 'État Système',
    radarTitle: 'Activité Utilisateur',
    polarTitle: 'Catégories Notification',
    lastUpdate: 'Dernière Mise à Jour',
    chartCustom: 'Personnalisation Graphique:',
    seeGuide: 'Voir Guide',
    guide: 'Guide',
    seeManual: 'Voir Manuel',
    manual: 'Manuel',
    seeEnd: 'pour référence',
    admin: 'Admin',
    manager: 'Manager'
  },
  de: {
    dashboard: 'Systemüberwachung',
    stats: 'Benachrichtigungen',
    error: 'Fehler',
    logs: 'Protokolle',
    loading: 'Laden...',
    retry: 'Wiederholen',
    noData: 'Keine Daten',
    refresh: 'Aktualisieren',
    search: 'Suchen',
    filter: 'Filter',
    all: 'Alle',
    important: 'Wichtig',
    warning: 'Warnung',
    info: 'Info',
    logNone: 'Keine Protokolle',
    chartTitle: 'Systemverkehr',
    barTitle: 'Ereignisverteilung',
    pieTitle: 'Benutzerverteilung',
    doughnutTitle: 'Systemstatus',
    radarTitle: 'Benutzeraktivität',
    polarTitle: 'Benachrichtigungskategorien',
    lastUpdate: 'Letzte Aktualisierung',
    chartCustom: 'Diagrammanpassung:',
    seeGuide: 'Anleitung anzeigen',
    guide: 'Anleitung',
    seeManual: 'Handbuch anzeigen',
    manual: 'Handbuch',
    seeEnd: 'als Referenz',
    admin: 'Admin',
    manager: 'Manager'
  }
};

interface Stat {
  label: string;
  value: string | number;
}

interface Log {
  time: string;
  event: string;
  user: string;
}

interface PageProps {
  params?: Record<string, never>;
  searchParams?: Record<string, never>;
}

export default function AdminMonitorPage(props: PageProps) {
  const [stats, setStats] = useState<Stat[]>([]);
  const [logs, setLogs] = useState<Log[]>([]);
  const [loading, setLoading] = useState(true);
  const [lang, setLang] = useState<'ko'|'zh'|'en'|'ja'|'fr'|'de'>('ko');

  const t = LANGS[lang];

  const fetchData = async () => {
    try {
      setLoading(true);
      // 실제 API 호출 대신 더미 데이터 사용
      const mockStats: Stat[] = [
        { label: t.stats, value: '1,234' },
        { label: t.error, value: '5' },
        { label: t.logs, value: '10,567' }
      ];
      
      const mockLogs: Log[] = [
        { time: '2024-01-15 14:30', event: '시스템 시작', user: t.admin },
        { time: '2024-01-15 14:25', event: '데이터베이스 연결', user: t.manager },
        { time: '2024-01-15 14:20', event: '백업 완료', user: t.admin }
      ];

      setStats(mockStats);
      setLogs(mockLogs);
    } catch (error) {
      console.error('데이터 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [lang]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-lg">{t.loading}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">{t.dashboard}</h1>
          <p className="text-gray-600">{t.lastUpdate}: {new Date().toLocaleString()}</p>
        </div>

        {/* 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {stats.map((stat, index) => (
            <div key={index} className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-700 mb-2">{stat.label}</h3>
              <p className="text-3xl font-bold text-blue-600">{stat.value}</p>
            </div>
          ))}
        </div>

        {/* 차트 섹션 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-700 mb-4">{t.chartTitle}</h3>
            <div className="h-64">
              <Line
                data={{
                  labels: ['1월', '2월', '3월', '4월', '5월', '6월'],
                  datasets: [{
                    label: '트래픽',
                    data: [65, 59, 80, 81, 56, 55],
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                  }]
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: false
                }}
              />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-700 mb-4">{t.barTitle}</h3>
            <div className="h-64">
              <Bar
                data={{
                  labels: ['이벤트 A', '이벤트 B', '이벤트 C', '이벤트 D'],
                  datasets: [{
                    label: '발생 횟수',
                    data: [12, 19, 3, 5],
                    backgroundColor: [
                      'rgba(255, 99, 132, 0.2)',
                      'rgba(54, 162, 235, 0.2)',
                      'rgba(255, 206, 86, 0.2)',
                      'rgba(75, 192, 192, 0.2)',
                    ],
                    borderColor: [
                      'rgba(255, 99, 132, 1)',
                      'rgba(54, 162, 235, 1)',
                      'rgba(255, 206, 86, 1)',
                      'rgba(75, 192, 192, 1)',
                    ],
                    borderWidth: 1
                  }]
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: false
                }}
              />
            </div>
          </div>
        </div>

        {/* 로그 섹션 */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-700">{t.logs}</h3>
            <button
              onClick={fetchData}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              {t.refresh}
            </button>
          </div>
          
          {logs.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      시간
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      이벤트
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      사용자
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {logs.map((log, index) => (
                    <tr key={index}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {log.time}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {log.event}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {log.user}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">{t.logNone}</p>
          )}
        </div>

        {/* 언어 선택 */}
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-4">언어 선택</h3>
          <div className="flex gap-2">
            {(['ko', 'zh', 'en', 'ja', 'fr', 'de'] as const).map((l) => (
              <button
                key={l}
                onClick={() => setLang(l)}
                className={`px-3 py-1 rounded ${
                  lang === l ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'
                }`}
              >
                {LANGS[l].dashboard}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
} 
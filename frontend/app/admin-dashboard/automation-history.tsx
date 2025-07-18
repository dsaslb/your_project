import React, { useEffect, useState } from 'react';

export default function AutomationHistory() {
  const [history, setHistory] = useState<any[]>([]);
  const [status, setStatus] = useState('');
  const [keyword, setKeyword] = useState('');
  const [selected, setSelected] = useState<any|null>(null);

  useEffect(() => {
    let url = '/api/automation-history';
    const params = [];
    if (status) params.push(`status=${status}`);
    if (keyword) params.push(`keyword=${encodeURIComponent(keyword)}`);
    if (params.length) url += '?' + params.join('&');
    fetch(url)
      .then(res => res.json())
      .then(data => setHistory(data.history || []));
  }, [status, keyword]);

  return (
    <section className="p-6" aria-label="자동화 이력">
      <h2 className="text-2xl font-bold mb-4">자동화 이력/검색/필터/상세/실전 대응</h2>
      <div className="mb-4 flex gap-2">
        <select value={status} onChange={e => setStatus(e.target.value)} className="px-2 py-1 border rounded" aria-label="상태 필터">
          <option value="">전체</option>
          <option value="success">정상</option>
          <option value="warning">경고</option>
        </select>
        <input value={keyword} onChange={e => setKeyword(e.target.value)} placeholder="이벤트/키워드 검색" className="px-2 py-1 border rounded" aria-label="이벤트 검색" />
      </div>
      <ul className="list-disc pl-6 space-y-1" role="list">
        {history.length === 0 ? (
          <li className="text-gray-400" aria-live="polite">이력 데이터가 없습니다.</li>
        ) : (
          history.map((h, i) => (
            <li key={h.id || i} className={h.status === 'warning' ? 'text-red-600 font-bold' : ''} role="listitem">
              [{h.timestamp}] {h.event}
              <button className="ml-2 px-2 py-1 text-xs bg-gray-200 rounded hover:bg-gray-300" aria-label="상세 보기" onClick={() => setSelected(h)}>상세</button>
            </li>
          ))
        )}
      </ul>
      {/* 상세 모달 */}
      {selected && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50" role="dialog" aria-modal="true" aria-label="이력 상세 모달">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg shadow-xl">
            <h3 className="text-lg font-bold mb-2">이력 상세</h3>
            <div className="mb-2"><b>이벤트:</b> {selected.event}</div>
            <div className="mb-2"><b>상태:</b> {selected.status}</div>
            <div className="mb-2"><b>발생 시각:</b> {selected.timestamp}</div>
            <button className="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700" onClick={() => setSelected(null)} aria-label="모달 닫기">닫기</button>
          </div>
        </div>
      )}
      <div className="mt-4 text-xs text-gray-500">실제 운영에서는 DB/로그/파일 등과 연동하여 확장 가능합니다.</div>
    </section>
  );
} 
import React, { useEffect, useState } from 'react';

// 플러그인 정보 타입 정의
interface PluginInfo {
  plugin_id: string;
  name: string;
  status: string;
  description?: string;
  author?: string;
  version?: string;
  downloads?: number;
  rating?: number;
  category?: string;
  meta?: any;
}

const API_LIST = '/api/marketplace/list'; // 승인된 플러그인 목록 조회 API (가정)
const API_INSTALL = (id: string) => `/api/marketplace/install/${id}`;
const API_RATING = (id: string) => `/api/marketplace/rating/${id}`;
const API_FEEDBACK = (id: string) => `/api/marketplace/feedback/${id}`;

const categories = ['전체', '비즈니스', '분석', '알림', '기타'];
const sortOptions = [
  { value: 'latest', label: '최신순' },
  { value: 'rating', label: '별점순' },
  { value: 'downloads', label: '다운로드순' }
];

// 브랜드/업종별 탭/필터 예시(실제 브랜드/업종 목록은 필요시 API로 불러올 수 있음)
const brands = ['전체', 'BRAND_A', 'BRAND_B'];
const industries = ['전체', 'RESTAURANT', 'CAFE'];

const PluginMarketplace: React.FC = () => {
  const [plugins, setPlugins] = useState<PluginInfo[]>([]);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('전체');
  const [sort, setSort] = useState('latest');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [selected, setSelected] = useState<PluginInfo | null>(null);
  const [rating, setRating] = useState(0);
  const [review, setReview] = useState('');
  const [feedback, setFeedback] = useState('');
  const [feedbacks, setFeedbacks] = useState<any[]>([]);
  const [brand, setBrand] = useState('전체');
  const [industry, setIndustry] = useState('전체');

  // 플러그인 목록 불러오기
  const fetchPlugins = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(API_LIST);
      const data = await res.json();
      if (data.success && data.plugins) {
        // 승인된 플러그인만 필터링
        setPlugins(data.plugins.filter((p: PluginInfo) => p.status === 'approved'));
      } else {
        setError('플러그인 목록을 불러오지 못했습니다.');
      }
    } catch (e) {
      setError('서버 오류: ' + (e as any).toString());
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchPlugins();
  }, []);

  // 설치 처리
  const handleInstall = async (plugin_id: string) => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const res = await fetch(API_INSTALL(plugin_id), { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        setSuccess('설치 완료!');
      } else {
        setError(data.msg || '설치 실패');
      }
    } catch (e) {
      setError('서버 오류: ' + (e as any).toString());
    }
    setLoading(false);
  };

  // 별점/리뷰 제출
  const submitRating = async () => {
    if (!selected) return;
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const res = await fetch(API_RATING(selected.plugin_id), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rating, review })
      });
      const data = await res.json();
      if (data.success) {
        setSuccess('별점/리뷰가 등록되었습니다!');
        setRating(0);
        setReview('');
      } else {
        setError(data.msg || '등록 실패');
      }
    } catch (e) {
      setError('서버 오류: ' + (e as any).toString());
    }
    setLoading(false);
  };

  // 피드백/버그 신고 제출
  const submitFeedback = async () => {
    if (!selected) return;
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const res = await fetch(API_FEEDBACK(selected.plugin_id), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ feedback })
      });
      const data = await res.json();
      if (data.success) {
        setSuccess('피드백/버그 신고가 등록되었습니다!');
        setFeedback('');
      } else {
        setError(data.msg || '등록 실패');
      }
    } catch (e) {
      setError('서버 오류: ' + (e as any).toString());
    }
    setLoading(false);
  };

  // 피드백/리뷰 불러오기
  const fetchFeedbacks = async (plugin_id: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(API_FEEDBACK(plugin_id));
      const data = await res.json();
      if (data.success && data.feedbacks) {
        setFeedbacks(data.feedbacks);
      } else {
        setFeedbacks([]);
      }
    } catch {
      setFeedbacks([]);
    }
    setLoading(false);
  };

  // 검색/필터/정렬/브랜드/업종 적용
  let filtered = plugins.filter(p =>
    (category === '전체' || p.category === category) &&
    (brand === '전체' || p.brand_code === brand) &&
    (industry === '전체' || p.industry_code === industry) &&
    (p.name.toLowerCase().includes(search.toLowerCase()) ||
      (p.description || '').toLowerCase().includes(search.toLowerCase()))
  );
  if (sort === 'rating') filtered = [...filtered].sort((a, b) => (b.rating || 0) - (a.rating || 0));
  if (sort === 'downloads') filtered = [...filtered].sort((a, b) => (b.downloads || 0) - (a.downloads || 0));

  return (
    <div style={{ padding: 24 }}>
      <h2>플러그인 마켓플레이스</h2>
      <div style={{ marginBottom: 16 }}>
        {/* 브랜드/업종별 탭/필터 */}
        <select value={brand} onChange={e => setBrand(e.target.value)} style={{ marginRight: 8 }}>
          {brands.map(b => <option key={b} value={b}>{b}</option>)}
        </select>
        <select value={industry} onChange={e => setIndustry(e.target.value)} style={{ marginRight: 8 }}>
          {industries.map(i => <option key={i} value={i}>{i}</option>)}
        </select>
        <input
          type="text"
          placeholder="플러그인 검색..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{ marginRight: 8, padding: 4, width: 200 }}
        />
        <select value={category} onChange={e => setCategory(e.target.value)} style={{ marginRight: 8 }}>
          {categories.map(cat => <option key={cat} value={cat}>{cat}</option>)}
        </select>
        <select value={sort} onChange={e => setSort(e.target.value)}>
          {sortOptions.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
        </select>
      </div>
      {loading && <div>로딩 중...</div>}
      {error && <div style={{ color: 'red' }}>{error}</div>}
      {success && <div style={{ color: 'green' }}>{success}</div>}
      <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: 16 }}>
        <thead>
          <tr>
            <th>이름</th>
            <th>카테고리</th>
            <th>버전</th>
            <th>설명</th>
            <th>개발자</th>
            <th>다운로드</th>
            <th>별점</th>
            <th>상세정보</th>
            <th>설치</th>
          </tr>
        </thead>
        <tbody>
          {filtered.length === 0 && !loading && (
            <tr><td colSpan={9}>플러그인이 없습니다.</td></tr>
          )}
          {filtered.map(plugin => (
            <tr key={plugin.plugin_id} style={{ borderBottom: '1px solid #eee' }}>
              <td>{plugin.name}</td>
              <td>{plugin.category || '-'}</td>
              <td>{plugin.version}</td>
              <td>{plugin.description}</td>
              <td>{plugin.author}</td>
              <td>{plugin.downloads || 0}</td>
              <td>{plugin.rating || '-'}</td>
              <td>
                <button onClick={() => { setSelected(plugin); fetchFeedbacks(plugin.plugin_id); }}>상세</button>
              </td>
              <td>
                <button onClick={() => handleInstall(plugin.plugin_id)} disabled={loading}>설치</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {/* 상세 모달 */}
      {selected && (
        <div style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: 'rgba(0,0,0,0.3)', zIndex: 9999 }} onClick={() => setSelected(null)}>
          <div style={{ background: '#fff', padding: 24, borderRadius: 8, width: 600, margin: '40px auto', position: 'relative' }} onClick={e => e.stopPropagation()}>
            <h3>{selected.name} 상세정보</h3>
            <pre style={{ fontSize: 12 }}>{JSON.stringify(selected.meta, null, 2)}</pre>
            <div style={{ marginTop: 16 }}>
              <strong>별점 주기:</strong>
              {[1,2,3,4,5].map(star => (
                <span key={star} style={{ cursor: 'pointer', color: rating >= star ? 'gold' : '#ccc', fontSize: 24 }} onClick={() => setRating(star)}>★</span>
              ))}
              <input type="text" placeholder="리뷰(선택)" value={review} onChange={e => setReview(e.target.value)} style={{ marginLeft: 8, width: 200 }} />
              <button onClick={submitRating} style={{ marginLeft: 8 }}>별점/리뷰 등록</button>
            </div>
            <div style={{ marginTop: 16 }}>
              <strong>피드백/버그 신고:</strong>
              <input type="text" placeholder="피드백/버그 내용" value={feedback} onChange={e => setFeedback(e.target.value)} style={{ marginLeft: 8, width: 300 }} />
              <button onClick={submitFeedback} style={{ marginLeft: 8 }}>신고</button>
            </div>
            <div style={{ marginTop: 16 }}>
              <strong>리뷰/피드백 목록</strong>
              <ul>
                {feedbacks.length === 0 && <li>리뷰/피드백이 없습니다.</li>}
                {feedbacks.map((f, i) => (
                  <li key={i}>{f.rating ? `★${f.rating}` : ''} {f.review || f.feedback} - {f.user || ''} ({f.timestamp})</li>
                ))}
              </ul>
            </div>
            <button onClick={() => setSelected(null)} style={{ position: 'absolute', top: 8, right: 8 }}>닫기</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default PluginMarketplace; 
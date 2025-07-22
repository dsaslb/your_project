import React, { useEffect, useState } from 'react';
import { useToast } from '../../components/GlobalToast';

interface Plugin {
  id: string;
  name: string;
  description?: string;
  version?: string;
  author?: string;
}

const PluginMarket: React.FC = () => {
  const [market, setMarket] = useState<Plugin[]>([]);
  const [installed, setInstalled] = useState<Plugin[]>([]);
  const [q, setQ] = useState('');
  const [loading, setLoading] = useState(true);
  const { showToast } = useToast();

  const fetchMarket = async () => {
    setLoading(true);
    try {
      const res = await fetch(`/api/admin/plugins/market?q=${encodeURIComponent(q)}`);
      const data = await res.json();
      setMarket(data.plugins || []);
    } catch {
      showToast('마켓 목록을 불러오지 못했습니다.', 'error');
    } finally {
      setLoading(false);
    }
  };
  const fetchInstalled = async () => {
    try {
      const res = await fetch('/api/admin/plugins/installed');
      const data = await res.json();
      setInstalled(data.plugins || []);
    } catch {
      showToast('설치 목록을 불러오지 못했습니다.', 'error');
    }
  };

  useEffect(() => {
    fetchMarket();
    fetchInstalled();
    // eslint-disable-next-line
  }, [q]);

  const handleInstall = async (plugin: Plugin) => {
    try {
      const res = await fetch('/api/admin/plugins/install', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plugin_id: plugin.id }),
      });
      if (res.ok) {
        showToast('설치 완료', 'success');
        fetchInstalled();
      } else {
        showToast('설치 실패', 'error');
      }
    } catch {
      showToast('설치 실패', 'error');
    }
  };
  const handleUninstall = async (plugin: Plugin) => {
    if (!window.confirm('정말 삭제하시겠습니까?')) return;
    try {
      const res = await fetch('/api/admin/plugins/uninstall', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plugin_id: plugin.id }),
      });
      if (res.ok) {
        showToast('삭제 완료', 'success');
        fetchInstalled();
      } else {
        showToast('삭제 실패', 'error');
      }
    } catch {
      showToast('삭제 실패', 'error');
    }
  };
  const handleUpdate = async (plugin: Plugin) => {
    try {
      const res = await fetch('/api/admin/plugins/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plugin_id: plugin.id }),
      });
      if (res.ok) {
        showToast('업데이트 완료', 'success');
        fetchInstalled();
      } else {
        showToast('업데이트 실패', 'error');
      }
    } catch {
      showToast('업데이트 실패', 'error');
    }
  };

  const isInstalled = (plugin: Plugin) => installed.some(p => p.id === plugin.id);

  return (
    <div className="p-4 max-w-4xl mx-auto">
      <h2 className="text-xl font-bold mb-4">플러그인 마켓</h2>
      <div className="mb-2 flex gap-2">
        <input
          type="text"
          placeholder="플러그인 검색..."
          value={q}
          onChange={e => setQ(e.target.value)}
          className="border rounded px-2 py-1 text-sm w-64"
        />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="font-semibold mb-2">마켓 플러그인</h3>
          {loading ? (
            <div className="text-gray-500">불러오는 중...</div>
          ) : (
            <ul className="divide-y">
              {market.map((p) => (
                <li key={p.id} className="py-2 flex flex-col md:flex-row md:items-center md:justify-between gap-2">
                  <div>
                    <div className="font-bold">{p.name}</div>
                    <div className="text-xs text-gray-500">{p.description}</div>
                    <div className="text-xs text-gray-400">{p.version} {p.author && `| ${p.author}`}</div>
                  </div>
                  <div>
                    {isInstalled(p) ? (
                      <button className="bg-gray-300 text-gray-600 px-2 py-1 rounded mr-2" disabled>
                        설치됨
                      </button>
                    ) : (
                      <button className="bg-blue-600 text-white px-2 py-1 rounded" onClick={() => handleInstall(p)}>
                        설치
                      </button>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
        <div>
          <h3 className="font-semibold mb-2">설치된 플러그인</h3>
          <ul className="divide-y">
            {installed.length === 0 ? (
              <li className="text-gray-400 py-2">설치된 플러그인 없음</li>
            ) : (
              installed.map((p) => (
                <li key={p.id} className="py-2 flex flex-col md:flex-row md:items-center md:justify-between gap-2">
                  <div>
                    <div className="font-bold">{p.name}</div>
                    <div className="text-xs text-gray-500">{p.description}</div>
                    <div className="text-xs text-gray-400">{p.version} {p.author && `| ${p.author}`}</div>
                  </div>
                  <div className="flex gap-2">
                    <button className="bg-yellow-500 text-white px-2 py-1 rounded" onClick={() => handleUpdate(p)}>
                      업데이트
                    </button>
                    <button className="bg-red-600 text-white px-2 py-1 rounded" onClick={() => handleUninstall(p)}>
                      삭제
                    </button>
                  </div>
                </li>
              ))
            )}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default PluginMarket; 
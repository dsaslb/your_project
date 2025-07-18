import React, { useEffect, useState } from 'react';
import { apiFetch } from '../../utils/api';

type Plugin = {
  id: string;
  name: string;
  description: string;
  is_active: boolean;
};

type PluginManagerProps = {
  level: 'industry' | 'brand' | 'branch' | 'user';
};

const PluginManager: React.FC<PluginManagerProps> = ({ level }) => {
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updating, setUpdating] = useState<string | null>(null);

  useEffect(() => {
    fetchPlugins();
  }, [level]);

  async function fetchPlugins() {
    setLoading(true);
    setError(null);
    try {
      const data = await apiFetch<Plugin[]>(`/api/plugins?level=${level}`);
      setPlugins(data);
    } catch (e) {
      setPlugins([
        { id: 'attendance', name: '출근 관리', description: '직원 출근/퇴근 관리', is_active: true },
        { id: 'inventory', name: '재고 관리', description: '상품별 재고 추적', is_active: false },
        { id: 'purchase', name: '구매 관리', description: '발주/공급업체 관리', is_active: true },
        { id: 'schedule', name: '스케줄 관리', description: '직원 스케줄 관리', is_active: false },
        { id: 'ai-analytics', name: 'AI 분석', description: '매출/근태/운영 데이터 분석', is_active: true },
      ]);
      setError('API 연동 실패, 샘플 데이터로 대체');
    }
    setLoading(false);
  }

  async function togglePlugin(pluginId: string, isActive: boolean) {
    setUpdating(pluginId);
    try {
      const endpoint = isActive ? 'enable' : 'disable';
      await apiFetch(`/api/plugins/${pluginId}/${endpoint}`, {
        method: 'POST',
        body: JSON.stringify({ level })
      });
      
      // 로컬 상태 업데이트
      setPlugins(prev => prev.map(plugin => 
        plugin.id === pluginId ? { ...plugin, is_active: isActive } : plugin
      ));
    } catch (e) {
      setError(`플러그인 ${isActive ? '활성화' : '비활성화'} 실패`);
    }
    setUpdating(null);
  }

  async function updatePermission(pluginId: string, targetType: string, targetId: string, isAllowed: boolean) {
    setUpdating(pluginId);
    try {
      await apiFetch(`/api/plugins/${pluginId}/access-control/${targetType}`, {
        method: 'POST',
        body: JSON.stringify({
          [`${targetType}_id`]: targetId,
          is_allowed: isAllowed,
          access_type: 'use'
        })
      });
    } catch (e) {
      setError(`권한 설정 실패`);
    }
    setUpdating(null);
  }

  if (loading) {
    return <div className="border rounded p-4 bg-gray-50">로딩 중...</div>;
  }

  return (
    <div className="border rounded p-4 bg-gray-50">
      <h3 className="font-semibold mb-4">플러그인 관리 ({level})</h3>
      
      <div className="space-y-4">
        {plugins.map((plugin) => (
          <div key={plugin.id} className="border rounded p-3 bg-white">
            <div className="flex items-center justify-between mb-2">
              <div>
                <h4 className="font-medium">{plugin.name}</h4>
                <p className="text-sm text-gray-600">{plugin.description}</p>
              </div>
              <div className="flex items-center space-x-2">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={plugin.is_active}
                    onChange={(e) => togglePlugin(plugin.id, e.target.checked)}
                    disabled={updating === plugin.id}
                    className="mr-2"
                  />
                  {updating === plugin.id ? '업데이트 중...' : (plugin.is_active ? 'ON' : 'OFF')}
                </label>
              </div>
            </div>
            
            {/* 권한 분배 UI (브랜드/매장 관리자 레벨에서만 표시) */}
            {level !== 'user' && plugin.is_active && (
              <div className="mt-3 pt-3 border-t">
                <h5 className="text-sm font-medium mb-2">권한 분배</h5>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  {level === 'industry' && (
                    <>
                      <label className="flex items-center">
                        <input
                          type="checkbox"
                          defaultChecked={true}
                          onChange={(e) => updatePermission(plugin.id, 'brand', 'all', e.target.checked)}
                          className="mr-2"
                        />
                        브랜드 관리자
                      </label>
                    </>
                  )}
                  {level === 'brand' && (
                    <>
                      <label className="flex items-center">
                        <input
                          type="checkbox"
                          defaultChecked={true}
                          onChange={(e) => updatePermission(plugin.id, 'store', 'all', e.target.checked)}
                          className="mr-2"
                        />
                        매장 관리자
                      </label>
                      <label className="flex items-center">
                        <input
                          type="checkbox"
                          defaultChecked={false}
                          onChange={(e) => updatePermission(plugin.id, 'user', 'all', e.target.checked)}
                          className="mr-2"
                        />
                        직원
                      </label>
                    </>
                  )}
                  {level === 'branch' && (
                    <>
                      <label className="flex items-center">
                        <input
                          type="checkbox"
                          defaultChecked={false}
                          onChange={(e) => updatePermission(plugin.id, 'user', 'all', e.target.checked)}
                          className="mr-2"
                        />
                        직원
                      </label>
                    </>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
      
      {error && (
        <div className="text-red-500 mt-4 p-2 bg-red-50 rounded">
          {error}
        </div>
      )}
    </div>
  );
};

export default PluginManager; 
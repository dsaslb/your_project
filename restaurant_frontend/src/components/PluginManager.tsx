import React from 'react';
import { useGlobalStore, Plugin } from '../store/useGlobalStore';

const PluginManager: React.FC = () => {
  const plugins = useGlobalStore((state) => state.plugins);
  const addPlugin = useGlobalStore((state) => state.addPlugin);

  // 샘플 플러그인 데이터
  const samplePlugins: Plugin[] = [
    { id: 'reservation', name: '예약 관리', enabled: false },
    { id: 'medical', name: '진료 관리', enabled: false },
    { id: 'beauty', name: '시술 관리', enabled: false },
    { id: 'inventory', name: '재고 관리', enabled: true },
    { id: 'notification', name: '알림 시스템', enabled: true },
  ];

  const handleTogglePlugin = (pluginId: string) => {
    const plugin = samplePlugins.find(p => p.id === pluginId);
    if (plugin) {
      addPlugin({ ...plugin, enabled: !plugin.enabled });
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6">
      <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">플러그인 관리</h3>
      <div className="space-y-3">
        {samplePlugins.map((plugin) => (
          <div key={plugin.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div>
              <span className="font-medium text-gray-900 dark:text-white">{plugin.name}</span>
              <p className="text-sm text-gray-500">업종별 맞춤 기능</p>
            </div>
            <button
              onClick={() => handleTogglePlugin(plugin.id)}
              className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                plugin.enabled
                  ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                  : 'bg-gray-100 text-gray-600 dark:bg-gray-600 dark:text-gray-300'
              }`}
            >
              {plugin.enabled ? '활성화' : '비활성화'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PluginManager; 
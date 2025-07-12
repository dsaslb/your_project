import React, { useState, useEffect } from 'react';
import { useGlobalStore } from '@/store/useGlobalStore';

interface SecuritySettings {
  sessionTimeout: number;
  requireMFA: boolean;
  passwordPolicy: {
    minLength: number;
    requireSpecialChar: boolean;
    requireNumber: boolean;
    requireUppercase: boolean;
  };
  auditLogging: boolean;
}

const SecurityManager: React.FC = () => {
  const [settings, setSettings] = useState<SecuritySettings>({
    sessionTimeout: 30,
    requireMFA: false,
    passwordPolicy: {
      minLength: 8,
      requireSpecialChar: true,
      requireNumber: true,
      requireUppercase: true,
    },
    auditLogging: true,
  });

  const [tokenInfo, setTokenInfo] = useState<any>(null);
  const [securityLogs, setSecurityLogs] = useState<any[]>([]);

  useEffect(() => {
    // JWT 토큰 정보 파싱
    const token = localStorage.getItem('auth_token');
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        setTokenInfo({
          userId: payload.user_id,
          role: payload.role,
          exp: new Date(payload.exp * 1000),
          iat: new Date(payload.iat * 1000),
        });
      } catch (error) {
        console.error('토큰 파싱 오류:', error);
      }
    }

    // 보안 로그 로드
    loadSecurityLogs();
  }, []);

  const loadSecurityLogs = async () => {
    try {
      // 실제 보안 로그 API 호출
      const response = await fetch('/api/security/logs', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSecurityLogs(data.logs);
      } else {
        // API 호출 실패 시 더미 데이터 사용
        setSecurityLogs([
          {
            id: 1,
            timestamp: new Date(),
            action: '로그인',
            user: 'admin',
            ip: '192.168.1.100',
            status: '성공',
          },
          {
            id: 2,
            timestamp: new Date(Date.now() - 3600000),
            action: '권한 변경',
            user: 'admin',
            ip: '192.168.1.100',
            status: '성공',
          },
          {
            id: 3,
            timestamp: new Date(Date.now() - 7200000),
            action: '로그인 시도',
            user: 'unknown',
            ip: '192.168.1.101',
            status: '실패',
          },
        ]);
      }
    } catch (error) {
      console.error('보안 로그 로드 실패:', error);
      setSecurityLogs([]);
    }
  };

  const refreshToken = async () => {
    try {
      // TODO: 실제 토큰 갱신 API 호출
      console.log('토큰 갱신 중...');
      // 새로운 토큰을 받아서 localStorage 업데이트
    } catch (error) {
      console.error('토큰 갱신 실패:', error);
    }
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    window.location.href = '/login';
  };

  const updateSecuritySettings = (newSettings: Partial<SecuritySettings>) => {
    setSettings(prev => ({ ...prev, ...newSettings }));
    // TODO: 실제 설정 저장 API 호출
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6">
      <div className="flex items-center space-x-3 mb-6">
        <div className="w-12 h-12 bg-gradient-to-br from-red-400 to-red-600 rounded-xl flex items-center justify-center">
          <span className="text-2xl">🔒</span>
        </div>
        <div>
          <h3 className="text-xl font-bold text-gray-900 dark:text-white">보안 관리</h3>
          <p className="text-sm text-gray-500">JWT 토큰, 권한, 보안 설정 관리</p>
        </div>
      </div>

      <div className="space-y-6">
        {/* JWT 토큰 정보 */}
        {tokenInfo && (
          <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
            <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-3">JWT 토큰 정보</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-blue-800 dark:text-blue-200">사용자 ID:</span>
                <span className="font-medium">{tokenInfo.userId}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-blue-800 dark:text-blue-200">권한:</span>
                <span className="font-medium">{tokenInfo.role}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-blue-800 dark:text-blue-200">만료 시간:</span>
                <span className="font-medium">{tokenInfo.exp.toLocaleString()}</span>
              </div>
            </div>
            <div className="flex space-x-2 mt-3">
              <button
                onClick={refreshToken}
                className="px-3 py-1 bg-blue-500 text-white rounded text-xs hover:bg-blue-600"
              >
                토큰 갱신
              </button>
              <button
                onClick={logout}
                className="px-3 py-1 bg-red-500 text-white rounded text-xs hover:bg-red-600"
              >
                로그아웃
              </button>
            </div>
          </div>
        )}

        {/* 보안 설정 */}
        <div>
          <h4 className="font-medium text-gray-900 dark:text-white mb-3">보안 설정</h4>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-700 dark:text-gray-300">세션 타임아웃 (분)</span>
              <input
                type="number"
                value={settings.sessionTimeout}
                onChange={(e) => updateSecuritySettings({ sessionTimeout: parseInt(e.target.value) })}
                className="w-20 px-2 py-1 border rounded text-sm"
                min="5"
                max="120"
              />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-700 dark:text-gray-300">2단계 인증</span>
              <input
                type="checkbox"
                checked={settings.requireMFA}
                onChange={(e) => updateSecuritySettings({ requireMFA: e.target.checked })}
                className="w-4 h-4"
              />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-700 dark:text-gray-300">감사 로그</span>
              <input
                type="checkbox"
                checked={settings.auditLogging}
                onChange={(e) => updateSecuritySettings({ auditLogging: e.target.checked })}
                className="w-4 h-4"
              />
            </div>
          </div>
        </div>

        {/* 보안 로그 */}
        <div>
          <h4 className="font-medium text-gray-900 dark:text-white mb-3">보안 로그</h4>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {securityLogs.map((log) => (
              <div key={log.id} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded text-xs">
                <div className="flex items-center space-x-2">
                  <span className={`w-2 h-2 rounded-full ${
                    log.status === '성공' ? 'bg-green-400' : 'bg-red-400'
                  }`}></span>
                  <span className="text-gray-600 dark:text-gray-300">{log.action}</span>
                </div>
                <div className="text-gray-500 dark:text-gray-400">
                  {log.timestamp.toLocaleTimeString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SecurityManager; 

"use client";

import { useSecurityEvents, useSecuritySettings } from "@/hooks/useSecurity";
import { 
  Shield, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Eye, 
  Lock, 
  UserCheck,
  FileText,
  Activity
} from "lucide-react";

interface SecurityDashboardProps {
  className?: string;
}

export default function SecurityDashboard({ className = "" }: SecurityDashboardProps) {
  const { data: securityEvents, isLoading: eventsLoading } = useSecurityEvents({
    page: 1,
    per_page: 10
  });
  
  const { data: securitySettings, isLoading: settingsLoading } = useSecuritySettings();

  if (eventsLoading || settingsLoading) {
    return (
      <div className={`bg-white rounded-lg shadow-sm border p-6 ${className}`}>
        <h2 className="text-xl font-semibold text-gray-900 mb-6">보안 대시보드</h2>
        <div className="space-y-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="animate-pulse">
              <div className="h-12 bg-gray-200 rounded-lg"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  const getEventIcon = (eventType: string) => {
    switch (eventType) {
      case 'login_attempt':
        return <UserCheck className="h-4 w-4 text-blue-600" />;
      case 'failed_login':
        return <AlertTriangle className="h-4 w-4 text-red-600" />;
      case 'file_upload':
        return <FileText className="h-4 w-4 text-green-600" />;
      case 'permission_change':
        return <Lock className="h-4 w-4 text-purple-600" />;
      default:
        return <Activity className="h-4 w-4 text-gray-600" />;
    }
  };

  const getEventColor = (eventType: string) => {
    switch (eventType) {
      case 'failed_login':
        return 'text-red-600';
      case 'login_attempt':
        return 'text-blue-600';
      case 'file_upload':
        return 'text-green-600';
      case 'permission_change':
        return 'text-purple-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className={`bg-white rounded-lg shadow-sm border p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">보안 대시보드</h2>
        <div className="flex items-center space-x-2 text-xs text-gray-500">
          <Shield className="h-3 w-3" />
          <span>실시간 모니터링</span>
        </div>
      </div>
      
      {/* 보안 설정 요약 */}
      <div className="mb-6">
        <h3 className="text-sm font-medium text-gray-900 mb-3">보안 설정</h3>
        <div className="grid grid-cols-2 gap-3">
          <div className="p-3 bg-blue-50 rounded-lg">
            <div className="flex items-center space-x-2">
              <Lock className="h-4 w-4 text-blue-600" />
              <span className="text-sm font-medium text-blue-900">최대 로그인 시도</span>
            </div>
            <div className="text-lg font-bold text-blue-600 mt-1">
              {securitySettings?.max_login_attempts || 5}회
            </div>
          </div>
          
          <div className="p-3 bg-green-50 rounded-lg">
            <div className="flex items-center space-x-2">
              <Clock className="h-4 w-4 text-green-600" />
              <span className="text-sm font-medium text-green-900">세션 타임아웃</span>
            </div>
            <div className="text-lg font-bold text-green-600 mt-1">
              {securitySettings?.session_timeout || 30}분
            </div>
          </div>
          
          <div className="p-3 bg-purple-50 rounded-lg">
            <div className="flex items-center space-x-2">
              <Eye className="h-4 w-4 text-purple-600" />
              <span className="text-sm font-medium text-purple-900">2FA 요구</span>
            </div>
            <div className="text-lg font-bold text-purple-600 mt-1">
              {securitySettings?.require_2fa ? '활성화' : '비활성화'}
            </div>
          </div>
          
          <div className="p-3 bg-orange-50 rounded-lg">
            <div className="flex items-center space-x-2">
              <Shield className="h-4 w-4 text-orange-600" />
              <span className="text-sm font-medium text-orange-900">비밀번호 만료</span>
            </div>
            <div className="text-lg font-bold text-orange-600 mt-1">
              {securitySettings?.password_expiry_days || 90}일
            </div>
          </div>
        </div>
      </div>

      {/* 최근 보안 이벤트 */}
      <div>
        <h3 className="text-sm font-medium text-gray-900 mb-3">최근 보안 이벤트</h3>
        <div className="space-y-3">
          {securityEvents?.logs?.slice(0, 5).map((event: any, index: number) => (
            <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
              {getEventIcon(event.type)}
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <span className={`text-sm font-medium ${getEventColor(event.type)}`}>
                    {event.type === 'login_attempt' && '로그인 시도'}
                    {event.type === 'failed_login' && '로그인 실패'}
                    {event.type === 'file_upload' && '파일 업로드'}
                    {event.type === 'permission_change' && '권한 변경'}
                    {event.type === 'security_alert' && '보안 경고'}
                    {!['login_attempt', 'failed_login', 'file_upload', 'permission_change', 'security_alert'].includes(event.type) && event.type}
                  </span>
                  {event.severity === 'high' && (
                    <span className="px-2 py-1 text-xs bg-red-100 text-red-800 rounded-full">
                      높음
                    </span>
                  )}
                  {event.severity === 'medium' && (
                    <span className="px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded-full">
                      중간
                    </span>
                  )}
                  {event.severity === 'low' && (
                    <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
                      낮음
                    </span>
                  )}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {event.message || '보안 이벤트가 발생했습니다'}
                </div>
                <div className="text-xs text-gray-400 mt-1">
                  {event.timestamp ? 
                    new Date(event.timestamp).toLocaleString('ko-KR') : 
                    '알 수 없음'
                  }
                </div>
              </div>
            </div>
          ))}
          
          {(!securityEvents?.logs || securityEvents.logs.length === 0) && (
            <div className="text-center py-8 text-gray-500">
              <CheckCircle className="h-8 w-8 mx-auto mb-2 text-green-500" />
              <p>최근 보안 이벤트가 없습니다</p>
            </div>
          )}
        </div>
      </div>

      {/* 보안 통계 */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h3 className="text-sm font-medium text-gray-900 mb-3">보안 통계</h3>
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-lg font-bold text-blue-600">
              {securityEvents?.logs?.filter((e: any) => e.type === 'login_attempt').length || 0}
            </div>
            <div className="text-xs text-gray-600">로그인 시도</div>
          </div>
          <div>
            <div className="text-lg font-bold text-red-600">
              {securityEvents?.logs?.filter((e: any) => e.type === 'failed_login').length || 0}
            </div>
            <div className="text-xs text-gray-600">실패한 로그인</div>
          </div>
          <div>
            <div className="text-lg font-bold text-green-600">
              {securityEvents?.logs?.filter((e: any) => e.severity === 'high').length || 0}
            </div>
            <div className="text-xs text-gray-600">높은 위험도</div>
          </div>
        </div>
      </div>

      {/* 보안 권장사항 */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h3 className="text-sm font-medium text-blue-900 mb-2">보안 권장사항</h3>
        <ul className="text-xs text-blue-800 space-y-1">
          {securitySettings?.require_2fa === false && (
            <li>• 2단계 인증을 활성화하여 계정 보안을 강화하세요.</li>
          )}
          {(securityEvents?.logs?.filter((e: any) => e.type === 'failed_login').length || 0) > 5 && (
            <li>• 로그인 실패가 많습니다. 비밀번호를 변경하거나 계정을 잠그세요.</li>
          )}
          {securitySettings?.password_expiry_days > 90 && (
            <li>• 비밀번호 만료 기간을 90일 이하로 설정하는 것을 권장합니다.</li>
          )}
          {(!securityEvents?.logs || securityEvents.logs.length === 0) && (
            <li>• 모든 보안 설정이 적절하게 구성되어 있습니다.</li>
          )}
        </ul>
      </div>
    </div>
  );
} 
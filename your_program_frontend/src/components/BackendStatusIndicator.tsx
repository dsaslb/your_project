"use client";
import { useState, useEffect } from 'react';
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Loader2, Wifi, WifiOff, Server } from "lucide-react";
import apiClient from '@/lib/api-client';

interface BackendStatusIndicatorProps {
  children?: React.ReactNode;
  showDummyData?: boolean;
}

export default function BackendStatusIndicator({ 
  children, 
  showDummyData = false 
}: BackendStatusIndicatorProps) {
  const [backendStatus, setBackendStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking');

  // const checkBackendStatus = async () => {
  //   try {
  //     const isConnected = await apiClient.checkBackendStatus();
  //     setBackendStatus(isConnected ? 'connected' : 'disconnected');
  //   } catch (error) {
  //     console.error('Backend status check failed:', error);
  //     setBackendStatus('disconnected');
  //   }
  // };

  if (backendStatus === 'checking') {
    return (
      <Alert>
        <Loader2 className="h-4 w-4 animate-spin" />
        <AlertDescription>백엔드 서버 연결 상태를 확인 중입니다...</AlertDescription>
      </Alert>
    );
  }

  if (backendStatus === 'disconnected') {
    return (
      <div className="space-y-4">
        <Alert variant="destructive">
          <WifiOff className="h-4 w-4" />
          <AlertDescription>
            <div className="flex items-center gap-2">
              <span>백엔드 서버에 연결할 수 없습니다.</span>
              <Badge variant="secondary">프론트엔드 모드</Badge>
            </div>
            <p className="text-sm mt-1">
              실제 데이터 대신 더미 데이터가 표시됩니다. 
              백엔드 서버를 실행하면 실시간 데이터를 확인할 수 있습니다.
            </p>
          </AlertDescription>
        </Alert>
        {showDummyData && children}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <Alert>
        <Wifi className="h-4 w-4" />
        <AlertDescription>
          <div className="flex items-center gap-2">
            <span>백엔드 서버에 정상적으로 연결되었습니다.</span>
            <Badge variant="default">실시간 모드</Badge>
          </div>
        </AlertDescription>
      </Alert>
      {children}
    </div>
  );
}

// 더미 데이터 훅
export function useDummyData() {
  const [backendStatus, setBackendStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking');

  // const checkBackendStatus = async () => {
  //   try {
  //     const isConnected = await apiClient.checkBackendStatus();
  //     setBackendStatus(isConnected ? 'connected' : 'disconnected');
  //   } catch (error) {
  //     setBackendStatus('disconnected');
  //   }
  // };

  const getDummyStats = () => ({
    totalUsers: 25,
    activeUsers: 18,
    totalOrders: 156,
    totalRevenue: 2500000,
    recentActivities: [
      { type: 'user_join', message: '새 직원 가입', time: '5분 전' },
      { type: 'order', message: '발주 승인', time: '10분 전' },
      { type: 'schedule', message: '근무표 수정', time: '15분 전' }
    ]
  });

  const getDummyOrders = () => ({
    orders: [
      { id: 1, customer: '김철수', items: ['김치찌개', '밥'], status: 'pending', total: 15000 },
      { id: 2, customer: '이영희', items: ['된장찌개', '밥'], status: 'completed', total: 12000 },
      { id: 3, customer: '박민수', items: ['비빔밥'], status: 'preparing', total: 8000 }
    ],
    total: 3,
    pending: 1,
    completed: 1,
    preparing: 1
  });

  return {
    backendStatus,
    isConnected: backendStatus === 'connected',
    isDisconnected: backendStatus === 'disconnected',
    getDummyStats,
    getDummyOrders
  };
} 
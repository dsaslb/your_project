'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { api } from '@/lib/api-client';
import { toast } from 'sonner';

export function RealTimeTest() {
  const [isLoading, setIsLoading] = useState(false);

  const sendTestNotification = async (type: 'info' | 'success' | 'warning' | 'error') => {
    setIsLoading(true);
    try {
      const response = await api.post('/api/test/notification', {
        type,
        message: `${type} 타입의 테스트 알림입니다.`
      });
      
      if (response.success) {
        toast.success('알림이 전송되었습니다.');
      }
    } catch (error) {
      toast.error('알림 전송에 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const sendTestSystemAlert = async (severity: 'low' | 'medium' | 'high' | 'critical') => {
    setIsLoading(true);
    try {
      const response = await api.post('/api/test/system-alert', {
        severity,
        message: `${severity} 심각도의 시스템 알림입니다.`
      });
      
      if (response.success) {
        toast.success('시스템 알림이 전송되었습니다.');
      }
    } catch (error) {
      toast.error('시스템 알림 전송에 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          실시간 테스트
          <Badge variant="outline">WebSocket</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <h4 className="font-medium mb-2">알림 테스트</h4>
          <div className="grid grid-cols-2 gap-2">
            <Button
              size="sm"
              variant="outline"
              onClick={() => sendTestNotification('info')}
              disabled={isLoading}
            >
              Info
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => sendTestNotification('success')}
              disabled={isLoading}
            >
              Success
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => sendTestNotification('warning')}
              disabled={isLoading}
            >
              Warning
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => sendTestNotification('error')}
              disabled={isLoading}
            >
              Error
            </Button>
          </div>
        </div>
        
        <div>
          <h4 className="font-medium mb-2">시스템 알림 테스트</h4>
          <div className="grid grid-cols-2 gap-2">
            <Button
              size="sm"
              variant="outline"
              onClick={() => sendTestSystemAlert('low')}
              disabled={isLoading}
            >
              Low
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => sendTestSystemAlert('medium')}
              disabled={isLoading}
            >
              Medium
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => sendTestSystemAlert('high')}
              disabled={isLoading}
            >
              High
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => sendTestSystemAlert('critical')}
              disabled={isLoading}
            >
              Critical
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
} 
'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { useRealtimeUpdates } from '@/hooks/useRealtimeUpdates';
import { formatDistanceToNow } from 'date-fns';
import { ko } from 'date-fns/locale';
import { 
  Clock, 
  Package, 
  ShoppingCart, 
  Wifi, 
  WifiOff, 
  Trash2,
  RefreshCw
} from 'lucide-react';

export function RealtimeUpdates() {
  const {
    attendanceUpdates,
    inventoryUpdates,
    purchaseOrderUpdates,
    isConnected,
    lastUpdate,
    hasUpdates,
    totalUpdates,
    clearUpdates,
    clearUpdatesByType,
  } = useRealtimeUpdates();

  const formatTime = (timestamp: string) => {
    return formatDistanceToNow(new Date(timestamp), { 
      addSuffix: true, 
      locale: ko 
    });
  };

  return (
    <div className="space-y-6">
      {/* 연결 상태 및 제어 패널 */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <CardTitle className="text-lg">실시간 업데이트</CardTitle>
              <Badge variant={isConnected ? "default" : "destructive"} className="flex items-center space-x-1">
                {isConnected ? (
                  <>
                    <Wifi className="h-3 w-3" />
                    <span>연결됨</span>
                  </>
                ) : (
                  <>
                    <WifiOff className="h-3 w-3" />
                    <span>연결 끊김</span>
                  </>
                )}
              </Badge>
            </div>
            <div className="flex items-center space-x-2">
              {hasUpdates && (
                <Badge variant="secondary" className="flex items-center space-x-1">
                  <RefreshCw className="h-3 w-3" />
                  <span>{totalUpdates}개 업데이트</span>
                </Badge>
              )}
              <Button
                variant="outline"
                size="sm"
                onClick={clearUpdates}
                disabled={!hasUpdates}
                className="flex items-center space-x-1"
              >
                <Trash2 className="h-3 w-3" />
                <span>전체 삭제</span>
              </Button>
            </div>
          </div>
          <CardDescription>
            모바일 앱에서 발생하는 실시간 업데이트를 확인하세요.
            {lastUpdate && (
              <span className="ml-2 text-muted-foreground">
                마지막 업데이트: {formatTime(lastUpdate.toISOString())}
              </span>
            )}
          </CardDescription>
        </CardHeader>
      </Card>

      {/* 출퇴근 업데이트 */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Clock className="h-5 w-5 text-blue-500" />
              <CardTitle className="text-base">출퇴근 기록</CardTitle>
              {attendanceUpdates.length > 0 && (
                <Badge variant="outline">{attendanceUpdates.length}</Badge>
              )}
            </div>
            {attendanceUpdates.length > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => clearUpdatesByType('attendance')}
                className="text-muted-foreground hover:text-foreground"
              >
                <Trash2 className="h-3 w-3" />
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {attendanceUpdates.length === 0 ? (
            <p className="text-muted-foreground text-sm">출퇴근 기록이 없습니다.</p>
          ) : (
            <div className="space-y-3">
              {attendanceUpdates.map((update, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <Badge variant={update.type === 'in' ? 'default' : 'secondary'}>
                      {update.type === 'in' ? '출근' : '퇴근'}
                    </Badge>
                    <div>
                      <p className="font-medium">{update.user_name}</p>
                      <p className="text-sm text-muted-foreground">
                        {formatTime(update.timestamp)}
                      </p>
                    </div>
                  </div>
                  {update.location && (
                    <div className="text-xs text-muted-foreground">
                      위치: {update.location.lat.toFixed(4)}, {update.location.lng.toFixed(4)}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* 재고 업데이트 */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Package className="h-5 w-5 text-green-500" />
              <CardTitle className="text-base">재고 조사</CardTitle>
              {inventoryUpdates.length > 0 && (
                <Badge variant="outline">{inventoryUpdates.length}</Badge>
              )}
            </div>
            {inventoryUpdates.length > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => clearUpdatesByType('inventory')}
                className="text-muted-foreground hover:text-foreground"
              >
                <Trash2 className="h-3 w-3" />
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {inventoryUpdates.length === 0 ? (
            <p className="text-muted-foreground text-sm">재고 조사 기록이 없습니다.</p>
          ) : (
            <div className="space-y-3">
              {inventoryUpdates.map((update, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <Badge variant="outline">{update.quantity}개</Badge>
                    <div>
                      <p className="font-medium">{update.product_name}</p>
                      <p className="text-sm text-muted-foreground">
                        {update.user_name} • {formatTime(update.timestamp)}
                      </p>
                    </div>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    바코드: {update.barcode}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* 발주 업데이트 */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <ShoppingCart className="h-5 w-5 text-orange-500" />
              <CardTitle className="text-base">발주 요청</CardTitle>
              {purchaseOrderUpdates.length > 0 && (
                <Badge variant="outline">{purchaseOrderUpdates.length}</Badge>
              )}
            </div>
            {purchaseOrderUpdates.length > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => clearUpdatesByType('purchaseOrder')}
                className="text-muted-foreground hover:text-foreground"
              >
                <Trash2 className="h-3 w-3" />
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {purchaseOrderUpdates.length === 0 ? (
            <p className="text-muted-foreground text-sm">발주 요청이 없습니다.</p>
          ) : (
            <div className="space-y-3">
              {purchaseOrderUpdates.map((update, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <Badge variant="destructive">발주</Badge>
                    <div>
                      <p className="font-medium">{update.branch_name}</p>
                      <p className="text-sm text-muted-foreground">
                        {update.user_name} • {formatTime(update.timestamp)}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-orange-600">
                      {update.total_amount.toLocaleString()}원
                    </p>
                    <p className="text-xs text-muted-foreground">
                      주문번호: {update.order_id}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

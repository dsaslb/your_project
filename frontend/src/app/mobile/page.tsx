'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { apiClient } from '@/lib/api-client';
import { 
  Clock, 
  User, 
  ShoppingCart, 
  Package, 
  Bell, 
  Calendar,
  TrendingUp,
  CheckCircle,
  XCircle
} from 'lucide-react';

interface MobileDashboard {
  role: string;
  stats?: any;
  today_schedule?: any;
  branch_id?: number;
}

interface Order {
  id: number;
  customer_name: string;
  items: string;
  total_amount: number;
  status: string;
  created_at: string;
}

interface Attendance {
  date: string;
  check_in_time: string | null;
  check_out_time: string | null;
  work_hours: number | null;
  status: string;
}

const MobilePage: React.FC = () => {
  const [dashboard, setDashboard] = useState<MobileDashboard | null>(null);
  const [orders, setOrders] = useState<Order[]>([]);
  const [attendance, setAttendance] = useState<Attendance[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loginData, setLoginData] = useState({ username: '', password: '' });

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiClient.post('/api/mobile/auth/login', loginData);
      const { token, user: userData } = response.data;
      
      // 로컬 스토리지에 토큰 저장
      localStorage.setItem('mobile_token', token);
      localStorage.setItem('mobile_user', JSON.stringify(userData));
      
    } catch (err: any) {
      setError(err.response?.data?.error || '로그인에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const fetchDashboard = async () => {
    try {
      const response = await apiClient.get('/api/mobile/dashboard');
      setDashboard(response.data);
    } catch (err) {
      console.error('Dashboard fetch error:', err);
    }
  };

  const fetchOrders = async () => {
    try {
      const response = await apiClient.get('/api/mobile/orders?per_page=10');
      setOrders(response.data.orders);
    } catch (err) {
      console.error('Orders fetch error:', err);
    }
  };

  const fetchAttendance = async () => {
    try {
      const response = await apiClient.get('/api/mobile/attendance/history?per_page=7');
      setAttendance(response.data.attendances);
    } catch (err) {
      console.error('Attendance fetch error:', err);
    }
  };

  const handleCheckIn = async () => {
    try {
      await apiClient.post('/api/mobile/attendance/check-in');
      fetchAttendance();
    } catch (err: any) {
      setError(err.response?.data?.error || '출근 기록에 실패했습니다.');
    }
  };

  const handleCheckOut = async () => {
    try {
      await apiClient.post('/api/mobile/attendance/check-out');
      fetchAttendance();
    } catch (err: any) {
      setError(err.response?.data?.error || '퇴근 기록에 실패했습니다.');
    }
  };

  const updateOrderStatus = async (orderId: number, status: string) => {
    try {
      await apiClient.put(`/api/mobile/orders/${orderId}/status`, { status });
      fetchOrders();
    } catch (err: any) {
      setError(err.response?.data?.error || '주문 상태 업데이트에 실패했습니다.');
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW'
    }).format(amount);
  };

  const formatTime = (timeString: string) => {
    return new Date(timeString).toLocaleTimeString('ko-KR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-500';
      case 'confirmed': return 'bg-blue-500';
      case 'completed': return 'bg-green-500';
      case 'cancelled': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 헤더 */}
      <div className="bg-white shadow-sm border-b">
        <div className="px-4 py-3 flex items-center justify-between">
          <div>
            <h1 className="text-lg font-semibold">레스토랑 관리</h1>
            // <p className="text-sm text-gray-600">user 정보 표시(임시 비활성화)</p>
          </div>
          // 로그아웃 버튼(임시 비활성화)
        </div>
      </div>

      <div className="p-4 space-y-4">
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* 대시보드 카드 */}
        {dashboard && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                대시보드
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                {dashboard.stats && (
                  <>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">
                        {dashboard.stats.total_orders || dashboard.stats.branch_orders || 0}
                      </div>
                      <div className="text-sm text-gray-600">총 주문</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {dashboard.stats.today_orders || dashboard.stats.today_branch_orders || 0}
                      </div>
                      <div className="text-sm text-gray-600">오늘 주문</div>
                    </div>
                  </>
                )}
                {dashboard.today_schedule && (
                  <div className="col-span-2">
                    <div className="text-center">
                      <div className="text-lg font-semibold">오늘 근무</div>
                      <div className="text-sm text-gray-600">
                        {dashboard.today_schedule.start_time && 
                         formatTime(dashboard.today_schedule.start_time)} - 
                        {dashboard.today_schedule.end_time && 
                         formatTime(dashboard.today_schedule.end_time)}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* 출근 관리 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              출근 관리
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-2">
              <Button onClick={handleCheckIn} className="flex-1">
                출근 체크인
              </Button>
              <Button onClick={handleCheckOut} variant="outline" className="flex-1">
                퇴근 체크아웃
              </Button>
            </div>
            
            {attendance.length > 0 && (
              <div className="mt-4">
                <h4 className="font-medium mb-2">최근 출근 기록</h4>
                <div className="space-y-2">
                  {attendance.slice(0, 3).map((record, index) => (
                    <div key={index} className="flex items-center justify-between text-sm">
                      <span>{new Date(record.date).toLocaleDateString('ko-KR')}</span>
                      <div className="flex items-center gap-2">
                        {record.check_in_time && (
                          <Badge variant="outline" className="text-xs">
                            {formatTime(record.check_in_time)}
                          </Badge>
                        )}
                        {record.check_out_time && (
                          <Badge variant="outline" className="text-xs">
                            {formatTime(record.check_out_time)}
                          </Badge>
                        )}
                        <Badge className={record.status === 'present' ? 'bg-green-500' : 'bg-red-500'}>
                          {record.status === 'present' ? '출근' : '결근'}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* 주문 관리 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ShoppingCart className="h-5 w-5" />
              주문 관리
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {orders.map((order) => (
                <div key={order.id} className="border rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium">{order.customer_name}</span>
                    <Badge className={getStatusColor(order.status)}>
                      {order.status}
                    </Badge>
                  </div>
                  <div className="text-sm text-gray-600 mb-2">
                    {order.items}
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="font-semibold">{formatCurrency(order.total_amount)}</span>
                    <div className="flex gap-1">
                      {order.status === 'pending' && (
                        <>
                          <Button
                            size="sm"
                            onClick={() => updateOrderStatus(order.id, 'confirmed')}
                            className="h-6 px-2 text-xs"
                          >
                            확인
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => updateOrderStatus(order.id, 'cancelled')}
                            className="h-6 px-2 text-xs"
                          >
                            취소
                          </Button>
                        </>
                      )}
                      {order.status === 'confirmed' && (
                        <Button
                          size="sm"
                          onClick={() => updateOrderStatus(order.id, 'completed')}
                          className="h-6 px-2 text-xs"
                        >
                          완료
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* 빠른 액션 */}
        <div className="grid grid-cols-2 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="text-center">
                <Package className="h-8 w-8 mx-auto mb-2 text-blue-600" />
                <div className="font-medium">재고 확인</div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="text-center">
                <Bell className="h-8 w-8 mx-auto mb-2 text-orange-600" />
                <div className="font-medium">알림</div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default MobilePage; 
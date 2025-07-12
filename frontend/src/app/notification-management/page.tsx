'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { toast } from 'sonner';
import { 
  Bell, 
  Mail, 
  MessageSquare, 
  Smartphone, 
  Settings, 
  History, 
  BarChart3, 
  Plus,
  Edit,
  Trash2,
  TestTube,
  CheckCircle,
  XCircle,
  AlertTriangle
} from 'lucide-react';

interface NotificationChannel {
  id: number;
  name: string;
  type: string;
  enabled: boolean;
  priority: number;
  created_at: string;
  updated_at: string;
}

interface NotificationHistory {
  id: number;
  title: string;
  message: string;
  level: string;
  channel: string;
  recipient?: string;
  sent_at: string;
  success: boolean;
  error_message?: string;
}

interface NotificationStatistics {
  period: {
    start_date: string;
    end_date: string;
    days: number;
  };
  overall_stats: {
    total_sent: number;
    successful_sent: number;
    failed_sent: number;
    success_rate: number;
  };
  level_stats: Array<{
    level: string;
    count: number;
    success_count: number;
    success_rate: number;
  }>;
  channel_stats: Array<{
    channel: string;
    count: number;
    success_count: number;
    success_rate: number;
  }>;
  hourly_stats: Array<{
    hour: string;
    count: number;
  }>;
}

export default function NotificationManagementPage() {
  const [channels, setChannels] = useState<NotificationChannel[]>([]);
  const [history, setHistory] = useState<NotificationHistory[]>([]);
  const [statistics, setStatistics] = useState<NotificationStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  // 새 채널 생성 상태
  const [showCreateChannel, setShowCreateChannel] = useState(false);
  const [newChannel, setNewChannel] = useState({
    name: '',
    type: 'email',
    enabled: true,
    priority: 2,
    config: {}
  });

  // 테스트 알림 상태
  const [testNotification, setTestNotification] = useState({
    title: '',
    message: '',
    level: 'info',
    channel: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // 채널 목록 로드
      const channelsResponse = await fetch('/api/admin/notifications/channels');
      const channelsData = await channelsResponse.json();
      if (channelsData.status === 'success') {
        setChannels(channelsData.channels);
      }

      // 히스토리 로드
      const historyResponse = await fetch('/api/admin/notifications/history?per_page=20');
      const historyData = await historyResponse.json();
      if (historyData.status === 'success') {
        setHistory(historyData.history);
      }

      // 통계 로드
      const statsResponse = await fetch('/api/admin/notifications/statistics?days=7');
      const statsData = await statsResponse.json();
      if (statsData.status === 'success') {
        setStatistics(statsData);
      }

    } catch (error) {
      console.error('Failed to load notification data:', error);
      toast.error('데이터 로드에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const createChannel = async () => {
    try {
      const response = await fetch('/api/admin/notifications/channels', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newChannel),
      });

      const data = await response.json();
      if (data.status === 'success') {
        toast.success('채널이 생성되었습니다.');
        setShowCreateChannel(false);
        setNewChannel({ name: '', type: 'email', enabled: true, priority: 2, config: {} });
        loadData();
      } else {
        toast.error(data.message || '채널 생성에 실패했습니다.');
      }
    } catch (error) {
      console.error('Failed to create channel:', error);
      toast.error('채널 생성에 실패했습니다.');
    }
  };

  const testChannel = async (channelId: number) => {
    try {
      const response = await fetch(`/api/admin/notifications/channels/${channelId}/test`, {
        method: 'POST',
      });

      const data = await response.json();
      if (data.status === 'success' && data.success) {
        toast.success('채널 테스트가 성공했습니다.');
      } else {
        toast.error('채널 테스트에 실패했습니다.');
      }
    } catch (error) {
      console.error('Failed to test channel:', error);
      toast.error('채널 테스트에 실패했습니다.');
    }
  };

  const sendTestNotification = async () => {
    try {
      const response = await fetch('/api/admin/notifications/send', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(testNotification),
      });

      const data = await response.json();
      if (data.status === 'success') {
        toast.success('테스트 알림이 전송되었습니다.');
        setTestNotification({ title: '', message: '', level: 'info', channel: '' });
        loadData();
      } else {
        toast.error(data.message || '알림 전송에 실패했습니다.');
      }
    } catch (error) {
      console.error('Failed to send notification:', error);
      toast.error('알림 전송에 실패했습니다.');
    }
  };

  const getChannelIcon = (type: string) => {
    switch (type) {
      case 'email': return <Mail className="h-4 w-4" />;
      case 'slack': return <MessageSquare className="h-4 w-4" />;
      case 'sms': return <Smartphone className="h-4 w-4" />;
      default: return <Bell className="h-4 w-4" />;
    }
  };

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'critical': return 'bg-red-100 text-red-800';
      case 'warning': return 'bg-yellow-100 text-yellow-800';
      case 'info': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getLevelIcon = (level: string) => {
    switch (level) {
      case 'critical': return <XCircle className="h-4 w-4" />;
      case 'warning': return <AlertTriangle className="h-4 w-4" />;
      case 'info': return <CheckCircle className="h-4 w-4" />;
      default: return <Bell className="h-4 w-4" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">알림 관리</h1>
        <Button onClick={() => setShowCreateChannel(true)}>
          <Plus className="h-4 w-4 mr-2" />
          새 채널 추가
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">개요</TabsTrigger>
          <TabsTrigger value="channels">채널 관리</TabsTrigger>
          <TabsTrigger value="history">히스토리</TabsTrigger>
          <TabsTrigger value="test">테스트</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* 통계 카드 */}
          {statistics && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">총 전송</CardTitle>
                  <Bell className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{statistics.overall_stats.total_sent}</div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">성공률</CardTitle>
                  <CheckCircle className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{statistics.overall_stats.success_rate.toFixed(1)}%</div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">성공</CardTitle>
                  <CheckCircle className="h-4 w-4 text-green-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-green-600">{statistics.overall_stats.successful_sent}</div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">실패</CardTitle>
                  <XCircle className="h-4 w-4 text-red-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-red-600">{statistics.overall_stats.failed_sent}</div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* 레벨별 통계 */}
          {statistics && (
            <Card>
              <CardHeader>
                <CardTitle>레벨별 통계</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {statistics.level_stats.map((stat) => (
                    <div key={stat.level} className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        {getLevelIcon(stat.level)}
                        <span className="font-medium">{stat.level.toUpperCase()}</span>
                      </div>
                      <div className="flex items-center space-x-4">
                        <span>{stat.count}개</span>
                        <Badge variant="outline">{stat.success_rate.toFixed(1)}% 성공</Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* 채널별 통계 */}
          {statistics && (
            <Card>
              <CardHeader>
                <CardTitle>채널별 통계</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {statistics.channel_stats.map((stat) => (
                    <div key={stat.channel} className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        {getChannelIcon(stat.channel)}
                        <span className="font-medium">{stat.channel}</span>
                      </div>
                      <div className="flex items-center space-x-4">
                        <span>{stat.count}개</span>
                        <Badge variant="outline">{stat.success_rate.toFixed(1)}% 성공</Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="channels" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>알림 채널</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {channels.map((channel) => (
                  <div key={channel.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      {getChannelIcon(channel.type)}
                      <div>
                        <h3 className="font-medium">{channel.name}</h3>
                        <p className="text-sm text-muted-foreground">{channel.type}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant={channel.enabled ? "default" : "secondary"}>
                        {channel.enabled ? '활성' : '비활성'}
                      </Badge>
                      <Badge variant="outline">우선순위 {channel.priority}</Badge>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => testChannel(channel.id)}
                      >
                        <TestTube className="h-4 w-4" />
                      </Button>
                      <Button size="sm" variant="outline">
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button size="sm" variant="outline" className="text-red-600">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="history" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>알림 히스토리</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {history.map((item) => (
                  <div key={item.id} className="p-4 border rounded-lg">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          {getLevelIcon(item.level)}
                          <h3 className="font-medium">{item.title}</h3>
                          <Badge className={getLevelColor(item.level)}>
                            {item.level.toUpperCase()}
                          </Badge>
                          <Badge variant="outline">{item.channel}</Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mb-2">{item.message}</p>
                        <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                          <span>{new Date(item.sent_at).toLocaleString()}</span>
                          {item.recipient && <span>수신자: {item.recipient}</span>}
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        {item.success ? (
                          <CheckCircle className="h-4 w-4 text-green-600" />
                        ) : (
                          <XCircle className="h-4 w-4 text-red-600" />
                        )}
                      </div>
                    </div>
                    {item.error_message && (
                      <Alert className="mt-2">
                        <AlertDescription className="text-red-600">
                          {item.error_message}
                        </AlertDescription>
                      </Alert>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="test" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>테스트 알림 전송</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="title">제목</Label>
                  <Input
                    id="title"
                    value={testNotification.title}
                    onChange={(e) => setTestNotification({ ...testNotification, title: e.target.value })}
                    placeholder="알림 제목을 입력하세요"
                  />
                </div>

                <div>
                  <Label htmlFor="message">메시지</Label>
                  <Textarea
                    id="message"
                    value={testNotification.message}
                    onChange={(e) => setTestNotification({ ...testNotification, message: e.target.value })}
                    placeholder="알림 메시지를 입력하세요"
                    rows={3}
                  />
                </div>

                <div>
                  <Label htmlFor="level">레벨</Label>
                  <Select
                    value={testNotification.level}
                    onValueChange={(value) => setTestNotification({ ...testNotification, level: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="info">정보</SelectItem>
                      <SelectItem value="warning">경고</SelectItem>
                      <SelectItem value="critical">중요</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="channel">채널</Label>
                  <Select
                    value={testNotification.channel}
                    onValueChange={(value) => setTestNotification({ ...testNotification, channel: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="채널을 선택하세요" />
                    </SelectTrigger>
                    <SelectContent>
                      {channels.map((channel) => (
                        <SelectItem key={channel.id} value={channel.name}>
                          {channel.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <Button onClick={sendTestNotification} className="w-full">
                  테스트 알림 전송
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* 새 채널 생성 모달 */}
      {showCreateChannel && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">새 채널 추가</h2>
            <div className="space-y-4">
              <div>
                <Label htmlFor="channel-name">채널 이름</Label>
                <Input
                  id="channel-name"
                  value={newChannel.name}
                  onChange={(e) => setNewChannel({ ...newChannel, name: e.target.value })}
                  placeholder="채널 이름을 입력하세요"
                />
              </div>

              <div>
                <Label htmlFor="channel-type">채널 타입</Label>
                <Select
                  value={newChannel.type}
                  onValueChange={(value) => setNewChannel({ ...newChannel, type: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="email">이메일</SelectItem>
                    <SelectItem value="slack">Slack</SelectItem>
                    <SelectItem value="discord">Discord</SelectItem>
                    <SelectItem value="sms">SMS</SelectItem>
                    <SelectItem value="webhook">Webhook</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="channel-priority">우선순위</Label>
                <Select
                  value={newChannel.priority.toString()}
                  onValueChange={(value) => setNewChannel({ ...newChannel, priority: parseInt(value) })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">높음</SelectItem>
                    <SelectItem value="2">중간</SelectItem>
                    <SelectItem value="3">낮음</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  id="channel-enabled"
                  checked={newChannel.enabled}
                  onCheckedChange={(checked) => setNewChannel({ ...newChannel, enabled: checked })}
                />
                <Label htmlFor="channel-enabled">활성화</Label>
              </div>

              <div className="flex space-x-2">
                <Button onClick={createChannel} className="flex-1">
                  생성
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setShowCreateChannel(false)}
                  className="flex-1"
                >
                  취소
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 
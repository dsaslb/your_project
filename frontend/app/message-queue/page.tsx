'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Plus, Trash2, RefreshCw, Send, Inbox, CheckCircle, AlertTriangle } from 'lucide-react';
import { ApiClient } from '@/lib/api-client';
import { useLoadingState } from '@/hooks/useLoadingState';
import { useErrorHandler } from '@/hooks/useErrorHandler';

const apiClient = new ApiClient();

interface Queue {
  queue_id: string;
  name: string;
  type: string;
  max_size: number;
  current_size: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface Message {
  message_id: string;
  topic: string;
  payload: any;
  priority: string;
  status: string;
  created_at: string;
}

interface QueueStats {
  total_queues: number;
  active_queues: number;
  total_messages: number;
  pending_messages: number;
  processing_messages: number;
  completed_messages: number;
  failed_messages: number;
  total_subscriptions: number;
  active_subscriptions: number;
  queue_stats: Array<{
    queue_id: string;
    name: string;
    type: string;
    current_size: number;
    max_size: number;
    utilization: number;
    pending_count: number;
    processing_count: number;
    completed_count: number;
    failed_count: number;
  }>;
}

export default function MessageQueuePage() {
  const [queues, setQueues] = useState<Queue[]>([]);
  const [stats, setStats] = useState<QueueStats | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [selectedQueue, setSelectedQueue] = useState<Queue | null>(null);
  const [isCreateQueueOpen, setIsCreateQueueOpen] = useState(false);
  const [isPublishOpen, setIsPublishOpen] = useState(false);
  const [newQueue, setNewQueue] = useState({ name: '', queue_type: 'standard', max_size: 1000 });
  const [publishForm, setPublishForm] = useState({ topic: '', payload: '', priority: 'normal' });
  const { loading, setLoading } = useLoadingState();
  const { error, handleError, clearError } = useErrorHandler();
    useEffect(() => {
    loadQueues();
    loadStats();
  }, []);

  const loadQueues = async () => {
    try {
      setLoading(true);
      clearError();
      const res = await apiClient.get('/api/message-queue/queues');
      setQueues(res.data);
    } catch (err) {
      handleError(err, '큐 목록 로드 실패');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const res = await apiClient.get('/api/message-queue/stats');
      setStats(res.data);
    } catch (err) {
      handleError(err, '통계 로드 실패');
    }
  };

  const createQueue = async () => {
    try {
      setLoading(true);
      clearError();
      await apiClient.post('/api/message-queue/queues', newQueue);
      setIsCreateQueueOpen(false);
      setNewQueue({ name: '', queue_type: 'standard', max_size: 1000 });
      await loadQueues();
      await loadStats();
    } catch (err) {
      handleError(err, '큐 생성 실패');
    } finally {
      setLoading(false);
    }
  };

  const deleteQueue = async (queue_id: string) => {
    if (!confirm('정말로 이 큐를 삭제하시겠습니까?')) return;
    try {
      setLoading(true);
      clearError();
      await apiClient.delete(`/api/message-queue/queues/${queue_id}`);
      await loadQueues();
      await loadStats();
    } catch (err) {
      handleError(err, '큐 삭제 실패');
    } finally {
      setLoading(false);
    }
  };

  const publishMessage = async () => {
    if (!selectedQueue) return;
    try {
      setLoading(true);
      clearError();
      await apiClient.post('/api/message-queue/messages', {
        queue_id: selectedQueue.queue_id,
        topic: publishForm.topic,
        payload: publishForm.payload,
        priority: publishForm.priority
      });
      setIsPublishOpen(false);
      setPublishForm({ topic: '', payload: '', priority: 'normal' });
      await loadStats();
    } catch (err) {
      handleError(err, '메시지 발행 실패');
    } finally {
      setLoading(false);
    }
  };

  const consumeMessage = async (queue_id: string) => {
    try {
      setLoading(true);
      clearError();
      const res = await apiClient.post('/api/message-queue/messages/consume', { queue_id });
      if (res.status === 'success') {
        setMessages([res.data]);
      } else {
        setMessages([]);
      }
    } catch (err) {
      handleError(err, '메시지 소비 실패');
    } finally {
      setLoading(false);
    }
  };

  const completeMessage = async (message_id: string) => {
    try {
      setLoading(true);
      clearError();
      await apiClient.post(`/api/message-queue/messages/${message_id}/complete`, { success: true });
      setMessages([]);
      await loadStats();
    } catch (err) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">메시지 큐 관리</h1>
          <p className="text-gray-600 mt-2">비동기 작업, 이벤트, Pub/Sub 큐를 관리합니다</p>
        </div>
        <Button onClick={() => { loadQueues(); loadStats(); }} disabled={loading}>
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          새로고침
        </Button>
      </div>
      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 큐</CardTitle>
            <Inbox className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_queues || 0}</div>
            <p className="text-xs text-muted-foreground">활성: {stats?.active_queues || 0}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 메시지</CardTitle>
            <Send className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_messages || 0}</div>
            <p className="text-xs text-muted-foreground">대기: {stats?.pending_messages || 0}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">구독</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_subscriptions || 0}</div>
            <p className="text-xs text-muted-foreground">활성: {stats?.active_subscriptions || 0}</p>
          </CardContent>
        </Card>
      </div>
      <Tabs defaultValue="queues" className="space-y-6">
        <TabsList>
          <TabsTrigger value="queues">큐 관리</TabsTrigger>
          <TabsTrigger value="stats">통계</TabsTrigger>
        </TabsList>
        <TabsContent value="queues" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>큐 목록</CardTitle>
                  <CardDescription>메시지 큐를 생성, 삭제, 관리합니다</CardDescription>
                </div>
                <Dialog open={isCreateQueueOpen} onOpenChange={setIsCreateQueueOpen}>
                  <DialogTrigger asChild>
                    <Button>
                      <Plus className="w-4 h-4 mr-2" />
                      새 큐
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-[400px]">
                    <DialogHeader>
                      <DialogTitle>새 큐 생성</DialogTitle>
                      <DialogDescription>새로운 메시지 큐를 생성합니다</DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                      <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="queue-name" className="text-right">큐 이름</Label>
                        <Input
                          id="queue-name"
                          value={newQueue.name}
                          onChange={(e) => setNewQueue({ ...newQueue, name: e.target.value })}
                          className="col-span-3"
                        />
                      </div>
                      <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="queue-type" className="text-right">타입</Label>
                        <Input
                          id="queue-type"
                          value={newQueue.queue_type}
                          onChange={(e) => setNewQueue({ ...newQueue, queue_type: e.target.value })}
                          className="col-span-3"
                        />
                      </div>
                      <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="queue-size" className="text-right">최대 크기</Label>
                        <Input
                          id="queue-size"
                          type="number"
                          value={newQueue.max_size}
                          onChange={(e) => setNewQueue({ ...newQueue, max_size: parseInt(e.target.value) })}
                          className="col-span-3"
                        />
                      </div>
                    </div>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setIsCreateQueueOpen(false)}>
                        취소
                      </Button>
                      <Button onClick={createQueue} disabled={loading}>
                        생성
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>이름</TableHead>
                    <TableHead>타입</TableHead>
                    <TableHead>크기</TableHead>
                    <TableHead>상태</TableHead>
                    <TableHead>작업</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {queues.map((queue) => (
                    <TableRow key={queue.queue_id}>
                      <TableCell>{queue.name}</TableCell>
                      <TableCell>{queue.type}</TableCell>
                      <TableCell>{queue.current_size} / {queue.max_size}</TableCell>
                      <TableCell>
                        {queue.is_active ? <Badge variant="default">활성</Badge> : <Badge variant="secondary">비활성</Badge>}
                      </TableCell>
                      <TableCell>
                        <div className="flex space-x-2">
                          <Button size="sm" variant="outline" onClick={() => { setSelectedQueue(queue); setIsPublishOpen(true); }}>
                            <Send className="h-4 w-4" />
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => consumeMessage(queue.queue_id)}>
                            <Inbox className="h-4 w-4" />
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => deleteQueue(queue.queue_id)}>
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
          <Dialog open={isPublishOpen} onOpenChange={setIsPublishOpen}>
            <DialogContent className="sm:max-w-[400px]">
              <DialogHeader>
                <DialogTitle>메시지 발행</DialogTitle>
                <DialogDescription>선택한 큐에 메시지를 발행합니다</DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="topic" className="text-right">토픽</Label>
                  <Input
                    id="topic"
                    value={publishForm.topic}
                    onChange={(e) => setPublishForm({ ...publishForm, topic: e.target.value })}
                    className="col-span-3"
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="payload" className="text-right">페이로드</Label>
                  <Input
                    id="payload"
                    value={publishForm.payload}
                    onChange={(e) => setPublishForm({ ...publishForm, payload: e.target.value })}
                    className="col-span-3"
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="priority" className="text-right">우선순위</Label>
                  <Input
                    id="priority"
                    value={publishForm.priority}
                    onChange={(e) => setPublishForm({ ...publishForm, priority: e.target.value })}
                    className="col-span-3"
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsPublishOpen(false)}>
                  취소
                </Button>
                <Button onClick={publishMessage} disabled={loading}>
                  발행
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
          {/* 메시지 소비 결과 */}
          {messages.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>소비된 메시지</CardTitle>
                <CardDescription>큐에서 소비된 메시지 정보</CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>메시지ID</TableHead>
                      <TableHead>토픽</TableHead>
                      <TableHead>페이로드</TableHead>
                      <TableHead>우선순위</TableHead>
                      <TableHead>상태</TableHead>
                      <TableHead>작업</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {messages.map((msg) => (
                      <TableRow key={msg.message_id}>
                        <TableCell>{msg.message_id}</TableCell>
                        <TableCell>{msg.topic}</TableCell>
                        <TableCell>{msg.payload}</TableCell>
                        <TableCell>{msg.priority}</TableCell>
                        <TableCell>{msg.status}</TableCell>
                        <TableCell>
                          <Button size="sm" variant="outline" onClick={() => completeMessage(msg.message_id)}>
                            완료
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          )}
        </TabsContent>
        <TabsContent value="stats" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>큐별 통계</CardTitle>
              <CardDescription>각 큐의 상태 및 메시지 통계</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>이름</TableHead>
                    <TableHead>타입</TableHead>
                    <TableHead>크기</TableHead>
                    <TableHead>대기</TableHead>
                    <TableHead>처리중</TableHead>
                    <TableHead>완료</TableHead>
                    <TableHead>실패</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {stats?.queue_stats.map((q) => (
                    <TableRow key={q.queue_id}>
                      <TableCell>{q.name}</TableCell>
                      <TableCell>{q.type}</TableCell>
                      <TableCell>{q.current_size} / {q.max_size}</TableCell>
                      <TableCell>{q.pending_count}</TableCell>
                      <TableCell>{q.processing_count}</TableCell>
                      <TableCell>{q.completed_count}</TableCell>
                      <TableCell>{q.failed_count}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
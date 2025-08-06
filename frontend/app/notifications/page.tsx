'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../src/components/ui/card';
import { Button } from '../../src/components/ui/button';
import { Input } from '../../src/components/ui/input';
import { Badge } from '../../src/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '../../src/components/ui/dialog';
import { Label } from '../../src/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../src/components/ui/select';
import { Textarea } from '../../src/components/ui/textarea';
import { Switch } from '../../src/components/ui/switch';
import { apiClient } from '../../src/lib/api-client';
import { useLoadingState } from '../../src/hooks/useLoadingState';
import { useErrorHandler } from '../../src/hooks/useErrorHandler';
import { toast } from 'sonner';
import { 
  Bell, 
  Plus, 
  Search, 
  Filter, 
  Edit, 
  Trash2, 
  Eye, 
  Check,
  X,
  Clock,
  AlertTriangle,
  Info,
  CheckCircle,
  Mail,
  Smartphone,
  Settings,
  Zap,
  Volume2,
  VolumeX,
  Star,
  Archive,
  RefreshCw,
  Send
} from 'lucide-react';

interface Notification {
  id: number;
  title: string;
  message: string;
  type: 'info' | 'warning' | 'error' | 'success' | 'urgent';
  category: 'system' | 'sales' | 'inventory' | 'customer' | 'employee' | 'quality' | 'marketing' | 'general';
  priority: 'low' | 'medium' | 'high' | 'critical';
  status: 'unread' | 'read' | 'archived';
  recipient_id: number;
  recipient_name: string;
  sender_id?: number;
  sender_name?: string;
  created_at: string;
  read_at?: string;
  scheduled_at?: string;
  sent_at?: string;
  delivery_method: 'in_app' | 'email' | 'sms' | 'push' | 'all';
  is_scheduled: boolean;
  is_sent: boolean;
}

interface NotificationTemplate {
  id: number;
  name: string;
  title: string;
  message: string;
  type: 'info' | 'warning' | 'error' | 'success' | 'urgent';
  category: 'system' | 'sales' | 'inventory' | 'customer' | 'employee' | 'quality' | 'marketing' | 'general';
  priority: 'low' | 'medium' | 'high' | 'critical';
  delivery_method: 'in_app' | 'email' | 'sms' | 'push' | 'all';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface NotificationFormData {
  title: string;
  message: string;
  type: 'info' | 'warning' | 'error' | 'success' | 'urgent';
  category: 'system' | 'sales' | 'inventory' | 'customer' | 'employee' | 'quality' | 'marketing' | 'general';
  priority: 'low' | 'medium' | 'high' | 'critical';
  recipient_id: number;
  delivery_method: 'in_app' | 'email' | 'sms' | 'push' | 'all';
  scheduled_at?: string;
}

interface NotificationSettings {
  id: number;
  user_id: number;
  email_notifications: boolean;
  sms_notifications: boolean;
  push_notifications: boolean;
  in_app_notifications: boolean;
  quiet_hours_start: string;
  quiet_hours_end: string;
  categories: {
    system: boolean;
    sales: boolean;
    inventory: boolean;
    customer: boolean;
    employee: boolean;
    quality: boolean;
    marketing: boolean;
    general: boolean;
  };
  priorities: {
    low: boolean;
    medium: boolean;
    high: boolean;
    critical: boolean;
  };
}

export default function Notifications() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [templates, setTemplates] = useState<NotificationTemplate[]>([]);
  const [settings, setSettings] = useState<NotificationSettings | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isSettingsDialogOpen, setIsSettingsDialogOpen] = useState(false);
  const [isTemplateDialogOpen, setIsTemplateDialogOpen] = useState(false);
  const [editingNotification, setEditingNotification] = useState<Notification | null>(null);
  const [viewingNotification, setViewingNotification] = useState<Notification | null>(null);
  
  const [formData, setFormData] = useState<NotificationFormData>({
    title: '',
    message: '',
    type: 'info',
    category: 'general',
    priority: 'medium',
    recipient_id: 0,
    delivery_method: 'in_app',
    scheduled_at: '',
  });

  const { isLoading, setLoading } = useLoadingState();
  const { handleError } = useErrorHandler();

  // 알림 목록 조회
  const fetchNotifications = async () => {
    try {
      const response = await apiClient.get('/api/notifications');
      if (response.success && response.data) {
        setNotifications(response.data);
      }
    } catch (error) {
      handleError(error as Error);
    }
  };

  // 알림 템플릿 조회
  const fetchTemplates = async () => {
    try {
      const response = await apiClient.get('/api/notification-templates');
      if (response.success && response.data) {
        setTemplates(response.data);
      }
    } catch (error) {
      handleError(error as Error);
    }
  };

  // 알림 설정 조회
  const fetchSettings = async () => {
    try {
      const response = await apiClient.get('/api/notification-settings');
      if (response.success && response.data) {
        setSettings(response.data);
      }
    } catch (error) {
      handleError(error as Error);
    }
  };

  // 초기 데이터 로드
  useEffect(() => {
    fetchNotifications();
    fetchTemplates();
    fetchSettings();
  }, []);

  // 폼 초기화
  const resetForm = () => {
    setFormData({
      title: '',
      message: '',
      type: 'info',
      category: 'general',
      priority: 'medium',
      recipient_id: 0,
      delivery_method: 'in_app',
      scheduled_at: '',
    });
  };

  // 알림 생성/수정 제출
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.title || !formData.message) {
      toast.error('필수 정보를 입력해주세요.');
      return;
    }

    try {
      setLoading(true);
      
      if (editingNotification) {
        const response = await apiClient.put(`/api/notifications/${editingNotification.id}`, formData);
        if (response.success) {
          toast.success('알림이 성공적으로 수정되었습니다.');
          setIsCreateDialogOpen(false);
          setEditingNotification(null);
          resetForm();
          fetchNotifications();
        }
      } else {
        const response = await apiClient.post('/api/notifications', formData);
        if (response.success) {
          toast.success('알림이 성공적으로 생성되었습니다.');
          setIsCreateDialogOpen(false);
          resetForm();
          fetchNotifications();
        }
      }
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 알림 삭제
  const handleDelete = async (notification: Notification) => {
    if (!confirm(`정말로 ${notification.title} 알림을 삭제하시겠습니까?`)) {
      return;
    }

    try {
      setLoading(true);
      const response = await apiClient.delete(`/api/notifications/${notification.id}`);
      if (response.success) {
        toast.success('알림이 성공적으로 삭제되었습니다.');
        fetchNotifications();
      }
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 알림 읽음 처리
  const handleMarkAsRead = async (notification: Notification) => {
    try {
      setLoading(true);
      const response = await apiClient.put(`/api/notifications/${notification.id}/read`);
      if (response.success) {
        toast.success('알림을 읽음 처리했습니다.');
        fetchNotifications();
      }
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 알림 보관 처리
  const handleArchive = async (notification: Notification) => {
    try {
      setLoading(true);
      const response = await apiClient.put(`/api/notifications/${notification.id}/archive`);
      if (response.success) {
        toast.success('알림을 보관했습니다.');
        fetchNotifications();
      }
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 알림 즉시 전송
  const handleSendNow = async (notification: Notification) => {
    try {
      setLoading(true);
      const response = await apiClient.post(`/api/notifications/${notification.id}/send`);
      if (response.success) {
        toast.success('알림이 즉시 전송되었습니다.');
        fetchNotifications();
      }
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 알림 수정 모드 시작
  const handleEdit = (notification: Notification) => {
    setEditingNotification(notification);
    setFormData({
      title: notification.title,
      message: notification.message,
      type: notification.type,
      category: notification.category,
      priority: notification.priority,
      recipient_id: notification.recipient_id,
      delivery_method: notification.delivery_method,
      scheduled_at: notification.scheduled_at || '',
    });
    setIsCreateDialogOpen(true);
  };

  // 알림 상세 보기
  const handleView = (notification: Notification) => {
    setViewingNotification(notification);
  };

  // 새 알림 생성 모드 시작
  const handleCreate = () => {
    setEditingNotification(null);
    resetForm();
    setIsCreateDialogOpen(true);
  };

  // 템플릿에서 알림 생성
  const handleCreateFromTemplate = (template: NotificationTemplate) => {
    setFormData({
      title: template.title,
      message: template.message,
      type: template.type,
      category: template.category,
      priority: template.priority,
      recipient_id: 0,
      delivery_method: template.delivery_method,
      scheduled_at: '',
    });
    setIsCreateDialogOpen(true);
  };

  // 타입별 색상
  const getTypeColor = (type: string) => {
    switch (type) {
      case 'info': return 'bg-blue-500/20 text-blue-400 border border-blue-500/30';
      case 'warning': return 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30';
      case 'error': return 'bg-red-500/20 text-red-400 border border-red-500/30';
      case 'success': return 'bg-green-500/20 text-green-400 border border-green-500/30';
      case 'urgent': return 'bg-purple-500/20 text-purple-400 border border-purple-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border border-gray-500/30';
    }
  };

  // 우선순위별 색상
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'low': return 'bg-green-500/20 text-green-400 border border-green-500/30';
      case 'medium': return 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30';
      case 'high': return 'bg-orange-500/20 text-orange-400 border border-orange-500/30';
      case 'critical': return 'bg-red-500/20 text-red-400 border border-red-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border border-gray-500/30';
    }
  };

  // 상태별 색상
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'unread': return 'bg-blue-500/20 text-blue-400 border border-blue-500/30';
      case 'read': return 'bg-gray-500/20 text-gray-400 border border-gray-500/30';
      case 'archived': return 'bg-purple-500/20 text-purple-400 border border-purple-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border border-gray-500/30';
    }
  };

  // 필터링된 알림 목록
  const filteredNotifications = notifications.filter(notification => {
    const matchesSearch = searchTerm === '' || 
      notification.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      notification.message.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesType = selectedType === 'all' || notification.type === selectedType;
    const matchesCategory = selectedCategory === 'all' || notification.category === selectedCategory;
    const matchesStatus = selectedStatus === 'all' || notification.status === selectedStatus;
    
    return matchesSearch && matchesType && matchesCategory && matchesStatus;
  });

  // 통계 계산
  const totalNotifications = notifications.length;
  const unreadNotifications = notifications.filter(n => n.status === 'unread').length;
  const urgentNotifications = notifications.filter(n => n.priority === 'critical').length;
  const scheduledNotifications = notifications.filter(n => n.is_scheduled).length;

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Bell className="h-8 w-8 text-orange-600" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">알림 시스템</h1>
            <p className="text-gray-600">실시간 알림과 알림 관리를 통해 중요한 정보를 놓치지 마세요</p>
          </div>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" onClick={() => setIsSettingsDialogOpen(true)}>
            <Settings className="h-4 w-4 mr-2" />
            설정
          </Button>
          <Button onClick={handleCreate} className="bg-orange-600 hover:bg-orange-700">
            <Plus className="h-4 w-4 mr-2" />
            새 알림 생성
          </Button>
        </div>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <Bell className="h-8 w-8 text-orange-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">총 알림</p>
                <p className="text-2xl font-bold text-gray-900">{totalNotifications.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <AlertTriangle className="h-8 w-8 text-blue-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">읽지 않은 알림</p>
                <p className="text-2xl font-bold text-gray-900">{unreadNotifications.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <Zap className="h-8 w-8 text-red-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">긴급 알림</p>
                <p className="text-2xl font-bold text-gray-900">{urgentNotifications.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <Clock className="h-8 w-8 text-purple-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">예약된 알림</p>
                <p className="text-2xl font-bold text-gray-900">{scheduledNotifications.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 필터 및 검색 */}
      <Card>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="알림 제목, 내용 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            
            <Select value={selectedType} onValueChange={setSelectedType}>
              <SelectTrigger>
                <SelectValue placeholder="알림 타입" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">전체 타입</SelectItem>
                <SelectItem value="info">정보</SelectItem>
                <SelectItem value="warning">경고</SelectItem>
                <SelectItem value="error">오류</SelectItem>
                <SelectItem value="success">성공</SelectItem>
                <SelectItem value="urgent">긴급</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger>
                <SelectValue placeholder="카테고리" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">전체 카테고리</SelectItem>
                <SelectItem value="system">시스템</SelectItem>
                <SelectItem value="sales">매출</SelectItem>
                <SelectItem value="inventory">재고</SelectItem>
                <SelectItem value="customer">고객</SelectItem>
                <SelectItem value="employee">직원</SelectItem>
                <SelectItem value="quality">품질</SelectItem>
                <SelectItem value="marketing">마케팅</SelectItem>
                <SelectItem value="general">일반</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={selectedStatus} onValueChange={setSelectedStatus}>
              <SelectTrigger>
                <SelectValue placeholder="상태" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">전체 상태</SelectItem>
                <SelectItem value="unread">읽지 않음</SelectItem>
                <SelectItem value="read">읽음</SelectItem>
                <SelectItem value="archived">보관됨</SelectItem>
              </SelectContent>
            </Select>
            
            <Button variant="outline" onClick={() => {
              setSearchTerm('');
              setSelectedType('all');
              setSelectedCategory('all');
              setSelectedStatus('all');
            }}>
              <Filter className="h-4 w-4 mr-2" />
              필터 초기화
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 알림 목록 */}
      <Card>
        <CardHeader>
          <CardTitle>알림 목록</CardTitle>
          <CardDescription>
            총 {filteredNotifications.length}개의 알림이 있습니다
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredNotifications.map((notification) => (
              <div key={notification.id} className={`border rounded-lg p-4 transition-colors ${
                notification.status === 'unread' ? 'bg-blue-50 border-blue-200' : 'hover:bg-gray-50'
              }`}>
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">{notification.title}</h3>
                      <Badge className={getTypeColor(notification.type)}>
                        {notification.type === 'info' && '정보'}
                        {notification.type === 'warning' && '경고'}
                        {notification.type === 'error' && '오류'}
                        {notification.type === 'success' && '성공'}
                        {notification.type === 'urgent' && '긴급'}
                      </Badge>
                      <Badge className={getPriorityColor(notification.priority)}>
                        {notification.priority === 'low' && '낮음'}
                        {notification.priority === 'medium' && '보통'}
                        {notification.priority === 'high' && '높음'}
                        {notification.priority === 'critical' && '긴급'}
                      </Badge>
                      <Badge className={getStatusColor(notification.status)}>
                        {notification.status === 'unread' && '읽지 않음'}
                        {notification.status === 'read' && '읽음'}
                        {notification.status === 'archived' && '보관됨'}
                      </Badge>
                    </div>
                    
                    <p className="text-sm text-gray-600 mb-2">{notification.message}</p>
                    
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm text-gray-500">
                      <div>
                        <span className="font-medium">카테고리:</span> {notification.category}
                      </div>
                      <div>
                        <span className="font-medium">수신자:</span> {notification.recipient_name}
                      </div>
                      <div>
                        <span className="font-medium">전송 방법:</span> {notification.delivery_method}
                      </div>
                      <div>
                        <span className="font-medium">생성일:</span> {new Date(notification.created_at).toLocaleDateString('ko-KR')}
                      </div>
                    </div>
                    
                    {notification.scheduled_at && (
                      <div className="mt-2 text-sm text-gray-500">
                        <span className="font-medium">예약 시간:</span> {new Date(notification.scheduled_at).toLocaleString('ko-KR')}
                      </div>
                    )}
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    {notification.status === 'unread' && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleMarkAsRead(notification)}
                      >
                        <Check className="h-4 w-4" />
                      </Button>
                    )}
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleView(notification)}
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEdit(notification)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    {!notification.is_sent && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleSendNow(notification)}
                      >
                        <Send className="h-4 w-4" />
                      </Button>
                    )}
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleArchive(notification)}
                    >
                      <Archive className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDelete(notification)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
            
            {filteredNotifications.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <Bell className="h-12 w-12 mx-auto mb-2" />
                <p>알림이 없습니다.</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* 알림 생성/수정 다이얼로그 */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              {editingNotification ? '알림 수정' : '새 알림 생성'}
            </DialogTitle>
            <DialogDescription>
              {editingNotification ? '알림 정보를 수정하세요.' : '새로운 알림을 생성하세요.'}
            </DialogDescription>
          </DialogHeader>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="title">알림 제목 *</Label>
              <Input
                id="title"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                required
              />
            </div>
            
            <div>
              <Label htmlFor="message">알림 내용 *</Label>
              <Textarea
                id="message"
                value={formData.message}
                onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                rows={3}
                required
              />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="type">알림 타입</Label>
                <Select value={formData.type} onValueChange={(value: any) => setFormData({ ...formData, type: value })}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="info">정보</SelectItem>
                    <SelectItem value="warning">경고</SelectItem>
                    <SelectItem value="error">오류</SelectItem>
                    <SelectItem value="success">성공</SelectItem>
                    <SelectItem value="urgent">긴급</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label htmlFor="category">카테고리</Label>
                <Select value={formData.category} onValueChange={(value: any) => setFormData({ ...formData, category: value })}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="system">시스템</SelectItem>
                    <SelectItem value="sales">매출</SelectItem>
                    <SelectItem value="inventory">재고</SelectItem>
                    <SelectItem value="customer">고객</SelectItem>
                    <SelectItem value="employee">직원</SelectItem>
                    <SelectItem value="quality">품질</SelectItem>
                    <SelectItem value="marketing">마케팅</SelectItem>
                    <SelectItem value="general">일반</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label htmlFor="priority">우선순위</Label>
                <Select value={formData.priority} onValueChange={(value: any) => setFormData({ ...formData, priority: value })}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">낮음</SelectItem>
                    <SelectItem value="medium">보통</SelectItem>
                    <SelectItem value="high">높음</SelectItem>
                    <SelectItem value="critical">긴급</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="delivery_method">전송 방법</Label>
                <Select value={formData.delivery_method} onValueChange={(value: any) => setFormData({ ...formData, delivery_method: value })}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="in_app">앱 내 알림</SelectItem>
                    <SelectItem value="email">이메일</SelectItem>
                    <SelectItem value="sms">SMS</SelectItem>
                    <SelectItem value="push">푸시 알림</SelectItem>
                    <SelectItem value="all">모든 방법</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label htmlFor="scheduled_at">예약 시간 (선택사항)</Label>
                <Input
                  id="scheduled_at"
                  type="datetime-local"
                  value={formData.scheduled_at}
                  onChange={(e) => setFormData({ ...formData, scheduled_at: e.target.value })}
                />
              </div>
            </div>
            
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                취소
              </Button>
              <Button type="submit" disabled={isLoading}>
                {isLoading ? '처리 중...' : (editingNotification ? '수정' : '생성')}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* 알림 상세 보기 다이얼로그 */}
      <Dialog open={!!viewingNotification} onOpenChange={() => setViewingNotification(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>알림 상세 정보</DialogTitle>
            <DialogDescription>
              {viewingNotification?.title} 알림의 상세 정보입니다.
            </DialogDescription>
          </DialogHeader>
          
          {viewingNotification && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm font-medium text-gray-600">알림 제목</Label>
                  <p className="text-lg font-semibold">{viewingNotification.title}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">알림 타입</Label>
                  <Badge className={getTypeColor(viewingNotification.type)}>
                    {viewingNotification.type === 'info' && '정보'}
                    {viewingNotification.type === 'warning' && '경고'}
                    {viewingNotification.type === 'error' && '오류'}
                    {viewingNotification.type === 'success' && '성공'}
                    {viewingNotification.type === 'urgent' && '긴급'}
                  </Badge>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">우선순위</Label>
                  <Badge className={getPriorityColor(viewingNotification.priority)}>
                    {viewingNotification.priority === 'low' && '낮음'}
                    {viewingNotification.priority === 'medium' && '보통'}
                    {viewingNotification.priority === 'high' && '높음'}
                    {viewingNotification.priority === 'critical' && '긴급'}
                  </Badge>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">상태</Label>
                  <Badge className={getStatusColor(viewingNotification.status)}>
                    {viewingNotification.status === 'unread' && '읽지 않음'}
                    {viewingNotification.status === 'read' && '읽음'}
                    {viewingNotification.status === 'archived' && '보관됨'}
                  </Badge>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">카테고리</Label>
                  <p className="text-lg">{viewingNotification.category}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">수신자</Label>
                  <p className="text-lg">{viewingNotification.recipient_name}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">전송 방법</Label>
                  <p className="text-lg">{viewingNotification.delivery_method}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-600">생성일</Label>
                  <p className="text-lg">{new Date(viewingNotification.created_at).toLocaleString('ko-KR')}</p>
                </div>
              </div>
              
              <div>
                <Label className="text-sm font-medium text-gray-600">알림 내용</Label>
                <p className="text-lg bg-gray-50 p-3 rounded-lg">{viewingNotification.message}</p>
              </div>
              
              {viewingNotification.scheduled_at && (
                <div>
                  <Label className="text-sm font-medium text-gray-600">예약 시간</Label>
                  <p className="text-lg">{new Date(viewingNotification.scheduled_at).toLocaleString('ko-KR')}</p>
                </div>
              )}
            </div>
          )}
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setViewingNotification(null)}>
              닫기
            </Button>
            {viewingNotification && (
              <Button onClick={() => {
                setViewingNotification(null);
                handleEdit(viewingNotification);
              }}>
                수정하기
              </Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
} 
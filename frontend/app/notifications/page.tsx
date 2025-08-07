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
      setLoading(true);
      // 임시로 샘플 데이터 사용
      const sampleNotifications: Notification[] = [
        {
          id: 1,
          title: '재고 부족 알림',
          message: '음료 카테고리의 재고가 부족합니다. 즉시 보충이 필요합니다.',
          type: 'warning',
          category: 'inventory',
          priority: 'high',
          status: 'unread',
          recipient_id: 1,
          recipient_name: '김관리자',
          sender_id: 1,
          sender_name: '시스템',
          created_at: '2024-01-15T10:30:00Z',
          delivery_method: 'in_app',
          is_scheduled: false,
          is_sent: true
        },
        {
          id: 2,
          title: '매출 목표 달성',
          message: '이번 달 매출 목표를 달성했습니다! 훌륭한 성과입니다.',
          type: 'success',
          category: 'sales',
          priority: 'medium',
          status: 'read',
          recipient_id: 1,
          recipient_name: '김관리자',
          sender_id: 1,
          sender_name: '시스템',
          created_at: '2024-01-15T09:00:00Z',
          read_at: '2024-01-15T09:15:00Z',
          delivery_method: 'in_app',
          is_scheduled: false,
          is_sent: true
        },
        {
          id: 3,
          title: '시스템 점검 예정',
          message: '오늘 밤 12시부터 2시간 동안 시스템 점검이 예정되어 있습니다.',
          type: 'info',
          category: 'system',
          priority: 'low',
          status: 'unread',
          recipient_id: 1,
          recipient_name: '김관리자',
          sender_id: 1,
          sender_name: '시스템',
          created_at: '2024-01-15T08:00:00Z',
          delivery_method: 'in_app',
          is_scheduled: false,
          is_sent: true
        },
        {
          id: 4,
          title: '고객 문의 긴급',
          message: 'VIP 고객으로부터 긴급 문의가 접수되었습니다. 즉시 확인해주세요.',
          type: 'urgent',
          category: 'customer',
          priority: 'critical',
          status: 'unread',
          recipient_id: 1,
          recipient_name: '김관리자',
          sender_id: 1,
          sender_name: '시스템',
          created_at: '2024-01-15T07:30:00Z',
          delivery_method: 'all',
          is_scheduled: false,
          is_sent: true
        }
      ];
      
      setNotifications(sampleNotifications);
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 알림 템플릿 조회
  const fetchTemplates = async () => {
    try {
      const sampleTemplates: NotificationTemplate[] = [
        {
          id: 1,
          name: '재고 부족 알림',
          title: '재고 부족 알림',
          message: '{category} 카테고리의 재고가 부족합니다. 즉시 보충이 필요합니다.',
          type: 'warning',
          category: 'inventory',
          priority: 'high',
          delivery_method: 'in_app',
          is_active: true,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        },
        {
          id: 2,
          name: '매출 목표 달성',
          title: '매출 목표 달성',
          message: '이번 달 매출 목표를 달성했습니다! 훌륭한 성과입니다.',
          type: 'success',
          category: 'sales',
          priority: 'medium',
          delivery_method: 'in_app',
          is_active: true,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        }
      ];
      setTemplates(sampleTemplates);
    } catch (error) {
      handleError(error as Error);
    }
  };

  // 알림 설정 조회
  const fetchSettings = async () => {
    try {
      const sampleSettings: NotificationSettings = {
        id: 1,
        user_id: 1,
        email_notifications: true,
        sms_notifications: false,
        push_notifications: true,
        in_app_notifications: true,
        quiet_hours_start: '22:00',
        quiet_hours_end: '08:00',
        categories: {
          system: true,
          sales: true,
          inventory: true,
          customer: true,
          employee: false,
          quality: true,
          marketing: false,
          general: true
        },
        priorities: {
          low: true,
          medium: true,
          high: true,
          critical: true
        }
      };
      setSettings(sampleSettings);
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
        // 알림 정보 수정
        const updatedNotification = {
          ...editingNotification,
          ...formData,
          updated_at: new Date().toISOString()
        };
        
        setNotifications(prev => prev.map(notification => 
          notification.id === editingNotification.id ? updatedNotification : notification
        ));
        
        toast.success('알림이 수정되었습니다.');
      } else {
        // 새 알림 생성
        const newNotification: Notification = {
          id: Date.now(),
          ...formData,
          status: 'unread',
          recipient_name: '김관리자',
          sender_id: 1,
          sender_name: '시스템',
          created_at: new Date().toISOString(),
          is_scheduled: !!formData.scheduled_at,
          is_sent: !formData.scheduled_at
        };
        
        setNotifications(prev => [...prev, newNotification]);
        toast.success('알림이 생성되었습니다.');
      }
      
      setIsCreateDialogOpen(false);
      resetForm();
      setEditingNotification(null);
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  // 알림 삭제
  const handleDelete = async (notification: Notification) => {
    try {
      setLoading(true);
      setNotifications(prev => prev.filter(n => n.id !== notification.id));
      toast.success('알림이 삭제되었습니다.');
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
      setNotifications(prev => prev.map(n => 
        n.id === notification.id 
          ? { ...n, status: 'read' as const, read_at: new Date().toISOString() }
          : n
      ));
      toast.success('알림을 읽음 처리했습니다.');
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
      setNotifications(prev => prev.map(n => 
        n.id === notification.id 
          ? { ...n, status: 'archived' as const }
          : n
      ));
      toast.success('알림을 보관했습니다.');
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
      setNotifications(prev => prev.map(n => 
        n.id === notification.id 
          ? { ...n, is_sent: true, sent_at: new Date().toISOString() }
          : n
      ));
      toast.success('알림이 즉시 전송되었습니다.');
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
      case 'info': return 'bg-blue-500/20 text-blue-400';
      case 'warning': return 'bg-yellow-500/20 text-yellow-400';
      case 'error': return 'bg-red-500/20 text-red-400';
      case 'success': return 'bg-green-500/20 text-green-400';
      case 'urgent': return 'bg-purple-500/20 text-purple-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  // 우선순위별 색상
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'low': return 'bg-green-500/20 text-green-400';
      case 'medium': return 'bg-yellow-500/20 text-yellow-400';
      case 'high': return 'bg-orange-500/20 text-orange-400';
      case 'critical': return 'bg-red-500/20 text-red-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  // 상태별 색상
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'unread': return 'bg-blue-500/20 text-blue-400';
      case 'read': return 'bg-gray-500/20 text-gray-400';
      case 'archived': return 'bg-purple-500/20 text-purple-400';
      default: return 'bg-gray-500/20 text-gray-400';
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
    <div className="min-h-screen p-6">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <Bell className="w-6 h-6" />
          알림 시스템
        </h1>
        <p className="text-gray-300 mt-2">실시간 알림과 알림 관리를 통해 중요한 정보를 놓치지 마세요</p>
      </div>

      {/* 액션 버튼 */}
      <div className="flex gap-4 mb-8">
        <Button
          onClick={handleCreate}
          className="bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700"
        >
          <Plus className="w-4 h-4 mr-2" />
          새 알림 생성
        </Button>
        <Button
          onClick={() => setIsSettingsDialogOpen(true)}
          className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700"
        >
          <Settings className="w-4 h-4 mr-2" />
          설정
        </Button>
        <Button
          onClick={fetchNotifications}
          disabled={isLoading}
          className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          새로고침
        </Button>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">총 알림</p>
                <p className="text-2xl font-bold text-white">{totalNotifications.toLocaleString()}</p>
                <p className="text-gray-400 text-sm">전체 알림 수</p>
              </div>
              <div className="w-12 h-12 bg-orange-500/20 rounded-lg flex items-center justify-center">
                <Bell className="w-6 h-6 text-orange-400" />
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">읽지 않은 알림</p>
                <p className="text-2xl font-bold text-white">{unreadNotifications.toLocaleString()}</p>
                <p className="text-gray-400 text-sm">확인 필요</p>
              </div>
              <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
                <AlertTriangle className="w-6 h-6 text-blue-400" />
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">긴급 알림</p>
                <p className="text-2xl font-bold text-white">{urgentNotifications.toLocaleString()}</p>
                <p className="text-gray-400 text-sm">즉시 처리 필요</p>
              </div>
              <div className="w-12 h-12 bg-red-500/20 rounded-lg flex items-center justify-center">
                <Zap className="w-6 h-6 text-red-400" />
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">예약된 알림</p>
                <p className="text-2xl font-bold text-white">{scheduledNotifications.toLocaleString()}</p>
                <p className="text-gray-400 text-sm">자동 발송 예정</p>
              </div>
              <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center">
                <Clock className="w-6 h-6 text-purple-400" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 필터 및 검색 */}
      <Card className="bg-white/10 backdrop-blur-sm border border-white/20 mb-8">
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="알림 제목, 내용 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 bg-white/10 border-white/20 text-white placeholder-gray-400"
              />
            </div>
            
            <Select value={selectedType} onValueChange={setSelectedType}>
              <SelectTrigger className="bg-white/10 border-white/20 text-white">
                <SelectValue placeholder="알림 타입" />
              </SelectTrigger>
              <SelectContent className="bg-white/10 border-white/20">
                <SelectItem value="all">전체 타입</SelectItem>
                <SelectItem value="info">정보</SelectItem>
                <SelectItem value="warning">경고</SelectItem>
                <SelectItem value="error">오류</SelectItem>
                <SelectItem value="success">성공</SelectItem>
                <SelectItem value="urgent">긴급</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger className="bg-white/10 border-white/20 text-white">
                <SelectValue placeholder="카테고리" />
              </SelectTrigger>
              <SelectContent className="bg-white/10 border-white/20">
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
              <SelectTrigger className="bg-white/10 border-white/20 text-white">
                <SelectValue placeholder="상태" />
              </SelectTrigger>
              <SelectContent className="bg-white/10 border-white/20">
                <SelectItem value="all">전체 상태</SelectItem>
                <SelectItem value="unread">읽지 않음</SelectItem>
                <SelectItem value="read">읽음</SelectItem>
                <SelectItem value="archived">보관됨</SelectItem>
              </SelectContent>
            </Select>
            
            <Button
              variant="outline"
              onClick={() => {
                setSearchTerm('');
                setSelectedType('all');
                setSelectedCategory('all');
                setSelectedStatus('all');
              }}
              className="border-white/20 text-white hover:bg-white/10"
            >
              <Filter className="w-4 h-4 mr-2" />
              필터 초기화
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 알림 목록 */}
      <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
        <CardHeader>
          <CardTitle className="text-white">알림 목록</CardTitle>
          <CardDescription className="text-gray-300">
            총 {filteredNotifications.length}개의 알림이 있습니다
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredNotifications.map((notification) => (
              <div
                key={notification.id}
                className={`bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:bg-white/10 transition-all duration-300 ${
                  notification.status === 'unread' ? 'border-blue-500/30 bg-blue-500/5' : ''
                }`}
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-4 mb-3">
                      <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                        notification.type === 'info' ? 'bg-blue-500/20' :
                        notification.type === 'warning' ? 'bg-yellow-500/20' :
                        notification.type === 'error' ? 'bg-red-500/20' :
                        notification.type === 'success' ? 'bg-green-500/20' :
                        'bg-purple-500/20'
                      }`}>
                        {notification.type === 'info' && <Info className="w-6 h-6 text-blue-400" />}
                        {notification.type === 'warning' && <AlertTriangle className="w-6 h-6 text-yellow-400" />}
                        {notification.type === 'error' && <X className="w-6 h-6 text-red-400" />}
                        {notification.type === 'success' && <CheckCircle className="w-6 h-6 text-green-400" />}
                        {notification.type === 'urgent' && <Zap className="w-6 h-6 text-purple-400" />}
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-white">{notification.title}</h3>
                        <p className="text-gray-400">{notification.sender_name} • {new Date(notification.created_at).toLocaleDateString()}</p>
                        <p className="text-gray-400 text-sm">{notification.message}</p>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                      <div>
                        <p className="text-gray-300 text-sm">카테고리</p>
                        <p className="text-white font-medium">{notification.category}</p>
                      </div>
                      <div>
                        <p className="text-gray-300 text-sm">수신자</p>
                        <p className="text-white font-medium">{notification.recipient_name}</p>
                      </div>
                      <div>
                        <p className="text-gray-300 text-sm">전송 방법</p>
                        <p className="text-white font-medium">{notification.delivery_method}</p>
                      </div>
                      <div>
                        <p className="text-gray-300 text-sm">생성일</p>
                        <p className="text-white font-medium">{new Date(notification.created_at).toLocaleDateString()}</p>
                      </div>
                    </div>
                    
                    {notification.scheduled_at && (
                      <div className="bg-white/5 rounded-lg p-3">
                        <p className="text-gray-300 text-sm mb-1">예약 시간</p>
                        <p className="text-white">{new Date(notification.scheduled_at).toLocaleString()}</p>
                      </div>
                    )}
                  </div>
                  
                  <div className="flex flex-col gap-2 ml-4">
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
                    
                    <div className="flex gap-2">
                      {notification.status === 'unread' && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleMarkAsRead(notification)}
                          className="border-white/20 text-white hover:bg-white/10"
                        >
                          <Check className="w-4 h-4" />
                        </Button>
                      )}
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleView(notification)}
                        className="border-white/20 text-white hover:bg-white/10"
                      >
                        <Eye className="w-4 h-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleEdit(notification)}
                        className="border-white/20 text-white hover:bg-white/10"
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      {!notification.is_sent && (
                        <Button
                          size="sm"
                          onClick={() => handleSendNow(notification)}
                          className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700"
                        >
                          <Send className="w-4 h-4" />
                        </Button>
                      )}
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleArchive(notification)}
                        className="border-white/20 text-white hover:bg-white/10"
                      >
                        <Archive className="w-4 h-4" />
                      </Button>
                      <Button
                        size="sm"
                        onClick={() => handleDelete(notification)}
                        className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            
            {filteredNotifications.length === 0 && (
              <div className="text-center py-8 text-gray-400">
                <Bell className="h-12 w-12 mx-auto mb-2 text-gray-500" />
                <p className="text-gray-300">알림이 없습니다.</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* 알림 생성/수정 다이얼로그 */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="bg-white/10 backdrop-blur-sm border border-white/20 max-w-2xl">
          <DialogHeader>
            <DialogTitle className="text-white">
              {editingNotification ? '알림 수정' : '새 알림 생성'}
            </DialogTitle>
          </DialogHeader>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label className="text-gray-300">알림 제목 *</Label>
              <Input
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="mt-1 bg-white/10 border-white/20 text-white"
                placeholder="알림 제목을 입력하세요"
              />
            </div>
            
            <div>
              <Label className="text-gray-300">알림 내용 *</Label>
              <Textarea
                value={formData.message}
                onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                className="mt-1 bg-white/10 border-white/20 text-white"
                placeholder="알림 내용을 입력하세요"
                rows={3}
              />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label className="text-gray-300">알림 타입</Label>
                <Select value={formData.type} onValueChange={(value: any) => setFormData({ ...formData, type: value })}>
                  <SelectTrigger className="mt-1 bg-white/10 border-white/20 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-white/10 border-white/20">
                    <SelectItem value="info">정보</SelectItem>
                    <SelectItem value="warning">경고</SelectItem>
                    <SelectItem value="error">오류</SelectItem>
                    <SelectItem value="success">성공</SelectItem>
                    <SelectItem value="urgent">긴급</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label className="text-gray-300">카테고리</Label>
                <Select value={formData.category} onValueChange={(value: any) => setFormData({ ...formData, category: value })}>
                  <SelectTrigger className="mt-1 bg-white/10 border-white/20 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-white/10 border-white/20">
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
                <Label className="text-gray-300">우선순위</Label>
                <Select value={formData.priority} onValueChange={(value: any) => setFormData({ ...formData, priority: value })}>
                  <SelectTrigger className="mt-1 bg-white/10 border-white/20 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-white/10 border-white/20">
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
                <Label className="text-gray-300">전송 방법</Label>
                <Select value={formData.delivery_method} onValueChange={(value: any) => setFormData({ ...formData, delivery_method: value })}>
                  <SelectTrigger className="mt-1 bg-white/10 border-white/20 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-white/10 border-white/20">
                    <SelectItem value="in_app">앱 내 알림</SelectItem>
                    <SelectItem value="email">이메일</SelectItem>
                    <SelectItem value="sms">SMS</SelectItem>
                    <SelectItem value="push">푸시 알림</SelectItem>
                    <SelectItem value="all">모든 방법</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label className="text-gray-300">예약 시간 (선택사항)</Label>
                <Input
                  type="datetime-local"
                  value={formData.scheduled_at}
                  onChange={(e) => setFormData({ ...formData, scheduled_at: e.target.value })}
                  className="mt-1 bg-white/10 border-white/20 text-white"
                />
              </div>
            </div>
            
            <div className="flex gap-2">
              <Button type="submit" className="flex-1 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700">
                {editingNotification ? '수정' : '생성'}
              </Button>
              <Button type="button" variant="outline" onClick={() => setIsCreateDialogOpen(false)} className="border-white/20 text-white hover:bg-white/10">
                취소
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* 알림 상세 보기 다이얼로그 */}
      <Dialog open={!!viewingNotification} onOpenChange={() => setViewingNotification(null)}>
        <DialogContent className="bg-white/10 backdrop-blur-sm border border-white/20 max-w-2xl">
          <DialogHeader>
            <DialogTitle className="text-white">알림 상세 정보</DialogTitle>
          </DialogHeader>
          
          {viewingNotification && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label className="text-gray-300 text-sm">알림 제목</Label>
                  <p className="text-white font-medium">{viewingNotification.title}</p>
                </div>
                
                <div>
                  <Label className="text-gray-300 text-sm">알림 타입</Label>
                  <Badge className={getTypeColor(viewingNotification.type)}>
                    {viewingNotification.type === 'info' && '정보'}
                    {viewingNotification.type === 'warning' && '경고'}
                    {viewingNotification.type === 'error' && '오류'}
                    {viewingNotification.type === 'success' && '성공'}
                    {viewingNotification.type === 'urgent' && '긴급'}
                  </Badge>
                </div>
                
                <div>
                  <Label className="text-gray-300 text-sm">우선순위</Label>
                  <Badge className={getPriorityColor(viewingNotification.priority)}>
                    {viewingNotification.priority === 'low' && '낮음'}
                    {viewingNotification.priority === 'medium' && '보통'}
                    {viewingNotification.priority === 'high' && '높음'}
                    {viewingNotification.priority === 'critical' && '긴급'}
                  </Badge>
                </div>
                
                <div>
                  <Label className="text-gray-300 text-sm">상태</Label>
                  <Badge className={getStatusColor(viewingNotification.status)}>
                    {viewingNotification.status === 'unread' && '읽지 않음'}
                    {viewingNotification.status === 'read' && '읽음'}
                    {viewingNotification.status === 'archived' && '보관됨'}
                  </Badge>
                </div>
                
                <div>
                  <Label className="text-gray-300 text-sm">카테고리</Label>
                  <p className="text-white font-medium">{viewingNotification.category}</p>
                </div>
                
                <div>
                  <Label className="text-gray-300 text-sm">수신자</Label>
                  <p className="text-white font-medium">{viewingNotification.recipient_name}</p>
                </div>
                
                <div>
                  <Label className="text-gray-300 text-sm">전송 방법</Label>
                  <p className="text-white font-medium">{viewingNotification.delivery_method}</p>
                </div>
                
                <div>
                  <Label className="text-gray-300 text-sm">생성일</Label>
                  <p className="text-white font-medium">{new Date(viewingNotification.created_at).toLocaleString()}</p>
                </div>
              </div>
              
              <div>
                <Label className="text-gray-300 text-sm">알림 내용</Label>
                <p className="text-white bg-white/5 p-3 rounded-lg">{viewingNotification.message}</p>
              </div>
              
              {viewingNotification.scheduled_at && (
                <div>
                  <Label className="text-gray-300 text-sm">예약 시간</Label>
                  <p className="text-white font-medium">{new Date(viewingNotification.scheduled_at).toLocaleString()}</p>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
} 
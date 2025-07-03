"use client"

import React, { useState, useEffect } from 'react';
import { AppLayout } from "@/components/app-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { 
  Bell, 
  Plus, 
  Search, 
  Filter, 
  Eye, 
  Edit, 
  Trash2, 
  CheckCircle,
  AlertCircle,
  Info,
  X,
  Calendar,
  User,
  Tag
} from "lucide-react"
import { noticeApi, notificationApi, NotificationSSE } from "@/lib/api"
import { useUser } from "@/components/UserContext"

// 공지사항 타입
interface Notice {
  id: number;
  title: string;
  content: string;
  category: string;
  priority: 'high' | 'medium' | 'low';
  author: string;
  createdAt: string;
  updatedAt: string;
  readCount: number;
  targetRoles?: string[];
  isRead?: boolean;
}

// 알림 타입
interface Notification {
  id: number;
  type: 'notice' | 'order' | 'inventory' | 'schedule' | 'system';
  title: string;
  message: string;
  createdAt: string;
  isRead: boolean;
  data?: any;
}

interface NotificationItem {
  id: number;
  type: 'info' | 'warning' | 'error';
  message: string;
  date: string;
}

const dummyNotifications: NotificationItem[] = [
  { id: 1, type: 'info', message: '정기 점검 안내', date: '2024-06-01' },
  { id: 2, type: 'warning', message: '재고 부족 경고', date: '2024-06-02' },
  { id: 3, type: 'error', message: '서버 오류 발생', date: '2024-06-03' },
];

// Toast 알림 컴포넌트
function Toast({ message, type, onClose }: { message: string; type: "success" | "error"; onClose: () => void }) {
  useEffect(() => {
    const timer = setTimeout(onClose, 3000);
    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className={`fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg ${
      type === "success" ? "bg-green-500 text-white" : "bg-red-500 text-white"
    }`}>
      <div className="flex items-center space-x-2">
        {type === "success" ? <CheckCircle className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
        <span>{message}</span>
        <button onClick={onClose} className="ml-2">
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

export default function NotificationsPage() {
  const { user } = useUser();
  const [activeTab, setActiveTab] = useState<'notices' | 'notifications'>('notices');
  const [searchTerm, setSearchTerm] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [priorityFilter, setPriorityFilter] = useState("all");
  const [showAddForm, setShowAddForm] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedNotice, setSelectedNotice] = useState<Notice | null>(null);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState("");
  const [toastType, setToastType] = useState<"success" | "error">("success");

  // 데이터 상태
  const [notices, setNotices] = useState<Notice[]>([]);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string|null>(null);

  // 새 공지사항 폼 상태
  const [newNotice, setNewNotice] = useState({
    title: "",
    content: "",
    category: "일반",
    priority: "medium" as "high" | "medium" | "low",
    targetRoles: [] as string[]
  });

  // Toast 알림 표시 함수
  const showToastMessage = (message: string, type: "success" | "error" = "success") => {
    setToastMessage(message);
    setToastType(type);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };

  // 공지사항 목록 조회
  const fetchNotices = async () => {
    setLoading(true);
    try {
      const response = await noticeApi.getNotices({
        category: categoryFilter !== 'all' ? categoryFilter : undefined,
        status: priorityFilter !== 'all' ? priorityFilter : undefined
      });
      
      if (response.success && response.data) {
        setNotices(response.data);
      } else {
        setNotices([]);
        showToastMessage(response.error || "공지사항을 불러오는데 실패했습니다.", "error");
      }
    } catch (error) {
      setNotices([]);
      console.error('공지사항 조회 오류:', error);
      showToastMessage("공지사항을 불러오는데 실패했습니다.", "error");
    } finally {
      setLoading(false);
    }
  };

  // 알림 목록 조회
  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const response = await notificationApi.getNotifications();
      
      if (response.success && response.data) {
        setNotifications(response.data);
      } else {
        setNotifications([]);
        showToastMessage(response.error || "알림을 불러오는데 실패했습니다.", "error");
      }
    } catch (error) {
      setNotifications([]);
      console.error('알림 조회 오류:', error);
      showToastMessage("알림을 불러오는데 실패했습니다.", "error");
    } finally {
      setLoading(false);
    }
  };

  // 실시간 알림 연결
  useEffect(() => {
    const sse = new NotificationSSE((data) => {
      if (data.type === 'notification') {
        setNotifications(prev => [data.notification, ...prev]);
        showToastMessage(`새 알림: ${data.notification.title}`);
      }
    });

    sse.connect();

    return () => {
      sse.disconnect();
    };
  }, []);

  // 초기 데이터 로드
  useEffect(() => {
    fetchNotices();
    fetchNotifications();
  }, [categoryFilter, priorityFilter]);

  // 공지사항 추가
  const handleAddNotice = async () => {
    if (!newNotice.title || !newNotice.content) {
      showToastMessage("제목과 내용을 입력해주세요.", "error");
      return;
    }

    try {
      const response = await noticeApi.createNotice({
        title: newNotice.title,
        content: newNotice.content,
        category: newNotice.category,
        priority: newNotice.priority,
        targetRoles: newNotice.targetRoles
      });

      if (response.success) {
        showToastMessage("공지사항이 성공적으로 등록되었습니다.");
        setNewNotice({ title: "", content: "", category: "일반", priority: "medium", targetRoles: [] });
        setShowAddForm(false);
        fetchNotices();
      } else {
        showToastMessage(response.error || "공지사항 등록에 실패했습니다.", "error");
      }
    } catch (error) {
      console.error('공지사항 등록 오류:', error);
      showToastMessage("공지사항 등록에 실패했습니다.", "error");
    }
  };

  // 공지사항 수정
  const handleEditNotice = async () => {
    if (!selectedNotice) return;

    try {
      const response = await noticeApi.updateNotice(selectedNotice.id, {
        title: selectedNotice.title,
        content: selectedNotice.content,
        category: selectedNotice.category,
        priority: selectedNotice.priority,
        targetRoles: selectedNotice.targetRoles
      });

      if (response.success) {
        showToastMessage("공지사항이 성공적으로 수정되었습니다.");
        setShowEditModal(false);
        setSelectedNotice(null);
        fetchNotices();
      } else {
        showToastMessage(response.error || "공지사항 수정에 실패했습니다.", "error");
      }
    } catch (error) {
      console.error('공지사항 수정 오류:', error);
      showToastMessage("공지사항 수정에 실패했습니다.", "error");
    }
  };

  // 공지사항 삭제
  const handleDeleteNotice = async (id: number) => {
    try {
      const response = await noticeApi.deleteNotice(id);
      
      if (response.success) {
        showToastMessage("공지사항이 성공적으로 삭제되었습니다.");
        setShowDetailModal(false);
        fetchNotices();
      } else {
        showToastMessage(response.error || "공지사항 삭제에 실패했습니다.", "error");
      }
    } catch (error) {
      console.error('공지사항 삭제 오류:', error);
      showToastMessage("공지사항 삭제에 실패했습니다.", "error");
    }
  };

  // 공지사항 읽음 처리
  const handleMarkAsRead = async (id: number) => {
    try {
      const response = await noticeApi.markAsRead(id);
      
      if (response.success) {
        setNotices(prev => prev.map(notice => 
          notice.id === id ? { ...notice, isRead: true } : notice
        ));
      }
    } catch (error) {
      console.error('읽음 처리 오류:', error);
    }
  };

  // 알림 읽음 처리
  const handleMarkNotificationAsRead = async (id: number) => {
    try {
      const response = await notificationApi.markAsRead(id);
      
      if (response.success) {
        setNotifications(prev => prev.map(notification => 
          notification.id === id ? { ...notification, isRead: true } : notification
        ));
      }
    } catch (error) {
      console.error('알림 읽음 처리 오류:', error);
    }
  };

  // 모든 알림 읽음 처리
  const handleMarkAllNotificationsAsRead = async () => {
    try {
      const response = await notificationApi.markAllAsRead();
      
      if (response.success) {
        setNotifications(prev => prev.map(notification => ({ ...notification, isRead: true })));
        showToastMessage("모든 알림을 읽음 처리했습니다.");
      }
    } catch (error) {
      console.error('모든 알림 읽음 처리 오류:', error);
      showToastMessage("알림 읽음 처리에 실패했습니다.", "error");
    }
  };

  // 필터링된 데이터
  const filteredNotices = notices.filter(notice =>
    notice.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    notice.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
    notice.author.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredNotifications = notifications.filter(notification =>
    notification.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    notification.message.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // 우선순위 색상
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  // 알림 타입 색상
  const getNotificationTypeColor = (type: string) => {
    switch (type) {
      case 'order': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'inventory': return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200';
      case 'schedule': return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200';
      case 'system': return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  // 권한별 분기 예시
  if (!user) return <div className="p-6">로그인 필요</div>;
  if (user.role === 'employee') {
    return <div className="p-6">직원은 본인 알림만 확인할 수 있습니다.</div>;
  }

  return (
    <AppLayout>
      <div className="p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* 헤더 */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">공지사항 & 알림</h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                공지사항과 알림을 관리하고 확인하세요
              </p>
            </div>
            <div className="flex items-center space-x-2">
              {activeTab === 'notices' && (
                <Button onClick={() => setShowAddForm(true)}>
                  <Plus className="w-4 h-4 mr-2" />
                  공지사항 작성
                </Button>
              )}
              {activeTab === 'notifications' && (
                <Button variant="outline" onClick={handleMarkAllNotificationsAsRead}>
                  모두 읽음 처리
                </Button>
              )}
            </div>
          </div>

          {/* 탭 네비게이션 */}
          <div className="flex space-x-1 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
            <button
              onClick={() => setActiveTab('notices')}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'notices'
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              공지사항
            </button>
            <button
              onClick={() => setActiveTab('notifications')}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'notifications'
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              알림
              {notifications.filter(n => !n.isRead).length > 0 && (
                <Badge className="ml-2 bg-red-500 text-white text-xs">
                  {notifications.filter(n => !n.isRead).length}
                </Badge>
              )}
            </button>
          </div>

          {/* 검색 및 필터 */}
          <div className="flex items-center space-x-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            {activeTab === 'notices' && (
              <>
                <select
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  className="border rounded-md px-3 py-2 bg-white dark:bg-gray-800"
                >
                  <option value="all">모든 카테고리</option>
                  <option value="일반">일반</option>
                  <option value="업무">업무</option>
                  <option value="시스템">시스템</option>
                  <option value="일정">일정</option>
                </select>
                <select
                  value={priorityFilter}
                  onChange={(e) => setPriorityFilter(e.target.value)}
                  className="border rounded-md px-3 py-2 bg-white dark:bg-gray-800"
                >
                  <option value="all">모든 우선순위</option>
                  <option value="high">높음</option>
                  <option value="medium">보통</option>
                  <option value="low">낮음</option>
                </select>
              </>
            )}
          </div>

          {/* 공지사항 탭 */}
          {activeTab === 'notices' && (
            <div className="grid gap-6">
              {loading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                  <p className="mt-2 text-gray-600 dark:text-gray-400">로딩 중...</p>
                </div>
              ) : filteredNotices.length === 0 ? (
                <div className="text-center py-8 text-gray-400">공지사항이 없습니다.</div>
              ) : (
                filteredNotices.map((notice) => (
                  <Card key={notice.id} className="hover:shadow-lg transition-shadow">
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                              {notice.title}
                            </h3>
                            <Badge className={getPriorityColor(notice.priority)}>
                              {notice.priority === 'high' ? '높음' : 
                               notice.priority === 'medium' ? '보통' : '낮음'}
                            </Badge>
                            <Badge variant="outline">{notice.category}</Badge>
                          </div>
                          <p className="text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">
                            {notice.content}
                          </p>
                          <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                            <div className="flex items-center">
                              <User className="w-4 h-4 mr-1" />
                              {notice.author}
                            </div>
                            <div className="flex items-center">
                              <Calendar className="w-4 h-4 mr-1" />
                              {new Date(notice.createdAt).toLocaleDateString()}
                            </div>
                            <div className="flex items-center">
                              <Eye className="w-4 h-4 mr-1" />
                              조회 {notice.readCount}회
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2 ml-4">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setSelectedNotice(notice);
                              setShowDetailModal(true);
                              handleMarkAsRead(notice.id);
                            }}
                          >
                            <Eye className="w-3 h-3" />
                          </Button>
                          {(user?.role === 'admin' || user?.role === 'manager') && (
                            <>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => {
                                  setSelectedNotice({ ...notice });
                                  setShowEditModal(true);
                                }}
                              >
                                <Edit className="w-3 h-3" />
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleDeleteNotice(notice.id)}
                              >
                                <Trash2 className="w-3 h-3" />
                              </Button>
                            </>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          )}

          {/* 알림 탭 */}
          {activeTab === 'notifications' && (
            <div className="space-y-4">
              {loading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                  <p className="mt-2 text-gray-600 dark:text-gray-400">로딩 중...</p>
                </div>
              ) : filteredNotifications.length === 0 ? (
                <div className="text-center py-8 text-gray-400">알림이 없습니다.</div>
              ) : (
                filteredNotifications.map((notification) => (
                  <Card 
                    key={notification.id} 
                    className={`hover:shadow-lg transition-shadow ${
                      !notification.isRead ? 'border-l-4 border-blue-500 bg-blue-50 dark:bg-blue-900/20' : ''
                    }`}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <h3 className="font-semibold text-gray-900 dark:text-white">
                              {notification.title}
                            </h3>
                            <Badge className={getNotificationTypeColor(notification.type)}>
                              {notification.type === 'order' ? '발주' :
                               notification.type === 'inventory' ? '재고' :
                               notification.type === 'schedule' ? '일정' : '시스템'}
                            </Badge>
                            {!notification.isRead && (
                              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                            )}
                          </div>
                          <p className="text-gray-600 dark:text-gray-400 mb-2">
                            {notification.message}
                          </p>
                          <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                            <Calendar className="w-4 h-4 mr-1" />
                            {new Date(notification.createdAt).toLocaleString()}
                          </div>
                        </div>
                        <div className="flex items-center space-x-2 ml-4">
                          {!notification.isRead && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleMarkNotificationAsRead(notification.id)}
                            >
                              읽음 처리
                            </Button>
                          )}
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDeleteNotice(notification.id)}
                          >
                            <Trash2 className="w-3 h-3" />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          )}
        </div>

        {/* 공지사항 작성 모달 */}
        {showAddForm && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-900 rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold">공지사항 작성</h2>
                <Button variant="ghost" size="sm" onClick={() => setShowAddForm(false)}>
                  <X className="w-4 h-4" />
                </Button>
              </div>
              <div className="space-y-4">
                <Input
                  placeholder="제목"
                  value={newNotice.title}
                  onChange={(e) => setNewNotice({...newNotice, title: e.target.value})}
                />
                <Textarea
                  placeholder="내용"
                  value={newNotice.content}
                  onChange={(e) => setNewNotice({...newNotice, content: e.target.value})}
                  rows={6}
                />
                <div className="grid grid-cols-2 gap-4">
                  <select
                    value={newNotice.category}
                    onChange={(e) => setNewNotice({...newNotice, category: e.target.value})}
                    className="border rounded px-3 py-2"
                  >
                    <option value="일반">일반</option>
                    <option value="업무">업무</option>
                    <option value="시스템">시스템</option>
                    <option value="일정">일정</option>
                  </select>
                  <select
                    value={newNotice.priority}
                    onChange={(e) => setNewNotice({...newNotice, priority: e.target.value as "high" | "medium" | "low"})}
                    className="border rounded px-3 py-2"
                  >
                    <option value="low">낮음</option>
                    <option value="medium">보통</option>
                    <option value="high">높음</option>
                  </select>
                </div>
              </div>
              <div className="flex justify-end space-x-2 mt-6">
                <Button variant="outline" onClick={() => setShowAddForm(false)}>
                  취소
                </Button>
                <Button onClick={handleAddNotice}>
                  등록
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* 공지사항 상세 모달 */}
        {showDetailModal && selectedNotice && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-900 rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold">공지사항 상세</h2>
                <Button variant="ghost" size="sm" onClick={() => setShowDetailModal(false)}>
                  <X className="w-4 h-4" />
                </Button>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">제목</label>
                  <p className="text-gray-900 dark:text-white">{selectedNotice.title}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">내용</label>
                  <p className="text-gray-900 dark:text-white whitespace-pre-wrap">{selectedNotice.content}</p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">카테고리</label>
                    <Badge variant="outline">{selectedNotice.category}</Badge>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">우선순위</label>
                    <Badge className={getPriorityColor(selectedNotice.priority)}>
                      {selectedNotice.priority === 'high' ? '높음' : 
                       selectedNotice.priority === 'medium' ? '보통' : '낮음'}
                    </Badge>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">작성자</label>
                    <p className="text-gray-900 dark:text-white">{selectedNotice.author}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">작성일</label>
                    <p className="text-gray-900 dark:text-white">
                      {new Date(selectedNotice.createdAt).toLocaleString()}
                    </p>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">조회수</label>
                  <p className="text-gray-900 dark:text-white">{selectedNotice.readCount}회</p>
                </div>
              </div>
              <div className="flex justify-end mt-6">
                <Button onClick={() => setShowDetailModal(false)}>
                  닫기
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* 공지사항 수정 모달 */}
        {showEditModal && selectedNotice && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-900 rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold">공지사항 수정</h2>
                <Button variant="ghost" size="sm" onClick={() => setShowEditModal(false)}>
                  <X className="w-4 h-4" />
                </Button>
              </div>
              <div className="space-y-4">
                <Input
                  placeholder="제목"
                  value={selectedNotice.title}
                  onChange={(e) => setSelectedNotice({...selectedNotice, title: e.target.value})}
                />
                <Textarea
                  placeholder="내용"
                  value={selectedNotice.content}
                  onChange={(e) => setSelectedNotice({...selectedNotice, content: e.target.value})}
                  rows={6}
                />
                <div className="grid grid-cols-2 gap-4">
                  <select
                    value={selectedNotice.category}
                    onChange={(e) => setSelectedNotice({...selectedNotice, category: e.target.value})}
                    className="border rounded px-3 py-2"
                  >
                    <option value="일반">일반</option>
                    <option value="업무">업무</option>
                    <option value="시스템">시스템</option>
                    <option value="일정">일정</option>
                  </select>
                  <select
                    value={selectedNotice.priority}
                    onChange={(e) => setSelectedNotice({...selectedNotice, priority: e.target.value as "high" | "medium" | "low"})}
                    className="border rounded px-3 py-2"
                  >
                    <option value="low">낮음</option>
                    <option value="medium">보통</option>
                    <option value="high">높음</option>
                  </select>
                </div>
              </div>
              <div className="flex justify-end space-x-2 mt-6">
                <Button variant="outline" onClick={() => setShowEditModal(false)}>
                  취소
                </Button>
                <Button onClick={handleEditNotice}>
                  수정
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Toast 알림 */}
        {showToast && (
          <Toast
            message={toastMessage}
            type={toastType}
            onClose={() => setShowToast(false)}
          />
        )}
      </div>
    </AppLayout>
  )
} 
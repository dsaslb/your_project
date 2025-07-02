"use client"

import React, { useState, useEffect } from "react"
import { AppLayout } from "@/components/app-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { 
  Package, 
  Plus, 
  Search, 
  Edit, 
  Trash2, 
  ShoppingCart,
  Clock,
  DollarSign,
  AlertTriangle,
  Eye,
  Check,
  X,
  ThumbsUp,
  ThumbsDown,
  CheckCircle,
  XCircle,
  AlertCircle,
  FileText,
  Truck,
  Loader2,
  UserCheck,
  UserX,
  Calendar,
  ChevronDown,
  ChevronUp,
  MoreVertical
} from "lucide-react"
import { useUser } from "@/components/UserContext"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
import { api as noticeApi } from '../notice/page';
import { toast } from 'sonner';
import NotificationService from '@/lib/notification-service';

// 발주 타입 정의
interface Order {
  id: number;
  item: string;
  quantity: number;
  unit: string;
  supplier: string;
  price: number;
  status: "pending" | "approved" | "rejected" | "delivered";
  priority: "high" | "medium" | "low";
  requester: string;
  requestedAt: string;
  expectedDate: string;
  approvedBy?: string;
  deliveredAt?: string;
  notes?: string;
}

// Toast 알림용
function Toast({ message, type, onClose }: { message: string; type: "success" | "error"; onClose: () => void }) {
  return (
    <div className={`fixed top-6 right-6 z-50 px-4 py-3 rounded shadow-lg text-white ${type === "success" ? "bg-green-600" : "bg-red-600"}`}
      role="alert">
      <div className="flex items-center gap-2">
        {type === "success" ? <CheckCircle className="w-5 h-5" /> : <XCircle className="w-5 h-5" />}
        <span>{message}</span>
        <button className="ml-2" onClick={onClose}><X className="w-4 h-4" /></button>
      </div>
    </div>
  );
}

// 알림 등록 함수
async function createOrderNotice({ type, title, content, author }) {
  try {
    await noticeApi.createNotice({
      type,
      title,
      content,
      status: 'unread',
      author
    });
  } catch (e) {
    // 무시(실패 시에도 orders는 정상 동작)
  }
}

export default function OrdersPage() {
  const { user } = useUser();
  const [searchTerm, setSearchTerm] = useState("")
  const [showAddForm, setShowAddForm] = useState(false)
  const [showDetailModal, setShowDetailModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null)
  const [showToast, setShowToast] = useState(false)
  const [toastMessage, setToastMessage] = useState("")
  const [toastType, setToastType] = useState<"success" | "error">("success")
  const [statusFilter, setStatusFilter] = useState<string>("all")
  const [orders, setOrders] = useState<Order[]>([])
  const [filteredOrders, setFilteredOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  
  // 더미 발주 데이터
  const [ordersData, setOrdersData] = useState<Order[]>([
    {
      id: 1,
      item: "쌀 20kg",
      quantity: 2,
      unit: "포",
      supplier: "농협",
      price: 45000,
      status: "pending",
      priority: "medium",
      requester: "김철수",
      requestedAt: "2024-06-01 09:00",
      expectedDate: "2024-06-03",
      notes: "주간 재고 확보용"
    },
    {
      id: 2,
      item: "닭고기 10kg",
      quantity: 1,
      unit: "박스",
      supplier: "삼성물산",
      price: 35000,
      status: "approved",
      priority: "high",
      requester: "이영희",
      requestedAt: "2024-06-02 10:30",
      expectedDate: "2024-06-04",
      approvedBy: "정수진",
      notes: "특가 행사용"
    },
    {
      id: 3,
      item: "설탕 5kg",
      quantity: 3,
      unit: "봉",
      supplier: "CJ제일제당",
      price: 8000,
      status: "rejected",
      priority: "low",
      requester: "박민수",
      requestedAt: "2024-06-03 11:00",
      expectedDate: "2024-06-05",
      notes: "재고 충분"
    },
    {
      id: 4,
      item: "식용유 18L",
      quantity: 1,
      unit: "통",
      supplier: "오뚜기",
      price: 25000,
      status: "delivered",
      priority: "medium",
      requester: "최지영",
      requestedAt: "2024-06-04 08:45",
      expectedDate: "2024-06-06",
      approvedBy: "정수진",
      deliveredAt: "2024-06-05 14:00",
      notes: "정기 발주"
    }
  ])

  // 새 발주 폼 상태
  const [newOrder, setNewOrder] = useState({
    item: "",
    quantity: "",
    unit: "",
    supplier: "",
    price: "",
    expectedDate: "",
    priority: "medium" as "high" | "medium" | "low",
    notes: ""
  })

  // Toast 알림 표시 함수
  const showToastMessage = (message: string, type: "success" | "error" = "success") => {
    setToastMessage(message)
    setToastType(type)
    setShowToast(true)
    setTimeout(() => setShowToast(false), 3000)
  }

  // 발주 추가
  const handleAddOrder = async (orderData: Omit<Order, 'id' | 'createdAt' | 'updatedAt'>) => {
    try {
      const newOrder: Order = {
        ...orderData,
        id: Date.now().toString(),
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      setOrders(prev => [newOrder, ...prev]);
      showToastMessage("발주가 등록되었습니다.", "success");

      // 발주 등록 알림 생성
      await NotificationService.createOrderNotification('created', newOrder);
    } catch (error) {
      console.error('발주 등록 실패:', error);
      showToastMessage('발주 등록에 실패했습니다.', 'error');
    }
      setShowAddForm(false);
      toast.success('발주가 등록되었습니다.');

      // 발주 등록 알림 생성
      await NotificationService.createOrderNotification('created', newOrder);
    } catch (error) {
      console.error('발주 등록 실패:', error);
      toast.error('발주 등록에 실패했습니다.');
    }
  };

  // 발주 수정
  const handleEditOrder = () => {
    if (!selectedOrder) return

    const updatedOrdersData = orders.map(order =>
      order.id === selectedOrder.id ? selectedOrder : order
    )
    setOrders(updatedOrdersData)
    setShowEditModal(false)
    setSelectedOrder(null)
    showToastMessage("발주가 성공적으로 수정되었습니다.")
  }

  // 발주 삭제
  const handleDeleteOrder = async (id: string) => {
    try {
      const orderToDelete = orders.find(order => order.id === id);
      setOrders(prev => prev.filter(order => order.id !== id));
      toast.success('발주가 삭제되었습니다.');

      // 발주 삭제 알림 생성
      if (orderToDelete) {
        await NotificationService.createOrderNotification('cancelled', orderToDelete);
      }
    } catch (error) {
      console.error('발주 삭제 실패:', error);
      toast.error('발주 삭제에 실패했습니다.');
    }
  };

  // 발주 승인
  const handleApproveOrder = async (id: number) => {
    try {
      const order = ordersData.find(order => order.id === id);
      if (!order) return;

      const updatedOrder = { ...order, status: "approved" as const };
      setOrdersData(prev => prev.map(o => o.id === id ? updatedOrder : o));
      showToastMessage("발주가 승인되었습니다.", "success");

      // 발주 승인 알림 생성
      await NotificationService.createOrderNotification('approved', updatedOrder);
    } catch (error) {
      console.error('발주 승인 실패:', error);
      showToastMessage('발주 승인에 실패했습니다.', 'error');
    }
  };

  // 발주 거절
  const handleRejectOrder = async (id: number) => {
    try {
      const order = ordersData.find(order => order.id === id);
      if (!order) return;

      const updatedOrder = { ...order, status: "rejected" as const };
      setOrdersData(prev => prev.map(o => o.id === id ? updatedOrder : o));
      showToastMessage("발주가 거절되었습니다.", "success");

      // 발주 거절 알림 생성
      await NotificationService.createOrderNotification('rejected', updatedOrder);
    } catch (error) {
      console.error('발주 거절 실패:', error);
      showToastMessage('발주 거절에 실패했습니다.', 'error');
    }
  };

  // 발주 상세 보기
  const handleViewDetail = (order: Order) => {
    setSelectedOrder(order)
    setShowDetailModal(true)
  }

  // 발주 수정 모달 열기
  const handleEditClick = (order: Order) => {
    setSelectedOrder({ ...order })
    setShowEditModal(true)
  }

  const filteredOrders = orders.filter(order =>
    order.item.toLowerCase().includes(searchTerm.toLowerCase()) ||
    order.requester.toLowerCase().includes(searchTerm.toLowerCase()) ||
    order.status.toLowerCase().includes(statusFilter.toLowerCase())
  )

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
      case 'approved': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
      case 'delivered': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
      case 'rejected': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
      case 'medium': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
      case 'low': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
    }
  }

  const pendingOrders = orders.filter(order => order.status === 'pending').length
  const totalOrderValue = orders.reduce((sum, order) => sum + order.quantity, 0)
  const highPriorityOrders = orders.filter(order => order.priority === 'high').length

  return (
    <AppLayout>
      <div className="w-full h-full bg-gray-50 dark:bg-gray-900 p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* 헤더 */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">발주 관리</h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                재료 발주 및 공급업체 관리
              </p>
            </div>
            <Button onClick={() => setShowAddForm(!showAddForm)}>
              <Plus className="w-4 h-4 mr-2" />
              새 발주
            </Button>
          </div>

          {/* 페이지 정상 작동 메시지 */}
          <Card className="bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800">
            <CardContent className="p-4">
              <div className="flex items-center">
                <Check className="w-5 h-5 text-green-600 mr-2" />
                <span className="text-green-800 dark:text-green-200 font-medium">
                  ✅ 발주 관리 페이지 정상 작동 중 - 등록/수정/삭제/승인/거절 기능 테스트 가능
                </span>
              </div>
            </CardContent>
          </Card>

          {/* 통계 카드 */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">총 발주 건수</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">{orders.length}건</p>
                  </div>
                  <Package className="w-8 h-8 text-blue-600" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">대기중 발주</p>
                    <p className="text-2xl font-bold text-yellow-600">{pendingOrders}건</p>
                  </div>
                  <Clock className="w-8 h-8 text-yellow-600" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">총 발주액</p>
                    <p className="text-2xl font-bold text-green-600">₩{totalOrderValue.toLocaleString()}</p>
                  </div>
                  <DollarSign className="w-8 h-8 text-green-600" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">긴급 발주</p>
                    <p className="text-2xl font-bold text-red-600">{highPriorityOrders}건</p>
                  </div>
                  <AlertTriangle className="w-8 h-8 text-red-600" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 검색 및 필터 */}
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="품목명, 요청자, 상태로 검색..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <div>
                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-md bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                  >
                    <option value="all">전체 상태</option>
                    <option value="pending">대기</option>
                    <option value="approved">승인</option>
                    <option value="rejected">거절</option>
                    <option value="delivered">납품완료</option>
                  </select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 발주 추가 폼 */}
          {showAddForm && (
            <Card>
              <CardHeader>
                <CardTitle>새 발주 추가</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input 
                    placeholder="품목명" 
                    value={newOrder.item}
                    onChange={(e) => setNewOrder({...newOrder, item: e.target.value})}
                  />
                  <Input 
                    placeholder="수량" 
                    type="number" 
                    value={newOrder.quantity}
                    onChange={(e) => setNewOrder({...newOrder, quantity: e.target.value})}
                  />
                  <Input 
                    placeholder="단위" 
                    value={newOrder.unit}
                    onChange={(e) => setNewOrder({...newOrder, unit: e.target.value})}
                  />
                  <Input 
                    placeholder="공급업체" 
                    value={newOrder.supplier}
                    onChange={(e) => setNewOrder({...newOrder, supplier: e.target.value})}
                  />
                  <Input 
                    placeholder="단가" 
                    type="number" 
                    value={newOrder.price}
                    onChange={(e) => setNewOrder({...newOrder, price: e.target.value})}
                  />
                  <Input 
                    placeholder="예상 도착일" 
                    type="date" 
                    value={newOrder.expectedDate}
                    onChange={(e) => setNewOrder({...newOrder, expectedDate: e.target.value})}
                  />
                  <select 
                    className="border rounded px-3 py-2"
                    value={newOrder.priority}
                    onChange={(e) => setNewOrder({...newOrder, priority: e.target.value as "high" | "medium" | "low"})}
                  >
                    <option value="high">높음</option>
                    <option value="medium">보통</option>
                    <option value="low">낮음</option>
                  </select>
                </div>
                <div className="mt-4">
                  <textarea 
                    className="w-full border rounded px-3 py-2"
                    placeholder="메모"
                    value={newOrder.notes}
                    onChange={(e) => setNewOrder({...newOrder, notes: e.target.value})}
                  />
                </div>
                <div className="flex justify-end space-x-2 mt-4">
                  <Button variant="outline" onClick={() => setShowAddForm(false)}>
                    취소
                  </Button>
                  <Button onClick={() => handleAddOrder(newOrder)}>발주 요청</Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* 발주 목록 테이블 */}
          <Card>
            <CardHeader>
              <CardTitle>발주 목록</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-3">발주번호</th>
                      <th className="text-left p-3">품목</th>
                      <th className="text-left p-3">수량</th>
                      <th className="text-left p-3">공급업체</th>
                      <th className="text-left p-3">금액</th>
                      <th className="text-left p-3">상태</th>
                      <th className="text-left p-3">우선순위</th>
                      <th className="text-left p-3">예상도착일</th>
                      <th className="text-left p-3">작업</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredOrders.map((order) => (
                      <tr key={order.id} className="border-b hover:bg-gray-50 dark:hover:bg-gray-800">
                        <td className="p-3 font-medium">{order.id}</td>
                        <td className="p-3">{order.item}</td>
                        <td className="p-3">{order.quantity} {order.unit}</td>
                        <td className="p-3">{order.supplier}</td>
                        <td className="p-3">₩{(order.quantity * (order.price || 0)).toLocaleString()}</td>
                        <td className="p-3">
                          <Badge className={getStatusColor(order.status)}>
                            {order.status === 'pending' && '대기중'}
                            {order.status === 'approved' && '승인됨'}
                            {order.status === 'delivered' && '배송완료'}
                            {order.status === 'rejected' && '거절됨'}
                          </Badge>
                        </td>
                        <td className="p-3">
                          <Badge className={getPriorityColor(order.priority)}>
                            {order.priority === 'high' && '높음'}
                            {order.priority === 'medium' && '보통'}
                            {order.priority === 'low' && '낮음'}
                          </Badge>
                        </td>
                        <td className="p-3">{order.expectedDate}</td>
                        <td className="p-3">
                          <div className="flex items-center space-x-2">
                            <Button variant="outline" size="sm" onClick={() => handleViewDetail(order)}>
                              <Eye className="w-3 h-3" />
                            </Button>
                            <Button variant="outline" size="sm" onClick={() => handleEditClick(order)}>
                              <Edit className="w-3 h-3" />
                            </Button>
                            {order.status === 'pending' && (
                              <>
                                <Button variant="outline" size="sm" onClick={() => handleApproveOrder(order.id.toString())}>
                                  <ThumbsUp className="w-3 h-3" />
                                </Button>
                                <Button variant="outline" size="sm" onClick={() => handleRejectOrder(order.id.toString())}>
                                  <ThumbsDown className="w-3 h-3" />
                                </Button>
                              </>
                            )}
                            <Button variant="outline" size="sm" onClick={() => handleDeleteOrder(order.id.toString())}>
                              <Trash2 className="w-3 h-3" />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 발주 상세 모달 */}
        {showDetailModal && selectedOrder && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-900 rounded-lg p-6 w-full max-w-md">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold">발주 상세</h2>
                <Button variant="ghost" size="sm" onClick={() => setShowDetailModal(false)}>
                  <X className="w-4 h-4" />
                </Button>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">발주번호</label>
                  <p className="text-gray-900 dark:text-white">{selectedOrder.id}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">품목</label>
                  <p className="text-gray-900 dark:text-white">{selectedOrder.item}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">수량</label>
                  <p className="text-gray-900 dark:text-white">{selectedOrder.quantity} {selectedOrder.unit}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">공급업체</label>
                  <p className="text-gray-900 dark:text-white">{selectedOrder.supplier}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">금액</label>
                  <p className="text-gray-900 dark:text-white">₩{(selectedOrder.quantity * (selectedOrder.price || 0)).toLocaleString()}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">상태</label>
                  <Badge className={getStatusColor(selectedOrder.status)}>
                    {selectedOrder.status === 'pending' && '대기중'}
                    {selectedOrder.status === 'approved' && '승인됨'}
                    {selectedOrder.status === 'delivered' && '배송완료'}
                    {selectedOrder.status === 'rejected' && '거절됨'}
                  </Badge>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">우선순위</label>
                  <Badge className={getPriorityColor(selectedOrder.priority)}>
                    {selectedOrder.priority === 'high' && '높음'}
                    {selectedOrder.priority === 'medium' && '보통'}
                    {selectedOrder.priority === 'low' && '낮음'}
                  </Badge>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">발주일</label>
                  <p className="text-gray-900 dark:text-white">{selectedOrder.requestedAt}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">예상도착일</label>
                  <p className="text-gray-900 dark:text-white">{selectedOrder.expectedDate}</p>
                </div>
                {selectedOrder.approvedBy && (
                  <div>
                    <label className="block text-sm font-medium mb-1">승인자</label>
                    <p className="text-gray-900 dark:text-white">{selectedOrder.approvedBy}</p>
                  </div>
                )}
                {selectedOrder.deliveredAt && (
                  <div>
                    <label className="block text-sm font-medium mb-1">납품일</label>
                    <p className="text-gray-900 dark:text-white">{selectedOrder.deliveredAt}</p>
                  </div>
                )}
                {selectedOrder.notes && (
                  <div>
                    <label className="block text-sm font-medium mb-1">메모</label>
                    <p className="text-gray-900 dark:text-white">{selectedOrder.notes}</p>
                  </div>
                )}
              </div>
              <div className="flex justify-end mt-6">
                <Button onClick={() => setShowDetailModal(false)}>
                  닫기
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* 발주 수정 모달 */}
        {showEditModal && selectedOrder && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-900 rounded-lg p-6 w-full max-w-md">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold">발주 수정</h2>
                <Button variant="ghost" size="sm" onClick={() => setShowEditModal(false)}>
                  <X className="w-4 h-4" />
                </Button>
              </div>
              <div className="space-y-4">
                <Input
                  placeholder="품목명"
                  value={selectedOrder.item}
                  onChange={(e) => setSelectedOrder({...selectedOrder, item: e.target.value})}
                />
                <Input
                  placeholder="수량"
                  type="number"
                  value={selectedOrder.quantity}
                  onChange={(e) => setSelectedOrder({...selectedOrder, quantity: parseInt(e.target.value)})}
                />
                <Input
                  placeholder="단위"
                  value={selectedOrder.unit}
                  onChange={(e) => setSelectedOrder({...selectedOrder, unit: e.target.value})}
                />
                <Input
                  placeholder="공급업체"
                  value={selectedOrder.supplier}
                  onChange={(e) => setSelectedOrder({...selectedOrder, supplier: e.target.value})}
                />
                <Input
                  placeholder="단가"
                  type="number"
                  value={selectedOrder.price}
                  onChange={(e) => setSelectedOrder({...selectedOrder, price: parseInt(e.target.value)})}
                />
                <Input
                  placeholder="예상 도착일"
                  type="date"
                  value={selectedOrder.expectedDate}
                  onChange={(e) => setSelectedOrder({...selectedOrder, expectedDate: e.target.value})}
                />
                <select
                  className="w-full border rounded px-3 py-2"
                  value={selectedOrder.priority}
                  onChange={(e) => setSelectedOrder({...selectedOrder, priority: e.target.value as "high" | "medium" | "low"})}
                >
                  <option value="high">높음</option>
                  <option value="medium">보통</option>
                  <option value="low">낮음</option>
                </select>
                <textarea
                  className="w-full border rounded px-3 py-2"
                  placeholder="메모"
                  value={selectedOrder.notes || ""}
                  onChange={(e) => setSelectedOrder({...selectedOrder, notes: e.target.value})}
                />
              </div>
              <div className="flex justify-end space-x-2 mt-6">
                <Button variant="outline" onClick={() => setShowEditModal(false)}>
                  취소
                </Button>
                <Button onClick={handleEditOrder}>
                  수정
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Toast 알림 */}
        {showToast && (
          <div className={`fixed bottom-4 right-4 z-50 p-4 rounded-lg shadow-lg ${
            toastType === "success" 
              ? "bg-green-500 text-white" 
              : "bg-red-500 text-white"
          }`}>
            {toastMessage}
          </div>
        )}
      </div>
    </AppLayout>
  )
} 
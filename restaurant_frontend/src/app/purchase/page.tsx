"use client";
import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Package, User, Calendar, Clock, CheckCircle, AlertCircle, XCircle, Plus, Search } from "lucide-react";
import NotificationPopup from "@/components/NotificationPopup";

interface Order {
  id: number;
  item: string;
  quantity: number;
  unit: string;
  order_date: string;
  ordered_by: string;
  ordered_by_id: number;
  status: string;
  detail: string;
  memo: string;
  supplier: string;
  unit_price: number;
  total_cost: number;
  created_at: string;
  completed_at?: string;
}

export default function PurchasePage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [newOrder, setNewOrder] = useState({
    item: "",
    quantity: 1,
    unit: "개",
    order_date: new Date().toISOString().split('T')[0],
    detail: "",
    memo: "",
    supplier: "",
    unit_price: 0
  });

  // 발주 목록 로드
  useEffect(() => {
    loadOrders();
  }, []);

  const loadOrders = async () => {
    try {
      const response = await fetch('/api/orders', {
        credentials: 'include'
      });
      const data = await response.json();
      
      if (data.success) {
        setOrders(data.data);
      } else {
        console.error('발주 목록 로드 실패:', data.error);
      }
    } catch (error) {
      console.error('발주 목록 로드 오류:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddOrder = async () => {
    if (!newOrder.item || newOrder.quantity <= 0) {
      alert("물품명과 수량을 입력해주세요.");
      return;
    }

    try {
      const response = await fetch('/api/orders', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(newOrder)
      });

      const result = await response.json();

      if (result.success) {
        alert("발주가 성공적으로 생성되었습니다.");
        setNewOrder({
          item: "",
          quantity: 1,
          unit: "개",
          order_date: new Date().toISOString().split('T')[0],
          detail: "",
          memo: "",
          supplier: "",
          unit_price: 0
        });
        setShowAddModal(false);
        loadOrders();
      } else {
        alert(result.error || "발주 생성 중 오류가 발생했습니다.");
      }
    } catch (error) {
      console.error('발주 생성 오류:', error);
      alert("발주 생성 중 오류가 발생했습니다.");
    }
  };

  const handleStatusChange = async (orderId: number, newStatus: string) => {
    try {
      let endpoint = '';
      let method = 'POST';
      
      switch (newStatus) {
        case 'approved':
          endpoint = `/api/orders/${orderId}/approve`;
          break;
        case 'rejected':
          endpoint = `/api/orders/${orderId}/reject`;
          break;
        case 'delivered':
          endpoint = `/api/orders/${orderId}/deliver`;
          break;
        default:
          return;
      }

      const response = await fetch(endpoint, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: newStatus === 'rejected' ? JSON.stringify({ reason: '관리자 거절' }) : undefined
      });

      const result = await response.json();

      if (result.success) {
        alert(result.message);
        loadOrders();
      } else {
        alert(result.error || "상태 변경 중 오류가 발생했습니다.");
      }
    } catch (error) {
      console.error('상태 변경 오류:', error);
      alert("상태 변경 중 오류가 발생했습니다.");
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      pending: { label: "대기중", color: "bg-yellow-100 text-yellow-800" },
      approved: { label: "승인됨", color: "bg-blue-100 text-blue-800" },
      delivered: { label: "배송완료", color: "bg-green-100 text-green-800" },
      rejected: { label: "거절됨", color: "bg-red-100 text-red-800" }
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.pending;
    
    return (
      <Badge className={config.color}>
        {config.label}
      </Badge>
    );
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <Clock className="h-4 w-4" />;
      case 'approved':
        return <AlertCircle className="h-4 w-4" />;
      case 'delivered':
        return <CheckCircle className="h-4 w-4" />;
      case 'rejected':
        return <XCircle className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  const filteredOrders = orders.filter(order => {
    const matchesSearch = order.item.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         order.ordered_by.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === "all" || order.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  if (loading) {
    return (
      <div className="p-6">
        <div className="text-center">로딩 중...</div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">발주 관리</h1>
        <Button onClick={() => setShowAddModal(true)}>
          <Plus className="h-4 w-4 mr-2" />
          새 발주
        </Button>
      </div>

      {/* 필터 및 검색 */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="물품명 또는 발주자로 검색..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="상태 필터" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">전체</SelectItem>
                <SelectItem value="pending">대기중</SelectItem>
                <SelectItem value="approved">승인됨</SelectItem>
                <SelectItem value="delivered">배송완료</SelectItem>
                <SelectItem value="rejected">거절됨</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* 발주 목록 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Package className="h-5 w-5" />
            발주 목록 ({filteredOrders.length}건)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredOrders.map((order) => (
              <div key={order.id} className="border rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      {getStatusIcon(order.status)}
                      <span className="font-semibold text-lg">{order.item}</span>
                      {getStatusBadge(order.status)}
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600 mb-2">
                      <div className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        <span>발주일: {order.order_date}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <User className="h-4 w-4" />
                        <span>발주자: {order.ordered_by}</span>
                      </div>
                      <div>
                        <span>수량: {order.quantity} {order.unit}</span>
                      </div>
                      <div>
                        <span>단가: {order.unit_price?.toLocaleString()}원</span>
                      </div>
                    </div>
                    
                    {order.detail && (
                      <p className="text-gray-700 mb-2">{order.detail}</p>
                    )}
                    
                    {order.memo && (
                      <p className="text-gray-500 text-sm mb-2">메모: {order.memo}</p>
                    )}
                    
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span>공급업체: {order.supplier || "미지정"}</span>
                      <span>총 비용: {order.total_cost?.toLocaleString()}원</span>
                      <span>생성일: {new Date(order.created_at).toLocaleString()}</span>
                    </div>
                  </div>
                  
                  <div className="flex flex-col gap-2">
                    {order.status === 'pending' && (
                      <>
                        <Button
                          size="sm"
                          onClick={() => handleStatusChange(order.id, 'approved')}
                          className="bg-blue-600 hover:bg-blue-700"
                        >
                          승인
                        </Button>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => handleStatusChange(order.id, 'rejected')}
                        >
                          거절
                        </Button>
                      </>
                    )}
                    
                    {order.status === 'approved' && (
                      <Button
                        size="sm"
                        onClick={() => handleStatusChange(order.id, 'delivered')}
                        className="bg-green-600 hover:bg-green-700"
                      >
                        배송완료
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            ))}
            
            {filteredOrders.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                발주 내역이 없습니다.
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* 발주 추가 모달 */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">새 발주 추가</h3>
            <div className="space-y-4">
              <div>
                <Label htmlFor="item">물품명 *</Label>
                <Input
                  id="item"
                  value={newOrder.item}
                  onChange={(e) => setNewOrder({...newOrder, item: e.target.value})}
                  placeholder="물품명을 입력하세요"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="quantity">수량 *</Label>
                  <Input
                    id="quantity"
                    type="number"
                    min="1"
                    value={newOrder.quantity}
                    onChange={(e) => setNewOrder({...newOrder, quantity: parseInt(e.target.value) || 1})}
                  />
                </div>
                <div>
                  <Label htmlFor="unit">단위</Label>
                  <Select value={newOrder.unit} onValueChange={(value) => setNewOrder({...newOrder, unit: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="개">개</SelectItem>
                      <SelectItem value="kg">kg</SelectItem>
                      <SelectItem value="L">L</SelectItem>
                      <SelectItem value="박스">박스</SelectItem>
                      <SelectItem value="세트">세트</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div>
                <Label htmlFor="order_date">발주일</Label>
                <Input
                  id="order_date"
                  type="date"
                  value={newOrder.order_date}
                  onChange={(e) => setNewOrder({...newOrder, order_date: e.target.value})}
                />
              </div>
              <div>
                <Label htmlFor="supplier">공급업체</Label>
                <Input
                  id="supplier"
                  value={newOrder.supplier}
                  onChange={(e) => setNewOrder({...newOrder, supplier: e.target.value})}
                  placeholder="공급업체명"
                />
              </div>
              <div>
                <Label htmlFor="unit_price">단가 (원)</Label>
                <Input
                  id="unit_price"
                  type="number"
                  min="0"
                  value={newOrder.unit_price}
                  onChange={(e) => setNewOrder({...newOrder, unit_price: parseInt(e.target.value) || 0})}
                  placeholder="0"
                />
              </div>
              <div>
                <Label htmlFor="detail">상세 설명</Label>
                <Textarea
                  id="detail"
                  value={newOrder.detail}
                  onChange={(e) => setNewOrder({...newOrder, detail: e.target.value})}
                  placeholder="상세 설명을 입력하세요"
                />
              </div>
              <div>
                <Label htmlFor="memo">메모</Label>
                <Textarea
                  id="memo"
                  value={newOrder.memo}
                  onChange={(e) => setNewOrder({...newOrder, memo: e.target.value})}
                  placeholder="메모를 입력하세요"
                />
              </div>
            </div>
            <div className="flex gap-2 mt-6">
              <Button onClick={handleAddOrder} className="flex-1">
                발주 추가
              </Button>
              <Button variant="outline" onClick={() => setShowAddModal(false)} className="flex-1">
                취소
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* 알림창 */}
      <NotificationPopup 
        message="새로운 발주 요청이 있습니다! 빠르게 확인해보세요." 
        delay={1000}
      />
    </div>
  );
} 
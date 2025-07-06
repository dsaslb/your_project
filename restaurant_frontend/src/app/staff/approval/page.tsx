"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Check, X, User, Clock, AlertCircle, Eye, CheckCircle, XCircle } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';

interface PendingStaff {
  id: number;
  name: string;
  position: string;
  department: string;
  email: string;
  phone: string;
  username: string;
  join_date: string;
  status: string;
  role: string;
  branch_name?: string;
  salary?: string;
  permissions?: any;
}

interface Permission {
  view: boolean;
  create?: boolean;
  edit?: boolean;
  delete?: boolean;
  approve?: boolean;
  assign_roles?: boolean;
  send?: boolean;
  backup?: boolean;
  restore?: boolean;
  settings?: boolean;
  monitoring?: boolean;
  export?: boolean;
  admin_only?: boolean;
}

export default function StaffApprovalPage() {
  const router = useRouter();
  const [pendingStaff, setPendingStaff] = useState<PendingStaff[]>([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState<number | null>(null);
  const [showRejectDialog, setShowRejectDialog] = useState(false);
  const [selectedStaff, setSelectedStaff] = useState<PendingStaff | null>(null);
  const [rejectReason, setRejectReason] = useState('');
  const [showPermissionDialog, setShowPermissionDialog] = useState(false);
  const [permissionForm, setPermissionForm] = useState({
    dashboard: { view: true, edit: false, admin_only: false },
    employee_management: { view: false, create: false, edit: false, delete: false, approve: false, assign_roles: false },
    schedule_management: { view: true, create: false, edit: false, delete: false, approve: false },
    order_management: { view: true, create: false, edit: false, delete: false, approve: false },
    inventory_management: { view: true, create: false, edit: false, delete: false },
    notification_management: { view: true, send: false, delete: false },
    system_management: { view: false, backup: false, restore: false, settings: false, monitoring: false },
    reports: { view: false, export: false, admin_only: false },
  });

  // 미승인 직원 목록 로드
  const fetchPendingStaff = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:5000/api/staff/pending', {
        credentials: 'include',
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setPendingStaff(data.staff || []);
        } else {
          console.error('미승인 직원 목록 로드 실패:', data.error);
        }
      } else {
        console.error('미승인 직원 목록 로드 실패:', response.status);
      }
    } catch (error) {
      console.error('미승인 직원 목록 로드 오류:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPendingStaff();
  }, []);

  // 권한 설정 다이얼로그 열기
  const openPermissionDialog = (staff: PendingStaff) => {
    setSelectedStaff(staff);
    if (staff.permissions) {
      setPermissionForm(staff.permissions);
    }
    setShowPermissionDialog(true);
  };

  // 권한 설정 저장
  const handlePermissionSave = async () => {
    if (!selectedStaff) return;

    try {
      setProcessing(selectedStaff.id);
      const response = await fetch(`http://localhost:5000/api/staff/${selectedStaff.id}/permissions`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ permissions: permissionForm }),
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          alert('권한이 설정되었습니다!');
          setShowPermissionDialog(false);
          fetchPendingStaff(); // 목록 새로고침
        } else {
          alert(`권한 설정 실패: ${data.error}`);
        }
      } else {
        alert('권한 설정 중 오류가 발생했습니다.');
      }
    } catch (error) {
      console.error('권한 설정 오류:', error);
      alert('권한 설정 중 오류가 발생했습니다.');
    } finally {
      setProcessing(null);
    }
  };

  // 직원 승인 (권한 포함)
  const handleApprove = async (staffId: number) => {
    try {
      setProcessing(staffId);
      const response = await fetch(`http://localhost:5000/api/staff/${staffId}/approve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ permissions: permissionForm }),
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          alert('직원이 승인되었습니다!');
          fetchPendingStaff(); // 목록 새로고침
          // 직원 목록/스케줄 새로고침 이벤트 발생
          window.dispatchEvent(new CustomEvent('staffDataUpdated'));
        } else {
          alert(`승인 실패: ${data.error}`);
        }
      } else {
        alert('승인 처리 중 오류가 발생했습니다.');
      }
    } catch (error) {
      console.error('승인 처리 오류:', error);
      alert('승인 처리 중 오류가 발생했습니다.');
    } finally {
      setProcessing(null);
    }
  };

  // 직원 거절
  const handleReject = async () => {
    if (!selectedStaff) return;

    try {
      setProcessing(selectedStaff.id);
      const response = await fetch(`http://localhost:5000/api/staff/${selectedStaff.id}/reject`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ reason: rejectReason }),
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          alert('직원이 거절되었습니다!');
          setShowRejectDialog(false);
          setRejectReason('');
          setSelectedStaff(null);
          fetchPendingStaff(); // 목록 새로고침
        } else {
          alert(`거절 실패: ${data.error}`);
        }
      } else {
        alert('거절 처리 중 오류가 발생했습니다.');
      }
    } catch (error) {
      console.error('거절 처리 오류:', error);
      alert('거절 처리 중 오류가 발생했습니다.');
    } finally {
      setProcessing(null);
    }
  };

  // 거절 다이얼로그 열기
  const openRejectDialog = (staff: PendingStaff) => {
    setSelectedStaff(staff);
    setShowRejectDialog(true);
  };

  // 상태별 배지 색상
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">대기중</Badge>;
      case 'active':
        return <Badge variant="default" className="bg-green-100 text-green-800">승인됨</Badge>;
      case 'rejected':
        return <Badge variant="destructive">거절됨</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-lg">미승인 직원 목록을 불러오는 중...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-4">
            <Button
              variant="outline"
              onClick={() => router.back()}
              className="flex items-center gap-2"
            >
              ← 뒤로가기
            </Button>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">직원 승인 관리</h1>
          </div>
          <p className="text-gray-600 dark:text-gray-400">
            대기중인 직원들의 승인/거절을 관리하세요.
          </p>
        </div>

        {/* 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-yellow-100 rounded-full">
                  <Clock className="h-6 w-6 text-yellow-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">대기중</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {pendingStaff.filter(s => s.status === 'pending').length}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-green-100 rounded-full">
                  <CheckCircle className="h-6 w-6 text-green-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">승인됨</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {pendingStaff.filter(s => s.status === 'active').length}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-red-100 rounded-full">
                  <XCircle className="h-6 w-6 text-red-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">거절됨</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {pendingStaff.filter(s => s.status === 'rejected').length}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-blue-100 rounded-full">
                  <User className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">전체</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {pendingStaff.length}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 직원 목록 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5" />
              미승인 직원 목록
            </CardTitle>
            <CardDescription>
              승인 대기중인 직원들을 확인하고 승인 또는 거절하세요.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {pendingStaff.length === 0 ? (
              <div className="text-center py-12">
                <User className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  대기중인 직원이 없습니다
                </h3>
                <p className="text-gray-500 dark:text-gray-400">
                  모든 직원이 처리되었습니다.
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 dark:bg-gray-700">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        직원
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        부서/직책
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        연락처
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        계정 정보
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        상태
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        신청일
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        작업
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                    {pendingStaff.map((staff) => (
                      <tr key={staff.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="w-10 h-10 bg-gray-300 dark:bg-gray-600 rounded-full flex items-center justify-center">
                              <User className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                            </div>
                            <div className="ml-4">
                              <div className="text-sm font-medium text-gray-900 dark:text-white">
                                {staff.name}
                              </div>
                              <div className="text-sm text-gray-500 dark:text-gray-400">
                                {staff.role}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900 dark:text-white">{staff.department}</div>
                          <div className="text-sm text-gray-500 dark:text-gray-400">{staff.position}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900 dark:text-white">{staff.phone}</div>
                          <div className="text-sm text-gray-500 dark:text-gray-400">{staff.email}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900 dark:text-white">ID: {staff.username}</div>
                          <div className="text-sm text-gray-500 dark:text-gray-400">계정 생성됨</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {getStatusBadge(staff.status)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                          {staff.join_date}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <div className="flex items-center justify-end space-x-2">
                            {staff.status === 'pending' && (
                              <>
                                <Button
                                  size="sm"
                                  onClick={() => openPermissionDialog(staff)}
                                  disabled={processing === staff.id}
                                  className="bg-blue-600 hover:bg-blue-700 text-white"
                                >
                                  <Eye className="h-4 w-4 mr-1" />
                                  권한설정
                                </Button>
                                <Button
                                  size="sm"
                                  onClick={() => handleApprove(staff.id)}
                                  disabled={processing === staff.id}
                                  className="bg-green-600 hover:bg-green-700 text-white"
                                >
                                  <Check className="h-4 w-4 mr-1" />
                                  {processing === staff.id ? '처리중...' : '승인'}
                                </Button>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => openRejectDialog(staff)}
                                  disabled={processing === staff.id}
                                  className="border-red-300 text-red-600 hover:bg-red-50"
                                >
                                  <X className="h-4 w-4 mr-1" />
                                  거절
                                </Button>
                              </>
                            )}
                            {staff.status !== 'pending' && (
                              <span className="text-gray-500">
                                {staff.status === 'active' ? '승인됨' : '거절됨'}
                              </span>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* 거절 사유 입력 다이얼로그 */}
      <Dialog open={showRejectDialog} onOpenChange={setShowRejectDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>직원 거절</DialogTitle>
            <DialogDescription>
              {selectedStaff?.name} 직원을 거절하시겠습니까? 거절 사유를 입력해주세요.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="reason">거절 사유</Label>
              <Textarea
                id="reason"
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                placeholder="거절 사유를 입력하세요..."
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setShowRejectDialog(false);
                setRejectReason('');
                setSelectedStaff(null);
              }}
            >
              취소
            </Button>
            <Button
              onClick={handleReject}
              disabled={processing === selectedStaff?.id}
              className="bg-red-600 hover:bg-red-700"
            >
              {processing === selectedStaff?.id ? '처리중...' : '거절'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 권한 설정 다이얼로그 */}
      <Dialog open={showPermissionDialog} onOpenChange={setShowPermissionDialog}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>권한 설정 - {selectedStaff?.name}</DialogTitle>
            <DialogDescription>
              {selectedStaff?.name} 직원의 권한을 설정하세요.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-6">
            {/* 대시보드 권한 */}
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold mb-3">대시보드</h3>
              <div className="space-y-2">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={permissionForm.dashboard.view}
                    onChange={(e) => setPermissionForm({
                      ...permissionForm,
                      dashboard: { ...permissionForm.dashboard, view: e.target.checked }
                    })}
                  />
                  <span>대시보드 보기</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={permissionForm.dashboard.edit}
                    onChange={(e) => setPermissionForm({
                      ...permissionForm,
                      dashboard: { ...permissionForm.dashboard, edit: e.target.checked }
                    })}
                  />
                  <span>대시보드 편집</span>
                </label>
              </div>
            </div>

            {/* 직원 관리 권한 */}
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold mb-3">직원 관리</h3>
              <div className="space-y-2">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={permissionForm.employee_management.view}
                    onChange={(e) => setPermissionForm({
                      ...permissionForm,
                      employee_management: { ...permissionForm.employee_management, view: e.target.checked }
                    })}
                  />
                  <span>직원 목록 보기</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={permissionForm.employee_management.create}
                    onChange={(e) => setPermissionForm({
                      ...permissionForm,
                      employee_management: { ...permissionForm.employee_management, create: e.target.checked }
                    })}
                  />
                  <span>직원 등록</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={permissionForm.employee_management.edit}
                    onChange={(e) => setPermissionForm({
                      ...permissionForm,
                      employee_management: { ...permissionForm.employee_management, edit: e.target.checked }
                    })}
                  />
                  <span>직원 정보 수정</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={permissionForm.employee_management.approve}
                    onChange={(e) => setPermissionForm({
                      ...permissionForm,
                      employee_management: { ...permissionForm.employee_management, approve: e.target.checked }
                    })}
                  />
                  <span>직원 승인</span>
                </label>
              </div>
            </div>

            {/* 스케줄 관리 권한 */}
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold mb-3">스케줄 관리</h3>
              <div className="space-y-2">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={permissionForm.schedule_management.view}
                    onChange={(e) => setPermissionForm({
                      ...permissionForm,
                      schedule_management: { ...permissionForm.schedule_management, view: e.target.checked }
                    })}
                  />
                  <span>스케줄 보기</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={permissionForm.schedule_management.create}
                    onChange={(e) => setPermissionForm({
                      ...permissionForm,
                      schedule_management: { ...permissionForm.schedule_management, create: e.target.checked }
                    })}
                  />
                  <span>스케줄 생성</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={permissionForm.schedule_management.edit}
                    onChange={(e) => setPermissionForm({
                      ...permissionForm,
                      schedule_management: { ...permissionForm.schedule_management, edit: e.target.checked }
                    })}
                  />
                  <span>스케줄 수정</span>
                </label>
              </div>
            </div>

            {/* 주문 관리 권한 */}
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold mb-3">주문 관리</h3>
              <div className="space-y-2">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={permissionForm.order_management.view}
                    onChange={(e) => setPermissionForm({
                      ...permissionForm,
                      order_management: { ...permissionForm.order_management, view: e.target.checked }
                    })}
                  />
                  <span>주문 보기</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={permissionForm.order_management.create}
                    onChange={(e) => setPermissionForm({
                      ...permissionForm,
                      order_management: { ...permissionForm.order_management, create: e.target.checked }
                    })}
                  />
                  <span>주문 생성</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={permissionForm.order_management.edit}
                    onChange={(e) => setPermissionForm({
                      ...permissionForm,
                      order_management: { ...permissionForm.order_management, edit: e.target.checked }
                    })}
                  />
                  <span>주문 수정</span>
                </label>
              </div>
            </div>

            {/* 재고 관리 권한 */}
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold mb-3">재고 관리</h3>
              <div className="space-y-2">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={permissionForm.inventory_management.view}
                    onChange={(e) => setPermissionForm({
                      ...permissionForm,
                      inventory_management: { ...permissionForm.inventory_management, view: e.target.checked }
                    })}
                  />
                  <span>재고 보기</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={permissionForm.inventory_management.create}
                    onChange={(e) => setPermissionForm({
                      ...permissionForm,
                      inventory_management: { ...permissionForm.inventory_management, create: e.target.checked }
                    })}
                  />
                  <span>재고 등록</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={permissionForm.inventory_management.edit}
                    onChange={(e) => setPermissionForm({
                      ...permissionForm,
                      inventory_management: { ...permissionForm.inventory_management, edit: e.target.checked }
                    })}
                  />
                  <span>재고 수정</span>
                </label>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowPermissionDialog(false)}
            >
              취소
            </Button>
            <Button
              onClick={handlePermissionSave}
              disabled={processing === selectedStaff?.id}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {processing === selectedStaff?.id ? '저장중...' : '권한 저장'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
} 
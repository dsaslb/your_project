"use client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { 
  Building2, 
  MapPin, 
  Phone, 
  Mail,
  Users,
  DollarSign,
  Plus,
  Edit,
  Trash2,
  Search,
  Filter,
  X
} from "lucide-react";
import { useEffect, useState } from "react";
import { Dialog } from "@/components/ui/dialog";

export default function BranchManagement() {
  const [branches, setBranches] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [editBranch, setEditBranch] = useState<any>(null);
  const [form, setForm] = useState<any>({ name: '', address: '', phone: '', email: '', manager: '', employees: 0, status: 'active', revenue: '', openDate: '' });
  const [submitLoading, setSubmitLoading] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // 목록 fetch
  const fetchBranches = () => {
    setLoading(true);
    setError(null);
    fetch("/api/branches")
      .then(res => res.json())
      .then(data => setBranches(data.branches || []))
      .catch(() => setError("매장 목록을 불러오지 못했습니다."))
      .finally(() => setLoading(false));
  };
  useEffect(fetchBranches, []);

  // 생성/수정 핸들러
  const handleSubmit = async (e: any) => {
    e.preventDefault();
    setSubmitLoading(true);
    setSubmitError(null);
    try {
      const method = editBranch ? 'PUT' : 'POST';
      const url = editBranch ? `/api/branches/${editBranch.id}` : '/api/branches';
      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      if (!res.ok) throw new Error('저장 실패');
      setModalOpen(false);
      setEditBranch(null);
      setForm({ name: '', address: '', phone: '', email: '', manager: '', employees: 0, status: 'active', revenue: '', openDate: '' });
      fetchBranches();
    } catch (err) {
      setSubmitError('저장에 실패했습니다.');
    } finally {
      setSubmitLoading(false);
    }
  };

  // 삭제 핸들러
  const handleDelete = async (id: number) => {
    if (!window.confirm('정말 삭제하시겠습니까?')) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/branches/${id}`, { method: 'DELETE' });
      if (!res.ok) throw new Error('삭제 실패');
      fetchBranches();
    } catch (err) {
      setError('삭제에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 폼 열기/닫기
  const openCreate = () => {
    setEditBranch(null);
    setForm({ name: '', address: '', phone: '', email: '', manager: '', employees: 0, status: 'active', revenue: '', openDate: '' });
    setModalOpen(true);
  };
  const openEdit = (branch: any) => {
    setEditBranch(branch);
    setForm({ ...branch });
    setModalOpen(true);
  };
  const closeModal = () => {
    setModalOpen(false);
    setEditBranch(null);
    setForm({ name: '', address: '', phone: '', email: '', manager: '', employees: 0, status: 'active', revenue: '', openDate: '' });
    setSubmitError(null);
  };

  const stats = {
    totalBranches: branches.length,
    activeBranches: branches.filter(b => b.status === "active").length,
    totalEmployees: branches.reduce((sum, b) => sum + (b.employees || 0), 0),
    totalRevenue: branches.reduce((sum, b) => sum + (typeof b.revenue === 'string' ? parseInt(b.revenue.replace(/[₩,]/g, '')) : (b.revenue || 0)), 0)
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "active":
        return <Badge variant="default" className="bg-green-600">운영 중</Badge>;
      case "maintenance":
        return <Badge variant="secondary">점검 중</Badge>;
      case "closed":
        return <Badge variant="destructive">폐점</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            브랜치 관리
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            매장 정보 및 운영 현황 관리
          </p>
        </div>
        <Button className="flex items-center space-x-2" onClick={openCreate}>
          <Plus className="h-4 w-4" />
          <span>새 매장 추가</span>
        </Button>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">전체 매장</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalBranches}</div>
            <p className="text-xs text-muted-foreground">
              등록된 매장 수
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">운영 중</CardTitle>
            <Building2 className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.activeBranches}</div>
            <p className="text-xs text-muted-foreground">
              정상 운영 매장
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">전체 직원</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalEmployees}</div>
            <p className="text-xs text-muted-foreground">
              총 직원 수
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 매출</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">₩{stats.totalRevenue.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              전체 매장 매출
            </p>
          </CardContent>
        </Card>
      </div>

      {/* 검색 및 필터 */}
      <Card>
        <CardHeader>
          <CardTitle>매장 검색</CardTitle>
          <CardDescription>
            매장명, 주소, 매니저로 검색하세요
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex space-x-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="매장 검색..."
                  className="pl-10"
                />
              </div>
            </div>
            <Button variant="outline" className="flex items-center space-x-2">
              <Filter className="h-4 w-4" />
              <span>필터</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 매장 목록 */}
      <Card>
        <CardHeader>
          <CardTitle>매장 목록</CardTitle>
          <CardDescription>
            등록된 모든 매장 정보
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading && <div className="text-sm text-gray-500 mb-2">로딩 중...</div>}
          {error && <div className="text-sm text-red-500 mb-2">{error}</div>}
          <div className="space-y-4">
            {branches.map((branch) => (
              <div key={branch.id} className="flex items-center justify-between p-6 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                    <Building2 className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                  </div>
                  <div>
                    <h3 className="font-medium text-lg">{branch.name}</h3>
                    <div className="flex items-center space-x-4 text-sm text-muted-foreground mt-1">
                      <div className="flex items-center space-x-1">
                        <MapPin className="h-3 w-3" />
                        <span>{branch.address}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Phone className="h-3 w-3" />
                        <span>{branch.phone}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Mail className="h-3 w-3" />
                        <span>{branch.email}</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-6">
                  <div className="text-right">
                    <p className="text-sm font-medium">매니저: {branch.manager}</p>
                    <p className="text-sm text-muted-foreground">{branch.employees}명 직원</p>
                    <p className="text-sm text-muted-foreground">개점일: {branch.openDate}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">{branch.revenue}</p>
                    <p className="text-sm text-muted-foreground">월 매출</p>
                  </div>
                  {getStatusBadge(branch.status)}
                  <div className="flex items-center space-x-2">
                    <Button variant="outline" size="sm" onClick={() => openEdit(branch)}>
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => handleDelete(branch.id)}>
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 매장 생성/수정 모달 */}
      <Dialog open={modalOpen} onOpenChange={closeModal}>
        <div className={`fixed inset-0 z-50 flex items-center justify-center ${modalOpen ? '' : 'hidden'}`}> 
          <div className="bg-white rounded-xl shadow-2xl p-6 min-w-[320px] max-w-md relative animate-fade-in">
            <button className="absolute top-2 right-2 text-gray-400 hover:text-gray-700 text-2xl" onClick={closeModal} aria-label="닫기"><X /></button>
            <h2 className="text-lg font-bold mb-3 text-indigo-700">{editBranch ? '매장 수정' : '새 매장 추가'}</h2>
            <form onSubmit={handleSubmit} className="space-y-3">
              <input className="w-full border rounded px-2 py-1" placeholder="매장명" value={form.name} onChange={e => setForm((f: any) => ({ ...f, name: e.target.value }))} required />
              <input className="w-full border rounded px-2 py-1" placeholder="주소" value={form.address} onChange={e => setForm((f: any) => ({ ...f, address: e.target.value }))} required />
              <input className="w-full border rounded px-2 py-1" placeholder="전화번호" value={form.phone} onChange={e => setForm((f: any) => ({ ...f, phone: e.target.value }))} required />
              <input className="w-full border rounded px-2 py-1" placeholder="이메일" value={form.email} onChange={e => setForm((f: any) => ({ ...f, email: e.target.value }))} />
              <input className="w-full border rounded px-2 py-1" placeholder="매니저" value={form.manager} onChange={e => setForm((f: any) => ({ ...f, manager: e.target.value }))} />
              <input className="w-full border rounded px-2 py-1" type="number" placeholder="직원 수" value={form.employees} onChange={e => setForm((f: any) => ({ ...f, employees: Number(e.target.value) }))} />
              <input className="w-full border rounded px-2 py-1" placeholder="월 매출(숫자만)" value={form.revenue} onChange={e => setForm((f: any) => ({ ...f, revenue: e.target.value }))} />
              <input className="w-full border rounded px-2 py-1" placeholder="개점일(YYYY-MM-DD)" value={form.openDate} onChange={e => setForm((f: any) => ({ ...f, openDate: e.target.value }))} />
              <select className="w-full border rounded px-2 py-1" value={form.status} onChange={e => setForm((f: any) => ({ ...f, status: e.target.value }))}>
                <option value="active">운영 중</option>
                <option value="maintenance">점검 중</option>
                <option value="closed">폐점</option>
              </select>
              {submitError && <div className="text-red-500 text-sm">{submitError}</div>}
              <button type="submit" className="w-full bg-blue-600 text-white rounded py-2 font-semibold mt-2" disabled={submitLoading}>{submitLoading ? '저장 중...' : (editBranch ? '수정' : '등록')}</button>
            </form>
          </div>
        </div>
      </Dialog>

      {/* 매장별 상세 통계 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>매장별 매출 현황</CardTitle>
            <CardDescription>
              각 매장의 월별 매출 비교
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {branches.map((branch) => (
                <div key={branch.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div>
                    <h3 className="font-medium">{branch.name}</h3>
                    <p className="text-sm text-muted-foreground">{branch.manager} 매니저</p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">{branch.revenue}</p>
                    <div className="w-32 bg-gray-200 rounded-full h-2 mt-1">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{width: `${((typeof branch.revenue === 'string' ? parseInt(branch.revenue.replace(/[₩,]/g, '')) : (branch.revenue || 0)) / 350000000) * 100}%`}}
                      ></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>매장별 직원 현황</CardTitle>
            <CardDescription>
              각 매장의 직원 수 및 구성
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {branches.map((branch) => (
                <div key={branch.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div>
                    <h3 className="font-medium">{branch.name}</h3>
                    <p className="text-sm text-muted-foreground">총 {branch.employees}명</p>
                  </div>
                  <div className="text-right">
                    <Badge variant="outline">{branch.employees}명</Badge>
                    <div className="w-32 bg-gray-200 rounded-full h-2 mt-1">
                      <div 
                        className="bg-green-600 h-2 rounded-full" 
                        style={{width: `${(branch.employees / 28) * 100}%`}}
                      ></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 
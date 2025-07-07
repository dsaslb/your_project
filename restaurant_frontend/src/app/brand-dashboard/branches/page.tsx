"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  Building2,
  Users,
  MapPin,
  Phone,
  Mail,
  Plus,
  Edit,
  Trash2,
  Eye,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
} from "lucide-react";
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogClose,
  DialogDescription,
} from "@/components/ui/dialog";

interface Branch {
  id: number;
  name: string;
  address: string;
  phone: string;
  email: string;
  manager: string;
  status: string;
  employees: number;
  sales: number;
  orders: number;
}

export default function BranchesPage() {
  const router = useRouter();
  const [branches, setBranches] = useState<Branch[]>([]);
  const [isLoaded, setIsLoaded] = useState(false);
  const [openAddModal, setOpenAddModal] = useState(false);
  const [openEditModal, setOpenEditModal] = useState(false);
  const [selectedBranch, setSelectedBranch] = useState<Branch | null>(null);

  // 새 매장 폼 데이터
  const [newBranch, setNewBranch] = useState({
    name: "",
    address: "",
    phone: "",
    email: "",
    manager: "",
  });

  useEffect(() => {
    loadBranches();
  }, []);

  const loadBranches = async () => {
    // 실제로는 API 호출
    const mockBranches: Branch[] = [
      {
        id: 1,
        name: "강남점",
        address: "서울시 강남구 테헤란로 123",
        phone: "02-1234-5678",
        email: "gangnam@restaurant.com",
        manager: "김강남",
        status: "운영중",
        employees: 12,
        sales: 8500000,
        orders: 156,
      },
      {
        id: 2,
        name: "홍대점",
        address: "서울시 마포구 홍대로 456",
        phone: "02-2345-6789",
        email: "hongdae@restaurant.com",
        manager: "이홍대",
        status: "운영중",
        employees: 10,
        sales: 7200000,
        orders: 134,
      },
      {
        id: 3,
        name: "부산점",
        address: "부산시 해운대구 해운대로 789",
        phone: "051-3456-7890",
        email: "busan@restaurant.com",
        manager: "박부산",
        status: "운영중",
        employees: 8,
        sales: 6800000,
        orders: 98,
      },
      {
        id: 4,
        name: "대구점",
        address: "대구시 중구 동성로 321",
        phone: "053-4567-8901",
        email: "daegu@restaurant.com",
        manager: "최대구",
        status: "운영중",
        employees: 9,
        sales: 6100000,
        orders: 87,
      },
      {
        id: 5,
        name: "인천점",
        address: "인천시 연수구 송도대로 654",
        phone: "032-5678-9012",
        email: "incheon@restaurant.com",
        manager: "정인천",
        status: "운영중",
        employees: 11,
        sales: 7800000,
        orders: 142,
      },
    ];

    setBranches(mockBranches);
    setIsLoaded(true);
  };

  const handleAddBranch = () => {
    if (newBranch.name && newBranch.address && newBranch.phone) {
      const branch: Branch = {
        id: branches.length + 1,
        ...newBranch,
        status: "운영중",
        employees: 0,
        sales: 0,
        orders: 0,
      };
      setBranches([...branches, branch]);
      setNewBranch({ name: "", address: "", phone: "", email: "", manager: "" });
      setOpenAddModal(false);
    }
  };

  const handleEditBranch = (branch: Branch) => {
    setSelectedBranch(branch);
    setOpenEditModal(true);
  };

  const handleDeleteBranch = (id: number) => {
    if (confirm("정말로 이 매장을 삭제하시겠습니까?")) {
      setBranches(branches.filter(branch => branch.id !== id));
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "운영중":
        return "text-green-600 bg-green-100";
      case "점검중":
        return "text-yellow-600 bg-yellow-100";
      case "휴무":
        return "text-red-600 bg-red-100";
      default:
        return "text-gray-600 bg-gray-100";
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ko-KR').format(amount);
  };

  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">매장 정보 로딩 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      {/* 헤더 */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">매장 관리</h1>
            <p className="text-gray-600 mt-2">전체 매장 정보 및 상태를 관리합니다.</p>
          </div>
          <Dialog open={openAddModal} onOpenChange={setOpenAddModal}>
            <DialogTrigger asChild>
              <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors">
                <Plus className="h-4 w-4" />
                새 매장 추가
              </button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>새 매장 추가</DialogTitle>
                <DialogDescription>
                  매장의 상세 정보를 입력할 수 있습니다.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    매장명
                  </label>
                  <input
                    type="text"
                    value={newBranch.name}
                    onChange={(e) => setNewBranch({...newBranch, name: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="매장명을 입력하세요"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    주소
                  </label>
                  <input
                    type="text"
                    value={newBranch.address}
                    onChange={(e) => setNewBranch({...newBranch, address: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="주소를 입력하세요"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    전화번호
                  </label>
                  <input
                    type="tel"
                    value={newBranch.phone}
                    onChange={(e) => setNewBranch({...newBranch, phone: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="전화번호를 입력하세요"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    이메일
                  </label>
                  <input
                    type="email"
                    value={newBranch.email}
                    onChange={(e) => setNewBranch({...newBranch, email: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="이메일을 입력하세요"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    매장 관리자
                  </label>
                  <input
                    type="text"
                    value={newBranch.manager}
                    onChange={(e) => setNewBranch({...newBranch, manager: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="매장 관리자명을 입력하세요"
                  />
                </div>
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <DialogClose asChild>
                  <button className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors">
                    취소
                  </button>
                </DialogClose>
                <button
                  onClick={handleAddBranch}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
                >
                  추가
                </button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">전체 매장</p>
              <p className="text-2xl font-bold text-gray-900">{branches.length}개</p>
            </div>
            <Building2 className="h-8 w-8 text-blue-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">운영중</p>
              <p className="text-2xl font-bold text-gray-900">
                {branches.filter(b => b.status === "운영중").length}개
              </p>
            </div>
            <CheckCircle className="h-8 w-8 text-green-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">총 직원</p>
              <p className="text-2xl font-bold text-gray-900">
                {branches.reduce((sum, b) => sum + b.employees, 0)}명
              </p>
            </div>
            <Users className="h-8 w-8 text-purple-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">총 매출</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(branches.reduce((sum, b) => sum + b.sales, 0))}원
              </p>
            </div>
            <TrendingUp className="h-8 w-8 text-green-600" />
          </div>
        </div>
      </div>

      {/* 매장 목록 */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">매장 목록</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  매장 정보
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  연락처
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  상태
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  직원
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  매출
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  액션
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {branches.map((branch) => (
                <tr key={branch.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div>
                      <div className="flex items-center">
                        <Building2 className="h-5 w-5 text-gray-400 mr-3" />
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {branch.name}
                          </div>
                          <div className="text-sm text-gray-500 flex items-center">
                            <MapPin className="h-3 w-3 mr-1" />
                            {branch.address}
                          </div>
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900">{branch.manager}</div>
                    <div className="text-sm text-gray-500 flex items-center">
                      <Phone className="h-3 w-3 mr-1" />
                      {branch.phone}
                    </div>
                    <div className="text-sm text-gray-500 flex items-center">
                      <Mail className="h-3 w-3 mr-1" />
                      {branch.email}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(branch.status)}`}>
                      {branch.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {branch.employees}명
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm font-medium text-gray-900">
                      {formatCurrency(branch.sales)}원
                    </div>
                    <div className="text-sm text-gray-500">
                      {branch.orders}건
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => router.push(`/brand-dashboard/branches/${branch.id}`)}
                        className="text-blue-600 hover:text-blue-900 p-1"
                        title="상세보기"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleEditBranch(branch)}
                        className="text-green-600 hover:text-green-900 p-1"
                        title="수정"
                      >
                        <Edit className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleDeleteBranch(branch.id)}
                        className="text-red-600 hover:text-red-900 p-1"
                        title="삭제"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
} 
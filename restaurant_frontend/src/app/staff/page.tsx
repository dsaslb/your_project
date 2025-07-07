"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Plus, Search, Filter, MoreHorizontal, Edit, Trash2, User, Phone, Mail, Calendar, MapPin, Download, Eye, AlertTriangle, CheckCircle, Clock, FileText, Shield, X, Building, CalendarDays, DollarSign, Award, Clock as ClockIcon, UserX, UserCheck, AlertCircle } from "lucide-react";
import NotificationPopup from "@/components/NotificationPopup";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { useStaffStore, type StaffMember } from '@/store';

export default function StaffPage() {
  const router = useRouter();
  const [selectedStaff, setSelectedStaff] = useState<StaffMember | null>(null);
  const [showStaffModal, setShowStaffModal] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [selectedFilter, setSelectedFilter] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [expiringDocuments, setExpiringDocuments] = useState<any[]>([]);
  const [showExpiringModal, setShowExpiringModal] = useState(false);
  
  // Store에서 데이터 가져오기
  const { 
    staffMembers, 
    loading, 
    error,
    fetchStaffData, 
    fetchExpiringDocuments, 
    refreshAllData,
    updateStaffStatus: updateStaffStatusStore,
    deleteStaff: deleteStaffStore
  } = useStaffStore();

  useEffect(() => {
    setIsLoaded(true);
    fetchStaffData('management');
    fetchExpiringDocuments();
  }, []);

  const togglePlay = () => {
    setIsPlaying(!isPlaying);
  };

  // 직원 등록/수정/삭제 후 데이터 새로고침 함수
  const refreshStaffData = async () => {
    console.log('직원 데이터 새로고침 중...');
    await refreshAllData();
  };

  // 직원 상태 변경 함수
  const updateStaffStatus = async (staffId: number, newStatus: string) => {
    try {
      const response = await fetch(`http://localhost:5000/api/staff/${staffId}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ status: newStatus })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          console.log(`직원 ${staffId} 상태 변경 성공: ${newStatus}`);
          updateStaffStatusStore(staffId, newStatus);
          await refreshStaffData();
        } else {
          console.error('상태 변경 실패:', data.error);
        }
      } else {
        console.error('상태 변경 실패:', response.status);
      }
    } catch (error) {
      console.error('상태 변경 오류:', error);
    }
  };

  // 직원 삭제 함수
  const deleteStaff = async (staffId: number) => {
    if (!confirm('정말로 이 직원을 삭제하시겠습니까?')) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:5000/api/staff/${staffId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          console.log(`직원 ${staffId} 삭제 성공`);
          deleteStaffStore(staffId);
          await refreshStaffData();
        } else {
          console.error('삭제 실패:', data.error);
        }
      } else {
        console.error('삭제 실패:', response.status);
      }
    } catch (error) {
      console.error('삭제 오류:', error);
    }
  };

  // 만료 임박 서류 조회 (로컬 상태용)
  const fetchExpiringDocumentsLocal = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/staff/expiring-documents', {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setExpiringDocuments(data.documents || []);
        }
      }
    } catch (error) {
      console.error('만료 임박 서류 조회 실패:', error);
    }
  };

  // 보건증 만료 알림 발송
  const sendHealthCertificateNotification = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/staff/health-certificate/notify', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          alert(data.message);
          fetchExpiringDocumentsLocal(); // 목록 새로고침
        }
      }
    } catch (error) {
      console.error('보건증 알림 발송 실패:', error);
      alert('알림 발송에 실패했습니다.');
    }
  };

  // 더미 데이터 (API 실패 시 사용)
  const getDummyData = (): StaffMember[] => [
    {
      id: 1,
      name: '김철수',
      position: '주방장',
      department: '주방',
      email: 'kim@restaurant.com',
      phone: '010-1234-5678',
      join_date: '2023-01-15',
      status: 'active',
      contracts: [
        {
          id: 1,
          contract_number: 'CT-2023-001',
          start_date: '2023-01-15',
          expiry_date: '2024-12-31',
          renewal_date: '2024-12-15',
          contract_type: '정규직',
          is_expiring_soon: true,
          is_expired: false,
          days_until_expiry: 25,
          file_path: '/documents/contract1.pdf',
          file_name: '김철수_계약서.pdf'
        }
      ],
      health_certificates: [
        {
          id: 1,
          certificate_number: 'HC-2023-001',
          issue_date: '2023-01-10',
          expiry_date: '2024-11-15',
          renewal_date: '2024-11-01',
          issuing_authority: '서울시보건소',
          certificate_type: '식품위생교육',
          is_expiring_soon: true,
          is_expired: false,
          days_until_expiry: 15,
          file_path: '/documents/health1.pdf',
          file_name: '김철수_보건증.pdf'
        }
      ]
    },
    {
      id: 2,
      name: '이영희',
      position: '서버',
      department: '홀',
      email: 'lee@restaurant.com',
      phone: '010-2345-6789',
      join_date: '2023-03-20',
      status: 'active',
      contracts: [
        {
          id: 2,
          contract_number: 'CT-2023-002',
          start_date: '2023-03-20',
          expiry_date: '2025-03-15',
          renewal_date: '2025-03-01',
          contract_type: '정규직',
          is_expiring_soon: false,
          is_expired: false,
          days_until_expiry: 120,
          file_path: '/documents/contract2.pdf',
          file_name: '이영희_계약서.pdf'
        }
      ],
      health_certificates: []
    }
  ];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge className="bg-green-100 text-green-800">재직중</Badge>;
      case 'inactive':
        return <Badge className="bg-red-100 text-red-800">퇴사</Badge>;
      case 'pending':
        return <Badge className="bg-yellow-100 text-yellow-800">대기중</Badge>;
      default:
        return <Badge variant="secondary">알 수 없음</Badge>;
    }
  };

  const getExpiryStatus = (isExpiringSoon: boolean, isExpired: boolean, daysUntilExpiry: number) => {
    if (isExpired) {
      return <Badge className="bg-red-100 text-red-800">만료됨</Badge>;
    } else if (isExpiringSoon) {
      return <Badge className="bg-orange-100 text-orange-800">만료 임박 ({daysUntilExpiry}일)</Badge>;
    } else {
      return <Badge className="bg-green-100 text-green-800">유효</Badge>;
    }
  };

  const handleDownload = async (documentId: number, documentType: string, fileName: string) => {
    try {
      const response = await fetch(`/api/staff/documents/${documentId}/download/${documentType}`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        alert('파일 다운로드에 실패했습니다.');
      }
    } catch (error) {
      console.error('다운로드 오류:', error);
      alert('파일 다운로드에 실패했습니다.');
    }
  };

  const filteredStaff = staffMembers.filter(staff => {
    const matchesSearch = staff.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         staff.position.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         staff.department.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = selectedFilter === 'all' || staff.status === selectedFilter;
    return matchesSearch && matchesFilter;
  });

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-lg">로딩 중...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">직원 관리</h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            직원 정보를 관리하고 계약서/보건증 현황을 확인하세요.
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
                <User className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">전체 직원</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{staffMembers.length}명</p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg">
                <User className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">근무중</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {staffMembers.filter(s => s.status === "active").length}명
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 dark:bg-yellow-900/20 rounded-lg">
                <AlertTriangle className="h-6 w-6 text-yellow-600 dark:text-yellow-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">계약서 만료 임박</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {staffMembers.filter(s => s.contracts.some(c => c.is_expiring_soon || c.is_expired)).length}명
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-red-100 dark:bg-red-900/20 rounded-lg">
                <Shield className="h-6 w-6 text-red-600 dark:text-red-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">보건증 만료 임박</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {staffMembers.filter(s => s.health_certificates.some(c => c.is_expiring_soon || c.is_expired)).length}명
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6">
          <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
            <div className="flex flex-col sm:flex-row gap-4 flex-1">
              {/* Search */}
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="직원 검색..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>

              {/* Filter */}
              <select 
                value={selectedFilter}
                onChange={(e) => setSelectedFilter(e.target.value)}
                className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="all">전체</option>
                <option value="active">재직중</option>
                <option value="inactive">퇴사</option>
                <option value="pending">대기중</option>
              </select>
            </div>

            {/* Add Button */}
            <div className="flex gap-2">
              <button 
                onClick={() => router.push('/staff/approval')}
                className="bg-yellow-600 text-white px-4 py-2 rounded-lg hover:bg-yellow-700 transition-colors flex items-center gap-2"
              >
                <Clock className="h-4 w-4" />
                승인 관리
              </button>
              <button 
                onClick={() => router.push('/staff/contract')}
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
              >
                <FileText className="h-4 w-4" />
                계약서 작성
              </button>
              <button 
                onClick={() => router.push('/staff/contract/mobile')}
                className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2"
              >
                <FileText className="h-4 w-4" />
                모바일 계약서
              </button>
              <button 
                onClick={() => router.push('/staff/register')}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
              >
                <Plus className="h-4 w-4" />
                새직원 등록
              </button>
            </div>
          </div>
        </div>

        {/* Staff List */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">직원 목록</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    직원
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    부서
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    연락처
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    상태
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    계약서
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    보건증
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    급여
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    입사일
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    작업
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {filteredStaff.map((member) => (
                  <tr 
                    key={member.id} 
                    className="hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer"
                    onClick={() => {
                      setSelectedStaff(member);
                      setShowStaffModal(true);
                    }}
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-10 h-10 bg-gray-300 dark:bg-gray-600 rounded-full flex items-center justify-center">
                          <User className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {member.name}
                          </div>
                          <div className="text-sm text-gray-500 dark:text-gray-400">
                            {member.position}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {member.department}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900 dark:text-white">{member.phone}</div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">{member.email}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadge(member.status)}`}>
                        {member.status === "active" ? "근무중" : member.status === "inactive" ? "퇴사" : "대기중"}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-2">
                        {member.contracts.length > 0 && (
                          <span className={`inline-flex items-center px-2 py-1 text-xs font-semibold rounded-full ${getExpiryStatus(member.contracts[0].is_expiring_soon, member.contracts[0].is_expired, member.contracts[0].days_until_expiry)}`}>
                            {member.contracts[0].file_path && (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleDownload(member.contracts[0].id, 'contract', member.contracts[0].file_name || 'contract.pdf')}
                              >
                                <Download className="w-4 h-4" />
                              </Button>
                            )}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-2">
                        {member.health_certificates.length > 0 && (
                          <span className={`inline-flex items-center px-2 py-1 text-xs font-semibold rounded-full ${getExpiryStatus(member.health_certificates[0].is_expiring_soon, member.health_certificates[0].is_expired, member.health_certificates[0].days_until_expiry)}`}>
                            {member.health_certificates[0].file_path && (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleDownload(member.health_certificates[0].id, 'health_certificate', member.health_certificates[0].file_name || 'health_cert.pdf')}
                              >
                                <Download className="w-4 h-4" />
                              </Button>
                            )}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {/* 급여 정보가 여기에 표시될 수 있습니다 */}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {member.join_date}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            router.push(`/staff/edit/${member.id}`);
                          }}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            updateStaffStatus(member.id, member.status === 'active' ? 'inactive' : 'active');
                          }}
                        >
                          {member.status === 'active' ? (
                            <UserX className="h-4 w-4 text-red-500" />
                          ) : (
                            <UserCheck className="h-4 w-4 text-green-500" />
                          )}
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteStaff(member.id);
                          }}
                        >
                          <Trash2 className="h-4 w-4 text-red-500" />
                        </Button>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end space-x-2">
                        <button 
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedStaff(member);
                            setShowStaffModal(true);
                          }}
                          className="text-blue-600 hover:text-blue-900 dark:hover:text-blue-400"
                        >
                          <Eye className="h-4 w-4" />
                        </button>
                        <button 
                          onClick={(e) => {
                            e.stopPropagation();
                            router.push(`/staff/edit/${member.id}`);
                          }}
                          className="text-green-600 hover:text-green-900 dark:hover:text-green-400"
                        >
                          <Edit className="h-4 w-4" />
                        </button>
                        <button 
                          onClick={(e) => {
                            e.stopPropagation();
                            router.push(`/staff/contract?edit=${member.id}`);
                          }}
                          className="text-blue-600 hover:text-blue-900 dark:hover:text-blue-400"
                          title="계약서 수정"
                        >
                          <FileText className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* 만료 임박 서류 알림 */}
        {expiringDocuments.length > 0 && (
          <Card className="mb-6 border-orange-200 bg-orange-50 dark:bg-orange-900/20">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-orange-800 dark:text-orange-200">
                <AlertCircle className="h-5 w-5" />
                만료 임박 서류 알림
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {expiringDocuments.slice(0, 3).map((doc, index) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-white dark:bg-gray-800 rounded">
                    <div>
                      <p className="font-medium">{doc.staff_name}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {doc.document_type}: {doc.expiry_date} 만료
                      </p>
                    </div>
                    <Badge variant="destructive">
                      {doc.days_until_expiry}일 남음
                    </Badge>
                  </div>
                ))}
                {expiringDocuments.length > 3 && (
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    외 {expiringDocuments.length - 3}건의 서류가 만료 임박입니다.
                  </p>
                )}
                <div className="flex gap-2 mt-4">
                  <Button
                    onClick={() => setShowExpiringModal(true)}
                    variant="outline"
                    size="sm"
                  >
                    전체 보기
                  </Button>
                  <Button
                    onClick={sendHealthCertificateNotification}
                    size="sm"
                    className="bg-orange-600 hover:bg-orange-700"
                  >
                    알림 발송
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* 직원 정보 모달 */}
      <Dialog open={showStaffModal} onOpenChange={setShowStaffModal}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <User className="h-5 w-5" />
              직원 정보
            </DialogTitle>
            <DialogDescription>
              직원의 상세 정보, 계약서, 보건증, 근무 통계를 확인할 수 있습니다.
            </DialogDescription>
          </DialogHeader>
          
          {selectedStaff && (
            <div className="space-y-6">
              {/* 기본 정보 */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <User className="h-4 w-4" />
                    기본 정보
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="flex items-center gap-3">
                      <div className="w-16 h-16 bg-gray-300 dark:bg-gray-600 rounded-full flex items-center justify-center">
                        <User className="h-8 w-8 text-gray-600 dark:text-gray-400" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                          {selectedStaff.name}
                        </h3>
                        <p className="text-gray-500 dark:text-gray-400">{selectedStaff.position}</p>
                        <Badge variant={selectedStaff.status === "active" ? "default" : "secondary"}>
                          {selectedStaff.status === "active" ? "재직중" : selectedStaff.status === "inactive" ? "퇴사" : "대기중"}
                        </Badge>
                      </div>
                    </div>
                    
                    <div className="space-y-3">
                      <div className="flex items-center gap-2">
                        <Building className="h-4 w-4 text-gray-500" />
                        <span className="text-sm text-gray-600 dark:text-gray-400">부서:</span>
                        <span className="text-sm font-medium">{selectedStaff.department}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <CalendarDays className="h-4 w-4 text-gray-500" />
                        <span className="text-sm text-gray-600 dark:text-gray-400">입사일:</span>
                        <span className="text-sm font-medium">{selectedStaff.join_date}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Phone className="h-4 w-4 text-gray-500" />
                        <span className="text-sm text-gray-600 dark:text-gray-400">연락처:</span>
                        <span className="text-sm font-medium">{selectedStaff.phone}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Mail className="h-4 w-4 text-gray-500" />
                        <span className="text-sm text-gray-600 dark:text-gray-400">이메일:</span>
                        <span className="text-sm font-medium">{selectedStaff.email}</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* 계약서 정보 */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-4 w-4" />
                    계약서 정보
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {selectedStaff.contracts.length > 0 ? (
                    <div className="space-y-3">
                      {selectedStaff.contracts.map((contract, index) => (
                        <div key={contract.id} className="p-3 border border-gray-200 dark:border-gray-600 rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <span className="font-medium text-gray-900 dark:text-white">
                                {contract.contract_number}
                              </span>
                              <Badge variant={contract.is_expired ? "destructive" : contract.is_expiring_soon ? "secondary" : "default"}>
                                {contract.is_expired ? "만료" : contract.is_expiring_soon ? "만료임박" : "유효"}
                              </Badge>
                            </div>
                            {contract.file_path && (
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleDownload(contract.id, 'contract', contract.file_name || 'contract.pdf')}
                              >
                                <Download className="h-4 w-4" />
                              </Button>
                            )}
                          </div>
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                              <span className="text-gray-500 dark:text-gray-400">계약 유형:</span>
                              <span className="ml-2 font-medium">{contract.contract_type}</span>
                            </div>
                            <div>
                              <span className="text-gray-500 dark:text-gray-400">시작일:</span>
                              <span className="ml-2 font-medium">{contract.start_date}</span>
                            </div>
                            <div>
                              <span className="text-gray-500 dark:text-gray-400">만료일:</span>
                              <span className="ml-2 font-medium">{contract.expiry_date}</span>
                            </div>
                            <div>
                              <span className="text-gray-500 dark:text-gray-400">갱신일:</span>
                              <span className="ml-2 font-medium">{contract.renewal_date}</span>
                            </div>
                          </div>
                          {contract.is_expiring_soon && (
                            <div className="mt-2 p-2 bg-yellow-50 dark:bg-yellow-900/20 rounded text-xs text-yellow-800 dark:text-yellow-200">
                              ⚠️ {contract.days_until_expiry}일 후 만료됩니다.
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-4 text-gray-500 dark:text-gray-400">
                      등록된 계약서가 없습니다.
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* 보건증 정보 */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Shield className="h-4 w-4" />
                    보건증 정보
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {selectedStaff.health_certificates.length > 0 ? (
                    <div className="space-y-3">
                      {selectedStaff.health_certificates.map((cert, index) => (
                        <div key={cert.id} className="p-3 border border-gray-200 dark:border-gray-600 rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <span className="font-medium text-gray-900 dark:text-white">
                                {cert.certificate_number}
                              </span>
                              <Badge variant={cert.is_expired ? "destructive" : cert.is_expiring_soon ? "secondary" : "default"}>
                                {cert.is_expired ? "만료" : cert.is_expiring_soon ? "만료임박" : "유효"}
                              </Badge>
                            </div>
                            {cert.file_path && (
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleDownload(cert.id, 'health_certificate', cert.file_name || 'health_cert.pdf')}
                              >
                                <Download className="h-4 w-4" />
                              </Button>
                            )}
                          </div>
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                              <span className="text-gray-500 dark:text-gray-400">증명서 유형:</span>
                              <span className="ml-2 font-medium">{cert.certificate_type}</span>
                            </div>
                            <div>
                              <span className="text-gray-500 dark:text-gray-400">발급기관:</span>
                              <span className="ml-2 font-medium">{cert.issuing_authority}</span>
                            </div>
                            <div>
                              <span className="text-gray-500 dark:text-gray-400">발급일:</span>
                              <span className="ml-2 font-medium">{cert.issue_date}</span>
                            </div>
                            <div>
                              <span className="text-gray-500 dark:text-gray-400">만료일:</span>
                              <span className="ml-2 font-medium">{cert.expiry_date}</span>
                            </div>
                          </div>
                          {cert.is_expiring_soon && (
                            <div className="mt-2 p-2 bg-yellow-50 dark:bg-yellow-900/20 rounded text-xs text-yellow-800 dark:text-yellow-200">
                              ⚠️ {cert.days_until_expiry}일 후 만료됩니다.
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-4 text-gray-500 dark:text-gray-400">
                      등록된 보건증이 없습니다.
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* 근무 통계 */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <ClockIcon className="h-4 w-4" />
                    근무 통계
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                      <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">24</div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">이번 달 근무일</div>
                    </div>
                    <div className="text-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                      <div className="text-2xl font-bold text-green-600 dark:text-green-400">192</div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">이번 달 근무시간</div>
                    </div>
                    <div className="text-center p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                      <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">2</div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">연차 사용일</div>
                    </div>
                    <div className="text-center p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                      <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">15</div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">잔여 연차</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* 액션 버튼 */}
              <div className="flex gap-3 pt-4">
                <Button
                  variant="outline"
                  onClick={() => setShowStaffModal(false)}
                  className="flex-1"
                >
                  닫기
                </Button>
                <Button
                  onClick={() => {
                    setShowStaffModal(false);
                    router.push(`/staff/edit/${selectedStaff.id}`);
                  }}
                  className="flex-1"
                >
                  <Edit className="h-4 w-4 mr-2" />
                  정보 수정
                </Button>
                <Button
                  onClick={() => {
                    setShowStaffModal(false);
                    router.push(`/staff/contract?staffId=${selectedStaff.id}&mode=edit`);
                  }}
                  className="flex-1"
                >
                  <FileText className="h-4 w-4 mr-2" />
                  계약서 수정
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* 알림창 */}
      <NotificationPopup 
        message="계약서/보건증 만료 알림이 설정되었습니다. 30일 전에 자동으로 알림이 발송됩니다." 
        delay={1500}
      />
    </div>
  );
} 
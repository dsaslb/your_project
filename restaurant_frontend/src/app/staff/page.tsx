"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Plus, Search, Filter, MoreHorizontal, Edit, Trash2, User, Phone, Mail, Calendar, MapPin, Download, Eye, AlertTriangle, CheckCircle, Clock, FileText, Shield } from "lucide-react";
import NotificationPopup from "@/components/NotificationPopup";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';

interface Contract {
  id: number;
  contract_number: string;
  start_date: string;
  expiry_date: string;
  renewal_date: string;
  contract_type: string;
  is_expiring_soon: boolean;
  is_expired: boolean;
  days_until_expiry: number;
  file_path?: string;
  file_name?: string;
}

interface HealthCertificate {
  id: number;
  certificate_number: string;
  issue_date: string;
  expiry_date: string;
  renewal_date: string;
  issuing_authority: string;
  certificate_type: string;
  is_expiring_soon: boolean;
  is_expired: boolean;
  days_until_expiry: number;
  file_path?: string;
  file_name?: string;
}

interface StaffMember {
  id: number;
  name: string;
  position: string;
  department: string;
  email: string;
  phone: string;
  join_date: string;
  status: 'active' | 'inactive' | 'pending';
  contracts: Contract[];
  health_certificates: HealthCertificate[];
}

export default function StaffPage() {
  const router = useRouter();
  const [selectedStaff, setSelectedStaff] = useState<StaffMember | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [selectedFilter, setSelectedFilter] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");
  const [staffMembers, setStaffMembers] = useState<StaffMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [expiringDocuments, setExpiringDocuments] = useState<any>(null);

  useEffect(() => {
    setIsLoaded(true);
    fetchStaffData();
    fetchExpiringDocuments();
  }, []);

  const togglePlay = () => {
    setIsPlaying(!isPlaying);
  };

  const fetchStaffData = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/staff', {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      if (response.ok) {
        const data = await response.json();
        setStaffMembers(data.staff || []);
      } else {
        console.error('직원 데이터 로드 실패');
        // 더미 데이터로 폴백
        setStaffMembers(getDummyData());
      }
    } catch (error) {
      console.error('API 호출 오류:', error);
      // 더미 데이터로 폴백
      setStaffMembers(getDummyData());
    } finally {
      setLoading(false);
    }
  };

  const fetchExpiringDocuments = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/staff/expiring-documents', {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      if (response.ok) {
        const data = await response.json();
        setExpiringDocuments(data);
      }
    } catch (error) {
      console.error('만료 임박 문서 로드 실패:', error);
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
            <button 
              onClick={() => router.push('/staff/add')}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <Plus className="h-4 w-4" />
              직원 추가
            </button>
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
                  <tr key={member.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
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
                      <div className="flex items-center justify-end space-x-2">
                        <button 
                          onClick={() => setSelectedStaff(member)}
                          className="text-blue-600 hover:text-blue-900 dark:hover:text-blue-400"
                        >
                          <Edit className="h-4 w-4" />
                        </button>
                        <button className="text-red-600 hover:text-red-900 dark:hover:text-red-400">
                          <Trash2 className="h-4 w-4" />
                        </button>
                        <button className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                          <MoreHorizontal className="h-4 w-4" />
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

      {/* 알림창 */}
      <NotificationPopup 
        message="계약서/보건증 만료 알림이 설정되었습니다. 30일 전에 자동으로 알림이 발송됩니다." 
        delay={1500}
      />
    </div>
  );
} 
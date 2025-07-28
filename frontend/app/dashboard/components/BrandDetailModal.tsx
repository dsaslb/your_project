'use client';
import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { X, Store, Users, DollarSign, TrendingUp, AlertTriangle, CheckCircle, Clock } from 'lucide-react';

interface Brand {
  id: number;
  name: string;
  code: string;
  description: string;
  status: 'active' | 'inactive' | 'pending';
  store_count: number;
  employee_count: number;
  total_revenue: number;
  improvement_requests: number;
  ai_diagnoses: number;
  pending_approvals: number;
  last_activity: string;
  stores?: any[];
  employees?: any[];
  sales_data?: any[];
  improvements?: any[];
  approvals?: any[];
}

interface BrandDetailModalProps {
  brand: Brand | null;
  isOpen: boolean;
  onClose: () => void;
}

export default function BrandDetailModal({ brand, isOpen, onClose }: BrandDetailModalProps) {
  if (!isOpen || !brand) return null;

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge className="bg-green-100 text-green-800 hover:bg-green-100">활성</Badge>;
      case 'inactive':
        return <Badge className="bg-red-100 text-red-800 hover:bg-red-100">비활성</Badge>;
      case 'pending':
        return <Badge className="bg-yellow-100 text-yellow-800 hover:bg-yellow-100">대기</Badge>;
      default:
        return <Badge variant="secondary">알 수 없음</Badge>;
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-slate-800 rounded-lg w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* 헤더 */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{brand.name}</h2>
              <p className="text-gray-500 dark:text-gray-400">{brand.code} - {brand.description}</p>
            </div>
            <div className="flex items-center gap-3">
              {getStatusBadge(brand.status)}
              <Button variant="outline" size="sm" onClick={onClose}>
                <X className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* 통계 카드 */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-500 dark:text-gray-400">매장 수</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center">
                  <Store className="w-5 h-5 text-blue-500 mr-2" />
                  <span className="text-2xl font-bold">{brand.store_count}개</span>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-500 dark:text-gray-400">직원 수</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center">
                  <Users className="w-5 h-5 text-green-500 mr-2" />
                  <span className="text-2xl font-bold">{brand.employee_count}명</span>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-500 dark:text-gray-400">총 매출</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center">
                  <DollarSign className="w-5 h-5 text-purple-500 mr-2" />
                  <span className="text-2xl font-bold">{(brand.total_revenue || 0).toLocaleString()}원</span>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-500 dark:text-gray-400">승인 대기</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center">
                  <Clock className="w-5 h-5 text-yellow-500 mr-2" />
                  <span className="text-2xl font-bold">{brand.pending_approvals}건</span>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 탭 컨텐츠 */}
          <Tabs defaultValue="overview" className="w-full">
            <TabsList className="grid w-full grid-cols-6">
              <TabsTrigger value="overview">개요</TabsTrigger>
              <TabsTrigger value="stores">매장</TabsTrigger>
              <TabsTrigger value="employees">직원</TabsTrigger>
              <TabsTrigger value="sales">매출</TabsTrigger>
              <TabsTrigger value="improvements">개선사항</TabsTrigger>
              <TabsTrigger value="approvals">승인</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>브랜드 개요</CardTitle>
                  <CardDescription>브랜드의 전반적인 현황을 확인합니다.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-medium mb-2">기본 정보</h4>
                      <div className="space-y-2 text-sm">
                        <div><span className="font-medium">브랜드명:</span> {brand.name}</div>
                        <div><span className="font-medium">코드:</span> {brand.code}</div>
                        <div><span className="font-medium">상태:</span> {getStatusBadge(brand.status)}</div>
                        <div><span className="font-medium">마지막 활동:</span> {new Date(brand.last_activity).toLocaleDateString()}</div>
                      </div>
                    </div>
                    <div>
                      <h4 className="font-medium mb-2">알림 현황</h4>
                      <div className="space-y-2 text-sm">
                        {brand.improvement_requests > 0 && (
                          <div className="flex items-center text-orange-600">
                            <AlertTriangle className="w-4 h-4 mr-2" />
                            <span>개선 요청 {brand.improvement_requests}건</span>
                          </div>
                        )}
                        {brand.ai_diagnoses > 0 && (
                          <div className="flex items-center text-blue-600">
                            <CheckCircle className="w-4 h-4 mr-2" />
                            <span>AI 진단 {brand.ai_diagnoses}건</span>
                          </div>
                        )}
                        {brand.pending_approvals > 0 && (
                          <div className="flex items-center text-yellow-600">
                            <Clock className="w-4 h-4 mr-2" />
                            <span>승인 대기 {brand.pending_approvals}건</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="stores" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>매장 관리</CardTitle>
                  <CardDescription>브랜드 소속 매장들의 현황을 확인합니다.</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-8 text-gray-500">
                    매장 목록이 여기에 표시됩니다.
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="employees" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>직원 관리</CardTitle>
                  <CardDescription>브랜드 소속 직원들의 현황을 확인합니다.</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-8 text-gray-500">
                    직원 목록이 여기에 표시됩니다.
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="sales" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>매출 현황</CardTitle>
                  <CardDescription>브랜드의 매출 데이터를 확인합니다.</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-8 text-gray-500">
                    매출 차트가 여기에 표시됩니다.
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="improvements" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>개선사항</CardTitle>
                  <CardDescription>브랜드 개선 요청사항을 확인합니다.</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-8 text-gray-500">
                    개선사항 목록이 여기에 표시됩니다.
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="approvals" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>승인 관리</CardTitle>
                  <CardDescription>승인 대기 중인 항목들을 확인합니다.</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-8 text-gray-500">
                    승인 대기 목록이 여기에 표시됩니다.
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
} 
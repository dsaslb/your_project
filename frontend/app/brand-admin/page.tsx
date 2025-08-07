'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../src/components/ui/card';
import { Button } from '../../src/components/ui/button';
import { Badge } from '../../src/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../../src/components/ui/dialog';
import { Textarea } from '../../src/components/ui/textarea';
import { Label } from '../../src/components/ui/label';
import { 
  Building2, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle,
  Brain,
  BarChart3,
  MessageSquare,
  Send,
  Eye,
  RefreshCw
} from 'lucide-react';
import { toast } from 'sonner';
import { apiClient } from '../../src/lib/api-client';

interface StoreAIReport {
  store_id: number;
  store_name: string;
  report_date: string;
  issues: string[];
  improvements: string[];
  efficiency_score: number;
}

interface BrandSummary {
  total_stores: number;
  avg_efficiency_score: number;
  common_issues: string[];
  top_improvements: string[];
  stores_with_issues: number;
}

export default function BrandAdmin() {
  const [storeReports, setStoreReports] = useState<StoreAIReport[]>([]);
  const [brandSummary, setBrandSummary] = useState<BrandSummary | null>(null);
  const [selectedStore, setSelectedStore] = useState<StoreAIReport | null>(null);
  const [isDetailDialogOpen, setIsDetailDialogOpen] = useState(false);
  const [isNotificationDialogOpen, setIsNotificationDialogOpen] = useState(false);
  const [notificationMessage, setNotificationMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // 현재 브랜드 ID (실제로는 사용자 정보에서 가져와야 함)
  const currentBrandId = 1;

  // 브랜드별 AI 리포트 요약 조회
  const fetchBrandAIReports = async () => {
    try {
      setIsLoading(true);
      const response = await apiClient.get(`/api/ai-reports/brand-summary?brand_id=${currentBrandId}`) as any;
      
      if (response.data.success) {
        setStoreReports(response.data.reports);
        
        // 브랜드 요약 계산
        const reports = response.data.reports;
        const totalStores = reports.length;
        const avgEfficiency = reports.reduce((sum: number, report: StoreAIReport) => sum + report.efficiency_score, 0) / totalStores;
        
        // 공통 문제점 수집
        const allIssues = reports.flatMap((report: StoreAIReport) => report.issues);
        const issueCounts = allIssues.reduce((acc: any, issue: string) => {
          acc[issue] = (acc[issue] || 0) + 1;
          return acc;
        }, {});
        const commonIssues = Object.entries(issueCounts)
          .sort(([,a]: any, [,b]: any) => b - a)
          .slice(0, 5)
          .map(([issue]) => issue);
        
        // 주요 개선사항 수집
        const allImprovements = reports.flatMap((report: StoreAIReport) => report.improvements);
        const improvementCounts = allImprovements.reduce((acc: any, improvement: string) => {
          acc[improvement] = (acc[improvement] || 0) + 1;
          return acc;
        }, {});
        const topImprovements = Object.entries(improvementCounts)
          .sort(([,a]: any, [,b]: any) => b - a)
          .slice(0, 5)
          .map(([improvement]) => improvement);
        
        const storesWithIssues = reports.filter((report: StoreAIReport) => report.issues.length > 0).length;
        
        setBrandSummary({
          total_stores: totalStores,
          avg_efficiency_score: avgEfficiency,
          common_issues: commonIssues,
          top_improvements: topImprovements,
          stores_with_issues: storesWithIssues
        });
      }
    } catch (error) {
      console.error('브랜드 AI 리포트 조회 실패:', error);
      toast.error('브랜드 AI 리포트 조회에 실패했습니다.');
      
      // 샘플 데이터로 대체
      const sampleReports = [
        {
          store_id: 1,
          store_name: '강남점',
          report_date: '2024-01-15',
          issues: ['월요일 오후 인원 과다', '화요일 저녁 인원 부족'],
          improvements: ['월요일 오후 인원 20% 감축', '화요일 저녁 인원 2명 추가'],
          efficiency_score: 75
        },
        {
          store_id: 2,
          store_name: '홍대점',
          report_date: '2024-01-15',
          issues: ['주말 인원 부족'],
          improvements: ['주말 인원 3명 추가'],
          efficiency_score: 85
        },
        {
          store_id: 3,
          store_name: '신촌점',
          report_date: '2024-01-15',
          issues: ['평일 오후 인원 과다', '고객 서비스 품질 저하'],
          improvements: ['평일 오후 인원 조정', '고객 서비스 교육 강화'],
          efficiency_score: 70
        }
      ];
      
      setStoreReports(sampleReports);
      setBrandSummary({
        total_stores: 3,
        avg_efficiency_score: 76.7,
        common_issues: ['평일 오후 인원 과다', '주말 인원 부족', '화요일 저녁 인원 부족'],
        top_improvements: ['인원 조정', '인원 추가', '고객 서비스 교육 강화'],
        stores_with_issues: 3
      });
    } finally {
      setIsLoading(false);
    }
  };

  // 매장에 알림/피드백 전송
  const sendNotification = async () => {
    if (!selectedStore || !notificationMessage.trim()) {
      toast.error('알림 메시지를 입력해주세요.');
      return;
    }

    try {
      // 실제로는 API를 통해 매장에 알림을 전송
      console.log(`매장 ${selectedStore.store_name}에 알림 전송:`, notificationMessage);
      
      toast.success(`${selectedStore.store_name}에 알림이 전송되었습니다.`);
      setIsNotificationDialogOpen(false);
      setNotificationMessage('');
      setSelectedStore(null);
    } catch (error) {
      toast.error('알림 전송에 실패했습니다.');
    }
  };

  useEffect(() => {
    fetchBrandAIReports();
  }, []);

  return (
    <div className="min-h-screen p-6">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <Building2 className="w-6 h-6" />
          브랜드 관리자 대시보드
        </h1>
        <p className="text-gray-300 mt-2">브랜드별 AI 분석 및 매장 관리</p>
      </div>

      {/* 액션 버튼 */}
      <div className="flex gap-4 mb-8">
        <Button
          onClick={fetchBrandAIReports}
          disabled={isLoading}
          className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          리포트 새로고침
        </Button>
      </div>

      {/* 브랜드 요약 통계 */}
      {brandSummary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-300 text-sm">총 매장 수</p>
                  <p className="text-2xl font-bold text-white">{brandSummary.total_stores}</p>
                </div>
                <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
                  <Building2 className="w-6 h-6 text-blue-400" />
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-300 text-sm">평균 효율도</p>
                  <p className="text-2xl font-bold text-white">{Math.round(brandSummary.avg_efficiency_score)}%</p>
                </div>
                <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center">
                  <BarChart3 className="w-6 h-6 text-purple-400" />
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-300 text-sm">문제 매장</p>
                  <p className="text-2xl font-bold text-red-400">{brandSummary.stores_with_issues}</p>
                </div>
                <div className="w-12 h-12 bg-red-500/20 rounded-lg flex items-center justify-center">
                  <AlertTriangle className="w-6 h-6 text-red-400" />
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-300 text-sm">정상 매장</p>
                  <p className="text-2xl font-bold text-green-400">
                    {brandSummary.total_stores - brandSummary.stores_with_issues}
                  </p>
                </div>
                <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
                  <CheckCircle className="w-6 h-6 text-green-400" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 브랜드 전체 분석 */}
      {brandSummary && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white">
                <AlertTriangle className="w-5 h-5 text-red-400" />
                주요 문제점
              </CardTitle>
            </CardHeader>
            <CardContent>
              {brandSummary.common_issues.length > 0 ? (
                <ul className="space-y-2">
                  {brandSummary.common_issues.map((issue, index) => (
                    <li key={index} className="flex items-center gap-2 text-gray-300">
                      <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                      {issue}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-400">현재 주요 문제점이 없습니다.</p>
              )}
            </CardContent>
          </Card>
          
          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white">
                <TrendingUp className="w-5 h-5 text-green-400" />
                주요 개선사항
              </CardTitle>
            </CardHeader>
            <CardContent>
              {brandSummary.top_improvements.length > 0 ? (
                <ul className="space-y-2">
                  {brandSummary.top_improvements.map((improvement, index) => (
                    <li key={index} className="flex items-center gap-2 text-gray-300">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      {improvement}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-400">현재 개선사항이 없습니다.</p>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* 매장별 AI 리포트 */}
      <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <Brain className="w-5 h-5 text-purple-400" />
            매장별 AI 분석 리포트
          </CardTitle>
        </CardHeader>
        <CardContent>
          {storeReports.length > 0 ? (
            <div className="space-y-4">
              {storeReports.map((report) => (
                <div key={report.store_id} className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:bg-white/10 transition-all duration-300">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="font-semibold text-lg text-white">{report.store_name}</h3>
                      <p className="text-sm text-gray-400">분석 날짜: {report.report_date}</p>
                    </div>
                    <div className="flex gap-2">
                      <Badge 
                        className={
                          report.efficiency_score >= 80 
                            ? 'bg-green-500/20 text-green-400' 
                            : report.efficiency_score >= 60 
                            ? 'bg-yellow-500/20 text-yellow-400' 
                            : 'bg-red-500/20 text-red-400'
                        }
                      >
                        효율도: {Math.round(report.efficiency_score)}%
                      </Badge>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => {
                          setSelectedStore(report);
                          setIsDetailDialogOpen(true);
                        }}
                        className="border-white/20 text-white hover:bg-white/10"
                      >
                        <Eye className="w-4 h-4 mr-1" />
                        상세보기
                      </Button>
                      {report.issues.length > 0 && (
                        <Button 
                          size="sm" 
                          onClick={() => {
                            setSelectedStore(report);
                            setIsNotificationDialogOpen(true);
                          }}
                          className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700"
                        >
                          <MessageSquare className="w-4 h-4 mr-1" />
                          알림
                        </Button>
                      )}
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {report.issues.length > 0 && (
                      <div>
                        <h4 className="font-medium text-red-400 mb-2">문제점</h4>
                        <ul className="space-y-1">
                          {report.issues.slice(0, 3).map((issue, index) => (
                            <li key={index} className="text-sm text-red-400">• {issue}</li>
                          ))}
                          {report.issues.length > 3 && (
                            <li className="text-sm text-gray-400">• 외 {report.issues.length - 3}개</li>
                          )}
                        </ul>
                      </div>
                    )}
                    
                    {report.improvements.length > 0 && (
                      <div>
                        <h4 className="font-medium text-green-400 mb-2">개선사항</h4>
                        <ul className="space-y-1">
                          {report.improvements.slice(0, 3).map((improvement, index) => (
                            <li key={index} className="text-sm text-green-400">• {improvement}</li>
                          ))}
                          {report.improvements.length > 3 && (
                            <li className="text-sm text-gray-400">• 외 {report.improvements.length - 3}개</li>
                          )}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-400">매장별 AI 리포트가 없습니다.</p>
          )}
        </CardContent>
      </Card>

      {/* 상세보기 다이얼로그 */}
      <Dialog open={isDetailDialogOpen} onOpenChange={setIsDetailDialogOpen}>
        <DialogContent className="bg-white/10 backdrop-blur-sm border border-white/20 max-w-2xl">
          <DialogHeader>
            <DialogTitle className="text-white">{selectedStore?.store_name} 상세 분석 리포트</DialogTitle>
          </DialogHeader>
          {selectedStore && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <div>
                  <p className="text-sm text-gray-400">분석 날짜: {selectedStore.report_date}</p>
                  <p className="text-sm text-gray-400">매장 ID: {selectedStore.store_id}</p>
                </div>
                <Badge 
                  className={
                    selectedStore.efficiency_score >= 80 
                      ? 'bg-green-500/20 text-green-400' 
                      : selectedStore.efficiency_score >= 60 
                      ? 'bg-yellow-500/20 text-yellow-400' 
                      : 'bg-red-500/20 text-red-400'
                  }
                >
                  효율도: {Math.round(selectedStore.efficiency_score)}%
                </Badge>
              </div>
              
              {selectedStore.issues.length > 0 && (
                <div>
                  <h4 className="font-medium text-red-400 mb-2">문제점</h4>
                  <ul className="space-y-1">
                    {selectedStore.issues.map((issue, index) => (
                      <li key={index} className="text-sm text-gray-300">• {issue}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {selectedStore.improvements.length > 0 && (
                <div>
                  <h4 className="font-medium text-green-400 mb-2">개선사항</h4>
                  <ul className="space-y-1">
                    {selectedStore.improvements.map((improvement, index) => (
                      <li key={index} className="text-sm text-gray-300">• {improvement}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* 알림 전송 다이얼로그 */}
      <Dialog open={isNotificationDialogOpen} onOpenChange={setIsNotificationDialogOpen}>
        <DialogContent className="bg-white/10 backdrop-blur-sm border border-white/20">
          <DialogHeader>
            <DialogTitle className="text-white">{selectedStore?.store_name}에 알림 전송</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <p className="text-sm text-gray-400">
              해당 매장의 관리자에게 개선사항이나 지시사항을 전송합니다.
            </p>
            
            <div>
              <Label className="text-sm font-medium text-gray-300">알림 메시지</Label>
              <Textarea
                className="w-full mt-1 bg-white/10 border-white/20 text-white"
                rows={4}
                value={notificationMessage}
                onChange={(e) => setNotificationMessage(e.target.value)}
                placeholder="매장 관리자에게 전송할 메시지를 입력하세요..."
              />
            </div>
            
            <div className="flex gap-2">
              <Button onClick={sendNotification} className="flex-1 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700">
                <Send className="w-4 h-4 mr-2" />
                전송
              </Button>
              <Button variant="outline" onClick={() => setIsNotificationDialogOpen(false)} className="border-white/20 text-white hover:bg-white/10">
                취소
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
} 
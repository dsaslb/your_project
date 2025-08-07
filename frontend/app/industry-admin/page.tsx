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
  Target,
  Users,
  Globe,
  RefreshCw
} from 'lucide-react';
import { toast } from 'sonner';
import { apiClient } from '../../src/lib/api-client';

interface BrandAIReport {
  brand_id: number;
  brand_name: string;
  total_stores: number;
  avg_efficiency_score: number;
  common_issues: string[];
  recommendations: string[];
}

interface IndustrySummary {
  total_brands: number;
  total_stores: number;
  avg_efficiency_score: number;
  high_risk_stores: number;
  optimization_opportunities: string[];
  best_practices: string[];
}

export default function IndustryAdmin() {
  const [brandReports, setBrandReports] = useState<BrandAIReport[]>([]);
  const [industrySummary, setIndustrySummary] = useState<IndustrySummary | null>(null);
  const [selectedBrand, setSelectedBrand] = useState<BrandAIReport | null>(null);
  const [isDetailDialogOpen, setIsDetailDialogOpen] = useState(false);
  const [isConsultingDialogOpen, setIsConsultingDialogOpen] = useState(false);
  const [consultingMessage, setConsultingMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // 현재 업종 ID (실제로는 사용자 정보에서 가져와야 함)
  const currentIndustryId = 1;

  // 업종별 AI 리포트 요약 조회
  const fetchIndustryAIReports = async () => {
    try {
      setIsLoading(true);
      const response = await apiClient.get(`/api/ai-reports/industry-summary?industry_id=${currentIndustryId}`) as any;
      
      if (response.data.success) {
        setBrandReports(response.data.reports);
        
        // 업종 요약 계산
        const reports = response.data.reports;
        const totalBrands = reports.length;
        const totalStores = reports.reduce((sum: number, report: BrandAIReport) => sum + report.total_stores, 0);
        const avgEfficiency = reports.reduce((sum: number, report: BrandAIReport) => sum + report.avg_efficiency_score, 0) / totalBrands;
        
        // 고위험 매장 수 (효율도 60% 미만)
        const highRiskStores = reports.reduce((sum: number, report: BrandAIReport) => {
          const lowEfficiencyStores = Math.floor(report.total_stores * (1 - report.avg_efficiency_score / 100));
          return sum + lowEfficiencyStores;
        }, 0);
        
        // 최적화 기회 수집
        const allIssues = reports.flatMap((report: BrandAIReport) => report.common_issues);
        const issueCounts = allIssues.reduce((acc: any, issue: string) => {
          acc[issue] = (acc[issue] || 0) + 1;
          return acc;
        }, {});
        const optimizationOpportunities = Object.entries(issueCounts)
          .sort(([,a]: any, [,b]: any) => b - a)
          .slice(0, 5)
          .map(([issue]) => issue);
        
        // 베스트 프랙티스 수집 (효율도 높은 브랜드의 추천사항)
        const highEfficiencyBrands = reports.filter((report: BrandAIReport) => report.avg_efficiency_score >= 80);
        const bestPractices = highEfficiencyBrands.flatMap((report: BrandAIReport) => report.recommendations);
        
        setIndustrySummary({
          total_brands: totalBrands,
          total_stores: totalStores,
          avg_efficiency_score: avgEfficiency,
          high_risk_stores: highRiskStores,
          optimization_opportunities: optimizationOpportunities,
          best_practices: bestPractices.slice(0, 5)
        });
      }
    } catch (error) {
      console.error('업종 AI 리포트 조회 실패:', error);
      toast.error('업종 AI 리포트 조회에 실패했습니다.');
      
      // 샘플 데이터로 대체
      const sampleReports = [
        {
          brand_id: 1,
          brand_name: '스타벅스',
          total_stores: 15,
          avg_efficiency_score: 78,
          common_issues: ['주말 인원 부족', '평일 오후 인원 과다'],
          recommendations: ['주말 인원 배치 최적화', '평일 오후 인원 조정']
        },
        {
          brand_id: 2,
          brand_name: '투썸플레이스',
          total_stores: 8,
          avg_efficiency_score: 82,
          common_issues: ['저녁 시간대 인원 부족'],
          recommendations: ['저녁 시간대 인원 증가', '고객 서비스 교육 강화']
        },
        {
          brand_id: 3,
          brand_name: '할리스',
          total_stores: 12,
          avg_efficiency_score: 75,
          common_issues: ['평일 오후 인원 과다', '고객 서비스 품질 저하'],
          recommendations: ['평일 오후 인원 조정', '고객 서비스 교육 강화']
        }
      ];
      
      setBrandReports(sampleReports);
      setIndustrySummary({
        total_brands: 3,
        total_stores: 35,
        avg_efficiency_score: 78.3,
        high_risk_stores: 8,
        optimization_opportunities: ['평일 오후 인원 과다', '주말 인원 부족', '저녁 시간대 인원 부족'],
        best_practices: ['고객 서비스 교육 강화', '인원 배치 최적화', '인원 조정']
      });
    } finally {
      setIsLoading(false);
    }
  };

  // 브랜드에 컨설팅/지원 메시지 전송
  const sendConsultingMessage = async () => {
    if (!selectedBrand || !consultingMessage.trim()) {
      toast.error('컨설팅 메시지를 입력해주세요.');
      return;
    }

    try {
      // 실제로는 API를 통해 브랜드에 컨설팅 메시지를 전송
      console.log(`브랜드 ${selectedBrand.brand_name}에 컨설팅 메시지 전송:`, consultingMessage);
      
      toast.success(`${selectedBrand.brand_name}에 컨설팅 메시지가 전송되었습니다.`);
      setIsConsultingDialogOpen(false);
      setConsultingMessage('');
      setSelectedBrand(null);
    } catch (error) {
      toast.error('컨설팅 메시지 전송에 실패했습니다.');
    }
  };

  useEffect(() => {
    fetchIndustryAIReports();
  }, []);

  return (
    <div className="min-h-screen p-6">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <Building2 className="w-6 h-6" />
          업종 관리자 대시보드
        </h1>
        <p className="text-gray-300 mt-2">업종별 AI 분석 및 브랜드 관리</p>
      </div>

      {/* 액션 버튼 */}
      <div className="flex gap-4 mb-8">
        <Button
          onClick={fetchIndustryAIReports}
          disabled={isLoading}
          className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          리포트 새로고침
        </Button>
      </div>

      {/* 업종 요약 통계 */}
      {industrySummary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-300 text-sm">총 브랜드</p>
                  <p className="text-2xl font-bold text-white">{industrySummary.total_brands}</p>
                </div>
                <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
                  <Globe className="w-6 h-6 text-blue-400" />
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-300 text-sm">총 매장</p>
                  <p className="text-2xl font-bold text-white">{industrySummary.total_stores}</p>
                </div>
                <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
                  <Building2 className="w-6 h-6 text-green-400" />
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-300 text-sm">평균 효율도</p>
                  <p className="text-2xl font-bold text-white">{Math.round(industrySummary.avg_efficiency_score)}%</p>
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
                  <p className="text-gray-300 text-sm">고위험 매장</p>
                  <p className="text-2xl font-bold text-red-400">{industrySummary.high_risk_stores}</p>
                </div>
                <div className="w-12 h-12 bg-red-500/20 rounded-lg flex items-center justify-center">
                  <AlertTriangle className="w-6 h-6 text-red-400" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 업종 전체 분석 */}
      {industrySummary && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white">
                <Target className="w-5 h-5 text-blue-400" />
                최적화 기회
              </CardTitle>
            </CardHeader>
            <CardContent>
              {industrySummary.optimization_opportunities.length > 0 ? (
                <ul className="space-y-2">
                  {industrySummary.optimization_opportunities.map((opportunity, index) => (
                    <li key={index} className="flex items-center gap-2 text-gray-300">
                      <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                      {opportunity}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-400">현재 최적화 기회가 없습니다.</p>
              )}
            </CardContent>
          </Card>
          
          <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white">
                <TrendingUp className="w-5 h-5 text-green-400" />
                베스트 프랙티스
              </CardTitle>
            </CardHeader>
            <CardContent>
              {industrySummary.best_practices.length > 0 ? (
                <ul className="space-y-2">
                  {industrySummary.best_practices.map((practice, index) => (
                    <li key={index} className="flex items-center gap-2 text-gray-300">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      {practice}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-400">현재 베스트 프랙티스가 없습니다.</p>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* 브랜드별 AI 리포트 */}
      <Card className="bg-white/10 backdrop-blur-sm border border-white/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <Brain className="w-5 h-5 text-purple-400" />
            브랜드별 AI 분석 리포트
          </CardTitle>
        </CardHeader>
        <CardContent>
          {brandReports.length > 0 ? (
            <div className="space-y-4">
              {brandReports.map((report) => (
                <div key={report.brand_id} className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:bg-white/10 transition-all duration-300">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="font-semibold text-lg text-white">{report.brand_name}</h3>
                      <p className="text-sm text-gray-400">총 {report.total_stores}개 매장</p>
                    </div>
                    <div className="flex gap-2">
                      <Badge 
                        className={
                          report.avg_efficiency_score >= 80 
                            ? 'bg-green-500/20 text-green-400' 
                            : report.avg_efficiency_score >= 60 
                            ? 'bg-yellow-500/20 text-yellow-400' 
                            : 'bg-red-500/20 text-red-400'
                        }
                      >
                        평균 효율도: {Math.round(report.avg_efficiency_score)}%
                      </Badge>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => {
                          setSelectedBrand(report);
                          setIsDetailDialogOpen(true);
                        }}
                        className="border-white/20 text-white hover:bg-white/10"
                      >
                        <Eye className="w-4 h-4 mr-1" />
                        상세보기
                      </Button>
                      {report.avg_efficiency_score < 70 && (
                        <Button 
                          size="sm" 
                          onClick={() => {
                            setSelectedBrand(report);
                            setIsConsultingDialogOpen(true);
                          }}
                          className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700"
                        >
                          <MessageSquare className="w-4 h-4 mr-1" />
                          컨설팅
                        </Button>
                      )}
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {report.common_issues.length > 0 && (
                      <div>
                        <h4 className="font-medium text-red-400 mb-2">주요 문제점</h4>
                        <ul className="space-y-1">
                          {report.common_issues.slice(0, 3).map((issue, index) => (
                            <li key={index} className="text-sm text-red-400">• {issue}</li>
                          ))}
                          {report.common_issues.length > 3 && (
                            <li className="text-sm text-gray-400">• 외 {report.common_issues.length - 3}개</li>
                          )}
                        </ul>
                      </div>
                    )}
                    
                    {report.recommendations.length > 0 && (
                      <div>
                        <h4 className="font-medium text-green-400 mb-2">추천사항</h4>
                        <ul className="space-y-1">
                          {report.recommendations.slice(0, 3).map((recommendation, index) => (
                            <li key={index} className="text-sm text-green-400">• {recommendation}</li>
                          ))}
                          {report.recommendations.length > 3 && (
                            <li className="text-sm text-gray-400">• 외 {report.recommendations.length - 3}개</li>
                          )}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-400">브랜드별 AI 리포트가 없습니다.</p>
          )}
        </CardContent>
      </Card>

      {/* 상세보기 다이얼로그 */}
      <Dialog open={isDetailDialogOpen} onOpenChange={setIsDetailDialogOpen}>
        <DialogContent className="bg-white/10 backdrop-blur-sm border border-white/20 max-w-2xl">
          <DialogHeader>
            <DialogTitle className="text-white">{selectedBrand?.brand_name} 상세 분석 리포트</DialogTitle>
          </DialogHeader>
          {selectedBrand && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <div>
                  <p className="text-sm text-gray-400">총 매장 수: {selectedBrand.total_stores}개</p>
                  <p className="text-sm text-gray-400">브랜드 ID: {selectedBrand.brand_id}</p>
                </div>
                <Badge 
                  className={
                    selectedBrand.avg_efficiency_score >= 80 
                      ? 'bg-green-500/20 text-green-400' 
                      : selectedBrand.avg_efficiency_score >= 60 
                      ? 'bg-yellow-500/20 text-yellow-400' 
                      : 'bg-red-500/20 text-red-400'
                  }
                >
                  평균 효율도: {Math.round(selectedBrand.avg_efficiency_score)}%
                </Badge>
              </div>
              
              {selectedBrand.common_issues.length > 0 && (
                <div>
                  <h4 className="font-medium text-red-400 mb-2">주요 문제점</h4>
                  <ul className="space-y-1">
                    {selectedBrand.common_issues.map((issue, index) => (
                      <li key={index} className="text-sm text-gray-300">• {issue}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {selectedBrand.recommendations.length > 0 && (
                <div>
                  <h4 className="font-medium text-green-400 mb-2">추천사항</h4>
                  <ul className="space-y-1">
                    {selectedBrand.recommendations.map((recommendation, index) => (
                      <li key={index} className="text-sm text-gray-300">• {recommendation}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* 컨설팅 메시지 다이얼로그 */}
      <Dialog open={isConsultingDialogOpen} onOpenChange={setIsConsultingDialogOpen}>
        <DialogContent className="bg-white/10 backdrop-blur-sm border border-white/20">
          <DialogHeader>
            <DialogTitle className="text-white">{selectedBrand?.brand_name} 컨설팅/지원 메시지</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <p className="text-sm text-gray-400">
              해당 브랜드의 관리자에게 컨설팅이나 지원 메시지를 전송합니다.
            </p>
            
            <div>
              <Label className="text-sm font-medium text-gray-300">컨설팅 메시지</Label>
              <Textarea
                className="w-full mt-1 bg-white/10 border-white/20 text-white"
                rows={4}
                value={consultingMessage}
                onChange={(e) => setConsultingMessage(e.target.value)}
                placeholder="브랜드 관리자에게 전송할 컨설팅 메시지를 입력하세요..."
              />
            </div>
            
            <div className="flex gap-2">
              <Button onClick={sendConsultingMessage} className="flex-1 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700">
                <Send className="w-4 h-4 mr-2" />
                전송
              </Button>
              <Button variant="outline" onClick={() => setIsConsultingDialogOpen(false)} className="border-white/20 text-white hover:bg-white/10">
                취소
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
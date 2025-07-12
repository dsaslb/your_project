"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { toast } from "sonner";
import {
  BarChart3,
  Star,
  TrendingUp,
  TrendingDown,
  Users,
  DollarSign,
  Clock,
  Award,
  Target,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Plus,
  Edit,
  Trash2,
  Download,
  Upload,
  Filter,
  Search,
  Calendar,
  FileText,
  PieChart,
  LineChart,
  Activity,
  Zap,
  Heart,
  ThumbsUp,
  ThumbsDown,
  MessageSquare,
  Eye,
  EyeOff,
  HistoryIcon,
} from "lucide-react";

// 평가 항목 타입 정의
interface EvaluationCategory {
  id: string;
  name: string;
  description: string;
  weight: number;
  maxScore: number;
  criteria: EvaluationCriteria[];
}

interface EvaluationCriteria {
  id: string;
  name: string;
  description: string;
  maxScore: number;
  weight: number;
}

interface EvaluationResult {
  id: string;
  date: string;
  evaluator: string;
  categoryId: string;
  criteriaId: string;
  score: number;
  comments: string;
  attachments?: string[];
}

interface OverallScore {
  totalScore: number;
  maxScore: number;
  percentage: number;
  grade: string;
  categoryScores: {
    categoryId: string;
    score: number;
    maxScore: number;
    percentage: number;
  }[];
}

// 평가 카테고리 데이터
const evaluationCategories: EvaluationCategory[] = [
  {
    id: "service",
    name: "서비스 품질",
    description: "고객 서비스 및 응대 품질",
    weight: 30,
    maxScore: 100,
    criteria: [
      { id: "service-1", name: "고객 응대 친절도", description: "직원의 고객 응대 태도", maxScore: 25, weight: 25 },
      { id: "service-2", name: "서비스 속도", description: "주문 처리 및 서비스 제공 속도", maxScore: 25, weight: 25 },
      { id: "service-3", name: "문제 해결 능력", description: "고객 불만 및 문제 해결 능력", maxScore: 25, weight: 25 },
      { id: "service-4", name: "서비스 일관성", description: "서비스 품질의 일관성", maxScore: 25, weight: 25 },
    ],
  },
  {
    id: "food",
    name: "음식 품질",
    description: "음식의 맛, 품질, 위생",
    weight: 35,
    maxScore: 100,
    criteria: [
      { id: "food-1", name: "음식 맛", description: "음식의 맛과 품질", maxScore: 30, weight: 30 },
      { id: "food-2", name: "위생 상태", description: "음식 준비 및 제공 시 위생", maxScore: 25, weight: 25 },
      { id: "food-3", name: "음식 온도", description: "음식의 적절한 온도 유지", maxScore: 20, weight: 20 },
      { id: "food-4", name: "음식 양", description: "음식의 적절한 양", maxScore: 15, weight: 15 },
      { id: "food-5", name: "음식 모양", description: "음식의 시각적 매력도", maxScore: 10, weight: 10 },
    ],
  },
  {
    id: "environment",
    name: "매장 환경",
    description: "매장의 청결도 및 분위기",
    weight: 20,
    maxScore: 100,
    criteria: [
      { id: "environment-1", name: "매장 청결도", description: "매장 전체의 청결 상태", maxScore: 40, weight: 40 },
      { id: "environment-2", name: "좌석 편의성", description: "좌석의 편안함과 배치", maxScore: 25, weight: 25 },
      { id: "environment-3", name: "조명 및 분위기", description: "매장의 조명과 전체적인 분위기", maxScore: 20, weight: 20 },
      { id: "environment-4", name: "온도 및 환기", description: "매장의 온도와 공기질", maxScore: 15, weight: 15 },
    ],
  },
  {
    id: "management",
    name: "운영 관리",
    description: "매장 운영 및 관리 효율성",
    weight: 15,
    maxScore: 100,
    criteria: [
      { id: "management-1", name: "재고 관리", description: "재료 및 재고 관리 효율성", maxScore: 30, weight: 30 },
      { id: "management-2", name: "직원 관리", description: "직원 스케줄 및 업무 분담", maxScore: 25, weight: 25 },
      { id: "management-3", name: "비용 관리", description: "운영 비용 및 수익성 관리", maxScore: 25, weight: 25 },
      { id: "management-4", name: "안전 관리", description: "안전 사고 예방 및 대응", maxScore: 20, weight: 20 },
    ],
  },
];

// 더미 평가 결과 데이터
const evaluationResults: EvaluationResult[] = [
  {
    id: "1",
    date: "2024-01-15",
    evaluator: "김매니저",
    categoryId: "service",
    criteriaId: "service-1",
    score: 23,
    comments: "전반적으로 친절한 응대를 보여줍니다. 개선 여지가 있지만 만족스러운 수준입니다.",
  },
  {
    id: "2",
    date: "2024-01-15",
    evaluator: "김매니저",
    categoryId: "service",
    criteriaId: "service-2",
    score: 20,
    comments: "서비스 속도가 다소 느린 편입니다. 효율성 개선이 필요합니다.",
  },
  {
    id: "3",
    date: "2024-01-15",
    evaluator: "김매니저",
    categoryId: "food",
    criteriaId: "food-1",
    score: 28,
    comments: "음식 맛이 매우 우수합니다. 고객 만족도가 높습니다.",
  },
  {
    id: "4",
    date: "2024-01-15",
    evaluator: "김매니저",
    categoryId: "food",
    criteriaId: "food-2",
    score: 25,
    comments: "위생 상태가 매우 깔끔합니다. 모든 기준을 충족합니다.",
  },
  {
    id: "5",
    date: "2024-01-15",
    evaluator: "김매니저",
    categoryId: "environment",
    criteriaId: "environment-1",
    score: 38,
    comments: "매장이 매우 깔끔하게 유지되고 있습니다.",
  },
  {
    id: "6",
    date: "2024-01-15",
    evaluator: "김매니저",
    categoryId: "management",
    criteriaId: "management-1",
    score: 27,
    comments: "재고 관리가 효율적으로 이루어지고 있습니다.",
  },
];

export default function EvaluationPage() {
  const [activeTab, setActiveTab] = useState("overview");
  const [selectedCategory, setSelectedCategory] = useState<string>("");
  const [isAddingEvaluation, setIsAddingEvaluation] = useState(false);
  const [newEvaluation, setNewEvaluation] = useState<Partial<EvaluationResult>>({
    categoryId: "",
    criteriaId: "",
    score: 0,
    comments: "",
  });

  // 전체 점수 계산
  const calculateOverallScore = (): OverallScore => {
    const categoryScores = evaluationCategories.map(category => {
      const categoryResults = evaluationResults.filter(result => result.categoryId === category.id);
      const totalScore = categoryResults.reduce((sum, result) => sum + result.score, 0);
      const maxScore = category.criteria.reduce((sum, criteria) => sum + criteria.maxScore, 0);
      const percentage = maxScore > 0 ? (totalScore / maxScore) * 100 : 0;
      
      return {
        categoryId: category.id,
        score: totalScore,
        maxScore,
        percentage,
      };
    });

    const totalScore = categoryScores.reduce((sum, cat) => sum + cat.score, 0);
    const maxScore = categoryScores.reduce((sum, cat) => sum + cat.maxScore, 0);
    const percentage = maxScore > 0 ? (totalScore / maxScore) * 100 : 0;

    let grade = "F";
    if (percentage >= 90) grade = "A+";
    else if (percentage >= 85) grade = "A";
    else if (percentage >= 80) grade = "B+";
    else if (percentage >= 75) grade = "B";
    else if (percentage >= 70) grade = "C+";
    else if (percentage >= 65) grade = "C";
    else if (percentage >= 60) grade = "D+";
    else if (percentage >= 55) grade = "D";

    return {
      totalScore,
      maxScore,
      percentage,
      grade,
      categoryScores,
    };
  };

  const overallScore = calculateOverallScore();

  const getGradeColor = (grade: string) => {
    switch (grade) {
      case "A+":
      case "A":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200";
      case "B+":
      case "B":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200";
      case "C+":
      case "C":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200";
      case "D+":
      case "D":
        return "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200";
      default:
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200";
    }
  };

  const getScoreColor = (percentage: number) => {
    if (percentage >= 90) return "text-green-600";
    if (percentage >= 80) return "text-blue-600";
    if (percentage >= 70) return "text-yellow-600";
    if (percentage >= 60) return "text-orange-600";
    return "text-red-600";
  };

  const handleAddEvaluation = () => {
    if (!newEvaluation.categoryId || !newEvaluation.criteriaId || newEvaluation.score === undefined) {
      toast("필수 정보를 입력해주세요.", {
        description: "카테고리, 평가 항목, 점수를 모두 입력해주세요.",
      });
      return;
    }

    const evaluation: EvaluationResult = {
      id: Date.now().toString(),
      date: new Date().toISOString().split('T')[0],
      evaluator: "현재 사용자",
      categoryId: newEvaluation.categoryId!,
      criteriaId: newEvaluation.criteriaId!,
      score: newEvaluation.score!,
      comments: newEvaluation.comments || "",
    };

    // 실제로는 API 호출로 저장
    toast("평가가 추가되었습니다.", {
      description: "평가 결과가 성공적으로 저장되었습니다.",
    });

    setNewEvaluation({
      categoryId: "",
      criteriaId: "",
      score: 0,
      comments: "",
    });
    setIsAddingEvaluation(false);
  };

  const getCategoryName = (categoryId: string) => {
    return evaluationCategories.find(cat => cat.id === categoryId)?.name || "";
  };

  const getCriteriaName = (criteriaId: string) => {
    for (const category of evaluationCategories) {
      const criteria = category.criteria.find(c => c.id === criteriaId);
      if (criteria) return criteria.name;
    }
    return "";
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">매장 종합 평가</h1>
          <p className="text-muted-foreground">
            매장의 전반적인 성과와 품질을 평가하고 관리하세요.
          </p>
        </div>
        <Button onClick={() => setIsAddingEvaluation(true)}>
          <Plus className="h-4 w-4 mr-2" />
          평가 추가
        </Button>
      </div>

      {/* 전체 점수 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">전체 점수</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{overallScore.totalScore}/{overallScore.maxScore}</div>
            <div className={`text-lg font-semibold ${getScoreColor(overallScore.percentage)}`}>
              {overallScore.percentage.toFixed(1)}%
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">등급</CardTitle>
            <Award className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <Badge className={`text-lg font-bold ${getGradeColor(overallScore.grade)}`}>
              {overallScore.grade}
            </Badge>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">평가 횟수</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{evaluationResults.length}</div>
            <p className="text-xs text-muted-foreground">이번 달 평가</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">평가자</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {new Set(evaluationResults.map(r => r.evaluator)).size}
            </div>
            <p className="text-xs text-muted-foreground">참여 평가자</p>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">전체 현황</TabsTrigger>
          <TabsTrigger value="categories">카테고리별</TabsTrigger>
          <TabsTrigger value="history">평가 이력</TabsTrigger>
          <TabsTrigger value="reports">보고서</TabsTrigger>
        </TabsList>

        {/* 전체 현황 탭 */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 카테고리별 점수 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PieChart className="h-5 w-5" />
                  카테고리별 점수
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {overallScore.categoryScores.map((categoryScore) => {
                  const category = evaluationCategories.find(cat => cat.id === categoryScore.categoryId);
                  return (
                    <div key={categoryScore.categoryId} className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="font-medium">{category?.name}</span>
                        <span className={`font-semibold ${getScoreColor(categoryScore.percentage)}`}>
                          {categoryScore.percentage.toFixed(1)}%
                        </span>
                      </div>
                      <Progress value={categoryScore.percentage} className="h-2" />
                      <div className="text-sm text-muted-foreground">
                        {categoryScore.score}/{categoryScore.maxScore}점
                      </div>
                    </div>
                  );
                })}
              </CardContent>
            </Card>

            {/* 최근 평가 결과 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  최근 평가 결과
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {evaluationResults.slice(0, 5).map((result) => (
                    <div key={result.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div>
                        <p className="font-medium">{getCriteriaName(result.criteriaId)}</p>
                        <p className="text-sm text-muted-foreground">
                          {getCategoryName(result.categoryId)} • {result.evaluator}
                        </p>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold">{result.score}점</div>
                        <div className="text-sm text-muted-foreground">{result.date}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 개선 사항 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5" />
                개선 사항
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 border rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertTriangle className="h-4 w-4 text-orange-500" />
                    <h3 className="font-semibold">우선 개선</h3>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    서비스 속도 개선이 필요합니다. 현재 20/25점으로 다소 낮은 수준입니다.
                  </p>
                </div>
                <div className="p-4 border rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingUp className="h-4 w-4 text-blue-500" />
                    <h3 className="font-semibold">유지 강화</h3>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    음식 품질과 위생 상태가 우수합니다. 현재 수준을 유지해주세요.
                  </p>
                </div>
                <div className="p-4 border rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <h3 className="font-semibold">우수 항목</h3>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    매장 청결도와 음식 맛이 매우 우수합니다. 고객 만족도가 높습니다.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 카테고리별 탭 */}
        <TabsContent value="categories" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {evaluationCategories.map((category) => {
              const categoryResults = evaluationResults.filter(result => result.categoryId === category.id);
              const categoryScore = overallScore.categoryScores.find(cs => cs.categoryId === category.id);
              
              return (
                <Card key={category.id}>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span>{category.name}</span>
                      <Badge className={getGradeColor(categoryScore?.percentage || 0 >= 90 ? "A" : "B")}>
                        {categoryScore?.percentage.toFixed(1)}%
                      </Badge>
                    </CardTitle>
                    <p className="text-sm text-muted-foreground">{category.description}</p>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {category.criteria.map((criteria) => {
                      const result = categoryResults.find(r => r.criteriaId === criteria.id);
                      const score = result?.score || 0;
                      const percentage = (score / criteria.maxScore) * 100;
                      
                      return (
                        <div key={criteria.id} className="space-y-2">
                          <div className="flex justify-between items-center">
                            <div>
                              <p className="font-medium">{criteria.name}</p>
                              <p className="text-sm text-muted-foreground">{criteria.description}</p>
                            </div>
                            <div className="text-right">
                              <div className="font-semibold">{score}/{criteria.maxScore}</div>
                              <div className={`text-sm ${getScoreColor(percentage)}`}>
                                {percentage.toFixed(1)}%
                              </div>
                            </div>
                          </div>
                          <Progress value={percentage} className="h-2" />
                          {result?.comments && (
                            <p className="text-sm text-muted-foreground italic">
                              "{result.comments}"
                            </p>
                          )}
                        </div>
                      );
                    })}
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        {/* 평가 이력 탭 */}
        <TabsContent value="history" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <HistoryIcon className="h-5 w-5" />
                평가 이력
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {evaluationResults.map((result) => (
                  <div key={result.id} className="border rounded-lg p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="font-semibold">{getCriteriaName(result.criteriaId)}</h3>
                        <p className="text-sm text-muted-foreground">
                          {getCategoryName(result.categoryId)} • {result.evaluator} • {result.date}
                        </p>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold">{result.score}점</div>
                        <div className="text-sm text-muted-foreground">평가 점수</div>
                      </div>
                    </div>
                    {result.comments && (
                      <div className="bg-muted p-3 rounded">
                        <p className="text-sm">{result.comments}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 보고서 탭 */}
        <TabsContent value="reports" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                종합 평가 보고서
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* 요약 정보 */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 border rounded-lg">
                    <div className="text-3xl font-bold text-blue-600">{overallScore.percentage.toFixed(1)}%</div>
                    <div className="text-sm text-muted-foreground">전체 평균 점수</div>
                  </div>
                  <div className="text-center p-4 border rounded-lg">
                    <div className="text-3xl font-bold text-green-600">{overallScore.grade}</div>
                    <div className="text-sm text-muted-foreground">종합 등급</div>
                  </div>
                  <div className="text-center p-4 border rounded-lg">
                    <div className="text-3xl font-bold text-purple-600">{evaluationResults.length}</div>
                    <div className="text-sm text-muted-foreground">총 평가 횟수</div>
                  </div>
                </div>

                {/* 상세 분석 */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">카테고리별 상세 분석</h3>
                  {overallScore.categoryScores.map((categoryScore) => {
                    const category = evaluationCategories.find(cat => cat.id === categoryScore.categoryId);
                    return (
                      <div key={categoryScore.categoryId} className="p-4 border rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-semibold">{category?.name}</h4>
                          <Badge className={getGradeColor(categoryScore.percentage >= 90 ? "A" : "B")}>
                            {categoryScore.percentage.toFixed(1)}%
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mb-3">{category?.description}</p>
                        <div className="space-y-2">
                          {category?.criteria.map((criteria) => {
                            const result = evaluationResults.find(r => 
                              r.categoryId === category.id && r.criteriaId === criteria.id
                            );
                            const score = result?.score || 0;
                            const percentage = (score / criteria.maxScore) * 100;
                            
                            return (
                              <div key={criteria.id} className="flex items-center justify-between text-sm">
                                <span>{criteria.name}</span>
                                <div className="flex items-center gap-2">
                                  <span>{score}/{criteria.maxScore}</span>
                                  <span className={getScoreColor(percentage)}>
                                    ({percentage.toFixed(1)}%)
                                  </span>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* 개선 권장사항 */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">개선 권장사항</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 border border-orange-200 bg-orange-50 rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <AlertTriangle className="h-4 w-4 text-orange-600" />
                        <h4 className="font-semibold text-orange-800">즉시 개선 필요</h4>
                      </div>
                      <ul className="text-sm text-orange-700 space-y-1">
                        <li>• 서비스 속도 개선 (현재 80% → 목표 90%)</li>
                        <li>• 직원 교육 강화</li>
                      </ul>
                    </div>
                    <div className="p-4 border border-blue-200 bg-blue-50 rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <TrendingUp className="h-4 w-4 text-blue-600" />
                        <h4 className="font-semibold text-blue-800">단계적 개선</h4>
                      </div>
                      <ul className="text-sm text-blue-700 space-y-1">
                        <li>• 매장 환경 개선</li>
                        <li>• 고객 피드백 시스템 강화</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* 평가 추가 모달 */}
      {isAddingEvaluation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>평가 추가</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>평가 카테고리 *</Label>
                <Select
                  value={newEvaluation.categoryId}
                  onValueChange={(value) => setNewEvaluation({ ...newEvaluation, categoryId: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="카테고리 선택" />
                  </SelectTrigger>
                  <SelectContent>
                    {evaluationCategories.map((category) => (
                      <SelectItem key={category.id} value={category.id}>
                        {category.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {newEvaluation.categoryId && (
                <div className="space-y-2">
                  <Label>평가 항목 *</Label>
                  <Select
                    value={newEvaluation.criteriaId}
                    onValueChange={(value) => setNewEvaluation({ ...newEvaluation, criteriaId: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="평가 항목 선택" />
                    </SelectTrigger>
                    <SelectContent>
                      {evaluationCategories
                        .find(cat => cat.id === newEvaluation.categoryId)
                        ?.criteria.map((criteria) => (
                          <SelectItem key={criteria.id} value={criteria.id}>
                            {criteria.name}
                          </SelectItem>
                        ))}
                    </SelectContent>
                  </Select>
                </div>
              )}

              {newEvaluation.criteriaId && (
                <div className="space-y-2">
                  <Label>점수 * (0-{evaluationCategories
                    .find(cat => cat.id === newEvaluation.categoryId)
                    ?.criteria.find(c => c.id === newEvaluation.criteriaId)?.maxScore || 0}점)</Label>
                  <Input
                    type="number"
                    value={newEvaluation.score}
                    onChange={(e) => setNewEvaluation({ ...newEvaluation, score: Number(e.target.value) })}
                    min="0"
                    max={evaluationCategories
                      .find(cat => cat.id === newEvaluation.categoryId)
                      ?.criteria.find(c => c.id === newEvaluation.criteriaId)?.maxScore || 0}
                  />
                </div>
              )}

              <div className="space-y-2">
                <Label>평가 의견</Label>
                <Textarea
                  value={newEvaluation.comments}
                  onChange={(e) => setNewEvaluation({ ...newEvaluation, comments: e.target.value })}
                  placeholder="평가에 대한 의견을 입력하세요"
                  rows={3}
                />
              </div>

              <div className="flex gap-2">
                <Button onClick={handleAddEvaluation} className="flex-1">
                  평가 추가
                </Button>
                <Button variant="outline" onClick={() => setIsAddingEvaluation(false)} className="flex-1">
                  취소
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
} 
"use client";
import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Calendar, Users, Clock, CheckCircle, AlertCircle, Settings } from "lucide-react";

interface CleaningPlan {
  id: number;
  date: string;
  plan: string;
  team: string;
  manager: string;
  status: string;
  completed_at?: string;
}

interface CleaningSettings {
  daily_cleaning_time: string;
  weekly_deep_cleaning: string;
  team_rotation: boolean;
  auto_reminder: boolean;
}

export default function CleaningPage() {
  const [cleaningPlans, setCleaningPlans] = useState<CleaningPlan[]>([]);
  const [settings, setSettings] = useState<CleaningSettings>({
    daily_cleaning_time: "22:00",
    weekly_deep_cleaning: "일요일",
    team_rotation: true,
    auto_reminder: true
  });
  const [showAddPlan, setShowAddPlan] = useState(false);
  const [newPlan, setNewPlan] = useState({
    date: "",
    plan: "",
    team: "",
    manager: ""
  });

  // 더미 청소 계획 데이터
  useEffect(() => {
    const dummyPlans: CleaningPlan[] = [
      {
        id: 1,
        date: "2024-01-15",
        plan: "일일 청소 - 주방, 홀 전체",
        team: "주방팀",
        manager: "김주방",
        status: "completed",
        completed_at: "2024-01-15 22:30"
      },
      {
        id: 2,
        date: "2024-01-16",
        plan: "일일 청소 - 주방, 홀 전체",
        team: "홀팀",
        manager: "이홀",
        status: "pending"
      },
      {
        id: 3,
        date: "2024-01-17",
        plan: "주간 심화 청소 - 주방 설비 점검",
        team: "주방팀",
        manager: "김주방",
        status: "pending"
      }
    ];
    setCleaningPlans(dummyPlans);
  }, []);

  const handleAddPlan = () => {
    if (newPlan.date && newPlan.plan && newPlan.team) {
      const plan: CleaningPlan = {
        id: Date.now(),
        date: newPlan.date,
        plan: newPlan.plan,
        team: newPlan.team,
        manager: newPlan.manager,
        status: "pending"
      };
      setCleaningPlans([...cleaningPlans, plan]);
      setNewPlan({ date: "", plan: "", team: "", manager: "" });
      setShowAddPlan(false);
    }
  };

  const handleCompletePlan = (id: number) => {
    setCleaningPlans(plans =>
      plans.map(plan =>
        plan.id === id
          ? { ...plan, status: "completed", completed_at: new Date().toISOString() }
          : plan
      )
    );
  };

  const getStatusIcon = (status: string) => {
    return status === "completed" ? (
      <CheckCircle className="h-4 w-4 text-green-500" />
    ) : (
      <AlertCircle className="h-4 w-4 text-yellow-500" />
    );
  };

  const getStatusText = (status: string) => {
    return status === "completed" ? "완료" : "대기중";
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">청소 관리</h1>
        <Button onClick={() => setShowAddPlan(true)}>
          청소 계획 추가
        </Button>
      </div>

      {/* 청소 설정 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            청소 설정
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="daily-time">일일 청소 시간</Label>
              <Input
                id="daily-time"
                type="time"
                value={settings.daily_cleaning_time}
                onChange={(e) => setSettings({...settings, daily_cleaning_time: e.target.value})}
              />
            </div>
            <div>
              <Label htmlFor="weekly-day">주간 심화 청소 요일</Label>
              <Select value={settings.weekly_deep_cleaning} onValueChange={(value) => setSettings({...settings, weekly_deep_cleaning: value})}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="일요일">일요일</SelectItem>
                  <SelectItem value="월요일">월요일</SelectItem>
                  <SelectItem value="화요일">화요일</SelectItem>
                  <SelectItem value="수요일">수요일</SelectItem>
                  <SelectItem value="목요일">목요일</SelectItem>
                  <SelectItem value="금요일">금요일</SelectItem>
                  <SelectItem value="토요일">토요일</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="flex gap-4">
            <Button variant="outline" onClick={() => setSettings({...settings, team_rotation: !settings.team_rotation})}>
              팀 순환: {settings.team_rotation ? "ON" : "OFF"}
            </Button>
            <Button variant="outline" onClick={() => setSettings({...settings, auto_reminder: !settings.auto_reminder})}>
              자동 알림: {settings.auto_reminder ? "ON" : "OFF"}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 청소 계획 목록 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            청소 계획
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {cleaningPlans.map((plan) => (
              <div key={plan.id} className="border rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      {getStatusIcon(plan.status)}
                      <span className="font-semibold">{plan.date}</span>
                      <span className={`px-2 py-1 rounded text-xs ${
                        plan.status === "completed" ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"
                      }`}>
                        {getStatusText(plan.status)}
                      </span>
                    </div>
                    <p className="text-gray-700 mb-2">{plan.plan}</p>
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span className="flex items-center gap-1">
                        <Users className="h-4 w-4" />
                        {plan.team}
                      </span>
                      <span>담당: {plan.manager}</span>
                      {plan.completed_at && (
                        <span className="flex items-center gap-1">
                          <Clock className="h-4 w-4" />
                          완료: {new Date(plan.completed_at).toLocaleString()}
                        </span>
                      )}
                    </div>
                  </div>
                  {plan.status === "pending" && (
                    <Button
                      size="sm"
                      onClick={() => handleCompletePlan(plan.id)}
                    >
                      완료 처리
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 청소 계획 추가 모달 */}
      {showAddPlan && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">청소 계획 추가</h3>
            <div className="space-y-4">
              <div>
                <Label htmlFor="plan-date">날짜</Label>
                <Input
                  id="plan-date"
                  type="date"
                  value={newPlan.date}
                  onChange={(e) => setNewPlan({...newPlan, date: e.target.value})}
                />
              </div>
              <div>
                <Label htmlFor="plan-content">청소 내용</Label>
                <Textarea
                  id="plan-content"
                  value={newPlan.plan}
                  onChange={(e) => setNewPlan({...newPlan, plan: e.target.value})}
                  placeholder="청소할 내용을 입력하세요"
                />
              </div>
              <div>
                <Label htmlFor="plan-team">담당 팀</Label>
                <Select value={newPlan.team} onValueChange={(value) => setNewPlan({...newPlan, team: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="팀을 선택하세요" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="주방팀">주방팀</SelectItem>
                    <SelectItem value="홀팀">홀팀</SelectItem>
                    <SelectItem value="전체">전체</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="plan-manager">담당자</Label>
                <Input
                  id="plan-manager"
                  value={newPlan.manager}
                  onChange={(e) => setNewPlan({...newPlan, manager: e.target.value})}
                  placeholder="담당자 이름"
                />
              </div>
            </div>
            <div className="flex gap-2 mt-6">
              <Button onClick={handleAddPlan} className="flex-1">
                추가
              </Button>
              <Button variant="outline" onClick={() => setShowAddPlan(false)} className="flex-1">
                취소
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 
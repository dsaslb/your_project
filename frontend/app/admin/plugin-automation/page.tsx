"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import { 
  Zap, 
  Play, 
  Pause, 
  Plus, 
  Edit, 
  Trash2, 
  Settings, 
  Activity, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  Bell,
  Mail,
  MessageSquare,
  Globe,
  Code,
  Database,
  Users,
  Calendar
} from "lucide-react";

// 더미 데이터
const dummyTriggers = [
  {
    id: 1,
    name: "플러그인 설치 알림",
    description: "새로운 플러그인이 설치될 때 알림을 보냅니다",
    event_type: "plugin_install",
    filter_conditions: { plugin_id: null },
    is_active: true,
    created_at: "2024-01-15T10:30:00Z"
  },
  {
    id: 2,
    name: "플러그인 오류 감지",
    description: "플러그인에서 오류가 발생할 때 관리자에게 알림",
    event_type: "plugin_error",
    filter_conditions: { severity: "high" },
    is_active: true,
    created_at: "2024-01-14T15:20:00Z"
  },
  {
    id: 3,
    name: "사용자 로그인 추적",
    description: "관리자 로그인 시 로그를 기록합니다",
    event_type: "user_login",
    filter_conditions: { user_role: "admin" },
    is_active: false,
    created_at: "2024-01-13T09:15:00Z"
  }
];

const dummyActions = [
  {
    id: 1,
    name: "알림 전송",
    description: "시스템 내 알림을 전송합니다",
    action_type: "notify",
    action_payload: { message: "새로운 플러그인이 설치되었습니다", type: "info" },
    is_active: true,
    created_at: "2024-01-15T10:30:00Z"
  },
  {
    id: 2,
    name: "이메일 알림",
    description: "관리자에게 이메일을 전송합니다",
    action_type: "email",
    action_payload: { to: "admin@example.com", subject: "플러그인 알림", body: "새로운 플러그인이 설치되었습니다" },
    is_active: true,
    created_at: "2024-01-14T15:20:00Z"
  },
  {
    id: 3,
    name: "Slack 알림",
    description: "Slack 채널에 메시지를 전송합니다",
    action_type: "slack",
    action_payload: { webhook_url: "https://hooks.slack.com/...", channel: "#alerts", message: "플러그인 알림" },
    is_active: true,
    created_at: "2024-01-13T09:15:00Z"
  },
  {
    id: 4,
    name: "API 호출",
    description: "외부 API를 호출합니다",
    action_type: "api_call",
    action_payload: { url: "https://api.example.com/webhook", method: "POST", data: { event: "plugin_install" } },
    is_active: false,
    created_at: "2024-01-12T14:45:00Z"
  }
];

const dummyWorkflows = [
  {
    id: 1,
    name: "플러그인 설치 알림 워크플로우",
    description: "플러그인 설치 시 알림을 보내는 워크플로우",
    trigger_id: 1,
    action_id: 1,
    trigger_name: "플러그인 설치 알림",
    action_name: "알림 전송",
    is_active: true,
    execution_order: 1,
    created_at: "2024-01-15T10:30:00Z"
  },
  {
    id: 2,
    name: "오류 감지 및 이메일 알림",
    description: "플러그인 오류 시 이메일로 알림",
    trigger_id: 2,
    action_id: 2,
    trigger_name: "플러그인 오류 감지",
    action_name: "이메일 알림",
    is_active: true,
    execution_order: 1,
    created_at: "2024-01-14T15:20:00Z"
  },
  {
    id: 3,
    name: "Slack 알림 워크플로우",
    description: "중요한 이벤트를 Slack으로 알림",
    trigger_id: 1,
    action_id: 3,
    trigger_name: "플러그인 설치 알림",
    action_name: "Slack 알림",
    is_active: false,
    execution_order: 2,
    created_at: "2024-01-13T09:15:00Z"
  }
];

const dummyAutomationLogs = [
  {
    id: 1,
    workflow_name: "플러그인 설치 알림 워크플로우",
    event_type: "plugin_install",
    action_name: "알림 전송",
    status: "success",
    result: { message: "새로운 플러그인이 설치되었습니다" },
    error_message: null,
    executed_at: "2024-01-15T10:35:00Z"
  },
  {
    id: 2,
    workflow_name: "오류 감지 및 이메일 알림",
    event_type: "plugin_error",
    action_name: "이메일 알림",
    status: "success",
    result: { to: "admin@example.com", subject: "플러그인 오류 알림" },
    error_message: null,
    executed_at: "2024-01-15T09:20:00Z"
  },
  {
    id: 3,
    workflow_name: "Slack 알림 워크플로우",
    event_type: "plugin_install",
    action_name: "Slack 알림",
    status: "failed",
    result: null,
    error_message: "Slack Webhook URL이 유효하지 않습니다",
    executed_at: "2024-01-15T08:15:00Z"
  }
];

const eventTypes = [
  { value: "plugin_install", label: "플러그인 설치", icon: Download },
  { value: "plugin_update", label: "플러그인 업데이트", icon: RefreshCw },
  { value: "plugin_uninstall", label: "플러그인 제거", icon: Trash2 },
  { value: "plugin_execute", label: "플러그인 실행", icon: Play },
  { value: "plugin_error", label: "플러그인 오류", icon: AlertTriangle },
  { value: "user_login", label: "사용자 로그인", icon: Users },
  { value: "user_action", label: "사용자 액션", icon: Activity },
  { value: "system_alert", label: "시스템 알림", icon: Bell },
  { value: "custom", label: "커스텀 이벤트", icon: Code }
];

const actionTypes = [
  { value: "notify", label: "알림 전송", icon: Bell },
  { value: "email", label: "이메일 전송", icon: Mail },
  { value: "slack", label: "Slack 메시지", icon: MessageSquare },
  { value: "api_call", label: "API 호출", icon: Globe },
  { value: "plugin_execute", label: "플러그인 실행", icon: Code },
  { value: "sms", label: "SMS 전송", icon: MessageSquare },
  { value: "custom", label: "커스텀 액션", icon: Settings }
];

export default function PluginAutomationPage() {
  const [triggers, setTriggers] = useState(dummyTriggers);
  const [actions, setActions] = useState(dummyActions);
  const [workflows, setWorkflows] = useState(dummyWorkflows);
  const [automationLogs, setAutomationLogs] = useState(dummyAutomationLogs);
  const [activeTab, setActiveTab] = useState("overview");
  const [isEngineRunning, setIsEngineRunning] = useState(true);

  // 폼 상태들
  const [triggerForm, setTriggerForm] = useState({
    name: "",
    description: "",
    event_type: "",
    filter_conditions: {}
  });

  const [actionForm, setActionForm] = useState({
    name: "",
    description: "",
    action_type: "",
    action_payload: {}
  });

  const [workflowForm, setWorkflowForm] = useState({
    name: "",
    description: "",
    trigger_id: "",
    action_id: "",
    execution_order: 1
  });

  const handleEngineToggle = () => {
    setIsEngineRunning(!isEngineRunning);
    toast.success(`자동화 엔진이 ${!isEngineRunning ? '시작' : '중지'}되었습니다.`);
  };

  const handleCreateTrigger = () => {
    if (!triggerForm.name || !triggerForm.event_type) {
      toast.error("필수 필드를 입력해주세요.");
      return;
    }

    const newTrigger = {
      id: Date.now(),
      ...triggerForm,
      is_active: true,
      created_at: new Date().toISOString()
    };

    setTriggers([...triggers, newTrigger]);
    setTriggerForm({ name: "", description: "", event_type: "", filter_conditions: {} });
    toast.success("트리거가 생성되었습니다.");
  };

  const handleCreateAction = () => {
    if (!actionForm.name || !actionForm.action_type) {
      toast.error("필수 필드를 입력해주세요.");
      return;
    }

    const newAction = {
      id: Date.now(),
      ...actionForm,
      is_active: true,
      created_at: new Date().toISOString()
    };

    setActions([...actions, newAction]);
    setActionForm({ name: "", description: "", action_type: "", action_payload: {} });
    toast.success("액션이 생성되었습니다.");
  };

  const handleCreateWorkflow = () => {
    if (!workflowForm.name || !workflowForm.trigger_id || !workflowForm.action_id) {
      toast.error("필수 필드를 입력해주세요.");
      return;
    }

    const trigger = triggers.find(t => t.id === parseInt(workflowForm.trigger_id));
    const action = actions.find(a => a.id === parseInt(workflowForm.action_id));

    const newWorkflow = {
      id: Date.now(),
      ...workflowForm,
      trigger_name: trigger?.name || "",
      action_name: action?.name || "",
      is_active: true,
      created_at: new Date().toISOString()
    };

    setWorkflows([...workflows, newWorkflow]);
    setWorkflowForm({ name: "", description: "", trigger_id: "", action_id: "", execution_order: 1 });
    toast.success("워크플로우가 생성되었습니다.");
  };

  const handleToggleTrigger = (triggerId: number) => {
    setTriggers(triggers.map(t => 
      t.id === triggerId ? { ...t, is_active: !t.is_active } : t
    ));
    toast.success("트리거 상태가 변경되었습니다.");
  };

  const handleToggleAction = (actionId: number) => {
    setActions(actions.map(a => 
      a.id === actionId ? { ...a, is_active: !a.is_active } : t
    ));
    toast.success("액션 상태가 변경되었습니다.");
  };

  const handleToggleWorkflow = (workflowId: number) => {
    setWorkflows(workflows.map(w => 
      w.id === workflowId ? { ...w, is_active: !w.is_active } : w
    ));
    toast.success("워크플로우 상태가 변경되었습니다.");
  };

  const handleDeleteTrigger = (triggerId: number) => {
    setTriggers(triggers.filter(t => t.id !== triggerId));
    toast.success("트리거가 삭제되었습니다.");
  };

  const handleDeleteAction = (actionId: number) => {
    setActions(actions.filter(a => a.id !== actionId));
    toast.success("액션이 삭제되었습니다.");
  };

  const handleDeleteWorkflow = (workflowId: number) => {
    setWorkflows(workflows.filter(w => w.id !== workflowId));
    toast.success("워크플로우가 삭제되었습니다.");
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "success":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "failed":
        return <XCircle className="h-4 w-4 text-red-500" />;
      case "pending":
        return <Clock className="h-4 w-4 text-yellow-500" />;
      default:
        return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "success":
        return <Badge variant="default" className="bg-green-100 text-green-800">성공</Badge>;
      case "failed":
        return <Badge variant="destructive">실패</Badge>;
      case "pending":
        return <Badge variant="secondary">대기중</Badge>;
      default:
        return <Badge variant="outline">알 수 없음</Badge>;
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">플러그인 자동화 관리</h1>
          <p className="text-muted-foreground">
            이벤트 기반 트리거와 워크플로우를 관리하여 자동화를 구성합니다
          </p>
        </div>
        <Button
          onClick={handleEngineToggle}
          variant={isEngineRunning ? "destructive" : "default"}
          className="flex items-center gap-2"
        >
          {isEngineRunning ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
          {isEngineRunning ? "엔진 중지" : "엔진 시작"}
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">자동화 개요</TabsTrigger>
          <TabsTrigger value="triggers">트리거 관리</TabsTrigger>
          <TabsTrigger value="actions">액션 관리</TabsTrigger>
          <TabsTrigger value="workflows">워크플로우 관리</TabsTrigger>
          <TabsTrigger value="logs">실행 로그</TabsTrigger>
        </TabsList>

        {/* 자동화 개요 */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">활성 트리거</CardTitle>
                <Zap className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{triggers.filter(t => t.is_active).length}</div>
                <p className="text-xs text-muted-foreground">
                  총 {triggers.length}개 중
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">활성 액션</CardTitle>
                <Settings className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{actions.filter(a => a.is_active).length}</div>
                <p className="text-xs text-muted-foreground">
                  총 {actions.length}개 중
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">활성 워크플로우</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{workflows.filter(w => w.is_active).length}</div>
                <p className="text-xs text-muted-foreground">
                  총 {workflows.length}개 중
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">엔진 상태</CardTitle>
                <CheckCircle className={`h-4 w-4 ${isEngineRunning ? 'text-green-500' : 'text-red-500'}`} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {isEngineRunning ? "실행 중" : "중지됨"}
                </div>
                <p className="text-xs text-muted-foreground">
                  자동화 엔진
                </p>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>최근 실행 로그</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {automationLogs.slice(0, 5).map((log) => (
                    <div key={log.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-3">
                        {getStatusIcon(log.status)}
                        <div>
                          <p className="font-medium">{log.workflow_name}</p>
                          <p className="text-sm text-muted-foreground">{log.event_type}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        {getStatusBadge(log.status)}
                        <p className="text-xs text-muted-foreground mt-1">
                          {new Date(log.executed_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>이벤트 타입별 통계</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {eventTypes.slice(0, 5).map((eventType) => {
                    const Icon = eventType.icon;
                    const count = triggers.filter(t => t.event_type === eventType.value).length;
                    return (
                      <div key={eventType.value} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center gap-3">
                          <Icon className="h-4 w-4 text-muted-foreground" />
                          <span>{eventType.label}</span>
                        </div>
                        <Badge variant="outline">{count}개</Badge>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* 트리거 관리 */}
        <TabsContent value="triggers" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>새 트리거 생성</CardTitle>
              <CardDescription>
                이벤트 발생 시 실행될 트리거를 생성합니다
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="trigger-name">트리거 이름</Label>
                  <Input
                    id="trigger-name"
                    value={triggerForm.name}
                    onChange={(e) => setTriggerForm({...triggerForm, name: e.target.value})}
                    placeholder="트리거 이름을 입력하세요"
                  />
                </div>
                <div>
                  <Label htmlFor="trigger-event-type">이벤트 타입</Label>
                  <Select value={triggerForm.event_type} onValueChange={(value) => setTriggerForm({...triggerForm, event_type: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="이벤트 타입을 선택하세요" />
                    </SelectTrigger>
                    <SelectContent>
                      {eventTypes.map((eventType) => {
                        const Icon = eventType.icon;
                        return (
                          <SelectItem key={eventType.value} value={eventType.value}>
                            <div className="flex items-center gap-2">
                              <Icon className="h-4 w-4" />
                              {eventType.label}
                            </div>
                          </SelectItem>
                        );
                      })}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div>
                <Label htmlFor="trigger-description">설명</Label>
                <Textarea
                  id="trigger-description"
                  value={triggerForm.description}
                  onChange={(e) => setTriggerForm({...triggerForm, description: e.target.value})}
                  placeholder="트리거에 대한 설명을 입력하세요"
                />
              </div>
              <Button onClick={handleCreateTrigger} className="flex items-center gap-2">
                <Plus className="h-4 w-4" />
                트리거 생성
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>트리거 목록</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {triggers.map((trigger) => {
                  const eventType = eventTypes.find(et => et.value === trigger.event_type);
                  const Icon = eventType?.icon || Activity;
                  return (
                    <div key={trigger.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center gap-4">
                        <Icon className="h-5 w-5 text-muted-foreground" />
                        <div>
                          <h3 className="font-medium">{trigger.name}</h3>
                          <p className="text-sm text-muted-foreground">{trigger.description}</p>
                          <div className="flex items-center gap-2 mt-1">
                            <Badge variant="outline">{eventType?.label}</Badge>
                            <Badge variant={trigger.is_active ? "default" : "secondary"}>
                              {trigger.is_active ? "활성" : "비활성"}
                            </Badge>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleToggleTrigger(trigger.id)}
                        >
                          {trigger.is_active ? "비활성화" : "활성화"}
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDeleteTrigger(trigger.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 액션 관리 */}
        <TabsContent value="actions" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>새 액션 생성</CardTitle>
              <CardDescription>
                트리거 발생 시 실행될 액션을 생성합니다
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="action-name">액션 이름</Label>
                  <Input
                    id="action-name"
                    value={actionForm.name}
                    onChange={(e) => setActionForm({...actionForm, name: e.target.value})}
                    placeholder="액션 이름을 입력하세요"
                  />
                </div>
                <div>
                  <Label htmlFor="action-type">액션 타입</Label>
                  <Select value={actionForm.action_type} onValueChange={(value) => setActionForm({...actionForm, action_type: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="액션 타입을 선택하세요" />
                    </SelectTrigger>
                    <SelectContent>
                      {actionTypes.map((actionType) => {
                        const Icon = actionType.icon;
                        return (
                          <SelectItem key={actionType.value} value={actionType.value}>
                            <div className="flex items-center gap-2">
                              <Icon className="h-4 w-4" />
                              {actionType.label}
                            </div>
                          </SelectItem>
                        );
                      })}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div>
                <Label htmlFor="action-description">설명</Label>
                <Textarea
                  id="action-description"
                  value={actionForm.description}
                  onChange={(e) => setActionForm({...actionForm, description: e.target.value})}
                  placeholder="액션에 대한 설명을 입력하세요"
                />
              </div>
              <Button onClick={handleCreateAction} className="flex items-center gap-2">
                <Plus className="h-4 w-4" />
                액션 생성
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>액션 목록</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {actions.map((action) => {
                  const actionType = actionTypes.find(at => at.value === action.action_type);
                  const Icon = actionType?.icon || Settings;
                  return (
                    <div key={action.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center gap-4">
                        <Icon className="h-5 w-5 text-muted-foreground" />
                        <div>
                          <h3 className="font-medium">{action.name}</h3>
                          <p className="text-sm text-muted-foreground">{action.description}</p>
                          <div className="flex items-center gap-2 mt-1">
                            <Badge variant="outline">{actionType?.label}</Badge>
                            <Badge variant={action.is_active ? "default" : "secondary"}>
                              {action.is_active ? "활성" : "비활성"}
                            </Badge>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleToggleAction(action.id)}
                        >
                          {action.is_active ? "비활성화" : "활성화"}
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDeleteAction(action.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 워크플로우 관리 */}
        <TabsContent value="workflows" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>새 워크플로우 생성</CardTitle>
              <CardDescription>
                트리거와 액션을 연결하여 워크플로우를 생성합니다
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="workflow-name">워크플로우 이름</Label>
                  <Input
                    id="workflow-name"
                    value={workflowForm.name}
                    onChange={(e) => setWorkflowForm({...workflowForm, name: e.target.value})}
                    placeholder="워크플로우 이름을 입력하세요"
                  />
                </div>
                <div>
                  <Label htmlFor="workflow-trigger">트리거</Label>
                  <Select value={workflowForm.trigger_id} onValueChange={(value) => setWorkflowForm({...workflowForm, trigger_id: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="트리거를 선택하세요" />
                    </SelectTrigger>
                    <SelectContent>
                      {triggers.filter(t => t.is_active).map((trigger) => (
                        <SelectItem key={trigger.id} value={trigger.id.toString()}>
                          {trigger.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="workflow-action">액션</Label>
                  <Select value={workflowForm.action_id} onValueChange={(value) => setWorkflowForm({...workflowForm, action_id: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="액션을 선택하세요" />
                    </SelectTrigger>
                    <SelectContent>
                      {actions.filter(a => a.is_active).map((action) => (
                        <SelectItem key={action.id} value={action.id.toString()}>
                          {action.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="workflow-order">실행 순서</Label>
                  <Input
                    id="workflow-order"
                    type="number"
                    value={workflowForm.execution_order}
                    onChange={(e) => setWorkflowForm({...workflowForm, execution_order: parseInt(e.target.value)})}
                    min="1"
                  />
                </div>
              </div>
              <div>
                <Label htmlFor="workflow-description">설명</Label>
                <Textarea
                  id="workflow-description"
                  value={workflowForm.description}
                  onChange={(e) => setWorkflowForm({...workflowForm, description: e.target.value})}
                  placeholder="워크플로우에 대한 설명을 입력하세요"
                />
              </div>
              <Button onClick={handleCreateWorkflow} className="flex items-center gap-2">
                <Plus className="h-4 w-4" />
                워크플로우 생성
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>워크플로우 목록</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {workflows.map((workflow) => (
                  <div key={workflow.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center gap-4">
                      <Activity className="h-5 w-5 text-muted-foreground" />
                      <div>
                        <h3 className="font-medium">{workflow.name}</h3>
                        <p className="text-sm text-muted-foreground">{workflow.description}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge variant="outline">{workflow.trigger_name}</Badge>
                          <span className="text-muted-foreground">→</span>
                          <Badge variant="outline">{workflow.action_name}</Badge>
                          <Badge variant={workflow.is_active ? "default" : "secondary"}>
                            {workflow.is_active ? "활성" : "비활성"}
                          </Badge>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleToggleWorkflow(workflow.id)}
                      >
                        {workflow.is_active ? "비활성화" : "활성화"}
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDeleteWorkflow(workflow.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 실행 로그 */}
        <TabsContent value="logs" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>자동화 실행 로그</CardTitle>
              <CardDescription>
                워크플로우 실행 결과와 오류 로그를 확인합니다
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {automationLogs.map((log) => (
                  <div key={log.id} className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        {getStatusIcon(log.status)}
                        <h3 className="font-medium">{log.workflow_name}</h3>
                      </div>
                      <div className="flex items-center gap-2">
                        {getStatusBadge(log.status)}
                        <span className="text-sm text-muted-foreground">
                          {new Date(log.executed_at).toLocaleString()}
                        </span>
                      </div>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="font-medium">이벤트:</span> {log.event_type}
                      </div>
                      <div>
                        <span className="font-medium">액션:</span> {log.action_name}
                      </div>
                      <div>
                        <span className="font-medium">결과:</span>
                        {log.result ? (
                          <pre className="text-xs bg-muted p-2 rounded mt-1 overflow-x-auto">
                            {JSON.stringify(log.result, null, 2)}
                          </pre>
                        ) : (
                          <span className="text-muted-foreground">결과 없음</span>
                        )}
                      </div>
                    </div>
                    {log.error_message && (
                      <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                        <div className="flex items-center gap-2 text-red-700">
                          <AlertTriangle className="h-4 w-4" />
                          <span className="font-medium">오류:</span>
                        </div>
                        <p className="text-sm text-red-600 mt-1">{log.error_message}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
} 
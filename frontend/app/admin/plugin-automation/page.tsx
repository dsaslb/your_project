"use client";

import React, { useState } from "react";
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
  Calendar,
  Download,
  RefreshCw
} from "lucide-react";

export default function PluginAutomationPage() {
  const [isEngineActive, setIsEngineActive] = useState(true);
  const [triggers, setTriggers] = useState<any[]>([]);
  const [actions, setActions] = useState<any[]>([]);
  const [workflows, setWorkflows] = useState<any[]>([]);

  const handleEngineToggle = () => {
    setIsEngineActive(!isEngineActive);
    toast.success(`자동화 엔진이 ${!isEngineActive ? '활성화' : '비활성화'}되었습니다.`);
  };

  const handleCreateTrigger = () => {
    const newTrigger = {
      id: Date.now(),
      name: "새 트리거",
      description: "새로 생성된 트리거입니다.",
      event_type: "plugin_install",
      filter_conditions: {},
      is_active: true,
      created_at: new Date().toISOString()
    };

    setTriggers([...triggers, newTrigger]);
    toast.success("트리거가 생성되었습니다.");
  };

  const handleCreateAction = () => {
    const newAction = {
      id: Date.now(),
      name: "새 액션",
      description: "새로 생성된 액션입니다.",
      action_type: "notify",
      action_payload: {},
      is_active: true,
      created_at: new Date().toISOString()
    };

    setActions([...actions, newAction]);
    toast.success("액션이 생성되었습니다.");
  };

  const handleCreateWorkflow = () => {
    const newWorkflow = {
      id: Date.now(),
      name: "새 워크플로우",
      description: "새로 생성된 워크플로우입니다.",
      trigger_id: null,
      action_ids: [],
      is_active: true,
      created_at: new Date().toISOString()
    };

    setWorkflows([...workflows, newWorkflow]);
    toast.success("워크플로우가 생성되었습니다.");
  };

  const handleToggleTrigger = (triggerId: number) => {
    setTriggers(triggers.map(trigger => 
      trigger.id === triggerId 
        ? { ...trigger, is_active: !trigger.is_active }
        : trigger
    ));
  };

  const handleToggleAction = (actionId: number) => {
    setActions(actions.map(action => 
      action.id === actionId 
        ? { ...action, is_active: !action.is_active }
        : action
    ));
  };

  const handleToggleWorkflow = (workflowId: number) => {
    setWorkflows(workflows.map(workflow => 
      workflow.id === workflowId 
        ? { ...workflow, is_active: !workflow.is_active }
        : workflow
    ));
  };

  const handleDeleteTrigger = (triggerId: number) => {
    setTriggers(triggers.filter(trigger => trigger.id !== triggerId));
    toast.success("트리거가 삭제되었습니다.");
  };

  const handleDeleteAction = (actionId: number) => {
    setActions(actions.filter(action => action.id !== actionId));
    toast.success("액션이 삭제되었습니다.");
  };

  const handleDeleteWorkflow = (workflowId: number) => {
    setWorkflows(workflows.filter(workflow => workflow.id !== workflowId));
    toast.success("워크플로우가 삭제되었습니다.");
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'inactive':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'error':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge className="bg-green-100 text-green-800">활성</Badge>;
      case 'inactive':
        return <Badge className="bg-red-100 text-red-800">비활성</Badge>;
      case 'error':
        return <Badge className="bg-yellow-100 text-yellow-800">오류</Badge>;
      default:
        return <Badge className="bg-gray-100 text-gray-800">대기</Badge>;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* 헤더 */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">플러그인 자동화</h1>
            <p className="text-gray-600 mt-1">플러그인 이벤트 기반 자동화 워크플로우를 관리하세요.</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">자동화 엔진:</span>
              <Button
                variant={isEngineActive ? "default" : "outline"}
                size="sm"
                onClick={handleEngineToggle}
                className={isEngineActive ? "bg-green-600 hover:bg-green-700" : ""}
              >
                {isEngineActive ? "활성" : "비활성"}
              </Button>
            </div>
          </div>
        </div>

        {/* 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">총 트리거</CardTitle>
              <Bell className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{triggers.length}</div>
              <p className="text-xs text-muted-foreground">
                활성 트리거 수
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">총 액션</CardTitle>
              <Zap className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{actions.length}</div>
              <p className="text-xs text-muted-foreground">
                활성 액션 수
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">총 워크플로우</CardTitle>
              <Settings className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{workflows.length}</div>
              <p className="text-xs text-muted-foreground">
                활성 워크플로우 수
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">실행 횟수</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">1,234</div>
              <p className="text-xs text-muted-foreground">
                이번 달 실행 횟수
              </p>
            </CardContent>
          </Card>
        </div>

        {/* 메인 콘텐츠 */}
        <Tabs defaultValue="triggers" className="space-y-6">
          <TabsList>
            <TabsTrigger value="triggers">트리거</TabsTrigger>
            <TabsTrigger value="actions">액션</TabsTrigger>
            <TabsTrigger value="workflows">워크플로우</TabsTrigger>
          </TabsList>

          <TabsContent value="triggers" className="space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold">트리거 관리</h2>
              <Button onClick={handleCreateTrigger}>
                <Plus className="h-4 w-4 mr-2" />
                새 트리거 추가
              </Button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {triggers.map((trigger) => (
                <Card key={trigger.id}>
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="text-lg">{trigger.name}</CardTitle>
                        <CardDescription>{trigger.description}</CardDescription>
                      </div>
                      {getStatusIcon(trigger.is_active ? 'active' : 'inactive')}
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-500">이벤트 타입:</span>
                        <span className="font-medium">{trigger.event_type}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-500">상태:</span>
                        {getStatusBadge(trigger.is_active ? 'active' : 'inactive')}
                      </div>
                    </div>
                    <div className="flex gap-2 mt-4">
                      <Button variant="outline" size="sm" className="flex-1">
                        <Edit className="h-4 w-4 mr-2" />
                        수정
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="flex-1"
                        onClick={() => handleToggleTrigger(trigger.id)}
                      >
                        {trigger.is_active ? '비활성화' : '활성화'}
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleDeleteTrigger(trigger.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="actions" className="space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold">액션 관리</h2>
              <Button onClick={handleCreateAction}>
                <Plus className="h-4 w-4 mr-2" />
                새 액션 추가
              </Button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {actions.map((action) => (
                <Card key={action.id}>
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="text-lg">{action.name}</CardTitle>
                        <CardDescription>{action.description}</CardDescription>
                      </div>
                      {getStatusIcon(action.is_active ? 'active' : 'inactive')}
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-500">액션 타입:</span>
                        <span className="font-medium">{action.action_type}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-500">상태:</span>
                        {getStatusBadge(action.is_active ? 'active' : 'inactive')}
                      </div>
                    </div>
                    <div className="flex gap-2 mt-4">
                      <Button variant="outline" size="sm" className="flex-1">
                        <Edit className="h-4 w-4 mr-2" />
                        수정
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="flex-1"
                        onClick={() => handleToggleAction(action.id)}
                      >
                        {action.is_active ? '비활성화' : '활성화'}
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleDeleteAction(action.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="workflows" className="space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold">워크플로우 관리</h2>
              <Button onClick={handleCreateWorkflow}>
                <Plus className="h-4 w-4 mr-2" />
                새 워크플로우 추가
              </Button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {workflows.map((workflow) => (
                <Card key={workflow.id}>
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="text-lg">{workflow.name}</CardTitle>
                        <CardDescription>{workflow.description}</CardDescription>
                      </div>
                      {getStatusIcon(workflow.is_active ? 'active' : 'inactive')}
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-500">트리거:</span>
                        <span className="font-medium">연결됨</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-500">액션:</span>
                        <span className="font-medium">2개 연결됨</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-500">상태:</span>
                        {getStatusBadge(workflow.is_active ? 'active' : 'inactive')}
                      </div>
                    </div>
                    <div className="flex gap-2 mt-4">
                      <Button variant="outline" size="sm" className="flex-1">
                        <Edit className="h-4 w-4 mr-2" />
                        수정
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="flex-1"
                        onClick={() => handleToggleWorkflow(workflow.id)}
                      >
                        {workflow.is_active ? '비활성화' : '활성화'}
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleDeleteWorkflow(workflow.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
} 
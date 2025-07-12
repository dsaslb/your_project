"use client";

import { useState } from "react";
import { Bell, Send, Users, Briefcase } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { toast } from "sonner";

// 더미 데이터
const notifications = [
  { id: 1, time: "09:10", message: "발주 #ORD-002 대기 중", category: "주문", priority: "high" },
  { id: 2, time: "10:30", message: "재고 부족: 쌀", category: "재고", priority: "medium" },
  { id: 3, time: "11:00", message: "직원 출근: 이영희", category: "출근", priority: "low" },
];

const roles = [
  { id: "admin", name: "최고관리자", count: 2 },
  { id: "manager", name: "매장관리자", count: 5 },
  { id: "staff", name: "직원", count: 15 },
  { id: "kitchen", name: "주방직원", count: 8 },
  { id: "service", name: "서비스직원", count: 7 },
];

const departments = [
  { id: "kitchen", name: "주방", count: 8 },
  { id: "service", name: "서비스", count: 7 },
  { id: "management", name: "관리", count: 5 },
  { id: "inventory", name: "재고", count: 3 },
];

const notificationTemplates = [
  { id: "schedule", title: "스케줄 변경", content: "스케줄이 변경되었습니다. 확인해주세요." },
  { id: "inventory", title: "재고 알림", content: "재고가 부족합니다. 발주를 확인해주세요." },
  { id: "order", title: "주문 알림", content: "새로운 주문이 들어왔습니다." },
  { id: "maintenance", title: "점검 알림", content: "장비 점검이 필요합니다." },
];

export default function NotificationsPage() {
  const [activeTab, setActiveTab] = useState("view");
  const [selectedRoles, setSelectedRoles] = useState<string[]>([]);
  const [selectedDepartments, setSelectedDepartments] = useState<string[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState("");
  const [customTitle, setCustomTitle] = useState("");
  const [customContent, setCustomContent] = useState("");
  const [priority, setPriority] = useState("medium");
  const [isSending, setIsSending] = useState(false);

  const handleRoleToggle = (roleId: string) => {
    setSelectedRoles(prev => 
      prev.includes(roleId) 
        ? prev.filter(id => id !== roleId)
        : [...prev, roleId]
    );
  };

  const handleDepartmentToggle = (deptId: string) => {
    setSelectedDepartments(prev => 
      prev.includes(deptId) 
        ? prev.filter(id => id !== deptId)
        : [...prev, deptId]
    );
  };

  const handleTemplateSelect = (templateId: string) => {
    const template = notificationTemplates.find(t => t.id === templateId);
    if (template) {
      setSelectedTemplate(templateId);
      setCustomTitle(template.title);
      setCustomContent(template.content);
    }
  };

  const handleSendNotification = async () => {
    if (!customTitle.trim() || !customContent.trim()) {
      toast("입력 오류", {
        description: "제목과 내용을 모두 입력해주세요.",
      });
      return;
    }

    if (selectedRoles.length === 0 && selectedDepartments.length === 0) {
      toast("수신자 선택 오류", {
        description: "최소 하나의 직책이나 부서를 선택해주세요.",
      });
      return;
    }

    setIsSending(true);
    
    try {
      // API 호출 시뮬레이션
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      toast("알림 전송 완료", {
        description: `${selectedRoles.length + selectedDepartments.length}개 대상에게 알림을 전송했습니다.`,
      });

      // 폼 초기화
      setCustomTitle("");
      setCustomContent("");
      setSelectedRoles([]);
      setSelectedDepartments([]);
      setSelectedTemplate("");
      setPriority("medium");
      
    } catch (error) {
      toast("전송 실패", {
        description: "알림 전송 중 오류가 발생했습니다.",
      });
    } finally {
      setIsSending(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high": return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200";
      case "medium": return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200";
      case "low": return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200";
      default: return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200";
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-2">알림/공지</h1>
      <p className="text-zinc-500 mb-6">알림을 확인하고 새로운 알림을 전송하세요.</p>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">전체 알림</CardTitle>
            <Bell className="h-4 w-4 text-zinc-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{notifications.length}건</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">미읽 알림</CardTitle>
            <Bell className="h-4 w-4 text-zinc-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">3건</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">전체 직원</CardTitle>
            <Users className="h-4 w-4 text-zinc-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">37명</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">부서 수</CardTitle>
            <Briefcase className="h-4 w-4 text-zinc-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">4개</div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="view">알림 확인</TabsTrigger>
          <TabsTrigger value="send">알림 전송</TabsTrigger>
        </TabsList>

        <TabsContent value="view" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5" />
                최근 알림 목록
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {notifications.map((notification) => (
                  <div key={notification.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm text-gray-500">{notification.time}</span>
                        <Badge className={getPriorityColor(notification.priority)}>
                          {notification.priority === "high" ? "긴급" : 
                           notification.priority === "medium" ? "보통" : "낮음"}
                        </Badge>
                        <Badge variant="outline">{notification.category}</Badge>
                      </div>
                      <p className="text-sm">{notification.message}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="send" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Send className="h-5 w-5" />
                새 알림 작성
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* 템플릿 선택 */}
              <div className="space-y-2">
                <Label>알림 템플릿</Label>
                <Select value={selectedTemplate} onValueChange={handleTemplateSelect}>
                  <SelectTrigger>
                    <SelectValue placeholder="템플릿을 선택하세요" />
                  </SelectTrigger>
                  <SelectContent>
                    {notificationTemplates.map((template) => (
                      <SelectItem key={template.id} value={template.id}>
                        {template.title}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* 제목 입력 */}
              <div className="space-y-2">
                <Label htmlFor="title">제목</Label>
                <Input
                  id="title"
                  value={customTitle}
                  onChange={(e) => setCustomTitle(e.target.value)}
                  placeholder="알림 제목을 입력하세요"
                />
              </div>

              {/* 내용 입력 */}
              <div className="space-y-2">
                <Label htmlFor="content">내용</Label>
                <Textarea
                  id="content"
                  value={customContent}
                  onChange={(e) => setCustomContent(e.target.value)}
                  placeholder="알림 내용을 입력하세요"
                  rows={4}
                />
              </div>

              {/* 우선순위 선택 */}
              <div className="space-y-2">
                <Label>우선순위</Label>
                <Select value={priority} onValueChange={setPriority}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">낮음</SelectItem>
                    <SelectItem value="medium">보통</SelectItem>
                    <SelectItem value="high">긴급</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* 수신자 선택 */}
              <div className="space-y-4">
                <div>
                  <Label className="text-base font-medium">직책별 수신자</Label>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mt-2">
                    {roles.map((role) => (
                      <div key={role.id} className="flex items-center space-x-2">
                        <Checkbox
                          id={`role-${role.id}`}
                          checked={selectedRoles.includes(role.id)}
                          onCheckedChange={() => handleRoleToggle(role.id)}
                        />
                        <Label htmlFor={`role-${role.id}`} className="text-sm">
                          {role.name} ({role.count}명)
                        </Label>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <Label className="text-base font-medium">부서별 수신자</Label>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mt-2">
                    {departments.map((dept) => (
                      <div key={dept.id} className="flex items-center space-x-2">
                        <Checkbox
                          id={`dept-${dept.id}`}
                          checked={selectedDepartments.includes(dept.id)}
                          onCheckedChange={() => handleDepartmentToggle(dept.id)}
                        />
                        <Label htmlFor={`dept-${dept.id}`} className="text-sm">
                          {dept.name} ({dept.count}명)
                        </Label>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* 전송 버튼 */}
              <div className="flex justify-end">
                <Button 
                  onClick={handleSendNotification} 
                  disabled={isSending}
                  className="flex items-center gap-2"
                >
                  {isSending ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      전송 중...
                    </>
                  ) : (
                    <>
                      <Send className="h-4 w-4" />
                      알림 전송
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
} 
"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import {
  Sparkles,
  Calendar,
  CheckCircle,
  Clock,
  AlertTriangle,
  Plus,
  Edit,
  Trash2,
  Users,
  MapPin,
  Star,
  FileText,
  Download,
  Upload,
  RefreshCw,
  Filter,
  Search,
  BarChart3,
} from "lucide-react";

// 청소 작업 타입 정의
interface CleaningTask {
  id: string;
  title: string;
  description: string;
  area: string;
  frequency: "daily" | "weekly" | "monthly" | "custom";
  priority: "low" | "medium" | "high";
  assignedTo: string;
  status: "pending" | "in-progress" | "completed" | "overdue";
  dueDate: string;
  completedDate?: string;
  checklist: CleaningChecklist[];
  notes?: string;
}

interface CleaningChecklist {
  id: string;
  item: string;
  completed: boolean;
  completedBy?: string;
  completedAt?: string;
}

// 더미 데이터
const cleaningTasks: CleaningTask[] = [
  {
    id: "1",
    title: "주방 청소",
    description: "주방 전체 청소 및 위생 관리",
    area: "주방",
    frequency: "daily",
    priority: "high",
    assignedTo: "김주방",
    status: "completed",
    dueDate: "2024-01-15",
    completedDate: "2024-01-15",
    checklist: [
      { id: "1-1", item: "조리대 청소", completed: true, completedBy: "김주방", completedAt: "2024-01-15 09:30" },
      { id: "1-2", item: "가스레인지 청소", completed: true, completedBy: "김주방", completedAt: "2024-01-15 09:45" },
      { id: "1-3", item: "냉장고 정리", completed: true, completedBy: "김주방", completedAt: "2024-01-15 10:00" },
      { id: "1-4", item: "바닥 청소", completed: true, completedBy: "김주방", completedAt: "2024-01-15 10:15" },
    ],
  },
  {
    id: "2",
    title: "매장 내부 청소",
    description: "매장 내부 테이블, 의자, 바닥 청소",
    area: "매장 내부",
    frequency: "daily",
    priority: "medium",
    assignedTo: "이서비스",
    status: "in-progress",
    dueDate: "2024-01-15",
    checklist: [
      { id: "2-1", item: "테이블 청소", completed: true, completedBy: "이서비스", completedAt: "2024-01-15 08:30" },
      { id: "2-2", item: "의자 청소", completed: true, completedBy: "이서비스", completedAt: "2024-01-15 08:45" },
      { id: "2-3", item: "바닥 청소", completed: false },
      { id: "2-4", item: "창문 청소", completed: false },
    ],
  },
  {
    id: "3",
    title: "화장실 청소",
    description: "화장실 전체 청소 및 소독",
    area: "화장실",
    frequency: "daily",
    priority: "high",
    assignedTo: "박청소",
    status: "pending",
    dueDate: "2024-01-15",
    checklist: [
      { id: "3-1", item: "변기 청소", completed: false },
      { id: "3-2", item: "세면대 청소", completed: false },
      { id: "3-3", item: "바닥 청소", completed: false },
      { id: "3-4", item: "소독", completed: false },
    ],
  },
  {
    id: "4",
    title: "주차장 청소",
    description: "주차장 쓰레기 수거 및 청소",
    area: "주차장",
    frequency: "weekly",
    priority: "low",
    assignedTo: "최관리",
    status: "overdue",
    dueDate: "2024-01-14",
    checklist: [
      { id: "4-1", item: "쓰레기 수거", completed: false },
      { id: "4-2", item: "바닥 청소", completed: false },
      { id: "4-3", item: "조명 확인", completed: false },
    ],
  },
];

const cleaningAreas = [
  "주방", "매장 내부", "화장실", "주차장", "창고", "사무실", "입구", "테라스"
];

const staffMembers = [
  "김주방", "이서비스", "박청소", "최관리", "정직원", "한매니저"
];

export default function CleaningPage() {
  const [activeTab, setActiveTab] = useState("tasks");
  const [tasks, setTasks] = useState<CleaningTask[]>(cleaningTasks);
  const [selectedTask, setSelectedTask] = useState<CleaningTask | null>(null);
  const [isAddingTask, setIsAddingTask] = useState(false);
  const [newTask, setNewTask] = useState<Partial<CleaningTask>>({
    title: "",
    description: "",
    area: "",
    frequency: "daily",
    priority: "medium",
    assignedTo: "",
    dueDate: "",
    checklist: [],
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed": return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200";
      case "in-progress": return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200";
      case "pending": return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200";
      case "overdue": return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200";
      default: return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200";
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

  const handleAddTask = () => {
    if (!newTask.title || !newTask.area || !newTask.assignedTo || !newTask.dueDate) {
      toast("필수 정보를 입력해주세요.", {
        description: "제목, 구역, 담당자, 마감일을 모두 입력해주세요.",
      });
      return;
    }

    const task: CleaningTask = {
      id: Date.now().toString(),
      title: newTask.title!,
      description: newTask.description || "",
      area: newTask.area!,
      frequency: newTask.frequency!,
      priority: newTask.priority!,
      assignedTo: newTask.assignedTo!,
      status: "pending",
      dueDate: newTask.dueDate!,
      checklist: newTask.checklist || [],
    };

    setTasks([...tasks, task]);
    setNewTask({
      title: "",
      description: "",
      area: "",
      frequency: "daily",
      priority: "medium",
      assignedTo: "",
      dueDate: "",
      checklist: [],
    });
    setIsAddingTask(false);
    
    toast("청소 작업이 추가되었습니다.", {
      description: `${task.title} 작업이 성공적으로 추가되었습니다.`,
    });
  };

  const handleCompleteTask = (taskId: string) => {
    setTasks(tasks.map(task => 
      task.id === taskId 
        ? { ...task, status: "completed", completedDate: new Date().toISOString().split('T')[0] }
        : task
    ));
    
    toast("청소 작업이 완료되었습니다.", {
      description: "작업이 성공적으로 완료 처리되었습니다.",
    });
  };

  const handleCompleteChecklist = (taskId: string, checklistId: string) => {
    setTasks(tasks.map(task => 
      task.id === taskId 
        ? {
            ...task,
            checklist: task.checklist.map(item =>
              item.id === checklistId
                ? { ...item, completed: true, completedBy: "현재 사용자", completedAt: new Date().toISOString() }
                : item
            )
          }
        : task
    ));
  };

  const completedTasks = tasks.filter(task => task.status === "completed");
  const pendingTasks = tasks.filter(task => task.status === "pending");
  const inProgressTasks = tasks.filter(task => task.status === "in-progress");
  const overdueTasks = tasks.filter(task => task.status === "overdue");

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">청소 관리</h1>
          <p className="text-muted-foreground">
            매장 청소 일정과 체크리스트를 관리하세요.
          </p>
        </div>
        <Button onClick={() => setIsAddingTask(true)}>
          <Plus className="h-4 w-4 mr-2" />
          청소 작업 추가
        </Button>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">전체 작업</CardTitle>
            <Sparkles className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{tasks.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">완료</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{completedTasks.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">진행 중</CardTitle>
            <Clock className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{inProgressTasks.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">지연</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{overdueTasks.length}</div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="tasks">청소 작업</TabsTrigger>
          <TabsTrigger value="schedule">일정 관리</TabsTrigger>
          <TabsTrigger value="checklist">체크리스트</TabsTrigger>
          <TabsTrigger value="reports">보고서</TabsTrigger>
        </TabsList>

        {/* 청소 작업 탭 */}
        <TabsContent value="tasks" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* 작업 목록 */}
            <div className="lg:col-span-2 space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold">청소 작업 목록</h2>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm">
                    <Filter className="h-4 w-4 mr-2" />
                    필터
                  </Button>
                  <Button variant="outline" size="sm">
                    <Search className="h-4 w-4 mr-2" />
                    검색
                  </Button>
                </div>
              </div>

              <div className="space-y-4">
                {tasks.map((task) => (
                  <Card key={task.id} className="cursor-pointer hover:shadow-md transition-shadow">
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <h3 className="font-semibold">{task.title}</h3>
                            <Badge className={getStatusColor(task.status)}>
                              {task.status === "completed" && "완료"}
                              {task.status === "in-progress" && "진행 중"}
                              {task.status === "pending" && "대기"}
                              {task.status === "overdue" && "지연"}
                            </Badge>
                            <Badge className={getPriorityColor(task.priority)}>
                              {task.priority === "high" && "높음"}
                              {task.priority === "medium" && "보통"}
                              {task.priority === "low" && "낮음"}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground mb-2">{task.description}</p>
                          <div className="flex items-center gap-4 text-sm text-muted-foreground">
                            <span className="flex items-center gap-1">
                              <MapPin className="h-3 w-3" />
                              {task.area}
                            </span>
                            <span className="flex items-center gap-1">
                              <Users className="h-3 w-3" />
                              {task.assignedTo}
                            </span>
                            <span className="flex items-center gap-1">
                              <Calendar className="h-3 w-3" />
                              {task.dueDate}
                            </span>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          {task.status !== "completed" && (
                            <Button
                              size="sm"
                              onClick={() => handleCompleteTask(task.id)}
                            >
                              <CheckCircle className="h-4 w-4 mr-1" />
                              완료
                            </Button>
                          )}
                          <Button variant="outline" size="sm">
                            <Edit className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>

            {/* 작업 상세 */}
            <div className="space-y-4">
              <h2 className="text-xl font-semibold">작업 상세</h2>
              {selectedTask ? (
                <Card>
                  <CardContent className="p-4">
                    <h3 className="font-semibold mb-2">{selectedTask.title}</h3>
                    <p className="text-sm text-muted-foreground mb-4">{selectedTask.description}</p>
                    
                    <div className="space-y-3">
                      <h4 className="font-medium">체크리스트</h4>
                      {selectedTask.checklist.map((item) => (
                        <div key={item.id} className="flex items-center space-x-2">
                          <Checkbox
                            checked={item.completed}
                            onCheckedChange={() => handleCompleteChecklist(selectedTask.id, item.id)}
                          />
                          <Label className={item.completed ? "line-through text-muted-foreground" : ""}>
                            {item.item}
                          </Label>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ) : (
                <Card>
                  <CardContent className="p-4 text-center text-muted-foreground">
                    작업을 선택하여 상세 정보를 확인하세요.
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </TabsContent>

        {/* 일정 관리 탭 */}
        <TabsContent value="schedule" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                청소 일정 관리
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"].map((day) => (
                  <Card key={day} className="p-4">
                    <h3 className="font-semibold mb-3">{day}</h3>
                    <div className="space-y-2">
                      {tasks
                        .filter(task => task.frequency === "daily" || task.frequency === "weekly")
                        .slice(0, 3)
                        .map((task) => (
                          <div key={task.id} className="flex items-center justify-between p-2 bg-muted rounded">
                            <span className="text-sm">{task.title}</span>
                            <Badge className={getStatusColor(task.status)}>
                              {task.status === "completed" && "완료"}
                              {task.status === "in-progress" && "진행"}
                              {task.status === "pending" && "대기"}
                            </Badge>
                          </div>
                        ))}
                    </div>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 체크리스트 탭 */}
        <TabsContent value="checklist" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                청소 체크리스트
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {cleaningAreas.map((area) => (
                  <div key={area} className="border rounded-lg p-4">
                    <h3 className="font-semibold mb-3">{area} 청소 체크리스트</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {tasks
                        .filter(task => task.area === area)
                        .map((task) => (
                          <div key={task.id} className="space-y-2">
                            <h4 className="font-medium">{task.title}</h4>
                            {task.checklist.map((item) => (
                              <div key={item.id} className="flex items-center space-x-2">
                                <Checkbox
                                  checked={item.completed}
                                  onCheckedChange={() => handleCompleteChecklist(task.id, item.id)}
                                />
                                <Label className={item.completed ? "line-through text-muted-foreground" : ""}>
                                  {item.item}
                                </Label>
                              </div>
                            ))}
                          </div>
                        ))}
                    </div>
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
                <BarChart3 className="h-5 w-5" />
                청소 현황 보고서
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h3 className="font-semibold">구역별 완료율</h3>
                  {cleaningAreas.map((area) => {
                    const areaTasks = tasks.filter(task => task.area === area);
                    const completedTasks = areaTasks.filter(task => task.status === "completed");
                    const completionRate = areaTasks.length > 0 ? (completedTasks.length / areaTasks.length) * 100 : 0;
                    
                    return (
                      <div key={area} className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm">{area}</span>
                          <span className="text-sm font-medium">{completionRate.toFixed(0)}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full"
                            style={{ width: `${completionRate}%` }}
                          ></div>
                        </div>
                      </div>
                    );
                  })}
                </div>
                <div className="space-y-4">
                  <h3 className="font-semibold">담당자별 작업 현황</h3>
                  {staffMembers.map((staff) => {
                    const staffTasks = tasks.filter(task => task.assignedTo === staff);
                    const completedTasks = staffTasks.filter(task => task.status === "completed");
                    
                    return (
                      <div key={staff} className="flex items-center justify-between p-3 border rounded">
                        <span className="font-medium">{staff}</span>
                        <div className="text-right">
                          <div className="text-sm font-medium">{completedTasks.length}/{staffTasks.length}</div>
                          <div className="text-xs text-muted-foreground">완료</div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* 청소 작업 추가 모달 */}
      {isAddingTask && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>청소 작업 추가</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="title">작업 제목 *</Label>
                <Input
                  id="title"
                  value={newTask.title}
                  onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
                  placeholder="청소 작업 제목"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">설명</Label>
                <Textarea
                  id="description"
                  value={newTask.description}
                  onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
                  placeholder="작업에 대한 상세 설명"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>구역 *</Label>
                  <Select
                    value={newTask.area}
                    onValueChange={(value) => setNewTask({ ...newTask, area: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="구역 선택" />
                    </SelectTrigger>
                    <SelectContent>
                      {cleaningAreas.map((area) => (
                        <SelectItem key={area} value={area}>{area}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>담당자 *</Label>
                  <Select
                    value={newTask.assignedTo}
                    onValueChange={(value) => setNewTask({ ...newTask, assignedTo: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="담당자 선택" />
                    </SelectTrigger>
                    <SelectContent>
                      {staffMembers.map((staff) => (
                        <SelectItem key={staff} value={staff}>{staff}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>빈도</Label>
                  <Select
                    value={newTask.frequency}
                    onValueChange={(value: any) => setNewTask({ ...newTask, frequency: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="daily">매일</SelectItem>
                      <SelectItem value="weekly">매주</SelectItem>
                      <SelectItem value="monthly">매월</SelectItem>
                      <SelectItem value="custom">사용자 정의</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>우선순위</Label>
                  <Select
                    value={newTask.priority}
                    onValueChange={(value: any) => setNewTask({ ...newTask, priority: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">낮음</SelectItem>
                      <SelectItem value="medium">보통</SelectItem>
                      <SelectItem value="high">높음</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="dueDate">마감일 *</Label>
                <Input
                  id="dueDate"
                  type="date"
                  value={newTask.dueDate}
                  onChange={(e) => setNewTask({ ...newTask, dueDate: e.target.value })}
                />
              </div>
              <div className="flex gap-2">
                <Button onClick={handleAddTask} className="flex-1">
                  추가
                </Button>
                <Button variant="outline" onClick={() => setIsAddingTask(false)} className="flex-1">
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
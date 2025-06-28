"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { CalendarDays, Plus, Edit, Trash2, Clock } from "lucide-react";

export function ScheduleTable() {
  const [selectedWeek, setSelectedWeek] = useState("2024-01-15");

  const scheduleData = [
    {
      id: 1,
      name: "김서버",
      position: "서빙",
      avatar: "김서",
      schedule: {
        월: { shift: "오전", time: "09:00-17:00", status: "scheduled" },
        화: { shift: "오후", time: "17:00-01:00", status: "scheduled" },
        수: { shift: "휴무", time: "", status: "off" },
        목: { shift: "오전", time: "09:00-17:00", status: "scheduled" },
        금: { shift: "오후", time: "17:00-01:00", status: "scheduled" },
        토: { shift: "종일", time: "09:00-22:00", status: "scheduled" },
        일: { shift: "휴무", time: "", status: "off" },
      },
    },
    {
      id: 2,
      name: "박셰프",
      position: "주방",
      avatar: "박셰",
      schedule: {
        월: { shift: "오전", time: "08:00-16:00", status: "scheduled" },
        화: { shift: "오전", time: "08:00-16:00", status: "scheduled" },
        수: { shift: "오전", time: "08:00-16:00", status: "scheduled" },
        목: { shift: "휴무", time: "", status: "off" },
        금: { shift: "오전", time: "08:00-16:00", status: "scheduled" },
        토: { shift: "종일", time: "08:00-20:00", status: "scheduled" },
        일: { shift: "오후", time: "16:00-24:00", status: "scheduled" },
      },
    },
    {
      id: 3,
      name: "이매니저",
      position: "관리",
      avatar: "이매",
      schedule: {
        월: { shift: "종일", time: "10:00-19:00", status: "scheduled" },
        화: { shift: "종일", time: "10:00-19:00", status: "scheduled" },
        수: { shift: "종일", time: "10:00-19:00", status: "scheduled" },
        목: { shift: "종일", time: "10:00-19:00", status: "scheduled" },
        금: { shift: "종일", time: "10:00-19:00", status: "scheduled" },
        토: { shift: "휴무", time: "", status: "off" },
        일: { shift: "휴무", time: "", status: "off" },
      },
    },
    {
      id: 4,
      name: "정바리스타",
      position: "음료",
      avatar: "정바",
      schedule: {
        월: { shift: "오후", time: "14:00-22:00", status: "scheduled" },
        화: { shift: "오후", time: "14:00-22:00", status: "scheduled" },
        수: { shift: "오후", time: "14:00-22:00", status: "scheduled" },
        목: { shift: "오후", time: "14:00-22:00", status: "scheduled" },
        금: { shift: "오후", time: "14:00-22:00", status: "scheduled" },
        토: { shift: "종일", time: "10:00-22:00", status: "scheduled" },
        일: { shift: "휴무", time: "", status: "off" },
      },
    },
  ];

  const days = ["월", "화", "수", "목", "금", "토", "일"];

  const getShiftBadge = (shift: string, status: string) => {
    if (status === "off") {
      return (
        <Badge variant="secondary" className="bg-gray-100 text-gray-600">
          휴무
        </Badge>
      );
    }

    const variants = {
      오전: "bg-blue-100 text-blue-700 border-blue-200",
      오후: "bg-orange-100 text-orange-700 border-orange-200",
      종일: "bg-green-100 text-green-700 border-green-200",
    };

    return (
      <Badge variant="outline" className={variants[shift as keyof typeof variants] || "bg-gray-100 text-gray-600"}>
        {shift}
      </Badge>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">스케줄 관리</h2>
          <p className="text-gray-500 mt-1">직원 근무 일정을 관리하고 조정하세요</p>
        </div>
        <div className="flex items-center space-x-3">
          <Select value={selectedWeek} onValueChange={setSelectedWeek}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="주차 선택" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="2024-01-08">2024년 1월 1주차</SelectItem>
              <SelectItem value="2024-01-15">2024년 1월 2주차</SelectItem>
              <SelectItem value="2024-01-22">2024년 1월 3주차</SelectItem>
              <SelectItem value="2024-01-29">2024년 1월 4주차</SelectItem>
            </SelectContent>
          </Select>
          <Button>
            <Plus className="h-4 w-4 mr-2" />새 스케줄
          </Button>
        </div>
      </div>

      {/* Weekly Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Clock className="h-4 w-4 text-blue-500" />
              <div>
                <p className="text-sm font-medium">총 근무 시간</p>
                <p className="text-2xl font-bold text-blue-600">248시간</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <CalendarDays className="h-4 w-4 text-green-500" />
              <div>
                <p className="text-sm font-medium">근무 직원</p>
                <p className="text-2xl font-bold text-green-600">4명</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-orange-500 rounded-full"></div>
              <div>
                <p className="text-sm font-medium">오버타임</p>
                <p className="text-2xl font-bold text-orange-600">12시간</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-red-500 rounded-full"></div>
              <div>
                <p className="text-sm font-medium">빈 슬롯</p>
                <p className="text-2xl font-bold text-red-600">2개</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Schedule Table */}
      <Card>
        <CardHeader>
          <CardTitle>주간 스케줄</CardTitle>
          <CardDescription>2024년 1월 15일 - 1월 21일 주간 근무 일정</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-48">직원</TableHead>
                  {days.map((day) => (
                    <TableHead key={day} className="text-center min-w-32">
                      {day}요일
                    </TableHead>
                  ))}
                  <TableHead className="w-24">액션</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {scheduleData.map((employee) => (
                  <TableRow key={employee.id}>
                    <TableCell>
                      <div className="flex items-center space-x-3">
                        <Avatar className="h-10 w-10">
                          <AvatarFallback>{employee.avatar}</AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="font-medium">{employee.name}</p>
                          <p className="text-sm text-gray-500">{employee.position}</p>
                        </div>
                      </div>
                    </TableCell>
                    {days.map((day) => {
                      const daySchedule = employee.schedule[day];
                      return (
                        <TableCell key={day} className="text-center">
                          <div className="space-y-1">
                            {getShiftBadge(daySchedule.shift, daySchedule.status)}
                            {daySchedule.time && <p className="text-xs text-gray-500">{daySchedule.time}</p>}
                          </div>
                        </TableCell>
                      );
                    })}
                    <TableCell>
                      <div className="flex space-x-1">
                        <Button variant="ghost" size="sm">
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="sm">
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* Shift Legend */}
      <Card>
        <CardHeader>
          <CardTitle>근무 시간 안내</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="flex items-center space-x-2">
              <Badge variant="outline" className="bg-blue-100 text-blue-700 border-blue-200">
                오전
              </Badge>
              <span className="text-sm text-gray-600">08:00 - 17:00</span>
            </div>
            <div className="flex items-center space-x-2">
              <Badge variant="outline" className="bg-orange-100 text-orange-700 border-orange-200">
                오후
              </Badge>
              <span className="text-sm text-gray-600">17:00 - 01:00</span>
            </div>
            <div className="flex items-center space-x-2">
              <Badge variant="outline" className="bg-green-100 text-green-700 border-green-200">
                종일
              </Badge>
              <span className="text-sm text-gray-600">08:00 - 22:00</span>
            </div>
            <div className="flex items-center space-x-2">
              <Badge variant="secondary" className="bg-gray-100 text-gray-600">
                휴무
              </Badge>
              <span className="text-sm text-gray-600">근무 없음</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 
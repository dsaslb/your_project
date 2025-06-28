"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ChevronLeft, ChevronRight, Plus, Calendar, Users, Sparkles } from "lucide-react";

export function ScheduleCalendar() {
  const [currentDate, setCurrentDate] = useState(new Date(2024, 0, 15));
  const [viewMode, setViewMode] = useState<"month" | "week">("month");

  const staffData = [
    { id: 1, name: "김서버", position: "서빙", avatar: "김서", color: "from-blue-500 to-cyan-500" },
    { id: 2, name: "박셰프", position: "주방", avatar: "박셰", color: "from-red-500 to-orange-500" },
    { id: 3, name: "이매니저", position: "관리", avatar: "이매", color: "from-purple-500 to-pink-500" },
    { id: 4, name: "정바리스타", position: "음료", avatar: "정바", color: "from-green-500 to-emerald-500" },
  ];

  const scheduleData = {
    "2024-01-15": [
      { staffId: 1, shift: "오전", time: "09:00-17:00", type: "scheduled" },
      { staffId: 2, shift: "오전", time: "08:00-16:00", type: "scheduled" },
      { staffId: 3, shift: "종일", time: "10:00-19:00", type: "scheduled" },
    ],
    "2024-01-16": [
      { staffId: 1, shift: "오후", time: "17:00-01:00", type: "scheduled" },
      { staffId: 2, shift: "오전", time: "08:00-16:00", type: "scheduled" },
      { staffId: 4, shift: "오후", time: "14:00-22:00", type: "scheduled" },
    ],
    "2024-01-17": [
      { staffId: 2, shift: "오전", time: "08:00-16:00", type: "scheduled" },
      { staffId: 3, shift: "종일", time: "10:00-19:00", type: "scheduled" },
      { staffId: 4, shift: "오후", time: "14:00-22:00", type: "scheduled" },
    ],
  };

  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    const days = [];

    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null);
    }

    for (let day = 1; day <= daysInMonth; day++) {
      days.push(new Date(year, month, day));
    }

    return days;
  };

  const getWeekDays = (date: Date) => {
    const startOfWeek = new Date(date);
    const day = startOfWeek.getDay();
    const diff = startOfWeek.getDate() - day;
    startOfWeek.setDate(diff);

    const days = [];
    for (let i = 0; i < 7; i++) {
      const day = new Date(startOfWeek);
      day.setDate(startOfWeek.getDate() + i);
      days.push(day);
    }
    return days;
  };

  const formatDateKey = (date: Date) => {
    return date.toISOString().split("T")[0];
  };

  const getScheduleForDate = (date: Date) => {
    const dateKey = formatDateKey(date);
    return scheduleData[dateKey as keyof typeof scheduleData] || [];
  };

  const getShiftColor = (shift: string) => {
    const colors = {
      오전: "from-blue-500 to-cyan-500",
      오후: "from-orange-500 to-red-500",
      종일: "from-green-500 to-emerald-500",
    };
    return colors[shift as keyof typeof colors] || "from-gray-500 to-gray-600";
  };

  const navigateMonth = (direction: "prev" | "next") => {
    const newDate = new Date(currentDate);
    newDate.setMonth(currentDate.getMonth() + (direction === "next" ? 1 : -1));
    setCurrentDate(newDate);
  };

  const navigateWeek = (direction: "prev" | "next") => {
    const newDate = new Date(currentDate);
    newDate.setDate(currentDate.getDate() + (direction === "next" ? 7 : -7));
    setCurrentDate(newDate);
  };

  const monthNames = ["1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월"];
  const dayNames = ["일", "월", "화", "수", "목", "금", "토"];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            스케줄 캘린더
          </h2>
          <p className="text-gray-500 dark:text-gray-400 mt-1">직원 근무 일정을 시각적으로 관리하세요</p>
        </div>
        <div className="flex items-center space-x-3">
          <Select value={viewMode} onValueChange={(value: "month" | "week") => setViewMode(value)}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="month">월간 보기</SelectItem>
              <SelectItem value="week">주간 보기</SelectItem>
            </SelectContent>
          </Select>
          <Button className="bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white shadow-lg">
            <Plus className="h-4 w-4 mr-2" />새 스케줄
          </Button>
        </div>
      </div>

      <Card className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-0 shadow-lg">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => (viewMode === "month" ? navigateMonth("prev") : navigateWeek("prev"))}
                className="hover:bg-blue-50 dark:hover:bg-blue-900/20"
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <h3 className="text-xl font-semibold">
                {currentDate.getFullYear()}년 {monthNames[currentDate.getMonth()]}
                {viewMode === "week" && ` ${Math.ceil(currentDate.getDate() / 7)}주차`}
              </h3>
              <Button
                variant="outline"
                size="sm"
                onClick={() => (viewMode === "month" ? navigateMonth("next") : navigateWeek("next"))}
                className="hover:bg-blue-50 dark:hover:bg-blue-900/20"
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
                <Calendar className="h-4 w-4" />
                <span>총 {Object.keys(scheduleData).length}일 스케줄</span>
              </div>
              <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
                <Users className="h-4 w-4" />
                <span>{staffData.length}명 직원</span>
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {viewMode === "month" ? (
            <div className="grid grid-cols-7 gap-1">
              {dayNames.map((day) => (
                <div key={day} className="p-3 text-center text-sm font-medium text-gray-500 dark:text-gray-400">
                  {day}
                </div>
              ))}

              {getDaysInMonth(currentDate).map((day, index) => (
                <div
                  key={index}
                  className={`min-h-32 p-2 border border-gray-100 dark:border-gray-800 rounded-lg transition-all duration-200 ${
                    day
                      ? "bg-white dark:bg-gray-900 hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer"
                      : "bg-gray-50 dark:bg-gray-800/50"
                  }`}
                >
                  {day && (
                    <>
                      <div className="text-sm font-medium text-gray-900 dark:text-white mb-2">{day.getDate()}</div>
                      <div className="space-y-1">
                        {getScheduleForDate(day).map((schedule, scheduleIndex) => {
                          const staff = staffData.find((s) => s.id === schedule.staffId);
                          return (
                            <div
                              key={scheduleIndex}
                              className={`text-xs p-1 rounded bg-gradient-to-r ${getShiftColor(schedule.shift)} text-white shadow-sm`}
                            >
                              <div className="font-medium">{staff?.name}</div>
                              <div className="opacity-90">{schedule.shift}</div>
                            </div>
                          );
                        })}
                      </div>
                    </>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-4">
              <div className="grid grid-cols-8 gap-4">
                <div className="text-sm font-medium text-gray-500 dark:text-gray-400 p-2">직원</div>
                {getWeekDays(currentDate).map((day, index) => (
                  <div key={index} className="text-center">
                    <div className="text-sm font-medium text-gray-900 dark:text-white">{dayNames[day.getDay()]}</div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">{day.getDate()}</div>
                  </div>
                ))}
              </div>

              {staffData.map((staff) => (
                <div key={staff.id} className="grid grid-cols-8 gap-4 items-center">
                  <div className="flex items-center space-x-2 p-2">
                    <Avatar className="h-8 w-8">
                      <AvatarFallback className={`bg-gradient-to-r ${staff.color} text-white text-xs`}>
                        {staff.avatar}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <div className="text-sm font-medium">{staff.name}</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">{staff.position}</div>
                    </div>
                  </div>

                  {getWeekDays(currentDate).map((day, dayIndex) => {
                    const daySchedule = getScheduleForDate(day).find((s) => s.staffId === staff.id);
                    return (
                      <div key={dayIndex} className="p-2 min-h-16 bg-gray-50 dark:bg-gray-800 rounded-lg">
                        {daySchedule && (
                          <div
                            className={`p-2 rounded bg-gradient-to-r ${getShiftColor(daySchedule.shift)} text-white text-xs shadow-sm`}
                          >
                            <div className="font-medium">{daySchedule.shift}</div>
                            <div className="opacity-90">{daySchedule.time}</div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-0 shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Users className="h-5 w-5 text-blue-500" />
              <span>직원 목록</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-3">
              {staffData.map((staff) => (
                <div key={staff.id} className="flex items-center space-x-2 p-2 rounded-lg bg-gray-50 dark:bg-gray-800">
                  <Avatar className="h-8 w-8">
                    <AvatarFallback className={`bg-gradient-to-r ${staff.color} text-white text-xs`}>
                      {staff.avatar}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <div className="text-sm font-medium">{staff.name}</div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">{staff.position}</div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-0 shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Sparkles className="h-5 w-5 text-purple-500" />
              <span>근무 시간 안내</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <div className="w-4 h-4 rounded bg-gradient-to-r from-blue-500 to-cyan-500"></div>
                <span className="text-sm font-medium">오전 근무</span>
                <span className="text-xs text-gray-500 dark:text-gray-400">08:00 - 17:00</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-4 h-4 rounded bg-gradient-to-r from-orange-500 to-red-500"></div>
                <span className="text-sm font-medium">오후 근무</span>
                <span className="text-xs text-gray-500 dark:text-gray-400">17:00 - 01:00</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-4 h-4 rounded bg-gradient-to-r from-green-500 to-emerald-500"></div>
                <span className="text-sm font-medium">종일 근무</span>
                <span className="text-xs text-gray-500 dark:text-gray-400">08:00 - 22:00</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 
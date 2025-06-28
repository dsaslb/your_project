"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Clock, CheckCircle, XCircle, AlertCircle, Calendar } from "lucide-react";

export function AttendanceTracker() {
  const [selectedDate, setSelectedDate] = useState("2024-01-15");

  const attendanceData = [
    {
      id: 1,
      name: "김서버",
      position: "서빙",
      avatar: "김서",
      scheduledIn: "09:00",
      scheduledOut: "17:00",
      actualIn: "08:55",
      actualOut: "17:10",
      status: "present",
      totalHours: "8.25",
      overtime: "0.25",
    },
    {
      id: 2,
      name: "박셰프",
      position: "주방장",
      avatar: "박셰",
      scheduledIn: "08:00",
      scheduledOut: "16:00",
      actualIn: "07:50",
      actualOut: "16:05",
      status: "present",
      totalHours: "8.25",
      overtime: "0.25",
    },
    {
      id: 3,
      name: "이매니저",
      position: "매니저",
      avatar: "이매",
      scheduledIn: "10:00",
      scheduledOut: "19:00",
      actualIn: "10:15",
      actualOut: "19:00",
      status: "late",
      totalHours: "8.75",
      overtime: "0",
    },
    {
      id: 4,
      name: "정바리스타",
      position: "바리스타",
      avatar: "정바",
      scheduledIn: "14:00",
      scheduledOut: "22:00",
      actualIn: "14:00",
      actualOut: "",
      status: "working",
      totalHours: "",
      overtime: "",
    },
    {
      id: 5,
      name: "최서빙",
      position: "서빙",
      avatar: "최서",
      scheduledIn: "17:00",
      scheduledOut: "01:00",
      actualIn: "",
      actualOut: "",
      status: "absent",
      totalHours: "",
      overtime: "",
    },
  ];

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      present: {
        label: "출근",
        className: "bg-green-100 text-green-700 border-green-200",
        icon: CheckCircle,
      },
      late: {
        label: "지각",
        className: "bg-yellow-100 text-yellow-700 border-yellow-200",
        icon: AlertCircle,
      },
      working: {
        label: "근무중",
        className: "bg-blue-100 text-blue-700 border-blue-200",
        icon: Clock,
      },
      absent: {
        label: "결근",
        className: "bg-red-100 text-red-700 border-red-200",
        icon: XCircle,
      },
    };

    const config = statusConfig[status as keyof typeof statusConfig];
    const Icon = config.icon;

    return (
      <Badge variant="outline" className={config.className}>
        <Icon className="h-3 w-3 mr-1" />
        {config.label}
      </Badge>
    );
  };

  const summaryStats = {
    totalScheduled: attendanceData.length,
    present: attendanceData.filter((a) => a.status === "present" || a.status === "late" || a.status === "working")
      .length,
    late: attendanceData.filter((a) => a.status === "late").length,
    absent: attendanceData.filter((a) => a.status === "absent").length,
    totalHours: attendanceData.reduce((sum, a) => sum + (Number.parseFloat(a.totalHours) || 0), 0),
    totalOvertime: attendanceData.reduce((sum, a) => sum + (Number.parseFloat(a.overtime) || 0), 0),
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white">출석 관리</h2>
          <p className="text-gray-500 dark:text-gray-400 mt-1">직원 출퇴근 현황을 확인하고 관리하세요</p>
        </div>
        <div className="flex items-center space-x-3">
          <Select value={selectedDate} onValueChange={setSelectedDate}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="날짜 선택" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="2024-01-15">2024년 1월 15일</SelectItem>
              <SelectItem value="2024-01-14">2024년 1월 14일</SelectItem>
              <SelectItem value="2024-01-13">2024년 1월 13일</SelectItem>
            </SelectContent>
          </Select>
          <Button>
            <Calendar className="h-4 w-4 mr-2" />
            출석 보고서
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <p className="text-sm font-medium text-gray-600">예정 인원</p>
              <p className="text-2xl font-bold text-gray-900">{summaryStats.totalScheduled}명</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <p className="text-sm font-medium text-gray-600">출근</p>
              <p className="text-2xl font-bold text-green-600">{summaryStats.present}명</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <p className="text-sm font-medium text-gray-600">지각</p>
              <p className="text-2xl font-bold text-yellow-600">{summaryStats.late}명</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <p className="text-sm font-medium text-gray-600">결근</p>
              <p className="text-2xl font-bold text-red-600">{summaryStats.absent}명</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <p className="text-sm font-medium text-gray-600">총 근무시간</p>
              <p className="text-2xl font-bold text-blue-600">{summaryStats.totalHours.toFixed(1)}h</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <p className="text-sm font-medium text-gray-600">초과근무</p>
              <p className="text-2xl font-bold text-orange-600">{summaryStats.totalOvertime.toFixed(1)}h</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>일일 출석 현황</CardTitle>
          <CardDescription>{selectedDate} 출퇴근 기록</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>직원</TableHead>
                  <TableHead className="text-center">예정 출근</TableHead>
                  <TableHead className="text-center">실제 출근</TableHead>
                  <TableHead className="text-center">예정 퇴근</TableHead>
                  <TableHead className="text-center">실제 퇴근</TableHead>
                  <TableHead className="text-center">총 근무시간</TableHead>
                  <TableHead className="text-center">초과근무</TableHead>
                  <TableHead className="text-center">상태</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {attendanceData.map((record) => (
                  <TableRow key={record.id}>
                    <TableCell>
                      <div className="flex items-center space-x-3">
                        <Avatar className="h-10 w-10">
                          <AvatarFallback>{record.avatar}</AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="font-medium">{record.name}</p>
                          <p className="text-sm text-gray-500">{record.position}</p>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="text-center font-mono">{record.scheduledIn}</TableCell>
                    <TableCell className="text-center font-mono">
                      <span
                        className={
                          record.actualIn && record.actualIn > record.scheduledIn ? "text-red-600" : "text-green-600"
                        }
                      >
                        {record.actualIn || "-"}
                      </span>
                    </TableCell>
                    <TableCell className="text-center font-mono">{record.scheduledOut}</TableCell>
                    <TableCell className="text-center font-mono">
                      {record.actualOut || (record.status === "working" ? "근무중" : "-")}
                    </TableCell>
                    <TableCell className="text-center font-mono">
                      {record.totalHours ? `${record.totalHours}시간` : "-"}
                    </TableCell>
                    <TableCell className="text-center font-mono">
                      {record.overtime && Number.parseFloat(record.overtime) > 0 ? (
                        <span className="text-orange-600">+{record.overtime}시간</span>
                      ) : record.overtime === "" ? (
                        "-"
                      ) : (
                        "0시간"
                      )}
                    </TableCell>
                    <TableCell className="text-center">{getStatusBadge(record.status)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 
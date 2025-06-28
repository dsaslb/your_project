"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarInset,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import {
  Calendar,
  Users,
  Clock,
  TrendingUp,
  ChefHat,
  DollarSign,
  UserCheck,
  CalendarDays,
  Settings,
  Bell,
  Sparkles,
  Activity,
  AlertTriangle,
  Package,
  Home,
} from "lucide-react";
import { ScheduleCalendar } from "./schedule-calendar";
import { StaffManagement } from "./staff-management";
import { AttendanceTracker } from "./AttendanceTracker";
import { MenuManagement } from "./MenuManagement";
import { OrderManagement } from "./OrderManagement";
import { ThemeToggle } from "./ThemeToggle";

const menuItems = [
  { title: "대시보드", url: "#", icon: Home, id: "dashboard" },
  { title: "스케줄 관리", url: "#", icon: CalendarDays, id: "schedule" },
  { title: "직원 관리", url: "#", icon: Users, id: "staff" },
  { title: "출석 관리", url: "#", icon: Clock, id: "attendance" },
  { title: "메뉴 관리", url: "#", icon: ChefHat, id: "menu" },
  { title: "주문 관리", url: "#", icon: Package, id: "orders" },
];

export function RestaurantDashboard() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <Sidebar variant="inset">
          <SidebarHeader>
            <div className="flex items-center space-x-2 px-4 py-2">
              <div className="relative group">
                <div className="absolute inset-0 bg-gradient-to-r from-orange-500 via-pink-500 to-purple-500 rounded-xl blur-lg opacity-75 group-hover:opacity-100 transition-opacity animate-pulse"></div>
                <ChefHat className="relative h-8 w-8 text-white bg-gradient-to-r from-orange-500 via-pink-500 to-purple-500 p-2 rounded-xl shadow-lg" />
              </div>
              <div>
                <h1 className="text-lg font-bold bg-gradient-to-r from-gray-900 via-blue-800 to-purple-800 dark:from-white dark:via-blue-200 dark:to-purple-200 bg-clip-text text-transparent">
                  Restaurant Manager
                </h1>
                <p className="text-xs text-gray-500 dark:text-gray-400">운영 관리 시스템</p>
              </div>
            </div>
          </SidebarHeader>
          <SidebarContent>
            <SidebarGroup>
              <SidebarGroupLabel>메뉴</SidebarGroupLabel>
              <SidebarGroupContent>
                <SidebarMenu>
                  {menuItems.map((item) => (
                    <SidebarMenuItem key={item.id}>
                      <SidebarMenuButton
                        onClick={() => setActiveTab(item.id)}
                        isActive={activeTab === item.id}
                        className="w-full"
                      >
                        <item.icon className="h-4 w-4" />
                        <span>{item.title}</span>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          </SidebarContent>
        </Sidebar>

        <SidebarInset>
          {/* Header */}
          <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4 bg-white/90 dark:bg-gray-900/90 backdrop-blur-xl">
            <SidebarTrigger className="-ml-1" />
            <div className="flex flex-1 items-center justify-between">
              <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
                <Activity className="h-4 w-4" />
                <span>실시간 운영 관리</span>
                <Badge className="bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 text-xs">
                  LIVE
                </Badge>
              </div>
              <div className="flex items-center space-x-4">
                <div className="hidden md:flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-800 px-3 py-2 rounded-lg">
                  <Clock className="h-4 w-4" />
                  <span>{currentTime.toLocaleTimeString("ko-KR")}</span>
                </div>
                <ThemeToggle />
                <Button variant="outline" size="sm" className="relative bg-transparent">
                  <Bell className="h-4 w-4 mr-2" />
                  알림
                  <Badge className="ml-2 bg-red-500 text-white text-xs">3</Badge>
                </Button>
                <Button variant="outline" size="sm">
                  <Settings className="h-4 w-4 mr-2" />
                  설정
                </Button>
                <Avatar className="ring-2 ring-orange-500/30">
                  <AvatarImage src="/placeholder.svg?height=32&width=32" />
                  <AvatarFallback className="bg-gradient-to-r from-orange-500 to-pink-500 text-white">
                    관리자
                  </AvatarFallback>
                </Avatar>
              </div>
            </div>
          </header>

          {/* Main Content */}
          <main className="flex-1 p-6">
            {activeTab === "dashboard" && (
              <div className="space-y-6">
                <AttendanceTracker />
                <MenuManagement />
                <OrderManagement />
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                  <div className="bg-[hsl(var(--card))] text-[hsl(var(--card-foreground))] rounded-2xl shadow-md p-6">
                    <div className="text-lg font-bold">오늘 매출</div>
                    <div className="text-3xl mt-2">₩1,200,000</div>
                  </div>
                  <div className="bg-[hsl(var(--card))] text-[hsl(var(--card-foreground))] rounded-2xl shadow-md p-6">
                    <div className="text-lg font-bold">방문 고객</div>
                    <div className="text-3xl mt-2">85명</div>
                  </div>
                  <div className="bg-[hsl(var(--card))] text-[hsl(var(--card-foreground))] rounded-2xl shadow-md p-6">
                    <div className="text-lg font-bold">신규 예약</div>
                    <div className="text-3xl mt-2">12건</div>
                  </div>
                </div>
                <div className="bg-[hsl(var(--card))] text-[hsl(var(--card-foreground))] rounded-2xl shadow-md p-6">
                  <div className="text-lg font-bold mb-4">직원 출근 현황</div>
                  <table className="min-w-full">
                    <thead className="bg-[hsl(var(--muted))]">
                      <tr>
                        <th className="p-3 text-left">직원명</th>
                        <th className="p-3 text-left">출근</th>
                        <th className="p-3 text-left">퇴근</th>
                        <th className="p-3 text-left">상태</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-t border-[hsl(var(--border))]">
                        <td className="p-3">홍길동</td>
                        <td className="p-3">09:00</td>
                        <td className="p-3">18:00</td>
                        <td className="p-3 text-green-600">출근</td>
                      </tr>
                      <tr className="border-t border-[hsl(var(--border))]">
                        <td className="p-3">김철수</td>
                        <td className="p-3">09:30</td>
                        <td className="p-3">18:30</td>
                        <td className="p-3 text-yellow-600">지각</td>
                      </tr>
                      <tr className="border-t border-[hsl(var(--border))]">
                        <td className="p-3">이영희</td>
                        <td className="p-3">-</td>
                        <td className="p-3">-</td>
                        <td className="p-3 text-red-600">결근</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            )}
            {activeTab === "schedule" && <ScheduleCalendar />}
            {activeTab === "staff" && <StaffManagement />}
            {activeTab === "attendance" && <AttendanceTracker />}
            {activeTab === "menu" && <MenuManagement />}
            {activeTab === "orders" && <OrderManagement />}
          </main>
        </SidebarInset>
      </div>
    </SidebarProvider>
  );
} 
"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Sidebar } from "@/components/ui/Sidebar";
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
import { useRouter } from "next/navigation";

const menuItems = [
  { title: "대시보드", url: "/dashboard", icon: Home, id: "dashboard" },
  { title: "스케줄 관리", url: "/schedule", icon: CalendarDays, id: "schedule" },
  { title: "직원 관리", url: "/employees", icon: Users, id: "staff" },
  { title: "출석 관리", url: "/attendance", icon: Clock, id: "attendance" },
  { title: "메뉴 관리", url: "/menu", icon: ChefHat, id: "menu" },
  { title: "주문 관리", url: "/orders", icon: Package, id: "orders" },
];

export function RestaurantDashboard() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [currentTime, setCurrentTime] = useState(new Date());
  const router = useRouter();

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <Sidebar>
      {/* 여기에 대시보드, 메뉴, 헤더 등 원하는 컴포넌트/레이아웃 작성 */}
    </Sidebar>
  );
} 
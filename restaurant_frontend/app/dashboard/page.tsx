"use client"

import React, { useState, useEffect } from 'react'
import { DashboardLayout } from "@/components/dashboard-layout"
import { DashboardContentFull } from "@/components/dashboard-content-full"
import { DashboardHeader } from "@/components/dashboard-header-full"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  DollarSign, 
  Users, 
  ShoppingCart, 
  ChefHat,
  Utensils,
  Package,
  TrendingUp,
  TrendingDown,
  Clock,
  Bell,
  AlertCircle,
  AlertTriangle,
  Settings,
  FileText,
  CheckCircle,
  Activity,
  Calendar
} from "lucide-react"
import { useUser } from '@/components/UserContext'
import { toast } from '@/lib/toast'
import NotificationService from '@/lib/notification-service'
import { useRealtime, useRealtimeEvent } from '@/lib/realtime-service'
import { useNotifications } from '@/components/NotificationSystem'
import { apiClient } from '@/lib/api-client'

interface DashboardStats {
  totalOrders: number;
  pendingOrders: number;
  completedOrders: number;
  totalRevenue: number;
  totalStaff: number;
  activeStaff: number;
  inventoryItems: number;
  lowStockItems: number;
  todaySales: number;
  weeklyGrowth: number;
}

interface RecentActivity {
  id: string;
  type: string;
  title: string;
  description: string;
  timestamp: string;
  status: 'success' | 'warning' | 'error' | 'info';
}

export default function DashboardPage() {
  const [isNavOpen, setIsNavOpen] = useState(false);

  // AppLayout을 우회하기 위해 전체 페이지 구조를 직접 구성
  return (
    <div className="min-h-screen bg-background">
      <DashboardLayout>
        <DashboardHeader onToggleNav={() => setIsNavOpen(!isNavOpen)} />
        <DashboardContentFull />
      </DashboardLayout>
    </div>
  )
} 
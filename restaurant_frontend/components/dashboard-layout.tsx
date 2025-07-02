"use client"

import { useState } from "react"
import { DashboardHeader } from "@/components/dashboard-header-full"
import { DashboardContentFull } from "@/components/dashboard-content-full"
import { QuickNavigation } from "@/components/quick-navigation"

export function DashboardLayout() {
  const [showQuickNav, setShowQuickNav] = useState(false)

  return (
    <div className="min-h-screen bg-gray-50/50 dark:bg-gray-900/50">
      <DashboardHeader onToggleNav={() => setShowQuickNav(!showQuickNav)} />
      <DashboardContentFull />
      <QuickNavigation isOpen={showQuickNav} onClose={() => setShowQuickNav(false)} />
    </div>
  )
} 
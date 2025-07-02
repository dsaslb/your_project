"use client"

import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet"
import { Button } from "@/components/ui/button"
import { 
  Calendar, 
  Users, 
  Package, 
  ClipboardList, 
  BarChart3, 
  Settings,
  Home,
  Bell
} from "lucide-react"
import Link from "next/link"

interface QuickNavigationProps {
  isOpen: boolean
  onClose: () => void
}

export function QuickNavigation({ isOpen, onClose }: QuickNavigationProps) {
  const quickMenuItems = [
    { icon: Home, label: "대시보드", href: "/dashboard" },
    { icon: Calendar, label: "스케줄 관리", href: "/schedule" },
    { icon: Users, label: "직원 관리", href: "/staff" },
    { icon: Package, label: "발주 관리", href: "/orders" },
    { icon: ClipboardList, label: "재고 관리", href: "/inventory" },
    { icon: BarChart3, label: "통계/리포트", href: "/reports" },
    { icon: Settings, label: "설정", href: "/settings" },
    { icon: Bell, label: "알림", href: "/notifications" },
  ]

  return (
    <Sheet open={isOpen} onOpenChange={onClose}>
      <SheetContent side="right" className="w-80">
        <SheetHeader>
          <SheetTitle>빠른 메뉴</SheetTitle>
        </SheetHeader>
        
        <div className="mt-6 space-y-2">
          {quickMenuItems.map((item) => {
            const Icon = item.icon
            return (
              <Link key={item.href} href={item.href} onClick={onClose}>
                <Button
                  variant="ghost"
                  className="w-full justify-start gap-3 h-12"
                >
                  <Icon className="h-5 w-5" />
                  {item.label}
                </Button>
              </Link>
            )
          })}
        </div>
      </SheetContent>
    </Sheet>
  )
} 
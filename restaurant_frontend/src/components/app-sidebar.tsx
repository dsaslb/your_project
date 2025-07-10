import { Calendar, ChefHat, Home, Settings, TrendingUp, Users, UtensilsCrossed, Wallet, Activity } from "lucide-react"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from "@/components/ui/sidebar"
import Link from "next/link"

const menuItems = [
  {
    title: "Dashboard",
    url: "/",
    icon: Home,
  },
  {
    title: "Orders",
    url: "/orders",
    icon: UtensilsCrossed,
  },
  {
    title: "Menu Management",
    url: "/menu",
    icon: ChefHat,
  },
  {
    title: "Staff Schedule",
    url: "/schedule",
    icon: Calendar,
  },
  {
    title: "Analytics",
    url: "/analytics",
    icon: TrendingUp,
  },
  {
    title: "Staff",
    url: "/staff",
    icon: Users,
  },
  {
    title: "IoT Dashboard",
    url: "/iot",
    icon: Activity,
  },
  {
    title: "Finance",
    url: "/finance",
    icon: Wallet,
  },
  {
    title: "Settings",
    url: "/settings",
    icon: Settings,
  },
]

export function AppSidebar() {
  return (
    <Sidebar className="border-r border-cyan-500/20 bg-black/90 backdrop-blur-xl">
      <SidebarHeader className="border-b border-cyan-500/20 p-6">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-cyan-400 to-purple-600">
            <ChefHat className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-cyan-400">CyberRestaurant</h1>
            <p className="text-xs text-gray-400">Management System</p>
          </div>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel className="text-cyan-400/80">Navigation</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {menuItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild className="hover:bg-cyan-500/10 hover:text-cyan-400">
                    <Link href={item.url}>
                      <item.icon className="h-4 w-4" />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter className="border-t border-cyan-500/20 p-4">
        <div className="text-xs text-gray-500">© 2024 CyberRestaurant v2.0</div>
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  )
}

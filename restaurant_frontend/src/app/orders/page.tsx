import { useState } from "react"
import { SidebarInset, SidebarTrigger } from "@/components/ui/sidebar"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { UtensilsCrossed, Search, Filter, Clock, CheckCircle, AlertCircle, XCircle, Eye } from "lucide-react"

const orders = [
  {
    id: "#2847",
    table: "Table 12",
    customer: "John Smith",
    items: ["Grilled Salmon", "Caesar Salad", "Wine"],
    total: "$45.50",
    status: "preparing",
    time: "2m ago",
    priority: "high",
  },
  {
    id: "#2846",
    table: "Table 8",
    customer: "Sarah Johnson",
    items: ["Beef Tenderloin", "Mashed Potatoes", "Beer"],
    total: "$38.75",
    status: "ready",
    time: "5m ago",
    priority: "urgent",
  },
  {
    id: "#2845",
    table: "Table 3",
    customer: "Mike Wilson",
    items: ["Pasta Carbonara", "Garlic Bread"],
    total: "$22.00",
    status: "served",
    time: "8m ago",
    priority: "normal",
  },
  {
    id: "#2844",
    table: "Table 15",
    customer: "Emma Davis",
    items: ["Chicken Parmesan", "Side Salad", "Soda"],
    total: "$28.25",
    status: "preparing",
    time: "12m ago",
    priority: "normal",
  },
  {
    id: "#2843",
    table: "Table 6",
    customer: "David Brown",
    items: ["Fish & Chips", "Coleslaw", "Beer"],
    total: "$19.50",
    status: "cancelled",
    time: "15m ago",
    priority: "normal",
  },
]

export default function OrdersPage() {
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "preparing":
        return <Clock className="h-4 w-4" />
      case "ready":
        return <AlertCircle className="h-4 w-4" />
      case "served":
        return <CheckCircle className="h-4 w-4" />
      case "cancelled":
        return <XCircle className="h-4 w-4" />
      default:
        return <Clock className="h-4 w-4" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "preparing":
        return "bg-blue-500/20 text-blue-400 border-blue-500/50"
      case "ready":
        return "bg-yellow-500/20 text-yellow-400 border-yellow-500/50"
      case "served":
        return "bg-green-500/20 text-green-400 border-green-500/50"
      case "cancelled":
        return "bg-red-500/20 text-red-400 border-red-500/50"
      default:
        return "bg-gray-500/20 text-gray-400 border-gray-500/50"
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "urgent":
        return "bg-red-500/20 text-red-400 border-red-500/50"
      case "high":
        return "bg-orange-500/20 text-orange-400 border-orange-500/50"
      case "normal":
        return "bg-gray-500/20 text-gray-400 border-gray-500/50"
      default:
        return "bg-gray-500/20 text-gray-400 border-gray-500/50"
    }
  }

  return (
    <SidebarInset className="bg-black min-h-screen">
      <header className="flex h-16 shrink-0 items-center gap-2 border-b border-cyan-500/20 bg-black/50 backdrop-blur-xl px-4">
        <SidebarTrigger className="text-cyan-400 hover:bg-cyan-500/10" />
        <div className="flex items-center gap-2">
          <UtensilsCrossed className="h-5 w-5 text-cyan-400" />
          <span className="text-cyan-400 font-semibold">Order Management</span>
        </div>
        <div className="ml-auto flex items-center gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search orders..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 bg-gray-900/50 border-gray-700 text-gray-300 placeholder-gray-500"
            />
          </div>
          <Button variant="outline" className="border-cyan-500/50 text-cyan-400 hover:bg-cyan-500/10 bg-transparent">
            <Filter className="h-4 w-4 mr-2" />
            Filter
          </Button>
        </div>
      </header>

      <div className="flex-1 p-6 space-y-6">
        {/* Order Stats */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card className="bg-gradient-to-br from-blue-900/20 to-blue-800/10 border-blue-500/30">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-400 text-sm">Preparing</p>
                  <p className="text-2xl font-bold text-blue-300">8</p>
                </div>
                <Clock className="h-8 w-8 text-blue-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-yellow-900/20 to-yellow-800/10 border-yellow-500/30">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-yellow-400 text-sm">Ready</p>
                  <p className="text-2xl font-bold text-yellow-300">3</p>
                </div>
                <AlertCircle className="h-8 w-8 text-yellow-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-green-900/20 to-green-800/10 border-green-500/30">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-green-400 text-sm">Served</p>
                  <p className="text-2xl font-bold text-green-300">45</p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-red-900/20 to-red-800/10 border-red-500/30">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-red-400 text-sm">Cancelled</p>
                  <p className="text-2xl font-bold text-red-300">2</p>
                </div>
                <XCircle className="h-8 w-8 text-red-400" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Orders List */}
        <Card className="bg-black/40 border-cyan-500/30">
          <CardHeader>
            <CardTitle className="text-cyan-400 flex items-center gap-2">
              <UtensilsCrossed className="h-5 w-5" />
              Active Orders
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {orders.map((order) => (
              <div
                key={order.id}
                className="flex items-center justify-between p-4 rounded-lg bg-gray-900/50 border border-gray-700/50 hover:border-cyan-500/30 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className="text-cyan-400 font-mono text-sm">{order.id}</div>
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-gray-300 font-medium">{order.table}</span>
                      <span className="text-gray-500">•</span>
                      <span className="text-gray-400">{order.customer}</span>
                    </div>
                    <div className="text-sm text-gray-500">{order.items.join(", ")}</div>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <div className="text-gray-300 font-semibold">{order.total}</div>
                    <div className="text-xs text-gray-500">{order.time}</div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Badge className={`${getPriorityColor(order.priority)} border`}>{order.priority}</Badge>
                    <Badge className={`${getStatusColor(order.status)} border flex items-center gap-1`}>
                      {getStatusIcon(order.status)}
                      {order.status}
                    </Badge>
                  </div>

                  <Button
                    variant="outline"
                    size="sm"
                    className="border-cyan-500/50 text-cyan-400 hover:bg-cyan-500/10 bg-transparent"
                  >
                    <Eye className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <div className="grid gap-4 md:grid-cols-3">
          <Card className="bg-black/40 border-cyan-500/30">
            <CardHeader>
              <CardTitle className="text-cyan-400 text-sm">Kitchen Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Current Load</span>
                  <span className="text-cyan-400">78%</span>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-2">
                  <div className="bg-cyan-500 h-2 rounded-full" style={{ width: "78%" }}></div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-black/40 border-cyan-500/30">
            <CardHeader>
              <CardTitle className="text-cyan-400 text-sm">Average Wait Time</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-cyan-300">12m</div>
              <p className="text-xs text-gray-400">2m faster than yesterday</p>
            </CardContent>
          </Card>

          <Card className="bg-black/40 border-cyan-500/30">
            <CardHeader>
              <CardTitle className="text-cyan-400 text-sm">Orders Today</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-cyan-300">156</div>
              <p className="text-xs text-gray-400">+23 from yesterday</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </SidebarInset>
  )
}

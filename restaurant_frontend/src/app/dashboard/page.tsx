import { SidebarInset, SidebarTrigger } from "@/components/ui/sidebar"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Activity, DollarSign, TrendingUp, Users, UtensilsCrossed, Clock, AlertTriangle, Zap } from "lucide-react"

export default function Dashboard() {
  return (
    <SidebarInset className="bg-black min-h-screen">
      <header className="flex h-16 shrink-0 items-center gap-2 border-b border-cyan-500/20 bg-black/50 backdrop-blur-xl px-4">
        <SidebarTrigger className="text-cyan-400 hover:bg-cyan-500/10" />
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-green-400 animate-pulse"></div>
          <span className="text-cyan-400 font-mono">SYSTEM ONLINE</span>
        </div>
        <div className="ml-auto flex items-center gap-4">
          <div className="text-xs text-gray-400 font-mono">{new Date().toLocaleString()}</div>
        </div>
      </header>

      <div className="flex-1 space-y-6 p-6">
        {/* Status Grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card className="bg-gradient-to-br from-green-900/20 to-green-800/10 border-green-500/30">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-green-400">Revenue Today</CardTitle>
              <DollarSign className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-300">$2,847.50</div>
              <p className="text-xs text-green-400/70">+12.5% from yesterday</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-blue-900/20 to-blue-800/10 border-blue-500/30">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-blue-400">Active Orders</CardTitle>
              <UtensilsCrossed className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-300">23</div>
              <p className="text-xs text-blue-400/70">8 pending, 15 in progress</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-purple-900/20 to-purple-800/10 border-purple-500/30">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-purple-400">Staff Online</CardTitle>
              <Users className="h-4 w-4 text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-300">12/15</div>
              <p className="text-xs text-purple-400/70">3 on break</p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-cyan-900/20 to-cyan-800/10 border-cyan-500/30">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-cyan-400">Table Occupancy</CardTitle>
              <Activity className="h-4 w-4 text-cyan-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-cyan-300">85%</div>
              <p className="text-xs text-cyan-400/70">34/40 tables occupied</p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Grid */}
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Real-time Orders */}
          <Card className="lg:col-span-2 bg-black/40 border-cyan-500/30">
            <CardHeader>
              <CardTitle className="text-cyan-400 flex items-center gap-2">
                <Zap className="h-5 w-5" />
                Real-time Order Stream
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {[
                { id: "#2847", table: "Table 12", status: "Preparing", time: "2m ago", priority: "high" },
                { id: "#2846", table: "Table 8", status: "Ready", time: "5m ago", priority: "urgent" },
                { id: "#2845", table: "Table 3", status: "Served", time: "8m ago", priority: "normal" },
                { id: "#2844", table: "Table 15", status: "Preparing", time: "12m ago", priority: "normal" },
              ].map((order) => (
                <div
                  key={order.id}
                  className="flex items-center justify-between p-3 rounded-lg bg-gray-900/50 border border-gray-700/50"
                >
                  <div className="flex items-center gap-3">
                    <div className="text-cyan-400 font-mono">{order.id}</div>
                    <div className="text-gray-300">{order.table}</div>
                    <Badge
                      variant={
                        order.priority === "urgent"
                          ? "destructive"
                          : order.priority === "high"
                            ? "default"
                            : "secondary"
                      }
                      className={
                        order.priority === "urgent"
                          ? "bg-red-500/20 text-red-400"
                          : order.priority === "high"
                            ? "bg-yellow-500/20 text-yellow-400"
                            : "bg-gray-500/20 text-gray-400"
                      }
                    >
                      {order.status}
                    </Badge>
                  </div>
                  <div className="text-xs text-gray-500">{order.time}</div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* System Status */}
          <Card className="bg-black/40 border-cyan-500/30">
            <CardHeader>
              <CardTitle className="text-cyan-400 flex items-center gap-2">
                <Activity className="h-5 w-5" />
                System Status
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Kitchen Load</span>
                  <span className="text-green-400">78%</span>
                </div>
                <Progress value={78} className="h-2 bg-gray-800" />
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Server Response</span>
                  <span className="text-green-400">92%</span>
                </div>
                <Progress value={92} className="h-2 bg-gray-800" />
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">POS Systems</span>
                  <span className="text-green-400">100%</span>
                </div>
                <Progress value={100} className="h-2 bg-gray-800" />
              </div>

              <div className="pt-4 space-y-2">
                <div className="flex items-center gap-2 text-sm">
                  <div className="h-2 w-2 rounded-full bg-green-400"></div>
                  <span className="text-gray-400">All systems operational</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <div className="h-2 w-2 rounded-full bg-yellow-400"></div>
                  <span className="text-gray-400">Kitchen printer low ink</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Performance Metrics */}
        <div className="grid gap-6 lg:grid-cols-2">
          <Card className="bg-black/40 border-cyan-500/30">
            <CardHeader>
              <CardTitle className="text-cyan-400 flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Performance Metrics
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-4 rounded-lg bg-gray-900/50">
                  <div className="text-2xl font-bold text-green-400">4.8</div>
                  <div className="text-xs text-gray-400">Avg Rating</div>
                </div>
                <div className="text-center p-4 rounded-lg bg-gray-900/50">
                  <div className="text-2xl font-bold text-blue-400">12m</div>
                  <div className="text-xs text-gray-400">Avg Wait Time</div>
                </div>
                <div className="text-center p-4 rounded-lg bg-gray-900/50">
                  <div className="text-2xl font-bold text-purple-400">156</div>
                  <div className="text-xs text-gray-400">Orders Today</div>
                </div>
                <div className="text-center p-4 rounded-lg bg-gray-900/50">
                  <div className="text-2xl font-bold text-cyan-400">98%</div>
                  <div className="text-xs text-gray-400">Satisfaction</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-black/40 border-cyan-500/30">
            <CardHeader>
              <CardTitle className="text-cyan-400 flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" />
                Alerts & Notifications
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center gap-3 p-3 rounded-lg bg-red-900/20 border border-red-500/30">
                <AlertTriangle className="h-4 w-4 text-red-400" />
                <div className="flex-1">
                  <div className="text-sm text-red-400">Low Stock Alert</div>
                  <div className="text-xs text-red-400/70">Salmon running low (5 portions left)</div>
                </div>
              </div>

              <div className="flex items-center gap-3 p-3 rounded-lg bg-yellow-900/20 border border-yellow-500/30">
                <Clock className="h-4 w-4 text-yellow-400" />
                <div className="flex-1">
                  <div className="text-sm text-yellow-400">Long Wait Time</div>
                  <div className="text-xs text-yellow-400/70">Table 7 waiting 18 minutes</div>
                </div>
              </div>

              <div className="flex items-center gap-3 p-3 rounded-lg bg-blue-900/20 border border-blue-500/30">
                <Users className="h-4 w-4 text-blue-400" />
                <div className="flex-1">
                  <div className="text-sm text-blue-400">Staff Update</div>
                  <div className="text-xs text-blue-400/70">John clocked in for evening shift</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </SidebarInset>
  )
}

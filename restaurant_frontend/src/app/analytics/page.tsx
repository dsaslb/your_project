"use client"

import { SidebarInset, SidebarTrigger } from "@/components/ui/sidebar"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { BarChart3, TrendingUp, DollarSign, Users, Clock, Star, Calendar, ArrowUp, ArrowDown } from "lucide-react"

export default function AnalyticsPage() {
  return (
    <SidebarInset className="bg-gradient-to-br from-amber-50 via-white to-orange-50 min-h-screen">
      <header className="flex h-16 shrink-0 items-center gap-2 border-b border-amber-200 bg-white/80 backdrop-blur-xl px-4">
        <SidebarTrigger className="text-amber-700 hover:bg-amber-100" />
        <div className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-amber-600" />
          <span className="text-amber-900 font-semibold">Analytics Dashboard</span>
        </div>
        <div className="ml-auto flex items-center gap-4">
          <Badge variant="outline" className="border-amber-300 text-amber-700">
            <Calendar className="h-3 w-3 mr-1" />
            Last 30 days
          </Badge>
        </div>
      </header>

      <div className="flex-1 p-6 space-y-6">
        {/* Key Metrics */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card className="bg-white border-amber-200 shadow-lg">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-amber-800">Total Revenue</CardTitle>
              <DollarSign className="h-4 w-4 text-amber-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-amber-900">$45,231.89</div>
              <div className="flex items-center text-xs text-green-600">
                <ArrowUp className="h-3 w-3 mr-1" />
                +20.1% from last month
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white border-amber-200 shadow-lg">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-amber-800">Total Orders</CardTitle>
              <BarChart3 className="h-4 w-4 text-amber-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-amber-900">2,350</div>
              <div className="flex items-center text-xs text-green-600">
                <ArrowUp className="h-3 w-3 mr-1" />
                +180.1% from last month
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white border-amber-200 shadow-lg">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-amber-800">Avg. Order Value</CardTitle>
              <TrendingUp className="h-4 w-4 text-amber-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-amber-900">$19.25</div>
              <div className="flex items-center text-xs text-red-600">
                <ArrowDown className="h-3 w-3 mr-1" />
                -4.3% from last month
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white border-amber-200 shadow-lg">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-amber-800">Customer Satisfaction</CardTitle>
              <Star className="h-4 w-4 text-amber-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-amber-900">4.8/5</div>
              <div className="flex items-center text-xs text-green-600">
                <ArrowUp className="h-3 w-3 mr-1" />
                +0.2 from last month
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Performance Overview */}
        <div className="grid gap-6 lg:grid-cols-2">
          <Card className="bg-white border-amber-200 shadow-lg">
            <CardHeader>
              <CardTitle className="text-amber-900 flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-amber-600" />
                Revenue Trends
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-amber-700">This Week</span>
                  <span className="font-semibold text-amber-900">$12,847</span>
                </div>
                <Progress value={85} className="h-2 bg-amber-100" />

                <div className="flex justify-between items-center">
                  <span className="text-sm text-amber-700">Last Week</span>
                  <span className="font-semibold text-amber-900">$10,234</span>
                </div>
                <Progress value={68} className="h-2 bg-amber-100" />

                <div className="flex justify-between items-center">
                  <span className="text-sm text-amber-700">2 Weeks Ago</span>
                  <span className="font-semibold text-amber-900">$9,876</span>
                </div>
                <Progress value={65} className="h-2 bg-amber-100" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white border-amber-200 shadow-lg">
            <CardHeader>
              <CardTitle className="text-amber-900 flex items-center gap-2">
                <Clock className="h-5 w-5 text-amber-600" />
                Peak Hours Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-amber-700">12:00 - 14:00 (Lunch)</span>
                  <Badge className="bg-amber-100 text-amber-800">Peak</Badge>
                </div>
                <Progress value={95} className="h-2 bg-amber-100" />

                <div className="flex justify-between items-center">
                  <span className="text-sm text-amber-700">19:00 - 21:00 (Dinner)</span>
                  <Badge className="bg-amber-100 text-amber-800">High</Badge>
                </div>
                <Progress value={88} className="h-2 bg-amber-100" />

                <div className="flex justify-between items-center">
                  <span className="text-sm text-amber-700">15:00 - 17:00 (Afternoon)</span>
                  <Badge variant="outline" className="border-amber-300 text-amber-700">
                    Medium
                  </Badge>
                </div>
                <Progress value={45} className="h-2 bg-amber-100" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Detailed Analytics */}
        <div className="grid gap-6 lg:grid-cols-3">
          <Card className="bg-white border-amber-200 shadow-lg">
            <CardHeader>
              <CardTitle className="text-amber-900 flex items-center gap-2">
                <Users className="h-5 w-5 text-amber-600" />
                Customer Insights
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between items-center p-3 rounded-lg bg-amber-50">
                <div>
                  <div className="text-sm font-medium text-amber-900">New Customers</div>
                  <div className="text-xs text-amber-600">This month</div>
                </div>
                <div className="text-lg font-bold text-amber-900">342</div>
              </div>

              <div className="flex justify-between items-center p-3 rounded-lg bg-amber-50">
                <div>
                  <div className="text-sm font-medium text-amber-900">Returning Customers</div>
                  <div className="text-xs text-amber-600">This month</div>
                </div>
                <div className="text-lg font-bold text-amber-900">1,847</div>
              </div>

              <div className="flex justify-between items-center p-3 rounded-lg bg-amber-50">
                <div>
                  <div className="text-sm font-medium text-amber-900">Customer Retention</div>
                  <div className="text-xs text-amber-600">Rate</div>
                </div>
                <div className="text-lg font-bold text-amber-900">78%</div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white border-amber-200 shadow-lg">
            <CardHeader>
              <CardTitle className="text-amber-900">Top Menu Items</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {[
                { name: "Grilled Salmon", orders: 156, revenue: "$2,340" },
                { name: "Beef Tenderloin", orders: 134, revenue: "$2,010" },
                { name: "Caesar Salad", orders: 98, revenue: "$980" },
                { name: "Pasta Carbonara", orders: 87, revenue: "$1,305" },
                { name: "Chocolate Cake", orders: 76, revenue: "$456" },
              ].map((item, index) => (
                <div key={item.name} className="flex items-center justify-between p-2 rounded-lg bg-amber-50">
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 rounded-full bg-amber-200 flex items-center justify-center text-xs font-bold text-amber-800">
                      {index + 1}
                    </div>
                    <div>
                      <div className="text-sm font-medium text-amber-900">{item.name}</div>
                      <div className="text-xs text-amber-600">{item.orders} orders</div>
                    </div>
                  </div>
                  <div className="text-sm font-semibold text-amber-900">{item.revenue}</div>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card className="bg-white border-amber-200 shadow-lg">
            <CardHeader>
              <CardTitle className="text-amber-900">Operational Metrics</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-amber-700">Table Turnover Rate</span>
                  <span className="text-amber-900 font-semibold">2.3x/day</span>
                </div>
                <Progress value={76} className="h-2 bg-amber-100" />
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-amber-700">Kitchen Efficiency</span>
                  <span className="text-amber-900 font-semibold">92%</span>
                </div>
                <Progress value={92} className="h-2 bg-amber-100" />
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-amber-700">Staff Productivity</span>
                  <span className="text-amber-900 font-semibold">87%</span>
                </div>
                <Progress value={87} className="h-2 bg-amber-100" />
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-amber-700">Order Accuracy</span>
                  <span className="text-amber-900 font-semibold">96%</span>
                </div>
                <Progress value={96} className="h-2 bg-amber-100" />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </SidebarInset>
  )
}

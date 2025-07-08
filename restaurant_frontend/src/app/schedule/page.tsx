import { useState } from "react"
import { SidebarInset, SidebarTrigger } from "@/components/ui/sidebar"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Calendar, ChevronLeft, ChevronRight, Plus, Clock, Users } from "lucide-react"

const daysOfWeek = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
const timeSlots = [
  "09:00",
  "10:00",
  "11:00",
  "12:00",
  "13:00",
  "14:00",
  "15:00",
  "16:00",
  "17:00",
  "18:00",
  "19:00",
  "20:00",
  "21:00",
  "22:00",
]

const staffSchedule = {
  "John Doe": {
    role: "Chef",
    shifts: [
      { day: 0, start: "09:00", end: "17:00", type: "morning" },
      { day: 2, start: "09:00", end: "17:00", type: "morning" },
      { day: 4, start: "09:00", end: "17:00", type: "morning" },
    ],
  },
  "Sarah Wilson": {
    role: "Server",
    shifts: [
      { day: 1, start: "17:00", end: "22:00", type: "evening" },
      { day: 3, start: "17:00", end: "22:00", type: "evening" },
      { day: 5, start: "17:00", end: "22:00", type: "evening" },
    ],
  },
  "Mike Johnson": {
    role: "Manager",
    shifts: [
      { day: 0, start: "12:00", end: "20:00", type: "full" },
      { day: 1, start: "12:00", end: "20:00", type: "full" },
      { day: 2, start: "12:00", end: "20:00", type: "full" },
      { day: 3, start: "12:00", end: "20:00", type: "full" },
      { day: 4, start: "12:00", end: "20:00", type: "full" },
    ],
  },
  "Emma Davis": {
    role: "Server",
    shifts: [
      { day: 0, start: "11:00", end: "19:00", type: "day" },
      { day: 2, start: "11:00", end: "19:00", type: "day" },
      { day: 4, start: "11:00", end: "19:00", type: "day" },
      { day: 6, start: "11:00", end: "19:00", type: "day" },
    ],
  },
}

export default function SchedulePage() {
  const [currentWeek, setCurrentWeek] = useState(0)

  const getShiftColor = (type: string) => {
    switch (type) {
      case "morning":
        return "bg-blue-500/20 border-blue-500/50 text-blue-300"
      case "evening":
        return "bg-purple-500/20 border-purple-500/50 text-purple-300"
      case "full":
        return "bg-green-500/20 border-green-500/50 text-green-300"
      case "day":
        return "bg-orange-500/20 border-orange-500/50 text-orange-300"
      default:
        return "bg-gray-500/20 border-gray-500/50 text-gray-300"
    }
  }

  return (
    <SidebarInset className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 min-h-screen">
      <header className="flex h-16 shrink-0 items-center gap-2 border-b border-slate-700/50 bg-slate-900/80 backdrop-blur-xl px-4">
        <SidebarTrigger className="text-slate-300 hover:bg-slate-700/50" />
        <div className="flex items-center gap-2">
          <Calendar className="h-5 w-5 text-blue-400" />
          <span className="text-slate-200 font-semibold">Staff Schedule</span>
        </div>
        <div className="ml-auto">
          <Button className="bg-blue-600 hover:bg-blue-700 text-white">
            <Plus className="h-4 w-4 mr-2" />
            Add Shift
          </Button>
        </div>
      </header>

      <div className="flex-1 p-6 space-y-6">
        {/* Week Navigation */}
        <Card className="bg-slate-800/50 border-slate-700/50 backdrop-blur-sm">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-slate-200 flex items-center gap-2">
                <Calendar className="h-5 w-5 text-blue-400" />
                Week of December 9-15, 2024
              </CardTitle>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  className="border-slate-600 text-slate-300 hover:bg-slate-700 bg-transparent"
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="border-slate-600 text-slate-300 hover:bg-slate-700 bg-transparent"
                >
                  Today
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="border-slate-600 text-slate-300 hover:bg-slate-700 bg-transparent"
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardHeader>
        </Card>

        {/* Schedule Grid */}
        <Card className="bg-slate-800/50 border-slate-700/50 backdrop-blur-sm">
          <CardContent className="p-0">
            <div className="grid grid-cols-8 gap-0">
              {/* Header */}
              <div className="p-4 border-b border-r border-slate-700/50 bg-slate-900/50">
                <div className="text-sm font-medium text-slate-400">Staff</div>
              </div>
              {daysOfWeek.map((day, index) => (
                <div key={day} className="p-4 border-b border-r border-slate-700/50 bg-slate-900/50 text-center">
                  <div className="text-sm font-medium text-slate-300">{day}</div>
                  <div className="text-xs text-slate-500">Dec {9 + index}</div>
                </div>
              ))}

              {/* Staff Rows */}
              {Object.entries(staffSchedule).map(([name, data]) => (
                <div key={name} className="contents">
                  <div className="p-4 border-b border-r border-slate-700/50 bg-slate-900/30">
                    <div className="text-sm font-medium text-slate-200">{name}</div>
                    <Badge variant="secondary" className="text-xs mt-1 bg-slate-700/50 text-slate-400">
                      {data.role}
                    </Badge>
                  </div>
                  {daysOfWeek.map((_, dayIndex) => {
                    const shift = data.shifts.find((s) => s.day === dayIndex)
                    return (
                      <div key={dayIndex} className="p-2 border-b border-r border-slate-700/50 min-h-[80px]">
                        {shift && (
                          <div className={`p-2 rounded-lg border text-xs ${getShiftColor(shift.type)}`}>
                            <div className="font-medium">
                              {shift.start} - {shift.end}
                            </div>
                            <div className="capitalize opacity-80">{shift.type}</div>
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Schedule Summary */}
        <div className="grid gap-6 lg:grid-cols-3">
          <Card className="bg-slate-800/50 border-slate-700/50 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-slate-200 flex items-center gap-2">
                <Users className="h-5 w-5 text-green-400" />
                Staff Coverage
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {daysOfWeek.map((day, index) => {
                const dayShifts = Object.values(staffSchedule).flatMap((staff) =>
                  staff.shifts.filter((shift) => shift.day === index),
                )
                return (
                  <div key={day} className="flex justify-between items-center">
                    <span className="text-slate-300">{day}</span>
                    <Badge variant="outline" className="border-green-500/50 text-green-400">
                      {dayShifts.length} staff
                    </Badge>
                  </div>
                )
              })}
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-slate-700/50 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-slate-200 flex items-center gap-2">
                <Clock className="h-5 w-5 text-blue-400" />
                Shift Types
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-blue-500"></div>
                  <span className="text-slate-300">Morning</span>
                </div>
                <span className="text-slate-400">09:00 - 17:00</span>
              </div>
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-orange-500"></div>
                  <span className="text-slate-300">Day</span>
                </div>
                <span className="text-slate-400">11:00 - 19:00</span>
              </div>
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-purple-500"></div>
                  <span className="text-slate-300">Evening</span>
                </div>
                <span className="text-slate-400">17:00 - 22:00</span>
              </div>
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-green-500"></div>
                  <span className="text-slate-300">Full</span>
                </div>
                <span className="text-slate-400">12:00 - 20:00</span>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-slate-700/50 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-slate-200">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button className="w-full bg-blue-600 hover:bg-blue-700 text-white">
                <Plus className="h-4 w-4 mr-2" />
                Add New Shift
              </Button>
              <Button
                variant="outline"
                className="w-full border-slate-600 text-slate-300 hover:bg-slate-700 bg-transparent"
              >
                <Users className="h-4 w-4 mr-2" />
                Manage Staff
              </Button>
              <Button
                variant="outline"
                className="w-full border-slate-600 text-slate-300 hover:bg-slate-700 bg-transparent"
              >
                <Calendar className="h-4 w-4 mr-2" />
                Export Schedule
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </SidebarInset>
  )
}

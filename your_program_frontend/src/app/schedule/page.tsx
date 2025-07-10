import { useState, useEffect } from "react"
import { SidebarInset, SidebarTrigger } from "@/components/ui/sidebar"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Calendar, ChevronLeft, ChevronRight, Plus, Clock, Users } from "lucide-react"

// 직원 인터페이스 정의
interface StaffMember {
  id: number;
  name: string;
  position: string;
  department: string;
  role: string;
  status: string;
}

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

export default function SchedulePage() {
  const [currentWeek, setCurrentWeek] = useState(0)
  const [staffMembers, setStaffMembers] = useState<StaffMember[]>([])
  const [isLoading, setIsLoading] = useState(true)

  // 직원 목록 불러오기
  const fetchStaffMembers = async () => {
    try {
      setIsLoading(true);
      console.log('스케줄 관리: 직원 데이터 로딩 시작');
      
      const response = await fetch('http://localhost:5000/api/staff?page_type=schedule', {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      console.log('스케줄 관리: API 응답 상태:', response.status);
      
      if (response.ok) {
        const contentType = response.headers.get('content-type');
        
        if (contentType && contentType.includes('application/json')) {
          const data = await response.json();
          console.log('스케줄 관리: API 응답 데이터:', data);
          
          if (data.success) {
            console.log('스케줄 관리: 직원 수:', (data.staff || []).length);
            setStaffMembers(data.staff || []);
          } else {
            console.error('스케줄 관리: 직원 데이터 로드 실패:', data.error);
            setStaffMembers([]);
          }
        } else {
          const textResponse = await response.text();
          console.log('스케줄 관리: HTML 응답 (처음 200자):', textResponse.substring(0, 200));
          setStaffMembers([]);
        }
      } else {
        console.error('스케줄 관리: 직원 데이터 로드 실패:', response.status);
        setStaffMembers([]);
      }
    } catch (error) {
      console.error('스케줄 관리: 직원 데이터 로드 오류:', error);
      setStaffMembers([]);
    } finally {
      setIsLoading(false);
    }
  };

  // 컴포넌트 마운트 시 직원 데이터 로드
  useEffect(() => {
    fetchStaffMembers();
  }, []);

  // 더미 스케줄 데이터 (실제로는 API에서 가져와야 함)
  const getDummySchedule = (staffMember: StaffMember) => {
    const schedules = {
      "morning": [
        { day: 0, start: "09:00", end: "17:00", type: "morning" },
        { day: 2, start: "09:00", end: "17:00", type: "morning" },
        { day: 4, start: "09:00", end: "17:00", type: "morning" },
      ],
      "evening": [
        { day: 1, start: "17:00", end: "22:00", type: "evening" },
        { day: 3, start: "17:00", end: "22:00", type: "evening" },
        { day: 5, start: "17:00", end: "22:00", type: "evening" },
      ],
      "full": [
        { day: 0, start: "12:00", end: "20:00", type: "full" },
        { day: 1, start: "12:00", end: "20:00", type: "full" },
        { day: 2, start: "12:00", end: "20:00", type: "full" },
        { day: 3, start: "12:00", end: "20:00", type: "full" },
        { day: 4, start: "12:00", end: "20:00", type: "full" },
      ],
      "day": [
        { day: 0, start: "11:00", end: "19:00", type: "day" },
        { day: 2, start: "11:00", end: "19:00", type: "day" },
        { day: 4, start: "11:00", end: "19:00", type: "day" },
        { day: 6, start: "11:00", end: "19:00", type: "day" },
      ]
    };
    
    // 직원 ID를 기반으로 스케줄 타입 결정
    const scheduleTypes = Object.keys(schedules);
    const typeIndex = staffMember.id % scheduleTypes.length;
    return schedules[scheduleTypes[typeIndex] as keyof typeof schedules];
  };

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

  if (isLoading) {
    return (
      <SidebarInset className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 min-h-screen">
        <header className="flex h-16 shrink-0 items-center gap-2 border-b border-slate-700/50 bg-slate-900/80 backdrop-blur-xl px-4">
          <SidebarTrigger className="text-slate-300 hover:bg-slate-700/50" />
          <div className="flex items-center gap-2">
            <Calendar className="h-5 w-5 text-blue-400" />
            <span className="text-slate-200 font-semibold">Staff Schedule</span>
          </div>
        </header>
        <div className="flex-1 p-6 flex items-center justify-center">
          <div className="text-slate-300">직원 데이터를 불러오는 중...</div>
        </div>
      </SidebarInset>
    );
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
              {staffMembers.map((staffMember) => {
                const shifts = getDummySchedule(staffMember);
                return (
                  <div key={staffMember.id} className="contents">
                    <div className="p-4 border-b border-r border-slate-700/50 bg-slate-900/30">
                      <div className="text-sm font-medium text-slate-200">{staffMember.name}</div>
                      <Badge variant="secondary" className="text-xs mt-1 bg-slate-700/50 text-slate-400">
                        {staffMember.position}
                      </Badge>
                    </div>
                    {daysOfWeek.map((_, dayIndex) => {
                      const shift = shifts.find((s) => s.day === dayIndex)
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
                );
              })}
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
                const dayShifts = staffMembers.flatMap((staff) =>
                  getDummySchedule(staff).filter((shift) => shift.day === index),
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
                Total Hours
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-slate-200">168</div>
              <p className="text-slate-400 text-sm">This week</p>
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-slate-700/50 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-slate-200 flex items-center gap-2">
                <Users className="h-5 w-5 text-purple-400" />
                Active Staff
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-slate-200">{staffMembers.length}</div>
              <p className="text-slate-400 text-sm">Scheduled this week</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </SidebarInset>
  )
}

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export interface Schedule {
  id: number;
  staff_id: number;
  staff_name: string;
  date: string;
  start_time: string;
  end_time: string;
  shift_type: string;
  position: string;
  department: string;
  status: string;
  notes: string;
  created_at: string;
  updated_at: string;
  branch_id: number;
}

export interface ShiftRequest {
  id: number;
  staff_id: number;
  staff_name: string;
  request_type: 'swap' | 'time_off' | 'overtime';
  original_date: string;
  requested_date: string;
  original_start_time: string;
  original_end_time: string;
  requested_start_time: string;
  requested_end_time: string;
  reason: string;
  status: 'pending' | 'approved' | 'rejected';
  created_at: string;
  updated_at: string;
}

interface ScheduleStore {
  // 상태
  schedules: Schedule[];
  shiftRequests: ShiftRequest[];
  loading: boolean;
  error: string | null;

  // 액션
  setSchedules: (schedules: Schedule[]) => void;
  setShiftRequests: (requests: ShiftRequest[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  
  // 스케줄 관리
  addSchedule: (schedule: Schedule) => void;
  updateSchedule: (id: number, updates: Partial<Schedule>) => void;
  deleteSchedule: (id: number) => void;
  updateScheduleStatus: (id: number, status: string) => void;
  
  // API 호출
  fetchSchedules: () => Promise<void>;
  fetchShiftRequests: () => Promise<void>;
  createSchedule: (scheduleData: Partial<Schedule>) => Promise<boolean>;
  updateScheduleAPI: (id: number, scheduleData: Partial<Schedule>) => Promise<boolean>;
  deleteScheduleAPI: (id: number) => Promise<boolean>;
  createShiftRequest: (requestData: Partial<ShiftRequest>) => Promise<boolean>;
  approveShiftRequest: (requestId: number) => Promise<boolean>;
  rejectShiftRequest: (requestId: number, reason?: string) => Promise<boolean>;
  
  // 유틸리티
  getSchedulesByDate: (date: string) => Schedule[];
  getSchedulesByStaff: (staffId: number) => Schedule[];
  getSchedulesByDateRange: (startDate: string, endDate: string) => Schedule[];
  getScheduleById: (id: number) => Schedule | undefined;
  getShiftRequestsByStaff: (staffId: number) => ShiftRequest[];
  getPendingShiftRequests: () => ShiftRequest[];
  getSchedulesByDepartment: (department: string) => Schedule[];
}

// 더미 데이터 (API 실패 시 사용)
const getDummyScheduleData = (): Schedule[] => [
  {
    id: 1,
    staff_id: 1,
    staff_name: "김철수",
    date: "2024-01-20",
    start_time: "09:00",
    end_time: "17:00",
    shift_type: "주간",
    position: "주방장",
    department: "주방",
    status: "confirmed",
    notes: "정상 근무",
    created_at: "2024-01-15T10:00:00Z",
    updated_at: "2024-01-15T10:00:00Z",
    branch_id: 1
  },
  {
    id: 2,
    staff_id: 2,
    staff_name: "이영희",
    date: "2024-01-20",
    start_time: "10:00",
    end_time: "18:00",
    shift_type: "주간",
    position: "서버",
    department: "홀",
    status: "confirmed",
    notes: "정상 근무",
    created_at: "2024-01-15T10:00:00Z",
    updated_at: "2024-01-15T10:00:00Z",
    branch_id: 1
  },
  {
    id: 3,
    staff_id: 3,
    staff_name: "박민수",
    date: "2024-01-20",
    start_time: "17:00",
    end_time: "23:00",
    shift_type: "야간",
    position: "주방직원",
    department: "주방",
    status: "pending",
    notes: "신입 직원",
    created_at: "2024-01-15T10:00:00Z",
    updated_at: "2024-01-15T10:00:00Z",
    branch_id: 1
  },
  {
    id: 4,
    staff_id: 1,
    staff_name: "김철수",
    date: "2024-01-21",
    start_time: "09:00",
    end_time: "17:00",
    shift_type: "주간",
    position: "주방장",
    department: "주방",
    status: "confirmed",
    notes: "정상 근무",
    created_at: "2024-01-15T10:00:00Z",
    updated_at: "2024-01-15T10:00:00Z",
    branch_id: 1
  }
];

const getDummyShiftRequests = (): ShiftRequest[] => [
  {
    id: 1,
    staff_id: 2,
    staff_name: "이영희",
    request_type: "swap",
    original_date: "2024-01-22",
    requested_date: "2024-01-23",
    original_start_time: "10:00",
    original_end_time: "18:00",
    requested_start_time: "10:00",
    requested_end_time: "18:00",
    reason: "개인 일정으로 인한 교대 요청",
    status: "pending",
    created_at: "2024-01-16T14:30:00Z",
    updated_at: "2024-01-16T14:30:00Z"
  },
  {
    id: 2,
    staff_id: 3,
    staff_name: "박민수",
    request_type: "time_off",
    original_date: "2024-01-25",
    requested_date: "2024-01-25",
    original_start_time: "17:00",
    original_end_time: "23:00",
    requested_start_time: "",
    requested_end_time: "",
    reason: "병원 진료",
    status: "approved",
    created_at: "2024-01-17T09:15:00Z",
    updated_at: "2024-01-17T16:00:00Z"
  }
];

export const useScheduleStore = create<ScheduleStore>()(
  devtools(
    (set, get) => ({
      // 초기 상태
      schedules: [],
      shiftRequests: [],
      loading: false,
      error: null,

      // 상태 설정
      setSchedules: (schedules) => set({ schedules }),
      setShiftRequests: (requests) => set({ shiftRequests: requests }),
      setLoading: (loading) => set({ loading }),
      setError: (error) => set({ error }),

      // 스케줄 관리
      addSchedule: (schedule) => set((state) => ({
        schedules: [...state.schedules, schedule]
      })),

      updateSchedule: (id, updates) => set((state) => ({
        schedules: state.schedules.map(schedule =>
          schedule.id === id ? { ...schedule, ...updates, updated_at: new Date().toISOString() } : schedule
        )
      })),

      deleteSchedule: (id) => set((state) => ({
        schedules: state.schedules.filter(schedule => schedule.id !== id)
      })),

      updateScheduleStatus: (id, status) => set((state) => ({
        schedules: state.schedules.map(schedule =>
          schedule.id === id ? { ...schedule, status, updated_at: new Date().toISOString() } : schedule
        )
      })),

      // API 호출
      fetchSchedules: async () => {
        set({ loading: true, error: null });
        try {
          const response = await fetch('/api/schedule', {
            credentials: 'include'
          });
          const data = await response.json();
          
          if (data.success) {
            set({ schedules: data.data, loading: false });
            console.log('스케줄 데이터 로드 성공:', data.data.length, '건');
          } else {
            console.error('스케줄 목록 로드 실패:', data.error);
            set({ schedules: getDummyScheduleData(), loading: false });
          }
        } catch (error) {
          console.error('스케줄 목록 로드 오류:', error);
          set({ schedules: getDummyScheduleData(), loading: false });
        }
      },

      fetchShiftRequests: async () => {
        try {
          const response = await fetch('/api/schedule/shift-requests', {
            credentials: 'include'
          });
          const data = await response.json();
          
          if (data.success) {
            set({ shiftRequests: data.data });
            console.log('교대 요청 데이터 로드 성공:', data.data.length, '건');
          } else {
            console.error('교대 요청 목록 로드 실패:', data.error);
            set({ shiftRequests: getDummyShiftRequests() });
          }
        } catch (error) {
          console.error('교대 요청 목록 로드 오류:', error);
          set({ shiftRequests: getDummyShiftRequests() });
        }
      },

      createSchedule: async (scheduleData) => {
        try {
          const response = await fetch('/api/schedule', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify(scheduleData)
          });

          const result = await response.json();

          if (result.success) {
            get().addSchedule(result.data);
            console.log('스케줄 생성 성공');
            return true;
          } else {
            console.error('스케줄 생성 실패:', result.error);
            set({ error: result.error });
            return false;
          }
        } catch (error) {
          console.error('스케줄 생성 오류:', error);
          set({ error: '스케줄 생성 중 오류가 발생했습니다.' });
          return false;
        }
      },

      updateScheduleAPI: async (id, scheduleData) => {
        try {
          const response = await fetch(`/api/schedule/${id}`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify(scheduleData)
          });

          const result = await response.json();

          if (result.success) {
            get().updateSchedule(id, result.data);
            console.log('스케줄 수정 성공');
            return true;
          } else {
            console.error('스케줄 수정 실패:', result.error);
            set({ error: result.error });
            return false;
          }
        } catch (error) {
          console.error('스케줄 수정 오류:', error);
          set({ error: '스케줄 수정 중 오류가 발생했습니다.' });
          return false;
        }
      },

      deleteScheduleAPI: async (id) => {
        try {
          const response = await fetch(`/api/schedule/${id}`, {
            method: 'DELETE',
            headers: {
              'Content-Type': 'application/json',
            },
            credentials: 'include'
          });

          const result = await response.json();

          if (result.success) {
            get().deleteSchedule(id);
            console.log('스케줄 삭제 성공');
            return true;
          } else {
            console.error('스케줄 삭제 실패:', result.error);
            set({ error: result.error });
            return false;
          }
        } catch (error) {
          console.error('스케줄 삭제 오류:', error);
          set({ error: '스케줄 삭제 중 오류가 발생했습니다.' });
          return false;
        }
      },

      createShiftRequest: async (requestData) => {
        try {
          const response = await fetch('/api/schedule/shift-requests', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify(requestData)
          });

          const result = await response.json();

          if (result.success) {
            set((state) => ({
              shiftRequests: [...state.shiftRequests, result.data]
            }));
            console.log('교대 요청 생성 성공');
            return true;
          } else {
            console.error('교대 요청 생성 실패:', result.error);
            set({ error: result.error });
            return false;
          }
        } catch (error) {
          console.error('교대 요청 생성 오류:', error);
          set({ error: '교대 요청 생성 중 오류가 발생했습니다.' });
          return false;
        }
      },

      approveShiftRequest: async (requestId) => {
        try {
          const response = await fetch(`/api/schedule/shift-requests/${requestId}/approve`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            credentials: 'include'
          });

          const result = await response.json();

          if (result.success) {
            set((state) => ({
              shiftRequests: state.shiftRequests.map(request =>
                request.id === requestId ? { ...request, status: 'approved', updated_at: new Date().toISOString() } : request
              )
            }));
            console.log('교대 요청 승인 성공');
            return true;
          } else {
            console.error('교대 요청 승인 실패:', result.error);
            set({ error: result.error });
            return false;
          }
        } catch (error) {
          console.error('교대 요청 승인 오류:', error);
          set({ error: '교대 요청 승인 중 오류가 발생했습니다.' });
          return false;
        }
      },

      rejectShiftRequest: async (requestId, reason = '관리자 거절') => {
        try {
          const response = await fetch(`/api/schedule/shift-requests/${requestId}/reject`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ reason })
          });

          const result = await response.json();

          if (result.success) {
            set((state) => ({
              shiftRequests: state.shiftRequests.map(request =>
                request.id === requestId ? { ...request, status: 'rejected', updated_at: new Date().toISOString() } : request
              )
            }));
            console.log('교대 요청 거절 성공');
            return true;
          } else {
            console.error('교대 요청 거절 실패:', result.error);
            set({ error: result.error });
            return false;
          }
        } catch (error) {
          console.error('교대 요청 거절 오류:', error);
          set({ error: '교대 요청 거절 중 오류가 발생했습니다.' });
          return false;
        }
      },

      // 유틸리티
      getSchedulesByDate: (date) => {
        const { schedules } = get();
        return schedules.filter(schedule => schedule.date === date);
      },

      getSchedulesByStaff: (staffId) => {
        const { schedules } = get();
        return schedules.filter(schedule => schedule.staff_id === staffId);
      },

      getSchedulesByDateRange: (startDate, endDate) => {
        const { schedules } = get();
        return schedules.filter(schedule => {
          const scheduleDate = new Date(schedule.date);
          const start = new Date(startDate);
          const end = new Date(endDate);
          return scheduleDate >= start && scheduleDate <= end;
        });
      },

      getScheduleById: (id) => {
        const { schedules } = get();
        return schedules.find(schedule => schedule.id === id);
      },

      getShiftRequestsByStaff: (staffId) => {
        const { shiftRequests } = get();
        return shiftRequests.filter(request => request.staff_id === staffId);
      },

      getPendingShiftRequests: () => {
        const { shiftRequests } = get();
        return shiftRequests.filter(request => request.status === 'pending');
      },

      getSchedulesByDepartment: (department) => {
        const { schedules } = get();
        return schedules.filter(schedule => schedule.department === department);
      },
    }),
    {
      name: 'schedule-store',
    }
  )
); 
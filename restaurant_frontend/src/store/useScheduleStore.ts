import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { offlineStorage } from '../utils/offlineStorage';

export type Schedule = {
  id: number;
  staffId: number;
  staffName: string;
  date: string;
  startTime: string;
  endTime: string;
  position: string;
  status: 'scheduled' | 'confirmed' | 'completed' | 'cancelled';
  notes?: string;
  branchId: number;
  createdAt: string;
  updatedAt: string;
};

export type SyncStatus = 'synced' | 'pending' | 'offline' | 'error';

interface ScheduleStore {
  schedules: Schedule[];
  syncStatus: SyncStatus;
  lastSync: string | null;
  fetchSchedules: () => Promise<void>;
  addSchedule: (schedule: Omit<Schedule, 'id' | 'createdAt' | 'updatedAt'>) => void;
  updateSchedule: (id: number, updates: Partial<Schedule>) => void;
  removeSchedule: (id: number) => void;
  getSchedulesByDate: (date: string) => Schedule[];
  getSchedulesByStaff: (staffId: number) => Schedule[];
  getTodaySchedules: () => Schedule[];
  getUpcomingSchedules: (days: number) => Schedule[];
  clearAll: () => void;
  manualSync: () => Promise<void>;
  setOffline: () => void;
}

export const useScheduleStore = create<ScheduleStore>()(
  persist(
    (set, get) => ({
      schedules: [],
      syncStatus: 'synced',
      lastSync: null,
      
      fetchSchedules: async () => {
        try {
          set({ syncStatus: 'pending' });
          const res = await fetch('/api/schedules');
          if (!res.ok) throw new Error('API 오류');
          const data: Schedule[] = await res.json();
          set({ schedules: data, syncStatus: 'synced', lastSync: new Date().toISOString() });
          
          // 캐시에 저장
          await offlineStorage.saveCachedData('schedules', 'schedules', data);
        } catch (e: unknown) {
          set({ syncStatus: 'offline' });
          // 오프라인 시 캐시된 데이터 사용
          const cachedData = await offlineStorage.getCachedData('schedules');
          if (cachedData) {
            set({ schedules: cachedData });
          }
        }
      },
      
      addSchedule: async (schedule) => {
        const newSchedule: Schedule = {
          ...schedule,
          id: Date.now(),
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        };
        
        set((state: ScheduleStore) => ({
          schedules: [...state.schedules, newSchedule],
          syncStatus: 'pending',
        }));
        
        // 오프라인 데이터로 저장
        await offlineStorage.saveOfflineData('schedules', 'create', newSchedule);
      },
      
      updateSchedule: async (id: number, updates: Partial<Schedule>) => {
        set((state: ScheduleStore) => ({
          schedules: state.schedules.map((schedule) =>
            schedule.id === id ? { ...schedule, ...updates, updatedAt: new Date().toISOString() } : schedule
          ),
          syncStatus: 'pending',
        }));
        
        // 오프라인 데이터로 저장
        await offlineStorage.saveOfflineData('schedules', 'update', { id, ...updates });
      },
      
      removeSchedule: async (id: number) => {
        set((state: ScheduleStore) => ({
          schedules: state.schedules.filter((schedule) => schedule.id !== id),
          syncStatus: 'pending',
        }));
        
        // 오프라인 데이터로 저장
        await offlineStorage.saveOfflineData('schedules', 'delete', { id });
      },
      
      getSchedulesByDate: (date: string) => {
        return get().schedules.filter(schedule => schedule.date === date);
      },
      
      getSchedulesByStaff: (staffId: number) => {
        return get().schedules.filter(schedule => schedule.staffId === staffId);
      },
      
      getTodaySchedules: () => {
        const today = new Date().toISOString().split('T')[0];
        return get().schedules.filter(schedule => schedule.date === today);
      },
      
      getUpcomingSchedules: (days: number = 7) => {
        const today = new Date();
        const endDate = new Date();
        endDate.setDate(today.getDate() + days);
        
        return get().schedules.filter(schedule => {
          const scheduleDate = new Date(schedule.date);
          return scheduleDate >= today && scheduleDate <= endDate;
        }).sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
      },
      
      manualSync: async () => {
        await get().fetchSchedules();
      },
      
      clearAll: () => set({ schedules: [] }),
      setOffline: () => set({ syncStatus: 'offline' }),
    }),
    {
      name: 'schedule-store',
    }
  )
); 
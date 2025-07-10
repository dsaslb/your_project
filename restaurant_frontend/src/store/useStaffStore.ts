import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type Staff = {
  id: number;
  name: string;
  email: string;
  phone: string;
  position: string;
  role: string;
  branchId: number;
  updatedAt: string;
};

export type SyncStatus = 'synced' | 'pending' | 'offline' | 'error';

interface StaffStore {
  staffList: Staff[];
  staff: Staff[]; // 별칭 추가
  syncStatus: SyncStatus;
  lastSync: string | null;
  fetchStaff: () => Promise<void>;
  addOrUpdateStaff: (staff: Staff) => void;
  addStaff: (staff: Omit<Staff, 'id' | 'updatedAt'>) => void;
  removeStaff: (id: number) => void;
  clearAll: () => void;
  manualSync: () => Promise<void>;
  setOffline: () => void;
}

export const useStaffStore = create<StaffStore>()(
  persist(
    (set, get) => ({
      staffList: [],
      staff: [], // 별칭 추가
      syncStatus: 'synced',
      lastSync: null,
      fetchStaff: async () => {
        try {
          set({ syncStatus: 'pending' });
          // 실제 API 주소로 교체 필요
          const res = await fetch('/api/staff');
          if (!res.ok) throw new Error('API 오류');
          const data: Staff[] = await res.json();
          set({ staffList: data, staff: data, syncStatus: 'synced', lastSync: new Date().toISOString() });
        } catch (e: unknown) {
          set({ syncStatus: 'offline' });
        }
      },
      addOrUpdateStaff: (staff: Staff) => {
        set((state: StaffStore) => {
          const exists = state.staffList.find((s) => s.id === staff.id);
          let newList: Staff[];
          if (exists) {
            newList = state.staffList.map((s) => (s.id === staff.id ? staff : s));
          } else {
            newList = [...state.staffList, staff];
          }
          return { staffList: newList, staff: newList, syncStatus: 'pending' };
        });
      },
      addStaff: (staffData) => {
        const newStaff: Staff = {
          ...staffData,
          id: Date.now(),
          updatedAt: new Date().toISOString(),
        };
        set((state: StaffStore) => ({
          staffList: [...state.staffList, newStaff],
          staff: [...state.staff, newStaff],
          syncStatus: 'pending',
        }));
      },
      removeStaff: (id: number) => {
        set((state: StaffStore) => ({ 
          staffList: state.staffList.filter((s) => s.id !== id), 
          staff: state.staff.filter((s) => s.id !== id),
          syncStatus: 'pending' 
        }));
      },
      clearAll: () => set({ staffList: [], staff: [] }),
      manualSync: async () => {
        await get().fetchStaff();
      },
      setOffline: () => set({ syncStatus: 'offline' }),
    }),
    {
      name: 'staff-store',
    }
  )
); 
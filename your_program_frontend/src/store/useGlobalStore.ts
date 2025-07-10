import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// 계층형 데이터 타입 정의
export type Industry = {
  id: string;
  name: string;
  brands: Brand[];
};
export type Brand = {
  id: string;
  name: string;
  stores: Store[];
};
export type Store = {
  id: string;
  name: string;
  staff: Staff[];
};
export type Staff = {
  id: string;
  name: string;
  role: string;
};

// 플러그인 타입(업종별/지점별 기능 확장)
export type Plugin = {
  id: string;
  name: string;
  enabled: boolean;
  onLoad?: () => void;
};

// 글로벌 스토어 상태
interface GlobalStoreState {
  industries: Industry[];
  selectedIndustryId: string | null;
  selectedBrandId: string | null;
  selectedStoreId: string | null;
  plugins: Plugin[];
  isOnline: boolean;
  lastSync: string | null;
  // 동기화/오프라인 관련
  syncPending: boolean;
  offlineQueue: any[];
  // 액션
  setIndustries: (industries: Industry[]) => void;
  setSelectedIndustry: (id: string) => void;
  setSelectedBrand: (id: string) => void;
  setSelectedStore: (id: string) => void;
  addPlugin: (plugin: Plugin) => void;
  setOnline: (online: boolean) => void;
  enqueueOfflineAction: (action: any) => void;
  syncData: () => void;
}

export const useGlobalStore = create<GlobalStoreState>()(
  persist(
    (set, get) => ({
      industries: [],
      selectedIndustryId: null,
      selectedBrandId: null,
      selectedStoreId: null,
      plugins: [],
      isOnline: true,
      lastSync: null,
      syncPending: false,
      offlineQueue: [],
      setIndustries: (industries: Industry[]) => set({ industries }),
      setSelectedIndustry: (id: string) => set({ selectedIndustryId: id }),
      setSelectedBrand: (id: string) => set({ selectedBrandId: id }),
      setSelectedStore: (id: string) => set({ selectedStoreId: id }),
      addPlugin: (plugin: Plugin) => set((state: GlobalStoreState) => ({ plugins: [...state.plugins, plugin] })),
      setOnline: (online: boolean) => set({ isOnline: online }),
      enqueueOfflineAction: (action: any) => set((state: GlobalStoreState) => ({ offlineQueue: [...state.offlineQueue, action] })),
      syncData: () => set((state: GlobalStoreState) => ({ lastSync: new Date().toLocaleString() })),
    }),
    {
      name: 'global-store',
      partialize: (state: GlobalStoreState) => ({
        industries: state.industries,
        selectedIndustryId: state.selectedIndustryId,
        selectedBrandId: state.selectedBrandId,
        selectedStoreId: state.selectedStoreId,
        plugins: state.plugins,
        offlineQueue: state.offlineQueue,
        lastSync: state.lastSync,
      }),
    }
  )
);

// 실시간 동기화/오프라인 대응/플러그인 구조는 추후 확장 가능 
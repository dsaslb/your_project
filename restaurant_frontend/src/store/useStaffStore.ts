import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export interface Contract {
  id: number;
  contract_number: string;
  start_date: string;
  expiry_date: string;
  renewal_date: string;
  contract_type: string;
  is_expiring_soon: boolean;
  is_expired: boolean;
  days_until_expiry: number;
  file_path?: string;
  file_name?: string;
}

export interface HealthCertificate {
  id: number;
  certificate_number: string;
  issue_date: string;
  expiry_date: string;
  renewal_date: string;
  issuing_authority: string;
  certificate_type: string;
  is_expiring_soon: boolean;
  is_expired: boolean;
  days_until_expiry: number;
  file_path?: string;
  file_name?: string;
}

export interface StaffMember {
  id: number;
  name: string;
  position: string;
  department: string;
  email: string;
  phone: string;
  join_date: string;
  status: 'active' | 'inactive' | 'pending';
  contracts: Contract[];
  health_certificates: HealthCertificate[];
  username?: string;
  permissions?: any;
}

interface StaffStore {
  // 상태
  staffMembers: StaffMember[];
  pendingStaff: StaffMember[];
  expiringDocuments: any;
  loading: boolean;
  error: string | null;

  // 액션
  setStaffMembers: (staff: StaffMember[]) => void;
  setPendingStaff: (staff: StaffMember[]) => void;
  setExpiringDocuments: (documents: any) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  
  // 직원 관리
  addStaff: (staff: StaffMember) => void;
  updateStaff: (id: number, updates: Partial<StaffMember>) => void;
  deleteStaff: (id: number) => void;
  updateStaffStatus: (id: number, status: string) => void;
  
  // API 호출
  fetchStaffData: () => Promise<void>;
  fetchPendingStaff: () => Promise<void>;
  fetchExpiringDocuments: () => Promise<void>;
  refreshAllData: () => Promise<void>;
  
  // 유틸리티
  getActiveStaff: () => StaffMember[];
  getStaffById: (id: number) => StaffMember | undefined;
  getStaffByName: (name: string) => StaffMember | undefined;
}

// 더미 데이터 (API 실패 시 사용)
const getDummyStaffData = (): StaffMember[] => [
  {
    id: 1,
    name: '김철수',
    position: '주방장',
    department: '주방',
    email: 'kim@restaurant.com',
    phone: '010-1234-5678',
    join_date: '2023-01-15',
    status: 'active',
    contracts: [
      {
        id: 1,
        contract_number: 'CT-2023-001',
        start_date: '2023-01-15',
        expiry_date: '2024-12-31',
        renewal_date: '2024-12-15',
        contract_type: '정규직',
        is_expiring_soon: true,
        is_expired: false,
        days_until_expiry: 25,
        file_path: '/documents/contract1.pdf',
        file_name: '김철수_계약서.pdf'
      }
    ],
    health_certificates: [
      {
        id: 1,
        certificate_number: 'HC-2023-001',
        issue_date: '2023-01-10',
        expiry_date: '2024-11-15',
        renewal_date: '2024-11-01',
        issuing_authority: '서울시보건소',
        certificate_type: '식품위생교육',
        is_expiring_soon: true,
        is_expired: false,
        days_until_expiry: 15,
        file_path: '/documents/health1.pdf',
        file_name: '김철수_보건증.pdf'
      }
    ]
  },
  {
    id: 2,
    name: '이영희',
    position: '서버',
    department: '홀',
    email: 'lee@restaurant.com',
    phone: '010-2345-6789',
    join_date: '2023-02-01',
    status: 'active',
    contracts: [
      {
        id: 2,
        contract_number: 'CT-2023-002',
        start_date: '2023-02-01',
        expiry_date: '2024-12-31',
        renewal_date: '2024-12-15',
        contract_type: '정규직',
        is_expiring_soon: true,
        is_expired: false,
        days_until_expiry: 25,
        file_path: '/documents/contract2.pdf',
        file_name: '이영희_계약서.pdf'
      }
    ],
    health_certificates: [
      {
        id: 2,
        certificate_number: 'HC-2023-002',
        issue_date: '2023-01-25',
        expiry_date: '2024-11-20',
        renewal_date: '2024-11-05',
        issuing_authority: '서울시보건소',
        certificate_type: '식품위생교육',
        is_expiring_soon: true,
        is_expired: false,
        days_until_expiry: 20,
        file_path: '/documents/health2.pdf',
        file_name: '이영희_보건증.pdf'
      }
    ]
  },
  {
    id: 3,
    name: '박민수',
    position: '주방직원',
    department: '주방',
    email: 'park@restaurant.com',
    phone: '010-3456-7890',
    join_date: '2023-03-01',
    status: 'pending',
    contracts: [],
    health_certificates: []
  }
];

export const useStaffStore = create<StaffStore>()(
  devtools(
    (set, get) => ({
      // 초기 상태
      staffMembers: [],
      pendingStaff: [],
      expiringDocuments: null,
      loading: false,
      error: null,

      // 상태 설정
      setStaffMembers: (staff) => set({ staffMembers: staff }),
      setPendingStaff: (staff) => set({ pendingStaff: staff }),
      setExpiringDocuments: (documents) => set({ expiringDocuments: documents }),
      setLoading: (loading) => set({ loading }),
      setError: (error) => set({ error }),

      // 직원 관리
      addStaff: (staff) => set((state) => ({
        staffMembers: [...state.staffMembers, staff]
      })),

      updateStaff: (id, updates) => set((state) => ({
        staffMembers: state.staffMembers.map(staff =>
          staff.id === id ? { ...staff, ...updates } : staff
        )
      })),

      deleteStaff: (id) => set((state) => ({
        staffMembers: state.staffMembers.filter(staff => staff.id !== id)
      })),

      updateStaffStatus: (id, status) => set((state) => ({
        staffMembers: state.staffMembers.map(staff =>
          staff.id === id ? { ...staff, status: status as any } : staff
        )
      })),

      // API 호출
      fetchStaffData: async () => {
        set({ loading: true, error: null });
        try {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 5000);

          const response = await fetch('http://localhost:5000/api/staff', {
            credentials: 'include',
            headers: {
              'Content-Type': 'application/json',
            },
            signal: controller.signal,
          });
          
          clearTimeout(timeoutId);
          
          if (response.ok) {
            const data = await response.json();
            if (data.success) {
              const activeStaff = (data.staff || []).filter((staff: any) => 
                staff.status === 'active' || staff.status === 'pending'
              );
              set({ staffMembers: activeStaff, loading: false });
              console.log('직원 데이터 로드 성공:', activeStaff.length, '명');
            } else {
              console.error('직원 데이터 로드 실패:', data.error);
              set({ staffMembers: getDummyStaffData(), loading: false });
            }
          } else {
            console.error('직원 데이터 로드 실패:', response.status);
            set({ staffMembers: getDummyStaffData(), loading: false });
          }
        } catch (error) {
          console.error('API 호출 오류:', error);
          if (error instanceof Error && error.name === 'AbortError') {
            console.log('API 호출 타임아웃 - 더미 데이터 사용');
          }
          set({ staffMembers: getDummyStaffData(), loading: false });
        }
      },

      fetchPendingStaff: async () => {
        try {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 5000);

          const response = await fetch('http://localhost:5000/api/staff/pending', {
            credentials: 'include',
            headers: {
              'Content-Type': 'application/json',
            },
            signal: controller.signal,
          });
          
          clearTimeout(timeoutId);
          
          if (response.ok) {
            const data = await response.json();
            if (data.success) {
              set({ pendingStaff: data.staff || [] });
            } else {
              console.error('미승인 직원 로드 실패:', data.error);
            }
          } else {
            console.error('미승인 직원 로드 실패:', response.status);
          }
        } catch (error) {
          console.error('미승인 직원 로드 오류:', error);
        }
      },

      fetchExpiringDocuments: async () => {
        try {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 5000);

          const response = await fetch('http://localhost:5000/api/staff/expiring-documents', {
            credentials: 'include',
            headers: {
              'Content-Type': 'application/json',
            },
            signal: controller.signal,
          });
          
          clearTimeout(timeoutId);
          
          if (response.ok) {
            const data = await response.json();
            if (data.success) {
              set({ expiringDocuments: data });
            } else {
              console.error('만료 임박 문서 로드 실패:', data.error);
            }
          } else {
            console.error('만료 임박 문서 로드 실패:', response.status);
          }
        } catch (error) {
          console.error('만료 임박 문서 로드 오류:', error);
        }
      },

      refreshAllData: async () => {
        console.log('직원 데이터 전체 새로고침 중...');
        await Promise.all([
          get().fetchStaffData(),
          get().fetchPendingStaff(),
          get().fetchExpiringDocuments()
        ]);
        // 다른 Store들에게 알림
        window.dispatchEvent(new CustomEvent('staffDataUpdated'));
      },

      // 유틸리티
      getActiveStaff: () => {
        const { staffMembers } = get();
        return staffMembers.filter(staff => 
          staff.status === 'active' || staff.status === 'pending'
        );
      },

      getStaffById: (id) => {
        const { staffMembers } = get();
        return staffMembers.find(staff => staff.id === id);
      },

      getStaffByName: (name) => {
        const { staffMembers } = get();
        return staffMembers.find(staff => staff.name === name);
      },
    }),
    {
      name: 'staff-store',
    }
  )
); 
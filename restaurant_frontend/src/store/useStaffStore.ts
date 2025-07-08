import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { apiGet } from '../lib/api';

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
  updateStaffStatus: (id: number, status: 'active' | 'inactive' | 'pending') => void;
  
  // API 호출
  fetchStaffData: (pageType: string) => Promise<void>;
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

      updateStaffStatus: (id, status: 'active' | 'inactive' | 'pending') => set((state) => ({
        staffMembers: state.staffMembers.map(staff =>
          staff.id === id ? { ...staff, status } : staff
        )
      })),

      // API 호출
      fetchStaffData: async (pageType: string) => {
        set({ loading: true, error: null });
        
        try {
          const result = await apiGet<any[]>(`/api/staff/${pageType}`);
          
          if (result.error) {
            // 백엔드 연결 안 됨 - 더미 데이터 사용
            console.log('백엔드 연결 안 됨, 더미 데이터 사용');
            const dummyData = getDummyStaffData();
            set({ 
              staffMembers: dummyData,
              loading: false 
            });
            return;
          }
          
          set({ staffMembers: result.data || [], loading: false });
        } catch (error) {
          console.error('직원 데이터 가져오기 오류:', error);
          // 오류 시에도 더미 데이터 사용
          const dummyData = getDummyStaffData();
          set({ 
            staffMembers: dummyData,
            loading: false,
            error: '데이터를 가져올 수 없어 더미 데이터를 표시합니다.'
          });
        }
      },

      fetchPendingStaff: async () => {
        set({ loading: true, error: null });
        
        try {
          const result = await apiGet<any[]>('/api/staff/pending');
          
          if (result.error) {
            // 백엔드 연결 안 됨 - 더미 데이터에서 pending 상태만 필터링
            const dummyData = getDummyStaffData();
            const pendingData = dummyData.filter(staff => staff.status === 'pending');
            set({ 
              pendingStaff: pendingData,
              loading: false 
            });
            return;
          }
          
          set({ pendingStaff: result.data || [], loading: false });
        } catch (error) {
          console.error('대기 중인 직원 데이터 가져오기 오류:', error);
          const dummyData = getDummyStaffData();
          const pendingData = dummyData.filter(staff => staff.status === 'pending');
          set({ 
            pendingStaff: pendingData,
            loading: false,
            error: '데이터를 가져올 수 없어 더미 데이터를 표시합니다.'
          });
        }
      },

      fetchExpiringDocuments: async () => {
        set({ loading: true, error: null });
        
        try {
          const result = await apiGet<any>('/api/staff/expiring-documents');
          
          if (result.error) {
            // 백엔드 연결 안 됨 - 더미 만료 문서 데이터
            const dummyExpiringDocs = {
              contracts: [
                {
                  id: 1,
                  staff_name: '김철수',
                  document_type: '계약서',
                  expiry_date: '2024-12-31',
                  days_until_expiry: 25
                },
                {
                  id: 2,
                  staff_name: '이영희',
                  document_type: '계약서',
                  expiry_date: '2024-12-31',
                  days_until_expiry: 25
                }
              ],
              health_certificates: [
                {
                  id: 1,
                  staff_name: '김철수',
                  document_type: '보건증',
                  expiry_date: '2024-11-15',
                  days_until_expiry: 15
                },
                {
                  id: 2,
                  staff_name: '이영희',
                  document_type: '보건증',
                  expiry_date: '2024-11-20',
                  days_until_expiry: 20
                }
              ]
            };
            set({ 
              expiringDocuments: dummyExpiringDocs,
              loading: false 
            });
            return;
          }
          
          set({ expiringDocuments: result.data, loading: false });
        } catch (error) {
          console.error('만료 문서 데이터 가져오기 오류:', error);
          set({ 
            loading: false,
            error: '만료 문서 데이터를 가져올 수 없습니다.'
          });
        }
      },

      refreshAllData: async () => {
        const { fetchStaffData, fetchPendingStaff, fetchExpiringDocuments } = get();
        await Promise.all([
          fetchStaffData('all'),
          fetchPendingStaff(),
          fetchExpiringDocuments()
        ]);
      },

      // 유틸리티
      getActiveStaff: () => {
        const { staffMembers } = get();
        return staffMembers.filter(staff => staff.status === 'active');
      },

      getStaffById: (id: number) => {
        const { staffMembers } = get();
        return staffMembers.find(staff => staff.id === id);
      },

      getStaffByName: (name: string) => {
        const { staffMembers } = get();
        return staffMembers.find(staff => staff.name === name);
      }
    }),
    {
      name: 'staff-store'
    }
  )
); 
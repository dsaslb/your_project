'use client';

// 오프라인 스토리지 유틸리티
export class OfflineStorage {
  private static readonly STORAGE_KEYS = {
    INDUSTRIES: 'offline_industries',
    BRANDS: 'offline_brands',
    STORES: 'offline_stores',
    EMPLOYEES: 'offline_employees',
    LAST_SYNC: 'last_sync_timestamp',
    IS_OFFLINE: 'is_offline_mode'
  };

  // 데이터 저장
  static saveData<T>(key: string, data: T): void {
    try {
      if (typeof window !== 'undefined') {
        localStorage.setItem(key, JSON.stringify(data));
        console.log(`💾 오프라인 저장 완료: ${key}`, data);
      }
    } catch (error) {
      console.error(`❌ 오프라인 저장 실패: ${key}`, error);
    }
  }

  // 데이터 로드
  static loadData<T>(key: string): T | null {
    try {
      if (typeof window !== 'undefined') {
        const data = localStorage.getItem(key);
        if (data) {
          const parsed = JSON.parse(data);
          console.log(`📂 오프라인 데이터 로드: ${key}`, parsed);
          return parsed;
        }
      }
    } catch (error) {
      console.error(`❌ 오프라인 데이터 로드 실패: ${key}`, error);
    }
    return null;
  }

  // 업종 데이터 관리
  static saveIndustries(industries: any[]): void {
    this.saveData(this.STORAGE_KEYS.INDUSTRIES, industries);
  }

  static loadIndustries(): any[] {
    return this.loadData(this.STORAGE_KEYS.INDUSTRIES) || [];
  }

  // 브랜드 데이터 관리
  static saveBrands(brands: any[]): void {
    this.saveData(this.STORAGE_KEYS.BRANDS, brands);
  }

  static loadBrands(): any[] {
    return this.loadData(this.STORAGE_KEYS.BRANDS) || [];
  }

  // 매장 데이터 관리
  static saveStores(stores: any[]): void {
    this.saveData(this.STORAGE_KEYS.STORES, stores);
  }

  static loadStores(): any[] {
    return this.loadData(this.STORAGE_KEYS.STORES) || [];
  }

  // 직원 데이터 관리
  static saveEmployees(employees: any[]): void {
    this.saveData(this.STORAGE_KEYS.EMPLOYEES, employees);
  }

  static loadEmployees(): any[] {
    return this.loadData(this.STORAGE_KEYS.EMPLOYEES) || [];
  }

  // 마지막 동기화 시간 관리
  static saveLastSync(): void {
    this.saveData(this.STORAGE_KEYS.LAST_SYNC, new Date().toISOString());
  }

  static getLastSync(): string | null {
    return this.loadData(this.STORAGE_KEYS.LAST_SYNC);
  }

  // 오프라인 모드 상태 관리
  static setOfflineMode(isOffline: boolean): void {
    this.saveData(this.STORAGE_KEYS.IS_OFFLINE, isOffline);
  }

  static isOfflineMode(): boolean {
    return this.loadData(this.STORAGE_KEYS.IS_OFFLINE) || false;
  }

  // 모든 데이터 삭제
  static clearAll(): void {
    try {
      if (typeof window !== 'undefined') {
        Object.values(this.STORAGE_KEYS).forEach(key => {
          localStorage.removeItem(key);
        });
        console.log('🗑️ 모든 오프라인 데이터 삭제 완료');
      }
    } catch (error) {
      console.error('❌ 오프라인 데이터 삭제 실패:', error);
    }
  }

  // 기본 데이터 생성 (오프라인 모드용)
  static createDefaultData() {
    const defaultIndustries = [
      {
        id: 1,
        name: '음식점',
        code: 'FOOD',
        description: '음식점 및 카페 업종',
        brand_count: 5,
        status: 'active',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      {
        id: 2,
        name: '소매업',
        code: 'RETAIL',
        description: '소매 및 도매 업종',
        brand_count: 3,
        status: 'active',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      {
        id: 3,
        name: '서비스업',
        code: 'SERVICE',
        description: '다양한 서비스 업종',
        brand_count: 4,
        status: 'active',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    ];

    const defaultBrands = [
      {
        id: 1,
        name: '스타벅스',
        code: 'SBUX',
        description: '글로벌 커피 체인',
        industry_id: 1,
        store_count: 12,
        employee_count: 45,
        status: 'active',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      {
        id: 2,
        name: '맥도날드',
        code: 'MCD',
        description: '패스트푸드 체인',
        industry_id: 1,
        store_count: 8,
        employee_count: 32,
        status: 'active',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      {
        id: 3,
        name: '올리브영',
        code: 'OLIVE',
        description: '뷰티 소매 체인',
        industry_id: 2,
        store_count: 15,
        employee_count: 28,
        status: 'active',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    ];

    const defaultStores = [
      {
        id: 1,
        name: '강남점',
        code: 'GN001',
        address: '서울시 강남구 테헤란로 123',
        phone: '02-1234-5678',
        manager_name: '김매니저',
        brand_id: 1,
        employee_count: 15,
        status: 'active',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      {
        id: 2,
        name: '홍대점',
        code: 'HD001',
        address: '서울시 마포구 홍대로 456',
        phone: '02-2345-6789',
        manager_name: '이매니저',
        brand_id: 1,
        employee_count: 12,
        status: 'active',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      {
        id: 3,
        name: '신촌점',
        code: 'SC001',
        address: '서울시 서대문구 신촌로 789',
        phone: '02-3456-7890',
        manager_name: '박매니저',
        brand_id: 2,
        employee_count: 18,
        status: 'active',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    ];

    const defaultEmployees = [
      {
        id: '1',
        name: '김철수',
        email: 'kim@example.com',
        phone: '010-1234-5678',
        role: '매니저',
        department: '영업팀',
        hireDate: '2023-01-15',
        status: 'active',
        location: '서울 강남점',
        lastActive: '2024-01-15 14:30',
        workHours: 160,
        performance: 95,
      },
      {
        id: '2',
        name: '이영희',
        email: 'lee@example.com',
        phone: '010-2345-6789',
        role: '직원',
        department: '고객서비스팀',
        hireDate: '2023-03-20',
        status: 'active',
        location: '서울 강남점',
        lastActive: '2024-01-15 15:45',
        workHours: 140,
        performance: 88,
      },
      {
        id: '3',
        name: '박민수',
        email: 'park@example.com',
        phone: '010-3456-7890',
        role: '팀장',
        department: '개발팀',
        hireDate: '2022-08-10',
        status: 'active',
        location: '서울 홍대점',
        lastActive: '2024-01-15 16:20',
        workHours: 180,
        performance: 92,
      }
    ];

    // 기본 데이터 저장
    this.saveIndustries(defaultIndustries);
    this.saveBrands(defaultBrands);
    this.saveStores(defaultStores);
    this.saveEmployees(defaultEmployees);
    this.saveLastSync();
    this.setOfflineMode(true);

    console.log('📦 기본 오프라인 데이터 생성 완료');
    return { 
      industries: defaultIndustries, 
      brands: defaultBrands, 
      stores: defaultStores, 
      employees: defaultEmployees 
    };
  }

  // 데이터 동기화 상태 확인
  static getSyncStatus() {
    const lastSync = this.getLastSync();
    const isOffline = this.isOfflineMode();
    
    return {
      isOffline,
      lastSync: lastSync ? new Date(lastSync).toLocaleString('ko-KR') : '동기화 없음',
      hasData: {
        industries: this.loadIndustries().length > 0,
        brands: this.loadBrands().length > 0,
        stores: this.loadStores().length > 0,
        employees: this.loadEmployees().length > 0
      }
    };
  }
} 
import { apiCall } from './api';

// 자동 생성된 API 타입 import (생성 후 활성화)
// import type { paths } from '@/types/api-types';

/**
 * API 클라이언트 - 자동 생성된 타입을 사용
 * OpenAPI 스펙에서 자동으로 생성된 타입을 활용하여 타입 안전성 보장
 */

// 타입 정의 (임시, 자동 생성 후 교체)
export interface ApiPaths {
  '/api/admin/brands': {
    get: {
      responses: {
        200: {
          content: {
            'application/json': {
              success: boolean;
              data: Brand[];
              message?: string;
            };
          };
        };
      };
    };
    post: {
      requestBody: {
        content: {
          'application/json': CreateBrandRequest;
        };
      };
      responses: {
        201: {
          content: {
            'application/json': {
              success: boolean;
              data: Brand;
              message?: string;
            };
          };
        };
      };
    };
  };
  '/api/admin/stores': {
    get: {
      responses: {
        200: {
          content: {
            'application/json': {
              success: boolean;
              data: Store[];
              message?: string;
            };
          };
        };
      };
    };
  };
  '/api/admin/employees': {
    get: {
      responses: {
        200: {
          content: {
            'application/json': {
              success: boolean;
              data: { employees: Employee[] };
              message?: string;
            };
          };
        };
      };
    };
  };
  '/api/admin/brand_stats': {
    get: {
      responses: {
        200: {
          content: {
            'application/json': {
              success: boolean;
              data: BrandStats;
              message?: string;
            };
          };
        };
      };
    };
  };
  '/api/admin/store_stats': {
    get: {
      responses: {
        200: {
          content: {
            'application/json': {
              success: boolean;
              data: StoreStats;
              message?: string;
            };
          };
        };
      };
    };
  };
  '/api/admin/system-logs': {
    get: {
      responses: {
        200: {
          content: {
            'application/json': {
              success: boolean;
              data: SystemLog[];
              message?: string;
            };
          };
        };
      };
    };
  };
}

// 타입 정의
export interface Brand {
  id: number;
  name: string;
  industry_id: number;
  description?: string;
  website?: string;
  contact_email?: string;
  contact_phone?: string;
  address?: string;
  status: 'active' | 'inactive' | 'pending';
  created_at: string;
  updated_at: string;
}

export interface CreateBrandRequest {
  name: string;
  industry_id: number;
  description?: string;
  website?: string;
  contact_email?: string;
  contact_phone?: string;
  address?: string;
}

export interface Store {
  id: number;
  name: string;
  brand_id: number;
  address: string;
  phone?: string;
  manager_id?: number;
  status: 'active' | 'inactive' | 'pending';
  created_at: string;
  updated_at: string;
}

export interface Employee {
  id: number;
  name: string;
  role: 'manager' | 'staff' | 'kitchen' | 'cashier';
  status: 'active' | 'break' | 'off';
  start_time?: string;
  end_time?: string;
  avatar?: string;
}

export interface BrandStats {
  total_brands: number;
  active_brands: number;
  total_stores: number;
  total_employees: number;
  total_revenue: number;
  growth_rate: number;
}

export interface StoreStats {
  total_employees: number;
  active_employees: number;
  today_revenue: number;
  monthly_revenue: number;
  growth_rate: number;
  average_order_value: number;
  customer_satisfaction: number;
  pending_orders: number;
  low_stock_items: number;
}

export interface SystemLog {
  id: number;
  level: 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
  message: string;
  detail?: string;
  timestamp: string;
  user_id?: number;
  ip_address?: string;
}

// 타입 안전한 API 클라이언트
export class ApiClient {
  /**
   * 브랜드 목록 조회
   */
  static async getBrands() {
    return apiCall<Brand[]>('/api/admin/brands');
  }

  /**
   * 브랜드 생성
   */
  static async createBrand(data: CreateBrandRequest) {
    return apiCall<Brand>('/api/admin/brands', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * 매장 목록 조회
   */
  static async getStores() {
    return apiCall<Store[]>('/api/admin/stores');
  }

  /**
   * 직원 목록 조회
   */
  static async getEmployees() {
    return apiCall<{ employees: Employee[] }>('/api/admin/employees');
  }

  /**
   * 브랜드 통계 조회
   */
  static async getBrandStats() {
    return apiCall<BrandStats>('/api/admin/brand_stats');
  }

  /**
   * 매장 통계 조회
   */
  static async getStoreStats() {
    return apiCall<StoreStats>('/api/admin/store_stats');
  }

  /**
   * 시스템 로그 조회
   */
  static async getSystemLogs() {
    return apiCall<SystemLog[]>('/api/admin/system-logs');
  }
}

// 편의 함수들
export const apiClient = {
  brands: {
    list: ApiClient.getBrands,
    create: ApiClient.createBrand,
  },
  stores: {
    list: ApiClient.getStores,
  },
  employees: {
    list: ApiClient.getEmployees,
  },
  stats: {
    brands: ApiClient.getBrandStats,
    stores: ApiClient.getStoreStats,
  },
  system: {
    logs: ApiClient.getSystemLogs,
  },
}; 
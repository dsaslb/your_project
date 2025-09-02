import SafePost from '../utils/safePost';

// 발주 아이템 인터페이스
export interface PurchaseOrderItem {
  barcode: string;
  name: string;
  qty: number;
}

// 발주 생성 요청 인터페이스
export interface CreatePurchaseOrderRequest {
  branch_id: string;
  items: PurchaseOrderItem[];
  notes?: string;
  priority?: 'low' | 'medium' | 'high';
}

// 발주 생성 응답 인터페이스
export interface CreatePurchaseOrderResponse {
  success: boolean;
  data?: {
    po_id: string;
    branch_id: string;
    items: PurchaseOrderItem[];
    status: string;
    created_at: string;
    total_items: number;
  };
  error?: string;
  message?: string;
}

/**
 * 발주 생성 API 클라이언트
 */
export class PurchaseOrderAPI {
  private static readonly BASE_URL = 'http://localhost:5000/api/mobile';

  /**
   * 새로운 발주 생성
   */
  static async createPurchaseOrder(
    request: CreatePurchaseOrderRequest
  ): Promise<CreatePurchaseOrderResponse> {
    try {
      console.log('📋 발주 생성 요청:', request);

      const response = await SafePost.post<CreatePurchaseOrderResponse>(
        `${this.BASE_URL}/purchase_orders`,
        request,
        {
          'Authorization': 'Bearer mobile_token', // 실제 구현에서는 실제 토큰 사용
          'X-Client-Version': '1.0.0'
        }
      );

      if (response.success) {
        console.log('✅ 발주 생성 성공:', response.data);
        return response;
      } else {
        console.log('❌ 발주 생성 실패:', response.message);
        return response;
      }

    } catch (error) {
      console.error('❌ 발주 생성 API 오류:', error);
      return {
        success: false,
        error: 'api_error',
        message: '발주 생성 중 오류가 발생했습니다.'
      };
    }
  }

  /**
   * 발주 상태 조회
   */
  static async getPurchaseOrderStatus(poId: string): Promise<any> {
    try {
      const response = await fetch(`${this.BASE_URL}/purchase_orders/${poId}/status`, {
        method: 'GET',
        headers: {
          'Authorization': 'Bearer mobile_token',
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        console.log('✅ 발주 상태 조회 성공:', data);
        return { success: true, data };
      } else {
        console.log('❌ 발주 상태 조회 실패:', response.status);
        return { success: false, error: 'http_error' };
      }

    } catch (error) {
      console.error('❌ 발주 상태 조회 오류:', error);
      return { success: false, error: 'network_error' };
    }
  }

  /**
   * 지점별 발주 목록 조회
   */
  static async getPurchaseOrdersByBranch(branchId: string): Promise<any> {
    try {
      const response = await fetch(`${this.BASE_URL}/purchase_orders?branch_id=${branchId}`, {
        method: 'GET',
        headers: {
          'Authorization': 'Bearer mobile_token',
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        console.log('✅ 발주 목록 조회 성공:', data);
        return { success: true, data };
      } else {
        console.log('❌ 발주 목록 조회 실패:', response.status);
        return { success: false, error: 'http_error' };
      }

    } catch (error) {
      console.error('❌ 발주 목록 조회 오류:', error);
      return { success: false, error: 'network_error' };
    }
  }

  /**
   * 발주 취소
   */
  static async cancelPurchaseOrder(poId: string, reason?: string): Promise<any> {
    try {
      const response = await SafePost.put(
        `${this.BASE_URL}/purchase_orders/${poId}/cancel`,
        { reason },
        {
          'Authorization': 'Bearer mobile_token',
          'Content-Type': 'application/json'
        }
      );

      if (response.success) {
        console.log('✅ 발주 취소 성공:', poId);
        return response;
      } else {
        console.log('❌ 발주 취소 실패:', response.message);
        return response;
      }

    } catch (error) {
      console.error('❌ 발주 취소 API 오류:', error);
      return {
        success: false,
        error: 'api_error',
        message: '발주 취소 중 오류가 발생했습니다.'
      };
    }
  }
}

export default PurchaseOrderAPI;

import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';
import { v4 as uuidv4 } from 'uuid';

// 오프라인 큐 인터페이스
interface QueuedRequest {
  id: string;
  url: string;
  method: string;
  headers: Record<string, string>;
  body: any;
  timestamp: number;
  retryCount: number;
}

// API 응답 인터페이스
interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

/**
 * 안전한 POST 요청 유틸리티
 * - 자동으로 idempotency 키 추가
 * - 오프라인 시 큐에 저장
 * - 재연결 시 자동 재전송
 */
export class SafePost {
  private static readonly QUEUE_KEY = 'offline_request_queue';
  private static readonly MAX_RETRY_COUNT = 3;
  private static readonly RETRY_DELAY = 5000; // 5초

  /**
   * POST 요청 실행
   */
  static async post<T>(
    url: string,
    data: any,
    headers: Record<string, string> = {}
  ): Promise<ApiResponse<T>> {
    try {
      // 네트워크 상태 확인
      const netInfo = await NetInfo.fetch();
      
      if (!netInfo.isConnected) {
        // 오프라인: 큐에 저장
        console.log('📱 오프라인 상태 - 요청을 큐에 저장합니다');
        await this.addToQueue(url, 'POST', data, headers);
        return {
          success: false,
          error: 'offline',
          message: '오프라인 상태입니다. 요청이 큐에 저장되었습니다.'
        };
      }

      // 온라인: 즉시 요청 실행
      return await this.executeRequest<T>(url, 'POST', data, headers);
      
    } catch (error) {
      console.error('❌ SafePost 오류:', error);
      return {
        success: false,
        error: 'unknown',
        message: '요청 실행 중 오류가 발생했습니다.'
      };
    }
  }

  /**
   * PUT 요청 실행
   */
  static async put<T>(
    url: string,
    data: any,
    headers: Record<string, string> = {}
  ): Promise<ApiResponse<T>> {
    try {
      const netInfo = await NetInfo.fetch();
      
      if (!netInfo.isConnected) {
        await this.addToQueue(url, 'PUT', data, headers);
        return {
          success: false,
          error: 'offline',
          message: '오프라인 상태입니다. 요청이 큐에 저장되었습니다.'
        };
      }

      return await this.executeRequest<T>(url, 'PUT', data, headers);
      
    } catch (error) {
      console.error('❌ SafePost 오류:', error);
      return {
        success: false,
        error: 'unknown',
        message: '요청 실행 중 오류가 발생했습니다.'
      };
    }
  }

  /**
   * DELETE 요청 실행
   */
  static async delete<T>(
    url: string,
    headers: Record<string, string> = {}
  ): Promise<ApiResponse<T>> {
    try {
      const netInfo = await NetInfo.fetch();
      
      if (!netInfo.isConnected) {
        await this.addToQueue(url, 'DELETE', null, headers);
        return {
          success: false,
          error: 'offline',
          message: '오프라인 상태입니다. 요청이 큐에 저장되었습니다.'
        };
      }

      return await this.executeRequest<T>(url, 'DELETE', null, headers);
      
    } catch (error) {
      console.error('❌ SafePost 오류:', error);
      return {
        success: false,
        error: 'unknown',
        message: '요청 실행 중 오류가 발생했습니다.'
      };
    }
  }

  /**
   * 실제 HTTP 요청 실행
   */
  private static async executeRequest<T>(
    url: string,
    method: string,
    data: any,
    headers: Record<string, string>
  ): Promise<ApiResponse<T>> {
    // Idempotency 키 생성
    const idempotencyKey = uuidv4();
    
    // 기본 헤더 설정
    const defaultHeaders = {
      'Content-Type': 'application/json',
      'X-Idempotency-Key': idempotencyKey,
      ...headers
    };

    try {
      const response = await fetch(url, {
        method,
        headers: defaultHeaders,
        body: data ? JSON.stringify(data) : undefined
      });

      const responseData = await response.json();

      if (response.ok) {
        return {
          success: true,
          data: responseData
        };
      } else {
        return {
          success: false,
          error: 'http_error',
          message: responseData.message || `HTTP ${response.status} 오류`
        };
      }
      
    } catch (error) {
      console.error('❌ HTTP 요청 실패:', error);
      return {
        success: false,
        error: 'network_error',
        message: '네트워크 요청에 실패했습니다.'
      };
    }
  }

  /**
   * 오프라인 큐에 요청 추가
   */
  private static async addToQueue(
    url: string,
    method: string,
    data: any,
    headers: Record<string, string>
  ): Promise<void> {
    try {
      const queue = await this.getQueue();
      
      const queuedRequest: QueuedRequest = {
        id: uuidv4(),
        url,
        method,
        headers,
        body: data,
        timestamp: Date.now(),
        retryCount: 0
      };

      queue.push(queuedRequest);
      await AsyncStorage.setItem(this.QUEUE_KEY, JSON.stringify(queue));
      
      console.log('📦 요청이 오프라인 큐에 저장되었습니다:', queuedRequest.id);
      
    } catch (error) {
      console.error('❌ 큐 저장 실패:', error);
    }
  }

  /**
   * 오프라인 큐에서 요청 가져오기
   */
  private static async getQueue(): Promise<QueuedRequest[]> {
    try {
      const queueData = await AsyncStorage.getItem(this.QUEUE_KEY);
      return queueData ? JSON.parse(queueData) : [];
    } catch (error) {
      console.error('❌ 큐 읽기 실패:', error);
      return [];
    }
  }

  /**
   * 오프라인 큐 비우기
   */
  static async flushQueue(): Promise<void> {
    try {
      const queue = await this.getQueue();
      
      if (queue.length === 0) {
        console.log('📦 오프라인 큐가 비어있습니다');
        return;
      }

      console.log(`📦 ${queue.length}개의 대기 중인 요청을 처리합니다`);

      const netInfo = await NetInfo.fetch();
      if (!netInfo.isConnected) {
        console.log('❌ 여전히 오프라인 상태입니다');
        return;
      }

      // 큐의 모든 요청을 순차적으로 처리
      for (const request of queue) {
        try {
          if (request.retryCount >= this.MAX_RETRY_COUNT) {
            console.log(`❌ 최대 재시도 횟수 초과: ${request.id}`);
            continue;
          }

          console.log(`🔄 요청 재시도: ${request.id} (${request.retryCount + 1}/${this.MAX_RETRY_COUNT})`);
          
          const result = await this.executeRequest(
            request.url,
            request.method,
            request.body,
            request.headers
          );

          if (result.success) {
            console.log(`✅ 요청 성공: ${request.id}`);
            // 성공한 요청을 큐에서 제거
            await this.removeFromQueue(request.id);
          } else {
            console.log(`❌ 요청 실패: ${request.id}`, result.message);
            // 재시도 횟수 증가
            await this.incrementRetryCount(request.id);
          }

          // 요청 간 지연
          await new Promise(resolve => setTimeout(resolve, 1000));
          
        } catch (error) {
          console.error(`❌ 요청 처리 중 오류: ${request.id}`, error);
          await this.incrementRetryCount(request.id);
        }
      }

      console.log('📦 오프라인 큐 처리 완료');
      
    } catch (error) {
      console.error('❌ 큐 비우기 실패:', error);
    }
  }

  /**
   * 큐에서 특정 요청 제거
   */
  private static async removeFromQueue(requestId: string): Promise<void> {
    try {
      const queue = await this.getQueue();
      const filteredQueue = queue.filter(req => req.id !== requestId);
      await AsyncStorage.setItem(this.QUEUE_KEY, JSON.stringify(filteredQueue));
    } catch (error) {
      console.error('❌ 큐에서 요청 제거 실패:', error);
    }
  }

  /**
   * 재시도 횟수 증가
   */
  private static async incrementRetryCount(requestId: string): Promise<void> {
    try {
      const queue = await this.getQueue();
      const updatedQueue = queue.map(req => 
        req.id === requestId 
          ? { ...req, retryCount: req.retryCount + 1 }
          : req
      );
      await AsyncStorage.setItem(this.QUEUE_KEY, JSON.stringify(updatedQueue));
    } catch (error) {
      console.error('❌ 재시도 횟수 증가 실패:', error);
    }
  }

  /**
   * 큐 상태 확인
   */
  static async getQueueStatus(): Promise<{ count: number; oldestRequest?: QueuedRequest }> {
    try {
      const queue = await this.getQueue();
      const oldestRequest = queue.length > 0 ? queue[0] : undefined;
      
      return {
        count: queue.length,
        oldestRequest
      };
    } catch (error) {
      console.error('❌ 큐 상태 확인 실패:', error);
      return { count: 0 };
    }
  }

  /**
   * 큐 초기화
   */
  static async clearQueue(): Promise<void> {
    try {
      await AsyncStorage.removeItem(this.QUEUE_KEY);
      console.log('📦 오프라인 큐가 초기화되었습니다');
    } catch (error) {
      console.error('❌ 큐 초기화 실패:', error);
    }
  }
}

// 네트워크 상태 변경 감지 및 자동 큐 비우기
NetInfo.addEventListener(state => {
  if (state.isConnected) {
    console.log('🌐 네트워크 연결됨 - 오프라인 큐를 비웁니다');
    SafePost.flushQueue();
  } else {
    console.log('📱 네트워크 연결 끊김');
  }
});

export default SafePost;

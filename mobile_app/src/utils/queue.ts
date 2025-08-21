import AsyncStorage from '@react-native-async-storage/async-storage';
import { api } from '../api/client';
import { v4 as uuid } from 'uuid';

export interface QueueJob {
  id: string;
  url: string;
  method: 'POST' | 'PUT' | 'DELETE';
  body: any;
  headers: Record<string, string>;
  timestamp: number;
  retryCount: number;
  maxRetries: number;
}

export interface SafePostOptions {
  retryCount?: number;
  maxRetries?: number;
  priority?: 'high' | 'normal' | 'low';
}

const QUEUE_STORAGE_KEY = 'offlineQueue';
const MAX_QUEUE_SIZE = 100; // 최대 큐 크기

/**
 * 안전한 POST 요청 - 실패 시 오프라인 큐에 저장
 */
export async function safePost(
  url: string, 
  body: any, 
  options: SafePostOptions = {}
): Promise<any> {
  const idempotencyKey = uuid();
  const headers = {
    'X-Idempotency-Key': idempotencyKey,
    ...options.headers
  };
  
  console.log(`🔒 safePost 호출: ${url} with key: ${idempotencyKey}`);

  try {
    // 네트워크 요청 시도
    const response = await api.post(url, body, { headers });
    console.log(`✅ 요청 성공: ${url}`);
    return response;
  } catch (error: any) {
    console.log(`❌ 요청 실패: ${url} - ${error.message}`);
    
    // 네트워크 오류인 경우에만 큐에 저장
    if (isNetworkError(error)) {
      await addToQueue({
        id: uuid(),
        url,
        method: 'POST',
        body,
        headers,
        timestamp: Date.now(),
        retryCount: 0,
        maxRetries: options.maxRetries || 3
      });
      
      console.log(`📥 오프라인 큐에 추가됨: ${url}`);
      
      // 큐가 너무 커지면 오래된 항목 제거
      await cleanupQueue();
    }
    
    throw error;
  }
}

/**
 * 안전한 PUT 요청
 */
export async function safePut(
  url: string, 
  body: any, 
  options: SafePostOptions = {}
): Promise<any> {
  const idempotencyKey = uuid();
  const headers = {
    'X-Idempotency-Key': idempotencyKey,
    ...options.headers
  };

  try {
    const response = await api.put(url, body, { headers });
    console.log(`✅ PUT 요청 성공: ${url}`);
    return response;
  } catch (error: any) {
    if (isNetworkError(error)) {
      await addToQueue({
        id: uuid(),
        url,
        method: 'PUT',
        body,
        headers,
        timestamp: Date.now(),
        retryCount: 0,
        maxRetries: options.maxRetries || 3
      });
    }
    throw error;
  }
}

/**
 * 오프라인 큐에 작업 추가
 */
async function addToQueue(job: QueueJob): Promise<void> {
  try {
    const queue = await getQueue();
    
    // 중복 URL 체크 (같은 URL의 최신 작업만 유지)
    const existingIndex = queue.findIndex(item => item.url === job.url);
    if (existingIndex !== -1) {
      queue[existingIndex] = job;
    } else {
      queue.push(job);
    }
    
    // 큐 크기 제한
    if (queue.length > MAX_QUEUE_SIZE) {
      queue.sort((a, b) => a.timestamp - b.timestamp);
      queue.splice(0, queue.length - MAX_QUEUE_SIZE);
    }
    
    await AsyncStorage.setItem(QUEUE_STORAGE_KEY, JSON.stringify(queue));
    console.log(`📥 큐에 추가됨: ${job.url} (총 ${queue.length}개)`);
  } catch (error) {
    console.error('큐 저장 실패:', error);
  }
}

/**
 * 큐에서 작업 가져오기
 */
async function getQueue(): Promise<QueueJob[]> {
  try {
    const raw = await AsyncStorage.getItem(QUEUE_STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (error) {
    console.error('큐 로드 실패:', error);
    return [];
  }
}

/**
 * 큐 정리 (오래된 항목 제거)
 */
async function cleanupQueue(): Promise<void> {
  try {
    const queue = await getQueue();
    const now = Date.now();
    const oneDay = 24 * 60 * 60 * 1000; // 24시간
    
    // 24시간 이상 된 항목 제거
    const filtered = queue.filter(job => now - job.timestamp < oneDay);
    
    if (filtered.length !== queue.length) {
      await AsyncStorage.setItem(QUEUE_STORAGE_KEY, JSON.stringify(filtered));
      console.log(`🧹 큐 정리: ${queue.length - filtered.length}개 항목 제거됨`);
    }
  } catch (error) {
    console.error('큐 정리 실패:', error);
  }
}

/**
 * 오프라인 큐의 모든 작업을 처리
 */
export async function flushQueue(): Promise<{
  success: number;
  failed: number;
  total: number;
}> {
  try {
    const queue = await getQueue();
    if (queue.length === 0) {
      console.log('📭 오프라인 큐가 비어있습니다');
      return { success: 0, failed: 0, total: 0 };
    }
    
    console.log(`🔄 오프라인 큐 처리 시작: ${queue.length}개 작업`);
    
    const results = {
      success: 0,
      failed: 0,
      total: queue.length
    };
    
    const remaining: QueueJob[] = [];
    
    // 큐의 모든 작업을 순차적으로 처리
    for (const job of queue) {
      try {
        if (job.retryCount >= job.maxRetries) {
          console.log(`❌ 최대 재시도 횟수 초과: ${job.url}`);
          results.failed++;
          continue;
        }
        
        // API 요청 재시도
        let response;
        if (job.method === 'POST') {
          response = await api.post(job.url, job.body, { headers: job.headers });
        } else if (job.method === 'PUT') {
          response = await api.put(job.url, job.body, { headers: job.headers });
        } else {
          response = await api.delete(job.url, { headers: job.headers });
        }
        
        console.log(`✅ 큐 작업 성공: ${job.url}`);
        results.success++;
        
      } catch (error: any) {
        console.log(`❌ 큐 작업 실패: ${job.url} - ${error.message}`);
        
        // 재시도 횟수 증가
        job.retryCount++;
        
        if (job.retryCount < job.maxRetries) {
          // 아직 재시도 가능하면 큐에 유지
          remaining.push(job);
        } else {
          // 최대 재시도 횟수 초과
          results.failed++;
        }
      }
    }
    
    // 남은 작업들을 큐에 저장
    await AsyncStorage.setItem(QUEUE_STORAGE_KEY, JSON.stringify(remaining));
    
    console.log(`📊 큐 처리 완료: 성공 ${results.success}개, 실패 ${results.failed}개, 남음 ${remaining.length}개`);
    
    return results;
    
  } catch (error) {
    console.error('큐 처리 중 오류:', error);
    return { success: 0, failed: 0, total: 0 };
  }
}

/**
 * 네트워크 오류인지 확인
 */
function isNetworkError(error: any): boolean {
  if (!error.response) {
    // 네트워크 연결 실패
    return true;
  }
  
  // 특정 HTTP 상태 코드는 네트워크 오류로 간주
  const networkErrorCodes = [0, 502, 503, 504, 599];
  return networkErrorCodes.includes(error.response.status);
}

/**
 * 큐 상태 확인
 */
export async function getQueueStatus(): Promise<{
  total: number;
  pending: number;
  failed: number;
}> {
  try {
    const queue = await getQueue();
    const failed = queue.filter(job => job.retryCount >= job.maxRetries).length;
    
    return {
      total: queue.length,
      pending: queue.length - failed,
      failed
    };
  } catch (error) {
    console.error('큐 상태 확인 실패:', error);
    return { total: 0, pending: 0, failed: 0 };
  }
}

/**
 * 큐 초기화 (모든 작업 삭제)
 */
export async function clearQueue(): Promise<void> {
  try {
    await AsyncStorage.removeItem(QUEUE_STORAGE_KEY);
    console.log('🧹 오프라인 큐가 초기화되었습니다');
  } catch (error) {
    console.error('큐 초기화 실패:', error);
  }
}

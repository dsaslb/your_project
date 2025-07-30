/**
 * 성능 최적화 시스템
 * 메모리 관리, 이미지 최적화, 네트워크 최적화, 캐싱 시스템
 */

import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Image } from 'react-native';
import NetInfo from '@react-native-netinfo/netinfo';
import { InteractionManager } from 'react-native';

export interface PerformanceConfig {
  maxCacheSize: number; // MB
  maxImageCacheSize: number; // MB
  cacheExpirationTime: number; // ms
  enableImageOptimization: boolean;
  enableNetworkOptimization: boolean;
  enableMemoryOptimization: boolean;
  enableLazyLoading: boolean;
}

export interface CacheItem {
  key: string;
  data: any;
  size: number;
  timestamp: number;
  expirationTime: number;
}

export interface PerformanceMetrics {
  memoryUsage: number;
  cacheSize: number;
  imageCacheSize: number;
  networkLatency: number;
  renderTime: number;
  frameRate: number;
}

export class PerformanceOptimizer {
  private config: PerformanceConfig;
  private cache: Map<string, CacheItem> = new Map();
  private imageCache: Map<string, string> = new Map();
  private memoryMonitor: NodeJS.Timeout | null = null;
  private performanceMetrics: PerformanceMetrics;
  private isOptimizing = false;

  constructor(config: Partial<PerformanceConfig> = {}) {
    this.config = {
      maxCacheSize: 100, // 100MB
      maxImageCacheSize: 50, // 50MB
      cacheExpirationTime: 24 * 60 * 60 * 1000, // 24시간
      enableImageOptimization: true,
      enableNetworkOptimization: true,
      enableMemoryOptimization: true,
      enableLazyLoading: true,
      ...config,
    };

    this.performanceMetrics = {
      memoryUsage: 0,
      cacheSize: 0,
      imageCacheSize: 0,
      networkLatency: 0,
      renderTime: 0,
      frameRate: 60,
    };

    this.initialize();
  }

  /**
   * 초기화
   */
  private async initialize(): Promise<void> {
    await this.loadCache();
    this.startMemoryMonitoring();
    this.setupNetworkOptimization();
    console.log('성능 최적화 시스템 초기화 완료');
  }

  /**
   * 캐시 로드
   */
  private async loadCache(): Promise<void> {
    try {
      const cacheData = await AsyncStorage.getItem('performance_cache');
      if (cacheData) {
        const parsedCache = JSON.parse(cacheData);
        const now = Date.now();

        // 만료된 캐시 제거
        Object.entries(parsedCache).forEach(([key, item]: [string, any]) => {
          if (now < item.timestamp + item.expirationTime) {
            this.cache.set(key, item);
          }
        });

        this.updateCacheMetrics();
      }
    } catch (error) {
      console.error('캐시 로드 오류:', error);
    }
  }

  /**
   * 캐시 저장
   */
  private async saveCache(): Promise<void> {
    try {
      const cacheData = Object.fromEntries(this.cache);
      await AsyncStorage.setItem('performance_cache', JSON.stringify(cacheData));
    } catch (error) {
      console.error('캐시 저장 오류:', error);
    }
  }

  /**
   * 메모리 모니터링 시작
   */
  private startMemoryMonitoring(): void {
    if (!this.config.enableMemoryOptimization) return;

    this.memoryMonitor = setInterval(() => {
      this.checkMemoryUsage();
    }, 30000); // 30초마다 체크
  }

  /**
   * 메모리 사용량 체크
   */
  private checkMemoryUsage(): void {
    if (Platform.OS === 'android') {
      // Android 메모리 사용량 체크
      const used = (performance as any).memory?.usedJSHeapSize || 0;
      const total = (performance as any).memory?.totalJSHeapSize || 0;
      this.performanceMetrics.memoryUsage = used / total;
    } else {
      // iOS 메모리 사용량 체크 (간단한 추정)
      this.performanceMetrics.memoryUsage = this.cache.size / 1000; // 캐시 크기 기반 추정
    }

    // 메모리 사용량이 높으면 최적화 실행
    if (this.performanceMetrics.memoryUsage > 0.8) {
      this.optimizeMemory();
    }
  }

  /**
   * 메모리 최적화
   */
  private optimizeMemory(): void {
    if (this.isOptimizing) return;

    this.isOptimizing = true;
    console.log('메모리 최적화 시작');

    // 오래된 캐시 정리
    this.cleanExpiredCache();

    // 이미지 캐시 정리
    this.cleanImageCache();

    // 가비지 컬렉션 요청
    if (global.gc) {
      global.gc();
    }

    this.isOptimizing = false;
    console.log('메모리 최적화 완료');
  }

  /**
   * 만료된 캐시 정리
   */
  private cleanExpiredCache(): void {
    const now = Date.now();
    const expiredKeys: string[] = [];

    this.cache.forEach((item, key) => {
      if (now > item.timestamp + item.expirationTime) {
        expiredKeys.push(key);
      }
    });

    expiredKeys.forEach(key => {
      this.cache.delete(key);
    });

    if (expiredKeys.length > 0) {
      console.log(`${expiredKeys.length}개의 만료된 캐시 정리`);
      this.saveCache();
    }
  }

  /**
   * 이미지 캐시 정리
   */
  private cleanImageCache(): void {
    if (this.performanceMetrics.imageCacheSize > this.config.maxImageCacheSize) {
      const keys = Array.from(this.imageCache.keys());
      const keysToRemove = keys.slice(0, Math.floor(keys.length / 2));

      keysToRemove.forEach(key => {
        this.imageCache.delete(key);
      });

      console.log(`${keysToRemove.length}개의 이미지 캐시 정리`);
    }
  }

  /**
   * 네트워크 최적화 설정
   */
  private setupNetworkOptimization(): void {
    if (!this.config.enableNetworkOptimization) return;

    NetInfo.addEventListener((state) => {
      if (state.isConnected) {
        this.performanceMetrics.networkLatency = this.measureNetworkLatency();
      }
    });
  }

  /**
   * 네트워크 지연 시간 측정
   */
  private async measureNetworkLatency(): Promise<number> {
    const startTime = Date.now();
    
    try {
      await fetch('https://www.google.com/favicon.ico', {
        method: 'HEAD',
        cache: 'no-cache',
      });
      
      return Date.now() - startTime;
    } catch (error) {
      return 1000; // 기본값
    }
  }

  /**
   * 데이터 캐싱
   */
  async cacheData(key: string, data: any, expirationTime?: number): Promise<void> {
    try {
      const size = JSON.stringify(data).length;
      const item: CacheItem = {
        key,
        data,
        size,
        timestamp: Date.now(),
        expirationTime: expirationTime || this.config.cacheExpirationTime,
      };

      // 캐시 크기 제한 확인
      if (this.performanceMetrics.cacheSize + size > this.config.maxCacheSize * 1024 * 1024) {
        this.cleanOldestCache();
      }

      this.cache.set(key, item);
      this.updateCacheMetrics();
      await this.saveCache();

      console.log(`데이터 캐시 완료: ${key}`);
    } catch (error) {
      console.error('데이터 캐시 오류:', error);
    }
  }

  /**
   * 캐시된 데이터 가져오기
   */
  async getCachedData(key: string): Promise<any | null> {
    try {
      const item = this.cache.get(key);
      if (!item) return null;

      // 만료 확인
      if (Date.now() > item.timestamp + item.expirationTime) {
        this.cache.delete(key);
        await this.saveCache();
        return null;
      }

      return item.data;
    } catch (error) {
      console.error('캐시된 데이터 가져오기 오류:', error);
      return null;
    }
  }

  /**
   * 오래된 캐시 정리
   */
  private cleanOldestCache(): void {
    const items = Array.from(this.cache.entries());
    items.sort((a, b) => a[1].timestamp - b[1].timestamp);

    const itemsToRemove = items.slice(0, Math.floor(items.length / 4));
    itemsToRemove.forEach(([key]) => {
      this.cache.delete(key);
    });

    console.log(`${itemsToRemove.length}개의 오래된 캐시 정리`);
  }

  /**
   * 이미지 최적화
   */
  optimizeImage(uri: string, width?: number, height?: number): string {
    if (!this.config.enableImageOptimization) return uri;

    // 이미 캐시된 이미지인지 확인
    const cacheKey = `${uri}_${width}_${height}`;
    if (this.imageCache.has(cacheKey)) {
      return this.imageCache.get(cacheKey)!;
    }

    // 이미지 크기 최적화
    let optimizedUri = uri;
    
    if (width && height) {
      // URL 파라미터로 크기 지정 (서버에서 지원하는 경우)
      const separator = uri.includes('?') ? '&' : '?';
      optimizedUri = `${uri}${separator}w=${width}&h=${height}`;
    }

    // 이미지 캐시에 저장
    this.imageCache.set(cacheKey, optimizedUri);
    this.updateCacheMetrics();

    return optimizedUri;
  }

  /**
   * 지연 로딩
   */
  lazyLoad(callback: () => void, delay: number = 100): void {
    if (!this.config.enableLazyLoading) {
      callback();
      return;
    }

    InteractionManager.runAfterInteractions(() => {
      setTimeout(callback, delay);
    });
  }

  /**
   * 캐시 메트릭 업데이트
   */
  private updateCacheMetrics(): void {
    let totalSize = 0;
    this.cache.forEach(item => {
      totalSize += item.size;
    });

    this.performanceMetrics.cacheSize = totalSize;
    this.performanceMetrics.imageCacheSize = this.imageCache.size * 1024; // 추정치
  }

  /**
   * 성능 메트릭 가져오기
   */
  getPerformanceMetrics(): PerformanceMetrics {
    return { ...this.performanceMetrics };
  }

  /**
   * 캐시 통계
   */
  getCacheStats(): {
    totalItems: number;
    totalSize: number;
    imageCacheItems: number;
    imageCacheSize: number;
  } {
    return {
      totalItems: this.cache.size,
      totalSize: this.performanceMetrics.cacheSize,
      imageCacheItems: this.imageCache.size,
      imageCacheSize: this.performanceMetrics.imageCacheSize,
    };
  }

  /**
   * 캐시 초기화
   */
  async clearCache(): Promise<void> {
    try {
      this.cache.clear();
      this.imageCache.clear();
      this.updateCacheMetrics();
      await AsyncStorage.removeItem('performance_cache');
      console.log('캐시 초기화 완료');
    } catch (error) {
      console.error('캐시 초기화 오류:', error);
    }
  }

  /**
   * 특정 키의 캐시 제거
   */
  removeCache(key: string): void {
    this.cache.delete(key);
    this.updateCacheMetrics();
    this.saveCache();
  }

  /**
   * 이미지 프리로딩
   */
  preloadImages(uris: string[]): Promise<void[]> {
    return Promise.all(
      uris.map(uri => {
        return new Promise<void>((resolve) => {
          Image.prefetch(uri)
            .then(() => {
              console.log(`이미지 프리로드 완료: ${uri}`);
              resolve();
            })
            .catch(() => {
              console.warn(`이미지 프리로드 실패: ${uri}`);
              resolve();
            });
        });
      })
    );
  }

  /**
   * 네트워크 상태 확인
   */
  async getNetworkInfo(): Promise<{
    isConnected: boolean;
    type: string;
    isWifi: boolean;
    isCellular: boolean;
  }> {
    const state = await NetInfo.fetch();
    return {
      isConnected: state.isConnected ?? false,
      type: state.type,
      isWifi: state.type === 'wifi',
      isCellular: state.type === 'cellular',
    };
  }

  /**
   * 성능 최적화 권장사항
   */
  getOptimizationRecommendations(): string[] {
    const recommendations: string[] = [];

    if (this.performanceMetrics.memoryUsage > 0.8) {
      recommendations.push('메모리 사용량이 높습니다. 불필요한 데이터를 정리하세요.');
    }

    if (this.performanceMetrics.cacheSize > this.config.maxCacheSize * 1024 * 1024 * 0.8) {
      recommendations.push('캐시 크기가 제한에 가깝습니다. 오래된 캐시를 정리하세요.');
    }

    if (this.performanceMetrics.networkLatency > 1000) {
      recommendations.push('네트워크 지연이 높습니다. 네트워크 연결을 확인하세요.');
    }

    if (this.performanceMetrics.frameRate < 30) {
      recommendations.push('프레임 레이트가 낮습니다. 렌더링 성능을 최적화하세요.');
    }

    return recommendations;
  }

  /**
   * 서비스 정리
   */
  destroy(): void {
    if (this.memoryMonitor) {
      clearInterval(this.memoryMonitor);
    }
    this.cache.clear();
    this.imageCache.clear();
    console.log('성능 최적화 시스템 정리 완료');
  }
}

// 싱글톤 인스턴스
export const performanceOptimizer = new PerformanceOptimizer();

// 사용 예시
export const usePerformanceOptimizer = () => {
  return {
    cacheData: performanceOptimizer.cacheData.bind(performanceOptimizer),
    getCachedData: performanceOptimizer.getCachedData.bind(performanceOptimizer),
    optimizeImage: performanceOptimizer.optimizeImage.bind(performanceOptimizer),
    lazyLoad: performanceOptimizer.lazyLoad.bind(performanceOptimizer),
    preloadImages: performanceOptimizer.preloadImages.bind(performanceOptimizer),
    getPerformanceMetrics: performanceOptimizer.getPerformanceMetrics.bind(performanceOptimizer),
    getCacheStats: performanceOptimizer.getCacheStats.bind(performanceOptimizer),
    clearCache: performanceOptimizer.clearCache.bind(performanceOptimizer),
    getNetworkInfo: performanceOptimizer.getNetworkInfo.bind(performanceOptimizer),
    getOptimizationRecommendations: performanceOptimizer.getOptimizationRecommendations.bind(performanceOptimizer),
  };
}; 
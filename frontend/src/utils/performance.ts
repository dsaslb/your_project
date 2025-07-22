/**
 * 프론트엔드 성능 최적화 유틸리티
 * 메모리 관리, 렌더링 최적화, 캐싱 기능 제공
 */

interface PerformanceMetrics {
  timestamp: number;
  memoryUsage: number;
  renderTime: number;
  bundleSize: number;
  cacheHitRate: number;
}

interface CacheItem<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

class PerformanceOptimizer {
  private static instance: PerformanceOptimizer;
  private metrics: PerformanceMetrics[] = [];
  private cache = new Map<string, CacheItem<any>>();
  private renderTimes: number[] = [];
  private memoryThreshold = 50 * 1024 * 1024; // 50MB
  private maxMetricsHistory = 1000;

  private constructor() {
    this.startMonitoring();
  }

  static getInstance(): PerformanceOptimizer {
    if (!PerformanceOptimizer.instance) {
      PerformanceOptimizer.instance = new PerformanceOptimizer();
    }
    return PerformanceOptimizer.instance;
  }

  /**
   * 성능 모니터링 시작
   */
  private startMonitoring(): void {
    // 메모리 사용량 모니터링
    if ('memory' in performance) {
      setInterval(() => {
        this.recordMemoryUsage();
      }, 30000); // 30초마다
    }

    // 페이지 로드 시간 모니터링
    window.addEventListener('load', () => {
      this.recordPageLoadTime();
    });

    // 렌더링 성능 모니터링
    this.setupRenderMonitoring();
  }

  /**
   * 메모리 사용량 기록
   */
  private recordMemoryUsage(): void {
    if ('memory' in performance) {
      const memory = (performance as any).memory;
      const usedMemory = memory.usedJSHeapSize;
      
      if (usedMemory > this.memoryThreshold) {
        console.warn(`높은 메모리 사용량: ${(usedMemory / 1024 / 1024).toFixed(2)}MB`);
        this.triggerMemoryCleanup();
      }

      this.metrics.push({
        timestamp: Date.now(),
        memoryUsage: usedMemory,
        renderTime: 0,
        bundleSize: 0,
        cacheHitRate: this.calculateCacheHitRate()
      });

      // 메트릭 히스토리 크기 제한
      if (this.metrics.length > this.maxMetricsHistory) {
        this.metrics.shift();
      }
    }
  }

  /**
   * 페이지 로드 시간 기록
   */
  private recordPageLoadTime(): void {
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    if (navigation) {
      const loadTime = navigation.loadEventEnd - navigation.loadEventStart;
      console.log(`페이지 로드 시간: ${loadTime.toFixed(2)}ms`);
    }
  }

  /**
   * 렌더링 성능 모니터링 설정
   */
  private setupRenderMonitoring(): void {
    let frameCount = 0;
    let lastTime = performance.now();

    const measureFPS = () => {
      frameCount++;
      const currentTime = performance.now();
      
      if (currentTime - lastTime >= 1000) {
        const fps = Math.round((frameCount * 1000) / (currentTime - lastTime));
        if (fps < 30) {
          console.warn(`낮은 FPS 감지: ${fps}`);
        }
        frameCount = 0;
        lastTime = currentTime;
      }
      
      requestAnimationFrame(measureFPS);
    };

    requestAnimationFrame(measureFPS);
  }

  /**
   * 메모리 정리 트리거
   */
  private triggerMemoryCleanup(): void {
    // 가비지 컬렉션 요청 (브라우저가 지원하는 경우)
    if ('gc' in window) {
      (window as any).gc();
    }

    // 캐시 정리
    this.clearExpiredCache();

    // 이벤트 리스너 정리
    this.cleanupEventListeners();
  }

  /**
   * 만료된 캐시 정리
   */
  private clearExpiredCache(): void {
    const now = Date.now();
    for (const [key, item] of this.cache.entries()) {
      if (now - item.timestamp > item.ttl) {
        this.cache.delete(key);
      }
    }
  }

  /**
   * 이벤트 리스너 정리
   */
  private cleanupEventListeners(): void {
    // 전역 이벤트 리스너 정리 로직
    // 실제 구현에서는 컴포넌트별로 관리
  }

  /**
   * 캐시 히트율 계산
   */
  private calculateCacheHitRate(): number {
    // 실제 구현에서는 캐시 히트/미스 통계를 추적
    return 0.8; // 예시 값
  }

  /**
   * 데이터 캐싱
   */
  cacheData<T>(key: string, data: T, ttl: number = 300000): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl
    });
  }

  /**
   * 캐시된 데이터 조회
   */
  getCachedData<T>(key: string): T | null {
    const item = this.cache.get(key);
    if (!item) return null;

    const now = Date.now();
    if (now - item.timestamp > item.ttl) {
      this.cache.delete(key);
      return null;
    }

    return item.data as T;
  }

  /**
   * 렌더링 시간 측정
   */
  measureRenderTime(componentName: string, renderFn: () => void): void {
    const startTime = performance.now();
    renderFn();
    const endTime = performance.now();
    const renderTime = endTime - startTime;

    this.renderTimes.push(renderTime);
    if (this.renderTimes.length > 100) {
      this.renderTimes.shift();
    }

    if (renderTime > 16) { // 60fps 기준
      console.warn(`느린 렌더링 감지 (${componentName}): ${renderTime.toFixed(2)}ms`);
    }
  }

  /**
   * 성능 메트릭 반환
   */
  getMetrics(): PerformanceMetrics[] {
    return [...this.metrics];
  }

  /**
   * 평균 렌더링 시간
   */
  getAverageRenderTime(): number {
    if (this.renderTimes.length === 0) return 0;
    return this.renderTimes.reduce((a, b) => a + b, 0) / this.renderTimes.length;
  }

  /**
   * 메모리 사용량
   */
  getMemoryUsage(): number {
    if ('memory' in performance) {
      return (performance as any).memory.usedJSHeapSize;
    }
    return 0;
  }

  /**
   * 성능 리포트 생성
   */
  generateReport(): any {
    const currentMemory = this.getMemoryUsage();
    const avgRenderTime = this.getAverageRenderTime();
    const cacheSize = this.cache.size;

    return {
      timestamp: new Date().toISOString(),
      memoryUsage: {
        current: currentMemory,
        formatted: `${(currentMemory / 1024 / 1024).toFixed(2)}MB`,
        threshold: `${(this.memoryThreshold / 1024 / 1024).toFixed(2)}MB`
      },
      renderPerformance: {
        averageTime: avgRenderTime,
        formatted: `${avgRenderTime.toFixed(2)}ms`,
        isOptimal: avgRenderTime < 16
      },
      cache: {
        size: cacheSize,
        hitRate: this.calculateCacheHitRate()
      },
      status: this.getPerformanceStatus(currentMemory, avgRenderTime)
    };
  }

  /**
   * 성능 상태 판단
   */
  private getPerformanceStatus(memoryUsage: number, renderTime: number): string {
    if (memoryUsage > this.memoryThreshold || renderTime > 50) {
      return 'critical';
    } else if (memoryUsage > this.memoryThreshold * 0.8 || renderTime > 16) {
      return 'warning';
    } else {
      return 'optimal';
    }
  }
}

/**
 * React 컴포넌트 렌더링 최적화 훅
 */
export const usePerformanceOptimization = () => {
  const optimizer = PerformanceOptimizer.getInstance();

  const measureRender = (componentName: string, renderFn: () => void) => {
    optimizer.measureRenderTime(componentName, renderFn);
  };

  const cacheData = <T>(key: string, data: T, ttl?: number) => {
    optimizer.cacheData(key, data, ttl);
  };

  const getCachedData = <T>(key: string): T | null => {
    return optimizer.getCachedData<T>(key);
  };

  const getPerformanceReport = () => {
    return optimizer.generateReport();
  };

  return {
    measureRender,
    cacheData,
    getCachedData,
    getPerformanceReport
  };
};

/**
 * 이미지 지연 로딩 훅
 */
export const useLazyImage = (src: string, placeholder?: string) => {
  const [imageSrc, setImageSrc] = React.useState(placeholder || '');
  const [isLoaded, setIsLoaded] = React.useState(false);

  React.useEffect(() => {
    const img = new Image();
    img.src = src;
    img.onload = () => {
      setImageSrc(src);
      setIsLoaded(true);
    };
  }, [src]);

  return { imageSrc, isLoaded };
};

/**
 * 디바운스 훅
 */
export const useDebounce = <T>(value: T, delay: number): T => {
  const [debouncedValue, setDebouncedValue] = React.useState<T>(value);

  React.useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

/**
 * 스로틀 훅
 */
export const useThrottle = <T>(value: T, delay: number): T => {
  const [throttledValue, setThrottledValue] = React.useState<T>(value);
  const lastRun = React.useRef(Date.now());

  React.useEffect(() => {
    const handler = setTimeout(() => {
      if (Date.now() - lastRun.current >= delay) {
        setThrottledValue(value);
        lastRun.current = Date.now();
      }
    }, delay - (Date.now() - lastRun.current));

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return throttledValue;
};

export default PerformanceOptimizer.getInstance(); 
import { useCallback, useMemo, useRef, useEffect, useState } from 'react';
import { PerformanceOptimizer } from '../utils/performance';

interface PerformanceMetrics {
  renderTime: number;
  memoryUsage?: number;
  componentName: string;
  timestamp: number;
}

interface PerformanceConfig {
  enableMonitoring: boolean;
  logSlowRenders: boolean;
  slowRenderThreshold: number;
  maxMetricsHistory: number;
}

class PerformanceMonitor {
  private metrics: PerformanceMetrics[] = [];
  private config: PerformanceConfig;
  private observers: Set<(metrics: PerformanceMetrics[]) => void> = new Set();

  constructor(config: Partial<PerformanceConfig> = {}) {
    this.config = {
      enableMonitoring: true,
      logSlowRenders: true,
      slowRenderThreshold: 16, // 16ms = 60fps
      maxMetricsHistory: 1000,
      ...config
    };
  }

  recordRender(componentName: string, renderTime: number) {
    if (!this.config.enableMonitoring) return;

    const metric: PerformanceMetrics = {
      componentName,
      renderTime,
      timestamp: Date.now(),
      memoryUsage: this.getMemoryUsage()
    };

    this.metrics.push(metric);

    // 최대 기록 수 제한
    if (this.metrics.length > this.config.maxMetricsHistory) {
      this.metrics.shift();
    }

    // 느린 렌더링 로그
    if (this.config.logSlowRenders && renderTime > this.config.slowRenderThreshold) {
      console.warn(`느린 렌더링 감지: ${componentName} - ${renderTime.toFixed(2)}ms`);
    }

    // 옵저버들에게 알림
    this.observers.forEach(observer => observer(this.metrics));
  }

  private getMemoryUsage(): number | undefined {
    if ('memory' in performance) {
      return (performance as any).memory.usedJSHeapSize;
    }
    return undefined;
  }

  getMetrics(componentName?: string): PerformanceMetrics[] {
    if (componentName) {
      return this.metrics.filter(m => m.componentName === componentName);
    }
    return [...this.metrics];
  }

  getAverageRenderTime(componentName?: string): number {
    const metrics = this.getMetrics(componentName);
    if (metrics.length === 0) return 0;
    
    const totalTime = metrics.reduce((sum, m) => sum + m.renderTime, 0);
    return totalTime / metrics.length;
  }

  getSlowRenders(threshold?: number): PerformanceMetrics[] {
    const t = threshold || this.config.slowRenderThreshold;
    return this.metrics.filter(m => m.renderTime > t);
  }

  subscribe(callback: (metrics: PerformanceMetrics[]) => void): () => void {
    this.observers.add(callback);
    return () => this.observers.delete(callback);
  }

  clear() {
    this.metrics = [];
    this.observers.forEach(observer => observer(this.metrics));
  }

  updateConfig(newConfig: Partial<PerformanceConfig>) {
    this.config = { ...this.config, ...newConfig };
  }
}

// 전역 성능 모니터 인스턴스
const performanceMonitor = new PerformanceMonitor();

export const usePerformanceMonitor = (componentName: string) => {
  const renderStartTime = useRef<number>(0);
  const [metrics, setMetrics] = useState<PerformanceMetrics[]>([]);

  useEffect(() => {
    const unsubscribe = performanceMonitor.subscribe(setMetrics);
    return unsubscribe;
  }, []);

  const startRender = useCallback(() => {
    renderStartTime.current = performance.now();
  }, []);

  const endRender = useCallback(() => {
    const renderTime = performance.now() - renderStartTime.current;
    performanceMonitor.recordRender(componentName, renderTime);
  }, [componentName]);

  return {
    startRender,
    endRender,
    metrics: metrics.filter(m => m.componentName === componentName),
    allMetrics: metrics
  };
};

export const useRenderPerformance = (componentName: string) => {
  const renderStartTime = useRef<number>(0);

  useEffect(() => {
    renderStartTime.current = performance.now();
    
    return () => {
      const renderTime = performance.now() - renderStartTime.current;
      performanceMonitor.recordRender(componentName, renderTime);
    };
  });
};

// 디바운스 훅
export function useDebounce<T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): T {
  const timeoutRef = useRef<NodeJS.Timeout>();

  return useCallback(
    ((...args: Parameters<T>) => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      timeoutRef.current = setTimeout(() => callback(...args), delay);
    }) as T,
    [callback, delay]
  );
}

// 쓰로틀 훅
export function useThrottle<T extends (...args: any[]) => any>(
  callback: T,
  limit: number
): T {
  const inThrottleRef = useRef(false);

  return useCallback(
    ((...args: Parameters<T>) => {
      if (!inThrottleRef.current) {
        callback(...args);
        inThrottleRef.current = true;
        setTimeout(() => (inThrottleRef.current = false), limit);
      }
    }) as T,
    [callback, limit]
  );
}

// 무한 스크롤 훅
export function useInfiniteScroll(
  callback: () => void,
  options: {
    threshold?: number;
    rootMargin?: string;
    enabled?: boolean;
  } = {}
) {
  const { threshold = 0.1, rootMargin = '100px', enabled = true } = options;
  const observerRef = useRef<IntersectionObserver | null>(null);
  const targetRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!enabled) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            callback();
          }
        });
      },
      { threshold, rootMargin }
    );

    observerRef.current = observer;

    if (targetRef.current) {
      observer.observe(targetRef.current);
    }

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [callback, threshold, rootMargin, enabled]);

  return targetRef;
}

// 메모리 사용량 모니터링 훅
export function useMemoryMonitor() {
  const [memoryInfo, setMemoryInfo] = useState<any>(null);

  useEffect(() => {
    if ('memory' in performance) {
      const updateMemoryInfo = () => {
        setMemoryInfo((performance as any).memory);
      };

      updateMemoryInfo();
      const interval = setInterval(updateMemoryInfo, 5000);

      return () => clearInterval(interval);
    }
  }, []);

  return memoryInfo;
}

// 네트워크 상태 모니터링 훅
export function useNetworkStatus() {
  const [isOnline, setIsOnline] = useState(true);
  const [connection, setConnection] = useState<any>(null);

  useEffect(() => {
    const updateNetworkStatus = () => {
      setIsOnline(navigator.onLine);
      if ('connection' in navigator) {
        setConnection((navigator as any).connection);
      }
    };

    updateNetworkStatus();

    window.addEventListener('online', updateNetworkStatus);
    window.addEventListener('offline', updateNetworkStatus);

    return () => {
      window.removeEventListener('online', updateNetworkStatus);
      window.removeEventListener('offline', updateNetworkStatus);
    };
  }, []);

  return { isOnline, connection };
}

// 성능 최적화된 리스트 훅
export function useOptimizedList<T extends Record<string, any>>(
  items: T[],
  options: {
    pageSize?: number;
    searchTerm?: string;
    sortBy?: keyof T;
    sortDirection?: 'asc' | 'desc';
  } = {}
) {
  const { pageSize = 20, searchTerm = '', sortBy, sortDirection = 'asc' } = options;

  const filteredAndSortedItems = useMemo(() => {
    let result = [...items];

    // 검색 필터링
    if (searchTerm) {
      result = result.filter((item) =>
        Object.values(item).some((value) =>
          String(value).toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }

    // 정렬
    if (sortBy) {
      result.sort((a, b) => {
        const aValue = a[sortBy];
        const bValue = b[sortBy];

        if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
        if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
        return 0;
      });
    }

    return result;
  }, [items, searchTerm, sortBy, sortDirection]);

  const paginatedItems = useMemo(() => {
    return filteredAndSortedItems.slice(0, pageSize);
  }, [filteredAndSortedItems, pageSize]);

  return {
    items: paginatedItems,
    totalItems: filteredAndSortedItems.length,
    hasMore: filteredAndSortedItems.length > pageSize,
  };
}

// 성능 메트릭 수집 훅
export function usePerformanceMetrics() {
  const [metrics, setMetrics] = useState<any>(null);

  useEffect(() => {
    const performanceOptimizer = new PerformanceOptimizer();
    
    const updateMetrics = () => {
      const report = performanceOptimizer.getPerformanceReport();
      setMetrics(report);
    };

    updateMetrics();
    const interval = setInterval(updateMetrics, 10000); // 10초마다 업데이트

    return () => clearInterval(interval);
  }, []);

  return metrics;
}

// 이미지 프리로딩 훅
export function useImagePreload(imageUrls: string[]) {
  const [loadedImages, setLoadedImages] = useState<Set<string>>(new Set());

  useEffect(() => {
    const preloadImages = async () => {
      const promises = imageUrls.map((url) => {
        return new Promise<string>((resolve, reject) => {
          const img = new Image();
          img.onload = () => resolve(url);
          img.onerror = () => reject(url);
          img.src = url;
        });
      });

      try {
        const loadedUrls = await Promise.allSettled(promises);
        const successfulUrls = loadedUrls
          .filter((result) => result.status === 'fulfilled')
          .map((result) => (result as PromiseFulfilledResult<string>).value);
        
        setLoadedImages(new Set(successfulUrls));
      } catch (error) {
        console.warn('이미지 프리로딩 중 오류:', error);
      }
    };

    if (imageUrls.length > 0) {
      preloadImages();
    }
  }, [imageUrls]);

  return loadedImages;
}

export const useIntersectionObserver = (
  callback: IntersectionObserverCallback,
  options: IntersectionObserverInit = {}
) => {
  const observerRef = useRef<IntersectionObserver | null>(null);

  useEffect(() => {
    observerRef.current = new IntersectionObserver(callback, options);
    
    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [callback, options]);

  const observe = useCallback((element: Element) => {
    if (observerRef.current) {
      observerRef.current.observe(element);
    }
  }, []);

  const unobserve = useCallback((element: Element) => {
    if (observerRef.current) {
      observerRef.current.unobserve(element);
    }
  }, []);

  return { observe, unobserve };
};

export const useVirtualization = <T>(
  items: T[],
  itemHeight: number,
  containerHeight: number,
  overscan: number = 5
) => {
  const [scrollTop, setScrollTop] = useState(0);

  const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
  const endIndex = Math.min(
    items.length - 1,
    Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
  );

  const visibleItems = items.slice(startIndex, endIndex + 1);
  const totalHeight = items.length * itemHeight;
  const offsetY = startIndex * itemHeight;

  return {
    visibleItems,
    totalHeight,
    offsetY,
    setScrollTop,
    startIndex,
    endIndex
  };
};

export const useLocalStorage = <T>(key: string, initialValue: T) => {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  const setValue = useCallback((value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error);
    }
  }, [key, storedValue]);

  return [storedValue, setValue] as const;
};

export const useSessionStorage = <T>(key: string, initialValue: T) => {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.sessionStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error reading sessionStorage key "${key}":`, error);
      return initialValue;
    }
  });

  const setValue = useCallback((value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.sessionStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(`Error setting sessionStorage key "${key}":`, error);
    }
  }, [key, storedValue]);

  return [storedValue, setValue] as const;
};

// 성능 모니터링 유틸리티 함수들
export const getPerformanceMetrics = () => {
  return {
    metrics: performanceMonitor.getMetrics(),
    averageRenderTime: performanceMonitor.getAverageRenderTime(),
    slowRenders: performanceMonitor.getSlowRenders()
  };
};

export const clearPerformanceMetrics = () => {
  performanceMonitor.clear();
};

export const updatePerformanceConfig = (config: Partial<PerformanceConfig>) => {
  performanceMonitor.updateConfig(config);
};

// 개발 환경에서만 성능 모니터링 활성화
if (process.env.NODE_ENV === 'development') {
  performanceMonitor.updateConfig({
    enableMonitoring: true,
    logSlowRenders: true
  });
} 
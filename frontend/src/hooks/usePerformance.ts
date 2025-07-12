import { useCallback, useRef, useEffect, useState } from 'react';

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

export const useDebounce = <T>(value: T, delay: number): T => {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

export const useThrottle = <T>(value: T, delay: number): T => {
  const [throttledValue, setThrottledValue] = useState<T>(value);
  const lastRun = useRef<number>(Date.now());

  useEffect(() => {
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

export const useMemoizedCallback = <T extends (...args: any[]) => any>(
  callback: T,
  deps: React.DependencyList
): T => {
  return useCallback(callback, deps);
};

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
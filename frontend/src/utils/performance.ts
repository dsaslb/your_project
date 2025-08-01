import * as React from 'react';
/**
 * 프론트엔드 성능 최적화 유틸리티
 * 메모리 관리, 렌더링 최적화, 캐싱 기능 제공
 */

// 성능 모니터링 유틸리티

interface PerformanceMetrics {
  pageLoadTime: number;
  firstContentfulPaint: number;
  largestContentfulPaint: number;
  cumulativeLayoutShift: number;
  firstInputDelay: number;
  timeToInteractive: number;
}

interface PerformanceObserver {
  observe: (options: any) => void;
  disconnect: () => void;
}

// 성능 메트릭 수집
export class PerformanceMonitor {
  private metrics: PerformanceMetrics = {
    pageLoadTime: 0,
    firstContentfulPaint: 0,
    largestContentfulPaint: 0,
    cumulativeLayoutShift: 0,
    firstInputDelay: 0,
    timeToInteractive: 0,
  };

  private observers: PerformanceObserver[] = [];

  constructor() {
    this.initializeObservers();
  }

  private initializeObservers() {
    // First Contentful Paint
    if ('PerformanceObserver' in window) {
      try {
        const fcpObserver = new (window as any).PerformanceObserver((list: any) => {
          const entries = list.getEntries();
          const fcpEntry = entries.find((entry: any) => entry.name === 'first-contentful-paint');
          if (fcpEntry) {
            this.metrics.firstContentfulPaint = fcpEntry.startTime;
            this.logMetric('FCP', fcpEntry.startTime);
          }
        });
        fcpObserver.observe({ entryTypes: ['paint'] });
        this.observers.push(fcpObserver);
      } catch (error) {
        console.warn('FCP observer failed:', error);
      }

      // Largest Contentful Paint
      try {
        const lcpObserver = new (window as any).PerformanceObserver((list: any) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          if (lastEntry) {
            this.metrics.largestContentfulPaint = lastEntry.startTime;
            this.logMetric('LCP', lastEntry.startTime);
          }
        });
        lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
        this.observers.push(lcpObserver);
      } catch (error) {
        console.warn('LCP observer failed:', error);
      }

      // Cumulative Layout Shift
      try {
        const clsObserver = new (window as any).PerformanceObserver((list: any) => {
          let clsValue = 0;
          for (const entry of list.getEntries()) {
            if (!(entry as any).hadRecentInput) {
              clsValue += (entry as any).value;
            }
          }
          this.metrics.cumulativeLayoutShift = clsValue;
          this.logMetric('CLS', clsValue);
        });
        clsObserver.observe({ entryTypes: ['layout-shift'] });
        this.observers.push(clsObserver);
      } catch (error) {
        console.warn('CLS observer failed:', error);
      }

      // First Input Delay
      try {
        const fidObserver = new (window as any).PerformanceObserver((list: any) => {
          const entries = list.getEntries();
          for (const entry of entries) {
            this.metrics.firstInputDelay = (entry as any).processingStart - (entry as any).startTime;
            this.logMetric('FID', this.metrics.firstInputDelay);
            break; // 첫 번째 입력만 기록
          }
        });
        fidObserver.observe({ entryTypes: ['first-input'] });
        this.observers.push(fidObserver);
      } catch (error) {
        console.warn('FID observer failed:', error);
      }
    }

    // 페이지 로드 시간
    window.addEventListener('load', () => {
      const navigation = performance.getEntriesByType('navigation')[0] as any;
      if (navigation) {
        this.metrics.pageLoadTime = navigation.loadEventEnd - navigation.loadEventStart;
        this.logMetric('Page Load Time', this.metrics.pageLoadTime);
      }
    });
  }

  private logMetric(name: string, value: number) {
    console.log(`Performance Metric - ${name}: ${value.toFixed(2)}ms`);
    
    // 성능 임계값 체크
    this.checkPerformanceThreshold(name, value);
    
    // 분석 도구로 전송 (예: Google Analytics)
    this.sendToAnalytics(name, value);
  }

  private checkPerformanceThreshold(name: string, value: number) {
    const thresholds: Record<string, { good: number; poor: number }> = {
      'FCP': { good: 1800, poor: 3000 },
      'LCP': { good: 2500, poor: 4000 },
      'CLS': { good: 0.1, poor: 0.25 },
      'FID': { good: 100, poor: 300 },
    };

    const threshold = thresholds[name];
    if (threshold) {
      if (value <= threshold.good) {
        console.log(`✅ ${name} is good (${value.toFixed(2)}ms)`);
      } else if (value <= threshold.poor) {
        console.warn(`⚠️ ${name} needs improvement (${value.toFixed(2)}ms)`);
      } else {
        console.error(`❌ ${name} is poor (${value.toFixed(2)}ms)`);
      }
    }
  }

  private sendToAnalytics(name: string, value: number) {
    // Google Analytics 4 이벤트 전송
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'performance_metric', {
        metric_name: name,
        metric_value: value,
        page_location: window.location.href,
      });
    }
  }

  public getMetrics(): PerformanceMetrics {
    return { ...this.metrics };
  }

  public disconnect() {
    this.observers.forEach(observer => observer.disconnect());
  }
}

// 메모리 사용량 모니터링
export class MemoryMonitor {
  private interval: NodeJS.Timeout | null = null;

  startMonitoring(intervalMs: number = 5000) {
    if (typeof window !== 'undefined' && 'memory' in performance) {
      this.interval = setInterval(() => {
        const memory = (performance as any).memory;
        console.log('Memory Usage:', {
          used: `${(memory.usedJSHeapSize / 1048576).toFixed(2)} MB`,
          total: `${(memory.totalJSHeapSize / 1048576).toFixed(2)} MB`,
          limit: `${(memory.jsHeapSizeLimit / 1048576).toFixed(2)} MB`,
        });
      }, intervalMs);
    }
  }

  stopMonitoring() {
    if (this.interval) {
      clearInterval(this.interval);
      this.interval = null;
    }
  }
}

// 네트워크 성능 모니터링
export class NetworkMonitor {
  private observer: PerformanceObserver | null = null;

  startMonitoring() {
    if ('PerformanceObserver' in window) {
      try {
        this.observer = new (window as any).PerformanceObserver((list: any) => {
          const entries = list.getEntries();
          entries.forEach((entry: any) => {
            if (entry.entryType === 'resource') {
              this.logNetworkMetric(entry);
            }
          });
        });
        this.observer?.observe({ entryTypes: ['resource'] });
      } catch (error) {
        console.warn('Network observer failed:', error);
      }
    }
  }

  private logNetworkMetric(entry: any) {
    const duration = entry.duration;
    const size = entry.transferSize || 0;
    
    if (duration > 1000) { // 1초 이상 걸린 요청
      console.warn(`Slow network request: ${entry.name} (${duration.toFixed(2)}ms, ${size} bytes)`);
    }
  }

  stopMonitoring() {
    if (this.observer) {
      this.observer.disconnect();
      this.observer = null;
    }
  }
}

// 성능 최적화 유틸리티
export class PerformanceOptimizer {
  // 이미지 지연 로딩
  static enableLazyLoading() {
    if (typeof window !== 'undefined') {
      const images = document.querySelectorAll('img[data-src]');
      const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const img = entry.target as HTMLImageElement;
            img.src = img.dataset.src || '';
            img.classList.remove('lazy');
            imageObserver.unobserve(img);
          }
        });
      });

      images.forEach(img => imageObserver.observe(img));
    }
  }

  // 스크롤 성능 최적화
  static optimizeScroll() {
    if (typeof window !== 'undefined') {
      let ticking = false;
      
      const updateScroll = () => {
        // 스크롤 관련 업데이트 로직
        ticking = false;
      };

      const requestTick = () => {
        if (!ticking) {
          requestAnimationFrame(updateScroll);
          ticking = true;
        }
      };

      window.addEventListener('scroll', requestTick, { passive: true });
    }
  }

  // 디바운스 함수
  static debounce<T extends (...args: any[]) => any>(
    func: T,
    wait: number
  ): (...args: Parameters<T>) => void {
    let timeout: NodeJS.Timeout;
    return (...args: Parameters<T>) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => func(...args), wait);
    };
  }

  // 쓰로틀 함수
  static throttle<T extends (...args: any[]) => any>(
    func: T,
    limit: number
  ): (...args: Parameters<T>) => void {
    let inThrottle: boolean;
    return (...args: Parameters<T>) => {
      if (!inThrottle) {
        func(...args);
        inThrottle = true;
        setTimeout(() => (inThrottle = false), limit);
      }
    };
  }

  // 가상화된 리스트 최적화
  static createVirtualizedList<T>(
    items: T[],
    itemHeight: number,
    containerHeight: number,
    renderItem: (item: T, index: number) => React.ReactNode
  ) {
    const visibleCount = Math.ceil(containerHeight / itemHeight);
    const startIndex = Math.floor(window.scrollY / itemHeight);
    const endIndex = Math.min(startIndex + visibleCount, items.length);

    return {
      visibleItems: items.slice(startIndex, endIndex),
      startIndex,
      endIndex,
      totalHeight: items.length * itemHeight,
      offsetY: startIndex * itemHeight,
    };
  }

  // 성능 리포트 생성
  getPerformanceReport() {
    if (typeof window === 'undefined') {
      return { status: 'unknown', score: 0, message: '서버 사이드에서는 성능 측정이 불가능합니다.' };
    }

    const metrics = performanceMonitor?.getMetrics() || {
      pageLoadTime: 0,
      firstContentfulPaint: 0,
      largestContentfulPaint: 0,
      cumulativeLayoutShift: 0,
      firstInputDelay: 0,
      timeToInteractive: 0,
    };

    // Core Web Vitals 기준
    const fcpScore = metrics.firstContentfulPaint < 1800 ? 100 : 
                    metrics.firstContentfulPaint < 3000 ? 75 : 
                    metrics.firstContentfulPaint < 5000 ? 50 : 25;
    
    const lcpScore = metrics.largestContentfulPaint < 2500 ? 100 : 
                    metrics.largestContentfulPaint < 4000 ? 75 : 
                    metrics.largestContentfulPaint < 6000 ? 50 : 25;
    
    const clsScore = metrics.cumulativeLayoutShift < 0.1 ? 100 : 
                    metrics.cumulativeLayoutShift < 0.25 ? 75 : 
                    metrics.cumulativeLayoutShift < 0.5 ? 50 : 25;
    
    const fidScore = metrics.firstInputDelay < 100 ? 100 : 
                    metrics.firstInputDelay < 300 ? 75 : 
                    metrics.firstInputDelay < 500 ? 50 : 25;

    const totalScore = Math.round((fcpScore + lcpScore + clsScore + fidScore) / 4);
    
    let status: 'excellent' | 'good' | 'needs-improvement' | 'poor';
    if (totalScore >= 90) status = 'excellent';
    else if (totalScore >= 70) status = 'good';
    else if (totalScore >= 50) status = 'needs-improvement';
    else status = 'poor';

    return {
      status,
      score: totalScore,
      metrics: {
        fcp: { value: metrics.firstContentfulPaint, score: fcpScore },
        lcp: { value: metrics.largestContentfulPaint, score: lcpScore },
        cls: { value: metrics.cumulativeLayoutShift, score: clsScore },
        fid: { value: metrics.firstInputDelay, score: fidScore },
      },
      recommendations: this.getRecommendations(metrics),
      timestamp: new Date().toISOString(),
    };
  }

  // 성능 개선 권장사항
  private getRecommendations(metrics: PerformanceMetrics): string[] {
    const recommendations: string[] = [];

    if (metrics.firstContentfulPaint > 3000) {
      recommendations.push('First Contentful Paint 개선: 이미지 최적화 및 CSS 최소화');
    }
    if (metrics.largestContentfulPaint > 4000) {
      recommendations.push('Largest Contentful Paint 개선: 큰 이미지 최적화 및 CDN 사용');
    }
    if (metrics.cumulativeLayoutShift > 0.25) {
      recommendations.push('Cumulative Layout Shift 개선: 이미지 크기 지정 및 동적 콘텐츠 최적화');
    }
    if (metrics.firstInputDelay > 300) {
      recommendations.push('First Input Delay 개선: JavaScript 번들 최적화 및 메인 스레드 블로킹 방지');
    }

    if (recommendations.length === 0) {
      recommendations.push('성능이 양호합니다. 현재 상태를 유지하세요.');
    }

    return recommendations;
  }
}

// 전역 성능 모니터 인스턴스
let performanceMonitor: PerformanceMonitor | null = null;
let memoryMonitor: MemoryMonitor | null = null;
let networkMonitor: NetworkMonitor | null = null;

// 성능 모니터링 초기화
export const initializePerformanceMonitoring = () => {
  if (typeof window !== 'undefined') {
    performanceMonitor = new PerformanceMonitor();
    memoryMonitor = new MemoryMonitor();
    networkMonitor = new NetworkMonitor();

    // 메모리 모니터링 시작 (개발 환경에서만)
    if (process.env.NODE_ENV === 'development') {
      memoryMonitor.startMonitoring();
    }

    // 네트워크 모니터링 시작
    networkMonitor.startMonitoring();

    // 성능 최적화 적용
    PerformanceOptimizer.optimizeScroll();
  }
};

// 성능 모니터링 정리
export const cleanupPerformanceMonitoring = () => {
  if (performanceMonitor) {
    performanceMonitor.disconnect();
  }
  if (memoryMonitor) {
    memoryMonitor.stopMonitoring();
  }
  if (networkMonitor) {
    networkMonitor.stopMonitoring();
  }
};

// 성능 메트릭 가져오기
export const getPerformanceMetrics = () => {
  return performanceMonitor?.getMetrics() || null;
};

export default {
  PerformanceMonitor,
  MemoryMonitor,
  NetworkMonitor,
  PerformanceOptimizer,
  initializePerformanceMonitoring,
  cleanupPerformanceMonitoring,
  getPerformanceMetrics,
}; 
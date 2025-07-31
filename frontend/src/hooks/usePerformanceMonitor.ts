import { useEffect, useState, useCallback } from 'react';

interface PerformanceMetrics {
  pageLoadTime: number;
  firstContentfulPaint: number;
  largestContentfulPaint: number;
  cumulativeLayoutShift: number;
  firstInputDelay: number;
  timeToInteractive: number;
}

interface UsePerformanceMonitorOptions {
  autoReport?: boolean;
  reportUrl?: string;
  threshold?: {
    pageLoadTime?: number;
    firstContentfulPaint?: number;
    largestContentfulPaint?: number;
    cumulativeLayoutShift?: number;
    firstInputDelay?: number;
  };
}

export const usePerformanceMonitor = (options: UsePerformanceMonitorOptions = {}) => {
  const {
    autoReport = true,
    reportUrl = '/api/performance/metrics',
    threshold = {
      pageLoadTime: 3000,
      firstContentfulPaint: 1800,
      largestContentfulPaint: 2500,
      cumulativeLayoutShift: 0.1,
      firstInputDelay: 100,
    },
  } = options;

  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [isMonitoring, setIsMonitoring] = useState(false);

  const measurePageLoad = useCallback(() => {
    if (typeof window === 'undefined' || !window.performance) return;

    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    const pageLoadTime = navigation.loadEventEnd - navigation.loadEventStart;

    return pageLoadTime;
  }, []);

  const measureWebVitals = useCallback(() => {
    if (typeof window === 'undefined') return;

    const metrics: Partial<PerformanceMetrics> = {};

    // First Contentful Paint
    const fcpObserver = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      const fcp = entries[entries.length - 1];
      metrics.firstContentfulPaint = fcp.startTime;
    });
    fcpObserver.observe({ entryTypes: ['paint'] });

    // Largest Contentful Paint
    const lcpObserver = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      const lcp = entries[entries.length - 1];
      metrics.largestContentfulPaint = lcp.startTime;
    });
    lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });

    // Cumulative Layout Shift
    const clsObserver = new PerformanceObserver((list) => {
      let cls = 0;
      for (const entry of list.getEntries()) {
        if (!(entry as any).hadRecentInput) {
          cls += (entry as any).value;
        }
      }
      metrics.cumulativeLayoutShift = cls;
    });
    clsObserver.observe({ entryTypes: ['layout-shift'] });

    // First Input Delay
    const fidObserver = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      const fid = entries[entries.length - 1];
      metrics.firstInputDelay = (fid as any).processingStart - fid.startTime;
    });
    fidObserver.observe({ entryTypes: ['first-input'] });

    return { fcpObserver, lcpObserver, clsObserver, fidObserver };
  }, []);

  const startMonitoring = useCallback(() => {
    if (isMonitoring) return;

    setIsMonitoring(true);
    const startTime = performance.now();

    // 페이지 로드 시간 측정
    const pageLoadTime = measurePageLoad();

    // Web Vitals 측정
    const observers = measureWebVitals();

    // Time to Interactive 측정
    const ttiObserver = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      const tti = entries[entries.length - 1];
      
      const finalMetrics: PerformanceMetrics = {
        pageLoadTime: pageLoadTime || 0,
        firstContentfulPaint: 0,
        largestContentfulPaint: 0,
        cumulativeLayoutShift: 0,
        firstInputDelay: 0,
        timeToInteractive: tti.startTime,
      };

      setMetrics(finalMetrics);

      // 자동 리포트
      if (autoReport) {
        reportMetrics(finalMetrics);
      }

      // 임계값 체크
      checkThresholds(finalMetrics);

      // 관찰자 정리
      if (observers) {
        Object.values(observers).forEach(observer => observer.disconnect());
      }
      ttiObserver.disconnect();
      setIsMonitoring(false);
    });

    ttiObserver.observe({ entryTypes: ['measure'] });
  }, [isMonitoring, measurePageLoad, measureWebVitals, autoReport]);

  const reportMetrics = useCallback(async (metrics: PerformanceMetrics) => {
    try {
      await fetch(reportUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: window.location.href,
          timestamp: new Date().toISOString(),
          metrics,
        }),
      });
    } catch (error) {
      console.error('성능 메트릭 리포트 실패:', error);
    }
  }, [reportUrl]);

  const checkThresholds = useCallback((metrics: PerformanceMetrics) => {
    const warnings = [];

    if (metrics.pageLoadTime > (threshold.pageLoadTime || 3000)) {
      warnings.push(`페이지 로드 시간이 느림: ${metrics.pageLoadTime}ms`);
    }

    if (metrics.firstContentfulPaint > (threshold.firstContentfulPaint || 1800)) {
      warnings.push(`FCP가 느림: ${metrics.firstContentfulPaint}ms`);
    }

    if (metrics.largestContentfulPaint > (threshold.largestContentfulPaint || 2500)) {
      warnings.push(`LCP가 느림: ${metrics.largestContentfulPaint}ms`);
    }

    if (metrics.cumulativeLayoutShift > (threshold.cumulativeLayoutShift || 0.1)) {
      warnings.push(`CLS가 높음: ${metrics.cumulativeLayoutShift}`);
    }

    if (metrics.firstInputDelay > (threshold.firstInputDelay || 100)) {
      warnings.push(`FID가 느림: ${metrics.firstInputDelay}ms`);
    }

    if (warnings.length > 0) {
      console.warn('성능 경고:', warnings);
    }
  }, [threshold]);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      startMonitoring();
    }
  }, [startMonitoring]);

  return {
    metrics,
    isMonitoring,
    startMonitoring,
    reportMetrics,
  };
}; 
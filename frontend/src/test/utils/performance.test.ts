import { render, screen } from '@testing-library/react'
import { act } from 'react-dom/test-utils'

// 성능 테스트 유틸리티
export class PerformanceTestUtils {
  // 컴포넌트 렌더링 성능 측정
  static async measureRenderPerformance(
    component: React.ReactElement,
    iterations: number = 10
  ) {
    const times: number[] = []
    
    for (let i = 0; i < iterations; i++) {
      const start = performance.now()
      
      await act(async () => {
        render(component)
      })
      
      const end = performance.now()
      times.push(end - start)
      
      // 정리
      // screen.unmount() // React Testing Library v14에서는 unmount가 제거됨
    }
    
    const avg = times.reduce((a, b) => a + b, 0) / times.length
    const min = Math.min(...times)
    const max = Math.max(...times)
    
    return {
      avg,
      min,
      max,
      times,
      iterations,
    }
  }
  
  // 메모리 사용량 측정
  static measureMemoryUsage() {
    if ('memory' in performance) {
      const memory = (performance as any).memory
      return {
        used: memory.usedJSHeapSize,
        total: memory.totalJSHeapSize,
        limit: memory.jsHeapSizeLimit,
        percentage: (memory.usedJSHeapSize / memory.jsHeapSizeLimit) * 100,
      }
    }
    return null
  }
  
  // 네트워크 요청 성능 측정
  static async measureNetworkPerformance(
    requestFn: () => Promise<any>,
    iterations: number = 5
  ) {
    const times: number[] = []
    const results: any[] = []
    
    for (let i = 0; i < iterations; i++) {
      const start = performance.now()
      
      try {
        const result = await requestFn()
        results.push(result)
      } catch (error) {
        console.error('Network request failed:', error)
      }
      
      const end = performance.now()
      times.push(end - start)
    }
    
    const avg = times.reduce((a, b) => a + b, 0) / times.length
    const min = Math.min(...times)
    const max = Math.max(...times)
    
    return {
      avg,
      min,
      max,
      times,
      results,
      iterations,
    }
  }
  
  // 이벤트 핸들러 성능 측정
  static measureEventHandlerPerformance(
    handler: () => void,
    iterations: number = 1000
  ) {
    const times: number[] = []
    
    for (let i = 0; i < iterations; i++) {
      const start = performance.now()
      handler()
      const end = performance.now()
      times.push(end - start)
    }
    
    const avg = times.reduce((a, b) => a + b, 0) / times.length
    const min = Math.min(...times)
    const max = Math.max(...times)
    
    return {
      avg,
      min,
      max,
      times,
      iterations,
    }
  }
  
  // 스크롤 성능 측정
  static measureScrollPerformance(
    scrollElement: HTMLElement,
    scrollDistance: number = 1000
  ) {
    const times: number[] = []
    const startY = scrollElement.scrollTop
    
    return new Promise<{
      avg: number
      min: number
      max: number
      times: number[]
    }>((resolve) => {
      let frameCount = 0
      const totalFrames = 60 // 1초간 60fps
      
      const animate = () => {
        const start = performance.now()
        
        scrollElement.scrollTop = startY + (scrollDistance * frameCount) / totalFrames
        
        const end = performance.now()
        times.push(end - start)
        
        frameCount++
        
        if (frameCount < totalFrames) {
          requestAnimationFrame(animate)
        } else {
          const avg = times.reduce((a, b) => a + b, 0) / times.length
          const min = Math.min(...times)
          const max = Math.max(...times)
          
          resolve({ avg, min, max, times })
        }
      }
      
      requestAnimationFrame(animate)
    })
  }
  
  // 성능 임계값 체크
  static checkPerformanceThreshold(
    metric: string,
    value: number,
    thresholds: { good: number; poor: number }
  ) {
    if (value <= thresholds.good) {
      return { status: 'good', message: `${metric} is good (${value.toFixed(2)}ms)` }
    } else if (value <= thresholds.poor) {
      return { status: 'needs-improvement', message: `${metric} needs improvement (${value.toFixed(2)}ms)` }
    } else {
      return { status: 'poor', message: `${metric} is poor (${value.toFixed(2)}ms)` }
    }
  }
  
  // 성능 리포트 생성
  static generatePerformanceReport(results: {
    renderTime?: number
    memoryUsage?: any
    networkTime?: number
    eventHandlerTime?: number
    scrollTime?: number
  }) {
    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        overall: 'good',
        issues: [] as string[],
        recommendations: [] as string[],
      },
      details: results,
    }
    
    // 렌더링 시간 체크
    if (results.renderTime) {
      const renderCheck = this.checkPerformanceThreshold('Render Time', results.renderTime, {
        good: 16, // 60fps 기준
        poor: 50,
      })
      
      if (renderCheck.status !== 'good') {
        report.summary.issues.push(renderCheck.message)
        report.summary.recommendations.push('React.memo나 useMemo를 사용하여 불필요한 리렌더링을 방지하세요.')
      }
    }
    
    // 메모리 사용량 체크
    if (results.memoryUsage) {
      const memoryPercentage = results.memoryUsage.percentage
      if (memoryPercentage > 80) {
        report.summary.issues.push(`High memory usage: ${memoryPercentage.toFixed(1)}%`)
        report.summary.recommendations.push('메모리 누수를 확인하고 불필요한 객체 참조를 정리하세요.')
      }
    }
    
    // 네트워크 시간 체크
    if (results.networkTime) {
      const networkCheck = this.checkPerformanceThreshold('Network Time', results.networkTime, {
        good: 200,
        poor: 1000,
      })
      
      if (networkCheck.status !== 'good') {
        report.summary.issues.push(networkCheck.message)
        report.summary.recommendations.push('API 응답을 캐싱하거나 CDN을 사용하세요.')
      }
    }
    
    // 전체 상태 결정
    if (report.summary.issues.length === 0) {
      report.summary.overall = 'excellent'
    } else if (report.summary.issues.length <= 2) {
      report.summary.overall = 'good'
    } else {
      report.summary.overall = 'needs-improvement'
    }
    
    return report
  }
}

// Jest 매처 확장
expect.extend({
  toHaveGoodPerformance(received: number, threshold: number = 16) {
    const pass = received <= threshold
    if (pass) {
      return {
        message: () => `expected ${received}ms to be slower than ${threshold}ms`,
        pass: true,
      }
    } else {
      return {
        message: () => `expected ${received}ms to be faster than ${threshold}ms`,
        pass: false,
      }
    }
  },
  
  toUseReasonableMemory(received: any) {
    const percentage = received.percentage
    const pass = percentage <= 80
    if (pass) {
      return {
        message: () => `expected memory usage ${percentage.toFixed(1)}% to be higher than 80%`,
        pass: true,
      }
    } else {
      return {
        message: () => `expected memory usage ${percentage.toFixed(1)}% to be lower than 80%`,
        pass: false,
      }
    }
  },
})

// 타입 선언
declare global {
  namespace jest {
    interface Matchers<R> {
      toHaveGoodPerformance(threshold?: number): R
      toUseReasonableMemory(): R
    }
  }
} 
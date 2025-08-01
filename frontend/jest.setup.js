import '@testing-library/jest-dom'
import 'jest-environment-jsdom'

// 전역 테스트 환경 설정
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}))

// IntersectionObserver 모킹
global.IntersectionObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}))

// Performance API 모킹
Object.defineProperty(window, 'performance', {
  value: {
    getEntriesByType: jest.fn(() => []),
    mark: jest.fn(),
    measure: jest.fn(),
    now: jest.fn(() => Date.now()),
    memory: {
      usedJSHeapSize: 1000000,
      totalJSHeapSize: 2000000,
      jsHeapSizeLimit: 4000000,
    },
  },
  writable: true,
})

// localStorage 모킹
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
}
global.localStorage = localStorageMock

// sessionStorage 모킹
const sessionStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
}
global.sessionStorage = sessionStorageMock

// fetch 모킹
global.fetch = jest.fn()

// URL.createObjectURL 모킹
global.URL.createObjectURL = jest.fn(() => 'mocked-url')

// matchMedia 모킹
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
})

// 스크롤 이벤트 모킹
Object.defineProperty(window, 'scrollTo', {
  value: jest.fn(),
  writable: true,
})

// 뷰포트 크기 모킹
Object.defineProperty(window, 'innerWidth', {
  writable: true,
  configurable: true,
  value: 1024,
})

Object.defineProperty(window, 'innerHeight', {
  writable: true,
  configurable: true,
  value: 768,
})

// 커스텀 매처 추가
expect.extend({
  toBeInTheDocument(received) {
    const pass = received !== null && received !== undefined
    if (pass) {
      return {
        message: () => `expected ${received} not to be in the document`,
        pass: true,
      }
    } else {
      return {
        message: () => `expected ${received} to be in the document`,
        pass: false,
      }
    }
  },
})

// 테스트 환경 정리
afterEach(() => {
  jest.clearAllMocks()
  localStorageMock.clear()
  sessionStorageMock.clear()
})

// 성능 테스트를 위한 유틸리티
global.performanceTest = {
  measure: (name, fn) => {
    const start = performance.now()
    const result = fn()
    const end = performance.now()
    console.log(`${name} took ${end - start}ms`)
    return result
  },
  
  benchmark: (name, iterations, fn) => {
    const times = []
    for (let i = 0; i < iterations; i++) {
      const start = performance.now()
      fn()
      const end = performance.now()
      times.push(end - start)
    }
    const avg = times.reduce((a, b) => a + b, 0) / times.length
    const min = Math.min(...times)
    const max = Math.max(...times)
    console.log(`${name}: avg=${avg.toFixed(2)}ms, min=${min.toFixed(2)}ms, max=${max.toFixed(2)}ms`)
    return { avg, min, max, times }
  },
} 
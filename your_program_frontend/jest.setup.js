import '@testing-library/jest-dom'
import { server } from './src/__tests__/mocks/server'

// MSW 서버 설정
beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

// MSW v2에 필요한 polyfills
global.Response = class Response {
  constructor(body, init = {}) {
    this.body = body
    this.status = init.status || 200
    this.statusText = init.statusText || 'OK'
    this.headers = new Headers(init.headers)
    this.ok = this.status >= 200 && this.status < 300
  }

  static json(data, init) {
    return new Response(JSON.stringify(data), {
      ...init,
      headers: {
        'Content-Type': 'application/json',
        ...init?.headers,
      },
    })
  }

  static error() {
    return new Response(null, { status: 500 })
  }

  static redirect(url, status) {
    return new Response(null, { status, headers: { Location: url } })
  }

  clone() {
    return new Response(this.body, {
      status: this.status,
      statusText: this.statusText,
      headers: this.headers,
    })
  }

  json() {
    return Promise.resolve(JSON.parse(this.body))
  }

  text() {
    return Promise.resolve(this.body)
  }

  blob() {
    return Promise.resolve(new Blob([this.body]))
  }

  arrayBuffer() {
    return Promise.resolve(new ArrayBuffer(0))
  }

  formData() {
    return Promise.resolve(new FormData())
  }
}

global.Request = class Request {
  constructor(input, init = {}) {
    this.url = typeof input === 'string' ? input : input.url
    this.method = init.method || 'GET'
    this.headers = new Headers(init.headers)
    this.body = init.body
  }
}

global.Headers = class Headers {
  constructor(init) {
    this._headers = new Map()
    if (init) {
      Object.entries(init).forEach(([key, value]) => {
        this.set(key, value)
      })
    }
  }

  append(name, value) {
    const key = name.toLowerCase()
    if (this._headers.has(key)) {
      const existing = this._headers.get(key)
      this._headers.set(key, `${existing}, ${value}`)
    } else {
      this._headers.set(key, value)
    }
  }

  delete(name) {
    this._headers.delete(name.toLowerCase())
  }

  get(name) {
    return this._headers.get(name.toLowerCase()) || null
  }

  has(name) {
    return this._headers.has(name.toLowerCase())
  }

  set(name, value) {
    this._headers.set(name.toLowerCase(), value)
  }

  entries() {
    return this._headers.entries()
  }

  keys() {
    return this._headers.keys()
  }

  values() {
    return this._headers.values()
  }

  forEach(callback) {
    this._headers.forEach((value, key) => callback(value, key, this))
  }
}

// 전역 모킹 설정
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}))

global.IntersectionObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}))

// Next.js의 use-intersection 훅을 위한 추가 polyfill
global.IntersectionObserverEntry = class IntersectionObserverEntry {
  constructor(init) {
    this.target = init.target;
    this.isIntersecting = init.isIntersecting;
    this.intersectionRatio = init.intersectionRatio;
    this.boundingClientRect = init.boundingClientRect;
    this.rootBounds = init.rootBounds;
    this.time = init.time;
  }
}

// WebSocket 모킹
global.WebSocket = jest.fn().mockImplementation(() => ({
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  send: jest.fn(),
  close: jest.fn(),
  readyState: 1, // OPEN
}))

// Notification API 모킹
Object.defineProperty(window, 'Notification', {
  value: {
    permission: 'granted',
    requestPermission: jest.fn().mockResolvedValue('granted'),
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

// URL.revokeObjectURL 모킹
global.URL.revokeObjectURL = jest.fn()

// BroadcastChannel polyfill
global.BroadcastChannel = class BroadcastChannel {
  constructor(name) {
    this.name = name
    this.onmessage = null
  }
  postMessage() {}
  close() {}
  addEventListener() {}
  removeEventListener() {}
}

// console.error 무시 (테스트 중 불필요한 경고 숨김)
const originalError = console.error
beforeAll(() => {
  console.error = (...args) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('Warning: ReactDOM.render is no longer supported')
    ) {
      return
    }
    originalError.call(console, ...args)
  }
})

afterAll(() => {
  console.error = originalError
})

// 테스트 환경 설정
process.env.NODE_ENV = 'test'
process.env.NEXT_PUBLIC_API_URL = 'http://localhost:5001'
process.env.NEXT_PUBLIC_WS_URL = 'ws://localhost:5001'

// 타임아웃 설정
jest.setTimeout(10000)

// 커스텀 매처 추가
expect.extend({
  toBeInTheDocument(received) {
    const pass = received !== null
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
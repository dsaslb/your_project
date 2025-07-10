// Jest polyfills for browser APIs
import 'whatwg-fetch'

// TextEncoder/TextDecoder polyfills
import { TextEncoder, TextDecoder } from 'util'
global.TextEncoder = TextEncoder
global.TextDecoder = TextDecoder

// Web Streams API polyfills
global.TransformStream = class TransformStream {
  constructor() {
    this.readable = new ReadableStream()
    this.writable = new WritableStream()
  }
}

global.ReadableStream = class ReadableStream {
  constructor() {
    this.locked = false
  }
  
  getReader() {
    return {
      read: () => Promise.resolve({ done: true, value: undefined }),
      releaseLock: () => {},
    }
  }
  
  cancel() {
    return Promise.resolve()
  }
}

global.WritableStream = class WritableStream {
  constructor() {
    this.locked = false
  }
  
  getWriter() {
    return {
      write: () => Promise.resolve(),
      close: () => Promise.resolve(),
      abort: () => Promise.resolve(),
      releaseLock: () => {},
    }
  }
  
  close() {
    return Promise.resolve()
  }
}

global.CompressionStream = class CompressionStream {
  constructor(format) {
    this.format = format
    this.readable = new ReadableStream()
    this.writable = new WritableStream()
  }
}

global.DecompressionStream = class DecompressionStream {
  constructor(format) {
    this.format = format
    this.readable = new ReadableStream()
    this.writable = new WritableStream()
  }
}

// Blob polyfill
global.Blob = class Blob {
  constructor(parts, options) {
    this.parts = parts
    this.options = options
    this.size = parts.reduce((acc, part) => acc + (part.length || 0), 0)
    this.type = options?.type || ''
  }
}

global.File = class File extends Blob {
  constructor(parts, filename, options) {
    super(parts, options)
    this.name = filename
    this.lastModified = Date.now()
  }
}

global.FormData = class FormData {
  constructor() {
    this._data = new Map()
  }
  
  append(key, value) {
    this._data.set(key, value)
  }
  
  get(key) {
    return this._data.get(key) || null
  }
  
  has(key) {
    return this._data.has(key)
  }
  
  delete(key) {
    return this._data.delete(key)
  }
  
  entries() {
    return this._data.entries()
  }
  
  keys() {
    return this._data.keys()
  }
  
  values() {
    return this._data.values()
  }
  
  forEach(callback) {
    this._data.forEach((value, key) => callback(value, key, this))
  }
}

// Headers polyfill
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

// Request polyfill
global.Request = class Request {
  constructor(input, init = {}) {
    this.url = typeof input === 'string' ? input : input.url
    this.method = init.method || 'GET'
    this.headers = new Headers(init.headers)
    this.body = init.body
  }
}

// Response polyfill
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

// EventTarget polyfill
global.EventTarget = class EventTarget {
  constructor() {
    this._listeners = new Map()
  }

  addEventListener(type, listener, options) {
    if (!this._listeners.has(type)) {
      this._listeners.set(type, [])
    }
    this._listeners.get(type).push({ listener, options })
  }

  removeEventListener(type, listener) {
    if (!this._listeners.has(type)) return
    const listeners = this._listeners.get(type)
    const index = listeners.findIndex(l => l.listener === listener)
    if (index !== -1) {
      listeners.splice(index, 1)
    }
  }

  dispatchEvent(event) {
    if (!this._listeners.has(event.type)) return true
    const listeners = this._listeners.get(event.type)
    listeners.forEach(({ listener }) => {
      try {
        listener.call(this, event)
      } catch (error) {
        console.error('Error in event listener:', error)
      }
    })
    return true
  }
}

// Event polyfill
global.Event = class Event extends EventTarget {
  constructor(type, init = {}) {
    super()
    this.type = type
    this.target = null
    this.currentTarget = null
    this.eventPhase = 0
    this.bubbles = init.bubbles || false
    this.cancelable = init.cancelable || false
    this.defaultPrevented = false
    this.composed = init.composed || false
    this.timeStamp = Date.now()
    this.isTrusted = false
  }

  preventDefault() {
    if (this.cancelable) {
      this.defaultPrevented = true
    }
  }

  stopPropagation() {
    // Implementation would go here
  }

  stopImmediatePropagation() {
    // Implementation would go here
  }
}

// CustomEvent polyfill
global.CustomEvent = class CustomEvent extends Event {
  constructor(type, init = {}) {
    super(type, init)
    this.detail = init.detail || null
  }
}

// MessageEvent polyfill
global.MessageEvent = class MessageEvent extends Event {
  constructor(type, init = {}) {
    super(type, init)
    this.data = init.data || null
    this.origin = init.origin || ''
    this.lastEventId = init.lastEventId || ''
    this.source = init.source || null
    this.ports = init.ports || []
  }
}

// CloseEvent polyfill
global.CloseEvent = class CloseEvent extends Event {
  constructor(type, init = {}) {
    super(type, init)
    this.code = init.code || 0
    this.reason = init.reason || ''
    this.wasClean = init.wasClean || false
  }
}

// ErrorEvent polyfill
global.ErrorEvent = class ErrorEvent extends Event {
  constructor(type, init = {}) {
    super(type, init)
    this.message = init.message || ''
    this.filename = init.filename || ''
    this.lineno = init.lineno || 0
    this.colno = init.colno || 0
    this.error = init.error || null
  }
}

// Navigator polyfill
global.navigator = {
  userAgent: 'Jest Test Environment',
  language: 'ko-KR',
  languages: ['ko-KR', 'ko', 'en'],
  onLine: true,
  cookieEnabled: true,
  doNotTrack: null,
  geolocation: {
    getCurrentPosition: jest.fn(),
    watchPosition: jest.fn(),
    clearWatch: jest.fn(),
  },
  mediaDevices: {
    getUserMedia: jest.fn(),
    enumerateDevices: jest.fn(),
  },
  serviceWorker: {
    register: jest.fn(),
    getRegistration: jest.fn(),
    getRegistrations: jest.fn(),
  },
  sendBeacon: jest.fn(),
  share: jest.fn(),
  vibrate: jest.fn(),
}

// screen polyfill
global.screen = {
  availHeight: 1040,
  availWidth: 1920,
  colorDepth: 24,
  height: 1080,
  width: 1920,
  orientation: {
    angle: 0,
    type: 'landscape-primary',
  },
  pixelDepth: 24,
}

// window polyfill
global.window = global

// document polyfill
global.document = {
  createElement: jest.fn(() => ({
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    setAttribute: jest.fn(),
    getAttribute: jest.fn(),
    appendChild: jest.fn(),
    removeChild: jest.fn(),
    querySelector: jest.fn(),
    querySelectorAll: jest.fn(),
    getElementsByTagName: jest.fn(() => []),
    getElementsByClassName: jest.fn(() => []),
    getElementById: jest.fn(),
    focus: jest.fn(),
    blur: jest.fn(),
    click: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
  createTextNode: jest.fn((text) => ({ textContent: text })),
  getElementById: jest.fn(),
  querySelector: jest.fn(),
  querySelectorAll: jest.fn(() => []),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  dispatchEvent: jest.fn(),
  documentElement: {
    style: {},
  },
  body: {
    appendChild: jest.fn(),
    removeChild: jest.fn(),
  },
  head: {
    appendChild: jest.fn(),
    removeChild: jest.fn(),
  },
  title: 'Test Document',
  cookie: '',
  domain: 'localhost',
  lastModified: new Date().toISOString(),
  readyState: 'complete',
  referrer: '',
  URL: 'http://localhost:3000',
  visibilityState: 'visible',
  hidden: false,
}

// location polyfill
global.location = {
  href: 'http://localhost:3000',
  protocol: 'http:',
  host: 'localhost:3000',
  hostname: 'localhost',
  port: '3000',
  pathname: '/',
  search: '',
  hash: '',
  origin: 'http://localhost:3000',
  assign: jest.fn(),
  replace: jest.fn(),
  reload: jest.fn(),
}

// history polyfill
global.history = {
  length: 1,
  scrollRestoration: 'auto',
  state: null,
  back: jest.fn(),
  forward: jest.fn(),
  go: jest.fn(),
  pushState: jest.fn(),
  replaceState: jest.fn(),
}

// localStorage polyfill
global.localStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
  key: jest.fn(),
  length: 0,
}

// sessionStorage polyfill
global.sessionStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
  key: jest.fn(),
  length: 0,
}

// indexedDB polyfill
global.indexedDB = {
  open: jest.fn(),
  deleteDatabase: jest.fn(),
  databases: jest.fn(),
}

// crypto polyfill
global.crypto = {
  getRandomValues: jest.fn((array) => {
    for (let i = 0; i < array.length; i++) {
      array[i] = Math.floor(Math.random() * 256)
    }
    return array
  }),
  randomUUID: jest.fn(() => 'test-uuid'),
  subtle: {
    generateKey: jest.fn(),
    importKey: jest.fn(),
    exportKey: jest.fn(),
    sign: jest.fn(),
    verify: jest.fn(),
    encrypt: jest.fn(),
    decrypt: jest.fn(),
    digest: jest.fn(),
  },
}

// btoa/atob polyfill
global.btoa = (str) => Buffer.from(str, 'binary').toString('base64')
global.atob = (str) => Buffer.from(str, 'base64').toString('binary')

// requestAnimationFrame polyfill
global.requestAnimationFrame = (callback) => {
  return setTimeout(callback, 16)
}

global.cancelAnimationFrame = (id) => {
  clearTimeout(id)
}

// requestIdleCallback polyfill
global.requestIdleCallback = (callback) => {
  return setTimeout(callback, 1)
}

global.cancelIdleCallback = (id) => {
  clearTimeout(id)
} 

global.BroadcastChannel = class BroadcastChannel {
  constructor(name) {
    this.name = name
    this.onmessage = null
  }
  postMessage() {}
  close() {}
  addEventListener() {}
  removeEventListener() {}
}; 
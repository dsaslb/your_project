import { setupServer } from 'msw/node'
import { http, HttpResponse } from 'msw'

// API 응답 모킹 데이터
const mockUsers = [
  {
    id: 1,
    username: 'admin',
    name: '관리자',
    email: 'admin@yourprogram.com',
    role: 'super_admin',
    is_active: true,
  },
  {
    id: 2,
    username: 'manager',
    name: '매장 관리자',
    email: 'manager@yourprogram.com',
    role: 'store_manager',
    is_active: true,
  },
  {
    id: 3,
    username: 'employee',
    name: '직원',
    email: 'employee@yourprogram.com',
    role: 'employee',
    is_active: true,
  },
]

const mockOrders = [
  {
    id: 1,
    orderNumber: 'ORD-001',
    customerName: '김고객',
    items: [
      { id: 1, productName: '아메리카노', quantity: 2, price: 4500 },
      { id: 2, productName: '카페라떼', quantity: 1, price: 5500 },
    ],
    totalAmount: 14500,
    status: 'pending',
    branchId: 1,
    createdAt: '2024-01-15T10:30:00Z',
    updatedAt: '2024-01-15T10:30:00Z',
  },
  {
    id: 2,
    orderNumber: 'ORD-002',
    customerName: '이고객',
    items: [
      { id: 3, productName: '카푸치노', quantity: 1, price: 5000 },
    ],
    totalAmount: 5000,
    status: 'confirmed',
    branchId: 1,
    createdAt: '2024-01-15T11:00:00Z',
    updatedAt: '2024-01-15T11:00:00Z',
  },
]

const mockInventory = [
  {
    id: 1,
    name: '아메리카노',
    category: '음료',
    quantity: 100,
    unit: '잔',
    minQuantity: 10,
    maxQuantity: 200,
    price: 4500,
    supplier: '커피공급업체',
    lastUpdated: '2024-01-15T09:00:00Z',
  },
  {
    id: 2,
    name: '카페라떼',
    category: '음료',
    quantity: 80,
    unit: '잔',
    minQuantity: 10,
    maxQuantity: 150,
    price: 5500,
    supplier: '커피공급업체',
    lastUpdated: '2024-01-15T09:00:00Z',
  },
]

const mockStaff = [
  {
    id: 1,
    name: '김직원',
    email: 'kim@yourprogram.com',
    phone: '010-1234-5678',
    role: 'employee',
    department: '매장',
    position: '바리스타',
    hireDate: '2023-01-15',
    isActive: true,
  },
  {
    id: 2,
    name: '이매니저',
    email: 'lee@yourprogram.com',
    phone: '010-2345-6789',
    role: 'store_manager',
    department: '매장',
    position: '매장 관리자',
    hireDate: '2022-06-01',
    isActive: true,
  },
]

// API 핸들러 정의
export const handlers = [
  // 인증 관련 API
  http.post('/api/auth/login', async ({ request }) => {
    const { username, password } = await request.json() as any
    
    const user = mockUsers.find(u => u.username === username)
    
    if (user && password === 'password') {
      return HttpResponse.json({
        success: true,
        user,
        token: 'mock-jwt-token',
        redirect_to: '/dashboard'
      })
    }
    
    return HttpResponse.json(
      {
        success: false,
        message: '잘못된 사용자명 또는 비밀번호입니다.'
      },
      { status: 401 }
    )
  }),

  http.post('/api/auth/logout', () => {
    return HttpResponse.json({
      success: true,
      message: '로그아웃되었습니다.'
    })
  }),

  http.get('/api/auth/profile', ({ request }) => {
    const authHeader = request.headers.get('Authorization')
    
    if (authHeader && authHeader.startsWith('Bearer ')) {
      return HttpResponse.json(mockUsers[0])
    }
    
    return HttpResponse.json(
      {
        message: '인증이 필요합니다.'
      },
      { status: 401 }
    )
  }),

  // 사용자 관리 API
  http.get('/api/users', () => {
    return HttpResponse.json(mockUsers)
  }),

  http.get('/api/users/:id', ({ params }) => {
    const { id } = params
    const user = mockUsers.find(u => u.id === parseInt(id as string))
    
    if (user) {
      return HttpResponse.json(user)
    }
    
    return HttpResponse.json(
      {
        message: '사용자를 찾을 수 없습니다.'
      },
      { status: 404 }
    )
  }),

  http.post('/api/users', async ({ request }) => {
    const newUser = await request.json() as any
    const user = {
      ...newUser,
      id: mockUsers.length + 1,
      is_active: true,
    }
    
    return HttpResponse.json(user, { status: 201 })
  }),

  http.put('/api/users/:id', async ({ params, request }) => {
    const { id } = params
    const updates = await request.json() as any
    
    const user = mockUsers.find(u => u.id === parseInt(id as string))
    if (user) {
      const updatedUser = { ...user, ...updates }
      return HttpResponse.json(updatedUser)
    }
    
    return HttpResponse.json(
      {
        message: '사용자를 찾을 수 없습니다.'
      },
      { status: 404 }
    )
  }),

  http.delete('/api/users/:id', ({ params }) => {
    const { id } = params
    
    const user = mockUsers.find(u => u.id === parseInt(id as string))
    if (user) {
      return HttpResponse.json({
        message: '사용자가 삭제되었습니다.'
      })
    }
    
    return HttpResponse.json(
      {
        message: '사용자를 찾을 수 없습니다.'
      },
      { status: 404 }
    )
  }),

  // 주문 관리 API
  http.get('/api/orders', () => {
    return HttpResponse.json(mockOrders)
  }),

  http.get('/api/orders/:id', ({ params }) => {
    const { id } = params
    const order = mockOrders.find(o => o.id === parseInt(id as string))
    
    if (order) {
      return HttpResponse.json(order)
    }
    
    return HttpResponse.json(
      {
        message: '주문을 찾을 수 없습니다.'
      },
      { status: 404 }
    )
  }),

  http.post('/api/orders', async ({ request }) => {
    const newOrder = await request.json() as any
    const order = {
      ...newOrder,
      id: mockOrders.length + 1,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
    
    return HttpResponse.json(order, { status: 201 })
  }),

  http.put('/api/orders/:id', async ({ params, request }) => {
    const { id } = params
    const updates = await request.json() as any
    
    const order = mockOrders.find(o => o.id === parseInt(id as string))
    if (order) {
      const updatedOrder = { 
        ...order, 
        ...updates,
        updatedAt: new Date().toISOString()
      }
      return HttpResponse.json(updatedOrder)
    }
    
    return HttpResponse.json(
      {
        message: '주문을 찾을 수 없습니다.'
      },
      { status: 404 }
    )
  }),

  http.delete('/api/orders/:id', ({ params }) => {
    const { id } = params
    
    const order = mockOrders.find(o => o.id === parseInt(id as string))
    if (order) {
      return HttpResponse.json({
        message: '주문이 삭제되었습니다.'
      })
    }
    
    return HttpResponse.json(
      {
        message: '주문을 찾을 수 없습니다.'
      },
      { status: 404 }
    )
  }),

  // 재고 관리 API
  http.get('/api/inventory', () => {
    return HttpResponse.json(mockInventory)
  }),

  http.get('/api/inventory/:id', ({ params }) => {
    const { id } = params
    const item = mockInventory.find(i => i.id === parseInt(id as string))
    
    if (item) {
      return HttpResponse.json(item)
    }
    
    return HttpResponse.json(
      {
        message: '재고 항목을 찾을 수 없습니다.'
      },
      { status: 404 }
    )
  }),

  http.post('/api/inventory', async ({ request }) => {
    const newItem = await request.json() as any
    const item = {
      ...newItem,
      id: mockInventory.length + 1,
      lastUpdated: new Date().toISOString(),
    }
    
    return HttpResponse.json(item, { status: 201 })
  }),

  http.put('/api/inventory/:id', async ({ params, request }) => {
    const { id } = params
    const updates = await request.json() as any
    
    const item = mockInventory.find(i => i.id === parseInt(id as string))
    if (item) {
      const updatedItem = { 
        ...item, 
        ...updates,
        lastUpdated: new Date().toISOString()
      }
      return HttpResponse.json(updatedItem)
    }
    
    return HttpResponse.json(
      {
        message: '재고 항목을 찾을 수 없습니다.'
      },
      { status: 404 }
    )
  }),

  // 직원 관리 API
  http.get('/api/staff', () => {
    return HttpResponse.json(mockStaff)
  }),

  http.get('/api/staff/:id', ({ params }) => {
    const { id } = params
    const staff = mockStaff.find(s => s.id === parseInt(id as string))
    
    if (staff) {
      return HttpResponse.json(staff)
    }
    
    return HttpResponse.json(
      {
        message: '직원을 찾을 수 없습니다.'
      },
      { status: 404 }
    )
  }),

  // 대시보드 통계 API
  http.get('/api/dashboard/stats', () => {
    return HttpResponse.json({
      totalOrders: mockOrders.length,
      totalRevenue: mockOrders.reduce((sum, order) => sum + order.totalAmount, 0),
      totalUsers: mockUsers.length,
      totalInventory: mockInventory.length,
      recentOrders: mockOrders.slice(-5),
      lowStockItems: mockInventory.filter(item => item.quantity <= item.minQuantity),
    })
  }),

  // 알림 API
  http.get('/api/notifications', () => {
    return HttpResponse.json([
      {
        id: 1,
        title: '새로운 주문',
        message: '새로운 주문이 들어왔습니다.',
        type: 'order',
        read: false,
        createdAt: new Date().toISOString(),
      },
      {
        id: 2,
        title: '재고 부족',
        message: '아메리카노 재고가 부족합니다.',
        type: 'inventory',
        read: false,
        createdAt: new Date().toISOString(),
      },
    ])
  }),

  // 기본 핸들러 (404)
  http.all('*', ({ request }) => {
    console.warn(`Unhandled ${request.method} request to ${request.url}`)
    return HttpResponse.json(
      {
        message: '요청한 리소스를 찾을 수 없습니다.'
      },
      { status: 404 }
    )
  }),
]

// MSW 서버 설정
export const server = setupServer(...handlers) 
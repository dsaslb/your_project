import '@testing-library/jest-dom'

// Mock API functions
const mockApi = {
  login: async (credentials: { username: string; password: string }) => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 100))
    
    if (credentials.username === 'admin' && credentials.password === 'password') {
      return {
        success: true,
        token: 'mock-jwt-token',
        user: {
          id: 1,
          username: 'admin',
          role: 'super_admin'
        }
      }
    } else {
      throw new Error('Invalid credentials')
    }
  },
  
  getUsers: async (token: string) => {
    await new Promise(resolve => setTimeout(resolve, 50))
    
    if (token === 'mock-jwt-token') {
      return {
        success: true,
        users: [
          { id: 1, username: 'admin', role: 'super_admin' },
          { id: 2, username: 'manager', role: 'store_manager' },
          { id: 3, username: 'employee', role: 'employee' }
        ]
      }
    } else {
      throw new Error('Unauthorized')
    }
  },
  
  getNotifications: async (token: string) => {
    await new Promise(resolve => setTimeout(resolve, 30))
    
    if (token === 'mock-jwt-token') {
      return {
        success: true,
        notifications: [
          { id: 1, message: 'New order received', type: 'info' },
          { id: 2, message: 'Inventory low', type: 'warning' }
        ]
      }
    } else {
      throw new Error('Unauthorized')
    }
  }
}

describe('API Tests', () => {
  test('login with valid credentials', async () => {
    const credentials = { username: 'admin', password: 'password' }
    const result = await mockApi.login(credentials)
    
    expect(result.success).toBe(true)
    expect(result.token).toBe('mock-jwt-token')
    expect(result.user.username).toBe('admin')
    expect(result.user.role).toBe('super_admin')
  })
  
  test('login with invalid credentials', async () => {
    const credentials = { username: 'admin', password: 'wrong' }
    
    await expect(mockApi.login(credentials)).rejects.toThrow('Invalid credentials')
  })
  
  test('getUsers with valid token', async () => {
    const token = 'mock-jwt-token'
    const result = await mockApi.getUsers(token)
    
    expect(result.success).toBe(true)
    expect(result.users).toHaveLength(3)
    expect(result.users[0].username).toBe('admin')
    expect(result.users[1].username).toBe('manager')
    expect(result.users[2].username).toBe('employee')
  })
  
  test('getUsers with invalid token', async () => {
    const token = 'invalid-token'
    
    await expect(mockApi.getUsers(token)).rejects.toThrow('Unauthorized')
  })
  
  test('getNotifications with valid token', async () => {
    const token = 'mock-jwt-token'
    const result = await mockApi.getNotifications(token)
    
    expect(result.success).toBe(true)
    expect(result.notifications).toHaveLength(2)
    expect(result.notifications[0].message).toBe('New order received')
    expect(result.notifications[1].type).toBe('warning')
  })
  
  test('API response time is reasonable', async () => {
    const startTime = Date.now()
    await mockApi.login({ username: 'admin', password: 'password' })
    const endTime = Date.now()
    
    const responseTime = endTime - startTime
    expect(responseTime).toBeGreaterThanOrEqual(100) // Should be at least 100ms due to mock delay
    expect(responseTime).toBeLessThan(200) // Should not be too slow
  })
}) 
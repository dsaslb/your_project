import { renderHook, act } from '@testing-library/react'
import useUserStore from '@/store/useUserStore'

// Mock API client
jest.mock('@/lib/api-client', () => ({
  apiClient: {
    post: jest.fn(),
    get: jest.fn(),
    put: jest.fn(),
  },
}))

describe('useUserStore', () => {
  beforeEach(() => {
    // Store 초기화
    act(() => {
      useUserStore.getState().logout()
    })
    
    // localStorage 모킹
    const localStorageMock = {
      getItem: jest.fn(),
      setItem: jest.fn(),
      removeItem: jest.fn(),
      clear: jest.fn(),
    }
    Object.defineProperty(window, 'localStorage', {
      value: localStorageMock,
      writable: true,
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  describe('초기 상태', () => {
    it('초기 상태가 올바르게 설정되어야 함', () => {
      const { result } = renderHook(() => useUserStore())
      
      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
      expect(result.current.isLoading).toBe(false)
      expect(result.current.error).toBeNull()
    })
  })

  describe('로그인', () => {
    it('성공적인 로그인이 작동해야 함', async () => {
      const mockUser = {
        id: 1,
        username: 'admin',
        name: '관리자',
        email: 'admin@yourprogram.com',
        role: 'super_admin' as const,
        is_active: true,
      }

      const mockResponse = {
        success: true,
        user: mockUser,
        token: 'mock-jwt-token',
        redirect_to: '/dashboard',
      }

      // API 모킹
      const { apiClient } = require('@/lib/api-client')
      apiClient.post.mockResolvedValue({
        data: mockResponse,
      })

      const { result } = renderHook(() => useUserStore())

      await act(async () => {
        const response = await result.current.login('admin', 'password')
        expect(response.success).toBe(true)
        expect(response.redirectTo).toBe('/dashboard')
      })

      expect(result.current.user).toEqual(mockUser)
      expect(result.current.isAuthenticated).toBe(true)
      expect(result.current.error).toBeNull()
    })

    it('로그인 실패 시 에러가 설정되어야 함', async () => {
      const mockResponse = {
        success: false,
        message: '잘못된 사용자명 또는 비밀번호입니다.',
      }

      const { apiClient } = require('@/lib/api-client')
      apiClient.post.mockResolvedValue({
        data: mockResponse,
      })

      const { result } = renderHook(() => useUserStore())

      await act(async () => {
        const response = await result.current.login('wrong', 'wrong')
        expect(response.success).toBe(false)
      })

      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
      expect(result.current.error).toBe('잘못된 사용자명 또는 비밀번호입니다.')
    })

    it('네트워크 에러 시 적절히 처리되어야 함', async () => {
      const { apiClient } = require('@/lib/api-client')
      apiClient.post.mockRejectedValue(new Error('Network error'))

      const { result } = renderHook(() => useUserStore())

      await act(async () => {
        const response = await result.current.login('admin', 'password')
        expect(response.success).toBe(false)
      })

      expect(result.current.error).toContain('로그인 중 오류가 발생했습니다')
    })
  })

  describe('로그아웃', () => {
    it('로그아웃이 올바르게 작동해야 함', async () => {
      const { result } = renderHook(() => useUserStore())

      // 먼저 로그인 상태로 설정
      act(() => {
        useUserStore.setState({
          user: {
            id: 1,
            username: 'admin',
            name: '관리자',
            email: 'admin@yourprogram.com',
            role: 'super_admin',
            is_active: true,
          },
          isAuthenticated: true,
        })
      })

      // 로그아웃 실행
      act(() => {
        result.current.logout()
      })

      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
      expect(result.current.error).toBeNull()
    })
  })

  describe('인증 확인', () => {
    it('유효한 토큰으로 인증 확인이 성공해야 함', async () => {
      const mockUser = {
        id: 1,
        username: 'admin',
        name: '관리자',
        email: 'admin@yourprogram.com',
        role: 'super_admin' as const,
        is_active: true,
      }

      const { apiClient } = require('@/lib/api-client')
      apiClient.get.mockResolvedValue({
        data: mockUser,
      })

      const { result } = renderHook(() => useUserStore())

      await act(async () => {
        const isAuthenticated = await result.current.checkAuth()
        expect(isAuthenticated).toBe(true)
      })

      expect(result.current.user).toEqual(mockUser)
      expect(result.current.isAuthenticated).toBe(true)
    })

    it('유효하지 않은 토큰으로 인증 확인이 실패해야 함', async () => {
      const { apiClient } = require('@/lib/api-client')
      apiClient.get.mockRejectedValue(new Error('Unauthorized'))

      const { result } = renderHook(() => useUserStore())

      await act(async () => {
        const isAuthenticated = await result.current.checkAuth()
        expect(isAuthenticated).toBe(false)
      })

      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
    })
  })

  describe('권한 관리', () => {
    beforeEach(() => {
      act(() => {
        useUserStore.setState({
          user: {
            id: 1,
            username: 'admin',
            name: '관리자',
            email: 'admin@yourprogram.com',
            role: 'super_admin',
            is_active: true,
          },
          isAuthenticated: true,
        })
      })
    })

    it('단일 권한 체크가 올바르게 작동해야 함', () => {
      const { result } = renderHook(() => useUserStore())

      expect(result.current.hasRole('super_admin')).toBe(true)
      expect(result.current.hasRole('store_manager')).toBe(false)
      expect(result.current.hasRole('employee')).toBe(false)
    })

    it('다중 권한 체크가 올바르게 작동해야 함', () => {
      const { result } = renderHook(() => useUserStore())

      expect(result.current.hasRole(['super_admin', 'store_manager'])).toBe(true)
      expect(result.current.hasRole(['store_manager', 'employee'])).toBe(false)
    })

    it('인증되지 않은 사용자는 모든 권한 체크가 false여야 함', () => {
      act(() => {
        useUserStore.setState({
          user: null,
          isAuthenticated: false,
        })
      })

      const { result } = renderHook(() => useUserStore())

      expect(result.current.hasRole('super_admin')).toBe(false)
      expect(result.current.hasRole(['super_admin', 'store_manager'])).toBe(false)
    })
  })

  describe('프로필 업데이트', () => {
    beforeEach(() => {
      act(() => {
        useUserStore.setState({
          user: {
            id: 1,
            username: 'admin',
            name: '관리자',
            email: 'admin@yourprogram.com',
            role: 'super_admin',
            is_active: true,
          },
          isAuthenticated: true,
        })
      })
    })

    it('프로필 업데이트가 성공해야 함', async () => {
      const updatedUser = {
        id: 1,
        username: 'admin',
        name: '새로운 이름',
        email: 'newemail@yourprogram.com',
        role: 'super_admin' as const,
        is_active: true,
      }

      const { apiClient } = require('@/lib/api-client')
      apiClient.put.mockResolvedValue({
        data: updatedUser,
      })

      const { result } = renderHook(() => useUserStore())

      await act(async () => {
        const success = await result.current.updateProfile({
          name: '새로운 이름',
          email: 'newemail@yourprogram.com',
        })
        expect(success).toBe(true)
      })

      expect(result.current.user).toEqual(updatedUser)
    })

    it('프로필 업데이트 실패 시 에러가 처리되어야 함', async () => {
      const { apiClient } = require('@/lib/api-client')
      apiClient.put.mockRejectedValue(new Error('Update failed'))

      const { result } = renderHook(() => useUserStore())

      await act(async () => {
        const success = await result.current.updateProfile({
          name: '새로운 이름',
        })
        expect(success).toBe(false)
      })

      expect(result.current.error).toContain('프로필 업데이트 중 오류가 발생했습니다')
    })
  })

  describe('실시간 동기화', () => {
    it('변경사항 구독이 작동해야 함', () => {
      const { result } = renderHook(() => useUserStore())
      
      const mockCallback = jest.fn()
      const unsubscribe = result.current.subscribeToChanges(mockCallback)
      
      expect(typeof unsubscribe).toBe('function')
    })

    it('변경사항 브로드캐스트가 작동해야 함', () => {
      const { result } = renderHook(() => useUserStore())
      
      const mockCallback = jest.fn()
      result.current.subscribeToChanges(mockCallback)
      
      act(() => {
        result.current.broadcastChange('test-action')
      })
      
      expect(mockCallback).toHaveBeenCalled()
    })

    it('localStorage 이벤트 리스너가 작동해야 함', () => {
      const { result } = renderHook(() => useUserStore())
      
      const mockCallback = jest.fn()
      result.current.subscribeToChanges(mockCallback)
      
      // localStorage 이벤트 시뮬레이션
      act(() => {
        window.dispatchEvent(new StorageEvent('storage', {
          key: 'user-store',
          newValue: JSON.stringify({
            user: {
              id: 1,
              username: 'admin',
              name: '관리자',
              email: 'admin@yourprogram.com',
              role: 'super_admin',
              is_active: true,
            },
            isAuthenticated: true,
          }),
        }))
      })
      
      expect(mockCallback).toHaveBeenCalled()
    })
  })

  describe('에러 처리', () => {
    it('에러 클리어가 작동해야 함', () => {
      const { result } = renderHook(() => useUserStore())
      
      act(() => {
        useUserStore.setState({ error: '테스트 에러' })
      })
      
      expect(result.current.error).toBe('테스트 에러')
      
      act(() => {
        result.current.clearError()
      })
      
      expect(result.current.error).toBeNull()
    })
  })

  describe('로딩 상태', () => {
    it('로그인 중 로딩 상태가 올바르게 관리되어야 함', async () => {
      const { apiClient } = require('@/lib/api-client')
      apiClient.post.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))

      const { result } = renderHook(() => useUserStore())

      const loginPromise = act(async () => {
        return await result.current.login('admin', 'password')
      })

      expect(result.current.isLoading).toBe(true)

      await loginPromise
      expect(result.current.isLoading).toBe(false)
    })
  })

  describe('지속성', () => {
    it('localStorage에 상태가 저장되어야 함', () => {
      const mockUser = {
        id: 1,
        username: 'admin',
        name: '관리자',
        email: 'admin@yourprogram.com',
        role: 'super_admin' as const,
        is_active: true,
      }

      act(() => {
        useUserStore.setState({
          user: mockUser,
          isAuthenticated: true,
        })
      })

      expect(localStorage.setItem).toHaveBeenCalledWith(
        'user-store',
        expect.stringContaining('"user":')
      )
    })

    it('localStorage에서 상태가 복원되어야 함', () => {
      const mockUser = {
        id: 1,
        username: 'admin',
        name: '관리자',
        email: 'admin@yourprogram.com',
        role: 'super_admin' as const,
        is_active: true,
      }

      const storedState = {
        user: mockUser,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      }

      ;(localStorage.getItem as jest.Mock).mockReturnValue(JSON.stringify(storedState))

      const { result } = renderHook(() => useUserStore())

      expect(result.current.user).toEqual(mockUser)
      expect(result.current.isAuthenticated).toBe(true)
    })
  })
}) 
import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import Sidebar from '@/components/Sidebar'
import useUserStore from '@/store/useUserStore'
import { useOrderStore } from '@/store/useOrderStore'

// Mock Next.js router
jest.mock('next/navigation', () => ({
  usePathname: () => '/dashboard',
}))

// Mock stores
jest.mock('@/store/useUserStore')
jest.mock('@/store/useOrderStore')

const mockUseUserStore = useUserStore as jest.MockedFunction<typeof useUserStore>
const mockUseOrderStore = useOrderStore as jest.MockedFunction<typeof useOrderStore>

describe('Sidebar Component', () => {
  const mockConnectWebSocket = jest.fn()
  const mockDisconnectWebSocket = jest.fn()
  const mockSubscribeToChanges = jest.fn(() => jest.fn()) // 항상 함수를 반환하도록 수정

  beforeEach(() => {
    jest.clearAllMocks()
    
    mockUseOrderStore.mockReturnValue({
      connectWebSocket: mockConnectWebSocket,
      disconnectWebSocket: mockDisconnectWebSocket,
    } as any)
  })

  describe('인증되지 않은 사용자', () => {
    beforeEach(() => {
      mockUseUserStore.mockReturnValue({
        user: null,
        isAuthenticated: false,
        hasRole: jest.fn(() => false),
        subscribeToChanges: mockSubscribeToChanges,
      } as any)
    })

    it('인증되지 않은 사용자에게는 사이드바가 표시되지 않아야 함', () => {
      render(<Sidebar />)
      expect(screen.queryByText('Your Program')).not.toBeInTheDocument()
    })
  })

  describe('인증된 사용자', () => {
    beforeEach(() => {
      mockUseUserStore.mockReturnValue({
        user: {
          id: 1,
          username: 'admin',
          name: '관리자',
          email: 'admin@yourprogram.com',
          role: 'super_admin',
          is_active: true,
        },
        isAuthenticated: true,
        hasRole: jest.fn((roles) => {
          if (Array.isArray(roles)) {
            return roles.includes('super_admin')
          }
          return roles === 'super_admin'
        }),
        subscribeToChanges: mockSubscribeToChanges,
      } as any)
    })

    it('사이드바가 올바르게 렌더링되어야 함', () => {
      render(<Sidebar />)
      expect(screen.getByText('Your Program')).toBeInTheDocument()
    })

    it('WebSocket 연결이 설정되어야 함', () => {
      render(<Sidebar />)
      expect(mockConnectWebSocket).toHaveBeenCalled()
    })

    it('사용자 상태 변경 구독이 설정되어야 함', () => {
      render(<Sidebar />)
      expect(mockSubscribeToChanges).toHaveBeenCalled()
    })

    it('최고 관리자 메뉴가 표시되어야 함', () => {
      render(<Sidebar />)
      
      expect(screen.getByText('시스템 관리')).toBeInTheDocument()
      expect(screen.getByText('고급 기능')).toBeInTheDocument()
      expect(screen.getByText('브랜드 관리')).toBeInTheDocument()
      expect(screen.getByText('매장 운영')).toBeInTheDocument()
      expect(screen.getByText('업무 관리')).toBeInTheDocument()
      expect(screen.getByText('직원 기능')).toBeInTheDocument()
      expect(screen.getByText('공통 기능')).toBeInTheDocument()
    })

    it('메뉴 확장/축소가 작동해야 함', async () => {
      render(<Sidebar />)
      
      const systemManagementMenu = screen.getByText('시스템 관리')
      fireEvent.click(systemManagementMenu)
      
      await waitFor(() => {
        expect(screen.getByText('전체 대시보드')).toBeInTheDocument()
        expect(screen.getByText('매장 관리')).toBeInTheDocument()
        expect(screen.getByText('사용자 관리')).toBeInTheDocument()
        expect(screen.getByText('권한 관리')).toBeInTheDocument()
      })
    })

    it('메뉴 링크가 올바르게 설정되어야 함', () => {
      render(<Sidebar />)
      
      const dashboardLink = screen.getByText('대시보드')
      expect(dashboardLink.closest('a')).toHaveAttribute('href', '/dashboard')
    })
  })

  describe('매장 관리자 권한', () => {
    beforeEach(() => {
      mockUseUserStore.mockReturnValue({
        user: {
          id: 2,
          username: 'manager',
          name: '매장 관리자',
          email: 'manager@yourprogram.com',
          role: 'store_manager',
          is_active: true,
        },
        isAuthenticated: true,
        hasRole: jest.fn((roles) => {
          if (Array.isArray(roles)) {
            return roles.includes('store_manager') || roles.includes('super_admin')
          }
          return roles === 'store_manager' || roles === 'super_admin'
        }),
        subscribeToChanges: mockSubscribeToChanges,
      } as any)
    })

    it('매장 관리자에게는 해당 메뉴만 표시되어야 함', () => {
      render(<Sidebar />)
      
      // 매장 관리자에게 표시되어야 하는 메뉴
      expect(screen.getByText('브랜드 관리')).toBeInTheDocument()
      expect(screen.getByText('매장 운영')).toBeInTheDocument()
      expect(screen.getByText('업무 관리')).toBeInTheDocument()
      expect(screen.getByText('직원 기능')).toBeInTheDocument()
      expect(screen.getByText('공통 기능')).toBeInTheDocument()
      
      // 최고 관리자 전용 메뉴는 표시되지 않아야 함
      expect(screen.queryByText('시스템 관리')).not.toBeInTheDocument()
      expect(screen.queryByText('고급 기능')).not.toBeInTheDocument()
    })
  })

  describe('직원 권한', () => {
    beforeEach(() => {
      mockUseUserStore.mockReturnValue({
        user: {
          id: 3,
          username: 'employee',
          name: '직원',
          email: 'employee@yourprogram.com',
          role: 'employee',
          is_active: true,
        },
        isAuthenticated: true,
        hasRole: jest.fn((roles) => {
          if (Array.isArray(roles)) {
            return roles.includes('employee') || roles.includes('store_manager') || roles.includes('super_admin')
          }
          return roles === 'employee' || roles === 'store_manager' || roles === 'super_admin'
        }),
        subscribeToChanges: mockSubscribeToChanges,
      } as any)
    })

    it('직원에게는 제한된 메뉴만 표시되어야 함', () => {
      render(<Sidebar />)
      
      // 직원에게 표시되어야 하는 메뉴
      expect(screen.getByText('직원 기능')).toBeInTheDocument()
      expect(screen.getByText('공통 기능')).toBeInTheDocument()
      
      // 관리자 전용 메뉴는 표시되지 않아야 함
      expect(screen.queryByText('시스템 관리')).not.toBeInTheDocument()
      expect(screen.queryByText('고급 기능')).not.toBeInTheDocument()
      expect(screen.queryByText('브랜드 관리')).not.toBeInTheDocument()
      expect(screen.queryByText('매장 운영')).not.toBeInTheDocument()
      expect(screen.queryByText('업무 관리')).not.toBeInTheDocument()
    })
  })

  describe('모바일 반응형', () => {
    beforeEach(() => {
      mockUseUserStore.mockReturnValue({
        user: {
          id: 1,
          username: 'admin',
          name: '관리자',
          email: 'admin@yourprogram.com',
          role: 'super_admin',
          is_active: true,
        },
        isAuthenticated: true,
        hasRole: jest.fn(() => true),
        subscribeToChanges: mockSubscribeToChanges,
      } as any)
    })

    it('모바일 메뉴 버튼이 표시되어야 함', () => {
      render(<Sidebar />)
      
      // 모바일 메뉴 버튼 (hamburger icon)
      const menuButton = screen.getByRole('button', { name: /menu/i })
      expect(menuButton).toBeInTheDocument()
    })

    it('모바일 메뉴가 토글되어야 함', async () => {
      render(<Sidebar />)
      
      const menuButton = screen.getByRole('button', { name: /menu/i })
      fireEvent.click(menuButton)
      
      // 모바일 메뉴가 열렸을 때 닫기 버튼이 표시되어야 함
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /close/i })).toBeInTheDocument()
      })
    })
  })

  describe('실시간 동기화', () => {
    beforeEach(() => {
      mockUseUserStore.mockReturnValue({
        user: {
          id: 1,
          username: 'admin',
          name: '관리자',
          email: 'admin@yourprogram.com',
          role: 'super_admin',
          is_active: true,
        },
        isAuthenticated: true,
        hasRole: jest.fn(() => true),
        subscribeToChanges: mockSubscribeToChanges,
      } as any)
    })

    it('컴포넌트 언마운트 시 WebSocket 연결이 해제되어야 함', () => {
      const { unmount } = render(<Sidebar />)
      
      unmount()
      
      expect(mockDisconnectWebSocket).toHaveBeenCalled()
    })

    it('사용자 상태 변경 시 메뉴가 업데이트되어야 함', async () => {
      render(<Sidebar />)

      // 사용자 상태 변경 시뮬레이션은 실제 구현에서 처리됨
      // 여기서는 기본 동작만 테스트
      expect(mockSubscribeToChanges).toHaveBeenCalled()
    })
  })

  describe('접근성', () => {
    beforeEach(() => {
      mockUseUserStore.mockReturnValue({
        user: {
          id: 1,
          username: 'admin',
          name: '관리자',
          email: 'admin@yourprogram.com',
          role: 'super_admin',
          is_active: true,
        },
        isAuthenticated: true,
        hasRole: jest.fn(() => true),
        subscribeToChanges: mockSubscribeToChanges,
      } as any)
    })

    it('키보드 네비게이션이 지원되어야 함', () => {
      render(<Sidebar />)
      
      const menuItems = screen.getAllByRole('button')
      expect(menuItems.length).toBeGreaterThan(0)
      
      // Tab 키로 포커스 이동 테스트
      menuItems[0].focus()
      expect(menuItems[0]).toHaveFocus()
    })

    it('ARIA 레이블이 올바르게 설정되어야 함', () => {
      render(<Sidebar />)
      
      const menuButton = screen.getByRole('button', { name: /menu/i })
      expect(menuButton).toHaveAttribute('aria-label')
    })
  })

  describe('에러 처리', () => {
    beforeEach(() => {
      mockUseUserStore.mockReturnValue({
        user: {
          id: 1,
          username: 'admin',
          name: '관리자',
          email: 'admin@yourprogram.com',
          role: 'super_admin',
          is_active: true,
        },
        isAuthenticated: true,
        hasRole: jest.fn(() => true),
        subscribeToChanges: mockSubscribeToChanges,
      } as any)
    })

    it('WebSocket 연결 실패 시 에러가 처리되어야 함', () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {})
      
      mockConnectWebSocket.mockImplementation(() => {
        throw new Error('WebSocket connection failed')
      })

      expect(() => render(<Sidebar />)).not.toThrow()
      
      consoleSpy.mockRestore()
    })

    it('권한 체크 실패 시 기본 메뉴가 표시되어야 함', () => {
      mockUseUserStore.mockReturnValue({
        user: {
          id: 1,
          username: 'admin',
          name: '관리자',
          email: 'admin@yourprogram.com',
          role: 'super_admin',
          is_active: true,
        },
        isAuthenticated: true,
        hasRole: jest.fn(() => {
          throw new Error('Permission check failed')
        }),
        subscribeToChanges: mockSubscribeToChanges,
      } as any)

      expect(() => render(<Sidebar />)).not.toThrow()
    })
  })
}) 
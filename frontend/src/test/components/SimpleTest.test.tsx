import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'

// 간단한 테스트 컴포넌트
const TestComponent = () => {
  return (
    <div>
      <h1>테스트 컴포넌트</h1>
      <p>이것은 테스트용 컴포넌트입니다.</p>
      <button aria-label="테스트 버튼">클릭</button>
    </div>
  )
}

describe('SimpleTest', () => {
  it('컴포넌트가 올바르게 렌더링되어야 한다', () => {
    render(<TestComponent />)
    
    expect(screen.getByText('테스트 컴포넌트')).toBeInTheDocument()
    expect(screen.getByText('이것은 테스트용 컴포넌트입니다.')).toBeInTheDocument()
    expect(screen.getByRole('button')).toBeInTheDocument()
  })

  it('접근성 속성이 올바르게 설정되어야 한다', () => {
    render(<TestComponent />)
    
    const button = screen.getByRole('button')
    expect(button).toHaveAttribute('aria-label', '테스트 버튼')
  })

  it('성능 측정이 작동해야 한다', () => {
    const start = performance.now()
    
    render(<TestComponent />)
    
    const end = performance.now()
    const renderTime = end - start
    
    expect(renderTime).toBeLessThan(100) // 100ms 이하
    console.log(`렌더링 시간: ${renderTime.toFixed(2)}ms`)
  })
}) 
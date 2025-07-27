import React from 'react'
import { renderHook, act } from '@testing-library/react'
import '@testing-library/jest-dom'

// Mock custom hook
const useCounter = (initialValue = 0) => {
  const [count, setCount] = React.useState(initialValue)
  
  const increment = () => setCount(prev => prev + 1)
  const decrement = () => setCount(prev => prev - 1)
  const reset = () => setCount(initialValue)
  
  return { count, increment, decrement, reset }
}

// Mock form hook
const useForm = (initialValues: Record<string, any> = {}) => {
  const [values, setValues] = React.useState(initialValues)
  const [errors, setErrors] = React.useState<Record<string, string>>({})
  
  const handleChange = (name: string, value: any) => {
    setValues(prev => ({ ...prev, [name]: value }))
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }))
    }
  }
  
  const validate = () => {
    const newErrors: Record<string, string> = {}
    
    Object.keys(values).forEach(key => {
      if (!values[key]) {
        newErrors[key] = `${key} is required`
      }
    })
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }
  
  return { values, errors, handleChange, validate }
}

describe('Hook Tests', () => {
  test('useCounter hook works correctly', () => {
    const { result } = renderHook(() => useCounter(5))
    
    expect(result.current.count).toBe(5)
    
    act(() => {
      result.current.increment()
    })
    expect(result.current.count).toBe(6)
    
    act(() => {
      result.current.decrement()
    })
    expect(result.current.count).toBe(5)
    
    act(() => {
      result.current.reset()
    })
    expect(result.current.count).toBe(5)
  })
  
  test('useForm hook works correctly', async () => {
    const { result } = renderHook(() => useForm({ name: '', email: '' }))
    
    expect(result.current.values).toEqual({ name: '', email: '' })
    expect(result.current.errors).toEqual({})
    
    act(() => {
      result.current.handleChange('name', 'John')
    })
    expect(result.current.values.name).toBe('John')
    
    act(() => {
      result.current.handleChange('email', 'john@example.com')
    })
    expect(result.current.values.email).toBe('john@example.com')
    
    // Test validation
    act(() => {
      const isValid = result.current.validate()
      expect(isValid).toBe(true)
    })
    
    // Test validation with empty values
    act(() => {
      result.current.handleChange('name', '')
      result.current.handleChange('email', '')
    })
    
    act(() => {
      result.current.validate()
    })
    
    // Wait for state update
    await new Promise(resolve => setTimeout(resolve, 0))
    
    expect(result.current.errors.name).toBe('name is required')
    expect(result.current.errors.email).toBe('email is required')
  })
  
  test('useCounter with default value', () => {
    const { result } = renderHook(() => useCounter())
    
    expect(result.current.count).toBe(0)
    
    act(() => {
      result.current.increment()
    })
    expect(result.current.count).toBe(1)
  })
}) 
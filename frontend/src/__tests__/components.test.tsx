import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'

// Mock components
const MockComponent = () => {
  return <div data-testid="mock-component">Mock Component</div>
}

// Mock Button component
const Button = ({ children, onClick, disabled = false }: { 
  children: React.ReactNode; 
  onClick?: () => void; 
  disabled?: boolean 
}) => {
  return (
    <button 
      data-testid="button" 
      onClick={onClick} 
      disabled={disabled}
    >
      {children}
    </button>
  )
}

// Mock Card component
const Card = ({ title, children }: { 
  title: string; 
  children: React.ReactNode 
}) => {
  return (
    <div data-testid="card">
      <h3 data-testid="card-title">{title}</h3>
      <div data-testid="card-content">{children}</div>
    </div>
  )
}

describe('Component Tests', () => {
  test('renders mock component', () => {
    render(<MockComponent />)
    const element = screen.getByTestId('mock-component')
    expect(element).toBeInTheDocument()
    expect(element).toHaveTextContent('Mock Component')
  })

  test('renders button component', () => {
    render(<Button>Click me</Button>)
    const button = screen.getByTestId('button')
    expect(button).toBeInTheDocument()
    expect(button).toHaveTextContent('Click me')
    expect(button).not.toBeDisabled()
  })

  test('renders disabled button', () => {
    render(<Button disabled>Disabled Button</Button>)
    const button = screen.getByTestId('button')
    expect(button).toBeDisabled()
    expect(button).toHaveTextContent('Disabled Button')
  })

  test('renders card component', () => {
    render(
      <Card title="Test Card">
        <p>Card content</p>
      </Card>
    )
    
    const card = screen.getByTestId('card')
    const title = screen.getByTestId('card-title')
    const content = screen.getByTestId('card-content')
    
    expect(card).toBeInTheDocument()
    expect(title).toHaveTextContent('Test Card')
    expect(content).toHaveTextContent('Card content')
  })

  test('button click handler works', () => {
    const handleClick = jest.fn()
    render(<Button onClick={handleClick}>Click me</Button>)
    
    const button = screen.getByTestId('button')
    button.click()
    
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  test('basic math operations', () => {
    expect(2 + 2).toBe(4)
    expect(5 * 3).toBe(15)
    expect(10 - 3).toBe(7)
  })
}) 
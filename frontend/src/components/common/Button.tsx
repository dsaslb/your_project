import React from 'react';
import clsx from 'clsx';

interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'danger';
  [key: string]: any;
}

export const Button = ({ children, variant = 'primary', ...props }: ButtonProps) => (
  <button
    className={clsx(
      'rounded px-4 py-2 font-semibold',
      {
        'bg-blue-500 text-white hover:bg-blue-600': variant === 'primary',
        'bg-gray-500 text-white hover:bg-gray-600': variant === 'secondary',
        'bg-red-500 text-white hover:bg-red-600': variant === 'danger',
      }
    )}
    {...props}
  >
    {children}
  </button>
);

export default Button; 
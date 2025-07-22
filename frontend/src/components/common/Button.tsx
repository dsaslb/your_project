import React from 'react';
import clsx from 'clsx';

export const Button = ({ children, variant = 'primary', ...props }) => (
  <button
    className={clsx(
      'rounded px-4 py-2 font-semibold',
      variant === 'primary' && 'bg-blue-600 text-white',
      variant === 'secondary' && 'bg-gray-200 text-gray-800'
    )}
    {...props}
  >
    {children}
  </button>
);

export default Button; 
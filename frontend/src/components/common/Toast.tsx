import React from 'react';

type ToastProps = {
  message: string;
  type?: 'info' | 'success' | 'warning' | 'error';
};

const typeStyles = {
  info: 'bg-blue-100 text-blue-800',
  success: 'bg-green-100 text-green-800',
  warning: 'bg-yellow-100 text-yellow-800',
  error: 'bg-red-100 text-red-800',
};

export const Toast: React.FC<ToastProps> = ({ message, type = 'info' }) => (
  <div className={`px-4 py-2 rounded shadow ${typeStyles[type]} mb-2`}>{message}</div>
);

export default Toast; 
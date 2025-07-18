import React from 'react';

interface ToastProps {
  message: string;
  type?: 'success' | 'error' | 'info' | 'loading';
}

export const Toast: React.FC<ToastProps> = ({ message, type = 'info' }) => {
  const color =
    type === 'success' ? 'bg-green-600' :
    type === 'error' ? 'bg-red-600' :
    type === 'loading' ? 'bg-blue-600' :
    'bg-gray-800';
  return (
    <div className={`fixed bottom-6 right-6 z-50 px-4 py-2 rounded text-white shadow-lg ${color}`}
      role="status" aria-live="polite">
      {type === 'loading' && <span className="mr-2 animate-spin">⏳</span>}
      {message}
    </div>
  );
}; 
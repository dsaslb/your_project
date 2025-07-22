import React from 'react';

type ModalProps = {
  open: boolean;
  onClose: () => void;
  children: React.ReactNode;
};

export const Modal: React.FC<ModalProps> = ({ open, onClose, children }) => {
  if (!open) return null;
  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="bg-white rounded shadow-lg p-6 min-w-[300px]">
        {children}
        <button onClick={onClose} className="mt-4 px-4 py-2 bg-blue-600 text-white rounded">닫기</button>
      </div>
    </div>
  );
};

export default Modal; 
export function Modal({ open, onClose, title, children, ...props }: { open: boolean; onClose: () => void; title: string; children: React.ReactNode } & React.HTMLAttributes<HTMLDivElement>) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" aria-modal="true" role="dialog" aria-labelledby="modal-title" {...props}>
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow-lg w-full max-w-lg p-6 relative">
        <button className="absolute top-2 right-2 text-xl" onClick={onClose} aria-label="닫기">×</button>
        <h2 id="modal-title" className="text-2xl font-bold mb-4">{title}</h2>
        {children}
      </div>
    </div>
  );
} 
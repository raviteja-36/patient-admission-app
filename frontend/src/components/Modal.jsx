import { useEffect, useRef } from "react";

// Wraps the native <dialog> element: gives focus trapping and Esc-to-close for free.
export default function Modal({ title, onClose, children }) {
  const ref = useRef(null);
  useEffect(() => {
    const dlg = ref.current;
    if (dlg && !dlg.open) dlg.showModal();
  }, []);
  return (
    <dialog ref={ref} className="modal" onCancel={(e) => { e.preventDefault(); onClose(); }}
            onClick={(e) => { if (e.target === ref.current) onClose(); }} aria-label={title}>
      <div className="modal-body">
        <h2>{title}</h2>
        {children}
      </div>
    </dialog>
  );
}

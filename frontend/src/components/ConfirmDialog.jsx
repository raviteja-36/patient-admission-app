import { useState } from "react";
import Modal from "./Modal.jsx";

export default function ConfirmDialog({ patient, onCancel, onConfirm }) {
  const [busy, setBusy] = useState(false);
  return (
    <Modal title="Delete patient record?" onClose={onCancel}>
      <p>
        <strong>{patient.name}</strong> will be permanently removed. This cannot be undone.
      </p>
      <div className="actions">
        <button className="btn" onClick={onCancel} disabled={busy}>Keep record</button>
        <button className="btn danger" disabled={busy}
                onClick={async () => { setBusy(true); await onConfirm(); }}>
          {busy ? "Deleting…" : "Delete patient"}
        </button>
      </div>
    </Modal>
  );
}

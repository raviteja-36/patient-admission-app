import { useState } from "react";
import Modal from "./Modal.jsx";
import { api } from "../api";
import { todayLocal, validatePatient } from "../validation";

const EMPTY = {
  name: "", age: "", gender: "", ward: "", department: "", doctor: "",
  admission_date: todayLocal(), status: "Admitted",
};

export default function PatientForm({ options, patient, onClose, onSaved }) {
  const editing = Boolean(patient);
  const [values, setValues] = useState(editing ? { ...patient } : EMPTY);
  const [errors, setErrors] = useState({});
  const [formError, setFormError] = useState("");
  const [saving, setSaving] = useState(false);

  const set = (k) => (e) => setValues((v) => ({ ...v, [k]: e.target.value }));

  async function submit(e) {
    e.preventDefault();
    setFormError("");
    const found = validatePatient(values);
    setErrors(found);
    if (Object.keys(found).length) return;

    setSaving(true);
    try {
      const body = { ...values, name: values.name.trim(), age: Number(values.age) };
      const saved = editing ? await api.update(patient.id, body) : await api.create(body);
      onSaved(saved, editing);
    } catch (err) {
      setErrors(err.fieldErrors || {});   // show the backend's per-field messages
      setFormError(err.message);
      setSaving(false);
    }
  }

  const select = (key, label, list) => (
    <Field label={label} error={errors[key]}>
      <select value={values[key]} onChange={set(key)} aria-invalid={!!errors[key]}>
        <option value="">Select {label.toLowerCase()}</option>
        {list.map((o) => <option key={o} value={o}>{o}</option>)}
      </select>
    </Field>
  );

  return (
    <Modal title={editing ? "Edit patient" : "Add patient"} onClose={onClose}>
      <form onSubmit={submit} noValidate>
        <div className="form-grid">
          <Field label="Full name" error={errors.name} wide>
            <input value={values.name} onChange={set("name")} autoComplete="off" aria-invalid={!!errors.name} />
          </Field>
          <Field label="Age" error={errors.age}>
            <input type="number" inputMode="numeric" min="0" max="120" value={values.age}
                   onChange={set("age")} aria-invalid={!!errors.age} />
          </Field>
          {select("gender", "Gender", options.genders)}
          {select("ward", "Ward", options.wards)}
          {select("department", "Department", options.departments)}
          {select("doctor", "Doctor", options.doctors)}
          <Field label="Admission date" error={errors.admission_date}>
            <input type="date" max={todayLocal()} value={values.admission_date}
                   onChange={set("admission_date")} aria-invalid={!!errors.admission_date} />
          </Field>
          {select("status", "Status", options.statuses)}
        </div>
        {formError && <p className="form-error" role="alert">{formError}</p>}
        <div className="actions">
          <button type="button" className="btn" onClick={onClose} disabled={saving}>Cancel</button>
          <button type="submit" className="btn primary" disabled={saving}>
            {saving ? "Saving…" : editing ? "Save changes" : "Add patient"}
          </button>
        </div>
      </form>
    </Modal>
  );
}

function Field({ label, error, wide, children }) {
  return (
    <label className={`field${wide ? " wide" : ""}`}>
      <span>{label}</span>
      {children}
      {error && <small className="error">{error}</small>}
    </label>
  );
}

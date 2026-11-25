import { useCallback, useEffect, useState } from "react";
import { api } from "./api";
import Filters from "./components/Filters.jsx";
import PatientList from "./components/PatientList.jsx";
import PatientForm from "./components/PatientForm.jsx";
import ConfirmDialog from "./components/ConfirmDialog.jsx";

const NO_FILTERS = { search: "", ward: "", department: "", doctor: "" };

export default function App() {
  const [options, setOptions] = useState(null);
  const [patients, setPatients] = useState([]);
  const [filters, setFilters] = useState(NO_FILTERS);
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [form, setForm] = useState(null);       // null | {patient: obj|null}
  const [toDelete, setToDelete] = useState(null);
  const [toast, setToast] = useState("");

  const notify = (msg) => { setToast(msg); setTimeout(() => setToast(""), 3000); };

  // Wait 300 ms after typing stops before searching, so we don't call the API on every keystroke.
  useEffect(() => {
    const t = setTimeout(() => setDebouncedSearch(filters.search), 300);
    return () => clearTimeout(t);
  }, [filters.search]);

  useEffect(() => {
    api.options().then(setOptions).catch((e) => setError(e.message));
  }, []);

  const load = useCallback(async () => {
    try {
      setError("");
      setPatients(await api.list({ ...filters, search: debouncedSearch }));
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [filters.ward, filters.department, filters.doctor, debouncedSearch]); // eslint-disable-line

  useEffect(() => { load(); }, [load]);

  async function discharge(p) {
    try { await api.discharge(p.id); notify(`${p.name} discharged`); load(); }
    catch (e) { setError(e.message); }
  }

  async function confirmDelete() {
    try { await api.remove(toDelete.id); notify(`${toDelete.name} deleted`); load(); }
    catch (e) { setError(e.message); }
    setToDelete(null);
  }

  const admitted = patients.filter((p) => p.status === "Admitted").length;

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <h1>Patient admissions</h1>
          <p className="tally">
            {patients.length} {patients.length === 1 ? "patient" : "patients"} shown ·{" "}
            {admitted} admitted · {patients.length - admitted} discharged
          </p>
        </div>
        <button className="btn primary" disabled={!options} onClick={() => setForm({ patient: null })}>
          Add patient
        </button>
      </header>

      {options && (
        <Filters options={options} filters={filters} onChange={setFilters}
                 onClear={() => setFilters(NO_FILTERS)} />
      )}

      {error && <div className="banner" role="alert">{error}</div>}

      <main>
        {loading ? (
          <p className="empty">Loading patients…</p>
        ) : patients.length === 0 ? (
          <p className="empty">
            {Object.values(filters).some(Boolean)
              ? "No patients match these filters. Try clearing them."
              : "No patients admitted yet. Use “Add patient” to create the first record."}
          </p>
        ) : (
          <PatientList patients={patients} onEdit={(p) => setForm({ patient: p })}
                       onDischarge={discharge} onDelete={setToDelete} />
        )}
      </main>

      {form && (
        <PatientForm options={options} patient={form.patient} onClose={() => setForm(null)}
                     onSaved={(saved, wasEdit) => {
                       setForm(null);
                       notify(wasEdit ? "Changes saved" : `${saved.name} admitted`);
                       load();
                     }} />
      )}
      {toDelete && (
        <ConfirmDialog patient={toDelete} onCancel={() => setToDelete(null)} onConfirm={confirmDelete} />
      )}
      {toast && <div className="toast" role="status">{toast}</div>}
    </div>
  );
}

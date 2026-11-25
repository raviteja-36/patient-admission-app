// Mirrors the backend rules so users get instant feedback. The backend re-checks everything.
export function todayLocal() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

export function validatePatient(v) {
  const e = {};
  const name = v.name.trim().replace(/\s+/g, " ");
  if (!name) e.name = "Name is required";
  else if (!/^[A-Za-z]+( [A-Za-z]+)*$/.test(name)) e.name = "Name can contain letters and spaces only";

  if (v.age === "" || v.age === null) e.age = "Age is required";
  else if (!Number.isInteger(Number(v.age))) e.age = "Age must be a whole number";
  else if (Number(v.age) < 0 || Number(v.age) > 120) e.age = "Age must be between 0 and 120";

  [["gender", "Gender"], ["ward", "Ward"], ["department", "Department"], ["doctor", "Doctor"]].forEach(
    ([k, label]) => { if (!v[k]) e[k] = `${label} is required`; }
  );

  if (!v.admission_date) e.admission_date = "Admission date is required";
  else if (v.admission_date > todayLocal()) e.admission_date = "Admission date cannot be in the future";
  return e;
}

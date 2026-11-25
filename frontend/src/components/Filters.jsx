export default function Filters({ options, filters, onChange, onClear }) {
  const set = (k) => (e) => onChange({ ...filters, [k]: e.target.value });
  const select = (key, label, list) => (
    <select value={filters[key]} onChange={set(key)} aria-label={`Filter by ${label.toLowerCase()}`}>
      <option value="">All {label.toLowerCase()}s</option>
      {list.map((o) => <option key={o} value={o}>{o}</option>)}
    </select>
  );
  const active = Object.values(filters).some(Boolean);

  return (
    <section className="filters" aria-label="Search and filter">
      <input type="search" className="search" placeholder="Search patients by name"
             value={filters.search} onChange={set("search")} aria-label="Search patients by name" />
      {select("ward", "Ward", options.wards)}
      {select("department", "Department", options.departments)}
      {select("doctor", "Doctor", options.doctors)}
      <button className="btn" onClick={onClear} disabled={!active}>Clear filters</button>
    </section>
  );
}

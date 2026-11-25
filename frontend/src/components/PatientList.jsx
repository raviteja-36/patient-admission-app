function fmtDate(d) {
  return new Date(`${d}T00:00:00`).toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" });
}

function StatusPill({ status }) {
  return <span className={`pill ${status === "Admitted" ? "in" : "out"}`}>{status}</span>;
}

function Actions({ p, onEdit, onDischarge, onDelete }) {
  return (
    <div className="row-actions">
      {p.status === "Admitted" && (
        <button className="btn small" onClick={() => onDischarge(p)}>Discharge</button>
      )}
      <button className="btn small" onClick={() => onEdit(p)}>Edit</button>
      <button className="btn small danger-ghost" onClick={() => onDelete(p)}>Delete</button>
    </div>
  );
}

export default function PatientList({ patients, ...handlers }) {
  return (
    <>
      {/* Table: tablet and desktop */}
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Patient</th><th>Ward</th><th>Department</th><th>Doctor</th>
              <th>Admitted on</th><th>Status</th><th><span className="sr-only">Actions</span></th>
            </tr>
          </thead>
          <tbody>
            {patients.map((p) => (
              <tr key={p.id} className={p.status === "Discharged" ? "muted" : ""}>
                <td><strong>{p.name}</strong><div className="sub">{p.age} yrs · {p.gender}</div></td>
                <td>{p.ward}</td>
                <td>{p.department}</td>
                <td>{p.doctor}</td>
                <td>{fmtDate(p.admission_date)}</td>
                <td><StatusPill status={p.status} /></td>
                <td><Actions p={p} {...handlers} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Cards: mobile */}
      <ul className="cards">
        {patients.map((p) => (
          <li key={p.id} className={`card${p.status === "Discharged" ? " muted" : ""}`}>
            <div className="card-head">
              <div><strong>{p.name}</strong><div className="sub">{p.age} yrs · {p.gender}</div></div>
              <StatusPill status={p.status} />
            </div>
            <dl>
              <div><dt>Ward</dt><dd>{p.ward}</dd></div>
              <div><dt>Department</dt><dd>{p.department}</dd></div>
              <div><dt>Doctor</dt><dd>{p.doctor}</dd></div>
              <div><dt>Admitted on</dt><dd>{fmtDate(p.admission_date)}</dd></div>
            </dl>
            <Actions p={p} {...handlers} />
          </li>
        ))}
      </ul>
    </>
  );
}

export default function ReadingsTable({ readings = [], onDelete }) {
  if (readings.length === 0) {
    return <p className="text-secondary">No readings logged yet.</p>;
  }

  return (
    <div className="table-wrap">
      <table className="data-table">
        <thead>
          <tr>
            <th>Recorded</th>
            <th>TDS (ppm)</th>
            <th>pH</th>
            <th>Turbidity (NTU)</th>
            <th>Flow (L/min)</th>
            <th>Pressure (bar)</th>
            <th>Usage (L/day)</th>
            {onDelete ? <th aria-label="Actions" /> : null}
          </tr>
        </thead>
        <tbody>
          {[...readings].reverse().map((r) => (
            <tr key={r.id}>
              <td className="text-secondary">
                {new Date(r.recorded_at).toLocaleString(undefined, {
                  month: "short",
                  day: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </td>
              <td className="mono">{r.tds_ppm.toFixed(1)}</td>
              <td className="mono">{r.ph.toFixed(2)}</td>
              <td className="mono">{r.turbidity_ntu.toFixed(2)}</td>
              <td className="mono">{r.flow_rate_lpm.toFixed(2)}</td>
              <td className="mono">{r.pressure_bar.toFixed(2)}</td>
              <td className="mono">{r.daily_usage_liters.toFixed(0)}</td>
              {onDelete ? (
                <td>
                  <button className="link-button" onClick={() => onDelete(r.id)}>
                    Remove
                  </button>
                </td>
              ) : null}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

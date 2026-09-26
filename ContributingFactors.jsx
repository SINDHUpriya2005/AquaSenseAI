export default function ContributingFactors({ factors = {} }) {
  const entries = Object.entries(factors).sort((a, b) => b[1] - a[1]);

  if (entries.length === 0) {
    return <p className="text-secondary">No breakdown available yet.</p>;
  }

  return (
    <div className="factor-list">
      {entries.map(([label, weight]) => (
        <div className="factor-row" key={label}>
          <div className="factor-row__top">
            <span>{label}</span>
            <span className="mono text-secondary">{Math.round(weight * 100)}%</span>
          </div>
          <div className="factor-row__track">
            <div className="factor-row__fill" style={{ width: `${Math.max(weight * 100, 2)}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}

export default function KpiCard({ label, value, unit, tone = "neutral", icon: Icon, trend }) {
  return (
    <div className={`kpi-card kpi-card--${tone}`}>
      <div className="kpi-card__icon">{Icon ? <Icon width={18} height={18} /> : null}</div>
      <div className="kpi-card__label">{label}</div>
      <div className="kpi-card__value">
        <span className="mono">{value}</span>
        {unit ? <span className="kpi-card__unit">{unit}</span> : null}
      </div>
      {trend ? <div className="kpi-card__trend text-secondary">{trend}</div> : null}
    </div>
  );
}

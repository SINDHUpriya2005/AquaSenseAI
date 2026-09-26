function statusFor(key, value) {
  const ranges = {
    tds_ppm: { good: 50, watch: 100 },
    ph: null,
    turbidity_ntu: { good: 1, watch: 3 },
    flow_rate_lpm: { good: 1.6, watch: 1.0, invert: true },
    pressure_bar: { good: 2.6, watch: 3.4 },
  };

  if (key === "ph") {
    const dev = Math.abs(value - 7.2);
    if (dev < 0.4) return "good";
    if (dev < 0.8) return "watch";
    return "bad";
  }

  const range = ranges[key];
  if (!range) return "good";

  if (range.invert) {
    if (value >= range.good) return "good";
    if (value >= range.watch) return "watch";
    return "bad";
  }

  if (value <= range.good) return "good";
  if (value <= range.watch) return "watch";
  return "bad";
}

export default function WaterQualityMetric({ label, value, unit, metricKey, precision = 1 }) {
  const status = statusFor(metricKey, value);
  return (
    <div className={`metric-tile metric-tile--${status}`}>
      <div className="metric-tile__label">{label}</div>
      <div className="metric-tile__value mono">
        {typeof value === "number" ? value.toFixed(precision) : "--"}
        <span className="metric-tile__unit">{unit}</span>
      </div>
    </div>
  );
}

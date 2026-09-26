const TONE_COLORS = {
  ok: "var(--accent-lime)",
  watch: "var(--accent-blue)",
  warning: "var(--accent-amber)",
  critical: "var(--accent-coral)",
};

const TONE_LABELS = {
  ok: "Healthy",
  watch: "Monitor",
  warning: "Needs attention",
  critical: "Critical",
};

export default function HealthGauge({ score = 0, alertLevel = "ok", size = 220 }) {
  const strokeWidth = size * 0.09;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const clamped = Math.max(0, Math.min(100, score));
  const dashOffset = circumference * (1 - clamped / 100);
  const color = TONE_COLORS[alertLevel] || TONE_COLORS.ok;

  return (
    <div className="health-gauge" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="var(--border-subtle)"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={dashOffset}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          style={{ transition: "stroke-dashoffset 0.6s ease, stroke 0.3s ease" }}
        />
      </svg>
      <div className="health-gauge__center">
        <div className="health-gauge__score mono">{Math.round(clamped)}</div>
        <div className="health-gauge__max text-muted">/ 100</div>
        <div className="health-gauge__label" style={{ color }}>
          {TONE_LABELS[alertLevel] || TONE_LABELS.ok}
        </div>
      </div>
    </div>
  );
}

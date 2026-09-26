const CONFIG = {
  ok: { label: "Healthy", tone: "ok" },
  watch: { label: "Monitor", tone: "watch" },
  warning: { label: "Warning", tone: "warning" },
  critical: { label: "Critical", tone: "critical" },
};

export default function StatusPill({ level }) {
  const conf = CONFIG[level] || CONFIG.ok;
  return <span className={`status-pill status-pill--${conf.tone}`}>{conf.label}</span>;
}

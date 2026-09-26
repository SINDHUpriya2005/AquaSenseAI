import { IconAlert, IconCheck } from "./Icons";

export default function AlertBanner({ level, message }) {
  if (!level || level === "ok") {
    return (
      <div className="alert-banner alert-banner--ok">
        <IconCheck width={18} height={18} />
        <span>{message || "This filter is operating within its healthy range."}</span>
      </div>
    );
  }

  return (
    <div className={`alert-banner alert-banner--${level}`}>
      <IconAlert width={18} height={18} />
      <span>{message}</span>
    </div>
  );
}

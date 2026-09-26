import { IconDroplet } from "./Icons";

export default function EmptyState({ title, description, actionLabel, onAction }) {
  return (
    <div className="empty-state">
      <span className="empty-state__icon">
        <IconDroplet width={26} height={26} />
      </span>
      <h3>{title}</h3>
      <p className="text-secondary">{description}</p>
      {actionLabel ? (
        <button className="btn btn--primary" onClick={onAction}>
          {actionLabel}
        </button>
      ) : null}
    </div>
  );
}

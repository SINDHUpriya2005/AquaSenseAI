import StatusPill from "./StatusPill";
import { IconWrench } from "./Icons";

export default function PurifierCard({ purifier, summary, onReplaceFilter, onEdit, onDelete }) {
  const daysSinceChange = summary?.days_since_filter_change;

  return (
    <div className="purifier-card">
      <div className="purifier-card__header">
        <div>
          <h3>{purifier.name}</h3>
          <p className="text-secondary">
            {purifier.model} &middot; {purifier.filter_type}
          </p>
        </div>
        {summary?.alert_level ? <StatusPill level={summary.alert_level} /> : null}
      </div>

      <div className="purifier-card__stats">
        <div>
          <div className="text-muted">Health score</div>
          <div className="mono purifier-card__stat-value">
            {summary?.latest_health_score != null ? Math.round(summary.latest_health_score) : "--"}
          </div>
        </div>
        <div>
          <div className="text-muted">Remaining life</div>
          <div className="mono purifier-card__stat-value">
            {summary?.latest_remaining_life_days != null
              ? `${Math.round(summary.latest_remaining_life_days)}d`
              : "--"}
          </div>
        </div>
        <div>
          <div className="text-muted">Filter age</div>
          <div className="mono purifier-card__stat-value">
            {daysSinceChange != null ? `${daysSinceChange}d` : "--"}
          </div>
        </div>
      </div>

      {purifier.location ? <p className="text-secondary purifier-card__location">{purifier.location}</p> : null}

      <div className="purifier-card__actions">
        <button className="btn btn--ghost btn--sm" onClick={() => onReplaceFilter(purifier.id)}>
          <IconWrench width={15} height={15} />
          Log filter change
        </button>
        <button className="btn btn--ghost btn--sm" onClick={() => onEdit(purifier)}>
          Edit
        </button>
        <button className="btn btn--ghost btn--sm btn--danger" onClick={() => onDelete(purifier.id)}>
          Delete
        </button>
      </div>
    </div>
  );
}

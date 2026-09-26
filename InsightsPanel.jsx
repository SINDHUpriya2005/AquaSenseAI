export default function InsightsPanel({ insights = [] }) {
  return (
    <div className="panel">
      <div className="panel__header">
        <h3>AI maintenance insights</h3>
        <span className="text-muted">Generated from the latest reading</span>
      </div>
      {insights.length === 0 ? (
        <p className="text-secondary">Run a prediction to generate insights for this purifier.</p>
      ) : (
        <ul className="insight-list">
          {insights.map((insight, idx) => (
            <li key={idx}>{insight}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

import { useState } from "react";

const emptyForm = {
  tds_ppm: 45,
  ph: 7.1,
  turbidity_ntu: 0.8,
  flow_rate_lpm: 1.8,
  pressure_bar: 2.4,
  daily_usage_liters: 25,
  usage_frequency_per_day: 10,
  water_temperature_c: 25,
};

export default function ReadingForm({ purifierId, onSubmit, onCancel }) {
  const [form, setForm] = useState(emptyForm);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const update = (field) => (e) => {
    setForm((f) => ({ ...f, [field]: Number(e.target.value) }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await onSubmit({ ...form, purifier_id: purifierId });
    } catch (err) {
      setError(err?.response?.data?.detail || "Could not save this reading.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form className="form" onSubmit={handleSubmit}>
      {error ? <div className="form__error">{error}</div> : null}

      <div className="field-row">
        <label className="field">
          <span>TDS (ppm)</span>
          <input type="number" step="0.1" value={form.tds_ppm} onChange={update("tds_ppm")} required />
        </label>
        <label className="field">
          <span>pH</span>
          <input type="number" step="0.01" min="0" max="14" value={form.ph} onChange={update("ph")} required />
        </label>
      </div>

      <div className="field-row">
        <label className="field">
          <span>Turbidity (NTU)</span>
          <input
            type="number"
            step="0.01"
            value={form.turbidity_ntu}
            onChange={update("turbidity_ntu")}
            required
          />
        </label>
        <label className="field">
          <span>Flow rate (L/min)</span>
          <input
            type="number"
            step="0.01"
            value={form.flow_rate_lpm}
            onChange={update("flow_rate_lpm")}
            required
          />
        </label>
      </div>

      <div className="field-row">
        <label className="field">
          <span>Pressure (bar)</span>
          <input type="number" step="0.01" value={form.pressure_bar} onChange={update("pressure_bar")} required />
        </label>
        <label className="field">
          <span>Water temp (°C)</span>
          <input
            type="number"
            step="0.1"
            value={form.water_temperature_c}
            onChange={update("water_temperature_c")}
          />
        </label>
      </div>

      <div className="field-row">
        <label className="field">
          <span>Daily usage (liters)</span>
          <input
            type="number"
            step="0.1"
            value={form.daily_usage_liters}
            onChange={update("daily_usage_liters")}
            required
          />
        </label>
        <label className="field">
          <span>Uses per day</span>
          <input
            type="number"
            step="1"
            value={form.usage_frequency_per_day}
            onChange={update("usage_frequency_per_day")}
            required
          />
        </label>
      </div>

      <div className="form__actions">
        <button type="button" className="btn btn--ghost" onClick={onCancel}>
          Cancel
        </button>
        <button type="submit" className="btn btn--primary" disabled={submitting}>
          {submitting ? "Saving..." : "Save reading"}
        </button>
      </div>
    </form>
  );
}

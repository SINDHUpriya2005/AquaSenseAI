import { useState } from "react";

const FILTER_TYPES = ["RO", "UF", "RO+UF", "Activated Carbon", "UV"];

const emptyForm = {
  name: "",
  model: "",
  filter_type: "RO+UF",
  location: "",
  installation_date: new Date().toISOString().slice(0, 10),
  rated_filter_life_days: 180,
  rated_capacity_liters: 6000,
};

export default function PurifierForm({ initial, onSubmit, onCancel, submitLabel = "Save purifier" }) {
  const [form, setForm] = useState(initial ? { ...emptyForm, ...initial } : emptyForm);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const update = (field) => (e) => {
    const value = e.target.type === "number" ? Number(e.target.value) : e.target.value;
    setForm((f) => ({ ...f, [field]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await onSubmit(form);
    } catch (err) {
      setError(err?.response?.data?.detail || "Could not save this purifier.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form className="form" onSubmit={handleSubmit}>
      {error ? <div className="form__error">{error}</div> : null}

      <label className="field">
        <span>Purifier name</span>
        <input value={form.name} onChange={update("name")} placeholder="Kitchen RO Purifier" required />
      </label>

      <label className="field">
        <span>Model</span>
        <input value={form.model} onChange={update("model")} placeholder="AquaPure X7" required />
      </label>

      <div className="field-row">
        <label className="field">
          <span>Filter type</span>
          <select value={form.filter_type} onChange={update("filter_type")}>
            {FILTER_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </label>

        <label className="field">
          <span>Location</span>
          <input value={form.location || ""} onChange={update("location")} placeholder="Kitchen counter" />
        </label>
      </div>

      <div className="field-row">
        <label className="field">
          <span>Installed on</span>
          <input
            type="date"
            value={String(form.installation_date).slice(0, 10)}
            onChange={update("installation_date")}
            required
          />
        </label>

        <label className="field">
          <span>Rated filter life (days)</span>
          <input
            type="number"
            min={30}
            value={form.rated_filter_life_days}
            onChange={update("rated_filter_life_days")}
            required
          />
        </label>
      </div>

      <label className="field">
        <span>Rated capacity (liters)</span>
        <input
          type="number"
          min={100}
          value={form.rated_capacity_liters}
          onChange={update("rated_capacity_liters")}
          required
        />
      </label>

      <div className="form__actions">
        <button type="button" className="btn btn--ghost" onClick={onCancel}>
          Cancel
        </button>
        <button type="submit" className="btn btn--primary" disabled={submitting}>
          {submitting ? "Saving..." : submitLabel}
        </button>
      </div>
    </form>
  );
}


import { useEffect, useState } from "react";
import "./App.css";

type Incident = {
  id: number;
  service_name: string;
  severity: string;
  status: string;
  description: string;
  created_at: string;
  resolved_at: string | null;
};

const API_URL = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

function App() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [serviceName, setServiceName] = useState("");
  const [severity, setSeverity] = useState("medium");
  const [description, setDescription] = useState("");
  const [creating, setCreating] = useState(false);
  const [formMessage, setFormMessage] = useState("");
  const [resolvingId, setResolvingId] = useState<number | null>(null);
  const [resolveError, setResolveError] = useState("");

  async function loadIncidents() {
    try {
      setError("");

      const response = await fetch(`${API_URL}/incidents`);

      if (!response.ok) {
        throw new Error("Could not load incidents");
      }

      const data: Incident[] = await response.json();
      setIncidents(data);
    } catch {
      setError(
        "Unable to connect to PulseMesh API. Is the backend running?"
      );
    } finally {
      setLoading(false);
    }
  }

  async function createIncident(
    event: React.FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();
    setCreating(true);
    setFormMessage("");

    try {
      const response = await fetch(`${API_URL}/incidents`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          service_name: serviceName.trim(),
          severity,
          description: description.trim(),
        }),
      });

      if (!response.ok) {
        const result = await response.json();

        throw new Error(
          typeof result.detail === "string"
            ? result.detail
            : "Could not create incident"
        );
      }

      setServiceName("");
      setSeverity("medium");
      setDescription("");
      setFormMessage("Incident created successfully!");

      await loadIncidents();
    } catch (err) {
      setFormMessage(
        err instanceof Error
          ? err.message
          : "Could not create incident"
      );
    } finally {
      setCreating(false);
    }
  }

  async function resolveIncident(incidentId: number) {
    if (resolvingId !== null) return;

    setResolvingId(incidentId);
    setResolveError("");

    try {
      const response = await fetch(
        `${API_URL}/incidents/${incidentId}/resolve`,
        { method: "PATCH" }
      );

      if (!response.ok) {
        const result = await response.json().catch(() => null);

        throw new Error(
          typeof result?.detail === "string"
            ? result.detail
            : `Could not resolve incident #${incidentId}`
        );
      }

      // Update the incident immediately using the API response.
      const updatedIncident: Incident = await response.json();

      setIncidents((current) =>
        current.map((incident) =>
          incident.id === updatedIncident.id
            ? updatedIncident
            : incident
        )
      );

      // Refresh from the database to ensure the dashboard is current.
      await loadIncidents();
    } catch (err) {
      setResolveError(
        err instanceof Error
          ? err.message
          : "Could not resolve incident. Please try again."
      );
    } finally {
      setResolvingId(null);
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void loadIncidents();

    const timer = setInterval(() => {
      void loadIncidents();
    }, 10000);

    return () => clearInterval(timer);
  }, []);

  const openCount = incidents.filter(
    (incident) => incident.status === "open"
  ).length;

  const highCount = incidents.filter(
    (incident) =>
      incident.severity.toLowerCase() === "high" &&
      incident.status === "open"
  ).length;

  return (
    <main className="dashboard">
      <header className="topbar">
        <div className="brand">
          <div className="brand-icon">P</div>
          <div>
            <h1>PulseMesh</h1>
            <p>Incident Management Platform</p>
          </div>
        </div>

        <div className="live">
          <span /> Live monitoring
        </div>
      </header>

      <section className="welcome">
        <div>
          <p className="eyebrow">OVERVIEW</p>
          <h2>Incident Dashboard</h2>
          <p className="subheading">
            Monitor service health and manage incidents.
          </p>
        </div>

        <button className="refresh" onClick={() => void loadIncidents()}>
          ↻ Refresh
        </button>
      </section>

      <section className="stats">
        <article className="stat-card">
          <span className="stat-label">Total incidents</span>
          <strong>{incidents.length}</strong>
          <span className="stat-note">All recorded incidents</span>
        </article>

        <article className="stat-card">
          <span className="stat-label">Open incidents</span>
          <strong>{openCount}</strong>
          <span className="stat-note">Awaiting resolution</span>
        </article>

        <article className="stat-card">
          <span className="stat-label">High severity</span>
          <strong className="high-number">{highCount}</strong>
          <span className="stat-note">
            Open high-severity incidents
          </span>
        </article>
      </section>

      <section className="create-panel">
        <div className="panel-heading">
          <div>
            <h3>Create an incident</h3>
            <p>Report a service issue</p>
          </div>
        </div>

        <form className="incident-form" onSubmit={createIncident}>
          <label>
            Service name
            <input
              value={serviceName}
              onChange={(e) => setServiceName(e.target.value)}
              placeholder="e.g. payment-service"
              maxLength={100}
              required
            />
          </label>

          <label>
            Severity
            <select
              value={severity}
              onChange={(e) => setSeverity(e.target.value)}
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </label>

          <label className="description-field">
            Description
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe what happened..."
              required
              rows={3}
            />
          </label>

          <div className="form-actions">
            <button
              className="refresh"
              type="submit"
              disabled={creating}
            >
              {creating ? "Creating..." : "+ Create incident"}
            </button>

            {formMessage && (
              <span className="form-message">{formMessage}</span>
            )}
          </div>
        </form>
      </section>

      <section className="incidents-panel">
        <div className="panel-heading">
          <div>
            <h3>Recent incidents</h3>
            <p>Latest events from your services</p>
          </div>

          <span className="count">
            {incidents.length} records
          </span>
        </div>

        {resolveError && (
          <p className="message error" role="alert">
            {resolveError}
          </p>
        )}

        {loading ? (
          <p className="message">Loading incidents…</p>
        ) : error ? (
          <p className="message error">{error}</p>
        ) : incidents.length === 0 ? (
          <p className="message">No incidents recorded yet.</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>INCIDENT</th>
                  <th>SERVICE</th>
                  <th>SEVERITY</th>
                  <th>STATUS</th>
                  <th>CREATED</th>
                  <th>ACTION</th>
                </tr>
              </thead>

              <tbody>
                {incidents.map((incident) => (
                  <tr key={incident.id}>
                    <td className="incident-id">
                      #{incident.id}
                    </td>

                    <td>
                      <strong>{incident.service_name}</strong>
                      <span className="description">
                        {incident.description}
                      </span>
                    </td>

                    <td>
                      <span
                        className={`badge ${incident.severity.toLowerCase()}`}
                      >
                        {incident.severity}
                      </span>
                    </td>

                    <td>
                      <span
                        className={`status ${incident.status.toLowerCase()}`}
                      >
                        {incident.status}
                      </span>
                    </td>

                    <td className="date">
                      {new Date(
                        incident.created_at
                      ).toLocaleString()}
                    </td>

                    <td>
                      {incident.status === "open" ? (
                        <button
                          className="refresh"
                          type="button"
                          disabled={resolvingId !== null}
                          onClick={() =>
                            void resolveIncident(incident.id)
                          }
                        >
                          {resolvingId === incident.id
                            ? "Resolving..."
                            : "Resolve"}
                        </button>
                      ) : (
                        <span className="status resolved">
                          Resolved
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <footer>
        PulseMesh · Event-driven incident monitoring
      </footer>
    </main>
  );
}

export default App;

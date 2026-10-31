
import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:8010/api/system";

function StatCard({ title, value, detail, percent }) {
  return (
    <div className="monitor-card">
      <span className="monitor-card-label">{title}</span>
      <strong className="monitor-card-value">{value}</strong>
      <div className="monitor-progress">
        <div
          className="monitor-progress-fill"
          style={{ width: `${Math.min(100, Math.max(0, percent || 0))}%` }}
        />
      </div>
      <small>{detail}</small>
    </div>
  );
}

export default function SystemMonitor() {
  const [system, setSystem] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const loadSystem = async () => {
    try {
      const response = await fetch(API_URL);

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const data = await response.json();
      setSystem(data);
      setError("");
    } catch (err) {
      setError("Cannot connect to Nexa backend. Check whether the backend is running on port 8010.");
      console.error("System monitor error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSystem();

    const timer = window.setInterval(loadSystem, 3000);

    return () => window.clearInterval(timer);
  }, []);

  if (loading) {
    return <div className="monitor-message">Loading system information...</div>;
  }

  if (error && !system) {
    return (
      <div className="monitor-message">
        <p>{error}</p>
        <button onClick={loadSystem}>Retry</button>
      </div>
    );
  }

  if (!system) return null;

  const battery = system.battery;

  return (
    <section className="system-monitor">
      <div className="monitor-heading">
        <div>
          <span className="eyebrow">NEXA DESKTOP TOOLS</span>
          <h1>System Monitor</h1>
          <p>Live performance information from your computer.</p>
        </div>

        <button className="monitor-refresh" onClick={loadSystem}>
          ↻ Refresh
        </button>
      </div>

      {error && <p className="monitor-warning">{error} Showing last available data.</p>}

      <div className="monitor-grid">
        <StatCard
          title="CPU Usage"
          value={`${system.cpu_percent}%`}
          detail="Processor utilization"
          percent={system.cpu_percent}
        />

        <StatCard
          title="RAM Usage"
          value={`${system.ram.percent}%`}
          detail={`${system.ram.used_gb} GB used of ${system.ram.total_gb} GB`}
          percent={system.ram.percent}
        />

        <StatCard
          title="Disk Usage (C:)"
          value={`${system.disk.percent}%`}
          detail={`${system.disk.free_gb} GB free of ${system.disk.total_gb} GB`}
          percent={system.disk.percent}
        />

        <div className="monitor-card">
          <span className="monitor-card-label">Battery</span>
          <strong className="monitor-card-value">
            {battery.percent == null ? "Unavailable" : `${battery.percent}%`}
          </strong>
          <div className="monitor-progress">
            <div
              className="monitor-progress-fill"
              style={{ width: `${battery.percent ?? 0}%` }}
            />
          </div>
          <small>
            {battery.percent == null
              ? "Battery information unavailable"
              : battery.plugged_in
                ? "Plugged in / Charging"
                : "Running on battery"}
          </small>
        </div>
      </div>

      <div className="monitor-details">
        <h2>Computer Information</h2>

        <div className="monitor-detail-row">
          <span>Operating System</span>
          <strong>{system.system.operating_system}</strong>
        </div>

        <div className="monitor-detail-row">
          <span>OS Version</span>
          <strong>{system.system.version}</strong>
        </div>

        <div className="monitor-detail-row">
          <span>Processor</span>
          <strong>{system.system.processor}</strong>
        </div>

        <div className="monitor-detail-row">
          <span>Available RAM</span>
          <strong>{system.ram.available_gb} GB</strong>
        </div>
      </div>

      <p className="monitor-updated">
        Automatically refreshes every 3 seconds.
      </p>
    </section>
  );
}

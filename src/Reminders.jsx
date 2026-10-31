
import { useCallback, useEffect, useState } from "react";

const API = "http://127.0.0.1:8010/api";

function Reminders() {
  const [reminders, setReminders] = useState([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [remindAt, setRemindAt] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const loadReminders = useCallback(async () => {
    try {
      const response = await fetch(`${API}/reminders`);

      if (!response.ok) {
        throw new Error("Could not load reminders.");
      }

      const data = await response.json();
      setReminders(data.reminders || []);
      setError("");
    } catch (err) {
      setError(err.message);
    }
  }, []);

  useEffect(() => {
    loadReminders();
  }, [loadReminders]);

  const createReminder = async (event) => {
    event.preventDefault();

    if (!title.trim() || !remindAt) {
      setError("Enter a reminder title and date/time.");
      return;
    }

    setLoading(true);
    setError("");
    setNotice("");

    try {
      const response = await fetch(`${API}/reminders`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: title.trim(),
          description: description.trim(),
          remind_at: remindAt
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Could not create reminder.");
      }

      setTitle("");
      setDescription("");
      setRemindAt("");
      setNotice("Reminder saved successfully.");

      await loadReminders();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleReminder = async (id) => {
    try {
      const response = await fetch(`${API}/reminders/${id}`, {
        method: "PATCH"
      });

      if (!response.ok) {
        throw new Error("Could not update reminder.");
      }

      setNotice("Reminder updated successfully.");
      await loadReminders();
    } catch (err) {
      setError(err.message);
    }
  };

  const deleteReminder = async (id) => {
    if (!window.confirm("Delete this reminder?")) return;

    try {
      const response = await fetch(`${API}/reminders/${id}`, {
        method: "DELETE"
      });

      if (!response.ok) {
        throw new Error("Could not delete reminder.");
      }

      setNotice("Reminder deleted successfully.");
      await loadReminders();
    } catch (err) {
      setError(err.message);
    }
  };

  const sortedReminders = [...reminders].sort(
    (a, b) => new Date(a.remind_at) - new Date(b.remind_at)
  );

  const pending = sortedReminders.filter((item) => !item.completed);
  const completed = sortedReminders.filter((item) => item.completed);

  return (
    <section className="feature-page">
      <div className="feature-page-heading">
        <div>
          <span className="eyebrow">DESKTOP TOOLS</span>
          <h1>Reminders</h1>
          <p>Organize your tasks and important activities.</p>
        </div>
      </div>

      <form className="reminder-form" onSubmit={createReminder}>
        <h2>Create a reminder</h2>

        <label>Reminder title</label>
        <input
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          placeholder="Example: Complete DSA practice"
          maxLength={150}
          required
        />

        <label>Description (optional)</label>
        <textarea
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          placeholder="Add some details..."
          rows={3}
        />

        <label>Date and time</label>
        <input
          type="datetime-local"
          value={remindAt}
          onChange={(event) => setRemindAt(event.target.value)}
          required
        />

        <button type="submit" disabled={loading}>
          {loading ? "Saving..." : "+ Create reminder"}
        </button>
      </form>

      {error && (
        <div className="feature-error" role="alert">
          {error}
        </div>
      )}

      {notice && (
        <p className="reminder-notice" role="status">
          {notice}
        </p>
      )}

      <div className="reminder-summary">
        <div className="reminder-count">
          <strong>{pending.length}</strong>
          <span>Pending</span>
        </div>

        <div className="reminder-count">
          <strong>{completed.length}</strong>
          <span>Completed</span>
        </div>
      </div>

      <div className="reminder-list-heading">
        <h2>Your reminders</h2>
        <button type="button" onClick={loadReminders}>
          ↻ Refresh
        </button>
      </div>

      {sortedReminders.length === 0 ? (
        <div className="feature-empty">
          <span>◷</span>
          <strong>No reminders yet</strong>
          <p>Create your first reminder above.</p>
        </div>
      ) : (
        <div className="reminder-list">
          {sortedReminders.map((item) => (
            <article
              className={`reminder-item ${
                item.completed ? "completed" : ""
              }`}
              key={item.id}
            >
              <div className="reminder-item-main">
                <strong>{item.title}</strong>

                {item.description && <p>{item.description}</p>}

                <small>
                  {new Date(item.remind_at).toLocaleString()}
                </small>

                <span>
                  {item.completed ? "Completed" : "Pending"}
                </span>
              </div>

              <div className="reminder-actions">
                <button
                  type="button"
                  onClick={() => toggleReminder(item.id)}
                >
                  {item.completed ? "Undo" : "Complete"}
                </button>

                <button
                  type="button"
                  className="reminder-delete"
                  onClick={() => deleteReminder(item.id)}
                >
                  Delete
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

export default Reminders;

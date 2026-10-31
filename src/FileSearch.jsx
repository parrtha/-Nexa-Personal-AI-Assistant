import { useState } from "react";

const API_BASE = "http://127.0.0.1:8010/api";

function formatFileSize(bytes) {
  if (bytes === 0) return "0 Bytes";
  if (!bytes) return "Unknown";

  const units = ["Bytes", "KB", "MB", "GB"];
  const index = Math.floor(Math.log(bytes) / Math.log(1024));

  return `${(bytes / Math.pow(1024, index)).toFixed(2)} ${units[index]}`;
}

function FileSearch() {
  const [query, setQuery] = useState("");
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState("");
  const [openingPath, setOpeningPath] = useState("");

  const searchFiles = async () => {
    const searchText = query.trim();

    if (!searchText) {
      setError("Enter a filename to search.");
      return;
    }

    setLoading(true);
    setError("");
    setFiles([]);
    setSearched(false);

    try {
      const response = await fetch(
        `${API_BASE}/files/search?q=${encodeURIComponent(searchText)}`
      );

      if (!response.ok) {
        throw new Error(`Search failed (${response.status}).`);
      }

      const data = await response.json();

      setFiles(data.results || []);
      setSearched(true);
    } catch (err) {
      setError(
        "Unable to search files. Check that the Nexa backend is running on port 8010."
      );
      console.error("File search error:", err);
    } finally {
      setLoading(false);
    }
  };

  const openFile = async (file) => {
    setOpeningPath(file.path);
    setError("");

    try {
      const response = await fetch(`${API_BASE}/files/open`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          path: file.path
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Unable to open this file.");
      }

      alert(`${file.name} opened successfully.`);
    } catch (err) {
      setError(err.message || "Unable to open the selected file.");
      console.error("Open file error:", err);
    } finally {
      setOpeningPath("");
    }
  };

  return (
    <section className="file-search-page">
      <div className="file-search-heading">
        <div>
          <span className="file-search-eyebrow">
            DESKTOP TOOLS
          </span>

          <h1>File Search</h1>

          <p>
            Find files stored on your Desktop, Downloads and Documents.
          </p>
        </div>

        <div className="file-search-icon">⌕</div>
      </div>

      <div className="file-search-box">
        <span className="file-search-symbol">⌕</span>

        <input
          type="text"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              searchFiles();
            }
          }}
          placeholder="Search by filename... e.g. resume, pdf, project"
          aria-label="Search files by filename"
        />

        <button
          onClick={searchFiles}
          disabled={loading || !query.trim()}
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </div>

      <div className="file-search-locations">
        <span>Search locations:</span>
        <span>Desktop</span>
        <span>Downloads</span>
        <span>Documents</span>
      </div>

      {error && (
        <div className="file-search-error">
          {error}
        </div>
      )}

      <div className="file-results-header">
        <div>
          <h2>Search Results</h2>
          <p>
            {searched
              ? `${files.length} matching file(s) found`
              : "Your matching files will appear here."}
          </p>
        </div>

        {searched && (
          <button
            className="file-refresh-button"
            onClick={searchFiles}
            disabled={loading}
          >
            ↻ Refresh
          </button>
        )}
      </div>

      {loading ? (
        <div className="file-search-empty">
          <div className="file-loading-spinner" />
          <strong>Searching your files...</strong>
          <p>Please wait a moment.</p>
        </div>
      ) : files.length > 0 ? (
        <div className="file-results-list">
          {files.map((file, index) => (
            <article
              className="file-result-card"
              key={`${file.path}-${index}`}
            >
              <div className="file-result-icon">
                {file.name.split(".").pop()?.toLowerCase() === "pdf"
                  ? "📕"
                  : "📄"}
              </div>

              <div className="file-result-details">
                <strong title={file.name}>
                  {file.name}
                </strong>

                <span title={file.path}>
                  {file.path}
                </span>

                <div className="file-result-meta">
                  <small>{file.location}</small>
                  <small>{formatFileSize(file.size_bytes)}</small>
                  <small>{file.modified || "Date unavailable"}</small>
                </div>
              </div>

              <button
                className="file-open-button"
                onClick={() => openFile(file)}
                disabled={openingPath !== ""}
              >
                {openingPath === file.path ? "Opening..." : "Open"}
              </button>
            </article>
          ))}
        </div>
      ) : (
        <div className="file-search-empty">
          <div className="file-empty-icon">
            {searched ? "⌕" : "📁"}
          </div>

          <strong>
            {searched ? "No matching files found" : "Find your files with Nexa"}
          </strong>

          <p>
            {searched
              ? "Try another filename or a shorter search term."
              : "Enter a filename above and click Search to get started."}
          </p>
        </div>
      )}

      <div className="file-search-note">
        <span>🔒</span>
        <p>
          File search runs locally on your computer. It searches filenames,
          not the contents inside files.
        </p>
      </div>
    </section>
  );
}

export default FileSearch;
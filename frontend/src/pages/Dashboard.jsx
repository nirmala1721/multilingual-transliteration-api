import { useCallback, useEffect, useMemo, useState } from "react";
import {
  CheckCircle2,
  FileText,
  Languages,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

import { getDocuments } from "../services/api";

function Dashboard() {
  const navigate = useNavigate();

  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadDashboard = useCallback(async () => {
    try {
      setLoading(true);
      setError("");

      const result = await getDocuments();

      setDocuments(result.data.documents || []);
    } catch (error) {
      setError(
        error.message || "Failed to load dashboard"
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
  const handleDocumentUploaded = () => {
    loadDashboard();
  };

  window.addEventListener(
    "documentUploaded",
    handleDocumentUploaded
  );

  const timer = setTimeout(() => {
    loadDashboard();
  }, 0);

  return () => {
    clearTimeout(timer);

    window.removeEventListener(
      "documentUploaded",
      handleDocumentUploaded
    );
  };
}, [loadDashboard]);

  const completedDocuments = useMemo(() => {
    return documents.filter(
      (document) =>
        document.status?.toLowerCase() === "completed"
    ).length;
  }, [documents]);

  const languageCount = useMemo(() => {
    const languages = documents
      .map((document) =>
        document.language?.toLowerCase()
      )
      .filter(Boolean);

    return new Set(languages).size;
  }, [documents]);

  return (
    <section className="dashboard-page">

      {/* ======================================================
          PAGE HEADER
      ====================================================== */}

      <div className="page-heading">
        <span className="page-eyebrow">
          Workspace
        </span>

        <h1>Dashboard</h1>

        <p>
          Overview of your transliteration workspace
          and recent documents.
        </p>
      </div>

      {/* ======================================================
          ERROR
      ====================================================== */}

      {error && (
        <div className="history-error">
          {error}
        </div>
      )}

      {/* ======================================================
          SUMMARY CARDS
      ====================================================== */}

      <div className="dashboard-grid">

        {/* TOTAL DOCUMENTS */}

        <div className="dashboard-card">
          <div>
            <FileText size={20} />

            <span>
              Total Documents
            </span>
          </div>

          <strong>
            {loading
              ? "—"
              : documents.length}
          </strong>
        </div>

        {/* COMPLETED */}

        <div className="dashboard-card">
          <div>
            <CheckCircle2 size={20} />

            <span>
              Completed
            </span>
          </div>

          <strong>
            {loading
              ? "—"
              : completedDocuments}
          </strong>
        </div>

        {/* LANGUAGES */}

        <div className="dashboard-card">
          <div>
            <Languages size={20} />

            <span>
              Languages Used
            </span>
          </div>

          <strong>
            {loading
              ? "—"
              : languageCount}
          </strong>
        </div>

      </div>

      {/* ======================================================
          QUICK ACTIONS
      ====================================================== */}

      <div className="dashboard-section">

        <div className="dashboard-section-header">
          <div>
            <h2>
              Quick Actions
            </h2>

            <p>
              Start a new task or view your previous
              documents.
            </p>
          </div>
        </div>

        <div className="dashboard-quick-actions">

          {/* START TRANSLITERATION */}

          <button
            type="button"
            className="dashboard-quick-action"
            onClick={() =>
              navigate("/transliterate")
            }
          >
            <div className="dashboard-quick-action-icon">
              <FileText size={20} />
            </div>

            <div>
              <h3>
                Start Transliteration
              </h3>

              <p>
                Upload a file or enter text to begin.
              </p>
            </div>
          </button>

          {/* VIEW HISTORY */}

          <button
            type="button"
            className="dashboard-quick-action"
            onClick={() =>
              navigate("/history")
            }
          >
            <div className="dashboard-quick-action-icon">
              <Languages size={20} />
            </div>

            <div>
              <h3>
                View History
              </h3>

              <p>
                Browse and reopen your previous
                documents.
              </p>
            </div>
          </button>

        </div>

      </div>

    </section>
  );
}

export default Dashboard;
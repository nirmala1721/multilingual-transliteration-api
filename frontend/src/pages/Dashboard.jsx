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
  const [totalDocuments, setTotalDocuments] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // ============================================================
  // LOAD DASHBOARD DATA
  // ============================================================

  const loadDashboard = useCallback(async () => {
    try {
      setLoading(true);
      setError("");

      const result = await getDocuments();

      const responseData = result?.data || {};

      const documentList = Array.isArray(
        responseData.documents
      )
        ? responseData.documents
        : [];

      setDocuments(documentList);

      setTotalDocuments(
        typeof responseData.count === "number"
          ? responseData.count
          : documentList.length
      );
    } catch (error) {
      console.error(
        "Dashboard loading error:",
        error
      );

      setError(
        error?.message ||
          "Failed to load dashboard"
      );

      setDocuments([]);
      setTotalDocuments(0);
    } finally {
      setLoading(false);
    }
  }, []);

  // ============================================================
  // INITIAL LOAD + UPLOAD EVENT
  // ============================================================

  useEffect(() => {
    const handleDocumentUploaded = () => {
      loadDashboard();
    };

    window.addEventListener(
      "documentUploaded",
      handleDocumentUploaded
    );

    loadDashboard();

    return () => {
      window.removeEventListener(
        "documentUploaded",
        handleDocumentUploaded
      );
    };
  }, [loadDashboard]);

  // ============================================================
  // COMPLETED DOCUMENTS
  // ============================================================

  const completedDocuments = useMemo(() => {
    return documents.filter((document) => {
      const status = String(
        document?.status || ""
      )
        .trim()
        .toLowerCase();

      return status === "completed";
    }).length;
  }, [documents]);

  // ============================================================
  // LANGUAGES USED
  // ============================================================
  //
  // Supports:
  //
  // language: "telugu"
  //
  // language: "mixed"
  // languages: ["telugu", "hindi"]
  //
  // language: "mixed"
  // languages: ["telugu", "hindi", "tamil"]
  //
  // Duplicates are counted only once.
  //
  // "mixed" itself is NOT counted as a language.
  // ============================================================

  const languageCount = useMemo(() => {
    const languageSet = new Set();

    documents.forEach((document) => {
      // --------------------------------------------------------
      // 1. Check languages array
      // --------------------------------------------------------

      if (
        Array.isArray(document?.languages) &&
        document.languages.length > 0
      ) {
        document.languages.forEach((language) => {
          if (!language) {
            return;
          }

          const normalizedLanguage = String(language)
            .trim()
            .toLowerCase();

          if (
            normalizedLanguage &&
            normalizedLanguage !== "mixed"
          ) {
            languageSet.add(
              normalizedLanguage
            );
          }
        });
      }

      // --------------------------------------------------------
      // 2. Also check language field
      // --------------------------------------------------------
      //
      // This is intentionally NOT "else".
      //
      // We check both fields because a document can contain:
      //
      // language: "mixed"
      // languages: ["telugu", "hindi"]
      //
      // or:
      //
      // language: "telugu"
      // languages: []
      // --------------------------------------------------------

      const language = String(
        document?.language || ""
      )
        .trim()
        .toLowerCase();

      if (
        language &&
        language !== "mixed"
      ) {
        languageSet.add(language);
      }
    });

    return languageSet.size;
  }, [documents]);

  // ============================================================
  // PAGE
  // ============================================================

  return (
    <section className="dashboard-page">

      {/* ======================================================
          PAGE HEADER
      ====================================================== */}

      <div className="page-heading">

        <span className="page-eyebrow">
          Workspace
        </span>

        <h1>
          Dashboard
        </h1>

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
              : totalDocuments}
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
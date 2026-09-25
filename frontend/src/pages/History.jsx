import { useCallback, useEffect, useMemo, useState } from "react";
import {
  CalendarDays,
  ExternalLink,
  FileImage,
  FileText,
  FileType2,
  Languages,
  Search,
  Trash2,
  X,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

import {
  getDocuments,
  deleteDocument,
} from "../services/api";

function History() {
  const navigate = useNavigate();

  const [documents, setDocuments] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [fileTypeFilter, setFileTypeFilter] =
    useState("all");
  const [languageFilter, setLanguageFilter] =
    useState("all");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deletingDocumentId, setDeletingDocumentId] =
    useState(null);

  // ============================================================
  // DELETE CONFIRMATION MODAL
  // ============================================================

  const [documentToDelete, setDocumentToDelete] =
    useState(null);

  // ============================================================
  // LOAD HISTORY
  // ============================================================

  const loadHistory = useCallback(async () => {
    try {
      setLoading(true);
      setError("");

      const result = await getDocuments();

      setDocuments(result.data.documents || []);
    } catch (error) {
      setError(
        error.message || "Failed to load history"
      );
    } finally {
      setLoading(false);
    }
  }, []);

  // ============================================================
  // INITIAL LOAD + UPLOAD EVENT
  // ============================================================

  useEffect(() => {
  const handleDocumentUploaded = () => {
    loadHistory();
  };

  const timer = setTimeout(() => {
    loadHistory();
  }, 0);

  window.addEventListener(
    "documentUploaded",
    handleDocumentUploaded
  );

  return () => {
    clearTimeout(timer);

    window.removeEventListener(
      "documentUploaded",
      handleDocumentUploaded
    );
  };
}, [loadHistory]);
  // ============================================================
  // FILE TYPE OPTIONS
  // ============================================================

  const fileTypes = useMemo(() => {
    return [
      ...new Set(
        documents
          .map((document) =>
            document.file_type?.toLowerCase()
          )
          .filter(Boolean)
      ),
    ].sort();
  }, [documents]);

  // ============================================================
  // LANGUAGE OPTIONS
  // ============================================================

  const languages = useMemo(() => {
    return [
      ...new Set(
        documents
          .map((document) =>
            document.language?.toLowerCase()
          )
          .filter(Boolean)
      ),
    ].sort();
  }, [documents]);

  // ============================================================
  // FILTER HISTORY
  // ============================================================

  const filteredDocuments = useMemo(() => {
    const search = searchTerm.trim().toLowerCase();

    return documents.filter((document) => {
      const matchesSearch =
        !search ||
        document.filename
          ?.toLowerCase()
          .includes(search) ||
        document.file_type
          ?.toLowerCase()
          .includes(search) ||
        document.language
          ?.toLowerCase()
          .includes(search) ||
        document.status
          ?.toLowerCase()
          .includes(search);

      const matchesFileType =
        fileTypeFilter === "all" ||
        document.file_type?.toLowerCase() ===
          fileTypeFilter;

      const matchesLanguage =
        languageFilter === "all" ||
        document.language?.toLowerCase() ===
          languageFilter;

      return (
        matchesSearch &&
        matchesFileType &&
        matchesLanguage
      );
    });
  }, [
    documents,
    searchTerm,
    fileTypeFilter,
    languageFilter,
  ]);

  // ============================================================
  // OPEN DOCUMENT
  // ============================================================

  const handleOpenDocument = (documentId) => {
    navigate(
      `/transliterate?documentId=${documentId}`
    );
  };

  // ============================================================
  // OPEN DELETE CONFIRMATION
  // ============================================================

  const handleDeleteDocument = (document) => {
    setDocumentToDelete(document);
  };

  // ============================================================
  // CANCEL DELETE
  // ============================================================

  const handleCancelDelete = () => {
    if (deletingDocumentId !== null) {
      return;
    }

    setDocumentToDelete(null);
  };

  // ============================================================
  // CONFIRM DELETE
  // ============================================================

  const handleConfirmDelete = async () => {
    if (!documentToDelete) {
      return;
    }

    const document = documentToDelete;

    try {
      setDeletingDocumentId(document.id);
      setError("");

      await deleteDocument(document.id);

      setDocuments((currentDocuments) =>
        currentDocuments.filter(
          (item) => item.id !== document.id
        )
      );

      setDocumentToDelete(null);
    } catch (error) {
      setError(
        error.message || "Failed to delete document"
      );
    } finally {
      setDeletingDocumentId(null);
    }
  };

  // ============================================================
  // FILE ICON
  // ============================================================

  const getFileIcon = (fileType) => {
    const type = fileType?.toLowerCase();

    if (
      type === "png" ||
      type === "jpg" ||
      type === "jpeg"
    ) {
      return FileImage;
    }

    if (type === "pdf") {
      return FileType2;
    }

    return FileText;
  };

  // ============================================================
  // FORMAT DATE
  // ============================================================

  const formatDocumentDate = (createdAt) => {
    if (!createdAt) {
      return "Unknown date";
    }

    const date = new Date(createdAt);

    if (Number.isNaN(date.getTime())) {
      return "Unknown date";
    }

    return date.toLocaleString([], {
      dateStyle: "medium",
      timeStyle: "short",
    });
  };

  return (
    <section className="history-page">

      {/* ======================================================
          PAGE HEADER
      ====================================================== */}

      <div className="history-heading">
        <div>
          <span className="page-eyebrow">
            Workspace
          </span>

          <h1>History</h1>

          <p>
            View and reopen your previously uploaded
            documents.
          </p>
        </div>
      </div>

      {/* ======================================================
          SEARCH + FILTERS + SUMMARY
      ====================================================== */}

      <div className="history-toolbar">

        {/* SEARCH */}

        <div className="history-search">
          <Search size={17} />

          <input
            type="text"
            placeholder="Search files..."
            value={searchTerm}
            onChange={(event) =>
              setSearchTerm(event.target.value)
            }
          />
        </div>

        {/* FILE TYPE FILTER */}

        <div className="history-filter">
          <select
            value={fileTypeFilter}
            onChange={(event) =>
              setFileTypeFilter(event.target.value)
            }
          >
            <option value="all">
              All file types
            </option>

            {fileTypes.map((type) => (
              <option
                key={type}
                value={type}
              >
                {type.toUpperCase()}
              </option>
            ))}
          </select>
        </div>

        {/* LANGUAGE FILTER */}

        <div className="history-filter">
          <select
            value={languageFilter}
            onChange={(event) =>
              setLanguageFilter(event.target.value)
            }
          >
            <option value="all">
              All languages
            </option>

            {languages.map((language) => (
              <option
                key={language}
                value={language}
              >
                {language.charAt(0).toUpperCase() +
                  language.slice(1)}
              </option>
            ))}
          </select>
        </div>

        {/* SUMMARY */}

        <div className="history-summary">
          <Languages size={16} />

          <span>
            {filteredDocuments.length}{" "}
            {filteredDocuments.length === 1
              ? "file"
              : "files"}
          </span>
        </div>

      </div>

      {/* ======================================================
          ERROR
      ====================================================== */}

      {!loading && error && (
        <div className="history-error">
          <span>{error}</span>
        </div>
      )}

      {/* ======================================================
          LOADING
      ====================================================== */}

      {loading && (
        <div className="history-empty-state">

          <div className="history-empty-icon">
            <FileText size={22} />
          </div>

          <h3>Loading history...</h3>

          <p>
            Retrieving your previously uploaded files.
          </p>

        </div>
      )}

      {/* ======================================================
          HISTORY LIST
      ====================================================== */}

      {!loading &&
        filteredDocuments.length > 0 && (
          <div className="history-list">

            {filteredDocuments.map((document) => {
              const FileIcon = getFileIcon(
                document.file_type
              );

              const isDeleting =
                deletingDocumentId === document.id;

              return (
                <article
                  className="history-card"
                  key={document.id}
                >

                  {/* FILE ICON */}

                  <div className="history-card-icon">
                    <FileIcon size={21} />
                  </div>

                  {/* FILE DETAILS */}

                  <div className="history-card-main">

                    <div className="history-card-title">

                      <h3>
                        {document.filename}
                      </h3>

                      <span className="history-type">
                        {document.file_type?.toUpperCase()}
                      </span>

                    </div>

                    <div className="history-card-meta">

                      <span>
                        {document.language ||
                          "Unknown"}
                      </span>

                      <span className="history-meta-separator">
                        •
                      </span>

                      <span className="history-status">
                        <span className="status-dot" />
                        {document.status}
                      </span>

                    </div>

                  </div>

                  {/* DATE */}

                  <div className="history-card-date">

                    <span>
                      {formatDocumentDate(
                        document.created_at
                      )}
                    </span>

                    <CalendarDays size={14} />

                  </div>

                  {/* ACTIONS */}

                  <div className="history-card-actions">

                    {/* OPEN */}

                    <button
                      type="button"
                      className="history-open-button"
                      onClick={() =>
                        handleOpenDocument(
                          document.id
                        )
                      }
                      disabled={isDeleting}
                    >
                      <ExternalLink size={15} />
                      Open
                    </button>

                    {/* DELETE */}

                    <button
                      type="button"
                      className="history-delete-button"
                      onClick={() =>
                        handleDeleteDocument(
                          document
                        )
                      }
                      disabled={isDeleting}
                      aria-label={`Delete ${document.filename}`}
                      title={
                        isDeleting
                          ? "Deleting..."
                          : "Delete document"
                      }
                    >
                      <Trash2 size={15} />

                      <span>
                        {isDeleting
                          ? "Deleting..."
                          : "Delete"}
                      </span>
                    </button>

                  </div>

                </article>
              );
            })}

          </div>
        )}

      {/* ======================================================
          EMPTY STATE
      ====================================================== */}

      {!loading &&
        !error &&
        filteredDocuments.length === 0 && (
          <div className="history-empty-state">

            <div className="history-empty-icon">
              <Search size={22} />
            </div>

            <h3>
              {documents.length === 0
                ? "No files yet"
                : "No files found"}
            </h3>

            <p>
              {documents.length === 0
                ? "Upload a document to see it in your history."
                : "Try searching with a different filename, file type, language, or status."}
            </p>

          </div>
        )}

      {/* ======================================================
          DELETE CONFIRMATION MODAL
      ====================================================== */}

      {documentToDelete && (
        <div
          className="delete-modal-overlay"
          role="presentation"
          onMouseDown={(event) => {
            if (
              event.target === event.currentTarget &&
              deletingDocumentId === null
            ) {
              handleCancelDelete();
            }
          }}
        >

          <div
            className="delete-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="delete-modal-title"
          >

            <div className="delete-modal-header">

              <div className="delete-modal-icon">
                <Trash2 size={20} />
              </div>

              <button
                type="button"
                className="delete-modal-close"
                onClick={handleCancelDelete}
                disabled={
                  deletingDocumentId !== null
                }
                aria-label="Close"
              >
                <X size={18} />
              </button>

            </div>

            <div className="delete-modal-content">

              <h2 id="delete-modal-title">
                Delete document?
              </h2>

              <p>
                Are you sure you want to permanently
                delete{" "}
                <strong>
                  {documentToDelete.filename}
                </strong>
                ?
              </p>

              <span className="delete-modal-warning">
                This will remove the file and its
                transliteration history.
              </span>

            </div>

            <div className="delete-modal-actions">

              <button
                type="button"
                className="delete-modal-cancel"
                onClick={handleCancelDelete}
                disabled={
                  deletingDocumentId !== null
                }
              >
                Cancel
              </button>

              <button
                type="button"
                className="delete-modal-confirm"
                onClick={handleConfirmDelete}
                disabled={
                  deletingDocumentId !== null
                }
              >
                {deletingDocumentId !== null
                  ? "Deleting..."
                  : "Delete"}
              </button>

            </div>

          </div>

        </div>
      )}

    </section>
  );
}

export default History;
import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  useSearchParams,
} from "react-router-dom";

import {
  ArrowRight,
  Check,
  Clipboard,
  FileUp,
  Languages,
  RotateCcw,
} from "lucide-react";

import {
  transliterateText,
  transliterateFile,
  getDocument,
  getDocumentFileUrl,
} from "../../services/api";


const MAX_TEXT_LENGTH = 100000;

// Maximum upload size
const MAX_FILE_SIZE =
  10 * 1024 * 1024;

// Maximum processing time
const FILE_PROCESSING_TIMEOUT =
  3 * 60 * 1000;


// ============================================================
// COMPONENT
// ============================================================

function TransliterationWorkspace() {

  // ==========================================================
  // REFS
  // ==========================================================

  const fileInputRef =
    useRef(null);

  const fileAbortControllerRef =
    useRef(null);

  const fileTimeoutRef =
    useRef(null);


  // ==========================================================
  // URL PARAMS
  // ==========================================================

  const [searchParams] =
    useSearchParams();

  const documentId =
    searchParams.get(
      "documentId"
    );


  // ==========================================================
  // STATE
  // ==========================================================

  const [inputText, setInputText] =
    useState("");

  const [selectedFile, setSelectedFile] =
    useState(null);

  const [openedDocument, setOpenedDocument] =
    useState(null);

  const [
    openedDocumentFileUrl,
    setOpenedDocumentFileUrl,
  ] = useState("");

  const [
    textFilePreview,
    setTextFilePreview,
  ] = useState("");

  const [
    filePreviewUrl,
    setFilePreviewUrl,
  ] = useState("");

  const [outputText, setOutputText] =
    useState("");

  const [language, setLanguage] =
    useState("auto");

  const [
    detectedLanguage,
    setDetectedLanguage,
  ] = useState("Auto detection");

  const [copied, setCopied] =
    useState(false);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");


  const characterCount =
    inputText.length;


  // ==========================================================
  // CLEANUP
  // ==========================================================

  useEffect(() => {
    return () => {

      if (
        fileAbortControllerRef.current
      ) {
        fileAbortControllerRef.current.abort();
      }

      if (
        fileTimeoutRef.current
      ) {
        clearTimeout(
          fileTimeoutRef.current
        );
      }

      if (filePreviewUrl) {
        URL.revokeObjectURL(
          filePreviewUrl
        );
      }
    };
  }, []);


  // ==========================================================
  // FILE PROCESSING WITH TIMEOUT
  // ==========================================================

  const processFileWithTimeout =
    async (
      file,
      selectedLanguage
    ) => {

      // Cancel previous request
      if (
        fileAbortControllerRef.current
      ) {
        fileAbortControllerRef.current.abort();
      }

      // Clear previous timeout
      if (
        fileTimeoutRef.current
      ) {
        clearTimeout(
          fileTimeoutRef.current
        );
      }

      const controller =
        new AbortController();

      fileAbortControllerRef.current =
        controller;


      const timeoutPromise =
        new Promise(
          (_, reject) => {

            fileTimeoutRef.current =
              setTimeout(() => {

                controller.abort();

                reject(
                  new Error(
                    "This file could not be processed within 3 minutes. " +
                    "Please try a smaller file or a file with fewer pages."
                  )
                );

              },
              FILE_PROCESSING_TIMEOUT
            );
          }
        );


      try {

        return await Promise.race([
          transliterateFile(
            file,
            selectedLanguage,
            controller.signal
          ),

          timeoutPromise,
        ]);

      } catch (error) {

        if (
          error?.name ===
          "AbortError"
        ) {
          throw new Error(
            "This file could not be processed within 3 minutes. " +
            "Please try a smaller file or a file with fewer pages.",
            {
              cause: error,
            }
          );
        }

        throw error;

      } finally {

        if (
          fileTimeoutRef.current
        ) {
          clearTimeout(
            fileTimeoutRef.current
          );

          fileTimeoutRef.current =
            null;
        }

        if (
          fileAbortControllerRef.current ===
          controller
        ) {
          fileAbortControllerRef.current =
            null;
        }
      }
    };


  // ==========================================================
  // LOAD SAVED DOCUMENT
  // ==========================================================

  useEffect(() => {

    if (!documentId) {
      return;
    }


    const loadDocument =
      async () => {

        try {

          setLoading(true);
          setError("");

          const result =
            await getDocument(
              documentId
            );

          const document =
            result.data;


          setOpenedDocument(
            document
          );


          // IMPORTANT:
          // Use the actual Flask backend URL.
          setOpenedDocumentFileUrl(
            getDocumentFileUrl(
              documentId
            )
          );


          setOutputText(
            document.transliterated_text ||
            ""
          );


          setInputText(
            document.original_text ||
            ""
          );


          setDetectedLanguage(
            document.language ||
            "Auto detection"
          );


          setTextFilePreview(
            document.original_text ||
            ""
          );


          setSelectedFile(null);
          setFilePreviewUrl("");

        } catch (error) {

          console.error(
            "Failed to load document:",
            error
          );

          setError(
            error.message ||
            "Unable to load the selected document."
          );

          setOpenedDocument(null);
          setOpenedDocumentFileUrl("");

        } finally {

          setLoading(false);
        }
      };


    loadDocument();

  }, [documentId]);


  // ==========================================================
  // FILE HELPERS
  // ==========================================================

  const getFileType =
    (file) => {

      if (!file) {
        return "";
      }

      const extension =
        file.name
          .split(".")
          .pop()
          .toLowerCase();

      return extension.toUpperCase();
    };


  const isImageFile =
    (file) => {

      if (!file) {
        return false;
      }

      return (
        file.type ===
          "image/png" ||
        file.type ===
          "image/jpeg"
      );
    };


  const isPdfFile =
    (file) => {

      if (!file) {
        return false;
      }

      return (
        file.type ===
        "application/pdf"
      );
    };


  const isTextFile =
    (file) => {

      if (!file) {
        return false;
      }

      return (
        file.type ===
          "text/plain" ||
        file.name
          .toLowerCase()
          .endsWith(".txt")
      );
    };


  // ==========================================================
  // SAVED DOCUMENT FILE TYPE
  // ==========================================================

  const getOpenedDocumentExtension =
    () => {

      if (
        !openedDocument?.file_type
      ) {
        return "";
      }

      return openedDocument.file_type
        .toLowerCase();
    };


  const isOpenedDocumentImage =
    () => {

      const extension =
        getOpenedDocumentExtension();

      return (
        extension === "png" ||
        extension === "jpg" ||
        extension === "jpeg"
      );
    };


  const isOpenedDocumentPdf =
    () => {

      return (
        getOpenedDocumentExtension() ===
        "pdf"
      );
    };


  const isOpenedDocumentText =
    () => {

      return (
        getOpenedDocumentExtension() ===
        "txt"
      );
    };


  // ==========================================================
  // TEXT INPUT
  // ==========================================================

  const handleInputChange =
    (event) => {

      setInputText(
        event.target.value
      );

      setCopied(false);
      setError("");

      setOutputText("");


      if (selectedFile) {

        setSelectedFile(null);
        setTextFilePreview("");

        if (filePreviewUrl) {

          URL.revokeObjectURL(
            filePreviewUrl
          );

          setFilePreviewUrl("");
        }
      }


      if (openedDocument) {

        setOpenedDocument(null);
        setOpenedDocumentFileUrl("");
      }
    };


  // ==========================================================
  // LANGUAGE
  // ==========================================================

  const handleLanguageChange =
    (event) => {

      setLanguage(
        event.target.value
      );
    };


  // ==========================================================
  // CLEAR
  // ==========================================================

  const handleClear =
    () => {

      if (
        fileAbortControllerRef.current
      ) {

        fileAbortControllerRef.current.abort();

        fileAbortControllerRef.current =
          null;
      }


      if (
        fileTimeoutRef.current
      ) {

        clearTimeout(
          fileTimeoutRef.current
        );

        fileTimeoutRef.current =
          null;
      }


      if (filePreviewUrl) {

        URL.revokeObjectURL(
          filePreviewUrl
        );
      }


      setInputText("");
      setSelectedFile(null);
      setOpenedDocument(null);

      setOpenedDocumentFileUrl("");

      setTextFilePreview("");
      setFilePreviewUrl("");

      setOutputText("");

      setDetectedLanguage(
        "Auto detection"
      );

      setCopied(false);
      setError("");
      setLoading(false);


      if (fileInputRef.current) {

        fileInputRef.current.value =
          "";
      }
    };


  // ==========================================================
  // COPY
  // ==========================================================

  const handleCopy =
    async () => {

      if (!outputText) {
        return;
      }


      try {

        await navigator.clipboard
          .writeText(outputText);

        setCopied(true);


        setTimeout(() => {

          setCopied(false);

        }, 2000);

      } catch (error) {

        console.error(
          "Failed to copy text:",
          error
        );
      }
    };


  // ==========================================================
  // OPEN FILE PICKER
  // ==========================================================

  const handleUploadClick =
    () => {

      fileInputRef.current?.click();
    };


  // ==========================================================
  // FILE SELECTION
  // ==========================================================

  const handleFileChange =
    async (event) => {

      const file =
        event.target.files?.[0];


      if (!file) {
        return;
      }


      // ------------------------------------------------------
      // FILE SIZE
      // ------------------------------------------------------

      if (
        file.size >
        MAX_FILE_SIZE
      ) {

        setSelectedFile(null);
        setInputText("");
        setTextFilePreview("");
        setOutputText("");

        setDetectedLanguage(
          "Auto detection"
        );

        setCopied(false);
        setLoading(false);

        setError(
          "File size exceeds the maximum allowed size of 10 MB."
        );


        if (filePreviewUrl) {

          URL.revokeObjectURL(
            filePreviewUrl
          );

          setFilePreviewUrl("");
        }


        if (fileInputRef.current) {

          fileInputRef.current.value =
            "";
        }

        return;
      }


      // ------------------------------------------------------
      // REMOVE OLD PREVIEW
      // ------------------------------------------------------

      if (filePreviewUrl) {

        URL.revokeObjectURL(
          filePreviewUrl
        );
      }


      // ------------------------------------------------------
      // CREATE PREVIEW
      // ------------------------------------------------------

      const isPreviewable =
        file.type ===
          "image/png" ||
        file.type ===
          "image/jpeg" ||
        file.type ===
          "application/pdf";


      if (isPreviewable) {

        const previewUrl =
          URL.createObjectURL(
            file
          );

        setFilePreviewUrl(
          previewUrl
        );

      } else {

        setFilePreviewUrl("");
      }


      // ------------------------------------------------------
      // RESET STATE
      // ------------------------------------------------------

      setSelectedFile(file);

      setOpenedDocument(null);

      setOpenedDocumentFileUrl("");

      setInputText("");

      setTextFilePreview("");

      setOutputText("");

      setDetectedLanguage(
        "Auto detection"
      );

      setError("");

      setCopied(false);

      setLoading(true);


      // ------------------------------------------------------
      // TEXT FILE PREVIEW
      // ------------------------------------------------------

      if (isTextFile(file)) {

        try {

          const text =
            await file.text();

          setTextFilePreview(
            text
          );

        } catch (error) {

          console.error(
            "Failed to read text file:",
            error
          );
        }
      }


      // ------------------------------------------------------
      // SEND TO BACKEND
      // ------------------------------------------------------

      try {

        const result =
          await processFileWithTimeout(
            file,
            language
          );


        if (!result?.data) {

          throw new Error(
            "The file could not be processed."
          );
        }


        setOutputText(
          result.data
            .transliterated_text ||
          ""
        );


        setDetectedLanguage(
          result.data.language ||
          "Auto detection"
        );


        if (
          !isTextFile(file) &&
          result.data.original_text
        ) {

          setTextFilePreview(
            result.data.original_text
          );
        }


        // Tell History page
        // that a document was uploaded.
        window.dispatchEvent(
          new Event(
            "documentUploaded"
          )
        );

      } catch (error) {

        console.error(
          "File processing failed:",
          error
        );


        setOutputText("");


        setError(
          error.message ||
          "Unable to process the file."
        );

      } finally {

        setLoading(false);
      }
    };


  // ==========================================================
  // TEXT TRANSLITERATION
  // ==========================================================

  const handleTransliterate =
    async () => {

      if (
        !inputText.trim()
      ) {
        return;
      }


      setLoading(true);
      setError("");
      setOutputText("");
      setCopied(false);


      try {

        const result =
          await transliterateText(
            inputText,
            language
          );


        setOutputText(
          result.data
            .transliterated_text ||
          ""
        );


        setDetectedLanguage(
          result.data.language ||
          "Auto detection"
        );

      } catch (error) {

        console.error(
          "Text transliteration failed:",
          error
        );


        setError(
          error.message ||
          "Unable to transliterate the text."
        );

      } finally {

        setLoading(false);
      }
    };


  // ==========================================================
  // UI STATE
  // ==========================================================

  const hasSavedDocument =
    Boolean(
      documentId &&
      openedDocument
    );


  const hasSelectedFile =
    Boolean(
      selectedFile
    );


  const sourceDocumentName =
    hasSavedDocument
      ? openedDocument.filename
      : selectedFile?.name;


  const sourceDocumentType =
    hasSavedDocument
      ? openedDocument.file_type
          ?.toUpperCase()
      : getFileType(
          selectedFile
        );


  // ==========================================================
  // UI
  // ==========================================================

  return (
    <section className="transliteration-workspace">

      {/* =====================================================
          PAGE HEADER
      ===================================================== */}

      <div className="workspace-heading">

        <div>

          <span className="page-eyebrow">
            Language Processing
          </span>

          <h1>
            Transliteration Workspace
          </h1>

          <p>
            Convert Indian-language content
            into Latin characters while
            preserving pronunciation.
          </p>

        </div>

      </div>


      {/* =====================================================
          LANGUAGE CONTROLS
      ===================================================== */}

      <div className="workspace-controls">

        <div className="language-control">

          <label htmlFor="input-language">

            <Languages size={16} />

            Input language

          </label>


          <select
            id="input-language"
            value={language}
            onChange={
              handleLanguageChange
            }
          >

            <option value="auto">
              Auto Detect
            </option>

            <option value="telugu">
              Telugu
            </option>

            <option value="hindi">
              Hindi
            </option>

            <option value="tamil">
              Tamil
            </option>

            <option value="bengali">
              Bengali
            </option>

            <option value="kannada">
              Kannada
            </option>

            <option value="gujarati">
              Gujarati
            </option>

            <option value="punjabi">
              Punjabi
            </option>

            <option value="marathi">
              Marathi
            </option>

            <option value="odia">
              Odia
            </option>

          </select>

        </div>


        <div className="detection-status">

          <span className="status-label">
            Detected language
          </span>


          <div className="detected-language">

            <span className="status-dot" />

            <strong>
              {detectedLanguage}
            </strong>

          </div>

        </div>

      </div>


      {/* =====================================================
          TRANSLATION PANELS
      ===================================================== */}

      <div className="translation-panels">

        {/* ===================================================
            SOURCE PANEL
        =================================================== */}

        <div className="translation-panel">

          <div className="panel-header">

            <div>

              <span className="panel-label">

                {hasSelectedFile ||
                hasSavedDocument
                  ? "Source Document"
                  : "Input"}

              </span>


              <span className="panel-description">

                {hasSelectedFile
                  ? "Uploaded source file"
                  : hasSavedDocument
                  ? "Stored document"
                  : "Enter or paste your text"}

              </span>

            </div>


            {!hasSelectedFile &&
              !hasSavedDocument && (

                <span className="character-count">

                  {characterCount.toLocaleString()}

                  {" / "}

                  {MAX_TEXT_LENGTH.toLocaleString()}

                </span>
              )}

          </div>


          {/* =================================================
              NEW FILE
          ================================================= */}

          {hasSelectedFile ? (

            <div className="document-preview">

              {isImageFile(
                selectedFile
              ) && (

                <div className="image-preview-container">

                  <img
                    src={filePreviewUrl}
                    alt={selectedFile.name}
                    className="uploaded-image-preview"
                  />

                </div>
              )}


              {isPdfFile(
                selectedFile
              ) && (

                <div className="pdf-preview-container">

                  <iframe
                    src={filePreviewUrl}
                    title={selectedFile.name}
                    className="uploaded-pdf-preview"
                  />

                </div>
              )}


              {isTextFile(
                selectedFile
              ) && (

                <div className="text-file-preview-container">

                  <pre className="text-file-preview">

                    {textFilePreview}

                  </pre>

                </div>
              )}


              {!isImageFile(
                selectedFile
              ) &&
                !isPdfFile(
                  selectedFile
                ) &&
                !isTextFile(
                  selectedFile
                ) && (

                  <div className="text-file-preview-container">

                    <pre className="text-file-preview">

                      {textFilePreview ||
                        "Extracting document text..."}

                    </pre>

                  </div>
                )}


              <div className="document-preview-details">

                <div className="document-preview-info">

                  <strong>
                    {selectedFile.name}
                  </strong>

                  <span>

                    {getFileType(
                      selectedFile
                    )}

                    {" · "}

                    {(
                      selectedFile.size /
                      1024
                    ).toFixed(1)}

                    {" KB"}

                  </span>

                </div>


                <button
                  type="button"
                  className="replace-file-button"
                  onClick={
                    handleUploadClick
                  }
                  disabled={loading}
                >

                  <FileUp size={15} />

                  {loading
                    ? "Processing..."
                    : "Replace file"}

                </button>

              </div>

            </div>

          ) : hasSavedDocument ? (

            /* =================================================
               SAVED DOCUMENT
            ================================================= */

            <div className="document-preview">

              {isOpenedDocumentImage() && (

                <div className="image-preview-container">

                  <img
                    src={
                      openedDocumentFileUrl
                    }
                    alt={
                      openedDocument.filename
                    }
                    className="uploaded-image-preview"
                  />

                </div>
              )}


              {isOpenedDocumentPdf() && (

                <div className="pdf-preview-container">

                  <iframe
                    src={
                      openedDocumentFileUrl
                    }
                    title={
                      openedDocument.filename
                    }
                    className="uploaded-pdf-preview"
                  />

                </div>
              )}


              {isOpenedDocumentText() && (

                <div className="text-file-preview-container">

                  <pre className="text-file-preview">

                    {
                      openedDocument.original_text ||
                      ""
                    }

                  </pre>

                </div>
              )}


              {!isOpenedDocumentImage() &&
                !isOpenedDocumentPdf() &&
                !isOpenedDocumentText() && (

                  <div className="text-file-preview-container">

                    <pre className="text-file-preview">

                      {
                        openedDocument.original_text ||
                        "No extracted document text available."
                      }

                    </pre>

                  </div>
                )}


              <div className="document-preview-details">

                <div className="document-preview-info">

                  <strong>
                    {sourceDocumentName}
                  </strong>

                  <span>

                    {sourceDocumentType}

                    {" · "}

                    Stored document

                  </span>

                </div>


                <button
                  type="button"
                  className="replace-file-button"
                  onClick={
                    handleUploadClick
                  }
                  disabled={loading}
                >

                  <FileUp size={15} />

                  Replace file

                </button>

              </div>

            </div>

          ) : (

            /* =================================================
               TEXT INPUT
            ================================================= */

            <textarea
              className="translation-textarea"
              placeholder="Type or paste text here..."
              value={inputText}
              onChange={
                handleInputChange
              }
              maxLength={
                MAX_TEXT_LENGTH
              }
            />

          )}

        </div>


        {/* ===================================================
            OUTPUT PANEL
        =================================================== */}

        <div className="translation-panel output-panel">

          <div className="panel-header">

            <div>

              <span className="panel-label">
                Transliteration
              </span>

              <span className="panel-description">
                Latin pronunciation
              </span>

            </div>


            <button
              type="button"
              className="copy-button"
              onClick={handleCopy}
              disabled={!outputText}
              aria-label="Copy transliteration"
            >

              {copied ? (

                <>
                  <Check size={16} />
                  Copied
                </>

              ) : (

                <>
                  <Clipboard size={16} />
                  Copy
                </>

              )}

            </button>

          </div>


          <div className="translation-output">

            {error ? (

              <div className="translation-error">
                {error}
              </div>

            ) : outputText ? (

              outputText

            ) : (

              <span className="output-placeholder">
                Your transliterated text will
                appear here.
              </span>

            )}

          </div>

        </div>

      </div>


      {/* =====================================================
          ACTIONS
      ===================================================== */}

      <div className="workspace-actions">

        <button
          type="button"
          className="upload-button"
          onClick={
            handleUploadClick
          }
          disabled={loading}
        >

          <FileUp size={18} />

          {loading
            ? "Processing..."
            : "Upload file"}

        </button>


        <input
          ref={fileInputRef}
          type="file"
          accept=".txt,.pdf,.docx,.png,.jpg,.jpeg"
          style={{
            display: "none",
          }}
          onChange={
            handleFileChange
          }
        />


        <div className="primary-actions">

          <button
            type="button"
            className="secondary-button"
            onClick={
              handleClear
            }
          >

            <RotateCcw size={17} />

            Clear

          </button>


          <button
            type="button"
            className="primary-button"
            onClick={
              handleTransliterate
            }
            disabled={
              !inputText.trim() ||
              loading
            }
          >

            {loading
              ? "Processing..."
              : "Transliterate"}


            {!loading && (
              <ArrowRight size={17} />
            )}

          </button>

        </div>

      </div>

    </section>
  );
}


export default TransliterationWorkspace;
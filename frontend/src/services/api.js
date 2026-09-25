const API_BASE_URL = "/api/v1";

// ============================================================
// RESPONSE HELPER
// ============================================================

async function parseResponse(response, fallbackMessage) {
  let result;

  try {
    result = await response.json();
  } catch {
    result = null;
  }

  if (!response.ok) {
    throw new Error(
      result?.message ||
        result?.error ||
        fallbackMessage
    );
  }

  return result;
}

// ============================================================
// FETCH HELPER WITH TIMEOUT / CANCELLATION
// ============================================================

async function fetchWithTimeout(
  url,
  options = {},
  timeout = 3 * 60 * 1000
) {
  const controller = new AbortController();

  const timeoutId = setTimeout(() => {
    controller.abort();
  }, timeout);

  try {
    return await fetch(url, {
      ...options,
      signal: controller.signal,
    });
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error(
        "This file is taking too long to process. " +
          "Please try a smaller file or a file with fewer pages.",
        { cause: error }
      );
    }

    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}

// ============================================================
// TEXT TRANSLITERATION
// ============================================================

export async function transliterateText(
  text,
  language = null
) {
  const requestBody = {
    text,
  };

  if (language && language !== "auto") {
    requestBody.language = language;
  }

  let response;

  try {
    response = await fetchWithTimeout(
      `${API_BASE_URL}/transliterate/text`,
      {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify(requestBody),
      }
    );
  } catch (error) {
    throw new Error(
      "Unable to connect to the transliteration server.",
      { cause: error }
    );
  }

  return parseResponse(
    response,
    "Transliteration request failed."
  );
}

// ============================================================
// FILE TRANSLITERATION
// ============================================================

export async function transliterateFile(
  file,
  language = null,
  signal = null
) {
  const formData = new FormData();

  formData.append("file", file);

  if (language && language !== "auto") {
    formData.append("language", language);
  }

  let response;

  try {
    response = await fetch(
      `${API_BASE_URL}/transliterate/file`,
      {
        method: "POST",
        body: formData,
        signal,
      }
    );
  } catch (error) {
    if (error.name === "AbortError") {
      throw error;
    }

    throw new Error(
      "Unable to connect to the transliteration server.",
      { cause: error }
    );
  }

  return parseResponse(
    response,
    "File transliteration request failed."
  );
}

// ============================================================
// GET ALL DOCUMENTS
// ============================================================

export async function getDocuments() {
  let response;

  try {
    response = await fetch(
      `${API_BASE_URL}/documents`
    );
  } catch (error) {
    throw new Error(
      "Unable to connect to the document server.",
      { cause: error }
    );
  }

  return parseResponse(
    response,
    "Failed to retrieve documents."
  );
}

// ============================================================
// GET SINGLE DOCUMENT
// ============================================================

export async function getDocument(documentId) {
  if (!documentId) {
    throw new Error(
      "Document ID is required."
    );
  }

  let response;

  try {
    response = await fetch(
      `${API_BASE_URL}/documents/${documentId}`
    );
  } catch (error) {
    throw new Error(
      "Unable to connect to the document server.",
      { cause: error }
    );
  }

  return parseResponse(
    response,
    "Failed to retrieve document."
  );
}

// ============================================================
// DELETE DOCUMENT
// ============================================================

export async function deleteDocument(documentId) {
  if (!documentId) {
    throw new Error(
      "Document ID is required."
    );
  }

  let response;

  try {
    response = await fetch(
      `${API_BASE_URL}/documents/${documentId}`,
      {
        method: "DELETE",
      }
    );
  } catch (error) {
    throw new Error(
      "Unable to connect to the document server.",
      { cause: error }
    );
  }

  return parseResponse(
    response,
    "Failed to delete document."
  );
}
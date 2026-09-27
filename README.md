# Universal Multilingual Transliteration API

A full-stack multilingual transliteration application that converts supported Indian-language text into Latin characters while preserving pronunciation.

> Transliteration changes the script, not the meaning.
>
> Example: `నమస్కారం` becomes `namaskaram`; it is not translated to "hello".

The application supports direct text input as well as text extracted from documents and images.

---

## Contents

- [Overview](#overview)
- [Capabilities](#capabilities)
- [Application Architecture](#application-architecture)
- [Application Flow](#application-flow)
- [Document Lifecycle](#document-lifecycle)
- [Supported Languages and Files](#supported-languages-and-files)
- [Frontend](#frontend)
- [Backend](#backend)
- [API Reference](#api-reference)
- [Document APIs](#document-apis)
- [API Error Handling](#api-error-handling)
- [Configuration and Limits](#configuration-and-limits)
- [Document Storage](#document-storage)
- [Quick Start](#quick-start)
- [Frontend Setup](#frontend-setup)
- [Running the Full Application Locally](#running-the-full-application-locally)
- [Production Deployment](#production-deployment)
- [Testing](#testing)
- [Project Layout](#project-layout)
- [Security and Validation](#security-and-validation)
- [Known Limitations](#known-limitations)
- [Future Improvements](#future-improvements)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

The Universal Multilingual Transliteration application provides a web-based interface and REST API for converting Indian-language content from native scripts into Latin characters.

The application supports:

- Direct text transliteration
- File upload and processing
- Automatic language detection
- Optional language selection
- PDF text extraction
- Scanned PDF OCR
- DOCX text extraction
- Image OCR
- Transliteration provider abstraction
- User-specific document history
- Stored document reopening
- Document deletion
- Light and dark themes
- Swagger/OpenAPI API documentation

The application is organized into separate frontend, API, service, detection, extraction, OCR, provider, and storage responsibilities.

---

## Capabilities

### Text Transliteration

Users can enter or paste text directly into the Transliteration Workspace.

Example:

```text
నమస్కారం
```

Result:

```text
namaskaram
```

The API can automatically detect the language or accept an optional language value.

### File Transliteration

The application supports:

- `.txt`
- `.pdf`
- `.docx`
- `.png`
- `.jpg`
- `.jpeg`

Uploaded files are processed through the appropriate extraction pipeline before transliteration.

### Automatic Language Detection

The application can detect supported languages from the input text.

For example:

```text
नमस्ते
```

can be detected as:

```text
hindi
```

and:

```text
తిన్నావా?
```

can be detected as:

```text
telugu
```

An optional language can also be supplied when the language is already known. The application uses language detection together with script-based fallback handling when automatic detection is inconclusive.

### OCR

Images are processed using OCR. Scanned PDFs can also use OCR when normal embedded PDF text extraction does not provide usable text.

### Document History

Successfully processed uploaded documents are stored with their metadata and transliteration result.

The current implementation associates uploaded documents with a browser-generated `user_id`. The frontend stores this identifier in browser local storage and sends it with document-related API requests.

Users can:

- View previously processed documents
- Search documents
- Filter by file type
- Filter by language
- Open a previously processed document
- View its original content
- View its transliteration
- Delete documents

Document history is filtered by `user_id`, so documents created under one browser user identifier are not returned for a different identifier.

### Theme Support

The frontend supports:

- Light theme
- Dark theme

The selected theme is stored in browser local storage so that the preference remains available when the application is reopened.

---

## Application Architecture

The application consists of two primary layers:

```text
┌──────────────────────────────────────────────┐
│                 React Frontend                │
│                                                │
│ Dashboard                                     │
│ Transliteration Workspace                     │
│ History                                       │
│ Settings                                      │
│                                                │
│ API Service Layer                             │
└──────────────────────┬─────────────────────────┘
                        │
                        │ REST API
                        ▼
┌──────────────────────────────────────────────┐
│                 Flask Backend                 │
│                                                │
│ Flask-RESTX API                               │
│ Request Validation                            │
│ File Processing                               │
│ Language Detection                            │
│ Transliteration                               │
│ OCR                                           │
│ Document Storage                              │
└──────────────────────┬─────────────────────────┘
                        │
               ┌────────┴────────┐
               ▼                 ▼
        SQLite Database    File Storage
```

---

## Application Flow

### Text Flow

```text
User enters text
       │
       ▼
React Transliteration Workspace
       │
       ▼
POST /api/v1/transliterate/text
       │
       ▼
Request validation
       │
       ▼
Language detection
       │
       ▼
Provider selection
       │
       ▼
Transliteration
       │
       ▼
JSON response
       │
       ▼
React displays result
```

### File Flow

```text
User selects file
       │
       ▼
React file upload
       │
       ▼
POST /api/v1/transliterate/file
       │
       ▼
File validation
       │
       ▼
File type detection
       │
       ├── TXT
       │
       ├── PDF
       │      ├── Embedded text extraction
       │      └── OCR fallback
       │
       ├── DOCX
       │
       └── Image
              └── OCR
       │
       ▼
Extracted text validation
       │
       ▼
Language detection
       │
       ▼
Transliteration
       │
       ▼
Document storage
       │
       ├── SQLite metadata
       └── Physical uploaded file
       │
       ▼
API response
       │
       ▼
React displays result
```

---

## Document Lifecycle

Uploaded documents follow this lifecycle:

```text
Upload
   │
   ▼
Validate
   │
   ▼
Extract text
   │
   ▼
Detect language
   │
   ▼
Transliterate
   │
   ▼
Store document
   │
   ├── File
   └── Metadata + user_id
   │
   ▼
History
   │
   ├── Open
   └── Delete
```

When a document is deleted:

```text
Delete request
      │
      ▼
Find document metadata
      │
      ▼
Delete physical file
      │
      ▼
Delete SQLite record
```

---

## Supported Languages and Files

### Transliteration

| Language | Handling                               |
| -------- | --------------------------------------- |
| Telugu   | Aksharamukha transliteration           |
| Hindi    | Aksharamukha transliteration           |
| Marathi  | Aksharamukha transliteration           |
| Tamil    | Aksharamukha transliteration           |
| Bengali  | Aksharamukha transliteration           |
| Kannada  | Aksharamukha transliteration           |
| Gujarati | Aksharamukha transliteration           |
| Odia     | Aksharamukha transliteration           |
| Punjabi  | Aksharamukha transliteration           |
| Assamese | Aksharamukha/custom detection handling |
| English  | Returned unchanged                     |

Language detection is configured for supported Indian languages and English. The application also contains script-based fallback handling when automatic detection is inconclusive.

### File Inputs

| File type     | Extensions               | Processing                                              |
| ------------- | ------------------------ | -------------------------------------------------------- |
| Plain text    | `.txt`                   | Direct extraction                                         |
| PDF           | `.pdf`                   | Embedded-text extraction with scanned-PDF OCR fallback   |
| Word document | `.docx`                  | Paragraph and table-cell extraction                       |
| Image         | `.png`, `.jpg`, `.jpeg`  | OCR                                                        |

`.doc` files are not currently supported.

---

## Frontend

The frontend is implemented using React.

### Frontend Pages

**Dashboard** — Provides the main application landing/workspace view.

**Transliteration Workspace** — The main transliteration interface. It supports:

- Text input
- Language selection
- Auto language detection
- Text transliteration
- File upload
- PDF preview
- Image preview
- TXT preview
- DOCX extracted-text preview
- Transliteration output
- Copy-to-clipboard
- Clear/reset functionality
- File replacement
- Processing state
- Error display

The frontend supports a maximum text length of `100,000` characters.

**History** — Displays previously stored documents belonging to the current browser user identifier. Features include:

- Document listing
- Search
- File-type filtering
- Language filtering
- Document status
- Creation date
- Open document
- Delete document
- Delete confirmation modal
- Loading state
- Empty state
- Error state

Opening a document navigates to the Transliteration Workspace with its document ID:

```text
/transliterate?documentId=<document_id>
```

**Settings** — Provides application settings and configuration-related frontend controls.

### Frontend Routing

The React application uses `react-router-dom`.

Current routes:

| Route             | Page                       |
| ----------------- | -------------------------- |
| `/`               | Dashboard                  |
| `/transliterate`  | Transliteration Workspace  |
| `/history`        | History                    |
| `/settings`       | Settings                   |

Saved documents can be opened through:

```text
/transliterate?documentId=<document_id>
```

#### Vercel SPA Routing

The frontend contains `frontend/vercel.json` with a rewrite for React client-side routes. The configuration keeps the `/api/*` rewrite behavior and rewrites other frontend routes to `index.html`, allowing routes such as `/history` and `/settings` to work correctly when the browser is refreshed or a route is opened directly.

### Frontend API Integration

The frontend communicates with the backend through `frontend/src/services/api.js`.

The production API base URL is:

```text
https://multilingual-transliteration-api.onrender.com/api/v1
```

The local development backend URL can be used by commenting/uncommenting the corresponding configuration in `api.js`.

The frontend API service provides functions including:

```javascript
transliterateText();
transliterateFile();

getDocuments();
getDocument();
deleteDocument();
```

The service also handles:

- JSON response parsing
- Backend error messages
- Connection errors
- Missing document IDs
- HTTP failures

### Frontend User ID

The frontend generates a browser-specific identifier when one does not already exist: `transliteration_user_id`.

The identifier is stored in browser `localStorage`. The same identifier is sent with document upload and document-history requests, for example:

```text
POST /api/v1/transliterate/file
```

with:

```text
user_id=<current-browser-user-id>
```

and:

```text
GET /api/v1/documents?user_id=<current-browser-user-id>
```

This allows the backend to return document history for the current browser user rather than returning all documents.

A private/incognito browser session has separate browser storage, so it receives a different user identifier and does not automatically see history created under another browser session.

---

## Backend

The backend is implemented using:

- Python
- Flask
- Flask-RESTX
- SQLite
- Aksharamukha
- OCR services
- PDF extraction
- DOCX extraction

The backend is organized into separate layers for:

```text
API
Detectors
Providers
Services
Storage
Configuration
```

---

## API Reference

### Base URL

Local:

```text
http://127.0.0.1:5000/api/v1
```

Production:

```text
https://multilingual-transliteration-api.onrender.com/api/v1
```

### Endpoints

| Method   | Endpoint                                | Description                             |
| -------- | ---------------------------------------- | ---------------------------------------- |
| `GET`    | `/api/v1/health`                         | Service health check                     |
| `POST`   | `/api/v1/transliterate/text`             | Transliterate text                       |
| `POST`   | `/api/v1/transliterate/file`             | Process and transliterate uploaded file  |
| `GET`    | `/api/v1/documents`                      | Get documents for a user                 |
| `GET`    | `/api/v1/documents/<document_id>`        | Get one document                         |
| `GET`    | `/api/v1/documents/<document_id>/file`   | Retrieve stored physical file            |
| `DELETE` | `/api/v1/documents/<document_id>`        | Delete document                          |

### Health Check

```powershell
curl http://127.0.0.1:5000/api/v1/health
```

### Transliterate Text

```powershell
curl -X POST http://127.0.0.1:5000/api/v1/transliterate/text `
  -H "Content-Type: application/json" `
  -d '{"text":"నమస్కారం"}'
```

Optional language:

```json
{
  "text": "నమస్కారం",
  "language": "telugu"
}
```

Example response:

```json
{
  "success": true,
  "data": {
    "original_text": "నమస్కారం",
    "language": "telugu",
    "transliterated_text": "namaskaram",
    "provider": "AksharamukhaProvider",
    "provider_type": "local",
    "confidence": null
  }
}
```

### Transliterate File

The file endpoint accepts a multipart upload.

Example:

```powershell
curl -X POST http://127.0.0.1:5000/api/v1/transliterate/file `
  -F "file=@sample_files/telugu_example.docx" `
  -F "user_id=<user-id>"
```

The response includes information such as:

- Document ID
- Source filename
- Original extracted text
- Detected language
- Transliteration
- Provider
- Provider type
- Confidence
- Status
- Creation timestamp

---

## Document APIs

### Get All Documents

```text
GET /api/v1/documents?user_id=<user_id>
```

The `user_id` query parameter is required.

Example:

```json
{
  "success": true,
  "data": {
    "documents": [],
    "count": 0
  }
}
```

The backend queries documents using the supplied user identifier:

```sql
SELECT ...
FROM documents
WHERE user_id = ?
ORDER BY created_at DESC
```

This prevents the History page from returning documents belonging to another browser user identifier.

### Get One Document

```text
GET /api/v1/documents/<document_id>
```

Used by the frontend when opening a saved document from History.

### Get Stored Document File

```text
GET /api/v1/documents/<document_id>/file
```

Returns the actual stored file.

### Delete Document

```text
DELETE /api/v1/documents/<document_id>
```

The delete operation removes:

1. The physical stored file
2. The corresponding SQLite metadata record

---

## API Error Handling

Errors use a predictable response structure:

```json
{
  "success": false,
  "message": "Error description"
}
```

Common errors include:

- Missing request body
- Missing text
- Empty text
- Text exceeding the configured limit
- Missing file
- Empty file
- Unsupported extension
- Invalid file content
- Invalid PDF
- Invalid DOCX
- Invalid image
- OCR extraction failure
- PDF extraction failure
- Unknown language
- Language mismatch
- Missing user ID
- Document not found
- Stored file not found
- Document storage failure

---

## Configuration and Limits

Application settings are defined in `app/config.py`.

Current limits include:

| Setting              | Value                                             |
| --------------------- | -------------------------------------------------- |
| Maximum upload size   | 10 MB                                             |
| Maximum text length   | 100,000 characters                                |
| Accepted extensions   | `.txt`, `.pdf`, `.docx`, `.png`, `.jpg`, `.jpeg`  |

The frontend also limits direct text input to `100,000` characters.

File processing also has a client-side processing timeout, and additionally validates actual file content rather than trusting the filename extension alone.

---

## Document Storage

During development, uploaded documents are stored under `storage/documents/`.

Document metadata and transliteration results are stored in `storage/documents.db`.

The database contains information including:

```text
id
filename
stored_filename
file_type
file_path
user_id
language
status
original_text
transliterated_text
provider
provider_type
confidence
created_at
```

Stored filenames use generated UUIDs rather than the user's original filename. The original filename is retained as metadata for display in the application.

---

## Quick Start

### Backend Prerequisites

- Python 3.10 or later
- pip

Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install backend dependencies:

```powershell
pip install -r requirements.txt
```

Run the backend:

```powershell
python run.py
```

The API runs at:

```text
http://127.0.0.1:5000
```

Swagger/OpenAPI UI:

```text
http://127.0.0.1:5000/
```

---

## Frontend Setup

The frontend is a React application.

From the frontend directory:

```powershell
cd frontend
npm install
```

Start the frontend:

```powershell
npm run dev
```

For local development, configure `frontend/src/services/api.js` to use:

```text
http://127.0.0.1:5000/api/v1
```

For production, it uses:

```text
https://multilingual-transliteration-api.onrender.com/api/v1
```

---

## Running the Full Application Locally

The application consists of two development processes.

**Backend:**

```powershell
python run.py
```

The Flask backend runs at `127.0.0.1:5000`.

**Frontend:**

From the `frontend` directory:

```powershell
npm run dev
```

Both processes are required when testing the complete application locally. The frontend sends API requests to the configured backend URL.

---

## Production Deployment

The current deployment uses separate frontend and backend hosting.

### Backend

The Flask backend is deployed on Render.

Production API:

```text
https://multilingual-transliteration-api.onrender.com
```

API base path:

```text
https://multilingual-transliteration-api.onrender.com/api/v1
```

### Frontend

The React frontend is deployed on Vercel. The frontend production build communicates with the Render backend through the production API URL configured in `frontend/src/services/api.js`.

### Deployment Flow

```text
Developer changes
       │
       ▼
Git commit
       │
       ▼
GitHub feature/frontend
       │
       ├──────────────► Render
       │                 Flask backend
       │
       └──────────────► Vercel
                         React frontend
```

Frontend routing is configured in `frontend/vercel.json`. The Vercel configuration preserves the `/api/*` rewrite and provides an SPA fallback to `index.html` for React routes.

---

## Testing

The backend has a pytest test suite.

Run:

```powershell
pytest -q
```

Python syntax checks:

```powershell
python -m py_compile app/services/document_storage_service.py
python -m py_compile app/services/transliteration_service.py
python -m py_compile app/api/documents.py
python -m py_compile app/api/transliteration.py
```

Validate the Vercel configuration:

```powershell
python -m json.tool frontend/vercel.json
```

Git whitespace validation:

```powershell
git diff --check
```

Manual testing includes:

- Text transliteration
- Hindi language detection
- Telugu language detection
- TXT upload
- DOCX upload
- Image upload
- Document storage
- User-specific History
- Opening stored documents
- Document deletion
- Private/incognito browser history isolation
- Production frontend/backend communication
- Direct frontend route refresh handling

---

## Project Layout

```text
multilingual-transliteration-api/
│
├── app/
│   ├── api/
│   │   ├── response.py
│   │   ├── health.py
│   │   ├── transliteration.py
│   │   └── documents.py
│   │
│   ├── detectors/
│   │   └── ...
│   │
│   ├── providers/
│   │   └── ...
│   │
│   ├── services/
│   │   ├── document_storage_service.py
│   │   ├── file_processing_service.py
│   │   ├── file_extraction_service.py
│   │   ├── docx_extraction_service.py
│   │   ├── scanned_pdf_service.py
│   │   ├── ocr_service.py
│   │   └── transliteration_service.py
│   │
│   ├── __init__.py
│   └── config.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   │   └── api.js
│   │   └── App.jsx
│   │
│   ├── public/
│   ├── package.json
│   ├── vercel.json
│   └── vite.config.js
│
├── sample_files/
├── tests/
├── storage/
│   ├── documents/
│   └── documents.db
│
├── requirements.txt
├── run.py
└── README.md
```

---

## Security and Validation

The application performs validation at multiple stages.

**Filename Validation** — Uploaded filenames are validated before processing.

**Extension Validation** — Only configured file extensions are accepted.

**Content Validation** — The application validates actual file content rather than relying only on the filename extension:

```text
PDF   → PDF signature validation
DOCX  → ZIP/package validation
Image → Image content validation
```

**File Size Validation** — Uploads exceeding the configured maximum size are rejected.

**Text Length Validation** — Extracted text exceeding the configured maximum length is rejected.

**Rate Limiting** — The API applies rate limits to transliteration endpoints according to the backend configuration.

---

## Known Limitations

- Transliteration quality depends on the input and underlying provider.
- OCR quality depends on image/document quality.
- Short or mixed-script input can make language detection ambiguous.
- Devanagari is shared by multiple languages, so a language override may be useful for short text.
- `.doc` files are not supported.
- Large documents can require significant processing time.
- The frontend uses a client-side processing timeout for file processing.
- SQLite and local filesystem storage are currently used for document storage.
- Browser-generated user IDs are not a substitute for full account authentication and authorization.
- Current document-history isolation is based on the browser's stored `user_id`.
- Production deployment uses separate Render and Vercel services.

---

## Future Improvements

- Production-grade database support
- Cloud object storage for uploaded documents
- Background document processing
- Job/status tracking for large files
- More OCR languages
- Additional Indian languages
- Improved mixed-language detection
- More transliteration providers
- Full user authentication and authorization
- Containerization
- CI/CD pipeline
- Frontend automated testing
- Backend API integration testing
- Monitoring and structured logging
- Improved production persistence and scaling

---

## Contributing

1. Create a focused branch.
2. Keep API, service, detector, provider, storage, and frontend responsibilities separated.
3. Add or update tests for behavior changes.
4. Run the test suite before opening a pull request:

```powershell
pytest -q
```

For frontend changes, also run the frontend's configured lint/build/test commands before submitting changes.

Before committing configuration changes, validate relevant files, for example:

```powershell
python -m json.tool frontend/vercel.json
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

# Universal Multilingual Transliteration API

A full-stack multilingual transliteration application that converts supported Indian-language text into Latin characters while preserving pronunciation.

The application supports direct text input as well as text extracted from documents and images.

> Transliteration changes the script, not the meaning.
> For example, `నమస్కారం` becomes `namaskaram`; it is not translated to "hello".

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
- [Document Storage](#document-storage)
- [Quick Start](#quick-start)
- [Frontend Setup](#frontend-setup)
- [Running the Full Application](#running-the-full-application)
- [Testing](#testing)
- [Project Layout](#project-layout)
- [Security and Validation](#security-and-validation)
- [Known Limitations](#known-limitations)
- [Future Improvements](#future-improvements)
- [Contributing](#contributing)
- [License](#license)

---

# Overview

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
- Document history
- Stored document reopening
- Document deletion
- Light and dark themes
- Swagger/OpenAPI API documentation

The application is designed with separate frontend, API, service, detection, extraction, OCR, provider, and storage responsibilities.

---

# Capabilities

## Text Transliteration

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

---

## File Transliteration

The application supports:

- `.txt`
- `.pdf`
- `.docx`
- `.png`
- `.jpg`
- `.jpeg`

Uploaded files are processed through the appropriate extraction pipeline before transliteration.

---

## Automatic Language Detection

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

An optional language can also be supplied when the language is already known.

---

## OCR

Images are processed using OCR.

Scanned PDFs can also use OCR when normal embedded PDF text extraction does not provide usable text.

---

## Document History

Successfully processed uploaded documents are stored with their metadata and transliteration result.

Users can:

- View previously processed documents
- Search documents
- Filter by file type
- Filter by language
- Open a previously processed document
- View its original content
- View its transliteration
- Delete documents

---

## Theme Support

The frontend supports:

- Light theme
- Dark theme

The selected theme is stored in browser local storage so that the preference remains available when the application is reopened.

---

# Application Architecture

The application consists of two primary layers:

```text
┌──────────────────────────────────────────────┐
│                  React Frontend               │
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
│                Flask Backend                  │
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
           ┌────────────┴────────────┐
           ▼                         ▼
      SQLite Database          File Storage
```

---

# Application Flow

## Text Flow

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

---

## File Flow

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

# Document Lifecycle

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
   └── Metadata
   │
   ▼
History
   │
   ├── Open
   │
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

# Supported Languages and Files

## Transliteration

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

Language detection is configured for supported Indian languages and English.

The application also contains script-based fallback handling when automatic detection is inconclusive.

---

## File Inputs

| File type     | Extensions              | Processing                                             |
| ------------- | ------------------------ | -------------------------------------------------------- |
| Plain text    | `.txt`                  | Direct extraction                                       |
| PDF           | `.pdf`                  | Embedded-text extraction with scanned-PDF OCR fallback  |
| Word document | `.docx`                 | Paragraph and table-cell extraction                     |
| Image         | `.png`, `.jpg`, `.jpeg` | OCR                                                      |

`.doc` files are not currently supported.

---

# Frontend

The frontend is implemented using React.

## Frontend Pages

### Dashboard

Provides the main application landing/workspace view.

---

### Transliteration Workspace

The main transliteration interface.

It supports:

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

The frontend supports a maximum text length of:

```text
100,000 characters
```

The file processing UI also has a client-side processing timeout.

---

### History

The History page displays previously stored documents.

Features include:

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

Opening a document navigates to the Transliteration Workspace with its document ID.

Example:

```text
/transliterate?documentId=<document_id>
```

---

### Settings

The Settings page provides application settings and configuration-related frontend controls.

---

## Frontend Routing

The React application uses `react-router-dom`.

Current routes:

| Route             | Page                       |
| ----------------- | --------------------------- |
| `/`               | Dashboard                   |
| `/transliterate`  | Transliteration Workspace   |
| `/history`        | History                     |
| `/settings`       | Settings                    |

Saved documents can be opened through:

```text
/transliterate?documentId=<document_id>
```

---

## Frontend API Integration

The frontend communicates with the backend through a centralized API service located at:

```text
frontend/src/services/api.js
```

Base API path:

```text
/api/v1
```

The frontend API service currently provides:

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

---

## Frontend Document Loading

When a document is opened from History, the application navigates to:

```text
/transliterate?documentId=<document_id>
```

The Transliteration Workspace reads the document ID and requests:

```text
GET /api/v1/documents/<document_id>
```

The saved document information is then restored into the workspace.

For stored files, the frontend uses:

```text
GET /api/v1/documents/<document_id>/file
```

to display the physical document when supported.

---

# Backend

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

# API Reference

Base URL:

```text
/api/v1
```

## Endpoints

| Method   | Endpoint                                | Description                             |
| -------- | ---------------------------------------- | ---------------------------------------- |
| `GET`    | `/api/v1/health`                        | Service health check                    |
| `POST`   | `/api/v1/transliterate/text`            | Transliterate text                      |
| `POST`   | `/api/v1/transliterate/file`            | Process and transliterate uploaded file |
| `GET`    | `/api/v1/documents`                     | Get stored documents                    |
| `GET`    | `/api/v1/documents/<document_id>`       | Get one document                        |
| `GET`    | `/api/v1/documents/<document_id>/file`  | Retrieve stored physical file           |
| `DELETE` | `/api/v1/documents/<document_id>`       | Delete document                         |

---

## Health Check

```powershell
curl http://127.0.0.1:5000/api/v1/health
```

Example response:

```json
{
  "success": true,
  "message": "API is healthy"
}
```

---

## Transliterate Text

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

Successful response:

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

---

## Transliterate File

Send a `multipart/form-data` request with a `file` field:

```powershell
curl -X POST http://127.0.0.1:5000/api/v1/transliterate/file `
  -F "file=@sample_files/telugu_example.docx"
```

The response includes:

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

Example:

```json
{
  "success": true,
  "data": {
    "document_id": "document-uuid",
    "filename": "telugu_example.docx",
    "original_text": "నమస్కారం",
    "language": "telugu",
    "transliterated_text": "namaskaram",
    "provider": "AksharamukhaProvider",
    "provider_type": "local",
    "confidence": null,
    "status": "Completed",
    "created_at": "2026-01-01T00:00:00+00:00"
  }
}
```

---

## Document APIs

### Get all documents

```text
GET /api/v1/documents
```

Example response structure:

```json
{
  "success": true,
  "data": {
    "documents": [],
    "count": 0
  }
}
```

### Get one document

```text
GET /api/v1/documents/<document_id>
```

Used by the frontend when opening a saved document from History.

### Get stored document file

```text
GET /api/v1/documents/<document_id>/file
```

Returns the actual stored file. Used by the frontend to display stored PDF and image files.

### Delete document

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
- Document not found
- Stored file not found
- Document storage failure

---

# Configuration and Limits

Application settings are defined in:

```text
app/config.py
```

Current limits:

| Setting              | Value                                             |
| --------------------- | -------------------------------------------------- |
| Maximum upload size   | 10 MB                                              |
| Maximum text length   | 100,000 characters                                 |
| Accepted extensions   | `.txt`, `.pdf`, `.docx`, `.png`, `.jpg`, `.jpeg`  |

The frontend also limits direct text input to:

```text
100,000 characters
```

The frontend file-processing workflow has a client-side timeout of:

```text
3 minutes
```

File processing additionally validates actual file content rather than trusting the filename extension alone.

---

# Document Storage

During development, uploaded documents are stored under:

```text
storage/documents/
```

Document metadata and transliteration results are stored in:

```text
storage/documents.db
```

The database contains information including:

```text
id
filename
stored_filename
file_type
file_path
language
status
original_text
transliterated_text
provider
provider_type
confidence
created_at
```

Stored filenames use generated UUIDs rather than the user's original filename, e.g. `<uuid>.pdf`. The original filename is retained as metadata for display in the application.

---

# Quick Start

## Backend Prerequisites

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

# Frontend Setup

The frontend is a React application.

From the frontend directory, install the dependencies:

```powershell
npm install
```

Start the frontend using the project's configured development command:

```powershell
npm run dev
```

The exact development port depends on the frontend configuration.

The frontend communicates with the backend through:

```text
/api/v1
```

---

# Running the Full Application

The application consists of two development processes.

## Backend

```text
Flask
   ↓
127.0.0.1:5000
```

## Frontend

```text
React
   ↓
Development frontend server
```

The frontend sends API requests to:

```text
/api/v1
```

---

# Testing

The backend has a pytest test suite.

Run:

```powershell
pytest -q
```

The test suite covers areas including:

- API validation
- Text transliteration
- Language detection
- Language mismatch handling
- File processing
- PDF extraction
- DOCX extraction
- OCR paths
- Input limits

In addition to automated tests, the application has been manually verified through the frontend for:

- Text transliteration
- Hindi language detection
- Telugu language detection
- TXT upload
- Document storage
- History
- Opening stored documents
- Document deletion

---

## Frontend End-to-End Flow

The main frontend workflow is:

```text
Dashboard
    │
    ▼
Transliteration
    │
    ├── Enter text
    │      ↓
    │   Transliterate
    │
    └── Upload file
           ↓
       Process file
           ↓
       Display result
           ↓
       Store document
           ↓
         History
           │
           ├── Search
           ├── Filter
           ├── Open
           └── Delete
```

---

# Project Layout

The project contains separate backend and frontend sections.

```text
multilingual-transliteration/
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
│   │   │   ├── layout/
│   │   │   │   └── AppLayout.jsx
│   │   │   │
│   │   │   └── transliteration/
│   │   │       └── TransliterationWorkspace.jsx
│   │   │
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Transliterate.jsx
│   │   │   ├── History.jsx
│   │   │   └── Settings.jsx
│   │   │
│   │   ├── services/
│   │   │   └── api.js
│   │   │
│   │   └── App.jsx
│   │
│   └── package.json
│
├── sample_files/
│
├── tests/
│
├── storage/
│   ├── documents/
│   └── documents.db
│
├── requirements.txt
├── run.py
└── README.md
```

> The exact frontend directory and build configuration should match the repository's current project structure.

---

# Security and Validation

The application performs validation at multiple stages.

## Filename validation

Uploaded filenames are validated before processing.

## Extension validation

Only configured file extensions are accepted.

## Content validation

The application validates actual file content rather than relying only on the filename extension:

```text
PDF   → PDF signature validation
DOCX  → ZIP/package validation
Image → Image content validation
```

## File size validation

Uploads exceeding the configured maximum size are rejected.

## Text length validation

Extracted text exceeding the configured maximum length is rejected.

## Rate limiting

The API applies rate limits to transliteration endpoints.

Current limits:

```text
Text transliteration
60 requests per minute

File transliteration
10 requests per minute
```

---

# Known Limitations

- Transliteration quality depends on the input and underlying provider.
- OCR quality depends on image/document quality.
- OCR is currently configured primarily for Telugu and English.
- Short or mixed-script input can make language detection ambiguous.
- Devanagari is shared by multiple languages, so a language override may be useful for short text.
- `.doc` files are not supported.
- Large documents can require significant processing time.
- The frontend currently uses a client-side processing timeout for file processing.
- SQLite and local filesystem storage are intended for the current development setup rather than a distributed production storage architecture.
- Production deployment configuration is not yet included.

---

# Future Improvements

- Production database support
- Cloud object storage for uploaded documents
- Background document processing
- Job/status tracking for large files
- More OCR languages
- Additional Indian languages
- Improved mixed-language detection
- More transliteration providers
- User authentication and authorization
- User-specific document history
- Production deployment configuration
- Containerization
- CI/CD pipeline
- Frontend automated testing
- Backend API integration testing
- Monitoring and structured logging

---

# Contributing

1. Create a focused branch.
2. Keep API, service, detector, provider, storage, and frontend responsibilities separated.
3. Add or update tests for behavior changes.
4. Run the test suite before opening a pull request:

```powershell
pytest -q
```

For frontend changes, also run the frontend's configured lint/build/test commands before submitting changes.

---

## License

This project is licensed under the MIT License. See the
[LICENSE](LICENSE) file for details.

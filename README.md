# Institute Intelligent Document Assistant

A Flask-based retrieval-augmented generation (RAG) application for asking questions about institute PDF documents. The project combines document ingestion, permission-aware retrieval, hybrid search, and LLM-generated answers with source references.

## Core capabilities

- Student registration and login.
- Admin-only PDF document management.
- Public and private document access, including grants for individual students.
- PDF text extraction with optional OCR for scanned documents.
- Sentence Transformer embeddings and FAISS semantic search.
- BM25 lexical retrieval combined with semantic retrieval using Reciprocal Rank Fusion (RRF).
- Optional CrossEncoder reranking.
- Groq-powered answer generation with source document and page markers.
- Per-user conversation history and retrieval diagnostics.

## Architecture overview

```text
PDF upload
   |
Text extraction / optional OCR
   |
Chunking + metadata + access-control labels
   |
Lexical index (BM25) + semantic embeddings (FAISS)
   |
Permission filtering before retrieval
   |
Hybrid ranking (RRF) + optional reranking
   |
LLM answer generation
   |
Answer with document / page source markers
```

The permission filter is applied before semantic and lexical retrieval so a student's query is restricted to documents they are allowed to access.

## Technology

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Authentication and sessions | Flask session-based authentication, CSRF protection |
| Document processing | PDF text extraction, optional Tesseract OCR |
| Embeddings | Sentence Transformers |
| Retrieval | FAISS, BM25, Reciprocal Rank Fusion |
| Reranking | Optional CrossEncoder |
| Generation | Groq API |
| Persistence | SQLite in the development setup |

## Windows setup

Requirements: 64-bit Python 3.11 or 3.12.

```powershell
git clone https://github.com/malikahmad/Institute-Intelligent-Document-Assistant-AI-Powered-RAG-Chatbot.git
cd Institute-Intelligent-Document-Assistant-AI-Powered-RAG-Chatbot

python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

If PowerShell blocks script execution, run the following in the current terminal session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\setup_windows.ps1
```

Do not overwrite an existing `.env` file.

## Configuration

Edit `.env` and configure:

- A long, random `SECRET_KEY`.
- Your `GROQ_API_KEY`.
- A strong `ADMIN_EMAIL` and `ADMIN_PASSWORD`.
- `GROQ_MODEL` to a model currently available to your Groq account.

Keep credentials out of source control. Use `.env.example` for variable names only.

## Start the application

```powershell
.\.venv\Scripts\python.exe app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Typical workflow

1. Sign in using the configured bootstrap administrator account.
2. Upload institute PDFs and mark them public or private.
3. Grant private documents to authorized student accounts.
4. Students register and sign in.
5. Ask questions and inspect the returned document and page references.

## OCR for scanned PDFs

Install Tesseract OCR separately on Windows, then configure `OCR_ENABLED=true` and set `TESSERACT_CMD` to the full path of `tesseract.exe`.

## Security and evaluation notes

- Keep permission checks in the retrieval path; do not rely only on hiding documents in the UI.
- The current evaluation endpoint is a diagnostic, not a validated accuracy, faithfulness, or retrieval benchmark.
- Validate uploaded files, enforce size limits, scan files where appropriate, and protect secrets.
- The project is a development baseline. Before public production use, add a production WSGI server, HTTPS, secure cookie settings, rate limiting, backups, monitoring, database migrations, and stronger operational controls.
- Test for cross-user data leakage and prompt injection in retrieved documents.

## Troubleshooting

| Problem | Check |
|---|---|
| `py` command unavailable | Use `python` as shown above. |
| Groq model not found | Update `GROQ_MODEL` to a model available to your account. |
| Missing API key | Check `.env` and restart Flask. |
| Scanned PDF has no text | Install Tesseract and enable OCR. |
| FAISS installation fails | Use 64-bit Python 3.11/3.12 and update pip. |

## Author

**Ahmad Zulfiqar** — [GitHub](https://github.com/malikahmad) · [LinkedIn](https://www.linkedin.com/in/malik-ahmad-06abb31a1/)

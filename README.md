# Institute Intelligent Document Assistant

Flask-based RAG application for institute PDF documents. Features: student registration/login, admin-only document management, public/private document access grants, PDF text extraction, optional OCR, Sentence Transformer embeddings, BM25 + semantic hybrid retrieval with Reciprocal Rank Fusion, optional CrossEncoder reranking, Groq answer generation with source markers, per-user conversation history, and retrieval diagnostics.

## Windows / VS Code setup
Requires 64-bit Python 3.11 or 3.12. Open this folder in VS Code.

If PowerShell blocks the script:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\setup_windows.ps1
```
Manual installation (does not require `py`):
```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```
If `.env` already exists, do not overwrite it.

Edit `.env`: set a long random `SECRET_KEY`, your `GROQ_API_KEY`, and a strong `ADMIN_EMAIL` / `ADMIN_PASSWORD`. On first startup the app creates the admin user if that email is not already present.

Run:
```powershell
.\.venv\Scripts\python.exe app.py
```
Open http://127.0.0.1:5000

## Workflow
1. Sign in with bootstrap admin credentials.
2. Open Admin and upload PDFs as public or private.
3. Grant private documents to specific student accounts.
4. Students register and sign in.
5. Ask questions. Responses include source document and page references.

## OCR
For scanned PDFs, install Tesseract OCR separately on Windows. Set `OCR_ENABLED=true` and `TESSERACT_CMD` to the full path of `tesseract.exe`.

## Important implementation notes
- Permission filtering happens before semantic/lexical retrieval.
- FAISS index files are persisted/rebuilt during ingestion; the query path currently embeds only ACL-filtered chunks to prevent unauthorized documents from entering a student's retrieval results.
- The evaluation endpoint is a diagnostic, not a validated accuracy/faithfulness benchmark.
- The configured Groq model identifier may change; if Groq reports model-not-found, update `GROQ_MODEL` to a model currently available to your account.
- Sentence Transformer models download on first use and require internet access.
- CSRF is enabled. All browser POST forms include a hidden CSRF token; chat AJAX sends `X-CSRFToken`.

## Troubleshooting
- `py is not recognized`: this project setup uses `python`, not the Windows Python Launcher.
- HTTP 400 on register: refresh the registration page after changes; the hidden CSRF token is present. Check the Flask log for the CSRF failure detail.
- `faiss-cpu` installation error: use 64-bit Python 3.11/3.12 and upgrade pip.
- Groq key missing: configure `.env` and restart Flask.
- Scanned PDFs have no extracted text: configure Tesseract and enable OCR.

## Production hardening
This is a development baseline, not production-certified. Before public deployment, use PostgreSQL, HTTPS, secure cookies, a production WSGI server, rate limiting, malware scanning, strict file validation, backups, monitoring, audit logs, secret management, and tenant isolation if serving multiple institutes. Add database migrations rather than relying on `db.create_all()`.

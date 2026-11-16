# Student Registry

Streamlit dashboard for the existing `main.py` FastAPI app. Backend routes,
models, and `data.json` are unchanged. The frontend uses HTTP exclusively, so a
later PostgreSQL migration can stay behind the same API contract.

## Run (PowerShell, from this folder)

```powershell
.\first_venv\Scripts\python.exe -m pip install -r requirements.txt
.\first_venv\Scripts\python.exe -m uvicorn main:app --reload
```

In another terminal:

```powershell
.\first_venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

Open http://localhost:8501. API documentation is at http://127.0.0.1:8000/docs.
The API URL is editable in the sidebar. Start the backend from this folder
because its JSON storage path is relative to the working directory.

## Tests

```powershell
.\first_venv\Scripts\python.exe -m pytest -q
```

Tests replace backend storage with an isolated in-memory dictionary. They do
not write to your saved `data.json`. Coverage includes real FastAPI CRUD,
filter/sort/pagination contracts, validation, status boundaries, response
normalization, and Streamlit rendering with an API connection and offline.

## Behavior and current backend limitations

- Uses `id_new`, `full_name`, `email`, `major`, `gpa`, and `validate_gpa`.
- Open a profile with the selector below the table to edit or delete it.
- Create/edit dialogs preview GPA status; updates send changed fields only.
- Major filtering is case-sensitive. Combined search/filter/sort and totals
  use fetched records. Default unfiltered pages use `/data_paginate`.
- The current saved data includes GPAs above 10 and a partially populated
  student. They are flagged for review; invalid GPAs are excluded from GPA
  statistics. No records are silently rewritten or invented.
- Missing major fields can make the backend filter/sort routes fail. The UI
  reports the error and falls back to filtering/sorting fetched API data.
- The computed backend GPA status is annotated `bool` but returns strings.
  The UI derives the status using the backend's thresholds.
- The backend update model accepts `id_new`, but sending it can crash the
  route. The frontend keeps IDs read-only and never sends them on update.
- IDs are URL-encoded. Slash-containing IDs cannot be addressed by these
  single-segment backend routes; creation through the UI disallows them.
- JSON storage has no concurrent-write protection or authentication. This
  dashboard is for local development. PostgreSQL is not configured here.
- Activity is session-only (latest 300 requests), not a permanent audit log.

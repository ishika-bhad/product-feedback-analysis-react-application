# Sentiment Analytics Dashboard

A production-ready full-stack sentiment-analysis application. The system analyzes product feedback in real time using a lightweight, CPU-friendly custom NLP component built on **spaCy** and stores analysis history in an **SQLite** database using **SQLAlchemy ORM**. The **React** frontend provides a premium dashboard for submitting feedback, tracking historical logs, and charting sentiment trends over time.

---

## Architecture & Project Structure

The project separates backend and frontend concerns into isolated modular subsystems:

```
Assignment1-React/
│
├── backend/
│   └── app/
│       ├── auth/
│       │   └── bearer.py         # Static Bearer Token verification dependency
│       ├── config/
│       │   └── settings.py       # Configuration parser using pydantic-settings
│       ├── database/
│       │   └── connection.py     # SQLAlchemy engine, SessionLocal, and DB initializers
│       ├── logging/
│       │   ├── logger.py         # Structured JSON logger & file handlers (info/error)
│       │   └── middleware.py     # Execution timer and request-id ContextVar logging
│       ├── models/
│       │   ├── base.py           # Core declarative Base model
│       │   ├── feedback.py       # Feedback database table model
│       │   └── product.py        # Product database table model
│       ├── routes/
│       │   └── feedback.py       # Routes for POST submit, GET history, and GET products
│       ├── schemas/
│       │   ├── common.py         # Global envelope wrapper schemas (APIResponse)
│       │   ├── request.py        # Pydantic input validators (empty strings, UUID validation)
│       │   └── response.py       # Output serialization models
│       ├── services/
│       │   └── sentiment.py      # Rule-based sentiment logic with spaCy en_core_web_sm
│       └── main.py               # FastAPI entrypoint, lifespan triggers, CORS, and exception maps
│
├── react/
│   ├── src/
│   │   ├── charts/
│   │   │   └── TrendChart.tsx    # Sentiment trendline graph component using Recharts
│   │   ├── components/
│   │   │   ├── HistoricalView.tsx# Dropdown selector and feedback grid log table
│   │   │   ├── Metrics.tsx       # Sentiment summary cards (Positive, Negative, Neutral counters)
│   │   │   └── SubmissionForm.tsx# Feedback form, loader state, and sentiment output alert
│   │   ├── services/
│   │   │   └── api.ts            # Client interface, token headers, and request-id verification
│   │   ├── App.tsx               # Dashboard state conductor
│   │   ├── App.css               # Empty stylesheet
│   │   ├── index.css             # Vanilla CSS glassmorphism theme design tokens
│   │   └── main.tsx              # React mounting root
│   ├── package.json              # Node dependencies (Axios, Recharts, Lucide, React)
│   └── vite.config.ts            # Vite compile and build configurations
│
├── tests/
│   └── test_backend.py           # Automated API integration and authentication pytest suite
│
├── .env                          # Backend environment configurations (ignored)
├── .gitignore                    # Git file exclusion configs
├── pyproject.toml                # Root python metadata and packages managed by `uv`
└── README.md                     # Application documentation
```

---

## Technology Stack

- **Backend**: Python 3.11+, FastAPI, Uvicorn, Pydantic v2, Pydantic-Settings, SQLAlchemy, spaCy (`en_core_web_sm`).
- **Dependency Management (Python)**: `uv` package manager.
- **Frontend**: React 18, Vite, TypeScript, Axios, Recharts (charts), Lucide React (icons).
- **Styling**: Custom Vanilla CSS (custom variables, responsive layout, glassmorphism card panels, micro-animations, custom scrollbars).

---

## Security & Verification (Request ID & Authentication)

1. **Bearer Token Authentication**: All backend API endpoints are secured using a static Bearer Token. Clients must pass the header `Authorization: Bearer <token>`.
2. **Dynamic Request ID Validation**:
   - **Feedback Submission**: The React frontend generates a unique UUID `request_id` in the request body. When the backend finishes processing, it returns the same `request_id`. The React client verifies that the returned ID matches the generated one before displaying results to the user.
   - **Historical Retrieval**: When the React client requests historical feedback logs for a product, it generates a new UUID, transmits it in the `X-Request-ID` header, and verifies that the backend returns this same ID inside the response envelope.
3. **Important Security Note**: In production, client-side browser environments should not call token-secured backends directly with static tokens, as client-side code is public. For real systems, use session cookies, dynamic OAuth2 flows, or a BFF (Backend-For-Frontend) proxy layer to secure sensitive credentials.

---

## Setup & Running Guide

### 1. Backend Setup

First, ensure you have the `uv` tool installed on your system. If not, follow instructions from the [Astral UV documentation](https://github.com/astral-sh/uv).

1. **Install Python dependencies and create a virtual environment**:
   ```bash
   uv sync
   ```
2. **Download the spaCy English model**:
   ```bash
   uv run python -m spacy download en_core_web_sm
   ```
3. **Configure Environment Variables**:
   Create a `.env` file in the root project directory:
   ```env
   DATABASE_URL=sqlite:///./sentiment.db
   API_BEARER_TOKEN=supersecrettoken1234567890
   CORS_ORIGINS=http://localhost:5173
   LOG_DIR=logs
   ```
4. **Start the FastAPI Backend**:
   ```bash
   uv run uvicorn backend.app.main:app --reload
   ```
   The backend will be running at `http://127.0.0.1:8000`. You can inspect endpoints and try request payloads at the interactive Swagger UI: `http://127.0.0.1:8000/docs`.

---

### 2. Frontend Setup

1. **Navigate to the `react/` directory and install dependencies**:
   ```bash
   cd react
   npm install
   ```
2. **Configure Environment Variables**:
   Create a `.env` file inside the `react/` directory:
   ```env
   VITE_API_URL=http://localhost:8000
   VITE_API_BEARER_TOKEN=supersecrettoken1234567890
   ```
3. **Start the Vite Dev Server**:
   ```bash
   npm run dev
   ```
   The React dashboard will be running at `http://localhost:5173`. Open this URL in your web browser.

---

## Running the Automated Tests

To execute the test suite (validating endpoint responses, database operations, error formatting, and Bearer token challenges):

1. Set the PYTHONPATH and run pytest:
   ```bash
   # In PowerShell:
   $env:PYTHONPATH="."; uv run pytest
   
   # In Bash/Linux/macOS:
   PYTHONPATH=. uv run pytest
   ```

---

## Logging System

The backend logs every API transaction. Structured JSON logs are formatted and outputted to the console and to log files located inside the directory specified by `LOG_DIR` (e.g. `logs/`):
- `logs/info.log`: Captures all info events (application startup, database initialization, and successful HTTP requests).
- `logs/error.log`: Captures warning, error, and critical exceptions (unhandled server errors, database connectivity errors, and failed authorization attempts).

A sample log output:
```json
{"timestamp": "2026-08-20T10:45:07.123Z", "level": "INFO", "logger": "sentiment_analysis", "message": "POST /api/feedback - Status: 201 - Duration: 65ms", "request_id": "9d9b6264-9b21-4ea7-8b01-faee6a93b4a2", "execution_time_ms": 65, "path": "/api/feedback", "method": "POST", "status_code": 201}
```

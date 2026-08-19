# PR Campaign Assistant

AI-powered tool that helps PR consultants identify relevant journalists for a campaign and prepare personalized outreach pitches.

## Project structure

```text
pr-campaign-assistant/
├── README.md
├── frontend/          # React + TypeScript (Vite)
├── backend/           # FastAPI
├── sample-data/       # Example CSV files
└── docs/              # PRD, architecture, and implementation tasks
```

See [docs/PRD.md](./docs/PRD.md) and [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) for product and technical details.

## Prerequisites

- Node.js 18+
- Python 3.11+
- npm

## Environment configuration

Copy the example environment files and fill in values as needed:

```bash
cp .env.example .env
cp frontend/.env.example frontend/.env
```

| Variable | Location | Description |
| --- | --- | --- |
| `GROQ_API_KEY` | `.env` | LLM provider API key (required in later tasks) |
| `FRONTEND_ORIGIN` | `.env` | Allowed CORS origin for the backend (default: `http://localhost:5173`) |
| `VITE_API_URL` | `frontend/.env` | Backend base URL for the frontend (default: `http://localhost:8000`) |

Do not commit `.env` files. Secrets belong in local environment files only.

## Backend setup

Create and activate a Python virtual environment, then install dependencies:

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Run the API:

```bash
uvicorn app.main:app --reload --port 8000
```

Health check: [http://localhost:8000/health](http://localhost:8000/health)

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The app runs at [http://localhost:5173](http://localhost:5173) and checks the backend health endpoint on load.

## Sample data

Example journalist CSV files are in [`sample-data/`](./sample-data/).

## Development workflow

1. Start the backend (`uvicorn app.main:app --reload --port 8000` from `backend/`).
2. Start the frontend (`npm run dev` from `frontend/`).
3. Open the frontend in a browser and confirm the backend connection status shows as connected.

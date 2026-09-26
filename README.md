# AquaSense AI — Intelligent Water Purifier Filter Prognostics System

AquaSense AI predicts the health and remaining useful life of a water
purifier's filter from water-quality and usage data, so a maintenance
decision is based on how the filter is actually performing rather than a
generic replacement schedule.

The system ships with a physically-grounded **simulated dataset**, so it
works end-to-end with zero physical hardware. The API and data model are
already shaped for a real ESP32 / sensor feed to be dropped in later —
see [Connecting real sensors](#connecting-real-sensors-later).

## Architecture

```
aquasense-ai/
├── backend/            FastAPI + MongoDB + scikit-learn
│   └── app/
│       ├── core/        settings, JWT & password hashing
│       ├── db/           Motor (async MongoDB) connection
│       ├── models/       Pydantic request/response schemas
│       ├── routers/      auth, purifiers, readings, predictions, analytics
│       ├── ml/            synthetic dataset, training script, predictor
│       └── main.py        FastAPI app + startup/shutdown
│   └── scripts/seed_demo_data.py   demo account + 60 days of history
│
├── frontend/            React (Vite) + Recharts + JWT auth
│   └── src/
│       ├── api/            axios client + endpoint helpers
│       ├── context/        auth state, selected-purifier state
│       ├── components/     sidebar, gauge, KPI cards, charts, forms...
│       ├── pages/           Dashboard, Purifiers, Readings, Analytics, History
│       └── styles/          design tokens + component CSS
│
└── docker-compose.yml   mongo + backend + frontend, one command
```

## How the AI model works

`backend/app/ml/dataset.py` simulates how RO/UF cartridges actually degrade:
as a filter ages and processes more water, outlet **TDS** and **turbidity**
rise, **flow rate** drops, and **system pressure** climbs to compensate —
the same signals a real sensor rig would report. Two
`RandomForestRegressor` models are trained on this data
(`app/ml/train_model.py`):

- **Filter Health Score** (0–100)
- **Remaining Useful Life** (days)

At request time, `app/ml/predictor.py` turns a purifier's latest reading
into feature vector, produces both predictions, derives an **alert level**
(`ok` / `watch` / `warning` / `critical`), and generates plain-language
**maintenance insights** plus a **contributing-factors breakdown** (which
signal — TDS, turbidity, flow, pressure, pH — is driving the degradation).

Models are trained automatically the first time the backend starts if no
saved model is found in `app/ml/artifacts/`, so there's nothing to run
manually. Retraining on real sensor data later just means pointing
`train_model.py` at a DataFrame with the same feature schema.

## Getting started

### Option A — Docker Compose (recommended)

```bash
docker compose up --build
```

- API: http://localhost:8000 (docs at `/docs`)
- Frontend: http://localhost:5173

### Option B — Run locally

**Backend**

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                 # edit MONGO_URI etc. if needed
uvicorn app.main:app --reload
```

You need a MongoDB instance running locally (`mongod`) or a connection
string to Atlas in `.env`.

**Seed demo data (optional but recommended):**

```bash
python -m scripts.seed_demo_data
```

This creates a demo account with 60 days of realistic reading + prediction
history:

```
email:    demo@aquasense.ai
password: Demo@1234
```

**Frontend**

```bash
cd frontend
npm install
cp .env.example .env       # point VITE_API_BASE_URL at your backend if not localhost:8000
npm run dev
```

Open http://localhost:5173, sign in with the demo account (or register a
new one), and add your first purifier.

## Using the app

1. **Register / sign in.**
2. **Purifiers** → add a purifier (model, filter type, install date, rated
   life & capacity).
3. **Readings** → log a water-quality reading (TDS, pH, turbidity, flow,
   pressure, usage).
4. **Dashboard** → click "Run prediction" to get a health score, remaining
   life, alert level and AI insights, and watch the trend build up over
   time.
5. **Analytics** → fleet-wide KPIs plus water-quality trend charts.
6. **History** → the full log of every prediction the model has produced.

## Connecting real sensors (later)

The `POST /api/v1/readings` endpoint is the integration point: point an
ESP32 (or any microcontroller) at it with the same JSON body used by the
frontend's reading form (`tds_ppm`, `ph`, `turbidity_ntu`, `flow_rate_lpm`,
`pressure_bar`, `daily_usage_liters`, `usage_frequency_per_day`,
`water_temperature_c`), authenticated with a long-lived JWT. Nothing else
in the system needs to change — the ML pipeline, dashboard, and alerts all
work directly off whatever's in the `readings` collection.

## Deploying the frontend to GitHub Pages

`.github/workflows/deploy-pages.yml` builds the React app and publishes it
to GitHub Pages on every push to `main`. Two things to know before using it:

**GitHub Pages is static-only.** It can host the compiled frontend, but not
the FastAPI backend or MongoDB - those need a real server. Deploy the
`backend/` folder (with its `Dockerfile`) to something like Render, Railway,
Fly.io, or your own VM/VPS first, and connect it to a MongoDB instance
(Atlas's free tier works fine). Until that backend is reachable at a public
URL, the deployed Pages site will load but login/data calls will fail.

**One-time setup:**

1. In the repo, go to **Settings → Pages → Build and deployment** and set
   **Source** to **GitHub Actions**.
2. Go to **Settings → Secrets and variables → Actions → Variables** and add
   a repository variable named `VITE_API_BASE_URL` set to your deployed
   backend's API URL, e.g. `https://your-backend.onrender.com/api/v1`.
   (If you skip this, the build falls back to `http://localhost:8000/api/v1`,
   which only works when you're running the backend on your own machine.)
3. Push to `main` (or run the workflow manually from the **Actions** tab).
   The site will be live at `https://<your-username>.github.io/<repo-name>/`.

Two implementation details the workflow and app already account for so this
works correctly on a project-pages sub-path:
- `vite.config.js` reads `VITE_BASE_PATH`, which the workflow sets to
  `/<repo-name>/` at build time, so built asset URLs resolve correctly.
- The app uses React Router's `HashRouter` (URLs like `/#/dashboard`)
  instead of `BrowserRouter`, since Pages has no server-side rewrite rule
  to send deep-link requests back to `index.html`.

Also update your backend's `CORS_ORIGINS` env var to include your Pages URL
(`https://<your-username>.github.io`) so the browser doesn't block the API
calls.

## Tech stack

- **Frontend:** React 18 (Vite), React Router, Recharts, plain CSS
- **Backend:** FastAPI, Motor (async MongoDB), Pydantic v2
- **Auth:** JWT (python-jose) + bcrypt password hashing (passlib)
- **ML:** scikit-learn (RandomForestRegressor), pandas, numpy, joblib
- **Database:** MongoDB

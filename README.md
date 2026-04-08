# IS2209 DeployHub — Weather Integration Service

A Flask web service integrating OpenWeatherMap API and PostgreSQL, built with CI/CD via GitHub Actions and deployed on Render.

## Live URL
[https://is2209-deployhub.onrender.com]

## Setup

### Prerequisites
- Python 3.11+
- PostgreSQL database (Supabase recommended)
- OpenWeatherMap API key

### Local Development

```bash
git clone https://github.com/oisinfc33-sys/IS2209-DeployHub-.git
cd IS2209-DeployHub-
pip install -r requirements.txt
cp .env.example .env
# Fill in your .env values
python run.py
```

### Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `OPENWEATHER_API_KEY` | OpenWeatherMap API key |
| `FLASK_ENV` | `development` or `production` |
| `SECRET_KEY` | Random secret string |

## Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Main UI — search weather, view history |
| `/weather?city=Dublin` | GET | JSON weather data + saves to DB |
| `/health` | GET | Health check (DB connectivity) |
| `/status` | GET | Status page with diagnostics |

## CI/CD

GitHub Actions runs on every PR and push to `main`:
1. **Lint** — ruff
2. **Tests** — pytest with coverage
3. **Build** — Docker image built and pushed to GHCR
4. **Deploy** — Render auto-deploys from main branch

## Running Tests

```bash
pytest tests/ --cov=app --cov-report=term-missing
```

## Architecture

- **Flask** serves the API and minimal HTML UI
- **PostgreSQL (Supabase)** stores all weather searches
- **OpenWeatherMap API** provides live weather data
- **Docker** containerises the app
- **GitHub Actions** handles CI/CD
- **Render** hosts the live deployment
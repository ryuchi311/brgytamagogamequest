# Docker Deployment Guide - BRGY TAMAGO Quest Hub

This project now ships as a Docker image that you can build and run locally or in your preferred container platform.

## Prerequisites

1. Docker installed (`docker --version`).
2. Environment variables defined via `.env` or directly passed to Docker (you can copy `.env.example` to `.env`).
3. Optional: Install `docker-compose` if you prefer orchestrated local stacks.

## Build & Run (Pure Docker)

1. **Build the image**

   ```bash
   docker build -t brgy-tamago-quest-hub .
   ```

2. **Run locally with backend + frontend**

   ```bash
   docker run --rm -p 8000:8000 -p 8080:8080 \
       --env-file .env \
       -e PORT=8080 \
       -e API_PORT=8000 \
       -e SERVE_FRONTEND=true \
       brgy-tamago-quest-hub
   ```

   The container now launches FastAPI on `API_PORT` and a static server on `PORT`. Set `SERVE_FRONTEND=false` (the default) to run only the API.

3. **Use helper scripts**

   - `./start.sh` (for local development): starts backend on `localhost:8000` and frontend on `localhost:8080` with auto-recovery.
   - `./run-pure-docker.sh` / `./run-docker-8080.sh`: wrappers that expose ports depending on the workflow.

## Environment Variables Reference

| Variable | Description |
| --- | --- |
| `PORT` | Frontend port (default `8080`). |
| `API_PORT` | Backend port (default `8000`). |
| `SERVE_FRONTEND` | Set to `true` to serve static assets alongside the API. |
| `DATABASE_URL` | Postgres connection string. |
| `SUPABASE_*`, `SECRET_KEY`, `TELEGRAM_*`, `TWITTER_*`, `YOUTUBE_API_KEY` | Application credentials and secrets. |

## Docker Compose & Entry Points

- `docker-compose.yml` and `docker-compose.8080.yml` define local stacks for Postgres + API.
- `start-server.sh` is the entrypoint inside the container; it already understands `PORT`, `API_PORT`, and the `SERVE_FRONTEND` toggle.

## Debugging & Troubleshooting

- **Ports already in use**: run `lsof -iTCP -sTCP:LISTEN -P | grep -E '8000|8080'` and stop conflicting processes.
- **Build failures**: clear Docker builder cache with `docker builder prune` and rebuild with `docker build --no-cache -t brgy-tamago-quest-hub .`.
- **Missing secrets**: copy `.env.example` to `.env` and confirm every `SUPABASE`, `TELEGRAM`, and `TWITTER` key is populated before running.
- **Frontend not loading**: ensure `SERVE_FRONTEND=true` or proxy the `frontend/` directory through your own static host.

## Production Notes

For production deployments you may host the image on any orchestrator (Kubernetes, ECS, etc.). Map ports according to your platform and mount secrets/credentials via environment variables or secret managers.

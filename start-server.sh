#!/bin/bash
# Unified startup script for Quest Hub backend (Cloud Run & local containers)
# - Default behaviour (SERVE_FRONTEND != true): run FastAPI on $PORT (Cloud Run)
# - Optional SERVE_FRONTEND=true: also serve static frontend via python http.server

set -euo pipefail

PORT=${PORT:-8080}
HOST=${HOST:-0.0.0.0}
API_PORT=${API_PORT:-8000}
SERVE_FRONTEND=${SERVE_FRONTEND:-false}
FRONTEND_DIR=${FRONTEND_DIR:-frontend}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Launching Quest Hub services"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [[ "$SERVE_FRONTEND" == "true" ]]; then
	echo "🔧 Combined mode enabled (SERVE_FRONTEND=true)"
	echo "   ➤ Backend API  : http://${HOST}:${API_PORT}"
	echo "   ➤ Frontend     : http://${HOST}:${PORT} (serving ${FRONTEND_DIR})"

	python -m uvicorn app.api:app --host "$HOST" --port "$API_PORT" --proxy-headers --forwarded-allow-ips="*" &
	API_PID=$!

	python -m http.server "$PORT" --directory "$FRONTEND_DIR" &
	FRONT_PID=$!

	terminate() {
		echo "\n🛑 Caught shutdown signal, stopping services..."
		kill "$API_PID" "$FRONT_PID" 2>/dev/null || true
		wait "$API_PID" "$FRONT_PID" 2>/dev/null || true
		echo "✅ Services stopped"
		exit 0
	}

	trap terminate INT TERM
	echo "✅ Services running. Press Ctrl+C to stop."
	wait -n "$API_PID" "$FRONT_PID"
	exit $?
else
	echo "   ➤ Backend API : http://${HOST}:${PORT}"
	exec python -m uvicorn app.api:app --host "$HOST" --port "$PORT" --proxy-headers --forwarded-allow-ips="*"
fi

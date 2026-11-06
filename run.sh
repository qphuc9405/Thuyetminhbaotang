#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="$ROOT_DIR/backend/.venv/bin/python"
DB_PATH="${VITUYEN_DB_PATH:-$ROOT_DIR/backend/data/knowledge.sqlite3}"

if [[ ! -x "$PYTHON" ]]; then
  python3 -m venv "$ROOT_DIR/backend/.venv"
fi

if [[ ! -d "$ROOT_DIR/frontend/node_modules" ]]; then
  (cd "$ROOT_DIR/frontend" && npm ci)
fi

if [[ ! -f "$DB_PATH" ]]; then
  "$PYTHON" "$ROOT_DIR/backend/manage.py" seed
fi

backend_pid=""
frontend_pid=""

cleanup() {
  trap - EXIT INT TERM
  [[ -z "$backend_pid" ]] || kill "$backend_pid" 2>/dev/null || true
  [[ -z "$frontend_pid" ]] || kill "$frontend_pid" 2>/dev/null || true
  [[ -z "$backend_pid" ]] || wait "$backend_pid" 2>/dev/null || true
  [[ -z "$frontend_pid" ]] || wait "$frontend_pid" 2>/dev/null || true
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

"$PYTHON" "$ROOT_DIR/backend/server.py" &
backend_pid=$!
(
  cd "$ROOT_DIR/frontend"
  exec ./node_modules/.bin/vite --host 0.0.0.0
) &
frontend_pid=$!

echo "Mở http://localhost:5173 (Ctrl+C để dừng cả hai dịch vụ)"
wait -n "$backend_pid" "$frontend_pid"

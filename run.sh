#!/usr/bin/env bash
# ============================================================================
#  Thuyết minh bảo tàng Vĩ tuyến 17 – chạy toàn bộ hệ thống bằng 1 lệnh
#
#    ./run.sh              chạy web + backend
#    ./run.sh --build      dựng lại kho tư liệu (knowledge base) rồi chạy
#    ./run.sh --setup      chỉ cài đặt (Python venv + npm), không chạy
#    ./run.sh --help       xem hướng dẫn
#
#  Thành phần:
#    frontend/                 web chính (Vite + React)          → http://localhost:5173
#    museum-guide/backend/     kho tư liệu, chatbot, giọng đọc   → cổng 8077 (web gọi qua /mg)
#    backend/                  backend mẫu của repo (tuỳ chọn)   → cổng 8000 (web gọi qua /api)
#
#  Đổi cổng bằng biến môi trường: WEB_PORT=5173 MG_PORT=8077 SAMPLE_PORT=8000 ./run.sh
#  Chọn Python khác: PYTHON=/đường/dẫn/python3 ./run.sh
#  Tương thích bash 3.2 mặc định của macOS (không dùng `wait -n`, mảng kết hợp…).
# ============================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MG="$ROOT/museum-guide"
VENV="$ROOT/.venv"
WEB_PORT="${WEB_PORT:-5173}"
MG_PORT="${MG_PORT:-8077}"
SAMPLE_PORT="${SAMPLE_PORT:-8000}"

DO_BUILD=0
SETUP_ONLY=0
for arg in "$@"; do
  case "$arg" in
    --build) DO_BUILD=1 ;;
    --setup) SETUP_ONLY=1 ;;
    -h|--help) sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Không hiểu tham số: $arg (xem ./run.sh --help)" >&2; exit 2 ;;
  esac
done

# ---------- in ra có màu ----------
if [[ -t 1 ]]; then B=$'\033[1m'; G=$'\033[32m'; Y=$'\033[33m'; R=$'\033[31m'; C=$'\033[36m'; M=$'\033[35m'; N=$'\033[0m'; else B=""; G=""; Y=""; R=""; C=""; M=""; N=""; fi
step() { echo "${B}${C}==>${N} ${B}$*${N}"; }
ok()   { echo "    ${G}✓${N} $*"; }
warn() { echo "    ${Y}!${N} $*" >&2; }
die()  { echo "${R}✗ $*${N}" >&2; exit 1; }
port_busy() { (exec 3<>"/dev/tcp/127.0.0.1/$1") 2>/dev/null; }

[[ -d "$MG/backend" ]] || die "Không thấy $MG/backend – folder museum-guide phải nằm cạnh run.sh."
[[ -d "$ROOT/frontend" ]] || die "Không thấy $ROOT/frontend."

# ---------- 1. Python + venv riêng của dự án ----------
# Dùng venv riêng để không đụng Python của Homebrew/conda (Homebrew chặn pip install toàn cục).
step "Python"
if [[ ! -x "$VENV/bin/python" ]]; then
  PY_BASE="${PYTHON:-}"
  if [[ -z "$PY_BASE" ]]; then
    for c in python3.12 python3.11 python3.13 python3 python; do
      if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then PY_BASE="$c"; break; fi
    done
  fi
  [[ -n "$PY_BASE" ]] || die "Cần Python ≥ 3.10 (brew install python@3.12)."
  echo "    tạo môi trường ảo .venv bằng $("$PY_BASE" -c 'import sys; print(sys.executable, sys.version.split()[0])')"
  "$PY_BASE" -m venv "$VENV"
fi
PY="$VENV/bin/python"
ok "$("$PY" -c 'import sys; print(sys.version.split()[0])') ($VENV)"

# Cài thư viện khi lần đầu chạy hoặc khi requirements.txt thay đổi.
REQ="$MG/backend/requirements.txt"
STAMP="$VENV/.requirements.sha"
REQ_SHA="$(shasum "$REQ" 2>/dev/null | cut -d' ' -f1 || sha1sum "$REQ" | cut -d' ' -f1)"
if [[ ! -f "$STAMP" || "$(cat "$STAMP")" != "$REQ_SHA" ]]; then
  echo "    cài thư viện Python (lần đầu mất vài phút)…"
  "$PY" -m pip install --quiet --upgrade pip
  "$PY" -m pip install --quiet -r "$REQ"
  echo "$REQ_SHA" > "$STAMP"
fi
ok "thư viện Python đã đủ"

# ---------- 2. Node + npm ----------
step "Node.js"
command -v node >/dev/null 2>&1 || die "Cần Node.js ≥ 18 (brew install node)."
NODE_MAJOR="$(node -p 'process.versions.node.split(".")[0]')"
[[ "$NODE_MAJOR" -ge 18 ]] || die "Node.js $(node -v) quá cũ, cần ≥ 18."
LOCK="$ROOT/frontend/package-lock.json"
NSTAMP="$ROOT/frontend/node_modules/.install.sha"
LOCK_SHA="$(shasum "$LOCK" 2>/dev/null | cut -d' ' -f1 || sha1sum "$LOCK" | cut -d' ' -f1)"
if [[ ! -d "$ROOT/frontend/node_modules" || ! -f "$NSTAMP" || "$(cat "$NSTAMP")" != "$LOCK_SHA" ]]; then
  echo "    cài gói npm…"
  (cd "$ROOT/frontend" && npm ci --no-audit --no-fund --loglevel=error)
  echo "$LOCK_SHA" > "$NSTAMP"
fi
ok "node $(node -v), gói npm đã đủ"

# ---------- 3. Cấu hình (.env) ----------
step "Cấu hình"
ENVF="$MG/backend/.env"
if [[ ! -f "$ENVF" ]]; then
  cp "$MG/backend/.env.example" "$ENVF"
  warn "Đã tạo museum-guide/backend/.env từ mẫu. Điền OLLAMA_API_KEY (chatbot) và ELEVENLABS_API_KEY (giọng đọc) vào file này."
  warn "Chưa có khoá vẫn chạy được: chatbot trả lời bằng tư liệu có sẵn, giọng đọc dùng giọng của trình duyệt."
else
  grep -qE '^ELEVENLABS_API_KEY=.+' "$ENVF" && ok "có khoá ElevenLabs" || warn "chưa có ELEVENLABS_API_KEY → dùng giọng trình duyệt"
  if grep -qE '^OLLAMA_HOST=http://(localhost|127\.0\.0\.1)(:[0-9]+)?/?$' "$ENVF"; then
    ok "chatbot dùng Ollama cục bộ (không cần khoá API)"
  else
    grep -qE '^OLLAMA_API_KEY=.+' "$ENVF" && ok "có khoá Ollama" || warn "chưa có OLLAMA_API_KEY → Ollama Cloud dùng chế độ tư liệu dự phòng"
  fi
fi

# ---------- 4. Kho tư liệu ----------
step "Kho tư liệu"
ZONES="$MG/knowledge_base/zones.json"
if [[ "$DO_BUILD" == 0 ]] && ! grep -q '"topics"' "$ZONES" 2>/dev/null; then
  warn "zones.json chưa có phần 4 chủ đề → dựng lại."
  DO_BUILD=1
fi
if [[ "$DO_BUILD" == 1 ]]; then
  echo "    dựng knowledge base…"
  (cd "$MG" && "$PY" scripts/build_knowledge_base.py) || die "Dựng kho tư liệu lỗi (xem thông báo phía trên)."
fi
ok "zones.json sẵn sàng"

if [[ "$SETUP_ONLY" == 1 ]]; then
  echo; echo "${G}Cài đặt xong.${N} Chạy ${B}./run.sh${N} để bật hệ thống."; exit 0
fi

# ---------- 5. Chạy các dịch vụ ----------
PIDS=""
cleanup() {
  trap - EXIT INT TERM
  echo; step "Đang dừng…"
  for p in $PIDS; do kill "$p" 2>/dev/null || true; done
  for p in $PIDS; do wait "$p" 2>/dev/null || true; done
  ok "đã dừng"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

# Gắn nhãn vào từng dòng log để biết dòng nào của dịch vụ nào.
tag() { local t="$1"; while IFS= read -r line; do printf '%s %s\n' "$t" "$line"; done; }

step "Khởi động"
if port_busy "$MG_PORT"; then
  warn "cổng $MG_PORT đang bận – dùng museum-guide đang chạy sẵn (nếu là bản cũ, hãy tắt nó rồi chạy lại)."
else
  (cd "$MG/backend" && exec "$PY" -m uvicorn app.main:app --host 127.0.0.1 --port "$MG_PORT") \
    > >(tag "${M}[museum]${N}") 2>&1 &
  PIDS="$PIDS $!"
fi

if port_busy "$SAMPLE_PORT"; then
  warn "cổng $SAMPLE_PORT đang bận – bỏ qua backend mẫu (không ảnh hưởng nhà trưng bày, chat, giọng đọc)."
else
  if [[ ! -f "$ROOT/backend/data/knowledge.sqlite3" ]]; then
    "$PY" "$ROOT/backend/manage.py" seed > /dev/null 2>&1 || warn "không seed được backend mẫu"
  fi
  (cd "$ROOT/backend" && VITUYEN_PORT="$SAMPLE_PORT" exec "$PY" server.py) > >(tag "${Y}[mẫu]${N}  ") 2>&1 &
  PIDS="$PIDS $!"
fi

# Chờ museum-guide sẵn sàng (nạp kho tư liệu mất vài giây) trước khi bật web.
printf '    chờ museum-guide'
for _ in $(seq 1 60); do
  if curl -fs "http://127.0.0.1:$MG_PORT/api/health" > /dev/null 2>&1; then break; fi
  printf '.'; sleep 1
done
echo
curl -fs "http://127.0.0.1:$MG_PORT/api/health" > /dev/null 2>&1 && ok "museum-guide: http://127.0.0.1:$MG_PORT" || warn "museum-guide chưa trả lời – xem log [museum]"

(cd "$ROOT/frontend" && MG_API="http://127.0.0.1:$MG_PORT" SAMPLE_API="http://127.0.0.1:$SAMPLE_PORT" exec ./node_modules/.bin/vite --host 0.0.0.0 --port "$WEB_PORT" --strictPort) \
  > >(tag "${C}[web]${N}   ") 2>&1 &
WEB_PID=$!
PIDS="$PIDS $WEB_PID"

echo
echo "  ${B}${G}Mở trình duyệt: http://localhost:$WEB_PORT${N}   (Ctrl+C để dừng tất cả)"
echo

# Chạy đến khi một dịch vụ dừng hoặc người dùng bấm Ctrl+C.
while :; do
  for p in $PIDS; do
    if ! kill -0 "$p" 2>/dev/null; then
      warn "một dịch vụ đã dừng (pid $p) – tắt các dịch vụ còn lại."
      exit 1
    fi
  done
  sleep 1
done

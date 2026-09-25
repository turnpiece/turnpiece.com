#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── Colours ──────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
info()    { echo -e "${GREEN}[✓]${NC} $1"; }
warning() { echo -e "${YELLOW}[!]${NC} $1"; }
error()   { echo -e "${RED}[✗]${NC} $1"; exit 1; }

echo ""
echo "  turnpiece.com — local dev startup"
echo "  ──────────────────────────────────"
echo ""

# ── 1. Python virtual environment ────────────────────────────────────────────
VENV_DIR=""
for d in env env312 venv .venv; do
  if [ -d "$d" ] && [ -f "$d/bin/activate" ]; then
    VENV_DIR="$d"
    break
  fi
done

if [ -z "$VENV_DIR" ]; then
  warning "No virtual environment found. Creating one at ./env …"
  python3 -m venv env
  VENV_DIR="env"
else
  # Check the venv is usable and still lives where it was created. A venv that
  # has been moved keeps a working python symlink, but its pip/activate scripts
  # point at the old path.
  VENV_PYTHON="$VENV_DIR/bin/python"
  if [ ! -x "$VENV_PYTHON" ] || ! "$VENV_PYTHON" -m pip --version &>/dev/null \
     || ! grep -qF "$SCRIPT_DIR/$VENV_DIR" "$VENV_DIR/bin/activate"; then
    warning "Virtual environment '$VENV_DIR' is broken or was moved — recreating …"
    rm -rf "$VENV_DIR"
    python3 -m venv "$VENV_DIR"
  fi
fi

source "$VENV_DIR/bin/activate"
info "Virtual environment: $VENV_DIR"

# ── 2. Python dependencies ────────────────────────────────────────────────────
info "Installing/checking Python dependencies …"
python -m pip install -q -r requirements.txt

# ── 3. .env file ─────────────────────────────────────────────────────────────
if [ ! -f ".env" ]; then
  warning ".env not found — copying from env.example"
  cp env.example .env
  warning "Edit .env with your email/SMTP settings before using contact forms."
fi

# ── 4. Node / Tailwind CSS ────────────────────────────────────────────────────
if command -v node &>/dev/null; then
  info "Building Tailwind CSS …"
  (cd theme && npm install --silent && npm run build-css)
  python manage.py collectstatic --noinput -v 0
else
  warning "Node.js not found — skipping Tailwind build. CSS may be out of date."
fi

# ── 5. Database migrations ────────────────────────────────────────────────────
info "Running database migrations …"
python manage.py migrate --run-syncdb -v 0

# ── 6. Start dev server ───────────────────────────────────────────────────────
PORT="${PORT:-8000}"
PID_FILE="$SCRIPT_DIR/.server.pid"

echo ""
info "Starting development server on http://127.0.0.1:${PORT}/"
echo ""

# Record our PID for stop.sh, then replace this shell with the server. Running
# it in the foreground (rather than as a background job) means Ctrl-C reaches
# it; background jobs in a script ignore SIGINT and would keep the port bound.
echo "$$" > "$PID_FILE"
exec python manage.py runserver "$PORT"

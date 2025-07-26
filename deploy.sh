#!/usr/bin/env bash
# Exit on errors, undefined variables, or failed pipelines
set -euo pipefail

### ─── GLOBAL CONSTANTS ─────────────────────────────────────────────────────────
readonly PROD_DIR="/home/shane/Production/composer-explorer-vue"
readonly DEV_DIR="/home/shane/Documents/composer-explorer-vue"
readonly VENV_DIR="$PROD_DIR/server/venv"
readonly GIT_REPO_URL="https://github.com/shanewilliams29/composer-explorer-vue.git"
readonly SERVICES_URL="http://localhost:8000"

# Colors for logging
readonly RED=$'\e[31m'
readonly GREEN=$'\e[32m'
readonly NC=$'\e[0m'  # No Color

### ─── ERROR HANDLING ──────────────────────────────────────────────────────────
error_handler() {
  echo -e "${RED}[ERROR] on line $1${NC}" >&2
  exit 1
}
trap 'error_handler $LINENO' ERR

### ─── LOGGING HELPERS ─────────────────────────────────────────────────────────
info()  { echo -e "${GREEN}[INFO] $*${NC}"; }
error() { echo -e "${RED}[ERROR] $*${NC}" >&2; }

### ─── REQUIREMENTS CHECK ──────────────────────────────────────────────────────
check_requirements() {
  info "Checking for required programs: git, python3, npm"
  for prog in git python3 npm; do
    if ! command -v "$prog" &>/dev/null; then
      error "Missing dependency: $prog"
      exit 1
    fi
  done
}

### ─── GIT CLONE ────────────────────────────────────────────────────────────────
clone_repo() {
  if [[ ! -d "$PROD_DIR" ]]; then
    info "Cloning production repo into $(dirname "$PROD_DIR")"
    pushd "$(dirname "$PROD_DIR")" >/dev/null
      git clone "$GIT_REPO_URL"
      chown -R shane:shane "$PROD_DIR"
    popd >/dev/null
  else
    info "Production directory exists; skipping clone"
  fi
}

### ─── VIRTUAL ENVIRONMENT ─────────────────────────────────────────────────────
create_venv() {
  if [[ ! -d "$VENV_DIR" ]]; then
    info "Creating Python virtualenv at $VENV_DIR"
    python3 -m venv "$VENV_DIR"
  else
    info "Virtualenv already exists"
  fi
}

install_python_deps() {
  info "Installing Python dependencies"
  pushd "$PROD_DIR/server" >/dev/null
    source "$VENV_DIR/bin/activate"
      pip install --upgrade pip
      pip install -r requirements.txt
    deactivate
  popd >/dev/null
}

### ─── COPY ENV & CERTIFICATES ─────────────────────────────────────────────────
copy_env_and_certs() {
  info "Copying .env and JSON credentials"
  rsync -a \
    "$DEV_DIR/server/production_env/.env" \
    "$DEV_DIR/server/composer-explorer-4ab69db6d8b0.json" \
    "$PROD_DIR/server/"

  info "Copying CA certificates"
  mkdir -p "$PROD_DIR/server/certs"
  cp "$DEV_DIR/server/certs/ca.crt" "$PROD_DIR/server/certs/"
}

### ─── LOGS DIRECTORY ──────────────────────────────────────────────────────────
create_logs_dir() {
  info "Ensuring logs directory exists"
  mkdir -p "$PROD_DIR/server/logs"
  chown -R shane:shane "$PROD_DIR/server/logs"
}

### ─── RUN UNIT TESTS ──────────────────────────────────────────────────────────
run_tests() {
  info "Running server-side unit tests"
  pushd "$DEV_DIR/server" >/dev/null
    source "$VENV_DIR/bin/activate"
      if python3 -m unittest tests.py; then
        info "Tests passed"
      else
        error "Tests failed—aborting deployment"
        deactivate
        exit 1
      fi
    deactivate
  popd >/dev/null
}

### ─── BUILD FRONTEND ──────────────────────────────────────────────────────────
build_client() {
  info "Building frontend client"
  pushd "$DEV_DIR/client" >/dev/null
    if npm run build; then
      info "Client build succeeded"
    else
      error "Client build failed—aborting"
      exit 1
    fi
  popd >/dev/null
}

### ─── DEPLOY TO PRODUCTION ────────────────────────────────────────────────────
deploy() {
  info "Deploying to production server"
  pushd "$PROD_DIR/server" >/dev/null

    info "Pulling latest changes"
    git pull origin main

    info "Synchronizing built assets"
    rsync -a --delete "$DEV_DIR/server/dist/" dist/

    info "Reloading services"
    sudo supervisorctl reload
    sudo systemctl reload nginx

  popd >/dev/null
}

### ─── HEALTH CHECK WITH FIXED RETRIES & EXPLICIT OUTPUT ────────────────────
health_check() {
  local url=${1:-$SERVICES_URL}
  local expected=${2:-200}
  local retries=6                   # total attempts
  local delay=5                     # seconds between tries
  local attempt=1
  local status

  info "Waiting for ${url} to return HTTP ${expected} (up to $((retries*delay))s)..."

  while (( attempt <= retries )); do
    # run curl, force a 000 on error so we always get something
    status=$(curl -s -o /dev/null \
      --connect-timeout "$delay" \
      --max-time "$delay" \
      -w "%{http_code}" \
      "$url" || echo "000")

    if [[ "$status" -eq "$expected" ]]; then
      info "✅ Healthy on attempt $attempt (HTTP $status)."
      return 0
    fi

    error "Attempt $attempt/$retries: got HTTP $status — retrying in ${delay}s…"
    (( attempt++ ))
    sleep "$delay"
  done

  error "❌ Health check failed after $retries attempts (last status: $status)."
  exit 1
}

### ─── MAIN ────────────────────────────────────────────────────────────────────
main() {
  check_requirements
  clone_repo
  create_venv
  install_python_deps
  copy_env_and_certs
  create_logs_dir
  run_tests
  build_client
  deploy
  health_check
  info "🎉 DEPLOYMENT COMPLETE!"
}

main "$@"

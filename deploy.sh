#!/usr/bin/env bash
# Exit on errors, undefined variables, or failed pipelines
set -euo pipefail

### ─── GLOBAL CONSTANTS ─────────────────────────────────────────────────────────
readonly PROD_DIR="/home/shane/Production/composer-explorer-vue"
readonly DEV_DIR="/home/shane/Documents/composer-explorer-vue"
readonly VENV_DIR="$PROD_DIR/server/venv"
readonly GIT_REPO_URL="https://github.com/shanewilliams29/composer-explorer-vue.git"
readonly SERVICES_URL="http://localhost:8000"

# Colors for output
readonly RED=$'\e[31m'
readonly GREEN=$'\e[32m'
readonly NC=$'\e[0m'

### ─── ERROR HANDLING ──────────────────────────────────────────────────────────
error_handler() {
  echo -e "${RED}[ERROR] on line $1${NC}" >&2
  exit 1
}
trap 'error_handler $LINENO' ERR

### ─── LOGGING HELPERS ─────────────────────────────────────────────────────────
info()  { echo -e "${GREEN}✔ $*${NC}"; }
error() { echo -e "${RED}✖ $*${NC}" >&2; }

### ─── PROGRESS DISPLAY ─────────────────────────────────────────────────────────
TOTAL=10
STEP=1
step() {
  echo -e "\n${GREEN}[Step ${STEP}/${TOTAL}] $*...${NC}"
  (( STEP++ ))
}

### ─── TASK FUNCTIONS ──────────────────────────────────────────────────────────

check_requirements() {
  for prog in git python3 npm; do
    if ! command -v "$prog" &>/dev/null; then
      error "Missing dependency: $prog"
      exit 1
    fi
  done
}

clone_repo() {
  if [[ ! -d "$PROD_DIR" ]]; then
    pushd "$(dirname "$PROD_DIR")" >/dev/null
      git clone "$GIT_REPO_URL"
      chown -R shane:shane "$PROD_DIR"
    popd >/dev/null
  fi
}

create_venv() {
  if [[ ! -d "$VENV_DIR" ]]; then
    python3 -m venv "$VENV_DIR"
  fi
}

install_python_deps() {
  pushd "$PROD_DIR/server" >/dev/null
    source "$VENV_DIR/bin/activate"
      pip install --upgrade pip
      pip install -q -r requirements.txt
    deactivate
  popd >/dev/null
}

copy_env_and_certs() {
  mkdir -p "$PROD_DIR/server"
  rsync -a \
    "$DEV_DIR/server/production_env/.env" \
    "$DEV_DIR/server/composer-explorer-4ab69db6d8b0.json" \
    "$PROD_DIR/server/"
  mkdir -p "$PROD_DIR/server/certs"
  cp "$DEV_DIR/server/certs/ca.crt" "$PROD_DIR/server/certs/"
}

create_logs_dir() {
  mkdir -p "$PROD_DIR/server/logs"
  chown -R shane:shane "$PROD_DIR/server/logs"
}

run_tests() {
  pushd "$DEV_DIR/server" >/dev/null
    source "$VENV_DIR/bin/activate"
      if python3 -m unittest tests.py; then
        info "Unit tests passed"
      else
        error "Unit tests failed—aborting"
        deactivate
        exit 1
      fi
    deactivate
  popd >/dev/null
}

build_client() {
  pushd "$DEV_DIR/client" >/dev/null
    if npm run build >/dev/null 2>&1; then
      info "Frontend build succeeded"
    else
      error "Frontend build failed—aborting"
      exit 1
    fi
  popd >/dev/null
}

deploy() {
  pushd "$PROD_DIR/server" >/dev/null
    git pull origin main
    rsync -a --delete "$DEV_DIR/server/dist/" dist/
    sudo supervisorctl reload
    sudo systemctl reload nginx
  popd >/dev/null
}

health_check() {
  local url=${1:-$SERVICES_URL}
  local expected=${2:-200}
  local retries=6
  local delay=5
  local attempt=1
  local status

  echo -e "\n${GREEN}→ Waiting for ${url} to return ${expected} (up to $((retries*delay))s)${NC}"
  while (( attempt <= retries )); do
    status=$(curl -s -o /dev/null --connect-timeout "$delay" --max-time "$delay" -w "%{http_code}" "$url" || echo "000")
    if [[ "$status" -eq "$expected" ]]; then
      info "Service healthy (HTTP $status)"
      return 0
    fi
    echo -e "${RED}  attempt ${attempt}/${retries}: HTTP $status${NC}"
    (( attempt++ ))
    sleep "$delay"
  done

  error "Health check failed after $retries attempts"
  exit 1
}

### ─── MAIN ────────────────────────────────────────────────────────────────────
main() {
  step "Checking required programs"
  check_requirements && info "All dependencies found"

  step "Cloning repository"
  clone_repo && info "Repository ready"

  step "Setting up virtualenv"
  create_venv && info "Virtualenv created"

  step "Installing Python dependencies"
  install_python_deps

  step "Copying environment & cert files"
  copy_env_and_certs && info "Env and certs in place"

  step "Creating logs directory"
  create_logs_dir && info "Logs directory ready"

  step "Running unit tests"
  run_tests

  step "Building frontend"
  build_client

  step "Deploying to production"
  deploy && info "Code deployed"

  step "Performing health check"
  health_check

  echo -e "\n${GREEN}🎉 All $TOTAL steps completed successfully!${NC}\n"
}

main "$@"

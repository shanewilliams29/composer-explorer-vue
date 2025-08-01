#!/usr/bin/env bash
# Exit on errors, undefined variables, or failed pipelines
set -euo pipefail

### ─── GLOBAL CONSTANTS ─────────────────────────────────────────────────────────
# Local (dev) paths
readonly DEV_DIR="$HOME/Documents/composer-explorer-vue"
readonly LOCAL_VENV="$DEV_DIR/server/venv"

# Remote (prod) paths & SSH
readonly REMOTE_USER="root"
readonly REMOTE_HOST="94.72.125.158"   # ← change this!
readonly REMOTE="$REMOTE_USER@$REMOTE_HOST"

# Paths on remote
readonly PROD_DIR="/root/composer-explorer-vue"
readonly VENV_DIR="$PROD_DIR/server/venv"

readonly GIT_REPO_URL="https://github.com/shanewilliams29/composer-explorer-vue.git"
# readonly SERVICES_URL="http://localhost:8000"

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

### ─── PROMPT FOR PASSWORD ──────────────────────────────────────────────────────
read -s -p "Enter SSH password for ${REMOTE_USER}@${REMOTE_HOST}: " SSH_PASS
echo

# We'll pass -o StrictHostKeyChecking=no to avoid host-key prompts
readonly SSH_OPTS="-o StrictHostKeyChecking=no"

### ─── TASK FUNCTIONS ──────────────────────────────────────────────────────────

check_requirements() {
  for prog in git python3 npm sshpass ssh rsync; do
    if ! command -v "$prog" &>/dev/null; then
      error "Missing dependency: $prog"
      exit 1
    fi
  done
}

remote_ssh() {
  sshpass -p "$SSH_PASS" ssh $SSH_OPTS "$REMOTE" "$@"
}

clone_repo_remote() {
  remote_ssh "
    if [[ ! -d '$PROD_DIR/.git' ]]; then
      git clone '$GIT_REPO_URL' '$PROD_DIR' && \
      chown -R root:root '$PROD_DIR'
    else
      cd '$PROD_DIR' && \
      git reset --hard && \
      git pull --rebase
    fi
  "
}

create_venv_remote() {
  remote_ssh "if [[ ! -d '$VENV_DIR' ]]; then python3 -m venv '$VENV_DIR'; fi"
}

install_python_deps_remote() {
  remote_ssh "set -e; \
              source '$VENV_DIR/bin/activate'; \
              pip install --upgrade pip; \
              pip install -q -r '$PROD_DIR/server/requirements.txt'; \
              deactivate"
}

copy_env_remote() {
  # sync .env and service account JSON
  rsync -az -e "sshpass -p '$SSH_PASS' ssh $SSH_OPTS" \
    "$DEV_DIR/server/production_env/.env" \
    "$DEV_DIR/server/composer-explorer-4ab69db6d8b0.json" \
    "$REMOTE:$PROD_DIR/server/"
}

create_logs_dir_remote() {
  remote_ssh "mkdir -p '$PROD_DIR/server/logs' && chown -R root:root '$PROD_DIR/server/logs'"
}

run_tests_local() {
  pushd "$DEV_DIR/server" >/dev/null
    source "$LOCAL_VENV/bin/activate"
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
  step "Building frontend locally"

  # 1) Build the Vue client
  pushd "$DEV_DIR/client" >/dev/null

    info "Installing JS dependencies"
    npm ci || {
      error "npm ci failed—aborting"
      exit 1
    }

    info "Running npm run build (output below)"
    npm run build || {
      error "npm run build failed—aborting"
      exit 1
    }

    info "Client build succeeded"
  popd >/dev/null

  # 2) Sync into server/dist for rsync
  step "Preparing server/dist for deploy"
  if [[ -d "$DEV_DIR/server/dist" ]]; then
    info "Cleaning local server/dist (may need sudo)…"
    sudo rm -rf "$DEV_DIR/server/dist"
  fi

  mkdir -p "$DEV_DIR/server/dist"
  cp -a "$DEV_DIR/client/dist/." "$DEV_DIR/server/dist/"

  info "✔ server/dist is ready"
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
  info "Transferring static files"
  sshpass -p "$SSH_PASS" rsync -az --delete \
    -e "ssh $SSH_OPTS" \
    "$DEV_DIR/server/dist/" \
    "$REMOTE_USER@$REMOTE_HOST:$PROD_DIR/server/dist/"

  info "Reloading remote services"
  sshpass -p "$SSH_PASS" ssh $SSH_OPTS "$REMOTE_USER@$REMOTE_HOST" \
    "supervisorctl reload && systemctl reload nginx"
}

health_check_remote() {
  local url="https://${REMOTE_HOST}"
  local expected=200
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

  step "Cloning repository on remote"
  clone_repo_remote && info "Remote repository ready"

  step "Setting up virtualenv on remote"
  create_venv_remote && info "Remote virtualenv created"

  step "Installing Python dependencies on remote"
  install_python_deps_remote && info "Remote Python deps installed"

  step "Copying environment file"
  copy_env_remote && info "Env synced"

  step "Creating logs directory on remote"
  create_logs_dir_remote && info "Logs directory ready"

  step "Running unit tests locally"
  run_tests_local

  step "Building frontend locally"
  build_client

  step "Deploying to remote production"
  deploy && info "Remote code deployed"

  step "Performing health check on remote"
  health_check_remote

  echo -e "\n${GREEN}🎉 All $TOTAL steps completed successfully!${NC}\n"
}

main "$@"

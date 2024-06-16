#!/bin/bash

# Set safe environment
set -euo pipefail

# Constants for paths and colors
PROJECT_DIR="/home/shane/Documents"
PRODUCTION_DIR="$PROJECT_DIR/production/composer-explorer-vue/server"
DEVELOPMENT_DIR="$PROJECT_DIR/composer-explorer-vue"
VENV_PATH="venv"
RED='\033[31m'
GREEN='\033[32m'
NC='\033[0m' # No Color

# Logging function
log() {
  local message=$1
  local color=${2-""}  # Default to empty string if not provided
  echo -e "${color}${message}${NC}"
}

# Activate virtual environment
activate_env() {
  source "$VENV_PATH/bin/activate"
}

# Run unit tests
run_tests() {
  activate_env
  log "\nRunning unit tests..."  "${GREEN}"
  if python3 -m unittest tests.py; then
    log "\nUnit tests passed. Proceeding to deployment..." "${GREEN}"
    deactivate
  else
    log "\nUnit tests failed. Deployment canceled." "${RED}"
    deactivate
    exit 1
  fi
}

# Build client
build_client() {
  cd "$DEVELOPMENT_DIR/client" || exit 1
  log "\nRunning 'npm run build' in client directory..." "${GREEN}"
  npm run build
}

# Deploy to production
deploy_production() {
  cd "$PRODUCTION_DIR" || exit 1
  
  log "\nPulling from git for production server..." "${GREEN}"
  git pull origin main || exit 1
  
  activate_env
  log "\nInstalling updated Python dependencies from requirements.txt..." "${GREEN}"
  pip install -r requirements.txt
  deactivate
  
  log "\nCopying static dist files to production server..." "${GREEN}"
  rm -rf dist
  cp -r "$DEVELOPMENT_DIR/server/dist" "$PRODUCTION_DIR/dist"
  
  log "\nRestarting gunicorn..." "${GREEN}"
  sudo supervisorctl reload
}

# Main script execution
main() {
  run_tests
  build_client
  deploy_production
  log "\nDEPLOYMENT COMPLETE!\n" "${GREEN}"
}

# Run the script
main

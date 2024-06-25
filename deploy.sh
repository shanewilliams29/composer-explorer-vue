#!/bin/bash

# Set safe environment
set -euo pipefail

# Constants for paths and colors
PRODUCTION_DIR="/home/shane/Production/composer-explorer-vue"
DEVELOPMENT_DIR="/home/shane/Documents/composer-explorer-vue"
VENV_PATH="server/venv"
RED='\033[31m'
GREEN='\033[32m'
NC='\033[0m' # No Color

# Check for necessary program availability
check_requirements() {
    for program in git python3 npm; do
        command -v $program >/dev/null 2>&1 || { echo >&2 "I require $program but it's not installed. Aborting."; exit 1; }
    done
}

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
    if ! npm run build >/dev/null 2>&1; then
        log "\nClient build failed, aborting deployment." "${RED}"
        exit 1
    fi
}

# Deploy to production
deploy_production() {
  cd "$PRODUCTION_DIR/server" || exit 1
  
  log "\nPulling from git for production server..." "${GREEN}"
  if ! git pull origin main; then
      log "\nFailed to pull latest changes from git." "${RED}"
      exit 1
  fi
  
  activate_env
  log "\nInstalling updated Python dependencies from requirements.txt..." "${GREEN}"
  pip install --quiet -r requirements.txt
  deactivate
  
  log "\nCopying static dist files to production server..." "${GREEN}"
  rm -rf dist
  cp -r "$DEVELOPMENT_DIR/server/dist" "$PRODUCTION_DIR/server/dist"
  
  log "\nRestarting gunicorn..." "${GREEN}"
  sudo supervisorctl reload

  log "\nReloading nginx..." "${GREEN}"
  sudo systemctl reload nginx
}

# Function to check if the server is up and responding correctly
check_server_response() {
  local url=$1  # URL to check
  local expected_status=$2  # Expected HTTP status code

  # Using curl to make a request and check the response
  local status=$(curl -o /dev/null -s -w "%{http_code}\n" "$url")

  # Compare the response status code with the expected status
  if [ "$status" -eq "$expected_status" ]; then
    log "Server responded with $status, as expected.\n"
  else
    log "Server response check failed. Expected $expected_status but got $status.\n" "${RED}"
    return 1  # Return failure
  fi
}

# Function to perform post-deployment checks
post_deployment_verification() {
  log "\nWaiting for the application to stabilize..." "${GREEN}"
  sleep 5  # Wait for 5 seconds
  
  log "\nPerforming post-deployment verification..." "${GREEN}"
  # Assuming your Flask app has an endpoint that returns a 200 OK for root
  check_server_response "http://localhost:8000" 200 || exit 1
}

# Main script execution
main() {
  check_requirements
  run_tests
  build_client
  deploy_production
  post_deployment_verification
  log "DEPLOYMENT COMPLETE!\n" "${GREEN}"
}

# Run the script
main

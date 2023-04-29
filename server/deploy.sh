 #!/bin/bash

# Run unit tests
echo "Running unit tests..."
python3 -m unittest tests.py

# Check if tests were successful
if [ $? -eq 0 ]; then
  echo "Unit tests passed. Proceeding to deployment..."
  
  # Deploy to Google Cloud
  gcloud config set project composer-explorer
  gcloud app deploy --quiet
  
  echo "Deployment successful."
else
  echo "Unit tests failed. Deployment canceled."
  exit 1
fi
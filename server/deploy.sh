 #!/bin/bash

# Run unit tests
echo "Running unit tests..."
python3 -m unittest tests.py

# Check if tests were successful
if [ $? -eq 0 ]; then
  echo -e "\033[32mUnit tests passed. Proceeding to deployment...\033[0m"
  
  # Deploy to Google Cloud
  gcloud config set project composer-explorer
  gcloud app deploy --quiet
  
  echo -e "\033[32mDeployment successful.\033[0m"
else
  echo -e "\033[31mUnit tests failed. Deployment canceled.\033[0m"
  exit 1
fi
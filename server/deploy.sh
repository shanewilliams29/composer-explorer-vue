 #!/bin/bash

# activate venv
source venv/bin/activate

 # Save the current directory
initial_dir=$(pwd)

# Run unit tests
echo -e "\nRunning unit tests..."
python3 -m unittest tests.py

# Check if tests were successful
if [ $? -eq 0 ]; then
  echo -e "\033[32m\nUnit tests passed. Proceeding to deployment...\n\033[0m"

  # Change directory to ../client and run npm run serve
  cd ../client
  echo "Running 'npm run build' in ../client directory..."
  npm run build

  # Check if npm run build was successful
  if [ $? -eq 0 ]; then
    echo -e "\033[32m'npm run build' successful. Project ready for deployment!\n\033[0m"
  else
    echo -e "\033[31m'npm run build' failed. Exiting.\n\033[0m"
    exit 1
  fi
else
  echo -e "\033[31m\nUnit tests failed. Deployment canceled.\n\033[0m"
  exit 1
fi


# For Google App Engine Deployment
#   # Change back to the initial directory (../server)
#   cd "$initial_dir"
  
#   # Deploy to Google Cloud
#   gcloud config set project composer-explorer
#   gcloud app deploy --quiet

#   # Check if deployment was successful
#   if [ $? -eq 0 ]; then
#     echo -e "\033[32m\nDeployment successful!\n\033[0m"
#   else
#     echo -e "\033[31m\nDeployment failed!\n\033[0m"
#     exit 1
#   fi

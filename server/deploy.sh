#!/bin/bash

# Activate virtual environment
echo -e "\nActivating virtual environment in source directory..."
source venv/bin/activate || { echo -e "\033[31mFailed to activate virtual environment. Exiting.\033[0m"; exit 1; }

# Save the current directory
initial_dir=$(pwd)

# Run unit tests
echo -e "\nRunning unit tests..."
python3 -m unittest tests.py
if [ $? -eq 0 ]; then
  echo -e "\033[32m\nUnit tests passed. Proceeding to deployment...\033[0m"
else
  echo -e "\033[31m\nUnit tests failed. Deployment canceled.\033[0m"
  exit 1
fi

# Deactivate the virtual environment in the source directory
deactivate

# Change directory to ../client and run npm run serve
cd ../client || { echo -e "\033[31mFailed to change directory to ../client. Exiting.\033[0m"; exit 1; }
echo -e "\nRunning 'npm run build' in ../client directory..."
npm run build
if [ $? -eq 0 ]; then
  echo -e "\033[32m'npm run build' successful. Project ready for deployment!\033[0m"
else
  echo -e "\033[31m'npm run build' failed. Exiting.\033[0m"
  exit 1
fi

# Change directory to server folder in production
cd /home/shane/Documents/production/composer-explorer-vue/server/ || { echo -e "\033[31mFailed to navigate to production server directory. Exiting.\033[0m"; exit 1; }

echo -e "\nActivating virtual environment in production server..."
source venv/bin/activate || { echo -e "\033[31mFailed to activate virtual environment in production server. Exiting.\033[0m"; exit 1; }

# Pull latest updates from git
echo -e "\nPulling from git for production server..."
git pull origin main || { echo -e "\033[31mFailed to pull from Git. Exiting.\033[0m"; exit 1; }

# Install updated Python dependencies
echo -e "\nInstalling updated Python dependencies from requirements.txt..."
pip install -r requirements.txt || { echo -e "\033[31mFailed to install dependencies. Exiting.\033[0m"; exit 1; }

# Copy static dist files to production server
echo -e "\nCopying static dist files to production server..."
rm -r /home/shane/Documents/production/composer-explorer-vue/server/dist || { echo -e "\033[31mFailed to remove old dist folder. Exiting.\033[0m"; exit 1; }
cp -r /home/shane/Documents/composer-explorer-vue/server/dist /home/shane/Documents/production/composer-explorer-vue/server/dist || { echo -e "\033[31mFailed to copy dist files. Exiting.\033[0m"; exit 1; }

# Restart gunicorn using supervisor
echo -e "\nRestarting gunicorn..."
sudo supervisorctl reload || { echo -e "\033[31mFailed to restart gunicorn. Exiting.\033[0m"; exit 1; }

# Print completion message
echo -e "\033[32m\nDEPLOYMENT COMPLETE!\033[0m"

# Deactivate the virtual environment in the production directory
deactivate

# Return to the initial directory
cd "$initial_dir"
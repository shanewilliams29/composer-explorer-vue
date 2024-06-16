#!/bin/bash

# Activate virtual environment
echo "Activating virtual environment..."
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

# Change directory to ../client and run npm run serve
cd ../client || { echo -e "\033[31mFailed to change directory to ../client. Exiting.\033[0m"; exit 1; }
echo "Running 'npm run build' in ../client directory..."
npm run build
if [ $? -eq 0 ]; then
  echo -e "\033[32m'npm run build' successful. Project ready for deployment!\033[0m"
else
  echo -e "\033[31m'npm run build' failed. Exiting.\033[0m"
  exit 1
fi

# Change directory to server folder in production
cd /home/shane/Documents/production/composer-explorer-vue/server/ || { echo -e "\033[31mFailed to navigate to production server directory. Exiting.\033[0m"; exit 1; }

# Pull latest updates from git
echo -e "\nPulling from git for production server..."
git pull origin main || { echo -e "\033[31mFailed to pull from Git. Exiting.\033[0m"; exit 1; }

# Copy static dist files to production server
echo -e "\nCopying static dist files to production server..."
rm -r /home/shane/Documents/production/composer-explorer-vue/server/dist || { echo -e "\033[31mFailed to remove old dist folder. Exiting.\033[0m"; exit 1; }
cp -r /home/shane/Documents/composer-explorer-vue/server/dist /home/shane/Documents/production/composer-explorer-vue/server/dist || { echo -e "\033[31mFailed to copy dist files. Exiting.\033[0m"; exit 1; }

# Restart gunicorn using supervisor
echo -e "\nRestarting gunicorn..."
sudo supervisorctl reload || { echo -e "\033[31mFailed to restart gunicorn. Exiting.\033[0m"; exit 1; }

# Print completion message
echo -e "\033[32m\nDEPLOYMENT COMPLETE!\033[0m"

# Return to the initial directory
cd "$initial_dir"
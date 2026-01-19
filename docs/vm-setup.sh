#!/bin/bash
set -e

# Zero Cost Deployment Setup Script for Debian/Ubuntu (Google Cloud e2-micro)

echo ">>> Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

echo ">>> Installing Docker..."
# Add Docker's official GPG key:
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo ">>> Verifying Docker installation..."
sudo docker run --rm hello-world

echo ">>> Setup complete! You can now clone the repo and run:"
echo "    git clone https://github.com/aman12122/job-crawler.git"
echo "    cd job-crawler"
echo "    # Create .env file with DATABASE_PASSWORD=..."
echo "    sudo docker compose -f docker-compose.prod.yml up -d"

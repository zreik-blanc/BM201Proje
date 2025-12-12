#!/bin/bash
set -e

# Log the output of this script to /var/log/user-data.log
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

# Update package lists
sudo apt-get update -y
sudo apt-get upgrade -y

# Install Docker Engine
echo "Installing Docker Engine..."
sudo apt remove $(dpkg --get-selections docker.io docker-compose docker-compose-v2 docker-doc podman-docker containerd runc | cut -f1)
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt-get update -y

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
usermod -aG docker ubuntu

sudo systemctl enable docker
sudo systemctl start docker

if sudo docker run --rm hello-world; then
    echo "Docker installed successfully."
else
    echo "Error: Docker installation failed."
    exit 1 
fi

# Clone the Git repository
echo "Cloning Git repository..."

git clone https://github.com/zreik-blanc/BM201Proje.git /home/ubuntu/BM201Project

# Right now we are not running the Docker Compose setup automatically to allow for manual configuration first.
# # Run Docker Compose to set up the application
# echo "Setting up the application with Docker Compose..."

# if docker compose -f docker-compose.prod.yml up -d --build; then
#     echo "Application set up successfully."
# else
#     echo "Error: Application setup failed."
#     exit 1 
# fi
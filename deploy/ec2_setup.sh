#!/bin/bash
# Run this on a fresh Ubuntu 22.04/24.04 EC2 instance to set up the app.
# Usage: bash ec2_setup.sh

set -e

echo ">>> Updating system packages"
sudo apt update && sudo apt upgrade -y

echo ">>> Installing Python, pip, venv, nginx, mysql client"
sudo apt install -y python3-pip python3-venv nginx mysql-client git

echo ">>> Cloning app (replace with your actual repo URL)"
# git clone https://github.com/yourusername/sentiment-rag-bot.git
cd sentiment-rag-bot || { echo "Upload/clone your project into ~/sentiment-rag-bot first"; exit 1; }

echo ">>> Creating virtual environment"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ">>> Copy .env.example to .env and fill in your real credentials:"
echo "    cp .env.example .env && nano .env"

echo ">>> Setup complete. Next steps:"
echo "1. Fill in .env with your Anthropic API key and MySQL credentials"
echo "2. Test locally: uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo "3. Install the systemd service (see deploy/sentiment-bot.service)"
echo "4. Configure nginx as a reverse proxy (see deploy/nginx.conf)"

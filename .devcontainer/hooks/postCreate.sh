#!/bin/sh
sudo rm -f /etc/apt/apt.conf.d/docker-clean; \
  echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' | sudo tee /etc/apt/apt.conf.d/keep-cache

poetry config virtualenvs.in-project true
poetry config virtualenvs.prompt venv
poetry install

sudo chown -R vscode:vscode /home/vscode/.cache/pypoetry

sudo apt-get update && sudo apt-get install -y --no-install-recommends lshw
curl -fsSL https://ollama.com/install.sh | sh
sudo chown -R vscode:vscode /home/vscode/.ollama

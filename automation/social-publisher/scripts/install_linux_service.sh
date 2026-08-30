#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$ROOT/.venv"
PYTHON="$VENV/bin/python"
ENV_FILE="$ROOT/.env"
SERVICE_NAME="sklarz-social-publisher"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
USER_NAME="${SUDO_USER:-$USER}"

if [[ ! -x "$PYTHON" ]]; then
  echo "Virtual environment not found at $VENV"
  echo "Run: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
  exit 1
fi

if [[ ! -f "$ENV_FILE" ]]; then
  echo ".env not found. Copy .env.example to .env and configure credentials first."
  exit 1
fi

sudo tee "$SERVICE_FILE" >/dev/null <<EOF
[Unit]
Description=Sklarz Creative Direct Social Publisher
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$ROOT
ExecStart=$PYTHON $ROOT/scripts/run_loop.py
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"

echo "Installed $SERVICE_NAME."
echo "Run a dry test before starting it:"
echo "  $PYTHON -m social_publisher.main --dry-run"
echo "After setting PUBLISHER_ENABLED=true and DRY_RUN=false in .env:"
echo "  sudo systemctl start $SERVICE_NAME"
echo "Logs: journalctl -u $SERVICE_NAME -f"

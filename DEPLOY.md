# VPS Deploy (No Docker)

This repo now deploys with GitHub Actions by copying files directly to your VPS.

## Workflows

- API deploy workflow: `.github/workflows/deploy-api.yml`
- UI deploy workflow lives in the UI repo: `sendbyteUI/.github/workflows/deploy-ui.yml`

## Required GitHub Secrets

Set these in **both** repos:

- `VPS_HOST`: VPS hostname or IP
- `VPS_USER`: SSH user
- `VPS_SSH_KEY`: private key content for that user (recommended)
- `VPS_SSH_PASSWORD`: SSH password (optional, if using password auth)
- `VPS_APP_DIR`: base deploy directory on VPS (example: `/opt/sendbyte`)
- `VPS_API_RESTART_CMD`: restart command (example: `sudo systemctl restart sendbyte-api`)

Set this in the UI repo:

- `VITE_API_BASE_URL`: API base URL used at UI build time (example: `https://sendbyte.net`)

## Expected VPS Layout

After first deploy:

- `${VPS_APP_DIR}/api` -> API source + virtualenv + runtime folders
- `${VPS_APP_DIR}/api/dist` -> built UI copied by UI workflow
- `${VPS_APP_DIR}/api/files` -> uploaded zip files
- `${VPS_APP_DIR}/incoming` -> temporary uploaded archives

## API Runtime Setup (One-time)

1. Create a systemd service that runs from `${VPS_APP_DIR}/api`.
2. Use `${VPS_APP_DIR}/api/.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000`.
3. Put Nginx/Caddy in front for TLS and reverse proxy.

The deploy workflows then only need to copy files and run your restart command.

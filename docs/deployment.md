# Deployment

This project is deployed with a simple GitHub-first flow:

1. Commit local changes.
2. Push the commit to GitHub.
3. SSH into the VPS.
4. Pull the same commit from GitHub.
5. Restart the systemd service.

The helper script does steps 2-5:

```bash
./scripts/deploy.sh
```

## Repository

GitHub repository:

```text
https://github.com/shedax68-pixel/Project_6_tgbot
```

The repository is public. Do not commit secrets.

These files must stay local-only:

```text
.env
.venv/
__pycache__/
*.pyc
```

## Server

SSH alias:

```bash
ssh project6-tgbot
```

Application directory:

```text
/opt/project_6_tgbot
```

Service name:

```text
project6-tgbot.service
```

Useful checks:

```bash
ssh project6-tgbot 'systemctl status project6-tgbot'
ssh project6-tgbot 'journalctl -u project6-tgbot -f'
```

## Normal Workflow

Make changes locally, then run:

```bash
git status
git add .
git commit -m "Describe the change"
./scripts/deploy.sh
```

The deploy script refuses to run if there are uncommitted local changes. This keeps the server from receiving code that has not been saved in GitHub first.

## Server Setup Notes

The server copy is a Git checkout of the public GitHub repository. The production `.env` file stays on the server and is ignored by Git.

The bot runs under a dedicated `telegrambot` system user through systemd. The service starts automatically after reboot and restarts if the bot process exits.

## Manual Deploy

If the helper script is unavailable, use this sequence:

```bash
git status
git push origin main
ssh project6-tgbot
cd /opt/project_6_tgbot
git fetch origin main
git reset --hard origin/main
.venv/bin/python -m pip install -r requirements.txt
systemctl restart project6-tgbot
systemctl status project6-tgbot
```

Do not edit code directly on the server. Change code locally, commit it, push it to GitHub, then deploy.

# Session Notes - 2026-05-20

Date: 2026-05-20

This document summarizes the setup and deployment work done during the session so future agents can quickly understand the project state, the deployment process, and the safety rules.

## Context

The project is a Python Telegram bot. Before this session it could:

- respond to `/start` and `/help`
- echo regular text messages
- transcribe Telegram voice messages through Deepgram

The user wanted the bot hosted on a VPS and wanted a clean deployment process where code changes go to GitHub first and only then reach the server.

## VPS Access

Server:

```text
186.246.45.46
```

SSH alias configured locally:

```bash
ssh project6-tgbot
```

The local SSH config uses a dedicated key:

```text
~/.ssh/project_6_tgbot_vps_ed25519
```

Only the public key was installed on the server. Password SSH login was disabled, and root login is restricted to key-based auth.

Important security note: credentials were shared in chat during the session. Treat any shared server password or API key as exposed if this transcript is reused outside the local environment.

## Server Runtime

Application directory on the VPS:

```text
/opt/project_6_tgbot
```

The bot runs as a systemd service:

```text
project6-tgbot.service
```

The service runs under the dedicated system user:

```text
telegrambot
```

Useful checks:

```bash
ssh project6-tgbot 'systemctl status project6-tgbot'
ssh project6-tgbot 'journalctl -u project6-tgbot -f'
```

The production `.env` lives on the server and must not be committed.

## GitHub Repository

Repository:

```text
https://github.com/shedax68-pixel/Project_6_tgbot
```

Visibility:

```text
PUBLIC
```

The repository was already present during the session. It was switched from private to public.

Files that must stay ignored:

```text
.env
.venv/
__pycache__/
*.pyc
```

## Deployment Process

The intended process is:

1. Make changes locally.
2. Commit changes.
3. Push to GitHub.
4. Deploy to the VPS only when the user explicitly asks.
5. The server pulls the exact GitHub commit and restarts the service.

Helper script:

```bash
./scripts/deploy.sh
```

The script refuses to deploy with uncommitted local changes. It also handles Git's safe directory check on the server.

Critical user preference established during the session:

```text
Do not deploy to the server unless the user explicitly asks.
```

It is acceptable to make local changes. Push to GitHub only when it matches the user's current request. Deploy to VPS only after a clear request such as "выкатывай", "задеплой", or "обнови сервер".

## What Was Implemented

### VPS Hosting

The project was copied to the VPS, dependencies were installed in a server-side virtual environment, and systemd was configured so the bot starts automatically after reboot and restarts if it exits.

### GitHub-First Deployment

The VPS app directory was converted from a direct file copy into a Git checkout of the public GitHub repository. A backup of the old server copy was kept at:

```text
/opt/project_6_tgbot.backup.20260520182507
```

The deployment script and documentation were added:

```text
scripts/deploy.sh
docs/deployment.md
```

### Voice Status Text

The temporary voice-processing message was changed from:

```text
Слушаю голосовое и расшифровываю...
```

to:

```text
Я работаю...
```

This change was committed, pushed, and deployed after user approval at that point in the session.

### Groq Integration

After a voice message is transcribed, the bot now adds an inline button:

```text
Отправить в Groq
```

When pressed, the bot sends the transcript to Groq's OpenAI-compatible Chat Completions API:

```text
https://api.groq.com/openai/v1/chat/completions
```

Default model:

```text
llama-3.3-70b-versatile
```

Relevant environment variables:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
```

The Groq key was added to the server `.env` at the user's request. The value was not committed.

The Groq code was then committed, pushed, and deployed only after the user explicitly said:

```text
выкатывай
```

## Important Files

Main bot code:

```text
bot.py
```

Deployment helper:

```text
scripts/deploy.sh
```

Deployment documentation:

```text
docs/deployment.md
```

Voice and Groq documentation:

```text
docs/voice-transcription.md
```

Project docs index:

```text
docs/README.md
```

## Operational Notes for Future Agents

- Do not print secrets in command output.
- Do not commit `.env`.
- Do not deploy to VPS without explicit user approval.
- If testing locally, make sure the server bot is stopped or use a different Telegram bot token. Telegram polling allows only one active poller per bot token.
- If the bot logs `telegram.error.Conflict`, another copy of the bot is running with the same token.
- After changing server `.env`, restart the service only if the user has approved server-side changes.
- Prefer the existing async style and keep external API calls in helper functions.

## Verification Done

During the session the following checks were used:

```bash
.venv/bin/python -m py_compile bot.py
git status --short
./scripts/deploy.sh
ssh project6-tgbot 'systemctl is-active project6-tgbot.service'
ssh project6-tgbot 'journalctl -u project6-tgbot.service --since "1 minute ago" --no-pager'
```

At the end of the Groq deployment, the VPS service was active and the server code contained the Groq button handler.

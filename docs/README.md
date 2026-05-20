# Project Docs

This folder contains project notes for the Telegram bot.

## Pages

- [Voice Transcription](voice-transcription.md): how Telegram voice messages are transcribed with Deepgram.
- [Deployment](deployment.md): GitHub-first deployment flow for the VPS.
- [Session Notes - 2026-05-20](2026-05-20-session-notes.md): setup and deployment decisions from the 2026-05-20 session.

## Quick Start

Create `.env` in the project root:

```env
BOT_TOKEN=your_telegram_bot_token
DEEPGRAM_API_KEY=your_deepgram_api_key
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
```

Install dependencies:

```bash
.venv/bin/python -m pip install -r requirements.txt
```

Run the bot:

```bash
.venv/bin/python bot.py
```

Open the bot in Telegram and send `/start` or a voice message.

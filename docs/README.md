# Project Docs

This folder contains project notes for the Telegram bot.

## Pages

- [Voice Transcription](voice-transcription.md): how Telegram voice messages are transcribed with Deepgram.

## Quick Start

Create `.env` in the project root:

```env
BOT_TOKEN=your_telegram_bot_token
DEEPGRAM_API_KEY=your_deepgram_api_key
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

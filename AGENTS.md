# AGENTS.md

## Project

Telegram bot written in Python.

The bot currently:

- replies to `/start` and `/help`
- echoes normal text messages
- transcribes Telegram voice messages through Deepgram

## Run

Use the local virtual environment:

```bash
.venv/bin/python bot.py
```

The bot reads secrets from `.env`.

Required environment variables:

```env
BOT_TOKEN=your_telegram_bot_token
DEEPGRAM_API_KEY=your_deepgram_api_key
```

## Dependencies

Install dependencies with:

```bash
.venv/bin/python -m pip install -r requirements.txt
```

## Safety

Do not commit secrets.

The following should stay ignored:

- `.env`
- `.venv/`
- `__pycache__/`
- `*.pyc`

If a Telegram bot token or Deepgram API key is exposed, rotate it before sharing or publishing the repository.

## Code Notes

Keep the bot simple and async-friendly.

- Add Telegram handlers in `main()`.
- Keep command handlers small.
- Put external API calls in helper functions.
- Avoid blocking calls inside async handlers.

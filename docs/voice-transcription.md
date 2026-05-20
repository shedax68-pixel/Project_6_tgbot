# Voice Transcription

The bot can transcribe Telegram voice messages into text.

## Flow

1. A user sends a Telegram voice message.
2. `python-telegram-bot` receives it through `filters.VOICE`.
3. The bot downloads the voice file from Telegram as bytes.
4. The bot sends the audio bytes to Deepgram.
5. Deepgram returns a transcript.
6. The bot edits the temporary status message and shows the transcript.
7. The transcript message includes a button that can send the transcript to Groq.
8. Groq returns an assistant response in Telegram.

## Deepgram

The integration uses Deepgram's pre-recorded audio endpoint:

```text
https://api.deepgram.com/v1/listen
```

Current options:

- `model=nova-3`
- `smart_format=true`
- `detect_language=true`

Telegram voice messages are sent as OGG/Opus audio, so the request uses:

```text
Content-Type: audio/ogg
```

## Environment

The API keys are read from `.env`:

```env
DEEPGRAM_API_KEY=your_deepgram_api_key
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
```

If `DEEPGRAM_API_KEY` is missing, the bot replies with a setup error instead of trying to call Deepgram.

If `GROQ_API_KEY` is missing, transcription still works, but the Groq button replies with a setup error.

## Main Code

The relevant code lives in `bot.py`:

- `voice_message()` handles Telegram voice messages.
- `transcribe_audio()` sends audio to Deepgram and extracts the transcript.
- `ask_groq()` sends the transcript to Groq.
- `groq_button()` handles the inline "Send to Groq" button.
- `main()` registers the voice handler.

## Troubleshooting

If transcription does not work:

- Check that `.env` contains `DEEPGRAM_API_KEY`.
- Check that `.env` contains `GROQ_API_KEY` if the Groq button fails.
- Restart the bot after changing `.env`.
- Make sure the Deepgram key is active.
- Make sure the Groq key is active.
- Check the terminal logs for HTTP status errors from Deepgram or Groq.

If the bot does not respond at all:

- Check that `BOT_TOKEN` exists in `.env`.
- Make sure only one local copy of the bot is running with polling.
- Restart with `.venv/bin/python bot.py`.

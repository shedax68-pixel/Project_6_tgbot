import logging
import os
import sys

import httpx
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)

DEEPGRAM_URL = "https://api.deepgram.com/v1/listen"
DEEPGRAM_MODEL = "nova-3"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_TRANSCRIPTS_KEY = "groq_transcripts"
GROQ_CALLBACK_PREFIX = "groq:"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Я уже работаю. Пришли голосовое сообщение, и я расшифрую его в текст."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Я умею отвечать на /start, /help, повторять обычные сообщения и расшифровывать голосовые."
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)


async def transcribe_audio(audio_bytes: bytes, deepgram_api_key: str) -> str:
    headers = {
        "Authorization": f"Token {deepgram_api_key}",
        "Content-Type": "audio/ogg",
    }
    params = {
        "model": DEEPGRAM_MODEL,
        "smart_format": "true",
        "detect_language": "true",
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            DEEPGRAM_URL,
            headers=headers,
            params=params,
            content=audio_bytes,
        )
        response.raise_for_status()

    data = response.json()
    channels = data.get("results", {}).get("channels", [])
    if not channels:
        return ""

    alternatives = channels[0].get("alternatives", [])
    if not alternatives:
        return ""

    return alternatives[0].get("transcript", "").strip()


async def ask_groq(prompt: str, groq_api_key: str) -> str:
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": os.getenv("GROQ_MODEL", GROQ_MODEL),
        "messages": [
            {
                "role": "system",
                "content": "Ты полезный ассистент. Отвечай на русском языке кратко и по делу.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(GROQ_URL, headers=headers, json=payload)
        response.raise_for_status()

    data = response.json()
    choices = data.get("choices", [])
    if not choices:
        return ""

    message = choices[0].get("message", {})
    content = message.get("content", "")
    return content.strip()


async def voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if message is None or message.voice is None:
        return

    deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
    if not deepgram_api_key:
        await message.reply_text(
            "Не найден DEEPGRAM_API_KEY. Добавь ключ Deepgram в файл .env."
        )
        return

    status_message = await message.reply_text("Я работаю...")

    try:
        voice_file = await message.voice.get_file()
        audio = await voice_file.download_as_bytearray()
        transcript = await transcribe_audio(bytes(audio), deepgram_api_key)
    except httpx.HTTPStatusError as error:
        logger.exception("Deepgram вернул ошибку")
        await status_message.edit_text(
            f"Deepgram не принял аудио: HTTP {error.response.status_code}."
        )
        return
    except Exception:
        logger.exception("Не удалось расшифровать голосовое сообщение")
        await status_message.edit_text("Не получилось расшифровать голосовое.")
        return

    if transcript:
        transcript_key = str(status_message.message_id)
        context.bot_data.setdefault(GROQ_TRANSCRIPTS_KEY, {})[transcript_key] = transcript
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Отправить в Groq",
                        callback_data=f"{GROQ_CALLBACK_PREFIX}{transcript_key}",
                    )
                ]
            ]
        )
        await status_message.edit_text(
            f"Расшифровка:\n\n{transcript}",
            reply_markup=keyboard,
        )
    else:
        await status_message.edit_text("Я не разобрал речь в этом голосовом.")


async def groq_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or query.data is None or query.message is None:
        return

    await query.answer()

    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        await query.message.reply_text(
            "Не найден GROQ_API_KEY. Добавь ключ Groq в файл .env."
        )
        return

    transcript_key = query.data.removeprefix(GROQ_CALLBACK_PREFIX)
    transcripts = context.bot_data.get(GROQ_TRANSCRIPTS_KEY, {})
    transcript = transcripts.get(transcript_key)
    if not transcript:
        await query.message.reply_text("Не нашел текст расшифровки для отправки в Groq.")
        return

    thinking_message = await query.message.reply_text("Отправляю в Groq...")

    try:
        answer = await ask_groq(transcript, groq_api_key)
    except httpx.HTTPStatusError as error:
        logger.exception("Groq вернул ошибку")
        await thinking_message.edit_text(
            f"Groq не принял запрос: HTTP {error.response.status_code}."
        )
        return
    except Exception:
        logger.exception("Не удалось получить ответ от Groq")
        await thinking_message.edit_text("Не получилось получить ответ от Groq.")
        return

    if answer:
        await thinking_message.edit_text(f"Ответ Groq:\n\n{answer}")
    else:
        await thinking_message.edit_text("Groq вернул пустой ответ.")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Ошибка во время обработки сообщения", exc_info=context.error)


def main() -> None:
    load_dotenv()
    token = os.getenv("BOT_TOKEN")

    if not token:
        print(
            "Не найден BOT_TOKEN. Создай файл .env по примеру .env.example и вставь токен бота."
        )
        sys.exit(1)

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(
        CallbackQueryHandler(groq_button, pattern=f"^{GROQ_CALLBACK_PREFIX}")
    )
    application.add_handler(MessageHandler(filters.VOICE, voice_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_error_handler(error_handler)

    logger.info("Бот запущен. Нажми Ctrl+C, чтобы остановить.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

import logging
import os
import sys

import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)

DEEPGRAM_URL = "https://api.deepgram.com/v1/listen"
DEEPGRAM_MODEL = "nova-3"


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
        await status_message.edit_text(f"Расшифровка:\n\n{transcript}")
    else:
        await status_message.edit_text("Я не разобрал речь в этом голосовом.")


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
    application.add_handler(MessageHandler(filters.VOICE, voice_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_error_handler(error_handler)

    logger.info("Бот запущен. Нажми Ctrl+C, чтобы остановить.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

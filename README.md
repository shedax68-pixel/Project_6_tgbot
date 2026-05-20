# Telegram Bot Starter

Минимальный проект для Telegram-бота на Python.

## Что уже подготовлено

- Локальное Python-окружение `.venv`
- Библиотека `python-telegram-bot`
- Библиотека `python-dotenv` для токена в `.env`
- Простой бот в `bot.py`

## Как запустить

1. Создай бота через Telegram-бота `@BotFather`.
2. Получи токен.
3. Создай файл `.env` рядом с `bot.py`:

```env
BOT_TOKEN=твой_токен_сюда
```

4. Запусти бота:

```bash
.venv/bin/python bot.py
```

5. Открой своего бота в Telegram и напиши `/start`.

## Если нужно установить зависимости заново

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Где писать логику

Сейчас бот:

- отвечает на `/start`
- отвечает на `/help`
- повторяет обычные текстовые сообщения

Новую логику удобнее добавлять отдельными функциями в `bot.py`, а потом подключать их через обработчики `CommandHandler` или `MessageHandler`.

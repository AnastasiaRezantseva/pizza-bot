import asyncio
import json
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, Update
from aiogram.utils.serialization import deserialize_telegram_object_to_python

import dotenv

dotenv.load_dotenv()

dp = Dispatcher()


@dp.message(F.text)
async def echo_text(message: Message) -> None:
    await message.answer(message.text)


@dp.message(F.photo)
async def echo_photo(message: Message) -> None:
    await message.answer_photo(message.photo[-1].file_id)


@dp.update.outer_middleware()
async def log_all_updates(handler, event: Update, data: dict):
    payload = deserialize_telegram_object_to_python(event)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return await handler(event, data)


async def main() -> None:
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_TOKEN is not set (check .env file)")

    bot = Bot(token=token)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

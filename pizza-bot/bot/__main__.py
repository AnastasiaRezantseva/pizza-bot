import asyncio
import bot.long_polling
from bot.dispatcher import Dispatcher
from bot.handlers import get_handlers
from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.infrastructure.messenger_telegram import MessengerTelegram
from bot.infrastructure.storage_postgres import StoragePostgres


async def main() -> None:
    storage: Storage = StoragePostgres()
    messenger: Messenger = MessengerTelegram()

    try:
        dispatcher = Dispatcher(storage, messenger)
        dispatcher.add_handlers(*get_handlers())

        await bot.long_polling.start_long_polling(dispatcher, messenger)

    except KeyboardInterrupt:
        print("\nBye!")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:

        if hasattr(storage, "close"):
            await storage.close()
        if hasattr(messenger, "close"):
            await messenger.close()


if __name__ == "__main__":
    asyncio.run(main())

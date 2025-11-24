from bot.dispatcher import Dispatcher
from bot.handlers import get_handlers
from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.infrastructure.messenger_telegram import MessengerTelegram
from bot.infrastructure.storage_sqlite import StorageSqlite
import bot.long_polling


def main() -> None:
    try:
        storage: Storage = StorageSqlite()
        messenger: Messenger = MessengerTelegram()

        dispatcher = Dispatcher(storage, messenger)
        dispatcher.add_handlers(*get_handlers())
        bot.long_polling.start_long_polling(dispatcher, messenger)
    except KeyboardInterrupt:
        print("\nBye!")


if __name__ == "__main__":
    main()

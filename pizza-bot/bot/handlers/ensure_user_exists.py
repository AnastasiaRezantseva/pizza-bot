from bot.domain.messenger import Messenger
from bot.handlers.handler import Handler, HandlerStatus
from bot.domain.storage import Storage


class EnsureUserExists(Handler):
    def can_handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> bool:
        return "message" in update and "from" in update["message"]

    def handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        telegram_id = update["message"]["from"]["id"]

        storage.ensure_user_exists(telegram_id)

        return HandlerStatus.CONTINUE

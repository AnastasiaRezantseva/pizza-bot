from bot.handlers.handler import Handler, HandlerStatus
from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.domain.order_state import OrderState

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class EnsureUserExists(Handler):

    def can_handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messanger: Messenger,
    ) -> bool:
        return "message" in update and "from" in update["message"]

    async def handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messanger: Messenger,
    ) -> bool:
        logger.info("[HANDLER] EnsureUserExists handle start")
        telegram_id = update["message"]["from"]["id"]
        await storage.ensure_user_exists(telegram_id)
        logger.info("[HANDLER] EnsureUserExists handle end")
        return HandlerStatus.CONTINUE

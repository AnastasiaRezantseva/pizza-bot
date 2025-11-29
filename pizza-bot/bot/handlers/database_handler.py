import logging
from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus
from bot.domain.order_state import OrderState

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class UpdateDatabaseLogger(Handler):
    def can_handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> bool:
        return True

    async def handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        await storage.persist_updates(update)
        return HandlerStatus.CONTINUE

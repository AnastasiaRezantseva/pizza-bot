import json
import asyncio
import logging

from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus
from bot.keyboards.order_keyboards import pizza_keyboard
from bot.domain.order_state import OrderState


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class MessageStart(Handler):
    def can_handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> bool:
        return (
            "message" in update
            and "text" in update["message"]
            and update["message"]["text"] == "/start"
        )

    async def handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        logger.info("[HANDLER] handle MessageStart start")
        telegram_id = update["message"]["from"]["id"]

        await storage.clear_user_state_order(telegram_id)
        await storage.update_user_state(telegram_id, OrderState.WAIT_FOR_PIZZA_NAME)

        await asyncio.gather(
            messenger.send_message(
                chat_id=update["message"]["chat"]["id"],
                text="🍕 Welcome to Pizza shop!😋",
                reply_markup=json.dumps({"remove_keyboard": True}),
            ),
            messenger.send_message(
                chat_id=update["message"]["chat"]["id"],
                text="Please, choose pizza name:",
                reply_markup=pizza_keyboard(),
            ),
        )
        logger.info("[HANDLER] handle MessageStart end")
        return HandlerStatus.STOP

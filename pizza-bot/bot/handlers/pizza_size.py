import asyncio
import logging

from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus
from bot.keyboards.order_keyboards import drinks_keyboard
from bot.domain.order_state import OrderState

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class PizzaSizeHandler(Handler):
    def can_handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> bool:
        if "callback_query" not in update:
            return False

        if state != OrderState.WAIT_FOR_PIZZA_SIZE:
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("size_")

    async def handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        logger.info("[HANDLER] PizzaSizeHandler handle start")
        telegram_id = update["callback_query"]["from"]["id"]
        callback_data = update["callback_query"]["data"]
        chat_id = update["callback_query"]["message"]["chat"]["id"]

        size_mapping = {
            "size_small": "Small (25cm)",
            "size_medium": "Medium (30cm)",
            "size_large": "Large (35cm)",
            "size_xl": "Extra Large (40cm)",
        }

        pizza_size = size_mapping.get(callback_data)
        order_json["pizza_size"] = pizza_size

        await asyncio.gather(
            storage.update_user_order(telegram_id, order_json),
            storage.update_user_state(telegram_id, OrderState.WAIT_FOR_DRINKS),
            messenger.answer_callback_query(update["callback_query"]["id"]),
            messenger.delete_message(
                chat_id=chat_id,
                message_id=update["callback_query"]["message"]["message_id"],
            ),
        )
        await messenger.send_message(
            chat_id=chat_id,
            text="Please choose some drinks",
            reply_markup=drinks_keyboard(),
        )

        logger.info("[HANDLER] PizzaSizeHandler handle end")
        return HandlerStatus.STOP

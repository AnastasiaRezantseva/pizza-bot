import json

from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus
from bot.keyboards.order_keyboards import pizza_keyboard
from bot.domain.order_state import OrderState


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

    def handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        telegram_id = update["message"]["from"]["id"]

        storage.clear_user_state_order(telegram_id)
        storage.update_user_state(telegram_id, OrderState.WAIT_FOR_PIZZA_NAME)

        messenger.send_message(
            chat_id=update["message"]["chat"]["id"],
            text="🍕 Welcome to Pizza shop!😋",
            reply_markup=json.dumps({"remove_keyboard": True}),
        )

        messenger.send_message(
            chat_id=update["message"]["chat"]["id"],
            text="Please, choose pizza name:",
            reply_markup=pizza_keyboard(),
        )

        return HandlerStatus.STOP

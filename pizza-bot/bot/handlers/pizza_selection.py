from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus
from bot.keyboards.order_keyboards import size_keyboard
from bot.domain.order_state import OrderState

class PizzaSelectionHandler(Handler):
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

        if state != OrderState.WAIT_FOR_PIZZA_NAME:
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("pizza_")

    def handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        callback_data = update["callback_query"]["data"]
        chat_id = update["callback_query"]["message"]["chat"]["id"]

        pizza_name = callback_data.replace("pizza_", "").replace("_", " ").title()
        storage.update_user_order(telegram_id, {"pizza_name": pizza_name})
        storage.update_user_state(telegram_id, OrderState.WAIT_FOR_PIZZA_SIZE)
        messenger.answer_callback_query(update["callback_query"]["id"])
        messenger.delete_message(
            chat_id=chat_id,
            message_id=update["callback_query"]["message"]["message_id"],
        )
        messenger.send_message(
            chat_id=chat_id,
            text="📐Please, select pizza size:",
            reply_markup=size_keyboard(),
        )
        return HandlerStatus.STOP

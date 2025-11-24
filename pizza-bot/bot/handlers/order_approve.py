from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus
from bot.keyboards.order_keyboards import pizza_keyboard


class OrderApprovalHandler(Handler):
    def can_handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> bool:
        if "callback_query" not in update:
            return False

        if state != "WAIT_FOR_ORDER_APPROVE":
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data in ["order_approve", "order_restart"]

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

        messenger.answer_callback_query(update["callback_query"]["id"])
        messenger.delete_message(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            message_id=update["callback_query"]["message"]["message_id"],
        )

        if callback_data == "order_approve":
            storage.update_user_state(telegram_id, "ORDER_FINISHED")

            pizza_name = order_json.get("pizza_name", "Unknown")
            pizza_size = order_json.get("pizza_size", "Unknown")
            drink = order_json.get("drink", "Unknown")

            order_confirmation = f"""✅ **Order Confirmed!**
🍕 **Your Order:**
• Pizza: {pizza_name}
• Size: {pizza_size}
• Drink: {drink}

Thank you for your order! Your pizza will be ready soon.

Send /start to place another order."""

            messenger.send_message(
                chat_id=update["callback_query"]["message"]["chat"]["id"],
                text=order_confirmation,
                parse_mode="Markdown",
            )

        elif callback_data == "order_restart":
            storage.clear_user_order_json(telegram_id)

            storage.update_user_state(telegram_id, "WAIT_FOR_PIZZA_NAME")

            messenger.send_message(
                chat_id=update["callback_query"]["message"]["chat"]["id"],
                text="Please choose pizza type",
                reply_markup=pizza_keyboard(),
            )

        return HandlerStatus.STOP

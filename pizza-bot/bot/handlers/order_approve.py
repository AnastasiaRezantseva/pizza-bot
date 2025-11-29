import asyncio
import logging
from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus
from bot.keyboards.order_keyboards import pizza_keyboard
from bot.domain.order_state import OrderState

logger = logging.getLogger(__name__)


class OrderApprovalHandler(Handler):
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

        if state != OrderState.WAIT_FOR_ORDER_APPROVE:
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data in ["order_approve", "order_restart"]

    async def handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        logger.info("[HANDLER] handle OrderApprovalHandler start")
        telegram_id = update["callback_query"]["from"]["id"]
        callback_data = update["callback_query"]["data"]
        chat_id = update["callback_query"]["message"]["chat"]["id"]

        await asyncio.gather(
            messenger.answer_callback_query(update["callback_query"]["id"]),
            messenger.delete_message(
                chat_id=chat_id,
                message_id=update["callback_query"]["message"]["message_id"],
            ),
        )

        if callback_data == "order_approve":
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

            await asyncio.gather(
                storage.update_user_state(telegram_id, OrderState.ORDER_FINISHED),
                messenger.send_message(
                    chat_id=chat_id,
                    text=order_confirmation,
                    parse_mode="Markdown",
                ),
            )

        elif callback_data == "order_restart":
            await storage.clear_user_state_order(telegram_id)
            await storage.update_user_state(telegram_id, OrderState.WAIT_FOR_PIZZA_NAME)

            await messenger.send_message(
                chat_id=chat_id,
                text="Please choose pizza type",
                reply_markup=pizza_keyboard(),
            )

        logger.info("[HANDLER] handle OrderApprovalHandler end")
        return HandlerStatus.STOP

import asyncio
import logging

from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus
from bot.keyboards.order_keyboards import check_order_keyboard
from bot.domain.order_state import OrderState

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class PizzaDrinksHandler(Handler):
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

        if state != OrderState.WAIT_FOR_DRINKS:
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("drink_")

    async def handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        logger.info("[HANDLER] PizzaDrinksHandler handle start")
        telegram_id = update["callback_query"]["from"]["id"]
        callback_data = update["callback_query"]["data"]

        drink_mapping = {
            "drink_coca_cola": "Coca-Cola",
            "drink_pepsi": "Pepsi",
            "drink_orange_juice": "Orange Juice",
            "drink_apple_juice": "Apple Juice",
            "drink_water": "Water",
            "drink_iced_tea": "Iced Tea",
            "drink_none": "No drinks",
        }
        selected_drink = drink_mapping.get(callback_data)
        order_json["drink"] = selected_drink

        await asyncio.gather(
            storage.update_user_order(telegram_id, order_json),
            storage.update_user_state(telegram_id, OrderState.WAIT_FOR_ORDER_APPROVE),
            messenger.answer_callback_query(update["callback_query"]["id"]),
            messenger.delete_message(
                chat_id=update["callback_query"]["message"]["chat"]["id"],
                message_id=update["callback_query"]["message"]["message_id"],
            ),
        )

        user_order = await storage.get_user_order(telegram_id)

        if not user_order:
            await asyncio.gather(
                messenger.send_message(
                    chat_id=update["callback_query"]["message"]["chat"]["id"],
                    text="The basket is empty! Something went wrong!",
                ),
                storage.update_user_state(telegram_id, OrderState.WAIT_FOR_PIZZA_NAME),
            )
            logger.info("[HANDLER] PizzaDrinksHandler handle end")
            return HandlerStatus.CONTINUE
        else:
            pizza_name = user_order.get("pizza_name", "Unknown")
            pizza_size = user_order.get("pizza_size", "Unknown")
            drink = user_order.get("drink", "Unknown")

            order_summary = f"""🍕 **Your Order Summary:**

**Pizza:** {pizza_name}
**Size:** {pizza_size}
**Drink:** {drink}

Is everything correct?"""

            await messenger.send_message(
                chat_id=update["callback_query"]["message"]["chat"]["id"],
                text=order_summary,
                parse_mode="Markdown",
                reply_markup=check_order_keyboard(),
            )

        logger.info("[HANDLER] PizzaDrinksHandler handle end")
        return HandlerStatus.STOP

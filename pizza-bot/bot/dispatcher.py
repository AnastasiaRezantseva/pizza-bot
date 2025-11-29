import json
import logging
import time
from bot.handlers.handler import Handler, HandlerStatus
from bot.domain.messenger import Messenger
from bot.domain.storage import Storage

logger = logging.getLogger(__name__)


class Dispatcher:
    def __init__(self, storage: Storage, messenger: Messenger) -> None:
        self._handlers: list[Handler] = []
        self._storage: Storage = storage
        self._messenger: Messenger = messenger

    def unused_method(self) -> None:
        return None

    def add_handlers(self, *handlers: Handler) -> None:
        for handler in handlers:
            self._handlers.append(handler)

    def _get_telegram_id_from_update(self, update: dict) -> int | None:
        if "message" in update:
            return update["message"]["from"]["id"]
        elif "callback_query" in update:
            return update["callback_query"]["from"]["id"]
        return None

    async def dispatch(self, update: dict) -> None:
        update_id = update["update_id"]
        start_time = time.time()
        logger.info(f"[DISPATCH {update_id}] → dispatch started")
        try:
            telegram_id = self._get_telegram_id_from_update(update)

            user = await self._storage.get_user(telegram_id) if telegram_id else None

            user_state = user.get("state") if user else None

            user_data = user["order_json"] if user else "{}"
            if user_data is None:
                user_data = "{}"
            order_data = json.loads(user_data)

            if telegram_id:
                await self._storage.ensure_user_exists(telegram_id)

            for handler in self._handlers:
                if handler.can_handle(
                    update,
                    user_state,
                    order_data,
                    self._storage,
                    self._messenger,
                ):
                    status = await handler.handle(
                        update,
                        user_state,
                        order_data,
                        self._storage,
                        self._messenger,
                    )
                    if status == HandlerStatus.STOP:
                        break

            duration_ms = (time.time() - start_time) * 1000
            logger.info(
                f"[DISPATCH {update_id}] ← dispatch finished - {duration_ms:.2f}ms\n"
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"[DISPATCH {update_id}] ✗ dispatch failed - {duration_ms:.2f}ms - Error: {e}\n"
            )
            raise

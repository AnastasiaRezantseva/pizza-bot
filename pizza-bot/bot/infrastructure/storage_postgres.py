import json
import os
import logging
import asyncpg
from dotenv import load_dotenv

from bot.domain.order_state import OrderState
from bot.domain.storage import Storage

load_dotenv()

logger = logging.getLogger(__name__)


class StoragePostgres(Storage):
    def __init__(self) -> None:
        self._pool: asyncpg.Pool | None = None

    async def _get_pool(self) -> asyncpg.Pool:
        """Create and return a PostgreSQL connection pool."""
        if self._pool is None:
            host = os.getenv("POSTGRES_HOST")
            port = os.getenv("POSTGRES_PORT")
            user = os.getenv("POSTGRES_USER")
            password = os.getenv("POSTGRES_PASSWORD")
            database = os.getenv("POSTGRES_DATABASE")

            if host is None:
                raise ValueError("POSTGRES_HOST environment variable is not set")
            if port is None:
                raise ValueError("POSTGRES_PORT environment variable is not set")
            if user is None:
                raise ValueError("POSTGRES_USER environment variable is not set")
            if password is None:
                raise ValueError("POSTGRES_PASSWORD environment variable is not set")
            if database is None:
                raise ValueError("POSTGRES_DATABASE environment variable is not set")

            self._pool = await asyncpg.create_pool(
                host=host,
                port=int(port),
                user=user,
                password=password,
                database=database,
            )
        return self._pool

    async def close(self) -> None:
        """Close the connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None

    async def persist_updates(self, updates: list) -> None:
        """Сохранение нескольких обновлений"""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            for update in updates:
                payload = json.dumps(update, ensure_ascii=False, indent=2)
                await conn.execute(
                    "INSERT INTO telegram_events (payload) VALUES ($1)", payload
                )

    async def update_user_order(self, telegram_id: int, order: dict) -> None:
        """Обновление заказа пользователя"""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET order_json = $1 WHERE telegram_id = $2",
                json.dumps(order, ensure_ascii=False, indent=2),
                telegram_id,
            )

    async def recreate_database(self) -> None:
        """Пересоздание базы данных"""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute("DROP TABLE IF EXISTS telegram_events")
            await conn.execute("DROP TABLE IF EXISTS users")
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS telegram_events
                (
                    id SERIAL PRIMARY KEY,
                    payload TEXT NOT NULL
                )
            """
            )
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users
                (
                    id SERIAL PRIMARY KEY,
                    telegram_id BIGINT NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    state TEXT DEFAULT NULL,
                    order_json TEXT DEFAULT NULL
                )
            """
            )

    async def get_user(self, telegram_id: int | None) -> dict | None:
        """Получение пользователя"""
        if telegram_id is None:
            return None

        pool = await self._get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, telegram_id, created_at, state, order_json FROM users WHERE telegram_id = $1",
                telegram_id,
            )
            if row:
                return {
                    "id": row["id"],
                    "telegram_id": row["telegram_id"],
                    "created_at": row["created_at"],
                    "state": row["state"],
                    "order_json": row["order_json"],
                }
            return None

    async def clear_user_state_order(self, telegram_id: int) -> None:
        """Очистка состояния и заказа пользователя"""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET state = NULL, order_json = NULL WHERE telegram_id = $1",
                telegram_id,
            )

    async def update_user_state(self, telegram_id: int, state: OrderState) -> None:
        """Обновление состояния пользователя"""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET state = $1 WHERE telegram_id = $2",
                state.value if hasattr(state, "value") else str(state),
                telegram_id,
            )

    async def get_user_order(self, telegram_id: int | None) -> dict | None:
        """Получение заказа пользователя"""
        if telegram_id is None:
            return None

        user = await self.get_user(telegram_id)
        if user and user.get("order_json"):
            try:
                return json.loads(user["order_json"])
            except json.JSONDecodeError:
                return None
        return None

    async def ensure_user_exists(self, telegram_id: int) -> None:
        """Создание пользователя если не существует"""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            exists = await conn.fetchval(
                "SELECT 1 FROM users WHERE telegram_id = $1", telegram_id
            )
            if not exists:
                await conn.execute(
                    "INSERT INTO users (telegram_id) VALUES ($1)", telegram_id
                )

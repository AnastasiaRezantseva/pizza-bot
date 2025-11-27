import json
import os
import pg8000
from dotenv import load_dotenv

from bot.domain.order_state import OrderState
from bot.domain.storage import Storage

load_dotenv()


class StoragePostgres(Storage):
    def _get_connection(self):
        """Create and return a PostgreSQL connection."""
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

        return pg8000.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=database,
        )

    def persist_updates(self, updates: list) -> None:
        """Сохранение нескольких обновлений"""
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                for update in updates:
                    payload = json.dumps(update, ensure_ascii=False, indent=2)
                    cursor.execute(
                        "INSERT INTO telegram_events (payload) VALUES (%s)", (payload,)
                    )
            connection.commit()

    def update_user_order(self, telegram_id: int, order: dict) -> None:
        """Обновление заказа пользователя"""
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET order_json = %s WHERE telegram_id = %s",
                    (json.dumps(order, ensure_ascii=False, indent=2), telegram_id),
                )
            connection.commit()

    def recreate_database(self) -> None:
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DROP TABLE IF EXISTS telegram_events")
                cursor.execute("DROP TABLE IF EXISTS users")
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS telegram_events
                    (
                        id SERIAL PRIMARY KEY,
                        payload TEXT NOT NULL
                    )
                    """
                )
                cursor.execute(
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
            connection.commit()

    def get_user(self, telegram_id: int | None) -> dict | None:
        """Получение пользователя"""
        if telegram_id is None:
            return None

        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id, telegram_id, created_at, state, order_json FROM users WHERE telegram_id = %s",
                    (telegram_id,),
                )
                result = cursor.fetchone()
                if result:
                    return {
                        "id": result[0],
                        "telegram_id": result[1],
                        "created_at": result[2],
                        "state": result[3],
                        "order_json": result[4],
                    }
                return None

    def clear_user_state_order(self, telegram_id: int) -> None:
        """Очистка состояния и заказа пользователя"""
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET state = NULL, order_json = NULL WHERE telegram_id = %s",
                    (telegram_id,),
                )
            connection.commit()

    def update_user_state(self, telegram_id: int, state: OrderState) -> None:
        """Обновление состояния пользователя"""
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET state = %s WHERE telegram_id = %s",
                    (
                        state.value if hasattr(state, "value") else str(state),
                        telegram_id,
                    ),
                )
            connection.commit()

    def get_user_order(self, telegram_id: int | None) -> dict | None:
        """Получение заказа пользователя"""
        if telegram_id is None:
            return None

        user = self.get_user(telegram_id)
        if user and user.get("order_json"):
            try:
                return json.loads(user["order_json"])
            except json.JSONDecodeError:
                return None
        return None

    def ensure_user_exists(self, telegram_id: int) -> None:
        """Создание пользователя если не существует"""
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM users WHERE telegram_id = %s",
                    (telegram_id,),
                )

                if cursor.fetchone() is None:
                    cursor.execute(
                        "INSERT INTO users (telegram_id) VALUES (%s)",
                        (telegram_id,),
                    )
            connection.commit()

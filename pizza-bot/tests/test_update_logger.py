import pytest
from bot.dispatcher import Dispatcher
from bot.handlers.database_handler import UpdateDatabaseLogger
from tests.mocks import Mock


@pytest.mark.asyncio
async def test_update_database_logger_execution():
    test_update = {
        "update_id": 123456789,
        "message": {
            "message_id": 1,
            "from": {
                "id": 12345,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser",
            },
            "chat": {
                "id": 12345,
                "first_name": "Test",
                "username": "testuser",
                "type": "private",
            },
            "date": 1640995200,
            "text": "Hello, this is a test message",
        },
    }

    persist_updates_called = False
    ensure_user_exists_called = False

    async def persist_updates(update: dict) -> None:
        nonlocal persist_updates_called
        persist_updates_called = True
        assert update == test_update

    async def get_user(telegram_id: int) -> dict | None:
        assert telegram_id == 12345
        return None

    async def ensure_user_exists(telegram_id: int) -> None:
        assert telegram_id == 12345
        nonlocal ensure_user_exists_called
        ensure_user_exists_called = True

    mock_storage = Mock(
        {
            "persist_updates": persist_updates,
            "get_user": get_user,
            "ensure_user_exists": ensure_user_exists,
        }
    )
    mock_messenger = Mock({})

    dispatcher = Dispatcher(mock_storage, mock_messenger)
    update_logger = UpdateDatabaseLogger()
    dispatcher.add_handlers(update_logger)
    await dispatcher.dispatch(test_update)

    assert persist_updates_called
    assert ensure_user_exists_called

import pytest

from bot.dispatcher import Dispatcher
from bot.handlers.ensure_user_exists import EnsureUserExists
from tests.mocks import Mock


@pytest.mark.asyncio
async def test_ensure_user_exists_handler():
    test_update = {
        "update_id": 123456789,
        "message": {
            "message_id": 1,
            "from": {
                "id": 12345,
                "is_bot": False,
                "first_name": "Test",
            },
            "chat": {"id": 12345, "type": "private"},
            "date": 1640995200,
            "text": "Hello",
        },
    }

    ensure_user_exists_called = False

    async def ensure_user_exists(telegram_id: int) -> None:
        assert telegram_id == 12345
        nonlocal ensure_user_exists_called
        ensure_user_exists_called = True

    async def get_user(telegram_id: int) -> dict | None:
        assert telegram_id == 12345
        return None

    mock_storage = Mock(
        {
            "ensure_user_exists": ensure_user_exists,
            "get_user": get_user,
        }
    )
    mock_messenger = Mock({})

    dispatcher = Dispatcher(mock_storage, mock_messenger)
    dispatcher.add_handlers(EnsureUserExists())

    await dispatcher.dispatch(test_update)

    assert ensure_user_exists_called

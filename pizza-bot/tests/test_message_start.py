import pytest

from bot.dispatcher import Dispatcher
from bot.handlers.message_start import MessageStart
from bot.domain.order_state import OrderState

from tests.mocks import Mock


@pytest.mark.asyncio
async def test_message_start_handler():
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
            "text": "/start",
        },
    }

    clear_user_state_order_called = False
    update_user_state_called = False
    ensure_user_exists_called = False

    async def clear_user_state_order(telegram_id: int) -> None:
        assert telegram_id == 12345
        nonlocal clear_user_state_order_called
        clear_user_state_order_called = True

    async def update_user_state(telegram_id: int, state: OrderState) -> None:
        assert telegram_id == 12345
        assert state == OrderState.WAIT_FOR_PIZZA_NAME
        nonlocal update_user_state_called
        update_user_state_called = True

    async def get_user(telegram_id: int) -> dict | None:
        assert telegram_id == 12345
        return {"state": None, "order_json": "{}"}

    async def ensure_user_exists(telegram_id: int) -> None:
        assert telegram_id == 12345
        nonlocal ensure_user_exists_called
        ensure_user_exists_called = True

    send_message_calls = []

    async def send_message(chat_id: int, text: str, **kwargs) -> dict:
        assert chat_id == 12345
        send_message_calls.append({"text": text, "kwargs": kwargs})
        return {"ok": True}

    mock_storage = Mock(
        {
            "clear_user_state_order": clear_user_state_order,
            "update_user_state": update_user_state,
            "get_user": get_user,
            "ensure_user_exists": ensure_user_exists,
        }
    )
    mock_messenger = Mock({"send_message": send_message})

    dispatcher = Dispatcher(mock_storage, mock_messenger)
    dispatcher.add_handlers(MessageStart())

    await dispatcher.dispatch(test_update)

    assert clear_user_state_order_called
    assert update_user_state_called
    assert ensure_user_exists_called

    assert len(send_message_calls) == 2
    assert send_message_calls[0]["text"] == "🍕 Welcome to Pizza shop!😋"
    assert send_message_calls[1]["text"] == "Please, choose pizza name:"

import pytest
from bot.dispatcher import Dispatcher
from bot.handlers.pizza_size import PizzaSizeHandler
from tests.mocks import Mock


@pytest.mark.asyncio
async def test_pizza_size_handler():
    test_update = {
        "update_id": 123456789,
        "callback_query": {
            "id": "123",
            "from": {"id": 12345},
            "message": {
                "message_id": 10,
                "chat": {"id": 12345},
            },
            "data": "size_medium",
        },
    }

    update_user_order_json_called = False
    update_user_state_called = False
    ensure_user_exists_called = False
    send_message_calls = []

    async def update_user_order(telegram_id: int, data: dict) -> None:
        assert telegram_id == 12345
        assert data["pizza_size"] == "Medium (30cm)"
        nonlocal update_user_order_json_called
        update_user_order_json_called = True

    async def update_user_state(telegram_id: int, state: str) -> None:
        assert telegram_id == 12345
        assert state == "WAIT_FOR_DRINKS"
        nonlocal update_user_state_called
        update_user_state_called = True

    async def ensure_user_exists(telegram_id: int) -> None:
        nonlocal ensure_user_exists_called
        ensure_user_exists_called = True

    async def send_message(chat_id: int, text: str, **kwargs) -> dict:
        assert chat_id == 12345
        assert "Please choose some drinks" in text
        send_message_calls.append({"text": text, "kwargs": kwargs})
        return {"ok": True}

    async def answer_callback_query(callback_query_id: str) -> None:
        assert callback_query_id == "123"

    async def delete_message(chat_id: int, message_id: int) -> None:
        assert chat_id == 12345
        assert message_id == 10

    mock_storage = Mock(
        {
            "update_user_order": update_user_order,
            "update_user_state": update_user_state,
            "ensure_user_exists": ensure_user_exists,
        }
    )
    mock_messenger = Mock(
        {
            "send_message": send_message,
            "answer_callback_query": answer_callback_query,
            "delete_message": delete_message,
        }
    )

    dispatcher = Dispatcher(mock_storage, mock_messenger)
    dispatcher.add_handlers(PizzaSizeHandler())

    async def async_get_user(telegram_id: int):
        return {
            "state": "WAIT_FOR_PIZZA_SIZE",
            "order_json": '{"pizza_name": "Pepperoni"}',
        }

    dispatcher._storage.get_user = async_get_user

    await dispatcher.dispatch(test_update)

    assert update_user_order_json_called
    assert update_user_state_called
    assert ensure_user_exists_called
    assert len(send_message_calls) == 1

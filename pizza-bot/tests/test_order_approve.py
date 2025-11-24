from bot.dispatcher import Dispatcher
from bot.handlers.order_approve import OrderApprovalHandler
from tests.mocks import Mock


def test_order_approve_handler():
    """Test order approval flow - when user confirms order"""
    test_update = {
        "update_id": 123456789,
        "callback_query": {
            "id": "123",
            "from": {"id": 12345},
            "message": {
                "message_id": 10,
                "chat": {"id": 12345},
            },
            "data": "order_approve",
        },
    }

    update_user_state_called = False
    send_message_calls = []

    def update_user_state(telegram_id: int, state: str) -> None:
        assert telegram_id == 12345
        assert state == "ORDER_FINISHED"
        nonlocal update_user_state_called
        update_user_state_called = True

    def send_message(chat_id: int, text: str, **kwargs) -> dict:
        assert chat_id == 12345
        assert "Order Confirmed!" in text
        assert "Pepperoni" in text
        assert "Medium" in text
        assert "Coca-Cola" in text
        assert "Thank you for your order" in text
        assert "Send /start to place another order" in text
        send_message_calls.append({"text": text, "kwargs": kwargs})
        return {"ok": True}

    def answer_callback_query(callback_query_id: str) -> None:
        assert callback_query_id == "123"

    def delete_message(chat_id: int, message_id: int) -> None:
        assert chat_id == 12345
        assert message_id == 10

    mock_storage = Mock(
        {
            "update_user_state": update_user_state,
            "clear_user_order_json": lambda tid: None,  # Not called in approve flow
            "get_user": lambda tid: {
                "state": "WAIT_FOR_ORDER_APPROVE",
                "order_json": '{"pizza_name": "Pepperoni", "pizza_size": "Medium", "drink": "Coca-Cola"}',
            },
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
    dispatcher.add_handlers(OrderApprovalHandler())

    dispatcher.dispatch(test_update)

    assert update_user_state_called
    assert len(send_message_calls) == 1
    assert "parse_mode" in send_message_calls[0]["kwargs"]
    assert send_message_calls[0]["kwargs"]["parse_mode"] == "Markdown"


def test_order_approve_handler_restart():
    """Test order restart flow - when user wants to restart order"""
    test_update = {
        "update_id": 123456789,
        "callback_query": {
            "id": "123",
            "from": {"id": 12345},
            "message": {
                "message_id": 10,
                "chat": {"id": 12345},
            },
            "data": "order_restart",
        },
    }

    update_user_state_called = False
    clear_user_order_json_called = False
    send_message_calls = []

    def update_user_state(telegram_id: int, state: str) -> None:
        assert telegram_id == 12345
        assert state == "WAIT_FOR_PIZZA_NAME"
        nonlocal update_user_state_called
        update_user_state_called = True

    def clear_user_order_json(telegram_id: int) -> None:
        assert telegram_id == 12345
        nonlocal clear_user_order_json_called
        clear_user_order_json_called = True

    def send_message(chat_id: int, text: str, **kwargs) -> dict:
        assert chat_id == 12345
        assert "Please choose pizza type" in text
        assert "reply_markup" in kwargs
        send_message_calls.append({"text": text, "kwargs": kwargs})
        return {"ok": True}

    def answer_callback_query(callback_query_id: str) -> None:
        assert callback_query_id == "123"

    def delete_message(chat_id: int, message_id: int) -> None:
        assert chat_id == 12345
        assert message_id == 10

    mock_storage = Mock(
        {
            "update_user_state": update_user_state,
            "clear_user_order_json": clear_user_order_json,
            "get_user": lambda tid: {
                "state": "WAIT_FOR_ORDER_APPROVE",
                "order_json": '{"pizza_name": "Pepperoni", "pizza_size": "Medium", "drink": "Coca-Cola"}',
            },
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
    dispatcher.add_handlers(OrderApprovalHandler())

    dispatcher.dispatch(test_update)

    assert update_user_state_called
    assert clear_user_order_json_called
    assert len(send_message_calls) == 1
    assert "reply_markup" in send_message_calls[0]["kwargs"]
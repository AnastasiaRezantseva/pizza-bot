from abc import ABC, abstractmethod
from enum import Enum

from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.domain.order_state import OrderState

class HandlerStatus(Enum):
    CONTINUE = 1
    STOP = 2


class Handler(ABC):
    @abstractmethod
    def can_handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> bool: ...

    @abstractmethod
    def handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus: ...

import queue

from datetime import datetime
from abc import ABCMeta, abstractmethod
from event import FillEvent, OrderEvent

class ExecutionHandler(metaclass=ABCMeta):
    @abstractmethod
    def execute_order(self, event):
        raise NotImplementedError

class SimulateExecutionHandler(ExecutionHandler):
    def __init__(self, events):
        self.events = events

    def execute_order(self, event):
        if event.type == 'ORDER':
            print(event.type, event.symbol, event.quantity, event.direction)
            fill_event = FillEvent(datetime.utcnow(), event.symbol, 'ARCA', event.quantity, event.direction, 0)
            self.events.put(fill_event)

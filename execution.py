import queue

from datetime import datetime
from abc import ABCMeta, abstractmethod
from event import FillEvent, OrderEvent

class ExecutionHandler(metaclass=ABCMeta):
    @abstractmethod
    def execute_order(self, event):
        raise NotImplementedError

class SimulateExecutionHandler(ExecutionHandler):
    def __init__(self, events, verbose=False):
        self.events = events
        self.verbose = verbose

    def execute_order(self, event):
        if event.type == 'ORDER':
            if self.verbose: print("Order Executed:", event.symbol, event.quantity, event.direction)
            fill_event = FillEvent(datetime.utcnow(), event.symbol, 'ARCA', event.quantity, event.direction, 0)
            self.events.put(fill_event)

import pandas as pd
import math
from datetime import datetime
from event import SignalEvent
from strategies.strategy import Strategy

class BuyAndHoldStrategy(Strategy):
    def __init__(self, data, events, portfolio):
        self.data = data
        self.symbol_list = self.data.symbol_list
        self.events = events
        self.portfolio = portfolio
        self.name = 'Buy and Hold'

        self.bought = self._calculate_initial_bought()

    def _calculate_initial_bought(self):
        bought = {}
        for symbol in self.symbol_list:
            bought[symbol] = False

        return bought

    def calculate_signals(self, event):
        if event.type == 'MARKET':
            for symbol in self.symbol_list:
                data = self.data.get_latest_data(symbol, N=1)
                if data is not None and len(data) > 0:
                    if self.bought[symbol] == False:
                        quantity = math.floor(self.portfolio.current_holdings['cash'] / data[-1][self.data.price_col])
                        signal = SignalEvent(symbol, data[0][self.data.time_col], 'LONG', quantity)
                        self.events.put(signal)
                        self.bought[symbol] = True

class SellAndHoldStrategy(Strategy):
    def __init__(self, data, events, portfolio):
        self.data = data
        self.symbol_list = self.data.symbol_list
        self.events = events
        self.portfolio = portfolio
        self.name = 'Sell and Hold'

        self.bought = self._calculate_initial_bought()

    def _calculate_initial_bought(self):
        bought = {}
        for symbol in self.symbol_list:
            bought[symbol] = False

        return bought

    def calculate_signals(self, event):
        if event.type == 'MARKET':
            for symbol in self.symbol_list:
                data = self.data.get_latest_data(symbol)
                if data is not None and len(data) > 0:
                    if self.bought[symbol] == False:
                        quantity = math.floor(self.portfolio.current_holdings['cash'] / data[-1][self.data.price_col])
                        signal = SignalEvent(symbol, data[0][self.data.time_col], 'SHORT', quantity)
                        self.events.put(signal)
                        self.bought[symbol] = True
import pandas as pd
from datetime import datetime
from abc import ABCMeta, abstractmethod
from event import SignalEvent

class Strategy(metaclass=ABCMeta):
    @abstractmethod
    def calculate_signals(self):
        raise NotImplementedError

class BuyAndHoldStrategy(Strategy):
    def __init__(self, data, events):
        self.data = data
        self.symbol_list = self.data.symbol_list
        self.events = events

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
                        signal = SignalEvent(symbol, data[0][1], 'LONG', 1)
                        self.events.put(signal)
                        self.bought[symbol] = True

class MovingAveragesStrategy(Strategy):
    def __init__(self, data, events):
        self.data = data
        self.symbol_list = self.data.symbol_list
        self.events = events

        self.bought = self._calculate_initial_bought()

    def _calculate_initial_bought(self):
        bought = {}
        for symbol in self.symbol_list:
            bought[symbol] = False

        return bought

    def calculate_signals(self, event):
        if event.type == 'MARKET':
            for symbol in self.symbol_list:
                data = self.data.get_latest_data(symbol, N=26)
                df = pd.DataFrame(data, columns=['symbol','datetime','open','high','low','close','adj_close','volume'])
                df = df.drop(['symbol'], axis=1)
                df.set_index('datetime', inplace=True)
                if data is not None and len(data) >= 26:
                    df_short = df['close'].ewm(12).mean()
                    df_long = df['close'].ewm(26).mean()
                    if self.bought[symbol] == False and df_short.tail(1)[0] > df_long.tail(1)[0]:
                        signal = SignalEvent(symbol, data[-1][1], 'LONG', 1)
                        self.events.put(signal)
                        print("Buy:", data[-1][1], data[-1][5])
                        self.bought[symbol] = True
                    elif self.bought[symbol] == True and df_short.tail(1)[0] < df_long.tail(1)[0]:
                        signal = SignalEvent(symbol, data[-1][1], 'EXIT', 1)
                        self.events.put(signal)
                        print("Sell:", data[-1][1], data[-1][5])
                        self.bought[symbol] = False

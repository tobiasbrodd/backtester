import pandas as pd
from datetime import datetime
from abc import ABCMeta, abstractmethod
from event import SignalEvent

class Strategy(metaclass=ABCMeta):
    @abstractmethod
    def calculate_signals(self):
        raise NotImplementedError

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
                        quantity = self.portfolio.current_holdings['cash'] / self.data.get_latest_data(symbol, N=1)[0][self.data.price_col]
                        signal = SignalEvent(symbol, data[0][self.data.time_col], 'LONG', quantity)
                        self.events.put(signal)
                        self.bought[symbol] = True

class MovingAveragesStrategy(Strategy):
    def __init__(self, data, events, portfolio, short_period, long_period):
        self.data = data
        self.symbol_list = self.data.symbol_list
        self.events = events
        self.portfolio = portfolio
        self.short_period = short_period
        self.long_period = long_period
        self.name = 'Moving Averages'

        self.bought = self._calculate_initial_bought()

    def _calculate_initial_bought(self):
        bought = {}
        for symbol in self.symbol_list:
            bought[symbol] = False

        return bought

    def calculate_signals(self, event):
        if event.type == 'MARKET':
            for symbol in self.symbol_list:
                data = self.data.get_latest_data(symbol, N=self.long_period)
                df = pd.DataFrame(data, columns=['symbol','datetime','open','high','low','close','adj_close','volume'])
                df = df.drop(['symbol'], axis=1)
                df.set_index('datetime', inplace=True)
                if data is not None and len(data) >= self.long_period:
                    price_short = df['adj_close'].ewm(self.short_period).mean()[-1]
                    price_long = df['adj_close'].ewm(self.long_period).mean()[-1]
                    if self.bought[symbol] == False and price_short > price_long:
                        quantity = self.portfolio.current_holdings['cash'] / data[0][self.data.price_col]
                        signal = SignalEvent(symbol, data[-1][self.data.time_col], 'LONG', quantity)
                        self.events.put(signal)
                        self.bought[symbol] = True
                        print("Buy", data[0][self.data.time_col], data[0][self.data.price_col])
                    elif self.bought[symbol] == True and price_short < price_long:
                        quantity = self.portfolio.current_positions[symbol]
                        signal = SignalEvent(symbol, data[-1][self.data.time_col], 'EXIT', quantity)
                        self.events.put(signal)
                        self.bought[symbol] = False
                        print("Sell", data[0][self.data.time_col], data[0][self.data.price_col])

class StopLossStrategy(Strategy):
    def __init__(self, data, events, portfolio):
        self.data = data
        self.symbol_list = self.data.symbol_list
        self.events = events
        self.portfolio = portfolio
        self.name = 'Stop Loss'

        self.bought = self._calculate_initial_bought()
        self.stop_loss = self._calculate_initial_stop_loss()

    def _calculate_initial_bought(self):
        bought = {}
        for symbol in self.symbol_list:
            bought[symbol] = False

        return bought

    def _calculate_initial_stop_loss(self):
        stop_loss = {}
        for symbol in self.symbol_list:
            stop_loss[symbol] = None

        return stop_loss

    def calculate_signals(self, event):
        if event.type == 'MARKET':
            for symbol in self.symbol_list:
                data = self.data.get_latest_data(symbol, N=1)
                if data is not None and len(data) > 0:
                    latest_close = data[0][self.data.price_col]
                    if self.bought[symbol] == False and (self.stop_loss[symbol] is None or latest_close > self.stop_loss[symbol]):
                        quantity = self.portfolio.current_holdings['cash'] / latest_close
                        signal = SignalEvent(symbol, data[0][self.data.time_col], 'LONG', quantity)
                        self.events.put(signal)
                        self.bought[symbol] = True
                        self.stop_loss[symbol] = 0.97 * latest_close
                        print("Buy:", data[0][self.data.time_col], latest_close, self.stop_loss[symbol])
                    elif self.bought[symbol] == True and self.stop_loss[symbol] is not None:
                        if latest_close <= self.stop_loss[symbol]:
                            quantity = self.portfolio.current_positions[symbol]
                            signal = SignalEvent(symbol, data[0][self.data.time_col], 'EXIT', quantity)
                            self.events.put(signal)
                            self.bought[symbol] = False
                            print("Sell:", data[0][self.data.time_col], latest_close, self.stop_loss[symbol])
                        else:
                            data = self.data.get_latest_data(symbol, N=2)
                            if data is not None and len(data) > 1:
                                if data[1][self.data.price_col] > data[0][self.data.price_col]:
                                    self.stop_loss[symbol] = 0.97 * data[-1][self.data.price_col]

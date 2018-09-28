import pandas as pd
import math
from datetime import datetime
from event import SignalEvent
from strategies.strategy import Strategy

class StopLossStrategy(Strategy):
    def __init__(self, data, events, portfolio, stop_loss_percentage):
        self.data = data
        self.symbol_list = self.data.symbol_list
        self.events = events
        self.portfolio = portfolio
        self.name = 'Stop Loss'

        self.bought = self._calculate_initial_bought()
        self.stop_loss_percentage = stop_loss_percentage
        self.stop_loss = self._set_initial_stop_loss()

    def _calculate_initial_bought(self):
        bought = {}
        for symbol in self.symbol_list:
            bought[symbol] = False

        return bought

    def _set_initial_stop_loss(self):
        stop_loss = {}
        for symbol in self.symbol_list:
            stop_loss[symbol] = self.stop_loss_percentage

        return stop_loss

    def calculate_signals(self, event):
        if event.type == 'MARKET':
            for symbol in self.symbol_list:
                data = self.data.get_latest_data(symbol)
                if data is not None and len(data) > 0:
                    latest_close = data[-1][self.data.price_col]
                    if self.bought[symbol] == False and latest_close > self.stop_loss[symbol] / self.stop_loss_percentage:
                        quantity = math.floor(self.portfolio.current_holdings['cash'] / latest_close)
                        signal = SignalEvent(symbol, data[-1][self.data.time_col], 'LONG', quantity)
                        self.events.put(signal)
                        self.bought[symbol] = True
                        self.stop_loss[symbol] = self.stop_loss_percentage * latest_close
                        print("Long:", data[-1][self.data.time_col], latest_close)
                        print("Stop Loss:", self.stop_loss[symbol])
                    elif self.bought[symbol] == True:
                        if latest_close <= self.stop_loss[symbol]:
                            quantity = self.portfolio.current_positions[symbol]
                            signal = SignalEvent(symbol, data[0][self.data.time_col], 'EXIT', quantity)
                            self.events.put(signal)
                            self.bought[symbol] = False
                            print("Exit:", data[-1][self.data.time_col], latest_close)
                            print("Stop Loss:", self.stop_loss[symbol])
                        else:
                            data = self.data.get_latest_data(symbol, N=2)
                            if data is not None and len(data) > 1:
                                if data[-1][self.data.price_col] > data[0][self.data.price_col] and self.stop_loss_percentage * data[-1][self.data.price_col] > self.stop_loss[symbol]:
                                    self.stop_loss[symbol] = self.stop_loss_percentage * data[-1][self.data.price_col]
                                    print("Stop Loss:", self.stop_loss[symbol])
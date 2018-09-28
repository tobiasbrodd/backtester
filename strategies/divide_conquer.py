import pandas as pd
import math
from datetime import datetime
from event import SignalEvent
from strategies.strategy import Strategy

class DivideAndConquerStrategy(Strategy):
    def __init__(self, data, events, portfolio):
        self.data = data
        self.symbol_list = self.data.symbol_list
        self.events = events
        self.portfolio = portfolio
        self.name = 'Divide And Conquer'

    def calculate_signals(self, event):
        if event.type == 'MARKET':
            for symbol in self.symbol_list:
                data = self.data.get_latest_data(symbol, N=7)
                df = pd.DataFrame(data, columns=['symbol','datetime','open','high','low','close','adj_close','volume'])
                df = df.drop(['symbol'], axis=1)
                df.set_index('datetime', inplace=True)
                if data is not None and len(data) > 0:
                    mean = df['adj_close'].pct_change().mean()
                    latest_close = data[-1][self.data.price_col]
                    if mean < 0:
                        quantity = math.floor(self.portfolio.current_holdings['cash'] / (2*latest_close))
                        if quantity != 0:
                            signal = SignalEvent(symbol, data[-1][self.data.time_col], 'LONG', quantity)
                            self.events.put(signal)
                            print("Long:", data[-1][self.data.time_col], latest_close)
                    else:
                        quantity = math.floor(self.portfolio.current_positions[symbol] / 2)
                        if quantity != 0:
                            signal = SignalEvent(symbol, data[-1][self.data.time_col], 'EXIT', quantity)
                            self.events.put(signal)
                            print("Exit:", data[-1][self.data.time_col], latest_close)
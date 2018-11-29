import pandas as pd
import matplotlib.pyplot as plt
import math
from datetime import datetime
from matplotlib import style
from event import SignalEvent
from strategies.strategy import Strategy

class MovingAveragesLongStrategy(Strategy):
    def __init__(self, data, events, portfolio, short_period, long_period, version=1):
        self.data = data
        self.symbol_list = self.data.symbol_list
        self.events = events
        self.portfolio = portfolio
        self.short_period = short_period
        self.long_period = long_period
        self.name = 'Moving Averages Long'
        self.version = version

        self.signals = self._setup_signals()
        self.strategy = self._setup_strategy()
        self.bought = self._setup_initial_bought()

    def _setup_signals(self):
        signals = {}
        for symbol in self.symbol_list:
            signals[symbol] = pd.DataFrame(columns=['Date', 'Signal'])

        return signals

    def _setup_strategy(self):
        strategy = {}
        for symbol in self.symbol_list:
            strategy[symbol] = pd.DataFrame(columns=['Date', 'Short', 'Long'])

        return strategy

    def _setup_initial_bought(self):
        bought = {}
        for symbol in self.symbol_list:
            bought[symbol] = False

        return bought

    def calculate_long_short(self, df):
        price_short = None
        price_long = None
        if self.version == 1:
            price_short = df['adj_close'].ewm(span=self.short_period, min_periods=self.short_period, adjust=False).mean()[-1]
            price_long = df['adj_close'].ewm(span=self.long_period, min_periods=self.long_period, adjust=False).mean()[-1]
        else:
            price_short = df['adj_close'].tail(self.long_period).ewm(span=self.short_period, adjust=False).mean()[-1]
            price_long = df['adj_close'].tail(self.long_period).ewm(span=self.long_period, adjust=False).mean()[-1]

        return price_short, price_long

    def calculate_signals(self, event):
        if event.type == 'MARKET':
            for symbol in self.symbol_list:
                data = self.data.get_latest_data(symbol, N=-1)
                df = pd.DataFrame(data, columns=['symbol','datetime','open','high','low','close','adj_close','volume'])
                df = df.drop(['symbol'], axis=1)
                df.set_index('datetime', inplace=True)
                if data is not None and len(data) >= self.long_period:
                    price_short, price_long = self.calculate_long_short(df)
                    date = data[-1][self.data.time_col]
                    price = data[-1][self.data.price_col]
                    self.strategy[symbol] = self.strategy[symbol].append({'Date': date, 'Short': price_short, 'Long': price_long}, ignore_index=True)
                    if self.bought[symbol] == False and price_short > price_long:
                        quantity = math.floor(self.portfolio.current_holdings['cash'] / price)
                        signal = SignalEvent(symbol, date, 'LONG', quantity)
                        self.events.put(signal)
                        self.bought[symbol] = True
                        self.signals[symbol] = self.signals[symbol].append({'Signal': quantity, 'Date': date}, ignore_index=True)
                        print("Long", date, price)
                    elif self.bought[symbol] == True and price_short < price_long:
                        quantity = self.portfolio.current_positions[symbol]
                        signal = SignalEvent(symbol, date, 'EXIT', quantity)
                        self.events.put(signal)
                        self.bought[symbol] = False
                        self.signals[symbol] = self.signals[symbol].append({'Signal': -quantity, 'Date': date}, ignore_index=True)
                        print("Exit", date, price)

    def plot(self):
        style.use('ggplot')

        for symbol in self.symbol_list:
            self.strategy[symbol].set_index('Date', inplace=True)
            self.signals[symbol].set_index('Date', inplace=True)
            signals = self.signals[symbol]
            strategy_fig, strategy_ax = plt.subplots()
            df = self.data.all_data[symbol].copy()
            df.columns = ['close','open','high','low', 'OMXS30', 'volume']
            df = df.drop(['close','open','high','low','volume'], axis=1)
            # df['Short'] = df['OMXS30'].ewm(span=self.short_period, min_periods=self.short_period, adjust=False).mean()
            # df['Long'] = df['OMXS30'].ewm(span=self.long_period, min_periods=self.long_period, adjust=False).mean()

            df.plot(ax=strategy_ax, color='dodgerblue', linewidth=1.0)

            short_index = signals[signals['Signal'] < 0].index
            long_index = signals[signals['Signal'] > 0].index

            strategy_ax.plot(self.strategy[symbol]['Short'], label='Short EMA', color='grey')
            strategy_ax.plot(self.strategy[symbol]['Long'], label='Long EMA', color='k')
            strategy_ax.plot(short_index, df['OMXS30'].loc[short_index], 'v', markersize=10, color='r', label='Exit')
            strategy_ax.plot(long_index, df['OMXS30'].loc[long_index], '^', markersize=10, color='g', label='Long')

            strategy_ax.set_title(self.name)
            strategy_ax.set_xlabel('Time')
            strategy_ax.set_ylabel('Value')
            strategy_ax.legend()

        plt.show()

class MovingAveragesLongShortStrategy(Strategy):
    def __init__(self, data, events, portfolio, short_period, long_period, version=1):
        self.data = data
        self.symbol_list = self.data.symbol_list
        self.events = events
        self.portfolio = portfolio
        self.short_period = short_period
        self.long_period = long_period
        self.name = 'Moving Averages Long Short'
        self.version = version

        self.signals = self._setup_signals()
        self.strategy = self._setup_strategy()
        self.bought = self._setup_initial_bought()

    def _setup_signals(self):
        signals = {}
        for symbol in self.symbol_list:
            signals[symbol] = pd.DataFrame(columns=['Date', 'Signal'])

        return signals

    def _setup_strategy(self):
        strategy = {}
        for symbol in self.symbol_list:
            strategy[symbol] = pd.DataFrame(columns=['Date', 'Short', 'Long'])

        return strategy

    def _setup_initial_bought(self):
        bought = {}
        for symbol in self.symbol_list:
            bought[symbol] = False

        return bought

    def calculate_long_short(self, df):
        price_short = None
        price_long = None
        if self.version == 1:
            price_short = df['adj_close'].ewm(span=self.short_period, min_periods=self.short_period, adjust=False).mean()[-1]
            price_long = df['adj_close'].ewm(span=self.long_period, min_periods=self.long_period, adjust=False).mean()[-1]
        else:
            price_short = df['adj_close'].tail(self.long_period).ewm(span=self.short_period, adjust=False).mean()[-1]
            price_long = df['adj_close'].tail(self.long_period).ewm(span=self.long_period, adjust=False).mean()[-1]

        return price_short, price_long

    def calculate_signals(self, event):
        if event.type == 'MARKET':
            for symbol in self.symbol_list:
                data = self.data.get_latest_data(symbol, N=-1)
                df = pd.DataFrame(data, columns=['symbol','datetime','open','high','low','close','adj_close','volume'])
                df = df.drop(['symbol'], axis=1)
                df.set_index('datetime', inplace=True)
                if data is not None and len(data) >= self.long_period:
                    price_short, price_long = self.calculate_long_short(df)
                    date = data[-1][self.data.time_col]
                    price = data[-1][self.data.price_col]
                    if self.bought[symbol] == False and price_short > price_long:
                        current_positions = self.portfolio.current_positions[symbol]
                        quantity = math.floor(self.portfolio.current_holdings['cash'] / price + current_positions)
                        signal = SignalEvent(symbol, date, 'EXIT', math.fabs(current_positions))
                        self.events.put(signal)
                        signal = SignalEvent(symbol, date, 'LONG', quantity)
                        self.events.put(signal)
                        self.bought[symbol] = True
                        self.signals[symbol] = self.signals[symbol].append({'Signal': quantity, 'Date': date}, ignore_index=True)
                        print("Long", date, price)
                    elif self.bought[symbol] == True and price_short < price_long:
                        quantity = self.portfolio.current_positions[symbol]
                        signal = SignalEvent(symbol, date, 'EXIT', quantity)
                        self.events.put(signal)
                        signal = SignalEvent(symbol, date, 'SHORT', quantity)
                        self.events.put(signal)
                        self.bought[symbol] = False
                        self.signals[symbol] = self.signals[symbol].append({'Signal': -quantity, 'Date': date}, ignore_index=True)
                        print("Short", date, price)

    def plot(self):
        style.use('ggplot')

        for symbol in self.symbol_list:
            self.strategy[symbol].set_index('Date', inplace=True)
            self.signals[symbol].set_index('Date', inplace=True)
            signals = self.signals[symbol]
            strategy_fig, strategy_ax = plt.subplots()
            df = self.data.all_data[symbol].copy()
            df.columns = ['close','open','high','low', 'OMXS30', 'volume']
            df = df.drop(['close','open','high','low','volume'], axis=1)
            # df['Short'] = df['OMXS30'].ewm(span=self.short_period, min_periods=self.short_period, adjust=False).mean()
            # df['Long'] = df['OMXS30'].ewm(span=self.long_period, min_periods=self.long_period, adjust=False).mean()

            df.plot(ax=strategy_ax, color='dodgerblue', linewidth=1.0)

            short_index = signals[signals['Signal'] < 0].index
            long_index = signals[signals['Signal'] > 0].index

            strategy_ax.plot(self.strategy[symbol]['Short'], label='Short EMA', color='grey')
            strategy_ax.plot(self.strategy[symbol]['Long'], label='Long EMA', color='k')
            strategy_ax.plot(short_index, df['OMXS30'].loc[short_index], 'v', markersize=10, color='r', label='Short')
            strategy_ax.plot(long_index, df['OMXS30'].loc[long_index], '^', markersize=10, color='g', label='Long')

            strategy_ax.set_title(self.name)
            strategy_ax.set_xlabel('Time')
            strategy_ax.set_ylabel('Value')
            strategy_ax.legend()

        plt.show()

class MovingAveragesMomentumStrategy(Strategy):
    def __init__(self, data, events, portfolio, short_period, long_period):
        self.data = data
        self.symbol_list = self.data.symbol_list
        self.events = events
        self.portfolio = portfolio
        self.short_period = short_period
        self.long_period = long_period
        self.name = 'Moving Averages Momentum'

    def calculate_long_short(self, df):
        price_short = None
        price_long = None
        if self.version == 1:
            price_short = df['adj_close'].ewm(span=self.short_period, min_periods=self.short_period, adjust=False).mean()[-1]
            price_long = df['adj_close'].ewm(span=self.long_period, min_periods=self.long_period, adjust=False).mean()[-1]
        else:
            price_short = df['adj_close'].tail(self.long_period).ewm(span=self.short_period, adjust=False).mean()[-1]
            price_long = df['adj_close'].tail(self.long_period).ewm(span=self.long_period, adjust=False).mean()[-1]

        return price_short, price_long

    def calculate_signals(self, event):
        if event.type == 'MARKET':
            for symbol in self.symbol_list:
                data = self.data.get_latest_data(symbol, N=-1)
                df = pd.DataFrame(data, columns=['symbol','datetime','open','high','low','close','adj_close','volume'])
                df = df.drop(['symbol'], axis=1)
                df.set_index('datetime', inplace=True)
                if data is not None and len(data) >= self.long_period:
                    price_short, price_long = self.calculate_long_short(df)
                    diff = price_long - price_short
                    factor = math.fabs(2*math.atan(diff) / math.pi)
                    date = data[-1][self.data.time_col]
                    price = data[-1][self.data.price_col]
                    if price_short >= price_long:
                        quantity = math.floor(factor * self.portfolio.current_holdings['cash'] / price)
                        if quantity != 0:
                            signal = SignalEvent(symbol, date, 'LONG', quantity)
                            self.events.put(signal)
                            print('Long', date, price)
                    else:
                        quantity = math.floor(factor/2 * self.portfolio.current_positions[symbol])
                        if quantity != 0:
                            signal = SignalEvent(symbol, date, 'SHORT', quantity)
                            self.events.put(signal)
                            print('Short', date, price)
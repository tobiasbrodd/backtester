import pandas as pd
import matplotlib.pyplot as plt
import queue

from abc import ABCMeta, abstractmethod
from math import floor
from matplotlib import style
from event import FillEvent, OrderEvent
from performance import calculate_sharpe_ratio, calculate_drawdowns

class Portfolio(metaclass=ABCMeta):
    @abstractmethod
    def update_signal(self, event):
        raise NotImplementedError

    @abstractmethod
    def update_fill(self, event):
        raise NotImplementedError

class NaivePortfolio(Portfolio):
    def __init__(self, data, events, strategy_name, initial_capital=1.0):
        self.data = data
        self.events = events
        self.symbol_list = self.data.symbol_list
        self.initial_capital = initial_capital
        self.strategy_name = strategy_name

        self.all_positions = []
        self.current_positions = {symbol: 0.0 for symbol in self.symbol_list}

        self.all_holdings = []
        self.current_holdings = self.construct_current_holdings()

    def construct_current_holdings(self):
        holdings = {symbol: 0.0 for symbol in self.symbol_list}
        holdings['cash'] = self.initial_capital
        holdings['commission'] = 0.0
        holdings['total'] = self.initial_capital
        return holdings

    def update_timeindex(self, event):
        data = {symbol: self.data.get_latest_data(symbol) for symbol in self.symbol_list}
        datetime = data[self.symbol_list[0]][0][self.data.time_col]

        positions = {symbol: self.current_positions[symbol] for symbol in self.symbol_list}
        positions['datetime'] = datetime
        self.all_positions.append(positions)

        holdings = {symbol: 0.0 for symbol in self.symbol_list}
        holdings['datetime'] = datetime
        holdings['cash'] = self.current_holdings['cash']
        holdings['commission'] = self.current_holdings['commission']
        holdings['total'] = self.current_holdings['cash']

        for symbol in self.symbol_list:
            market_value = self.current_positions[symbol] * data[symbol][0][self.data.price_col]
            holdings[symbol] = market_value
            holdings['total'] += market_value

        self.all_holdings.append(holdings)

    def update_positions_from_fill(self, fill):
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        elif fill.direction == 'SELL':
            fill_dir = -1

        self.current_positions[fill.symbol] += fill_dir * fill.quantity

    def update_holdings_from_fill(self, fill):
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        elif fill.direction == 'SELL':
            fill_dir = -1

        fill_cost = self.data.get_latest_data(fill.symbol)[0][self.data.price_col]
        cost = fill_cost * fill_dir * fill.quantity
        self.current_holdings[fill.symbol] += cost
        self.current_holdings['commission'] += fill.commission
        self.current_holdings['cash'] -= (cost + fill.commission)
        self.current_holdings['total'] -= (cost + fill.commission)

    def update_fill(self, event):
        if event.type == 'FILL':
            self.update_positions_from_fill(event)
            self.update_holdings_from_fill(event)

    def generate_naive_order(self, signal):
        order = None

        symbol = signal.symbol
        direction = signal.signal_type
        quantity = signal.quantity

        market_quantity = quantity
        current_quantity = self.current_positions[symbol]
        order_type = 'MKT'

        if direction == 'LONG':
            order = OrderEvent(symbol, order_type, market_quantity, 'BUY')
        if direction == 'SHORT':
            order = OrderEvent(symbol, order_type, market_quantity, 'SELL')

        if direction == 'EXIT' and current_quantity > 0:
            order = OrderEvent(symbol, order_type, market_quantity, 'SELL')
        if direction == 'EXIT' and current_quantity < 0:
            order = OrderEvent(symbol, order_type, market_quantity, 'BUY')

        return order

    def update_signal(self, event):
        if event.type == 'SIGNAL':
            order_event = self.generate_naive_order(event)
            self.events.put(order_event)

    def create_equity_curve_dataframe(self):
        curve = pd.DataFrame(self.all_holdings)
        curve.set_index('datetime', inplace=True)
        curve['returns'] = curve['total'].pct_change()
        curve['equity_curve'] = (1.0 + curve['returns']).cumprod()
        self.equity_curve = curve
        self.holdings_curve = curve['total']

    def output_summary_stats(self):
        self.create_equity_curve_dataframe()
        total_return = self.equity_curve['equity_curve'][-1]
        returns = self.equity_curve['returns']
        pnl = self.equity_curve['equity_curve']

        sharpe_ratio = calculate_sharpe_ratio(returns)
        max_dd, dd_duration = calculate_drawdowns(pnl)

        stats = [("Total Return", "%0.2f%%" % ((total_return - 1.0) * 100.0)),
                ("Sharpe Ratio", "%0.2f" % sharpe_ratio),
                ("Max Drawdown", "%0.2f%%" % (max_dd * 100.0)),
                ("Drawdown Duration", "%d" % dd_duration)]

        return stats

    def plot_holdings(self):
        holdings_fig, holdings_ax = plt.subplots()
        self.holdings_curve.plot(ax=holdings_ax)
        holdings_ax.set_title('Holdings')
        holdings_ax.set_xlabel('Time')
        holdings_ax.set_ylabel('Total')

    def plot_performance(self):
        performance_df = self.data.create_baseline_dataframe()
        performance_df[self.strategy_name] = self.equity_curve['equity_curve']
        performance_df = (performance_df * 100) - 100
        performance_fig, performance_ax = plt.subplots()
        performance_df.plot(ax=performance_ax)
        performance_ax.set_title('Performance')
        performance_ax.set_xlabel('Time')
        performance_ax.set_ylabel('Return (%)')

    def plot_all(self):
        style.use('ggplot')
        self.create_equity_curve_dataframe()
        self.plot_performance()
        plt.show()

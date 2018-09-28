import pandas as pd
import os.path
import queue

from abc import ABCMeta, abstractmethod
from event import MarketEvent
from datetime import datetime
from enum import Enum

class DataSource(Enum):
    NASDAQ = "NASDAQ"
    YAHOO = "YAHOO"

class DataHandler(metaclass=ABCMeta):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_latest_data(self, symbol, N=1):
        raise NotImplementedError

    @abstractmethod
    def update_latest_data(self):
        raise NotImplementedError

class HistoricCSVDataHandler(DataHandler):
    def __init__(self, events, csv_dir, symbol_list, source=DataSource.NASDAQ):
        self.events = events
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list

        self.symbol_data = {}
        self.symbol_dataframe = {}
        self.latest_symbol_data = {}
        self.continue_backtest = True

        self.time_col = 1
        self.price_col = 6

        self._open_convert_csv_files(source)

    def _open_convert_csv_files(self, source):
        combined_index = None
        for symbol in self.symbol_list:
            if source == DataSource.NASDAQ:
                self.parse_nasdaq_csv(symbol)
            else:
                self.parse_yahoo_csv(symbol)

            if combined_index is None:
                combined_index = self.symbol_data[symbol].index
            else:
                combined_index.union(self.symbol_data[symbol].index)

            self.latest_symbol_data[symbol] = []

        for symbol in self.symbol_list:
            self.symbol_dataframe[symbol] = self.symbol_data[symbol].reindex(index=combined_index, method='pad')
            self.symbol_data[symbol] = self.symbol_dataframe[symbol].iterrows()

    def _get_new_data(self, symbol):
        for row in self.symbol_data[symbol]:
            yield tuple([symbol, row[0], row[1][0], row[1][1], row[1][2], row[1][3], row[1][4], row[1][5]])

    def get_latest_data(self, symbol, N=1):
        try:
            return self.latest_symbol_data[symbol][-N:]
        except KeyError:
            print("{symbol} is not a valid symbol.").format(symbol=symbol)

    def update_latest_data(self):
        for symbol in self.symbol_list:
            data = None
            try:
                data = next(self._get_new_data(symbol))
            except StopIteration:
                self.continue_backtest = False
            if data is not None:
                self.latest_symbol_data[symbol].append(data)

        self.events.put(MarketEvent())

    def create_baseline_dataframe(self):
        dataframe = None
        for symbol in self.symbol_list:
            df = self.symbol_dataframe[symbol]
            if dataframe == None:
                dataframe = pd.DataFrame(df['Adj Close'])
                dataframe.columns = [symbol]
            else:
                dataframe[symbol] = pd.DataFrame(df['Adj Close'])
            dataframe[symbol] = dataframe[symbol].pct_change()
            dataframe[symbol] = (1.0 + dataframe[symbol]).cumprod()

        return dataframe

    def parse_yahoo_csv(self, symbol):
        self.symbol_data[symbol] = pd.read_csv(os.path.join(self.csv_dir, symbol + '.csv'), header=0, index_col=0, parse_dates=True)

    def parse_nasdaq_csv(self, symbol):
        tmp = pd.read_csv(os.path.join(self.csv_dir, symbol + '.csv'), header=0, index_col=0, parse_dates=True).iloc[::-1]
        self.symbol_data[symbol] = pd.DataFrame(tmp['Closing price'])
        self.symbol_data[symbol].columns = ['Close']
        self.symbol_data[symbol]['Open'] = tmp['Closing price']
        self.symbol_data[symbol]['High'] = tmp['High price']
        self.symbol_data[symbol]['Low'] = tmp['Low price']
        self.symbol_data[symbol]['Close'] = tmp['Closing price']
        self.symbol_data[symbol]['Adj Close'] = tmp['Closing price']
        self.symbol_data[symbol]['Volume'] = tmp['Total volume']
        self.symbol_data[symbol] = self.symbol_data[symbol][self.symbol_data[symbol]['Close'] > 0.0]

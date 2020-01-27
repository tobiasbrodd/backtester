import queue
import time
import config
from datetime import datetime
from event import MarketEvent, SignalEvent, OrderEvent, FillEvent
from data import QuandlDataHandler, HistoricCSVDataHandler, DataSource
from strategies.hold import BuyAndHoldStrategy, SellAndHoldStrategy
from strategies.macd import MovingAveragesLongStrategy, MovingAveragesLongShortStrategy, MovingAveragesMomentumStrategy
from strategies.stop_loss import StopLossStrategy
from strategies.divide_conquer import DivideAndConquerStrategy
from portfolio import NaivePortfolio
from execution import SimulateExecutionHandler

def backtest(events, data, portfolio, strategy, broker):
    while True:
        data.update_latest_data()
        if data.continue_backtest == False:
            break

        while True:
            try:
                event = events.get(block=False)
            except queue.Empty:
                break

            if event is not None:
                if event.type == 'MARKET':
                    strategy.calculate_signals(event)
                    portfolio.update_timeindex(event)
                elif event.type == 'SIGNAL':
                    portfolio.update_signal(event)
                elif event.type == 'ORDER':
                    broker.execute_order(event)
                elif event.type == 'FILL':
                    portfolio.update_fill(event)

        # time.sleep(10*60)
    stats = portfolio.summary_stats()

    for stat in stats:
            print(stat[0] + ": " + stat[1])

    strategy.plot()
    portfolio.plot_all()

# for s in [5, 10, 50, 100, 200]:
#     for l in [s+10, s+50, s+100, s+200]:
#         events = queue.Queue()
#         data = HistoricCSVDataHandler(events, 'csv/', ['OMXS30'], DataSource.NASDAQ)
#         # data = QuandlDataHandler(events, ['OMXS30'], config.API_KEY)
#         portfolio = NaivePortfolio(data, events, '', initial_capital=2000)
#         # strategy = BuyAndHoldStrategy(data, events, portfolio)
#         # strategy = SellAndHoldStrategy(data, events, portfolio)
#         # strategy = MovingAveragesLongShortStrategy(data, events, portfolio, 100, 200, version=1)
#         # strategy = MovingAveragesMomentumStrategy(data, events, portfolio, 100, 200)
#         # strategy = StopLossStrategy(data, events, portfolio, 0.9)
#         # strategy = DivideAndConquerStrategy(data, events, portfolio)
#         strategy = MovingAveragesLongStrategy(data, events, portfolio, s, l, version=2)
#         portfolio.strategy_name = strategy.name
#         broker = SimulateExecutionHandler(events)
#         print('Short: {0}, Long: {1}'.format(s, l))
#         backtest(events, data, portfolio, strategy, broker)
#         print('----------')

events = queue.Queue()
data = HistoricCSVDataHandler(events, 'csv/', ['OMXS30'], DataSource.NASDAQ)
portfolio = NaivePortfolio(data, events, '', initial_capital=2000)
strategy = MovingAveragesLongStrategy(data, events, portfolio, 50, 100, version=1)
portfolio.strategy_name = strategy.name
broker = SimulateExecutionHandler(events)

backtest(events, data, portfolio, strategy, broker)
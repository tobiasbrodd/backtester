import queue
import time
from event import MarketEvent, SignalEvent, OrderEvent, FillEvent
from data import HistoricCSVDataHandler
from strategy import BuyAndHoldStrategy, MovingAveragesStrategy
from portfolio import NaivePortfolio
from execution import SimulateExecutionHandler

events = queue.Queue()
data = HistoricCSVDataHandler(events, '~/Code/python/backtesting/', ['AAPL'])
strategy = MovingAveragesStrategy(data, events)
portfolio = NaivePortfolio(data, events, '2017-01-01')
broker = SimulateExecutionHandler(events)

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

stats = portfolio.output_summary_stats()
for stat in stats:
    print(stat[0] + ": " + stat[1])

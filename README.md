# backtester
An event-driven backtester

## About
This backtester is based on a guide written by Quantstart's [Michael Halls-Moore](http://www.quantstart.com/about-mike/) on how to write an event-driven backtester. Improvements to the code in the guide made by [Douglas Denhartog](https://github.com/denhartog/quantstart-backtester) has also been incorporated. The code has then been modified by me to actually run and include more features.

**Guide:**
1. [Event-Driven Backtesting with Python - Part I](http://www.quantstart.com/articles/Event-Driven-Backtesting-with-Python-Part-I)
2. [Event-Driven Backtesting with Python - Part II](http://www.quantstart.com/articles/Event-Driven-Backtesting-with-Python-Part-II)
3. [Event-Driven Backtesting with Python - Part III](http://www.quantstart.com/articles/Event-Driven-Backtesting-with-Python-Part-III)
4. [Event-Driven Backtesting with Python - Part IV](http://www.quantstart.com/articles/Event-Driven-Backtesting-with-Python-Part-IV)
5. [Event-Driven Backtesting with Python - Part V](http://www.quantstart.com/articles/Event-Driven-Backtesting-with-Python-Part-V)
6. [Event-Driven Backtesting with Python - Part VI](http://www.quantstart.com/articles/Event-Driven-Backtesting-with-Python-Part-VI)
7. [Event-Driven Backtesting with Python - Part VII](http://www.quantstart.com/articles/Event-Driven-Backtesting-with-Python-Part-VII)
8. [Event-Driven Backtesting with Python - Part VIII](http://www.quantstart.com/articles/Event-Driven-Backtesting-with-Python-Part-VIII)

## How To
### Define Strategy
You can define a strategy by implementing the Strategy class found in **strategy.py**. There also exists three predefined strategies in **strategy.py**.

### Backtest a Strategy
In order to choose strategy to backtest, you have to change the used strategy class **loop.py**. You can also specify which CSV files/symbols that should be used in the backtesting suite by changing the CSV directory path and symbols in the same python file.  
**Note:** The specified CSV files must have the same format as CSV files downloaded from Yahoo Finance. If the CSV files have another format, they need to be converted to Yahoo's format.  
**Special Case:** If the specified CSV files were downloaded from Nasdaq, you can change the parser in data.py to the Nasdaq CSV parser.  

To run the backtesting suite, use  **python3 loop.py** from the terminal.

### Dependencies
- pandas
- numpy
- matplotlib

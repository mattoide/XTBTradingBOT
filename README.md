# XTBTradingBOT



> ##########   **__NOT A DEFINITIVE VERSION__**   ##########



###### Description
This bot detect 2 inversion's patterns: **Bullish/Bearish Engulfing Pattern**, **Hammer** and **Shooting Star**. It's Open **BUY** or **SELL** position if RSI is in optimal range. The Bot scan if there is a profit in pips, and add trailing stop loss to the opened position.

You can customize some vars, in ```configs/tradingConfig.py```,  like:

- RSI bottom and top values
- RSI period
- Chart period (timeframe)
- Minimum PIPS for appling trailing stop loss


###### Usage

- install python and python-pip on your system
    1.1 - ***if u are on linux, install gnome-terminal***
    
- run ```python install.py```

- update .env file

- run ```python XTBot.py EURUSD```  [replace "EURUSD" with custom asset, but check if it present in configs/symbolConfig.py]
or run ```python startAll.py``` for run bot for every configured asset

- run ```python stopAll.py``` for closing all bot instances

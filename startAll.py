import os


from utils.symbolConfig import *

symbols = json.loads(getAllSymbols())

for symbol in symbols:
    cmd = 'gnome-terminal --title=' + symbol['symbol'] + ' -- python startBotFor.py ' + symbol['symbol']
    os.system(cmd)
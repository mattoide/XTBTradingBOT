import os


from utils.symbolConfig import *

symbols = json.loads(getAllSymbols())

for symbol in symbols:
    # print(symbol['symbol'])
    cmd = 'gnome-terminal -- python startBotFor.py ' + symbol['symbol']
    # print(cmd)
    os.system(cmd)
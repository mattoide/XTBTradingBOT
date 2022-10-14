import os


from utils.symbolConfig import *

symbols = json.loads(getAllSymbols())

for symbol in symbols:
    cmd = 'gnome-terminal -- python startBotFor.py ' + symbol['symbol']
    os.system(cmd)
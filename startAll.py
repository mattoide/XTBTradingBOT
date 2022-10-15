import os
import json


from configs.symbolConfig import getAllSymbols

symbols = json.loads(getAllSymbols())

for symbol in symbols:
    cmd = 'gnome-terminal --title=' + symbol['symbol'] + ' -- python XTBot.py ' + symbol['symbol']
    os.system(cmd)
import os
import json


from configs.symbolConfig import getAllSymbols

symbols = json.loads(getAllSymbols())

for symbol in symbols:
    cmd = 'kill -9 $(ps -u | grep "XTBot.py ' + symbol['symbol'] + '" | awk \'{print $2}\' | head -n 1)'
    # print(cmd)
    os.system(cmd)
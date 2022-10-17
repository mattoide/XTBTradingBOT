import os
import json
import sys

platform = sys.platform


from configs.symbolConfig import getAllSymbols

symbols = json.loads(getAllSymbols())

cmd = ''

for symbol in symbols:
    if('linux' in platform):
        cmd = 'kill -9 $(ps -u | grep "XTBot.py ' + symbol['symbol'] + '" | awk \'{print $2}\' | head -n 1)'
    elif('win' in platform):
        s = symbol['symbol']
        cmd = f'for /F "tokens=1,2" %A in (\'\"tasklist /FI \"WINDOWTITLE eq {s}\" /FO LIST | FIND \"PID\" \"\') DO TASKKILL /pid %B'

    os.system(cmd)
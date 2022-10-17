import os
import json
import sys

platform = sys.platform

cmd = ''

if('win' in platform):
    cmd = 'pause'
elif('linux' in platform):
    cmd = 'read -n 1'


from configs.symbolConfig import getAllSymbols

symbols = json.loads(getAllSymbols())

for symbol in symbols:
    if('linux' in platform):
        cmd = 'gnome-terminal --title=' + symbol['symbol'] + ' -- python XTBot.py ' + symbol['symbol']
    elif('win' in platform):
        cmd = 'start "' +  symbol['symbol'] + ' "cmd /c python XTBot.py ' + symbol['symbol']

    os.system(cmd)
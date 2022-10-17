import os
import sys

platform = sys.platform

cmd = ''

if('win' in platform):
    cmd = 'pause'
elif('linux' in platform):
    cmd = 'read -n 1'

def waitForClose():
    os.system(cmd)
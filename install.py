import sys
import os

platform = sys.platform

cmd = ''

if('win' in platform):
    cmd = 'cmd installers\install.bat'
elif('linux' in platform):
    cmd = './installers/install.sh'

os.system(cmd)
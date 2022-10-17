import sys

platform = sys.platform

### no color for winzoz
if('win' in platform):
    RESET = ""
    GREEN = ""
    RED = ""
elif('linux' in platform):
    RESET = "\x1b[0m"
    GREEN = "\x1b[32;20m"
    RED = "\x1b[31;20m"




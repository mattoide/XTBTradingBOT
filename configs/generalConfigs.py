import sys

platform = sys.platform


if('win' in platform):
    RESET = "[0m"
    GREEN = "^<ESC^>[32m [32m"
    RED = "^<ESC^>[31m [31m"
elif('linux' in platform):
    RESET = "\x1b[0m"
    GREEN = "\x1b[32;20m"
    RED = "\x1b[31;20m"




import sys
from typing import Callable

def which(argv):
    sys.stdout.write("command: "+argv[0]+'\n')
    return 0

def shell_exit(argv):
    if len(argv) < 2: exit(0)
    exit(argv[1])

def echo(argv):
    sys.stdout.write(' '.join(argv[1:]) + '\n')
    return 0

BUILTINS: dict[str,Callable] = {
    "which": which,
    "exit": shell_exit,
    "echo": echo,
}

def shell_type(argv):
    if len(argv) < 2: return 1
    if argv[1] in BUILTINS.keys():
        sys.stdout.write(argv[1]+' is a shell builtin\n')
        return 0
    else:
        sys.stdout.write(argv[1]+': not found\n')
        return 1

BUILTINS["type"] = shell_type

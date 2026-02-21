import sys
from typing import Callable
import os

def find_command(cmd: str) -> tuple[bool, str]:
    path = os.environ.get("PATH")
    if path == None: print("PATH could not be found"); exit(1)

    path = path.split(os.pathsep)
    for directory in path:
        files = os.listdir(directory)
        if cmd in files:
            path = os.path.join(directory,cmd)
            if os.access(path, os.X_OK): return (True, path)
    return (False, "")

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

    path = find_command(argv[0])
    if path[0] == True:
        sys.stdout.write(argv[1]+' is '+path[1]+'\n')
        return 0

    sys.stdout.write(argv[1]+': not found\n')
    return 1

BUILTINS["type"] = shell_type

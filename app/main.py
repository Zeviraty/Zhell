import sys
from . import commands 
from typing import Callable

def get_command(cmd: list[str]) -> tuple[bool,Callable[[list[str]],int]]:
    if cmd[0] in commands.BUILTINS.keys():
        return (True,commands.BUILTINS[cmd[0]])
    else:
        return (False,lambda x: exit(x[0]))

def main():
    while True:
        sys.stdout.write("$ ")

        uin = input().split(" ")
        cmd = get_command(uin)

        if cmd[0] == True:
            cmd[1](uin)
        else:
            sys.stdout.write(f"{uin[0]}: command not found\n")

if __name__ == "__main__":
    main()

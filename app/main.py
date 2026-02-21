import sys
from . import commands 
from typing import Callable
import os

def run_command(path:str) -> Callable[[list[str]],int]:
    def command(argv:list[str]) -> int:
        pid = os.fork()

        if pid == 0:
            try:
                os.execv(path, argv)
            except Exception as _:
                os._exit(1)
        else:
            _, status = os.waitpid(pid, 0)
            return os.WEXITSTATUS(status)
    return command

def get_command(cmd: list[str]) -> tuple[bool,Callable[[list[str]],int]]:
    if cmd[0] in commands.BUILTINS.keys():
        return (True,commands.BUILTINS[cmd[0]])
    
    path = commands.find_command(cmd[0])
    if path[0] == True:
        return (True, run_command(path[1]))

    return (False,lambda x: exit(x[0]))

def main():
    while True:
        sys.stdout.write("$ ")

        uin = input().split(" ")
        cmd = get_command(uin)

        if cmd[0] == True:
            cmd[1](uin)
            continue
        
        sys.stdout.write(f"{uin[0]}: command not found\n")

if __name__ == "__main__":
    main()

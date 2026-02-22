import sys
from . import commands 
from typing import Callable
import os
import shlex
import readline

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

def completer(text: str, state: int) -> str | None:
    try:
        buffer = readline.get_line_buffer()
        try: line = shlex.split(buffer)
        except ValueError: return None

        if len(line) > 1: return None

        matches = [
            cmd for cmd in commands.BUILTINS.keys()
            if cmd.startswith(text)
        ]
        return matches[state] if state < len(matches) else None
    except Exception as e:
        print("Completer crashed:", e)
        return None

def main():
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")
    while True:
        try: uin = shlex.split(input("$ "))
        except EOFError: return
        if not uin: continue
        cmd = get_command(uin)

        if cmd[0] == True:
            cmd[1](uin)
            continue
        
        sys.stdout.write(f"{uin[0]}: command not found\n")

if __name__ == "__main__":
    main()

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

TAB_COUNT = 0
LAST_BUFFER = ""
CACHED_MATCHES = []

def completer(text: str, state: int):
    global TAB_COUNT

    if state != 0: return None

    matches = []
    if readline.get_begidx() != 0: return None

    for cmd in commands.BUILTINS.keys():
        if cmd.startswith(text):
            matches.append(cmd)

    for _, files in commands.get_path_files().items():
        for file in files:
            if file.startswith(text):
                matches.append(file)

    matches = sorted(set(matches))

    if not matches:
        return None

    if len(matches) == 1:
        return matches[0] + " "

    if TAB_COUNT == 0:
        sys.stdout.write("\x07")
        TAB_COUNT = 1
    else:
        TAB_COUNT = 0
        clean_matches = [m.rstrip() for m in matches]
        sys.stdout.write("\n"+"  ".join(clean_matches)+"\n")
        sys.stdout.write("$ " + readline.get_line_buffer())
        sys.stdout.flush()

    return None



def main():
    commands.get_path_files()
    readline.set_completer(completer)
    readline.parse_and_bind('tab: complete')
    readline.set_completer_delims(" \t\n;")
    while True:
        sys.stdout.flush()
        sys.stderr.flush()
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

import sys
from . import commands 

BUILTINS = {
    "which": commands.which
}

def get_command(cmd: list[str]) -> tuple:
    if cmd[0] in BUILTINS.keys():
        return (True,BUILTINS[cmd[0]])
    else:
        return (False,{})

def main():
    while True:
        sys.stdout.write("$ ")

        uin = input()
        cmd = get_command(uin.split(" "))

        if cmd[0] == True:
            pass
        else:
            sys.stdout.write(f"{uin}: command not found\n")


if __name__ == "__main__":
    main()

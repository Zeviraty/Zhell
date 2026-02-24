import sys
from . import commands 
from typing import Callable
import os
import shlex
import readline

def lcp(v: list[str]) -> str:
    ans=""
    v=sorted(v)
    first=v[0]
    last=v[-1]
    for i in range(min(len(first),len(last))):
        if(first[i]!=last[i]):
            return ans
        ans+=first[i]
    return ans 

def run_command(path: str, inputfd=0, outputfd=1, outputerrfd=2):
    def command(argv: list[str]) -> int:
        pid = os.fork()

        if pid == 0:
            try:
                if inputfd != 0:
                    os.dup2(inputfd, 0)
                if outputfd != 1:
                    os.dup2(outputfd, 1)
                if outputerrfd != 1:
                    os.dup2(outputerrfd, 2)

                if inputfd not in (0, 1, 2):
                    os.close(inputfd)
                if outputfd not in (0, 1, 2):
                    os.close(outputfd)
                if outputfd not in (0, 1,2 ):
                    os.close(outputerrfd)

                os.execv(path, argv)
            except Exception:
                os._exit(1)
        else:
            return pid
    return command

def get_command(cmd: list[str], inputfd=0, outputfd=1, outputerrfd=2):
    if cmd[0] in commands.BUILTINS:
        builtin = commands.BUILTINS[cmd[0]]

        if inputfd != 0 or outputfd != 1 or outputerrfd != 2:
            def forked_builtin(argv):
                pid = os.fork()
                if pid == 0:
                    if inputfd != 0:
                        os.dup2(inputfd, 0)
                    if outputfd != 1:
                        os.dup2(outputfd, 1)
                    if outputerrfd != 1:
                        os.dup2(outputfd, 2)
                    try:
                        exit_code = builtin(argv)
                    except Exception:
                        exit_code = 1
                    os._exit(exit_code)
                return pid
            return (True, forked_builtin)

        return (True, builtin)

    path = commands.find_command(cmd[0])
    if path[0]:
        return (True, run_command(path[1], inputfd, outputfd))

    return (False, lambda x: 127)

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

    prefix = lcp(matches)
    if prefix != text:
        return prefix

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
    readline.set_auto_history(True)
    histfile = os.environ.get("HISTFILE")
    if histfile != None and histfile.strip() != "" and os.path.exists(histfile): commands.history(["history","-r",histfile])
    while True:
        sys.stdout.flush()
        sys.stderr.flush()
        try:
            raw = input("$ ")
            raw = raw.replace("|", " | ")
            uin = shlex.split(raw)
        except EOFError: return
        if not uin: continue

        if '|' in uin:
            segments = []
            tmp = []
            for token in uin:
                if token == '|':
                    segments.append(tmp)
                    tmp = []
                else:
                    tmp.append(token)
            segments.append(tmp)

            pids = []
            prev_read = None

            for i, segment in enumerate(segments):
                if i < len(segments) - 1:
                    read_fd, write_fd = os.pipe()
                else:
                    read_fd, write_fd = None, None

                is_valid, cmd_fn = get_command(
                    segment,
                    inputfd=prev_read if prev_read is not None else 0,
                    outputfd=write_fd if write_fd is not None else 1
                )

                if not is_valid:
                    sys.stdout.write(f"{segment[0]}: command not found\n")
                    break

                pid = cmd_fn(segment)
                pids.append(pid)

                if prev_read is not None:
                    os.close(prev_read)
                if write_fd is not None:
                    os.close(write_fd)

                prev_read = read_fd

            for pid in pids:
                os.waitpid(pid, 0)
            continue

        elif '>' in uin or '1>' in uin or '2>' in uin:
            fd = 1
            loc = None
            if '>' in uin: loc=uin.index('>')
            elif '1>' in uin: loc=uin.index('1>')
            elif '2>' in uin: loc=uin.index('2>'); fd = 2
            if loc is None: continue
            cmd = uin[:loc+1]
            file= uin[loc+1:][0]
            ffd = os.open(file,os.O_CREAT|os.O_WRONLY)
            if fd == 1: valid, cmd_fn = get_command(cmd,outputfd=ffd)
            elif fd == 2: valid, cmd_fn = get_command(cmd,outputerrfd=ffd)
            else: continue
            
            if not valid:
                sys.stdout.write(f"{uin[0]}: command not found\n")
                continue
            
            result = cmd_fn(uin)

            if isinstance(result, int) and result > 0:
                try:
                    os.waitpid(result, 0)
                except ChildProcessError:
                    pass
        elif '>>' in uin or '1>>' in uin or '2>>' in uin:
            fd = 1
            loc = None
            if '>>' in uin: loc=uin.index('>>')
            elif '1>>' in uin: loc=uin.index('1>>')
            elif '2>>' in uin: loc=uin.index('2>>'); fd = 2
            if loc is None: continue
            cmd = uin[:loc+1]
            file= uin[loc+1:][0]
            ffd = os.open(file,os.O_CREAT|os.O_WRONLY)
            if fd == 1: valid, cmd_fn = get_command(cmd,outputfd=ffd)
            elif fd == 2: valid, cmd_fn = get_command(cmd,outputerrfd=ffd)
            else: continue
            if not valid:
                sys.stdout.write(f"{uin[0]}: command not found\n")
                continue
            
            result = cmd_fn(uin)

            if isinstance(result, int) and result > 0:
                try:
                    os.waitpid(result, 0)
                except ChildProcessError:
                    pass
        else:
            is_valid, cmd_fn = get_command(uin)

            if not is_valid:
                sys.stdout.write(f"{uin[0]}: command not found\n")
                continue

            result = cmd_fn(uin)

            if isinstance(result, int) and result > 0:
                try:
                    os.waitpid(result, 0)
                except ChildProcessError:
                    pass

if __name__ == "__main__":
    main()
    histfile = os.environ.get("HISTFILE")
    if histfile != None and histfile.strip() != "": commands.history(["history","-w",histfile])

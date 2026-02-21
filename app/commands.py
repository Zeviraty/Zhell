import sys

def which(argv):
    sys.stdout.write("command: "+argv[0])
    return 0

def shell_exit(argv):
    if len(argv) < 2: exit(0)
    exit(argv[1])

def echo(argv):
    sys.stdout.write(' '.join(argv[1:]) + '\n')
    return 0

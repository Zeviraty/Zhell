def which(argv):
    print("command: "+argv[0])
    return 0

def shell_exit(argv):
    if len(argv) < 2: exit(0)
    exit(argv[1])

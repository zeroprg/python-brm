import sys

def get_stdin():
    buf = ""
    for line in sys.stdin:
        buf = buf + line
        if(line == '' or line == '\n'): break

    return buf

if(__name__ == "__main__"):
    st = get_stdin()
    print(st)
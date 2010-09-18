
import re, sys

def datefilter(line):
    return re.sub(r'(20\d{2})(\d{2})(\d{2})', r'\1-\2-\3', line)

if __name__ == '__main__':
    for line in sys.stdin:
        sys.stdout.write(datefilter(line))
